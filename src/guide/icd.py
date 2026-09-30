"""Frozen WHO MMS denominator and adjudicated coverage, independent of clinical review."""
from __future__ import annotations
from collections import Counter
from io import BytesIO
import gzip
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from .model import ROOT, FIELDS, ValidationError, canonical_hash, content_hash, read_json, valid_date, dump_json

RELEASE = '2026-01'
OFFICIAL_SHA256 = 'f1356588f40953a83e3af2b662deab47c5e269f944d1ea4ed0cfeb2007c7cd39'
OFFICIAL_URL = 'https://icdcdn.who.int/static/releasefiles/2026-01/SimpleTabulation-ICD-11-MMS-en.zip'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def parse_tabulation(blob: bytes) -> list[dict]:
    """Read the official XLSX without lossy line-based parsing of multiline TSV cells."""
    with ZipFile(BytesIO(blob)) as outer:
        names = [n for n in outer.namelist() if n.endswith('.xlsx')]
        if len(names) != 1:
            raise ValidationError('ICD archive must contain exactly one XLSX')
        with ZipFile(BytesIO(outer.read(names[0]))) as workbook:
            strings = [''.join(t.text or '' for t in si.findall('.//s:t', NS))
                       for si in ET.fromstring(workbook.read('xl/sharedStrings.xml')).findall('s:si', NS)]
            sheet = ET.fromstring(workbook.read('xl/worksheets/sheet1.xml'))
    headers = None
    result = []
    for row in sheet.findall('s:sheetData/s:row', NS):
        cells = {}
        for cell in row.findall('s:c', NS):
            column = re.sub(r'\d', '', cell.attrib['r'])
            value = cell.find('s:v', NS)
            raw = value.text if value is not None and value.text is not None else ''
            if cell.get('t') == 's':
                raw = strings[int(raw)]
            elif cell.get('t') == 'inlineStr':
                raw = ''.join(t.text or '' for t in cell.findall('.//s:t', NS))
            cells[column] = raw
        if headers is None:
            headers = cells
            if not {'Code', 'Title', 'ClassKind', 'ChapterNo', 'isLeaf'} <= set(headers.values()):
                raise ValidationError('Unexpected ICD tabulation columns')
            continue
        fields = {headers.get(k, k): v for k, v in cells.items()}
        kind = fields.get('ClassKind', '')
        # Formatting-only spreadsheet rows remain in the exported audit, with an exclusion reason.
        result.append({'row': int(row.attrib['r']), 'code': fields.get('Code', ''),
                       'title': fields.get('Title', ''), 'class_kind': kind,
                       'chapter': fields.get('ChapterNo', ''),
                       'foundation_uri': fields.get('Foundation URI', ''),
                       'linearization_uri': fields.get('Linearization URI', ''),
                       'parent_uri': fields.get('Parent', ''),
                       'is_leaf': fields.get('isLeaf') == 'True',
                       'is_residual': fields.get('IsResidual') == 'True'})
    return result


def classify_rows(rows: list[dict], rules: dict) -> list[dict]:
    decisions = rules['special_purpose_decisions']
    seen_special = set()
    classified = []
    for original in rows:
        row = dict(original)
        chapter, kind = row['chapter'], row['class_kind']
        if not kind:
            state, reason = 'excluded', 'spreadsheet_formatting_row'
        elif chapter == '26':
            state, reason = 'supplementary', 'traditional_medicine_separately_disclosed'
        elif kind != 'category':
            state, reason = 'excluded', 'chapter_or_block_heading'
        elif chapter in rules['excluded_chapters']:
            state, reason = 'excluded', rules['excluded_chapters'][chapter]
        elif not row['is_leaf']:
            state, reason = 'excluded', 'parent_category_not_counted_twice'
        elif chapter in rules['included_chapters']:
            state, reason = 'included', 'eligible_leaf_including_residual'
        elif chapter == '25':
            decision = decisions.get(row['code'])
            if not decision:
                raise ValidationError(f"Unadjudicated special-purpose code: {row['code']}")
            seen_special.add(row['code'])
            state, reason = decision['decision'], decision['reason']
            if state not in ('included', 'excluded') or not reason:
                raise ValidationError('Invalid special-purpose decision')
        else:
            raise ValidationError(f'Unadjudicated ICD chapter: {chapter}')
        row.update(decision=state, reason=reason, release=RELEASE)
        classified.append(row)
    if seen_special != set(decisions):
        raise ValidationError('Special-purpose decisions do not match the frozen leaves')
    codes = [r['code'] for r in classified if r['class_kind'] == 'category']
    if len(codes) != len(set(codes)) or '' in codes:
        raise ValidationError('ICD category codes must be unique and nonempty')
    return classified


