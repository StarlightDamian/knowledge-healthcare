"""Reproducible editorial work queue; never changes ICD coverage or clinical status."""
from __future__ import annotations

from collections import defaultdict, deque
import csv
import gzip
import hashlib
import html
from io import BytesIO, StringIO
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from urllib.parse import quote

from .icd import RELEASE, coverage_icd, load_chinese_titles, load_icd
from .model import ROOT, canonical_hash, load, read_json, require, safe_url, valid_date

PRIORITIES = ('P0', 'P1', 'P2', 'P3')
METHOD = 'rule_based_editorial_priority'


def _matches(rows, eligible, rules):
    """Resolve exact identities and follow WHO parent edges, including residual leaves."""
    nodes = {r['row']: r for r in rows if r['class_kind'] in ('chapter', 'block', 'category')}
    aliases = defaultdict(set)
    foundations = {}
    for key, row in nodes.items():
        for field in ('code', 'foundation_uri', 'linearization_uri'):
            if row[field]:
                aliases[row[field]].add(key)
        if row['foundation_uri']:
            require(row['foundation_uri'] not in foundations, 'Duplicate WHO foundation URI')
            foundations[row['foundation_uri']] = key
    descendants = defaultdict(set)
    for row in eligible:
        key, seen = row['row'], set()
        while key is not None:
            require(key not in seen, 'Cycle in WHO parent graph')
            seen.add(key)
            descendants[key].add(row['code'])
            parent = nodes[key]['parent_uri']
            require(not parent or parent in foundations, 'Missing WHO parent URI')
            key = foundations[parent] if parent else None
    matched = defaultdict(list)
    for rule in rules:
        selector = rule.get('selector', {})
        require(set(selector) in ({'codes'}, {'ancestors'}), 'Use codes or ancestors selector')
        kind = next(iter(selector))
        values = selector[kind]
        require(isinstance(values, list) and values and all(isinstance(v, str) for v in values)
                and len(values) == len(set(values)), 'Selector must contain unique identities')
        selected = set()
        for value in values:
            require(len(aliases.get(value, ())) == 1, f'Unknown/ambiguous ICD selector: {value}')
            key = next(iter(aliases[value]))
            if kind == 'codes':
                require(nodes[key]['code'] == value, f'codes requires an official code: {value}')
                hits = {value} if nodes[key]['decision'] == 'included' else set()
            else:
                hits = descendants[key]
            require(bool(hits), f'Selector matches no eligible leaf: {value}')
            selected.update(hits)
        for code in selected:
            matched[code].append(rule)
    return matched


def _validate_config(config, chapters, departments):
    require(config.get('schema_version') == 1 and config.get('release') == RELEASE,
            'Priority rules must use schema 1 and the frozen ICD release')
    require(isinstance(config.get('purpose'), str) and config['purpose'].strip(), 'Priority purpose missing')
    axes = config.get('dimensions', {})
    require(bool(axes) and all(isinstance(v, dict) and v.get('label') and v.get('description')
                              for v in axes.values()), 'Priority dimensions missing definitions')
    levels = config.get('levels', {})
    require(set(levels) == set(PRIORITIES) and all(v.get('label') and v.get('description')
                                                for v in levels.values()), 'Define P0 through P3')
    sources = config.get('sources', [])
    source_ids = [s['id'] for s in sources]
    require(len(source_ids) == len(set(source_ids)) and all(source_ids), 'Duplicate/empty priority source ID')
    for source in sources:
        require(safe_url(source.get('url')) and valid_date(source.get('accessed_at'))
                and all(source.get(k) for k in ('title', 'locator', 'support_scope')),
                f'Incomplete priority source: {source["id"]}')
    defaults = config.get('chapter_defaults', {})
    require(set(defaults) == chapters, 'Chapter defaults must cover exactly the eligible chapters')
    rules = config.get('rules', [])
    ids = [r['id'] for r in rules]
    require(len(ids) == len(set(ids)) and all(ids), 'Duplicate/empty priority rule ID')
    for chapter, default in defaults.items():
        require(default.get('priority') == 'P2' and default.get('label'),
                f'Unassessed chapter {chapter} must remain P2, not low risk')
        require(default.get('department') in departments, f'Invalid department for chapter {chapter}')
    for item in [*defaults.values(), *rules]:
        require(item.get('priority') in PRIORITIES and item.get('reason'), 'Priority/reason missing')
        require('department' not in item or item['department'] in departments, 'Invalid priority department')
        dimensions = item.get('dimensions', {})
        require(set(dimensions) == set(axes) and all(v is None or isinstance(v, str) and v.strip()
                                                  for v in dimensions.values()), 'Invalid priority dimensions')
        refs = item.get('source_ids', [])
        require(isinstance(refs, list) and refs and len(refs) == len(set(refs))
                and set(refs) <= set(source_ids), 'Unknown/empty priority sources')


