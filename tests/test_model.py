import copy
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from src.guide.model import ROOT,load,validate,ValidationError,canonical_hash,content_hash,text_hash,safe_url,valid_date,FIELDS
from src.guide.build import script_json,bundle,sha_csp,build
from src.guide.evidence import impact,check_links
from src.guide.coverage import coverage
from src.guide.package import manifest,verify,package
from src.guide.__main__ import main

class ModelTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=load()
 def altered(self):return copy.deepcopy(self.data)
 def test_actual_counts(self):
  r=validate(self.data,today=date(2026,10,3));self.assertEqual((r['conditions'],r['clinically_reviewed'],r['verified_sections']),(98,0,434));self.assertIsNone(r['daily_need_coverage'])
 def test_clinical_build_blocked(self):
  with self.assertRaisesRegex(ValidationError,'clinical sign-off'):validate(self.data,'clinical')
 def test_duplicate_topic(self):
  d=self.altered();d['conditions'].append(d['conditions'][0]);self.assertRaises(ValidationError,validate,d)
 def test_duplicate_source(self):
  d=self.altered();d['sources'].append(d['sources'][0]);self.assertRaises(ValidationError,validate,d)
 def test_no_empty_database(self):
  d=self.altered();d['conditions']=[];self.assertRaises(ValidationError,validate,d)
 def test_required_section(self):
  d=self.altered();del d['conditions'][0]['sections']['medications'];self.assertRaises(ValidationError,validate,d)
 def test_empty_translation(self):
  d=self.altered();d['conditions'][0]['sections']['diet']['text']['en']='';self.assertRaises(ValidationError,validate,d)
 def test_unknown_source(self):
  d=self.altered();d['conditions'][0]['source_ids'][0]='nonexistent';self.assertRaises(ValidationError,validate,d)
 def test_same_source_family(self):
  d=self.altered();c=d['conditions'][0];sm={s['id']:s for s in d['sources']}
  for i in c['source_ids']:sm[i]['independence_group']='same'
  self.assertRaises(ValidationError,validate,d)
 def test_unknown_related(self):
  d=self.altered();d['conditions'][0]['related_ids']=['nothing'];self.assertRaises(ValidationError,validate,d)
 def test_self_related(self):
  d=self.altered();c=d['conditions'][0];c['related_ids']=[c['id']];self.assertRaises(ValidationError,validate,d)
 def test_unknown_department(self):
  d=self.altered();d['conditions'][0]['departments']=['not-a-real-key'];self.assertRaises(ValidationError,validate,d)
 def test_duplicate_department_membership(self):
  d=self.altered();d['department_groups'][1]['departments'].append(d['department_groups'][0]['departments'][0]);self.assertRaises(ValidationError,validate,d)
 def test_missing_department_group(self):
  d=self.altered();d['department_groups'][0]['departments'].pop();self.assertRaises(ValidationError,validate,d)
 def test_unknown_department_group(self):
  d=self.altered();d['department_groups'][0]['departments'].append('nonexistent');self.assertRaises(ValidationError,validate,d)
 def test_invalid_domain(self):
  d=self.altered();d['conditions'][0]['primary_domain']='magic';self.assertRaises(ValidationError,validate,d)
 def test_invalid_kind(self):
  d=self.altered();d['conditions'][0]['kind']='patient';self.assertRaises(ValidationError,validate,d)
 def test_unsafe_url(self):
  d=self.altered();d['sources'][0]['url']='javascript:alert(1)';self.assertRaises(ValidationError,validate,d)
 def test_fake_medical_date(self):
  d=self.altered();d['conditions'][0]['review']['medical_reviewed_at']='2026-09-29';self.assertRaises(ValidationError,validate,d)
 def test_rename_status_is_not_signoff(self):
  d=self.altered();c=d['conditions'][0];c['review']['status']='medically_reviewed';c['review']['medical_reviewed_at']='2026-09-29';c['clinical_region']='CN';self.assertRaises(ValidationError,validate,d)
 def test_overdue_drafts_warn(self):
  r=validate(self.data,today=date(2027,1,4));self.assertEqual(len(r['warnings']),98)
 def test_missing_locale_key(self):
  d=self.altered();del d['locales']['fr']['strings']['sourceInfo'];self.assertRaises(ValidationError,validate,d)
 def test_script_json_escaping(self):
  x={'x':'</script><script>alert(1)</script>&\u2028'};s=script_json(x);self.assertNotIn('<',s);self.assertEqual(json.loads(s),x)
 def test_bundle_uses_api_without_persisting_inputs(self):
  s=bundle(ROOT);self.assertIn('class GuideAPI',s);self.assertNotIn('localStorage',s);self.assertNotIn('import ',s)
 def test_source_impact(self):
  r=impact(self.data,'common-cold-nhs');self.assertEqual(r[0]['id'],'common-cold')
  expected={key for key,sec in next(c for c in self.data['conditions'] if c['id']=='common-cold')['sections'].items() if 'common-cold-nhs' in sec['source_ids']}
  self.assertEqual(set(r[0]['fields']),expected);self.assertGreater(len(expected),0)
 def test_unknown_impact(self):self.assertRaises(ValidationError,impact,self.data,'bad-id')
 def test_link_limit_validation(self):self.assertRaises(ValidationError,check_links,self.data,0)
 def test_future_access(self):
  d=self.altered();d['sources'][0]['accessed_at']='2099-01-01';self.assertRaises(ValidationError,validate,d)
 def test_safe_url(self):
  for x in ['http://example.com','https://u:p@example.com','javascript:x',None,'https://example.com/\n']:self.assertFalse(safe_url(x))
  self.assertTrue(safe_url('https://www.nhs.uk/'))
 def test_dates(self):
  for x in ['2026-2-2','2026-02-30',None]:self.assertFalse(valid_date(x))
  self.assertTrue(valid_date('2026-02-02'))
 def test_backlog_not_implemented(self):
  self.assertEqual(len(self.data['backlog']),188);self.assertTrue(all(not c['include_in_search'] and not c['include_in_coverage'] for c in self.data['backlog']))
 def test_stable_hash(self):self.assertEqual(canonical_hash({'a':1,'b':2}),canonical_hash({'b':2,'a':1}))
 def test_medical_review_hash_tracks_content(self):
  c=copy.deepcopy(self.data['conditions'][0]);h=content_hash(c);c['sections']['diet']['text']['en']='Edited';self.assertNotEqual(content_hash(c),h)
 def test_medical_review_hash_excludes_review(self):
  c=copy.deepcopy(self.data['conditions'][0]);h=content_hash(c);c['review']['approvals']=[{}];self.assertEqual(content_hash(c),h)
 def test_reproducible_build(self):
  with tempfile.TemporaryDirectory() as temp:
   a=Path(temp)/'a.html';b=Path(temp)/'b.html';build(ROOT,out=a);build(ROOT,out=b);self.assertEqual(a.read_bytes(),b.read_bytes())
 def test_csp_hash(self):self.assertTrue(sha_csp('test').startswith("'sha256-"))
 def test_cli_validation(self):self.assertEqual(main(['validate']),0)
 def test_cli_clinical_failure(self):self.assertEqual(main(['validate','--mode','clinical']),2)
 def test_json_schema_all_records(self):
  try:from jsonschema import Draft202012Validator,FormatChecker
  except ImportError:self.skipTest('optional jsonschema dependency not installed')
  for filename,records in [('condition',self.data['conditions']),('source',self.data['sources']),('safety-rule',self.data['rules']['rules'])]:
   v=Draft202012Validator(json.loads((ROOT/'schemas'/f'{filename}.schema.json').read_text()),format_checker=FormatChecker())
   for row in records:
    with self.subTest(schema=filename,id=row['id']):v.validate(row)

