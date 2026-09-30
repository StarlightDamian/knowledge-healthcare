"""Opt-in 16,000-row synthetic capacity and real backup/restore drill.

Run only after browser tests have released the disposable *_test database:
HEALTHCARE_RUN_CAPACITY=1 python -m unittest tests.test_store_capacity -v
The original test publication is restored even when an assertion fails.
"""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import psycopg.conninfo
import uvicorn

from src.guide.api import API, create_app
from src.guide.model import canonical_hash, load
from src.guide.store import PublicationStore, connect, import_release, migrate, publish_release


@unittest.skipUnless(os.environ.get('HEALTHCARE_RUN_CAPACITY') == '1', 'Opt-in synthetic capacity drill')
class CapacityTests(unittest.TestCase):
    def test_large_catalog_streaming_export_and_backup_restore(self):
        admin, writer, reader = [os.environ['HEALTHCARE_TEST_' + key + '_DSN']
                                 for key in ('ADMIN', 'IMPORT', 'READ')]
        connection = psycopg.conninfo.conninfo_to_dict(admin)
        if not connection.get('dbname', '').endswith('_test'):
            raise RuntimeError('Capacity drill requires a dedicated *_test database')
        env = dict(os.environ)
        for key, var in [('host', 'PGHOST'), ('port', 'PGPORT'), ('user', 'PGUSER'),
                         ('password', 'PGPASSWORD'), ('dbname', 'PGDATABASE')]:
            if key in connection:
                env[var] = connection[key]
        binary_root = os.environ.get('HEALTHCARE_PG_BIN')
        def pg_tool(name, *args):
            executable = str(Path(binary_root) / name) if binary_root else shutil.which(name)
            if not executable:
                raise RuntimeError(name + ' is required for the restore drill')
            result = subprocess.run([executable, *args], env=env, capture_output=True)
            if result.returncode:
                raise RuntimeError(name + ' failed with status ' + str(result.returncode))
        def reset_schema():
            with connect(admin) as conn:
                conn.execute('DROP SCHEMA healthcare CASCADE')
        store = PublicationStore(reader)
        original_id = store.active_release()
        original_data, _ = store.snapshot(original_id)
        original_hash = canonical_hash(original_data)
        metrics = {'synthetic': True, 'counted_as_medical_coverage': False, 'conditions': 16000}
        with tempfile.TemporaryDirectory(prefix='healthcare-restore-') as tmp:
            backup = Path(tmp) / 'baseline.dump'
            pg_tool('pg_dump', '--format=custom', '--no-owner', '--schema=healthcare', '--file=' + str(backup))
            metrics['backup_bytes'] = backup.stat().st_size
            metrics['backup_sha256'] = hashlib.sha256(backup.read_bytes()).hexdigest()
            try:
                reset_schema()
                migrate(admin)
                data = load()
                sample = data['conditions'][0]
                for i in range(16000 - len(data['conditions'])):
                    data['conditions'].append({**sample,
                        'id': 'capacity-case-' + str(i).zfill(5),
                        'names': {'en': 'SYNTHETIC capacity case ' + str(i), 'zh-CN': '容量测试模拟条目 ' + str(i)},
                        'aliases': {'en': [], 'zh-CN': []}, 'clinical_region': 'SYNTHETIC_TEST_ONLY',
                        'related_ids': [], 'coding': [], 'study_ids': []})
                data['project'] = {**data['project'], 'version': 'synthetic-capacity-test-only'}
                started = time.monotonic()
                receipt = import_release(writer, git_commit='e' * 40, data=data,
                                         editorial_records=[], allow_initial_baseline=True)
                rid = receipt['release_id']
                publish_release(writer, rid, expected_current=None)
                metrics['import_and_readback_seconds'] = round(time.monotonic() - started, 3)
                del data
                app = create_app(reader)
                sock = socket.socket()
                sock.bind(('127.0.0.1', 0))
                base = 'http://127.0.0.1:' + str(sock.getsockname()[1])
                server = uvicorn.Server(uvicorn.Config(app, log_level='critical', access_log=False))
                thread = threading.Thread(target=server.run, kwargs={'sockets': [sock]}, daemon=True)
                thread.start()
                for _ in range(100):
                    if server.started:
                        break
                    time.sleep(.05)
                self.assertTrue(server.started)
                try:
                    started = time.monotonic()
                    seen, transferred = set(), 0
                    for offset in range(0, 16000, 1000):
                        with urlopen(base + API + '/catalog?' + urlencode({
                                'release_id': rid, 'offset': offset, 'limit': 1000}), timeout=60) as response:
                            raw = response.read()
                        transferred += len(raw)
                        page = json.loads(raw)
                        self.assertEqual(page['total'], 16000)
                        self.assertEqual(len(page['items']), 1000)
                        self.assertTrue(all(set(item['sections']) == {'summary'} for item in page['items']))
                        seen.update(item['id'] for item in page['items'])
                    self.assertEqual(len(seen), 16000)
                    metrics['catalog_bytes'] = transferred
                    metrics['catalog_seconds'] = round(time.monotonic() - started, 3)
                    started = time.monotonic()
                    request = Request(base + API + '/exports/conditions.csv', data=urlencode({
                        'release_id': rid, 'locale': 'en', 'scope': 'all', 'ids': '[]'}).encode(),
                        headers={'Content-Type': 'application/x-www-form-urlencoded'})
                    with urlopen(request, timeout=120) as response:
                        self.assertNotIn('content-length', response.headers)
                        rows = csv.reader(io.TextIOWrapper(response, encoding='utf-8-sig', newline=''))
                        self.assertEqual(len(next(rows)), 22)
                        exported = 0
                        for row in rows:
                            self.assertEqual(len(row), 22)
                            self.assertIn(row[0], seen)
                            self.assertIn('\n', row[7])
                            exported += 1
                    self.assertEqual(exported, 16000)
                    metrics['export_rows'] = exported
                    metrics['export_seconds'] = round(time.monotonic() - started, 3)
                finally:
                    server.should_exit = True
                    thread.join(10)
            finally:
                reset_schema()
                pg_tool('pg_restore', '--exit-on-error', '--no-owner', '--dbname=' + connection['dbname'], str(backup))
            self.assertEqual(store.active_release(), original_id)
            restored, _ = store.snapshot(original_id)
            self.assertEqual(canonical_hash(restored), original_hash)
            metrics['restore_exact_snapshot'] = True
            print(json.dumps(metrics, sort_keys=True))


if __name__ == '__main__':
    unittest.main()
