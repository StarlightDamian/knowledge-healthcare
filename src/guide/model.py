"""Data loading, structural validation and conservative release gates.

This validates recorded attestations, NOT the authenticity of clinical credentials.
Protected reviews and independent clinical validation remain organizational duties.
"""
from __future__ import annotations
import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
FIELDS = ('summary','causes_risks','red_flags','care','diagnosis','differentials',
          'treatment','medications','diet','daily_care','special_populations',
          'prognosis_followup','complications','prevention')
ID_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$')
URGENCIES = {'context_dependent','self_care_possible','routine','same_day','emergency'}

class ValidationError(ValueError):
    """Human-readable data validation failure."""

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f'{path}: {exc}') from exc

def dump_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def canonical_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',',':')).encode()).hexdigest()

def content_hash(condition: dict) -> str:
    return canonical_hash({k:v for k,v in condition.items() if k != 'review'})

def text_hash(section: dict) -> str:
    return canonical_hash(section['text'])

def review_date() -> date:
    """Date-only editorial records use UTC+08, independent of the runner's timezone."""
    return datetime.now(timezone(timedelta(hours=8))).date()


def valid_date(value: str) -> bool:
    try:
        return isinstance(value,str) and date.fromisoformat(value).isoformat() == value
    except (ValueError,TypeError):
        return False

def safe_url(value: str) -> bool:
    if not isinstance(value,str): return False
    try:
        u=urlparse(value)
        return u.scheme=='https' and bool(u.hostname) and not u.username and not u.password and not any(ord(c)<32 for c in value)
    except ValueError:
        return False

def load(root: Path = ROOT) -> dict:
    from .knowledge import load_knowledge
    root=Path(root)
    data={'conditions':[read_json(p) for p in sorted((root/'data/conditions').glob('*.json'))]}
    for k,p in {'sources':'evidence/sources.json','studies':'evidence/studies.json',
                'reviewers':'evidence/reviewers.json','conflicts':'evidence/conflicts.json',
                'taxonomy':'taxonomy.json','departments':'departments.json','department_groups':'department-groups.json','fields':'fields.json',
                'rules':'safety/rules.json','locales':'locales/ui.json','project':'project.json',
                'backlog':'catalog/backlog.json'}.items():
        data[k]=read_json(root/'data'/p)
    data['knowledge']=load_knowledge(root)
    return data

def require(test: bool, message: str) -> None:
    if not test: raise ValidationError(message)

def bilingual(obj, label: str) -> None:
    require(isinstance(obj,dict), f'{label}: object required')
    for lang in ('zh-CN','en'):
        require(isinstance(obj.get(lang),str) and bool(obj[lang].strip()),f'{label}: {lang} text missing')

