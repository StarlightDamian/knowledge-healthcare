"""Content-bound editorial evidence records; software checks records, not medical truth."""
from __future__ import annotations
from collections import Counter
from datetime import date
from pathlib import Path
from .model import ROOT, FIELDS, ValidationError, canonical_hash, load, read_json, safe_url, valid_date


def section_content_hash(target: dict, section: dict) -> str:
    return canonical_hash({'target': target, 'text': section['text'],
                           'source_ids': sorted(section['source_ids']),
                           **({'context': section['context']} if 'context' in section else {})})


def target_key(target: dict) -> str:
    return '/'.join(str(target[k]) for k in ('kind', 'module_id', 'id', 'section') if k in target)


def editorial_sections(data: dict) -> dict:
    """Index condition, module, entry and stage sections in their actual source namespace."""
    result = {}
    global_sources = {s['id']: s for s in data.get('sources', [])}
    def add(target, sections, sources, review):
        for section_id, section in sections.items():
            address = {**target, 'section': section_id}
            key = target_key(address)
            if key in result:
                raise ValidationError(f'Duplicate editorial target: {key}')
            result[key] = {'target': address, 'section': section, 'sources': sources,
                           'review': review, 'content_sha256': section_content_hash(address, section)}
    for condition in data['conditions']:
        add({'kind': 'condition', 'id': condition['id']}, condition['sections'],
            global_sources, condition.get('review', {}))
    for module_id, module in data.get('knowledge', {}).items():
        sources = {s['id']: s for s in module['sources']}
        module_sections = {s['id']: s for s in module['sections']}
        if module.get('intro'):
            module_sections['intro'] = {'text': module['intro'], 'source_ids': sorted(sources)}
        add({'kind': 'module', 'id': module_id}, module_sections, sources, module['review'])
        for kind, collection in (('knowledge_entry', 'entries'), ('stage', 'stages')):
            for entry in module.get(collection, []):
                sections = {s['id']: s for s in entry['sections']}
                overview = 'summary' if kind == 'knowledge_entry' else 'intro'
                if entry.get(overview):
                    links = entry.get('source_ids') or sorted({sid for s in entry['sections'] for sid in s['source_ids']})
                    sections[overview] = {'text': entry[overview], 'source_ids': links}
                    if kind == 'stage':
                        sections[overview]['context'] = {key: entry.get(key) for key in ('age_min', 'age_max', 'kind')}
                add({'kind': kind, 'module_id': module_id, 'id': entry['id']},
                    sections, sources, module['review'])
    return result


def load_editorial_records(root: Path = ROOT) -> list[dict]:
    records = []
    for path in sorted((Path(root) / 'data/evidence/editorial-checks').glob('*.json')):
        value = read_json(path)
        items = value if isinstance(value, list) else value.get('checks') if isinstance(value, dict) else None
        if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
            raise ValidationError(f'{path}: editorial record array or checks array required')
        records.extend(items)
    return records


def make_editorial_record(data: dict, target: dict, record_id: str) -> dict:
    """Generate an honest pending scaffold; opening URLs never fills an attestation."""
    entry = editorial_sections(data).get(target_key(target))
    if entry is None:
        raise ValidationError('Unknown editorial target')
    return {'id': record_id, 'target': target, 'content_sha256': entry['content_sha256'],
            'status': 'pending', 'scope': 'full_section', 'checked_at': None, 'checker': None,
            'medical_reviewed': False, 'supports': [], 'claims': [],
            'claim_inventory': 'not_assessed',
            'adversarial_review': {'status': 'pending', 'reviewer': None, 'author': None,
                                   'checked_at': None, 'original_sources_reopened': [],
                                   'findings': [], 'resolution': ''},
            'independence': {'status': 'unknown', 'rationale': '', 'underlying_evidence': 'not_assessed'},
            'dispute': {'status': 'not_assessed', 'resolution': ''}}


