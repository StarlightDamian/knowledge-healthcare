"""Purely synthetic attestation fixtures. They are not genuine clinician reviews."""
import copy
import unittest
from datetime import date
from src.guide.model import load,clinical_record_gate,content_hash,text_hash,canonical_hash,ValidationError,FIELDS

class RecordedClinicalGateTests(unittest.TestCase):
 def fixture(self):
  data=copy.deepcopy(load());c=data['conditions'][0]
  c['review'].update(status='medically_reviewed',medical_reviewed_at='2026-09-29',next_editorial_review_due='2027-09-29')
  c['clinical_region']='CN'
  for loc in c['localizations'].values():loc.update(status='medically_reviewed',clinician_reviewed=True)
  data['reviewers']=[{'id':'synthetic-physician','role':'physician','credential_verified':True},
                     {'id':'synthetic-pharmacist','role':'pharmacist','credential_verified':True}]
  sm={s['id']:s for s in data['sources']}
  # This fixture models two independently supported sources; real draft sections
  # now cite only the sources relevant to each section and may legitimately cite one.
  fixture_sources=list({sm[sid]['independence_group']:sid for sid in c['source_ids']}.values())[:2]
  self.assertEqual(len(fixture_sources),2)
  for key in FIELDS:
   sec=c['sections'][key];sec['support_status']='verified';sec['source_ids']=fixture_sources.copy()
   sec['verification']=[{'source_id':sid,'reviewer_id':'synthetic-physician','text_sha256':text_hash(sec),
     'source_sha256':canonical_hash(sm[sid]),'support':'full','locator':'Synthetic fixture only',
     'reviewed_at':'2026-09-29'} for sid in sec['source_ids']]
  self.resign(c)
  return c,data
 def resign(self,c):
  c['review']['approvals']=[{'reviewer_id':rid,'content_sha256':content_hash(c),
   'attestation_url':'https://example.org/synthetic-test-only','reviewed_at':'2026-09-29'}
    for rid in ['synthetic-physician','synthetic-pharmacist']]
 def gate(self,c,d):return clinical_record_gate(c,d,date(2026,9,29))
 def test_synthetic_record_shape_can_pass(self):
  c,d=self.fixture();self.gate(c,d)
 def test_one_source_cannot_pass_clinical_gate(self):
  c,d=self.fixture();c['sections']['summary']['source_ids']=c['sections']['summary']['source_ids'][:1]
  self.resign(c);self.assertRaises(ValidationError,self.gate,c,d)
 def test_content_change_invalidates_signature_binding(self):
  c,d=self.fixture();c['sections']['diet']['text']['en']='Changed';self.assertRaises(ValidationError,self.gate,c,d)
 def test_source_change_invalidates_support_binding(self):
  c,d=self.fixture();sid=c['sections']['summary']['source_ids'][0];next(s for s in d['sources'] if s['id']==sid)['title']='Changed';self.assertRaises(ValidationError,self.gate,c,d)
 def test_same_reviewer_twice_not_two_people(self):
  c,d=self.fixture();c['review']['approvals']=[c['review']['approvals'][0]]*2;self.assertRaises(ValidationError,self.gate,c,d)
 def test_unverified_credentials_blocked(self):
  c,d=self.fixture();d['reviewers'][0]['credential_verified']=False;self.assertRaises(ValidationError,self.gate,c,d)
 def test_unreviewed_translation_blocked(self):
  c,d=self.fixture();c['localizations']['en']['clinician_reviewed']=False;self.resign(c);self.assertRaises(ValidationError,self.gate,c,d)
 def test_pending_section_blocked(self):
  c,d=self.fixture();c['sections']['diet']['support_status']='pending_claim_verification';self.resign(c);self.assertRaises(ValidationError,self.gate,c,d)
 def test_at_least_one_physician_record_required(self):
  c,d=self.fixture();d['reviewers'][0]['role']='pharmacist';self.assertRaises(ValidationError,self.gate,c,d)
if __name__=='__main__':unittest.main()