def load_icd(root: Path = ROOT) -> dict:
    """Return verified manifest, rules and every official spreadsheet row with its decision."""
    folder = Path(root) / 'data/icd'
    manifest = read_json(folder / 'manifest.json')
    rules = read_json(folder / 'rules.json')
    if manifest.get('release') != RELEASE or rules.get('release') != RELEASE:
        raise ValidationError('ICD release differs from the frozen release')
    blob = (folder / manifest['snapshot_file']).read_bytes()
    if hashlib.sha256(blob).hexdigest() != OFFICIAL_SHA256 or manifest['snapshot_sha256'] != OFFICIAL_SHA256:
        raise ValidationError('Official ICD snapshot hash mismatch')
    if canonical_hash(rules) != manifest['rules_sha256']:
        raise ValidationError('ICD denominator rules hash mismatch')
    rows = classify_rows(parse_tabulation(blob), rules)
    if canonical_hash(rows) != manifest['catalog_sha256']:
        raise ValidationError('ICD catalog differs from the frozen denominator')
    exported = json.loads(gzip.decompress((folder / manifest['catalog_file']).read_bytes()))
    if exported != rows:
        raise ValidationError('Exported ICD catalog differs from the official snapshot')
    return {'manifest': manifest, 'rules': rules, 'rows': rows}