def validate(data: dict, mode: str = 'preview', today: date | None = None) -> dict:
    from .knowledge import validate_knowledge
    today=today or review_date()
    require(mode in ('preview','clinical'), 'Unknown release mode')
    conditions=data['conditions']; sources=data['sources']
    require(bool(conditions),'No condition records')
    require(len({s['id'] for s in sources})==len(sources),'Duplicate source ID')
    require(len({c['id'] for c in conditions})==len(conditions),'Duplicate condition ID')
    domains={t['id'] for t in data['taxonomy']}; ids={c['id'] for c in conditions}
    require(len(domains)==len(data['taxonomy']),'Duplicate taxonomy ID')
    groups=data['department_groups']
    require(len({g['id'] for g in groups})==len(groups),'Duplicate department group ID')
    grouped=[]
    for group in groups:
        require(bool(ID_RE.fullmatch(group['id'])),'Invalid department group ID')
        bilingual(group['label'],group['id']+'/label')
        require(bool(group['departments']),'Empty department group')
        grouped.extend(group['departments'])
    require(len(grouped)==len(set(grouped)),'Department appears in multiple groups')
    require(set(grouped)==set(data['departments']),'Department group mapping is incomplete or unknown')
    smap={s['id']:s for s in sources}
    for s in sources:
        require(bool(ID_RE.fullmatch(s['id'])),f"Invalid source ID: {s['id']}")
        require(safe_url(s['url']),f"Unsafe source URL: {s['id']}")
        require(bool(s.get('title')) and bool(s.get('independence_group')),f"Source metadata missing: {s['id']}")
        require(valid_date(s['accessed_at']),f"Invalid access date: {s['id']}")
        require(date.fromisoformat(s['accessed_at'])<=today, f"Future access date: {s['id']}")
        require(s.get('publication_date') is None or valid_date(s['publication_date']),f"Invalid publication date: {s['id']}")
    warnings=[]
    for c in conditions:
        cid=c['id']; require(bool(ID_RE.fullmatch(cid)),f'Invalid condition ID: {cid}')
        require(c['schema_version']=='1.0.0',f'{cid}: unsupported schema')
        require(c['primary_domain'] in domains,f'{cid}: unknown domain')
        require(c['kind'] in ('condition','symptom'),f'{cid}: invalid kind')
        require(c['reference_urgency'] in URGENCIES,f'{cid}: invalid urgency')
        bilingual(c['names'],cid+'/names'); bilingual(c['limitations'],cid+'/limitations')
        require(bool(c['departments']) and set(c['departments'])<=set(data['departments']),f'{cid}: unknown/empty departments')
        require(bool(c['symptom_terms']),f'{cid}: empty symptom terms')
        for term in c['symptom_terms']: bilingual(term,cid+'/symptoms')
        for lang in ('zh-CN','en'):
            require(isinstance(c['aliases'].get(lang),list),f'{cid}: aliases missing')
            require(all(isinstance(a,str) and a.strip() for a in c['aliases'][lang]),f'{cid}: invalid aliases')
        require(set(FIELDS)<=set(c['sections']),f'{cid}: required sections missing')
        require(set(c['source_ids'])<=set(smap) and len(set(c['source_ids']))>=2,f'{cid}: source references invalid')
        require(len({smap[s]['independence_group'] for s in c['source_ids']})>=2,f'{cid}: two source families required even for a draft')
        require(set(c['related_ids'])<=ids and cid not in c['related_ids'],f'{cid}: invalid related ID')
        for key in FIELDS:
            sec=c['sections'][key]; bilingual(sec['text'],cid+'/'+key)
            require(bool(sec['source_ids']) and set(sec['source_ids'])<=set(c['source_ids']),f'{cid}/{key}: invalid source linkage')
            require(sec['support_status'] in ('pending_claim_verification','verified','disputed'),f'{cid}/{key}: invalid support state')
        rev=c['review']
        require(rev['status'] in ('editorial_draft','medically_reviewed','retired'),f'{cid}: invalid review state')
        require(valid_date(rev['editorial_updated_at']),f'{cid}: invalid editorial date')
        require(valid_date(rev['next_editorial_review_due']),f'{cid}: review due missing')
        require(rev['medical_reviewed_at'] is None or valid_date(rev['medical_reviewed_at']),f'{cid}: invalid medical review date')
        if rev['status']=='editorial_draft':
            require(rev['medical_reviewed_at'] is None,f'{cid}: draft cannot claim medical review date')
        if date.fromisoformat(rev['next_editorial_review_due'])<today:warnings.append(f'{cid}: editorial review overdue')
        if rev['status']=='medically_reviewed': clinical_record_gate(c,data,today)
    for rule in data['rules']['rules']:
        require(bool(ID_RE.fullmatch(rule['id'])), 'Invalid safety rule ID')
        require(rule['action'] in ('emergency','urgent_assessment'),'Invalid safety action')
        require(bool(rule['groups']) and all(g and all(isinstance(t,str) and t for t in g) for g in rule['groups']),'Empty safety pattern')
        require(set(rule['source_ids'])<=set(smap),f"{rule['id']}: unknown safety source")
    require(len({r['id'] for r in data['rules']['rules']})==len(data['rules']['rules']), 'Duplicate safety rule ID')
    for study in data['studies']:
        require(study['id'] in smap and set(study['condition_ids'])<=ids,'Unknown study linkage')
    baseline=set(data['locales']['en']['strings'])
    for locale in data['locales'].values():
        require(set(locale['strings'])==baseline,'UI translation keys differ')
        require(locale['dir'] in ('ltr','rtl'),'Bad language direction')
    if mode=='clinical':
        for c in conditions: clinical_record_gate(c,data,today)
    knowledge_stats=validate_knowledge(data.get('knowledge'),ids,today,mode)
    if mode=='clinical':
        require(data['rules']['status']=='clinically_validated','Safety rules lack independent clinical validation')
        require(data['project']['clinical_release']['authorized'] is True,'Clinical release not authorized')
        require(safe_url(data['project']['clinical_release'].get('validation_report_url','')),'Independent clinical validation report missing')
    return {'conditions':len(conditions),'sources':len(sources),'domains':len(domains),
            'ui_locales':len(data['locales']),'clinically_reviewed':sum(c['review']['status']=='medically_reviewed' for c in conditions),
            'verified_sections':sum(c['sections'][f]['support_status']=='verified' for c in conditions for f in FIELDS),
            'total_sections':len(conditions)*len(FIELDS),'warnings':warnings,'mode':mode,
            'daily_need_coverage':None,'coverage_note':'No representative, adjudicated target-population denominator supplied.',
            'knowledge':knowledge_stats}

