"""Deploy a verified Git archive on the existing Linux host; retain rollback inputs."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import urlsplit
from urllib.request import urlopen

from src.guide.model import ROOT
from src.guide.package import verify
from src.guide.store import (PublicationStore, ReleaseNotFound, activate_release,
                             import_release, migrate, publish_release)

PG_ROOT = Path('/mnt/raid1/03_software_engineering/01_database/project/knowledge-healthcare')
PG_BIN = Path('/mnt/raid1/03_software_engineering/01_database/postgres/18.6/bin')
PROJECT = Path('/mnt/raid1/03_software_engineering/05_github/knowledge/knowledge-healthcare')


def run(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, text=True, **kwargs)


def private_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(content, encoding='utf-8'); path.chmod(0o600)


def switch(link, target):
    temporary = link.with_name(link.name + '.candidate')
    if temporary.is_symlink(): temporary.unlink()
    temporary.symlink_to(target, target_is_directory=True)
    os.replace(temporary, link)


def wait_health(port, release_id):
    for _ in range(30):
        try:
            with urlopen(f'http://127.0.0.1:{port}/healthcare/api/v1/healthz', timeout=2) as response:
                if json.load(response)['release_id'] == release_id: return
        except (OSError, ValueError, KeyError): pass
        time.sleep(.5)
    raise RuntimeError('Candidate HTTP service did not become healthy')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--git-commit', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', args.git_commit): raise ValueError('Full Git SHA required')
    source = ROOT.resolve()
    if source != (PROJECT/'runtime-releases'/args.git_commit).resolve():
        raise ValueError('Deploy only a named immutable project release directory')
    verify(source)
    config = json.loads((PG_ROOT/'client-env.json').read_text())
    private_root = Path.home()/'.local/state/knowledge-healthcare'
    receipt_dir = private_root/('publication-'+args.git_commit)
    receipt_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    store = PublicationStore(config['HEALTHCARE_READ_DSN'])
    # Back up before any schema or publication changes. pg_dump receives no secret arguments.
    parsed = urlsplit(config['HEALTHCARE_ADMIN_DSN'])
    pg_env = {**os.environ, 'PGHOST': parsed.hostname, 'PGPORT': str(parsed.port),
              'PGUSER': parsed.username, 'PGPASSWORD': parsed.password, 'PGDATABASE': parsed.path[1:]}
    backup = receipt_dir/'before.dump'
    if not backup.exists():
        run([str(PG_BIN/'pg_dump'), '-Fc', '-f', str(backup)], env=pg_env)
        backup.chmod(0o600)
    migrate(config['HEALTHCARE_ADMIN_DSN'])
    try: previous_release = store.active_release()
    except ReleaseNotFound: previous_release = None
    candidate = import_release(config['HEALTHCARE_IMPORT_DSN'], source, git_commit=args.git_commit,
                               allow_initial_baseline=previous_release is None)
    runtime = Path.home()/'.local/share/knowledge-healthcare'
    runtime.mkdir(parents=True, exist_ok=True)
    current = runtime/'current'
    previous_runtime = str(current.resolve()) if current.is_symlink() else None
    units = Path.home()/'.config/systemd/user'
    homepage_unit = units/'home-page.service'
    original_homepage = homepage_unit.read_text()
    if not (receipt_dir/'home-page.service.before').exists():
        private_write(receipt_dir/'home-page.service.before', original_homepage)
    python = runtime/'venv312/bin/python'
    reader_env = private_root/'reader.env'
    private_write(reader_env, 'HEALTHCARE_READ_DSN='+config['HEALTHCARE_READ_DSN']+'\n')
    api_unit = f'''[Unit]
Description=Open Medical Guide read-only API
After=knowledge-healthcare-postgresql.service
Requires=knowledge-healthcare-postgresql.service

[Service]
WorkingDirectory={current}
EnvironmentFile={reader_env}
ExecStart={python} -m uvicorn src.guide.api:create_app --factory --host 127.0.0.1 --port 11004 --no-access-log
Restart=on-failure
RestartSec=3
UMask=0077
NoNewPrivileges=true

[Install]
WantedBy=default.target
'''
    private_write(units/'knowledge-healthcare-api.service', api_unit)
    mounted = False
    try:
        publish_release(config['HEALTHCARE_IMPORT_DSN'], candidate['release_id'], expected_current=previous_release, root=source)
        switch(current, source)
        run(['systemctl','--user','daemon-reload'])
        run(['systemctl','--user','enable','knowledge-healthcare-api.service'])
        run(['systemctl','--user','restart','knowledge-healthcare-api.service'])
        wait_health(11004, candidate['release_id'])
        # Changing only ExecStart keeps the shared service's existing policy and static root.
        command = f'ExecStart={python} {current}/src/ops/serve_gateway.py 11003 --bind 127.0.0.1 --directory {Path.home()}/.local/share/home-page/releases/current'
        updated, count = re.subn(r'^ExecStart=.*$', command, original_homepage, flags=re.MULTILINE)
        if count != 1: raise RuntimeError('Unexpected shared service layout')
        private_write(homepage_unit, updated); mounted = True
        run(['systemctl','--user','daemon-reload'])
        run(['systemctl','--user','restart','home-page.service'])
        wait_health(11003, candidate['release_id'])
        for path in ('/home/', '/fitness/'):
            with urlopen('http://127.0.0.1:11003'+path, timeout=10) as response:
                if response.status != 200: raise RuntimeError('Shared site regression')
        receipt = {**candidate, 'git_commit':args.git_commit, 'previous_release_id':previous_release,
                   'previous_runtime':previous_runtime, 'runtime':str(source), 'backup':str(backup),
                   'public_url':'https://www.zengyuwei.cn/healthcare/', 'local_http_verified':True,
                   'public_verified':False}
        private_write(receipt_dir/'receipt.json', json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt))
    except Exception:
        if mounted: private_write(homepage_unit, original_homepage)
        if previous_runtime: switch(current, previous_runtime)
        if previous_release and store.active_release() != previous_release:
            activate_release(config['HEALTHCARE_IMPORT_DSN'], previous_release, expected_current=candidate['release_id'])
        run(['systemctl','--user','daemon-reload'])
        if previous_runtime: run(['systemctl','--user','restart','knowledge-healthcare-api.service'])
        if mounted: run(['systemctl','--user','restart','home-page.service'])
        raise


if __name__ == '__main__': main()