def freeze_icd(root: Path = ROOT) -> dict:
    """Reproduce the frozen catalog from the checked official bytes and explicit rules."""
    folder = Path(root) / 'data/icd'
    archive = folder / 'SimpleTabulation-ICD-11-MMS-en-2026-01.zip'
    blob = archive.read_bytes()
    if hashlib.sha256(blob).hexdigest() != OFFICIAL_SHA256:
        raise ValidationError('Official ICD snapshot hash mismatch')
    rules = read_json(folder / 'rules.json')
    rows = classify_rows(parse_tabulation(blob), rules)
    catalog = json.dumps(rows, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    (folder / 'catalog.json.gz').write_bytes(gzip.compress(catalog, mtime=0))
    manifest = {'release': RELEASE, 'status': 'frozen', 'language': 'en',
                'official_url': OFFICIAL_URL, 'accessed_at': '2026-09-30',
                'snapshot_file': archive.name, 'snapshot_sha256': OFFICIAL_SHA256,
                'snapshot_bytes': len(blob), 'catalog_file': 'catalog.json.gz',
                'catalog_sha256': canonical_hash(rows), 'rules_sha256': canonical_hash(rules),
                'rows': len(rows), 'row_kinds': dict(Counter(r['class_kind'] for r in rows)),
                'decisions': dict(Counter(r['decision'] for r in rows)),
                'eligible_categories': sum(r['decision'] == 'included' for r in rows),
                'attribution': 'International Classification of Diseases, Eleventh Revision (ICD-11), World Health Organization (WHO) 2019. Release 2026-01. https://icd.who.int/browse11. CC BY-ND 3.0 IGO.',
                'project_additions': ['decision', 'reason', 'release', 'row'],
                'license_url': 'https://icd.who.int/en/docs/ICD11-license.pdf'}
    dump_json(folder / 'manifest.json', manifest)
    return manifest


def propose_mappings(data: dict, rows: list[dict]) -> list[dict]:
    """Exact normalized names are discovery candidates, never semantic adjudication."""
    def normal(text):
        return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKC', text).casefold()).strip()
    names = {}
    for condition in data['conditions']:
        for name in [condition['names']['en'], *condition.get('aliases', {}).get('en', [])]:
            names.setdefault(normal(name), set()).add(condition['id'])
    result = []
    for row in rows:
        if row['class_kind'] != 'category':
            continue
        for cid in sorted(names.get(normal(row['title']), [])):
            result.append({'condition_id': cid, 'code': row['code'], 'release': RELEASE,
                           'status': 'pending', 'method': 'normalized_exact_name',
                           'rationale': 'Name similarity only; clinical scope and leaf coverage remain unverified.'})
    return result


def coverage_icd(data: dict, root: Path = ROOT, mappings: list[dict] | None = None,
                 editorial: dict | None = None) -> dict:
    from .editorial import editorial_audit
    root = Path(root)
    snapshot = load_icd(root)
    rows = snapshot['rows']
    eligible = {r['code']: r for r in rows if r['decision'] == 'included'}
    all_codes = {r['code'] for r in rows if r['class_kind'] == 'category'}
    conditions = {c['id']: c for c in data['conditions']}
    mappings = read_json(root / 'data/icd/mappings.json') if mappings is None else mappings
    editorial = editorial_audit(root, data=data) if editorial is None else editorial
    qualified = set(editorial['qualified_condition_ids'])
    seen = set()
    mapped = {}
    confirmed = set()
    covered = set()
    issues = []
    for mapping in mappings:
        cid, code = mapping.get('condition_id'), mapping.get('code')
        key = (cid, code)
        if key in seen or cid not in conditions or code not in all_codes or mapping.get('release') != RELEASE:
            raise ValidationError(f'Invalid/duplicate ICD mapping: {cid}/{code}')
        seen.add(key)
        state = mapping.get('status')
        if state not in ('pending', 'partial', 'confirmed', 'rejected'):
            raise ValidationError('Unknown ICD mapping status')
        if state != 'rejected':
            mapped.setdefault(code, []).append({'condition_id': cid, 'status': state})
        if state != 'confirmed':
            continue
        adjudication = mapping.get('adjudication', {})
        if (adjudication.get('method') != 'semantic_scope_review'
                or not adjudication.get('reviewer') or not valid_date(adjudication.get('checked_at'))
                or not adjudication.get('rationale') or adjudication.get('scope') != 'entire_leaf_category'
                or not adjudication.get('exclusions_considered')
                or mapping.get('content_sha256') != content_hash(conditions[cid])):
            issues.append({'condition_id': cid, 'code': code, 'issue': 'missing_or_stale_semantic_adjudication'})
            continue
        if code not in eligible:
            issues.append({'condition_id': cid, 'code': code, 'issue': 'mapping_outside_denominator'})
            continue
        confirmed.add(code)
        condition = conditions[cid]
        complete = all(all(condition.get('sections', {}).get(f, {}).get('text', {}).get(lang, '').strip()
                           for lang in ('zh-CN', 'en')) for f in FIELDS)
        if (cid in qualified and complete and condition.get('review', {}).get('status') != 'retired'):
            covered.add(code)
    chapters = {}
    missing = []
    category_states = []
    for row in rows:
        if row['class_kind'] != 'category':
            continue
        code = row['code']
        state = ('out_of_scope' if code not in eligible else 'complete' if code in covered
                 else 'partial' if code in confirmed or any(m['status'] == 'partial' for m in mapped.get(code, [])) else 'missing')
        category_states.append({'code': code, 'state': state,
                                'reason': row['reason'] if code not in eligible else
                                'qualified_content_and_scope' if code in covered else
                                'content_or_evidence_incomplete' if state == 'partial' else 'no_confirmed_complete_article',
                                'candidates': mapped.get(code, [])})
    for code, row in eligible.items():
        chapter = chapters.setdefault(row['chapter'], {'eligible': 0, 'confirmed': 0, 'covered': 0})
        chapter['eligible'] += 1
        chapter['confirmed'] += code in confirmed
        chapter['covered'] += code in covered
        if code not in covered:
            missing.append({'code': code, 'title': row['title'], 'uri': row['linearization_uri'], 'chapter': row['chapter'],
                            'state': 'confirmed_content_gap' if code in confirmed else 'mapping_pending' if mapped.get(code) else 'unmapped',
                            'candidates': mapped.get(code, [])})
    for chapter in chapters.values():
        chapter['fraction'] = chapter['covered'] / chapter['eligible']
    denominator = len(eligible)
    return {'release': RELEASE, 'snapshot_sha256': snapshot['manifest']['snapshot_sha256'],
            'rules_sha256': snapshot['manifest']['rules_sha256'], 'denominator_frozen': True,
            'denominator': denominator, 'confirmed_categories': len(confirmed), 'covered_categories': len(covered),
            'fraction': len(covered) / denominator, 'target': 0.95, 'target_met': len(covered) / denominator >= 0.95,
            'mapping_records': len(mappings), 'mapping_states': dict(Counter(m['status'] for m in mappings)),
            'chapters': chapters, 'catalog_decisions': dict(Counter(r['decision'] for r in rows)),
            'supplementary_chapter_26': dict(Counter(r['class_kind'] for r in rows if r['chapter'] == '26')),
            'clinical_reviewed_conditions': sum(c.get('review', {}).get('status') == 'medically_reviewed' for c in conditions.values()),
            'knowledge_entries_in_denominator': False, 'issues': issues, 'gaps': missing,
            'category_states': category_states,
            'limitations': ['Classification coverage is not population, case-volume or disease-burden coverage.',
                            'Recorded editorial and mapping attestations require actual review; software only checks consistency.',
                            'Rare leaves and residual categories remain in the denominator; chapter 26 is disclosed separately.']}
