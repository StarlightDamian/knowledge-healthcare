"""Separate educational modules; structural validity is not clinical approval."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from .model import ID_RE, bilingual, read_json, require, review_date, safe_url, valid_date

MODULE_IDS = ('cancer', 'lifecycle')
AGE_PARTITION = ((0, 4), (5, 17), (18, 39), (40, 64), (65, 84), (85, None))


def load_knowledge(root: Path) -> dict:
    return {key: read_json(root / 'data/knowledge' / f'{key}.json') for key in MODULE_IDS}


def records(value, label: str, *, nonempty: bool = True) -> dict:
    require(isinstance(value, list), f'{label}: list required')
    require(not nonempty or bool(value), f'{label}: empty list')
    result = {}
    for row in value:
        require(isinstance(row, dict), f'{label}: object required')
        rid = row.get('id')
        require(isinstance(rid, str) and bool(ID_RE.fullmatch(rid)), f'{label}: invalid ID')
        require(rid not in result, f'{label}: duplicate ID {rid}')
        result[rid] = row
    return result


def references(value, allowed: set, label: str, *, nonempty: bool = False) -> None:
    require(isinstance(value, list) and all(isinstance(v, str) for v in value), f'{label}: ID list required')
    require(not nonempty or bool(value), f'{label}: empty references')
    require(len(value) == len(set(value)), f'{label}: duplicate references')
    require(set(value) <= allowed, f'{label}: unknown or out-of-scope reference')


def sections(value, source_ids: set, label: str) -> int:
    rows = records(value, label)
    for sid, section in rows.items():
        path = f'{label}/{sid}'
        bilingual(section.get('title'), path + '/title')
        bilingual(section.get('text'), path + '/text')
        references(section.get('source_ids'), source_ids, path + '/source_ids', nonempty=True)
    return len(rows)


def validate_knowledge(knowledge: dict, condition_ids: set, today: date | None = None,
                       mode: str = 'preview') -> dict:
    """Validate module-local evidence, canonical factors and the inclusive age partition."""
    today = today or review_date()
    require(mode in ('preview', 'clinical'), 'Unknown knowledge release mode')
    require(isinstance(knowledge, dict) and set(knowledge) == set(MODULE_IDS),
            'Knowledge must contain cancer and lifecycle modules')
    entries = {}
    all_entry_ids = set()
    for key in MODULE_IDS:
        module = knowledge[key]
        require(isinstance(module, dict) and module.get('id') == key, f'knowledge/{key}: module ID mismatch')
        entries[key] = records(module.get('entries'), f'knowledge/{key}/entries')
        require(not (all_entry_ids & entries[key].keys()), 'Knowledge entry IDs must be unique across modules')
        all_entry_ids.update(entries[key])
    factor_ids = set(entries['lifecycle'])
    counts = {}
    for key in MODULE_IDS:
        module = knowledge[key]
        path = f'knowledge/{key}'
        bilingual(module.get('title'), path + '/title')
        bilingual(module.get('intro'), path + '/intro')
        groups = records(module.get('groups'), path + '/groups')
        for gid, group in groups.items():
            bilingual(group.get('label'), f'{path}/groups/{gid}/label')
        sources = records(module.get('sources'), path + '/sources')
        for sid, source in sources.items():
            require(safe_url(source.get('url')), f'{path}/sources/{sid}: unsafe URL')
            for field in ('title', 'scope'):
                require(isinstance(source.get(field), str) and bool(source[field].strip()),
                        f'{path}/sources/{sid}: {field} missing')
            accessed = source.get('accessed_at')
            require(valid_date(accessed) and date.fromisoformat(accessed) <= today,
                    f'{path}/sources/{sid}: invalid access date')
        source_ids = set(sources)
        section_count = sections(module.get('sections'), source_ids, path + '/sections')
        for eid, entry in entries[key].items():
            ep = f'{path}/entries/{eid}'
            require(isinstance(entry.get('group_id'), str) and entry['group_id'] in groups,
                    f'{ep}: one valid group_id required')
            bilingual(entry.get('title'), ep + '/title')
            bilingual(entry.get('summary'), ep + '/summary')
            references(entry.get('source_ids'), source_ids, ep + '/source_ids', nonempty=True)
            references(entry.get('condition_ids'), condition_ids, ep + '/condition_ids')
            references(entry.get('factor_ids'), factor_ids, ep + '/factor_ids')
            section_count += sections(entry.get('sections'), set(entry['source_ids']), ep + '/sections')
        stage_count = 0
        if key == 'lifecycle':
            stages = records(module.get('stages'), path + '/stages')
            ages = []
            for sid, stage in stages.items():
                sp = f'{path}/stages/{sid}'
                bilingual(stage.get('title'), sp + '/title')
                bilingual(stage.get('intro'), sp + '/intro')
                kind = stage.get('kind')
                require(kind in ('age', 'overlay'), f'{sp}: invalid stage kind')
                require('age_min' in stage and 'age_max' in stage, f'{sp}: age bounds required')
                lower, upper = stage['age_min'], stage['age_max']
                if kind == 'age':
                    require(type(lower) is int and lower >= 0 and
                            (upper is None or (type(upper) is int and upper >= lower)),
                            f'{sp}: invalid age bounds')
                    ages.append((lower, upper))
                else:
                    require(lower is None and upper is None, f'{sp}: overlay must not occupy an age interval')
                references(stage.get('factor_ids'), factor_ids, sp + '/factor_ids')
                section_count += sections(stage.get('sections'), source_ids, sp + '/sections')
            require(tuple(sorted(ages, key=lambda bounds: bounds[0])) == AGE_PARTITION,
                    'knowledge/lifecycle: age partition must be 0–4, 5–17, 18–39, 40–64, 65–84 and 85+ without gaps or overlap')
            stage_count = len(stages)
        review = module.get('review')
        require(isinstance(review, dict) and review.get('status') == 'editorial',
                f'{path}: only editorial review is supported; clinical approval is not implemented')
        updated = review.get('updated_at')
        require(valid_date(updated) and date.fromisoformat(updated) <= today, f'{path}: invalid review date')
        counts[key] = {'entries': len(entries[key]), 'groups': len(groups), 'sections': section_count,
                       'sources': len(sources), 'stages': stage_count}
    # A status label cannot substitute for a separately designed, evidence-bound review process.
    require(mode != 'clinical', 'Knowledge modules lack clinical sign-off; editorial modules cannot be released clinically')
    return {'modules': len(counts),
            **{field: sum(c[field] for c in counts.values()) for field in ('entries', 'sections', 'stages')},
            'by_module': counts}
