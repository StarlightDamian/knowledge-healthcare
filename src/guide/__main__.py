"""Run from repository root: python -m src.guide --help."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from .model import ROOT,ValidationError,load,validate,dump_json,ID_RE

def main(argv=None)->int:
    p=argparse.ArgumentParser(description='Open Medical Guide: build, validate and maintain evidence drafts')
    p.add_argument('--root',type=Path,default=ROOT)
    sub=p.add_subparsers(dest='command',required=True)
    for name in ('validate','build'):
        q=sub.add_parser(name);q.add_argument('--mode',choices=['preview','clinical'],default='preview')
        if name=='build':q.add_argument('--out',type=Path)
    q=sub.add_parser('impact');q.add_argument('source_id')
    q=sub.add_parser('links');q.add_argument('--limit',type=int,default=10)
    q=sub.add_parser('coverage');q.add_argument('csv',type=Path);q.add_argument('--allow-synthetic',action='store_true')
    q=sub.add_parser('package');q.add_argument('--out',type=Path,default=Path('open-medical-guide.zip'))
    sub.add_parser('verify')
    sub.add_parser('content-audit')
    q=sub.add_parser('new');q.add_argument('id');q.add_argument('--zh',required=True);q.add_argument('--en',required=True)
    a=p.parse_args(argv)
    try:
        if a.command=='verify':
            from .package import verify
            verify(a.root);result={'integrity':'passed','signature':'not_signed'}
        elif a.command=='package':
            from .package import package
            result=package(a.root,a.out)
        elif a.command=='build':
            from .build import build
            result=build(a.root,a.mode,a.out)
        elif a.command=='content-audit':
            from .content_audit import content_audit
            result=content_audit(a.root)
        else:
            data=load(a.root)
            if a.command=='validate':result=validate(data,a.mode)
            elif a.command=='impact':
                from .evidence import impact
                result=impact(data,a.source_id)
            elif a.command=='links':
                from .evidence import check_links
                result=check_links(data,a.limit)
            elif a.command=='coverage':
                from .coverage import coverage
                result=coverage(data,a.csv,a.allow_synthetic)
            elif a.command=='new':
                if not ID_RE.fullmatch(a.id):raise ValidationError('ID must be a lowercase safe slug')
                target=a.root/'drafts'/f'{a.id}.json'
                if target.exists() or (a.root/'data/conditions'/f'{a.id}.json').exists():raise ValidationError('ID already exists')
                template=json.loads((a.root/'templates/condition.json').read_text())
                template.update(id=a.id,names={'zh-CN':a.zh,'en':a.en})
                dump_json(target,template);result={'draft':str(target),'next':'Complete fields and sources, validate, then move to data/conditions. Scaffold is not indexed.'}
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 2 if a.command=='content-audit' and result['issues'] else 0
    except (ValidationError,ValueError,OSError,KeyError) as exc:
        print('ERROR: '+str(exc),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
