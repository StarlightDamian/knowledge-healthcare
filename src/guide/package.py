"""Integrity manifest and reproducible repository archive (not a digital signature)."""
import hashlib
import json
import zipfile
from pathlib import Path
from .model import dump_json
EXCLUDED={'__pycache__','.git','.pytest_cache','node_modules','.venv','test-results'}
def files(root:Path):
    return sorted(p for p in root.rglob('*') if p.is_file() and not (set(p.relative_to(root).parts)&EXCLUDED) and p.suffix not in ('.pyc','.zip') and p.name!='MANIFEST.sha256.json')
def manifest(root:Path):
    m={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files(root)}
    dump_json(root/'MANIFEST.sha256.json',m);return m

def verify(root:Path) -> None:
    m=json.loads((root/'MANIFEST.sha256.json').read_text(encoding='utf-8'))
    actual={p.relative_to(root).as_posix() for p in files(root)}
    if set(m)!=actual:raise ValueError('Manifest file inventory differs')
    for path,digest in m.items():
        if hashlib.sha256((root/path).read_bytes()).hexdigest()!=digest:raise ValueError('Hash mismatch: '+path)

def package(root:Path,out:Path):
    manifest(root)
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in [*files(root),root/'MANIFEST.sha256.json']:
            info=zipfile.ZipInfo('open-medical-guide/'+p.relative_to(root).as_posix(),date_time=(2026,9,29,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,p.read_bytes())
    return {'path':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size}
