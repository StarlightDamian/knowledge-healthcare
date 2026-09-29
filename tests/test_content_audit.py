"""Editorial record regressions; these tests do not establish medical validity."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.guide.content_audit import content_audit
from src.guide.model import FIELDS, load


class ContentAuditTests(unittest.TestCase):
    def setUp(self):
        self.data=copy.deepcopy(load())
        self.data['conditions']=self.data['conditions'][:1]
        topic=self.data['conditions'][0]
        self.record={
            'condition_id':topic['id'],
            'inspected_sources':[{'source_id':sid} for sid in topic['source_ids']],
            'sections':{field:{'source_ids':section['source_ids'],
                               'locators':{sid:'Relevant heading' for sid in section['source_ids']}}
                        for field,section in topic['sections'].items()}}

    def audit(self, records):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);directory=root/'reports/content-expansion';directory.mkdir(parents=True)
            (directory/'batch-a.json').write_text(json.dumps(records),encoding='utf-8')
            with patch('src.guide.content_audit.load',return_value=self.data),patch('src.guide.content_audit.validate'):
                return content_audit(root)

    def test_list_structure_is_not_coverage_or_medical_review(self):
        report=self.audit([self.record])
        self.assertEqual(report['records'][0]['bilingual_fields_with_lists'],len(FIELDS)*2)
        self.assertEqual(report['clinically_reviewed'],0)
        self.assertIsNone(report['all_condition_coverage'])
        self.assertEqual(report['issues'],[])

    def test_omitted_translation_list_is_reported(self):
        self.data['conditions'][0]['sections']['care']['text']['en']='One sentence only.'
        issues=self.audit([self.record])['issues']
        self.assertTrue(any(x.get('field')=='care' and x.get('locale')=='en' for x in issues))

    def test_uninspected_and_unmapped_sources_are_reported(self):
        self.record['inspected_sources']=[]
        self.record['sections']['diet']['locators']={'unrelated-source':'Wrong heading'}
        kinds={x['issue'] for x in self.audit([self.record])['issues']}
        self.assertIn('section_references_uninspected_source',kinds)
        self.assertIn('source_locator_mapping_mismatch',kinds)

    def test_missing_and_duplicate_records_are_reported(self):
        self.assertIn('missing_editorial_record',{x['issue'] for x in self.audit([])['issues']})
        self.assertIn('duplicate_editorial_record',{x['issue'] for x in self.audit([self.record,self.record])['issues']})
