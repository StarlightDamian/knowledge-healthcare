"""Isolated educational fixtures, not clinical content or review attestations."""
import copy
import json
import re
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from src.guide.build import build, bundle
from src.guide.knowledge import AGE_PARTITION, load_knowledge, validate_knowledge
from src.guide.model import FIELDS, ValidationError, load, validate

TODAY = date(2026, 9, 29)


def bilingual(text='Fixture'):
    return {'zh-CN': '测试：' + text, 'en': text}


def section(source_id):
    return {'id': 'overview', 'title': bilingual(), 'text': bilingual(), 'source_ids': [source_id]}


def knowledge_fixture():
    modules = {}
    for key, eid in [('cancer', 'example-cancer'), ('lifecycle', 'tobacco')]:
        sid = key + '-source'
        modules[key] = {
            'id': key, 'title': bilingual(), 'intro': bilingual(),
            'groups': [{'id': 'general', 'label': bilingual()}],
            'sections': [section(sid)],
            'entries': [{'id': eid, 'group_id': 'general', 'title': bilingual(),
                         'summary': bilingual(), 'sections': [section(sid)],
                         'condition_ids': ['sample-condition'],
                         'factor_ids': ['tobacco'] if key == 'cancer' else [], 'source_ids': [sid]}],
            'sources': [{'id': sid, 'title': 'Fixture source', 'url': 'https://example.org/evidence',
                         'accessed_at': '2026-09-29', 'scope': 'Synthetic validation fixture'}],
            'review': {'status': 'editorial', 'updated_at': '2026-09-29'}
        }
    modules['lifecycle']['stages'] = [
        {'id': f'age-{lower}', 'title': bilingual(), 'kind': 'age',
         'age_min': lower, 'age_max': upper, 'intro': bilingual(),
         'sections': [section('lifecycle-source')], 'factor_ids': ['tobacco']}
        for lower, upper in AGE_PARTITION
    ] + [{'id': 'pregnancy', 'title': bilingual(), 'kind': 'overlay',
          'age_min': None, 'age_max': None, 'intro': bilingual(),
          'sections': [section('lifecycle-source')], 'factor_ids': ['tobacco']}]
    return modules


def write_project(root, knowledge):
    """Write a minimal complete project under a TemporaryDirectory, never the workspace."""
    sources = [{'id': sid, 'title': 'Fixture source', 'independence_group': sid,
                'url': 'https://example.org/evidence', 'accessed_at': '2026-09-29',
                'publication_date': None} for sid in ['source-a', 'source-b']]
    condition = {
        'id': 'sample-condition', 'schema_version': '1.0.0', 'kind': 'condition',
        'primary_domain': 'general', 'names': bilingual(), 'limitations': bilingual(),
        'reference_urgency': 'context_dependent', 'departments': ['primary-care'],
        'symptom_terms': [bilingual()], 'aliases': {'zh-CN': [], 'en': []},
        'source_ids': ['source-a', 'source-b'], 'related_ids': [],
        'sections': {key: {'text': bilingual(), 'source_ids': ['source-a'],
                           'support_status': 'pending_claim_verification'} for key in FIELDS},
        'review': {'status': 'editorial_draft', 'medical_reviewed_at': None,
                   'editorial_updated_at': '2026-09-29', 'next_editorial_review_due': '2027-09-29'}
    }
    files = {
        'conditions/sample-condition.json': condition, 'evidence/sources.json': sources,
        'evidence/studies.json': [], 'evidence/reviewers.json': [], 'evidence/conflicts.json': [],
        'taxonomy.json': [{'id': 'general'}], 'departments.json': {'primary-care': bilingual()},
        'department-groups.json': [{'id': 'general', 'label': bilingual(), 'departments': ['primary-care']}],
        'fields.json': [], 'safety/rules.json': {'rules': [], 'status': 'draft'},
        'locales/ui.json': {'en': {'dir': 'ltr', 'strings': {}}, 'zh-CN': {'dir': 'ltr', 'strings': {}}},
        'project.json': {'version': 'fixture', 'clinical_release': {'authorized': False}},
        'catalog/backlog.json': [], **{f'knowledge/{key}.json': value for key, value in knowledge.items()}
    }
    for name, value in files.items():
        target = root / 'data' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
    web = root / 'src/web'
    web.mkdir(parents=True)
    for name in ['search', 'safety', 'export', 'text', 'navigation', 'knowledge', 'api', 'app']:
        (web / f'{name}.mjs').write_text(f'// module:{name}\nexport function fixture_{name}() {{}}\n', encoding='utf-8')
    (web / 'style.css').write_text('body { color: black; }', encoding='utf-8')
    (web / 'template.html').write_text(
        '<meta http-equiv="Content-Security-Policy" content="{{CSP}}"><style>{{STYLE}}</style>'
        '<script id="payload" type="application/json">{{PAYLOAD}}</script><script>{{SCRIPT}}</script>',
        encoding='utf-8')