class CoverageAndIntegrityTests(unittest.TestCase):
 def test_coverage_synthetic_not_population(self):
  d=load()
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'x.csv';p.write_text('condition_id,weight,group,adjudicated,dataset_kind\ncommon-cold,2,adult,true,synthetic\nunknown,1,adult,true,synthetic\n')
   self.assertRaises(ValidationError,coverage,d,p)
   r=coverage(d,p,True);self.assertAlmostEqual(r['draft_topic_mapping'],2/3);self.assertEqual(r['clinically_reviewed_mapping'],0)
 def test_coverage_invalid_weights(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'x.csv'
   for weight in ['NaN','inf','-1','0','abc']:
    p.write_text(f'condition_id,weight,group,adjudicated,dataset_kind\ncommon-cold,{weight},adult,true,representative\n');self.assertRaises(ValidationError,coverage,load(),p)
 def test_coverage_adjudication(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'x.csv';p.write_text('condition_id,weight,group,adjudicated,dataset_kind\ncommon-cold,1,adult,false,representative\n');self.assertRaises(ValidationError,coverage,load(),p)
 def test_manifest_detects_tamper(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t);(r/'医学.txt').write_text('hello',encoding='utf-8');manifest(r);verify(r);(r/'医学.txt').write_text('tampered',encoding='utf-8');self.assertRaises(ValueError,verify,r)
 def test_manifest_detects_extra_file(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t);(r/'a.txt').write_text('hello');manifest(r);(r/'b.txt').write_text('extra');self.assertRaises(ValueError,verify,r)
 def test_archive_reproducible(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t)/'repo';r.mkdir();(r/'a.txt').write_text('hello');a=Path(t)/'a.zip';b=Path(t)/'b.zip';package(r,a);package(r,b);self.assertEqual(a.read_bytes(),b.read_bytes())
if __name__=='__main__':unittest.main()
