"""Reproducible structural/editorial audit, never a medical or ICD coverage score."""
from __future__ import annotations
import re
from pathlib import Path
from .model import ROOT,FIELDS,load,validate,read_json,content_hash,canonical_hash


def content_audit(root: Path=ROOT) -> dict:
    root=Path(root)
    data=load(root)
    validate(data)
    records={}
    issues=[]
    for path in sorted((root/'reports/content-expansion').glob('batch-?.json')):
        for record in read_json(path):
            cid=record['condition_id']
            if cid in records:issues.append({'condition_id':cid,'issue':'duplicate_editorial_record'})
            records[cid]=record
    sources={s['id']:s for s in data['sources']}
    topics=[]
    for condition in data['conditions']:
        cid=condition['id'];record=records.get(cid)
        if not record:issues.append({'condition_id':cid,'issue':'missing_editorial_record'})
        inspected={s['source_id'] for s in (record or {}).get('inspected_sources',[])}
        fields=(record or {}).get('sections',{})
        lists=0;zh_chars=0;en_words=0
        for field in FIELDS:
            section=condition['sections'][field]
            detail=fields.get(field,{})
            for locale in ('zh-CN','en'):
                text=section['text'][locale]
                if re.search(r'^- .+',text,re.M):lists+=1
                else:issues.append({'condition_id':cid,'field':field,'locale':locale,'issue':'no_list_manual_readability_check_needed'})
            zh_chars+=len(section['text']['zh-CN'])
            en_words+=len(section['text']['en'].split())
            locators=detail.get('locators',{})
            if not locators:issues.append({'condition_id':cid,'field':field,'issue':'missing_source_locator'})
            elif not isinstance(locators,dict) or set(locators)!=set(section['source_ids']) or not all(locators.values()):
                issues.append({'condition_id':cid,'field':field,'issue':'source_locator_mapping_mismatch'})
            if set(detail.get('source_ids',[]))!=set(section['source_ids']):
                issues.append({'condition_id':cid,'field':field,'issue':'editorial_source_mapping_mismatch'})
            if not set(section['source_ids'])<=inspected:
                issues.append({'condition_id':cid,'field':field,'issue':'section_references_uninspected_source'})
        topics.append({'id':cid,'kind':condition['kind'],'review_status':condition['review']['status'],
                       'content_sha256':content_hash(condition),
                       'sources_sha256':canonical_hash([sources[sid] for sid in sorted(condition['source_ids'])]),
                       'editorial_record_sha256':canonical_hash(record) if record else None,
                       'bilingual_fields_with_lists':lists,'chinese_characters':zh_chars,'english_words':en_words})
    known={c['id'] for c in data['conditions']}
    for extra in set(records)-known:issues.append({'condition_id':extra,'issue':'unknown_editorial_record'})
    return {'purpose':'Existing-topic content expansion and source-locator screening; not a medical validation or coverage estimate.',
            'classification_target':data['project']['coverage_target'],
            'topics':len(topics),'dimensions_per_topic':len(FIELDS),'bilingual_fields':len(topics)*len(FIELDS)*2,
            'editorial_records':len(records),'clinically_reviewed':sum(c['review']['status']=='medically_reviewed' for c in data['conditions']),
            'icd_mapped_topics':sum(bool(c['coding']) for c in data['conditions']),
            'all_condition_coverage':None,
            'limitations':['Lists, lengths and source locators do not prove comprehension or claim-level support.',
                           'Editorial source inspection is not independent medical or translation sign-off.',
                           'The full ICD-11 denominator and confirmed mappings have not been established.'],
            'issues':issues,'records':topics}
