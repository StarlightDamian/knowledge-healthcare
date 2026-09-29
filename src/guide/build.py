"""Reproducible offline build. No source/network retrieval occurs during a build."""
from __future__ import annotations
import base64
import hashlib
import json
from pathlib import Path
from .model import ROOT, load, validate, dump_json


def script_json(value) -> str:
    # Escaping '<' prevents a data field from terminating the JSON script element.
    return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026').replace('\u2028','\\u2028').replace('\u2029','\\u2029')

def sha_csp(text: str) -> str:
    return "'sha256-"+base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()+"'"

def bundle(root: Path) -> str:
    chunks=[]
    # Bundled modules have no imports or top-level side effects except app.mjs.
    for filename in ('search.mjs','safety.mjs','export.mjs','text.mjs','navigation.mjs','knowledge.mjs','app.mjs'):
        s=(root/'src/web'/filename).read_text(encoding='utf-8')
        s='\n'.join(l for l in s.splitlines() if not l.startswith('import '))
        s=s.replace('export function ','function ').replace('export const ','const ').replace('export class ','class ')
        if '</script' in s.lower():raise ValueError('Unexpected closing script literal in source')
        chunks.append(s)
    return "'use strict';\n(()=>{\n"+'\n'.join(chunks)+'\n})();'

def build(root: Path=ROOT,mode: str='preview',out: Path|None=None) -> dict:
    root=Path(root);data=load(root);stats=validate(data,mode)
    payload={k:v for k,v in data.items() if k not in ('reviewers','backlog')}
    payload['stats']=stats
    css=(root/'src/web/style.css').read_text(encoding='utf-8')
    js=bundle(root); serialized=script_json(payload)
    csp="default-src 'none'; script-src "+sha_csp(js)+' '+sha_csp(serialized)+"; style-src "+sha_csp(css)+"; img-src data:; connect-src 'none'; base-uri 'none'; form-action 'none'; object-src 'none'"
    html=(root/'src/web/template.html').read_text(encoding='utf-8')
    for name,val in {'CSP':csp,'STYLE':css,'PAYLOAD':serialized,'SCRIPT':js}.items():
        html=html.replace('{{'+name+'}}',val)
    target=Path(out) if out else root/'index.html';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(html,encoding='utf-8')
    # Machine readers can load one short catalog then an individual source JSON.
    catalog=[{k:c[k] for k in ('id','kind','names','primary_domain','source_ids')}|{'path':'data/conditions/'+c['id']+'.json','status':c['review']['status']} for c in data['conditions']]
    dump_json(root/'data/catalog/index.json',{'version':data['project']['version'],'topics':catalog})
    dump_json(root/'reports/content-audit.json',stats)
    return {'path':str(target),'bytes':target.stat().st_size,**stats}