def _round_robin(rows):
    queues = defaultdict(deque)
    for row in sorted(rows, key=lambda r: r['official_row']):
        queues[row['chapter']].append(row)
    while queues:
        for chapter in sorted(list(queues)):
            yield queues[chapter].popleft()
            if not queues[chapter]:
                del queues[chapter]


def build_priority_report(snapshot, coverage, config, departments, inventory=None, mece=None,
                          chinese_titles=None):
    """Pure construction API, also used with small explicit fixtures in contract tests."""
    eligible = [r for r in snapshot['rows'] if r['decision'] == 'included']
    codes = {r['code'] for r in eligible}
    require(len(codes) == len(eligible) and all(r['is_leaf'] and r['code'] for r in eligible),
            'Priority catalog contains duplicate/non-leaf categories')
    require(len(eligible) == snapshot['manifest']['eligible_categories'] == coverage['denominator'],
            'Priority denominator differs from frozen coverage')
    require(coverage['release'] == snapshot['manifest']['release'] == RELEASE, 'Coverage release mismatch')
    if chinese_titles is not None:
        require(all(isinstance(chinese_titles.get(code), str) and chinese_titles[code].strip()
                    for code in codes), 'Missing official Chinese title for eligible category')
    chapters = {r['chapter'] for r in eligible}
    _validate_config(config, chapters, departments)
    states = {r['code']: r for r in coverage['category_states'] if r['code'] in codes}
    require(len(states) == len(eligible) and all(r['state'] in ('complete', 'partial', 'missing')
                                              for r in states.values()), 'Missing/invalid coverage disposition')
    matches = _matches(snapshot['rows'], eligible, config['rules'])
    related = defaultdict(list)
    for item in (inventory or {}).get('items', []):
        if item['kind'] == 'backlog':
            for code in item['candidate_codes']:
                if code in codes:
                    related[code].append({'kind': 'backlog', 'id': item['id'],
                                          'status': 'title_only_scope_candidate'})
    for topic in (mece or {}).get('topics', []):
        if topic.get('publication_status') == 'not_published':
            for candidate in topic['icd_candidates']:
                if candidate['code'] in codes:
                    related[candidate['code']].append({'kind': 'draft', 'id': topic['canonical_id'],
                                                       'status': 'draft_scope_candidate'})
    result = []
    for row in eligible:
        candidates = sorted(matches[row['code']], key=lambda r: (PRIORITIES.index(r['priority']), r['id']))
        default = config['chapter_defaults'][row['chapter']]
        selected = candidates[0] if candidates else default
        department = selected.get('department', default['department'])
        state = states[row['code']]
        work = related[row['code']] + [{'kind': 'condition', 'id': c['condition_id'],
                                       'status': c['status']} for c in state['candidates']]
        result.append({'code': row['code'], 'title': row['title'],
                       'title_zh': chinese_titles[row['code']] if chinese_titles is not None else None,
                       'uri': row['linearization_uri'],
                       'foundation_uri': row['foundation_uri'], 'chapter': row['chapter'],
                       'official_row': row['row'], 'department': department,
                       'department_label': departments[department]['zh-CN'],
                       'priority': selected['priority'], 'reason': selected['reason'],
                       'rule_id': selected['id'] if candidates else f'chapter:{row["chapter"]}',
                       'matched_rule_ids': sorted(r['id'] for r in candidates),
                       'priority_assessment': METHOD,
                       'dimensions': dict(selected['dimensions']),
                       'unknown_dimensions': sorted(k for k, v in selected['dimensions'].items() if v is None),
                       'source_ids': sorted(selected['source_ids']), 'coverage_state': state['state'],
                       'related_work': [dict(kind=k, id=i, status=s) for k, i, s in
                                        sorted({(w['kind'], w['id'], w['status']) for w in work})],
                       'queue_rank': None, 'work_package': None})
    ordered, pending_count = [], 0
    for priority in PRIORITIES:
        tier = [r for r in result if r['priority'] == priority]
        for row in _round_robin([r for r in tier if r['coverage_state'] != 'complete']):
            pending_count += 1
            row.update(queue_rank=pending_count, work_package=f'WP-{(pending_count - 1) // 20 + 1:04d}')
            ordered.append(row)
        # Completed leaves stay visible at their priority but never consume a queue slot.
        ordered.extend(_round_robin([r for r in tier if r['coverage_state'] == 'complete']))
    complete = len(eligible) - pending_count
    require(complete == coverage['covered_categories'], 'Priority queue changed the coverage count')
    titles = {r['chapter']: r['title'] for r in snapshot['rows'] if r['class_kind'] == 'chapter'}
    chapter_stats = {}
    for chapter in sorted(chapters):
        members = [r for r in ordered if r['chapter'] == chapter]
        chapter_stats[chapter] = {'title': titles.get(chapter, chapter), 'categories': len(members),
                                 'complete': sum(r['coverage_state'] == 'complete' for r in members),
                                 'pending': sum(r['queue_rank'] is not None for r in members),
                                 'priorities': {p: sum(r['priority'] == p for r in members) for p in PRIORITIES}}
    summary = {'release': RELEASE, 'priority_assessment': METHOD, 'completion_target': 1.0,
               'reviewed_at': config.get('reviewed_at'),
               'denominator': len(eligible), 'covered_categories': complete, 'pending_categories': pending_count,
               'coverage_fraction': coverage['fraction'], 'work_packages': (pending_count + 19) // 20,
               'priorities': {p: {'all': sum(r['priority'] == p for r in ordered),
                                  'pending': sum(r['priority'] == p and r['queue_rank'] is not None for r in ordered)}
                              for p in PRIORITIES},
               'default_priority_categories': sum(not r['matched_rule_ids'] for r in ordered),
               'chapters': chapter_stats, 'next_package': [r for r in ordered if r['work_package'] == 'WP-0001'],
               'coverage_issues': coverage['issues'],
               'provenance': {'snapshot_sha256': snapshot['manifest']['snapshot_sha256'],
                              'catalog_sha256': snapshot['manifest']['catalog_sha256'],
                              'priority_rules_sha256': canonical_hash(config),
                              'existing_inventory_sha256': canonical_hash(inventory),
                              'batch_mece_sha256': canonical_hash(mece),
                              'coverage_dispositions_sha256': canonical_hash(coverage['category_states'])}}
    return {'schema_version': 1, 'summary': summary, 'policy': config, 'categories': ordered}


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _cell(value):
    return html.escape(str(value), quote=False).replace('|', '\\|').replace('\r', '').replace('\n', '<br>')