def _record_problems(record: dict, entry: dict, today: date) -> list[str]:
    problems = []
    if record.get('content_sha256') != entry['content_sha256']:
        problems.append('content_hash_mismatch')
    if record.get('medical_reviewed') is not False:
        problems.append('editorial_record_cannot_claim_medical_review')
    if record.get('status') not in ('pending', 'cross_checked', 'disputed'):
        problems.append('invalid_editorial_status')
    if record.get('scope') not in ('full_section', 'selected_claims'):
        problems.append('invalid_scope')
    if record.get('status') != 'cross_checked':
        return problems
    if not valid_date(record.get('checked_at')) or date.fromisoformat(record['checked_at']) > today:
        problems.append('invalid_check_date')
    if not isinstance(record.get('checker'), str) or not record['checker'].strip():
        problems.append('checker_missing')
    if record.get('scope') != 'full_section':
        problems.append('selected_claims_do_not_verify_whole_section')
    independence = record.get('independence', {})
    if (independence.get('status') != 'independent_editorial_sources'
            or not independence.get('rationale')
            or independence.get('underlying_evidence') not in ('not_assessed', 'overlap', 'independent')):
        problems.append('independent_editorial_origin_not_recorded')
    dispute = record.get('dispute', {})
    if dispute.get('status') not in ('none', 'regional_difference') or not dispute.get('resolution'):
        problems.append('unresolved_or_unassessed_dispute')
    supports = record.get('supports', [])
    if not isinstance(supports, list):
        return problems + ['supports_array_required']
    groups, urls, source_ids = set(), set(), set()
    for support in supports:
        if not isinstance(support, dict):
            problems.append('support_object_required')
            continue
        sid = support.get('source_id')
        source = entry['sources'].get(sid)
        if not source or sid not in entry['section']['source_ids']:
            problems.append('support_not_linked_to_target_section')
            continue
        if sid in source_ids:
            problems.append('duplicate_support_source')
        source_ids.add(sid)
        if support.get('source_metadata_sha256') != canonical_hash(source):
            problems.append('source_metadata_hash_mismatch')
        if not safe_url(source.get('url')):
            problems.append('unsafe_source_url')
        if source.get('retrieval_status') not in ('page_opened', 'search_text_retrieved', 'abstract_retrieved', 'article_retrieved'):
            problems.append('source_not_actually_read')
        urls.add(source.get('url', '').rstrip('/'))
        for field in ('locator', 'source_version', 'population', 'region', 'independence_group', 'assessment'):
            if not isinstance(support.get(field), str) or not support[field].strip():
                problems.append(f'support_{field}_missing')
        if not isinstance(support.get('upstream_evidence'), list) or not support['upstream_evidence']:
            problems.append('upstream_evidence_disclosure_missing')
        if not valid_date(support.get('accessed_at')) or date.fromisoformat(support['accessed_at']) > today:
            problems.append('invalid_source_access_date')
        if support.get('relation') != 'supports':
            problems.append('source_does_not_support_section')
        group = support.get('independence_group')
        if source.get('independence_group') and group != source['independence_group']:
            problems.append('source_independence_group_mismatch')
        if isinstance(group, str) and group.strip():
            groups.add(group)
    if min(len(groups), len(urls), len(source_ids)) < 2:
        problems.append('two_independent_editorial_sources_required')
    # A pair of page links does not establish support for every action or threshold.
    claims = record.get('claims', [])
    if record.get('claim_inventory') != 'all_medical_claims_in_section' or not isinstance(claims, list) or not claims:
        problems.append('complete_claim_inventory_required')
        claims = []
    claim_ids = set()
    support_map = {s.get('source_id'): s for s in supports if isinstance(s, dict)}
    for claim in claims:
        if not isinstance(claim, dict):
            problems.append('claim_object_required')
            continue
        cid = claim.get('id')
        if not isinstance(cid, str) or not cid or cid in claim_ids:
            problems.append('missing_or_duplicate_claim_id')
        claim_ids.add(cid)
        if claim.get('kind') not in ('explanation', 'action', 'threshold', 'benefit', 'risk'):
            problems.append('claim_kind_required')
        for lang in ('zh-CN', 'en'):
            excerpt = claim.get('text', {}).get(lang)
            if not isinstance(excerpt, str) or not excerpt.strip() or excerpt not in entry['section']['text'].get(lang, ''):
                problems.append('claim_not_bound_to_bilingual_text')
        refs = claim.get('supports', [])
        claim_groups = set()
        if not isinstance(refs, list):
            problems.append('claim_supports_array_required')
            refs = []
        for ref in refs:
            if not isinstance(ref, dict) or ref.get('source_id') not in support_map:
                problems.append('claim_source_not_in_section_supports')
                continue
            if not ref.get('locator') or not ref.get('assessment'):
                problems.append('claim_precise_support_required')
            support = support_map[ref['source_id']]
            if support.get('independence_group'):
                claim_groups.add(support['independence_group'])
        required = 1 if claim.get('kind') == 'explanation' else 2
        if len(claim_groups) < required:
            problems.append('claim_requires_two_independent_sources')
    review = record.get('adversarial_review', {})
    if (review.get('status') != 'accepted' or not review.get('reviewer') or not review.get('author')
            or review.get('reviewer') == review.get('author')
            or not valid_date(review.get('checked_at'))
            or (valid_date(review.get('checked_at')) and date.fromisoformat(review['checked_at']) > today)
            or not review.get('resolution')
            or not source_ids <= set(review.get('original_sources_reopened', []))):
        problems.append('independent_adversarial_review_required')
    findings = review.get('findings', [])
    if not isinstance(findings, list) or any(not isinstance(f, dict) or f.get('status') != 'resolved' or not f.get('resolution') for f in findings):
        problems.append('unresolved_adversarial_findings')
    return sorted(set(problems))


