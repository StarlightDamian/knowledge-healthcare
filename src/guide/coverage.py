"""Weighted, adjudicated need coverage; never infer coverage from a title count."""
import csv
import math
from pathlib import Path
from .model import ValidationError

def coverage(data:dict,path:Path,allow_synthetic:bool=False) -> dict:
    with path.open(encoding='utf-8-sig',newline='') as handle:
        rows=list(csv.DictReader(handle))
    required={'condition_id','weight','group','adjudicated','dataset_kind'}
    if not rows or not required<=set(rows[0]):raise ValidationError('Coverage CSV schema missing/empty')
    if any(r['dataset_kind']!='representative' for r in rows) and not allow_synthetic:
        raise ValidationError('Synthetic/convenience data cannot establish population coverage')
    ids={c['id'] for c in data['conditions']};reviewed={c['id'] for c in data['conditions'] if c['review']['status']=='medically_reviewed'}
    groups={};total=known=quality=0.0
    for row in rows:
        try:w=float(row['weight'])
        except ValueError as exc:raise ValidationError('Invalid weight') from exc
        if not math.isfinite(w) or w<=0:raise ValidationError('Weights must be positive and finite')
        if row['adjudicated']!='true':raise ValidationError('All input mappings require adjudication')
        g=groups.setdefault(row['group'],{'weight':0.0,'draft_mapped':0.0,'reviewed_mapped':0.0})
        total+=w;g['weight']+=w
        if row['condition_id'] in ids:known+=w;g['draft_mapped']+=w
        if row['condition_id'] in reviewed:quality+=w;g['reviewed_mapped']+=w
    return {'dataset_kind':sorted(set(r['dataset_kind'] for r in rows)),'input_rows':len(rows),'total_weight':total,
            'draft_topic_mapping':known/total,'clinically_reviewed_mapping':quality/total,'groups':groups,
            'confidence_interval':None,'note':'Sampling design and mapping validity require independent review. Weighted convenience rows do not prove 95% population coverage.'}