def _csv_value(value):
    text = _json(value) if isinstance(value, (dict, list)) else '' if value is None else str(value)
    # Same formula guard as guide.api.csv_cell, without importing the HTTP/DB runtime.
    if re.match(r'^[\s\ufeff]*[=+@\-＝＋＠－]', text) or text.startswith(('\t', '\r', '\n')):
        text = "'" + text
    return text


def _display_title(value):
    return re.sub(r'^(?:-\s+)+', '', value or '')


def _table(rows, chapter_links=False):
    lines = ['| 代码 | WHO官方中英名称 | 编辑归口 | 优先级 | 规则 | 覆盖与候选 | 顺序 / 工作包 |',
             '|---|---|---|---|---|---|---|']
    for row in rows:
        location = f'chapter-{row["chapter"]}.md' if chapter_links else ''
        rule_link = f'[{_cell(row["rule_id"])}]({location}#rule-{quote(row["rule_id"], safe="")})'
        names = '<br>'.join(_cell(_display_title(row[k])) for k in ('title_zh', 'title'))
        work = '<br>'.join(_cell(c['id'] + ': ' + c['status']) for c in row['related_work'])
        coverage = _cell(row['coverage_state']) + ('<br>' + work if work else '')
        schedule = f'{row["queue_rank"]}<br>{_cell(row["work_package"])}' if row['queue_rank'] is not None else '—'
        values = [f'[{_cell(row["code"])}]({row["uri"]})', names, _cell(row['department_label']),
                  row['priority'], rule_link, coverage, schedule]
        lines.append('| ' + ' | '.join(values) + ' |')
    return '\n'.join(lines) + '\n'