def editorial_audit(root: Path = ROOT, data: dict | None = None,
                    records: list[dict] | None = None, today: date | None = None) -> dict:
    root = Path(root)
    data = load(root) if data is None else data
    records = load_editorial_records(root) if records is None else records
    today = today or date.today()
    index = editorial_sections(data)
    issues, checked, seen_ids, seen_targets, qualified_sections = [], [], set(), set(), set()
    duplicate_targets = set()
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get('target'), dict):
            issues.append({'issue': 'malformed_editorial_record'})
            continue
        rid, key = record.get('id'), target_key(record['target'])
        problems = []
        if not isinstance(rid, str) or not rid or rid in seen_ids:
            problems.append('missing_or_duplicate_record_id')
        seen_ids.add(rid)
        if key in seen_targets:
            problems.append('duplicate_target_record')
            duplicate_targets.add(key)
        seen_targets.add(key)
        entry = index.get(key)
        if not entry:
            problems.append('unknown_editorial_target')
        else:
            problems.extend(_record_problems(record, entry, today))
        qualified = not problems and record.get('status') == 'cross_checked'
        if qualified:
            qualified_sections.add(key)
        state = 'qualified_record' if qualified else 'invalid_record' if problems else record.get('status')
        checked.append({'id': rid, 'target': record['target'], 'state': state, 'issues': problems})
        issues.extend({'record_id': rid, 'target': record['target'], 'issue': problem} for problem in problems)
    qualified_sections -= duplicate_targets
    targets = {}
    for key, entry in index.items():
        address = {k: v for k, v in entry['target'].items() if k != 'section'}
        target = targets.setdefault(target_key(address), {'target': address, 'required_sections': [],
                                                         'qualified_sections': [], 'qualified': False})
        target['required_sections'].append(entry['target']['section'])
        if key in qualified_sections:
            target['qualified_sections'].append(entry['target']['section'])
    qualified_ids = []
    for target in targets.values():
        expected = set(FIELDS) if target['target']['kind'] == 'condition' else set(target['required_sections'])
        target['qualified'] = bool(expected) and expected <= set(target['qualified_sections'])
        if target['qualified'] and target['target']['kind'] == 'condition':
            qualified_ids.append(target['target']['id'])
    legacy_path = root / 'data/evidence/claim-spot-checks.json'
    legacy = read_json(legacy_path) if legacy_path.exists() else []
    return {'purpose': 'Validate recorded editorial evidence and content binding, not actual medical support.',
            'conditions': len(data['conditions']),
            'knowledge_entries': sum(len(m['entries']) for m in data.get('knowledge', {}).values()),
            'required_sections': len(index), 'recorded_checks': len(records),
            'qualified_sections': len(qualified_sections), 'qualified_condition_ids': sorted(qualified_ids),
            'clinical_reviewed_conditions': sum(c.get('review', {}).get('status') == 'medically_reviewed' for c in data['conditions']),
            'legacy_spot_checks': {'count': len(legacy), 'scope': 'selected_claims',
                                   'promoted_to_section_verification': 0,
                                   'content_binding': 'not_recorded_in_legacy_format'},
            'states': dict(Counter(r['state'] for r in checked)), 'issues': issues,
            'targets': list(targets.values()), 'records': checked,
            'limitations': ['A syntactically valid record is not proof that a source supports its text.',
                            'Different organizations may share underlying studies or republish the same text.',
                            'Editorial comparison is not clinician sign-off or clinical release authorization.']}


def require_editorial_changes(data: dict, baseline_data: dict, root: Path = ROOT,
                              records: list[dict] | None = None) -> dict:
    """Gate new/changed text or source links while preserving the explicitly imported baseline."""
    audit = editorial_audit(root, data=data, records=records)
    previous = editorial_sections(baseline_data)
    current = editorial_sections(data)
    changed = {target_key({k: v for k, v in item['target'].items() if k != 'section'})
               for key, item in current.items()
               if key not in previous or item['content_sha256'] != previous[key]['content_sha256']
               or any(canonical_hash(item['sources'].get(sid)) != canonical_hash(previous[key]['sources'].get(sid))
                      for sid in item['section']['source_ids'])}
    failed = [target_key(item['target']) for item in audit['targets']
              if target_key(item['target']) in changed and not item['qualified']]
    if failed:
        raise ValidationError('New or changed content lacks full editorial cross-checks: ' + ', '.join(sorted(failed)))
    return audit
