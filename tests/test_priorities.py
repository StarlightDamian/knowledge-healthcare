import copy
import csv
import gzip
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.guide.model import ValidationError, canonical_hash
from src.guide.icd import load_icd
from src.guide.priorities import build_priority_report, check_priority_outputs, priorities_icd, write_priority_outputs


def fixture():
    def row(number, code, chapter, parent='', kind='category', included=False, residual=False):
        return {'row': number, 'code': code, 'title': '- Official ' + (code or chapter),
                'chapter': chapter, 'class_kind': kind,
                'foundation_uri': '' if residual else f'http://id.who.int/icd/entity/{number}',
                'linearization_uri': f'http://id.who.int/icd/release/11/mms/{number}',
                'parent_uri': f'http://id.who.int/icd/entity/{parent}' if parent else '',
                'decision': 'included' if included else 'excluded', 'is_leaf': included,
                'is_residual': residual, 'release': '2026-01'}
    rows = [row(1, '', '01', kind='chapter'), row(2, '', '02', kind='chapter'),
            row(3, 'P', '01', 1), row(4, 'X', '01', 3, included=True),
            row(5, 'X2', '01', 3, included=True, residual=True),
            row(6, 'P.Z', '02', 2, included=True), row(7, 'Y', '01', 1, included=True)]
    snapshot = {'rows': rows, 'manifest': {'release': '2026-01', 'eligible_categories': 4,
                'snapshot_sha256': 'snapshot-fixture', 'catalog_sha256': canonical_hash(rows)}}
    coverage = {'release': '2026-01', 'denominator': 4, 'covered_categories': 1, 'fraction': 0.25,
                'issues': [], 'category_states': [{'code': r['code'], 'state': 'complete' if r['code'] == 'X2' else 'missing',
                 'candidates': [{'condition_id': 'published', 'status': 'confirmed'}] if r['code'] == 'X2' else []}
                 for r in rows if r['decision'] == 'included']}
    config = {'schema_version': 1, 'release': '2026-01', 'purpose': '测试全量编辑排程',
              'dimensions': {'urgency': {'label': '时效', 'description': '未知保留空值'}},
              'levels': {p: {'label': p, 'description': '编辑优先级'} for p in ('P0', 'P1', 'P2', 'P3')},
              'sources': [{'id': 'official', 'title': 'Official', 'url': 'https://example.org/guide',
                           'locator': 'Section 1', 'accessed_at': '2026-10-02', 'support_scope': '规则依据'}],
              'chapter_defaults': {chapter: {'priority': 'P2', 'department': 'primary-care', 'label': chapter,
                      'reason': '未逐类评估，不等于低危', 'dimensions': {'urgency': None}, 'source_ids': ['official']}
                                   for chapter in ('01', '02')},
              'rules': [{'id': 'a-parent', 'selector': {'ancestors': ['P']}, 'priority': 'P0',
                         'reason': '祖先指定', 'dimensions': {'urgency': '已指定'}, 'source_ids': ['official']},
                        {'id': 'z-exact', 'selector': {'codes': ['X']}, 'priority': 'P0',
                         'reason': '同级另规则', 'dimensions': {'urgency': '独立评估'}, 'source_ids': ['official']}]}
    return snapshot, coverage, config, {'primary-care': {'zh-CN': '全科', 'en': 'Primary care'}}