def _rule_notes(rows, policy):
    """Each winning rule is explained once per chapter, with every category linked to it."""
    rules = {}
    for row in rows:
        rules.setdefault(row['rule_id'], row)
    lines = ['## 本章规则说明', '',
             '类别表链接到决定其优先级的规则；理由、医学考虑与来源在此按规则列出一次。所有命中规则可查CSV与JSON；[原始规则](../../data/icd/priorities.json)保留完整选择范围。', '']
    for key, row in sorted(rules.items()):
        lines.extend([f'<a id="rule-{html.escape(key, quote=True)}"></a>', '',
                      f'### {_cell(key)} · {row["priority"]}', '', _cell(row['reason']), '',
                      '| 医学考虑 | 判断 |', '|---|---|'])
        for axis, definition in policy['dimensions'].items():
            value = row['dimensions'][axis]
            lines.append(f'| {_cell(definition["label"])} | {_cell(value) if value is not None else "未知（null）"} |')
        sources = ', '.join(f'[{_cell(source)}](index.md#source-{quote(source, safe="")})'
                            for source in row['source_ids'])
        lines.extend(['', '来源与定位：' + sources, ''])
    return '\n'.join(lines)


def write_priority_outputs(report, root=ROOT):
    """Write only priority artifacts, using deterministic bytes and UTF-8 BOM CSV."""
    root = Path(root)
    reports, docs = root / 'reports', root / 'docs/icd-priorities'
    reports.mkdir(parents=True, exist_ok=True)
    docs.mkdir(parents=True, exist_ok=True)
    packed = BytesIO()
    with gzip.GzipFile(filename='', mode='wb', fileobj=packed, mtime=0) as output:
        output.write(_json(report).encode('utf-8'))
    (reports / 'icd-priorities.json.gz').write_bytes(packed.getvalue())
    (reports / 'icd-priority-summary.json').write_bytes((_json(report['summary']) + '\n').encode('utf-8'))
    stream = StringIO(newline='')
    fields = ('code', 'title_zh', 'title', 'uri', 'chapter', 'department', 'department_label', 'priority', 'reason',
              'rule_id', 'matched_rule_ids', 'priority_assessment', 'dimensions', 'unknown_dimensions',
              'source_ids', 'coverage_state', 'related_work', 'queue_rank', 'work_package')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\r\n')
    writer.writeheader()
    for row in report['categories']:
        writer.writerow({k: _csv_value(row[k]) for k in fields})
    (reports / 'icd-priorities.csv').write_bytes(stream.getvalue().encode('utf-8-sig'))
    summary, policy = report['summary'], report['policy']
    intro = ['# 全量ICD病症编辑优先清单', '', policy['purpose'], '',
             f'冻结版本 {RELEASE}：{summary["denominator"]:,} 个合格叶类别全部列出；已完成 {summary["covered_categories"]:,} 类，待办 {summary["pending_categories"]:,} 类，目标100%。', '',
             '这是规则驱动的编辑排程，不是患者分诊或逐病种医学精确排名。未评估类别默认P2；未知保留null，不能解释为低危。已完成类别仍保留优先级，但待办顺序与工作包为空。', '',
             '同级待办按章节轮转，章内保持WHO官方顺序；每20个待办类别组成一个工作包。同级顺序仅用于调度。已有候选按精确代码关联当前正文映射、标题库存及首批草稿；标题和草稿不继承正文完整或审核状态。', '',
             'CSV对可能被Excel解释为公式的文本加单引号；WHO标题的逐字原值保存在JSON。修改内容、映射或规则后运行 `python -m src.guide priorities-icd`；`python -m src.guide priorities-icd --check` 只检查生成物是否过期。', '',
             '中英文名称取自同版WHO官方表；Markdown仅去除标题层级缩进，JSON保留原值。中文表只补充名称，分类、祖先继承、分母和顺序仍以冻结英文树为准。', '',
             '[方法与范围](../coverage-audit-and-roadmap.md) · [规则与来源](../../data/icd/priorities.json) · [冻结目录](../../data/icd/README.md) · [CSV全量清单](../../reports/icd-priorities.csv)', '',
             '## 优先级定义', '']
    intro.extend(f'- **{p} {_cell(policy["levels"][p]["label"])}**：{_cell(policy["levels"][p]["description"])}' for p in PRIORITIES)
    intro.extend(['', '## 医学考虑维度', ''])
    intro.extend(f'- **{_cell(value["label"])}**（{axis}）：{_cell(value["description"])}' for axis, value in sorted(policy['dimensions'].items()))
    intro.extend(['', '## 逐章全量清单', '', '| 章 | 中文编辑标签 / WHO官方英文章名 | 全部 | 已完成 | 待办 | P0 | P1 | P2 | P3 |', '|---|---|---:|---:|---:|---:|---:|---:|---:|'])
    for chapter, stats in summary['chapters'].items():
        label = _cell(policy['chapter_defaults'][chapter]['label'])
        intro.append(f'| [{chapter}](chapter-{chapter}.md) | {label}<br>{_cell(stats["title"])} | {stats["categories"]} | {stats["complete"]} | {stats["pending"]} | ' + ' | '.join(str(stats['priorities'][p]) for p in PRIORITIES) + ' |')
        members = [r for r in report['categories'] if r['chapter'] == chapter]
        text = f'# {chapter} {label}\n\nWHO官方英文章名：{_cell(stats["title"])}\n\n[返回总表](index.md)\n\n本章 {len(members)} 个合格叶类别；逐类列出，不以父级或标题代替正文覆盖。规则链接可查理由、医学考虑及来源。\n\n' + _table(members) + '\n' + _rule_notes(members, policy)
        (docs / f'chapter-{chapter}.md').write_bytes(text.encode('utf-8'))
    intro.extend(['', '## 下一工作包：20个待办类别（末包不足20时按实列出）', '', _table(summary['next_package'], chapter_links=True), '## 来源与定位', ''])
    chinese = summary['provenance'].get('chinese_titles')
    if chinese:
        intro.append(f'- **WHO官方中文名称** [同版中文电子表格]({chinese["source_url"]})；读取：{chinese["accessed_at"]}；快照SHA-256：`{chinese["snapshot_sha256"]}`；支持范围：同码官方中文名称，不替换英文分类树。')
    for source in sorted(policy['sources'], key=lambda s: s['id']):
        intro.extend([f'<a id="source-{html.escape(source["id"], quote=True)}"></a>', ''])
        intro.append(f'- **{_cell(source["id"])}** [{_cell(source["title"])}]({source["url"]})；定位：{_cell(source["locator"])}；读取：{source["accessed_at"]}；支持范围：{_cell(source["support_scope"])}')
    intro.extend(['', 'WHO原文标题、代码与URI保持不变；编辑归口、优先级、医学考虑及排程属于项目添加。优先级生成不会改变类别覆盖或医学签审。', ''])
    (docs / 'index.md').write_bytes('\n'.join(intro).encode('utf-8'))
    return summary


