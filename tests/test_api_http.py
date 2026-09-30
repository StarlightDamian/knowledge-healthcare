"""Real HTTP, real PostgreSQL contract tests without an additional HTTP dependency."""
import copy
import csv
import io
import json
import socket
import threading
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import psycopg
import uvicorn

from src.guide.api import API, create_app, csv_cell
from src.guide.store import activate_release, import_release, publish_release
from tests.test_store_publication import AVAILABLE, database_fixture


class CSVTests(unittest.TestCase):
    def test_formula_guards_quotes_and_embedded_lines(self):
        for value in ('=CMD()', ' +1', '\ufeff＠cmd', '\ttext', '\ntext', '－3'):
            self.assertTrue(csv_cell(value).startswith('"\''))
        self.assertEqual(csv_cell('A "quote"\nnext'), '"A ""quote""\nnext"')


@unittest.skipUnless(AVAILABLE, 'Real PostgreSQL test DSNs are required')
class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.admin, cls.writer, cls.reader, cls.data, cls.baseline = database_fixture()
        cls.app = create_app(cls.reader)
        cls.store = cls.app.state.store
        sock = socket.socket()
        sock.bind(('127.0.0.1', 0))
        cls.base = 'http://127.0.0.1:' + str(sock.getsockname()[1])
        cls.server = uvicorn.Server(uvicorn.Config(cls.app, log_level='critical', access_log=False))
        cls.thread = threading.Thread(target=cls.server.run, kwargs={'sockets': [sock]}, daemon=True)
        cls.thread.start()
        for _ in range(100):
            if cls.server.started:
                break
            time.sleep(.05)
        if not cls.server.started:
            raise RuntimeError('HTTP server failed to start')

    @classmethod
    def tearDownClass(cls):
        cls.server.should_exit = True
        cls.thread.join(10)

    def setUp(self):
        current = self.store.active_release()
        if current != self.baseline:
            activate_release(self.writer, self.baseline, expected_current=current)

    def request(self, path, *, body=None, headers=None):
        request = Request(self.base + path, data=body, headers=headers or {})
        try:
            response = urlopen(request, timeout=20)
        except HTTPError as exc:
            response = exc
        with response:
            raw = response.read()
            parsed = json.loads(raw) if 'application/json' in response.headers.get('content-type', '') else raw
            return response.status, response.headers, parsed

    def get(self, path, release=True):
        return self.request(API + path + ('?' + urlencode({'release_id': self.baseline}) if release else ''))

    def post(self, path, body, headers=None):
        return self.request(API + path, body=json.dumps(body).encode(), headers={
            'Content-Type': 'application/json', **(headers or {})})

    def test_bootstrap_has_small_metadata_not_full_articles(self):
        status, headers, body = self.get('/bootstrap', False)
        self.assertEqual(status, 200)
        self.assertEqual(body['release_id'], self.baseline)
        self.assertEqual(body['stats']['conditions'], len(self.data['conditions']))
        self.assertNotIn('conditions', body)
        self.assertNotIn('entries', body['knowledge']['cancer'])
        self.assertEqual(len(body['knowledge']['cancer']['entry_index']), 36)
        self.assertEqual(len(body['locales']), 12)
        self.assertTrue(body['coverage']['denominator_frozen'])
        self.assertFalse(body['coverage']['target_met'])
        self.assertEqual(body['editorial']['conditions'], len(self.data['conditions']))
        self.assertIn('no-store', headers['cache-control'])
        self.assertNotIn('Access-Control-Allow-Origin', headers)
        self.assertLess(len(json.dumps(body)), 500000)

    def test_catalog_and_detail_are_fixed_to_requested_release(self):
        data = copy.deepcopy(self.data)
        data['project']['version'] = 'http-next-release'
        candidate = import_release(self.writer, git_commit='d' * 40, data=data)
        if candidate['published']:
            activate_release(self.writer, candidate['release_id'], expected_current=self.baseline)
        else:
            publish_release(self.writer, candidate['release_id'], expected_current=self.baseline)
        status, _, body = self.get('/catalog')
        self.assertEqual(status, 200)
        self.assertEqual(body['release_id'], self.baseline)
        cid = self.data['conditions'][0]['id']
        self.assertEqual(self.get('/conditions/' + cid)[2]['condition'], self.data['conditions'][0])
        self.assertEqual(self.get('/bootstrap', False)[2]['release_id'], candidate['release_id'])
        self.assertEqual(self.request(API + '/catalog?release_id=rel-' + '0' * 64)[0], 404)
        self.assertEqual(self.request(API + '/catalog')[0], 422)

    def test_batch_limits_ids_and_explicit_missing_items(self):
        ids = [condition['id'] for condition in self.data['conditions'][:4]]
        status, _, body = self.post('/conditions/batch', {'release_id': self.baseline, 'ids': ids})
        self.assertEqual(status, 200)
        self.assertEqual([item['id'] for item in body['conditions']], ids)
        self.assertGreater(len(body['sources']), 0)
        self.assertEqual(self.post('/conditions/batch', {'release_id': self.baseline, 'ids': ids * 26})[0], 422)
        self.assertEqual(self.post('/conditions/batch', {'release_id': self.baseline, 'ids': ['does-not-exist']})[0], 404)
        self.assertEqual(self.post('/conditions/batch', {'release_id': self.baseline, 'ids': ["' OR TRUE --"]})[0], 422)

    def test_post_same_origin_enforcement(self):
        body = {'release_id': self.baseline, 'ids': []}
        self.assertEqual(self.post('/conditions/batch', body, {'Origin': 'https://unrelated.example'})[0], 403)
        self.assertEqual(self.post('/conditions/batch', body, {'Origin': self.base})[0], 200)
        self.assertEqual(self.post('/conditions/batch', body, {'Sec-Fetch-Site': 'cross-site'})[0], 403)
        self.assertEqual(self.post('/conditions/batch', body, {'Origin': 'null'})[0], 403)
        self.assertEqual(self.post('/conditions/batch', body, {
            'Origin': 'null', 'Sec-Fetch-Site': 'same-origin'})[0], 200)

    def test_full_csv_22_columns_multiline_and_english_fallback(self):
        fields = {'release_id': self.baseline, 'scope': 'all', 'ids': '[]', 'locale': 'ar'}
        status, headers, body = self.request(API + '/exports/conditions.csv', body=urlencode(fields).encode(),
                                           headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.assertEqual(status, 200)
        self.assertEqual(headers['X-Healthcare-Release'], self.baseline)
        self.assertNotIn('content-length', headers)
        rows = list(csv.reader(io.StringIO(body.decode('utf-8-sig'), newline='')))
        self.assertEqual(len(rows), len(self.data['conditions']) + 1)
        self.assertEqual(len(rows[0]), 22)
        by_id = {row[0]: row for row in rows[1:]}
        for condition in self.data['conditions']:
            row = by_id[condition['id']]
            self.assertEqual(row[1], condition['names']['en'])
            for field in self.data['fields']:
                # Read the existing formula-escaped wire contract through CSV.
                text = condition['sections'][field['id']]['text']['en']
                expected = next(csv.reader([csv_cell(text)]))[0]
                self.assertEqual(row[rows[0].index(field['id'])], expected)

    def test_knowledge_exact_and_no_static_json_fallback(self):
        self.assertEqual(self.get('/knowledge/lifecycle')[2]['module'], self.data['knowledge']['lifecycle'])
        self.assertEqual(self.request('/healthcare/data/conditions/common-cold.json')[0], 404)
        self.assertEqual(self.request('/data/conditions/common-cold.json')[0], 404)

    def test_health_and_database_failure_not_empty_catalog(self):
        self.assertEqual(self.get('/healthz', False)[2]['status'], 'ok')
        with patch.object(self.store, 'active_release', side_effect=psycopg.OperationalError('private-password-sentinel')):
            status, _, body = self.get('/bootstrap', False)
        self.assertEqual(status, 503)
        self.assertNotIn('private-password-sentinel', json.dumps(body))
        self.assertNotIn('conditions', body)


if __name__ == '__main__':
    unittest.main()
