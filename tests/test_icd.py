import copy
import unittest
from unittest.mock import patch
from src.guide.icd import (OFFICIAL_SHA256, classify_rows, coverage_icd, load_icd,
                           propose_mappings, load_chinese_titles)
from src.guide.model import ValidationError, content_hash
from tests.test_editorial import fixture


class ICDTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = load_icd()

    def test_official_archive_and_every_row_are_frozen(self):
        manifest = self.snapshot['manifest']
        self.assertEqual(manifest['snapshot_sha256'], OFFICIAL_SHA256)
        self.assertEqual(manifest['rows'], 37152)
        self.assertEqual(manifest['eligible_categories'], 13155)
        self.assertEqual(manifest['row_kinds']['category'], 35664)
        self.assertTrue(all(row['reason'] and row['release'] == '2026-01' for row in self.snapshot['rows']))

    def test_chinese_names_align_without_changing_frozen_structure(self):
        names = load_chinese_titles(snapshot=self.snapshot)
        self.assertEqual(names['manifest']['eligible_titles'], 13155)
        self.assertEqual(names['manifest']['category_count'], 35664)
        self.assertIn('急性ST段抬高型心肌梗死', names['titles']['BA41.0'])
        self.assertEqual(len(names['manifest']['parent_discrepancy_codes']), 19)
        self.assertEqual(self.snapshot['manifest']['snapshot_sha256'], OFFICIAL_SHA256)

    def test_special_conditions_included_placeholders_excluded(self):
        rows = {r['code']: r for r in self.snapshot['rows'] if r['class_kind'] == 'category'}
        for code in ('RA00.0', 'RA01.0', 'RA01.1', 'RA02', 'RA03'):
            self.assertEqual(rows[code]['decision'], 'included')
        for code in ('RA04', 'RA09', 'RA20', 'RA26'):
            self.assertEqual(rows[code]['decision'], 'excluded')

    def test_residuals_remain_in_denominator_parents_do_not(self):
        rows = self.snapshot['rows']
        self.assertGreater(sum(r['decision'] == 'included' and r['is_residual'] for r in rows), 1000)
        self.assertFalse(any(r['decision'] == 'included' and not r['is_leaf'] for r in rows))
        self.assertFalse(any(r['decision'] == 'included' and r['chapter'] in ('23', '24', '26', 'V', 'X') for r in rows))

    def test_unadjudicated_special_leaf_fails(self):
        rules = copy.deepcopy(self.snapshot['rules'])
        del rules['special_purpose_decisions']['RA02']
        with self.assertRaisesRegex(ValidationError, 'Unadjudicated'):
            classify_rows(self.snapshot['rows'], rules)

    def test_matching_names_do_not_auto_confirm_coverage(self):
        data, _ = fixture()
        data['conditions'][0]['names'] = {'en': 'Cholera'}
        proposals = propose_mappings(data, self.snapshot['rows'])
        self.assertEqual(proposals[0]['status'], 'pending')
        self.assertEqual(proposals[0]['code'], '1A00')

    def report(self, data, mappings, qualified=()):
        data = dict(data, project={'coverage_target': {'target': 1.0, 'milestone': 0.95}})
        with patch('src.guide.icd.load_icd', return_value=self.snapshot):
            return coverage_icd(data, mappings=mappings, editorial={'qualified_condition_ids': list(qualified)})

    def mapping(self, data):
        return {'condition_id': 'test-condition', 'code': '1A00', 'release': '2026-01',
                'status': 'confirmed', 'content_sha256': content_hash(data['conditions'][0]),
                'adjudication': {'method': 'semantic_scope_review', 'reviewer': 'Test reviewer',
                                 'checked_at': '2026-09-30', 'scope': 'entire_leaf_category',
                                 'rationale': 'Fixture scope only.', 'exclusions_considered': 'Fixture exclusions.'}}

    def test_full_coverage_requires_mapping_and_editorial_qualification(self):
        data, _ = fixture(); mapping = self.mapping(data)
        partial = self.report(data, [mapping])
        self.assertEqual(partial['covered_categories'], 0)
        self.assertEqual(partial['confirmed_categories'], 1)
        complete = self.report(data, [mapping], ['test-condition'])
        self.assertEqual(complete['covered_categories'], 1)
        self.assertEqual(complete['fraction'], 1 / 13155)
        self.assertFalse(complete['target_met'])

    def test_stale_mapping_does_not_qualify(self):
        data, _ = fixture(); mapping = self.mapping(data)
        data['conditions'][0]['sections']['summary']['text']['en'] += ' Changed.'
        result = self.report(data, [mapping], ['test-condition'])
        self.assertEqual(result['confirmed_categories'], 0)
        self.assertEqual(result['issues'][0]['issue'], 'missing_or_stale_semantic_adjudication')

    def test_each_category_has_a_disposition(self):
        data, _ = fixture()
        result = self.report(data, [])
        self.assertEqual(len(result['category_states']), 35664)
        self.assertEqual(len(result['gaps']), 13155)
        self.assertEqual({r['state'] for r in result['category_states']}, {'missing', 'out_of_scope'})
        self.assertEqual(result['fraction'], 0)

    def test_95_percent_is_a_milestone_not_completion(self):
        data, _ = fixture()
        rows = [r for r in self.snapshot['rows'] if r['decision'] == 'included'][:20]
        snapshot = dict(self.snapshot, rows=rows)
        conditions, mappings = [], []
        for i, row in enumerate(rows[:19]):
            condition = copy.deepcopy(data['conditions'][0]); condition['id'] = f'topic-{i}'
            conditions.append(condition)
            mapping = self.mapping({'conditions': [condition]})
            mapping.update(condition_id=condition['id'], code=row['code'])
            mappings.append(mapping)
        data.update(conditions=conditions, project={'coverage_target': {'target': 1.0, 'milestone': 0.95}})
        with patch('src.guide.icd.load_icd', return_value=snapshot):
            result = coverage_icd(data, mappings=mappings, editorial={'qualified_condition_ids': [c['id'] for c in conditions]})
        self.assertEqual(result['fraction'], 0.95)
        self.assertTrue(result['milestone_met'])
        self.assertFalse(result['target_met'])
        self.assertEqual(result['target'], 1.0)

    def test_duplicate_mapping_rejected(self):
        data, _ = fixture(); mapping = self.mapping(data)
        with self.assertRaisesRegex(ValidationError, 'duplicate'):
            self.report(data, [mapping, mapping])


if __name__ == '__main__':
    unittest.main()