def check_priority_outputs(report, root=ROOT):
    """Render in an isolated temporary directory; never repair stale artifacts in check mode."""
    root = Path(root)
    with TemporaryDirectory(prefix='icd-priority-check-') as directory:
        temporary = Path(directory)
        write_priority_outputs(report, temporary)
        expected = {p.relative_to(temporary): p.read_bytes() for p in temporary.rglob('*') if p.is_file()}
    changed = [str(p) for p, contents in expected.items()
               if not (root / p).is_file() or (root / p).read_bytes() != contents]
    changed.extend(str(p.relative_to(root)) for p in (root / 'docs/icd-priorities').glob('chapter-*.md')
                   if p.relative_to(root) not in expected)
    require(not changed, 'Missing/stale ICD priority outputs: ' + ', '.join(sorted(changed)))
    return dict(report['summary'], check='passed')


def priorities_icd(root=ROOT, check=False):
    root = Path(root)
    snapshot = load_icd(root)
    chinese = load_chinese_titles(root, snapshot=snapshot)
    data = load(root)
    coverage = coverage_icd(data, root=root)
    report = build_priority_report(snapshot, coverage, read_json(root / 'data/icd/priorities.json'),
                                   data['departments'], read_json(root / 'reports/icd-existing-inventory.json'),
                                   read_json(root / 'reports/batch-01-mece.json'), chinese['titles'])
    report['summary']['provenance']['chinese_titles'] = chinese['manifest']
    inputs = [root / 'data/icd/priorities.json', root / 'data/icd/mappings.json',
              root / 'data/departments.json', root / 'reports/icd-existing-inventory.json',
              root / 'reports/batch-01-mece.json']
    inputs.extend(sorted((root / 'data/evidence/editorial-checks').glob('*.json')))
    report['summary']['provenance']['input_file_sha256'] = {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    report['summary']['provenance']['content_and_evidence_sha256'] = canonical_hash(data)
    if check:
        return check_priority_outputs(report, root)
    return write_priority_outputs(report, root)