class PriorityTests(unittest.TestCase):
    def test_parent_edges_residual_and_overlapping_rules_do_not_match_code_prefixes(self):
        snapshot, coverage, rules, departments = fixture()
        before = copy.deepcopy(coverage)
        report = build_priority_report(snapshot, coverage, rules, departments)
        rows = {r['code']: r for r in report['categories']}
        self.assertEqual(set(rows), {'X', 'X2', 'P.Z', 'Y'})
        self.assertEqual(rows['X']['matched_rule_ids'], ['a-parent', 'z-exact'])
        self.assertEqual(rows['X']['rule_id'], 'a-parent')
        self.assertEqual(rows['X2']['priority'], 'P0')
        self.assertIsNone(rows['X2']['queue_rank'])
        self.assertIsNone(rows['X2']['work_package'])
        self.assertEqual(rows['P.Z']['priority'], 'P2')
        self.assertEqual(rows['P.Z']['unknown_dimensions'], ['urgency'])
        self.assertIsNone(rows['P.Z']['dimensions']['urgency'])
        self.assertEqual(coverage, before)
        # URI block/category references resolve identically to code references.
        rules['rules'][0]['selector'] = {'ancestors': [snapshot['rows'][2]['linearization_uri']]}
        self.assertEqual(build_priority_report(snapshot, coverage, rules, departments)['categories'], report['categories'])

    def test_queue_round_robin_official_order_and_twenty_category_packages(self):
        snapshot, coverage, rules, departments = fixture()
        rules['rules'] = []
        coverage.update(covered_categories=0, fraction=0)
        for state in coverage['category_states']:
            state.update(state='missing', candidates=[])
        report = build_priority_report(snapshot, coverage, rules, departments)
        self.assertEqual([r['code'] for r in report['categories']], ['X', 'P.Z', 'X2', 'Y'])
        # Additional independent leaf identities exercise the actual package boundary.
        for number in range(8, 46):
            row = dict(snapshot['rows'][-1], row=number, code=f'N{number}',
                       foundation_uri=f'http://id.who.int/icd/entity/{number}',
                       linearization_uri=f'http://id.who.int/icd/release/11/mms/{number}')
            snapshot['rows'].append(row)
            coverage['category_states'].append({'code': row['code'], 'state': 'missing', 'candidates': []})
        snapshot['manifest']['eligible_categories'] = coverage['denominator'] = 42
        report = build_priority_report(snapshot, coverage, rules, departments)
        self.assertEqual([r['queue_rank'] for r in report['categories']], list(range(1, 43)))
        self.assertEqual([r['work_package'] for r in report['categories'][19:21]], ['WP-0001', 'WP-0002'])
        self.assertEqual(report['categories'][-1]['work_package'], 'WP-0003')
        self.assertEqual(len(report['summary']['next_package']), 20)

    def test_input_errors_fail_instead_of_silently_dropping_categories_or_evidence(self):
        cases = {
            'unknown selector': lambda s, c, r: r['rules'][0].update(selector={'codes': ['no-code']}),
            'empty ancestor': lambda s, c, r: r['rules'][0].update(selector={'codes': ['P']}),
            'bad source': lambda s, c, r: r['rules'][0].update(source_ids=['missing']),
            'bad department': lambda s, c, r: r['rules'][0].update(department='missing'),
            'low default': lambda s, c, r: r['chapter_defaults']['01'].update(priority='P3'),
            'duplicate leaf': lambda s, c, r: s['rows'].append(dict(s['rows'][-1])),
            'lost state': lambda s, c, r: c['category_states'].pop(),
            'lost chapter': lambda s, c, r: r['chapter_defaults'].pop('02'),
        }
        for name, change in cases.items():
            with self.subTest(name=name):
                s, c, r, departments = fixture()
                change(s, c, r)
                with self.assertRaises(ValidationError):
                    build_priority_report(s, c, r, departments)

    def test_related_work_uses_exact_codes_without_inheriting_completion(self):
        s, c, r, d = fixture()
        inventory = {'items': [{'kind': 'backlog', 'id': 'planned-one', 'candidate_codes': ['P.Z']},
                               {'kind': 'backlog', 'id': 'parent-only', 'candidate_codes': ['P']}]}
        mece = {'topics': [{'canonical_id': 'draft-one', 'publication_status': 'not_published',
                            'icd_candidates': [{'code': 'P.Z'}]}]}
        report = build_priority_report(s, c, r, d, inventory, mece)
        rows = {x['code']: x for x in report['categories']}
        self.assertEqual(rows['P.Z']['related_work'], [
            {'kind': 'backlog', 'id': 'planned-one', 'status': 'title_only_scope_candidate'},
            {'kind': 'draft', 'id': 'draft-one', 'status': 'draft_scope_candidate'}])
        self.assertEqual(rows['X']['related_work'], [])
        self.assertEqual(rows['P.Z']['coverage_state'], 'missing')
        self.assertEqual(report['summary']['covered_categories'], 1)
        self.assertEqual(report['summary']['provenance']['batch_mece_sha256'], canonical_hash(mece))

    def test_output_bytes_are_reproducible_csv_is_bom_and_every_leaf_has_a_markdown_row(self):
        titles = {code: '- - 官方中文' + code for code in ('X', 'X2', 'P.Z', 'Y')}
        report = build_priority_report(*fixture(), chinese_titles=titles)
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            for folder in (a, b):
                root = Path(folder)
                (root / 'reports').mkdir()
                (root / 'reports/icd-coverage.json').write_bytes(b'coverage must stay unchanged')
                write_priority_outputs(report, root)
                self.assertEqual((root / 'reports/icd-coverage.json').read_bytes(), b'coverage must stay unchanged')
            left = {str(p.relative_to(a)): p.read_bytes() for p in Path(a).rglob('*') if p.is_file()}
            right = {str(p.relative_to(b)): p.read_bytes() for p in Path(b).rglob('*') if p.is_file()}
            self.assertEqual(left, right)
            packed = Path(a, 'reports/icd-priorities.json.gz').read_bytes()
            self.assertEqual(json.loads(gzip.decompress(packed)), report)
            csv_bytes = Path(a, 'reports/icd-priorities.csv').read_bytes()
            self.assertTrue(csv_bytes.startswith(b'\xef\xbb\xbf'))
            records = list(csv.DictReader(io.StringIO(csv_bytes.decode('utf-8-sig'))))
            self.assertEqual(len(records), 4)
            self.assertTrue(all(r['title'].startswith("'- Official") for r in records))
            self.assertTrue(all(r['title_zh'].startswith("'- - 官方中文") for r in records))
            self.assertEqual(next(r for r in records if r['code'] == 'X2')['queue_rank'], '')
            markdown = ''.join(p.read_text(encoding='utf-8') for p in Path(a, 'docs/icd-priorities').glob('chapter-*.md'))
            for row in report['categories']:
                self.assertEqual(markdown.count(f'| [{row["code"]}]('), 1)
                self.assertEqual(row['title_zh'], titles[row['code']])
                self.assertIn('| 官方中文' + row['code'] + '<br>Official ', markdown)

    def test_markdown_rules_are_shared_linked_and_names_escape_html(self):
        s, c, r, d = fixture()
        s['rows'][3]['title'] = '- Age <5 & >1 | note'
        r['chapter_defaults']['01']['label'] = '中文章名'
        report = build_priority_report(s, c, r, d)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_priority_outputs(report, root)
            chapter = (root / 'docs/icd-priorities/chapter-01.md').read_text(encoding='utf-8')
            index = (root / 'docs/icd-priorities/index.md').read_text(encoding='utf-8')
            self.assertIn('# 01 中文章名', chapter)
            self.assertIn('WHO官方英文章名：- Official 01', chapter)
            self.assertIn('Age &lt;5 &amp; &gt;1 \\| note', chapter)
            self.assertEqual(chapter.count('祖先指定'), 1)
            self.assertEqual(chapter.count('<a id="rule-a-parent"></a>'), 1)
            self.assertEqual(chapter.count('[a-parent](#rule-a-parent)'), 2)
            self.assertIn('未知（null）', chapter)
            self.assertIn('[official](index.md#source-official)', chapter)
            self.assertIn('[a-parent](chapter-01.md#rule-a-parent)', index)
            self.assertIn('<a id="source-official"></a>', index)

    def test_entrypoint_audits_then_only_writes_priority_artifacts(self):
        s, c, r, d = fixture()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, value in {'data/icd/priorities.json': r, 'data/icd/mappings.json': [], 'data/departments.json': d,
                                'reports/icd-existing-inventory.json': {'items': []},
                                'reports/batch-01-mece.json': {'topics': []}}.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(value), encoding='utf-8')
            with patch('src.guide.priorities.load_icd', return_value=s) as official, \
                 patch('src.guide.priorities.load_chinese_titles', return_value={
                     'titles': {x['code']: '官方中文' for x in c['category_states']},
                     'manifest': {'source_url': 'https://example.org/zh', 'accessed_at': '2026-10-02',
                                  'snapshot_sha256': 'chinese-fixture'}}) as chinese, \
                 patch('src.guide.priorities.load', return_value={'departments': d}), \
                 patch('src.guide.priorities.coverage_icd', return_value=c) as audit:
                summary = priorities_icd(root)
            official.assert_called_once_with(root)
            chinese.assert_called_once_with(root, snapshot=s)
            audit.assert_called_once_with({'departments': d}, root=root)
            self.assertEqual(summary['covered_categories'], 1)
            self.assertEqual(summary['pending_categories'], 3)
            self.assertEqual(summary['provenance']['chinese_titles']['snapshot_sha256'], 'chinese-fixture')

    def test_check_mode_detects_missing_changed_and_extra_artifacts_without_writing(self):
        report = build_priority_report(*fixture())
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaisesRegex(ValidationError, 'Missing/stale'):
                check_priority_outputs(report, root)
            self.assertEqual(list(root.iterdir()), [])
            write_priority_outputs(report, root)
            self.assertEqual(check_priority_outputs(report, root)['check'], 'passed')
            changed = root / 'reports/icd-priorities.csv'
            changed.write_bytes(b'old queue')
            with self.assertRaisesRegex(ValidationError, 'icd-priorities.csv'):
                check_priority_outputs(report, root)
            self.assertEqual(changed.read_bytes(), b'old queue')
            write_priority_outputs(report, root)
            extra = root / 'docs/icd-priorities/chapter-99.md'
            extra.write_bytes(b'stale chapter')
            with self.assertRaisesRegex(ValidationError, 'chapter-99.md'):
                check_priority_outputs(report, root)
            self.assertEqual(extra.read_bytes(), b'stale chapter')

    def test_real_frozen_catalog_all_13155_leaves_across_23_chapters(self):
        snapshot = load_icd()
        _, _, rules, departments = fixture()
        leaves = [r for r in snapshot['rows'] if r['decision'] == 'included']
        rules['chapter_defaults'] = {chapter: dict(rules['chapter_defaults']['01'])
                                     for chapter in {r['chapter'] for r in leaves}}
        rules['rules'] = []
        coverage = {'release': '2026-01', 'denominator': 13155, 'covered_categories': 0, 'fraction': 0,
                    'issues': [], 'category_states': [{'code': r['code'], 'state': 'missing', 'candidates': []}
                                                    for r in leaves]}
        report = build_priority_report(snapshot, coverage, rules, departments)
        self.assertEqual(len(report['categories']), 13155)
        self.assertEqual(len({r['code'] for r in report['categories']}), 13155)
        self.assertEqual(len(report['summary']['chapters']), 23)
        self.assertTrue(all(r['priority'] == 'P2' and r['unknown_dimensions'] for r in report['categories']))


if __name__ == '__main__':
    unittest.main()
