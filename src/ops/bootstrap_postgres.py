"""Provision the dedicated healthcare cluster using the server's existing PostgreSQL.

Run as the deployment user on Linux. Credentials stay in private files, never stdout.
This does not modify another project's database or the public website route.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import time


def run(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, text=True, **kwargs)


def private_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(text, encoding='utf-8')
    path.chmod(0o600)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bin', type=Path, default=Path('/mnt/raid1/03_software_engineering/01_database/postgres/18.6/bin'))
    parser.add_argument('--root', type=Path, default=Path('/mnt/raid1/03_software_engineering/01_database/project/knowledge-healthcare'))
    parser.add_argument('--port', type=int, default=54330)
    args = parser.parse_args()
    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    root.chmod(0o700)
    data, sockets = root / 'data', root / 'run'
    sockets.mkdir(mode=0o700, exist_ok=True)
    secret_file = root / 'credentials.json'
    roles = ('healthcare_admin', 'healthcare_importer', 'healthcare_reader')
    if secret_file.exists():
        credentials = json.loads(secret_file.read_text())
        if set(credentials) != set(roles):
            raise RuntimeError('Existing credential inventory does not match this application')
    else:
        if (data / 'PG_VERSION').exists():
            raise RuntimeError('Existing cluster has no matching credential file; refusing to replace credentials')
        credentials = {role: secrets.token_hex(32) for role in roles}
        private_write(secret_file, json.dumps(credentials))
    if not (data / 'PG_VERSION').exists():
        with socket.socket() as probe:
            if probe.connect_ex(('127.0.0.1', args.port)) == 0:
                raise RuntimeError('Requested PostgreSQL port is already occupied')
        if data.exists() and any(data.iterdir()):
            raise RuntimeError('Refusing to initialize a nonempty data directory')
        run([str(args.bin / 'initdb'), '-D', str(data), '--encoding=UTF8', '--locale=C.UTF-8', '--auth-local=peer', '--auth-host=scram-sha-256'])
        with (data / 'postgresql.conf').open('a') as config:
            config.write(f"\nlisten_addresses = '127.0.0.1'\nport = {args.port}\nunix_socket_directories = '{sockets}'\nmax_connections = 32\nshared_buffers = '128MB'\nwork_mem = '4MB'\nlog_statement = 'none'\n")
    if (data / 'PG_VERSION').read_text().strip() != '18':
        raise RuntimeError('Expected a dedicated PostgreSQL 18 cluster')
    unit_path = Path.home() / '.config/systemd/user/knowledge-healthcare-postgresql.service'
    unit = f'''[Unit]
Description=Open Medical Guide dedicated PostgreSQL
After=network.target

[Service]
Type=simple
ExecStart={args.bin / 'postgres'} -D {data}
Restart=on-failure
RestartSec=3
TimeoutStopSec=60
KillSignal=SIGINT
UMask=0077

[Install]
WantedBy=default.target
'''
    if unit_path.exists() and unit_path.read_text() != unit:
        raise RuntimeError('Existing healthcare service differs; review it before updating')
    private_write(unit_path, unit)
    run(['systemctl', '--user', 'daemon-reload'])
    run(['systemctl', '--user', 'enable', '--now', unit_path.stem])
    for _ in range(30):
        ready = subprocess.run([str(args.bin / 'pg_isready'), '-h', str(sockets), '-p', str(args.port)], capture_output=True)
        if ready.returncode == 0:
            break
        time.sleep(0.2)
    else:
        raise RuntimeError('Dedicated PostgreSQL did not become ready')
    psql = [str(args.bin / 'psql'), '-X', '-v', 'ON_ERROR_STOP=1', '-h', str(sockets), '-p', str(args.port), '-d', 'postgres']
    existing_roles = set(run(psql + ['-Atc', "SELECT rolname FROM pg_roles WHERE rolname LIKE 'healthcare_%'"]).stdout.splitlines())
    for role, password in credentials.items():
        if role not in existing_roles:
            # Names are fixed above and passwords are hex; neither is user-controlled SQL.
            run(psql, input=f"CREATE ROLE {role} LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD '{password}';")
    existing_dbs = set(run(psql + ['-Atc', "SELECT datname FROM pg_database WHERE datname IN ('knowledge_healthcare','knowledge_healthcare_test')"]).stdout.splitlines())
    for db in ('knowledge_healthcare', 'knowledge_healthcare_test'):
        if db not in existing_dbs:
            run(psql, input=f'CREATE DATABASE {db} OWNER healthcare_admin;')
        run(psql, input=f'REVOKE ALL ON DATABASE {db} FROM PUBLIC; GRANT CONNECT ON DATABASE {db} TO healthcare_admin,healthcare_importer,healthcare_reader;')
    client = {}
    for suffix, db in (('', 'knowledge_healthcare'), ('TEST_', 'knowledge_healthcare_test')):
        for role, label in zip(roles, ('ADMIN', 'IMPORT', 'READ')):
            client[f'HEALTHCARE_{suffix}{label}_DSN'] = f'postgresql://{role}:{credentials[role]}@127.0.0.1:{args.port}/{db}'
    private_write(root / 'client-env.json', json.dumps(client, indent=2) + '\n')
    print(json.dumps({'cluster': str(data), 'port': args.port, 'service': unit_path.stem, 'client_env_file': str(root / 'client-env.json'), 'databases': ['knowledge_healthcare', 'knowledge_healthcare_test']}))


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as exc:
        # SQL input may contain a newly generated password. Do not echo command output.
        raise SystemExit(f'Provisioning command failed (exit {exc.returncode}); inspect the dedicated service status locally') from None
