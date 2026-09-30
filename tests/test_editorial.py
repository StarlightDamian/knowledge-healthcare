import copy
import unittest
from datetime import date
from src.guide.editorial import (editorial_audit, editorial_sections, make_editorial_record,
                                require_editorial_changes)
from src.guide.model import FIELDS, ValidationError, canonical_hash, load


def fixture():
    sources = [{'id': 'authority-a', 'url': 'https://a.example/clinical', 'independence_group': 'a',
                'retrieval_status': 'article_retrieved'},
               {'id': 'authority-b', 'url': 'https://b.example/clinical', 'independence_group': 'b',
                'retrieval_status': 'page_opened'}]
    text = {'zh-CN': '测试病症说明。\n\n- 发生危险变化时就医。',
            'en': 'Test condition explanation.\n\n- Seek care for dangerous changes.'}
    condition = {'id': 'test-condition', 'review': {'status': 'editorial_draft'},
                 'sections': {key: {'text': dict(text), 'source_ids': ['authority-a', 'authority-b']}
                              for key in FIELDS}}
    data = {'conditions': [condition], 'sources': sources, 'knowledge': {}}
    records = []
    for key in FIELDS:
        record = make_editorial_record(data, {'kind': 'condition', 'id': condition['id'], 'section': key}, key)
        record.update(status='cross_checked', checked_at='2026-09-30', checker='Test editor',
                      claim_inventory='all_medical_claims_in_section')
        record['supports'] = [
            {'source_id': source['id'], 'source_metadata_sha256': canonical_hash(source),
             'locator': 'Test source section 1', 'source_version': 'Test 2026 edition',
             'accessed_at': '2026-09-30', 'population': 'Adults', 'region': 'Test region',
             'independence_group': source['independence_group'], 'assessment': 'Supports the fixture action.',
             'upstream_evidence': ['Fixture only'], 'relation': 'supports'} for source in sources]
        record['claims'] = [{'id': 'test-action', 'kind': 'action', 'text': dict(text),
                             'supports': [{'source_id': s['id'], 'locator': 'Section 1',
                                           'assessment': 'Supports fixture action'} for s in sources]}]
        record['independence'] = {'status': 'independent_editorial_sources', 'rationale': 'Two independent test authors.',
                                  'underlying_evidence': 'not_assessed'}
        record['dispute'] = {'status': 'none', 'resolution': 'No disagreement in this fixture.'}
        record['adversarial_review'] = {'status': 'accepted', 'author': 'Author role', 'reviewer': 'Other reviewer',
                                        'checked_at': '2026-09-30', 'findings': [],
                                        'original_sources_reopened': [s['id'] for s in sources],
                                        'resolution': 'Fixture reviewed.'}
        records.append(record)
    return data, records


class EditorialTests(unittest.TestCase):
    def audit(self, data, records):
        return editorial_audit(data=data, records=records, today=date(2026, 9, 30))

    def test_actual_baseline_does_not_gain_review_from_migration(self):
        result = self.audit(load(), [])
        self.assertGreaterEqual(result['conditions'], 72)
        self.assertEqual(result['qualified_condition_ids'], [])
        self.assertEqual(result['legacy_spot_checks']['promoted_to_section_verification'], 0)

    def test_complete_records_qualify_only_editorially(self):
        data, records = fixture()
        result = self.audit(data, records)
        self.assertEqual(result['qualified_condition_ids'], ['test-condition'])
        self.assertEqual(result['clinical_reviewed_conditions'], 0)
        self.assertEqual(result['issues'], [])

    def test_action_needs_two_independent_sources_not_two_links(self):
        data, records = fixture()
        records[0]['claims'][0]['supports'].pop()
        result = self.audit(data, records)
        self.assertEqual(result['qualified_condition_ids'], [])
        self.assertIn('claim_requires_two_independent_sources', [i['issue'] for i in result['issues']])

    def test_same_origin_cannot_pass(self):
        data, records = fixture()
        data['sources'][1]['independence_group'] = 'a'
        for record in records:
            record['supports'][1].update(independence_group='a', source_metadata_sha256=canonical_hash(data['sources'][1]))
        self.assertEqual(self.audit(data, records)['qualified_condition_ids'], [])

    def test_content_and_source_change_invalidate_attestation(self):
        for edit in ('text', 'source'):
            data, records = fixture()
            if edit == 'text':
                data['conditions'][0]['sections']['summary']['text']['en'] += ' Changed.'
            else:
                data['sources'][0]['url'] = 'https://a.example/changed'
            self.assertEqual(self.audit(data, records)['qualified_condition_ids'], [])

    def test_selected_claims_are_not_full_section_review(self):
        data, records = fixture()
        records[0]['scope'] = 'selected_claims'
        self.assertEqual(self.audit(data, records)['qualified_condition_ids'], [])

    def test_duplicate_target_does_not_qualify(self):
        data, records = fixture()
        duplicate = copy.deepcopy(records[0]); duplicate['id'] = 'another-record'
        self.assertEqual(self.audit(data, records + [duplicate])['qualified_condition_ids'], [])

    def test_author_cannot_self_attest_independent_review(self):
        data, records = fixture()
        records[0]['adversarial_review']['reviewer'] = 'Author role'
        self.assertEqual(self.audit(data, records)['qualified_condition_ids'], [])

    def test_open_source_questions_prevent_complete_verification(self):
        data, records = fixture()
        records[0]['unresolved_questions'] = ['The second source does not support this action.']
        result = self.audit(data, records)
        self.assertEqual(result['qualified_condition_ids'], [])
        self.assertIn('unresolved_source_questions', [i['issue'] for i in result['issues']])

    def test_unresolved_or_unread_source_does_not_qualify(self):
        data, records = fixture()
        records[0]['dispute']['status'] = 'unresolved'
        data['sources'][0]['retrieval_status'] = 'metadata_only'
        self.assertEqual(self.audit(data, records)['qualified_condition_ids'], [])

    def test_translated_claim_must_bind_to_actual_text(self):
        data, records = fixture()
        records[0]['claims'][0]['text']['en'] = 'Fabricated translation not in source text.'
        self.assertEqual(self.audit(data, records)['qualified_condition_ids'], [])

    def test_changed_source_metadata_is_publication_gate_input(self):
        data, _ = fixture()
        baseline = copy.deepcopy(data)
        data['sources'][0]['url'] = 'https://a.example/new'
        with self.assertRaisesRegex(ValidationError, 'cross-checks'):
            require_editorial_changes(data, baseline, records=[])

    def test_unchanged_baseline_preserves_its_real_status(self):
        data, _ = fixture()
        result = require_editorial_changes(data, copy.deepcopy(data), records=[])
        self.assertEqual(result['qualified_condition_ids'], [])

    def test_module_and_entry_namespaces_are_distinct(self):
        data, _ = fixture()
        section = {'id': 'summary', 'text': {'zh-CN': '说明', 'en': 'Explanation'}, 'source_ids': []}
        data['knowledge'] = {'test': {'sources': [], 'review': {}, 'sections': [section],
                                      'entries': [{'id': 'test', 'sections': [section]}]}}
        index = editorial_sections(data)
        self.assertIn('module/test/summary', index)
        self.assertIn('knowledge_entry/test/test/summary', index)


if __name__ == '__main__':
    unittest.main()