def clinical_record_gate(c: dict,data: dict,today: date) -> None:
    cid=c['id'];rev=c['review'];smap={s['id']:s for s in data['sources']}
    require(rev['status']=='medically_reviewed',f'{cid}: no clinical sign-off')
    require(valid_date(rev.get('medical_reviewed_at')) and date.fromisoformat(rev['medical_reviewed_at'])<=today,f'{cid}: medical date invalid')
    require(date.fromisoformat(rev['next_editorial_review_due'])>=today,f'{cid}: expired review')
    require(c['clinical_region']!='UNSPECIFIED',f'{cid}: region not clinically localized')
    reviewers={r['id']:r for r in data['reviewers']}
    approved=set()
    for a in rev.get('approvals',[]):
        r=reviewers.get(a.get('reviewer_id'),{})
        if (r.get('credential_verified') is True and r.get('role') in ('physician','pharmacist')
            and a.get('content_sha256')==content_hash(c) and safe_url(a.get('attestation_url',''))
            and valid_date(a.get('reviewed_at')) and date.fromisoformat(a['reviewed_at'])<=today):
            approved.add(a['reviewer_id'])
    require(len(approved)>=2,f'{cid}: two distinct credential-checked, content-bound clinical attestations required')
    require(any(reviewers[r].get('role')=='physician' for r in approved),f'{cid}: at least one physician attestation required')
    for f in FIELDS:
        sec=c['sections'][f]
        require(sec['support_status']=='verified',f'{cid}/{f}: claim verification pending')
        independent=set()
        for v in sec.get('verification',[]):
            s=smap.get(v.get('source_id'),{})
            if (v.get('source_id') in sec['source_ids'] and v.get('reviewer_id') in approved
                and v.get('text_sha256')==text_hash(sec) and v.get('source_sha256')==canonical_hash(s)
                and v.get('support')=='full' and bool(v.get('locator'))
                and valid_date(v.get('reviewed_at')) and date.fromisoformat(v['reviewed_at'])<=today):
                independent.add(s['independence_group'])
        require(len(independent)>=2,f'{cid}/{f}: two independent source support attestations missing')
    for lang in c['names']:
        loc=c['localizations'].get(lang,{})
        require(loc.get('status')=='medically_reviewed' and loc.get('clinician_reviewed') is True,f'{cid}/{lang}: translation not clinically reviewed')