class KnowledgeValidationTests(unittest.TestCase):
    def setUp(self):
        self.data = knowledge_fixture()

    def check(self, data=None, mode='preview'):
        return validate_knowledge(self.data if data is None else data, {'sample-condition'}, TODAY, mode)

    def test_counts_are_separate_and_overlay_is_not_an_age_partition(self):
        result = self.check()
        self.assertEqual((result['modules'], result['entries'], result['sections'], result['stages']), (2, 2, 11, 7))
        self.assertEqual(result['by_module']['cancer']['entries'], 1)

    def test_duplicate_module_entry_group_section_and_source_ids_rejected(self):
        mutations = [
            lambda d: d['cancer'].update(id='lifecycle'),
            lambda d: d['cancer']['entries'].append(copy.deepcopy(d['cancer']['entries'][0])),
            lambda d: d['cancer']['entries'][0].update(id='tobacco'),
            lambda d: d['cancer']['groups'].append(copy.deepcopy(d['cancer']['groups'][0])),
            lambda d: d['cancer']['sections'].append(copy.deepcopy(d['cancer']['sections'][0])),
            lambda d: d['cancer']['sources'].append(copy.deepcopy(d['cancer']['sources'][0])),
            lambda d: d['lifecycle']['stages'].append(copy.deepcopy(d['lifecycle']['stages'][0]))
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                data = copy.deepcopy(self.data); mutate(data)
                self.assertRaises(ValidationError, self.check, data)

    def test_all_required_translations_checked(self):
        module = self.data['lifecycle']
        targets = [module['title'], module['intro'], module['groups'][0]['label'],
                   module['sections'][0]['title'], module['sections'][0]['text'],
                   module['entries'][0]['title'], module['entries'][0]['summary'],
                   module['entries'][0]['sections'][0]['title'], module['entries'][0]['sections'][0]['text'],
                   module['stages'][0]['title'], module['stages'][0]['intro'],
                   module['stages'][0]['sections'][0]['title'], module['stages'][0]['sections'][0]['text']]
        for index, text in enumerate(targets):
            for lang in ['zh-CN', 'en']:
                with self.subTest(target=index, language=lang):
                    original = text[lang]; text[lang] = ' '
                    self.assertRaises(ValidationError, self.check)
                    text[lang] = original

    def test_entry_has_one_known_group(self):
        for group in ['unknown', ['general'], None]:
            with self.subTest(group=group):
                self.data['cancer']['entries'][0]['group_id'] = group
                self.assertRaises(ValidationError, self.check)

    def test_source_urls_and_dates_are_validated(self):
        source = self.data['cancer']['sources'][0]
        for value in ['http://example.org', 'javascript:alert(1)', 'https://user:pass@example.org', None]:
            with self.subTest(url=value):
                source['url'] = value
                self.assertRaises(ValidationError, self.check)
        source['url'] = 'https://example.org'
        for value in ['2099-01-01', '2026-02-30', None]:
            with self.subTest(date=value):
                source['accessed_at'] = value
                self.assertRaises(ValidationError, self.check)

    def test_section_evidence_cannot_escape_entry_scope(self):
        module = self.data['cancer']
        extra = copy.deepcopy(module['sources'][0]); extra['id'] = 'other-source'
        module['sources'].append(extra)
        module['entries'][0]['sections'][0]['source_ids'] = ['other-source']
        with self.assertRaisesRegex(ValidationError, 'out-of-scope'):
            self.check()
        module['entries'][0]['source_ids'].append('other-source')
        self.check()

    def test_unknown_and_empty_sources_rejected_at_every_level(self):
        targets = [self.data['cancer']['sections'][0], self.data['cancer']['entries'][0],
                   self.data['cancer']['entries'][0]['sections'][0], self.data['lifecycle']['stages'][0]['sections'][0]]
        for index, row in enumerate(targets):
            original = row['source_ids']
            for refs in [[], ['absent'], ['lifecycle-source', 'lifecycle-source']]:
                with self.subTest(target=index, references=refs):
                    row['source_ids'] = refs
                    self.assertRaises(ValidationError, self.check)
            row['source_ids'] = original

    def test_condition_and_canonical_factor_references(self):
        entry = self.data['cancer']['entries'][0]
        for field in ['condition_ids', 'factor_ids']:
            with self.subTest(field=field):
                original = entry[field]; entry[field] = ['absent']
                self.assertRaises(ValidationError, self.check)
                entry[field] = original
        self.data['lifecycle']['stages'][0]['factor_ids'] = ['example-cancer']
        self.assertRaises(ValidationError, self.check)

    def test_age_gaps_overlaps_open_ends_and_wrong_partition_rejected(self):
        for bounds in [(0, 3), (0, 5), (1, 4), (0, None), (True, 4), (0, 4.0)]:
            with self.subTest(bounds=bounds):
                data = copy.deepcopy(self.data)
                data['lifecycle']['stages'][0].update(age_min=bounds[0], age_max=bounds[1])
                self.assertRaises(ValidationError, self.check, data)
        self.data['lifecycle']['stages'][5]['age_max'] = 120
        self.assertRaises(ValidationError, self.check)

    def test_age_order_and_display_ids_do_not_define_partition(self):
        stages = self.data['lifecycle']['stages']
        stages.reverse()
        for index, stage in enumerate(stages): stage['id'] = f'stage-{index}'
        self.check()

    def test_pregnancy_overlay_cannot_claim_age_bounds(self):
        self.data['lifecycle']['stages'][-1].update(age_min=18, age_max=39)
        with self.assertRaisesRegex(ValidationError, 'overlay'):
            self.check()

    def test_missing_module_rejected(self):
        del self.data['lifecycle']
        self.assertRaises(ValidationError, self.check)

    def test_status_rename_is_not_medical_review(self):
        for value in ['medically_reviewed', 'approved', None]:
            with self.subTest(status=value):
                self.data['cancer']['review']['status'] = value
                self.assertRaises(ValidationError, self.check)

    def test_editorial_knowledge_blocks_clinical_mode(self):
        with self.assertRaisesRegex(ValidationError, 'Knowledge modules lack clinical sign-off'):
            self.check(mode='clinical')


class KnowledgeIntegrationTests(unittest.TestCase):
    def test_load_and_stats_keep_condition_counts_separate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); fixture = knowledge_fixture(); write_project(root, fixture)
            data = load(root)
            self.assertEqual(data['knowledge'], fixture)
            self.assertEqual(load_knowledge(root), fixture)
            stats = validate(data, today=TODAY)
            self.assertEqual((stats['conditions'], stats['sources'], stats['total_sections']), (1, 2, 14))
            self.assertEqual((stats['clinically_reviewed'], stats['verified_sections']), (0, 0))
            self.assertEqual(stats['knowledge']['entries'], 2)
            self.assertIsNone(stats['daily_need_coverage'])
            # Even if the condition gate has independently succeeded, new draft modules still block release.
            with patch('src.guide.model.clinical_record_gate'):
                with self.assertRaisesRegex(ValidationError, 'Knowledge modules lack clinical sign-off'):
                    validate(data, mode='clinical', today=TODAY)

    def test_online_shell_excludes_bodies_without_catalog_inflation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); fixture = knowledge_fixture()
            fixture['cancer']['intro']['en'] = '</script><script>bad()</script>'
            write_project(root, fixture)
            first = root / 'first.html'; second = root / 'second.html'
            build(root, out=first); build(root, out=second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            html = first.read_text(encoding='utf-8')
            self.assertNotIn('<script>bad()', html)
            payload = json.loads(re.search(r'<script id="payload" type="application/json">(.*?)</script>', html).group(1))
            self.assertEqual(payload['conditions'], [])
            self.assertEqual(set(payload['knowledge']), {'cancer', 'lifecycle'})
            self.assertTrue(all('entries' not in value and 'sections' not in value for value in payload['knowledge'].values()))
            self.assertIn("connect-src 'self'", html)
            self.assertIn("form-action 'self'", html)
            script = bundle(root)
            self.assertLess(script.index('// module:text'), script.index('// module:knowledge'))
            self.assertLess(script.index('// module:knowledge'), script.index('// module:app'))
            self.assertNotIn('import ', script)
            catalog = json.loads((root / 'data/catalog/index.json').read_text(encoding='utf-8'))
            self.assertEqual([row['id'] for row in catalog['topics']], ['sample-condition'])


if __name__ == '__main__':
    unittest.main()
