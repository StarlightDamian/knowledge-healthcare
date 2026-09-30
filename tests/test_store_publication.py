"""Real PostgreSQL tests; the dedicated *_test database is disposable test data."""
import copy
import os
import unittest

import psycopg

from src.guide.model import load, canonical_hash, ValidationError
from src.guide.store import (PublicationStore, PublicationConflict, ReleaseNotFound,
    activate_release, connect, import_release, migrate, publish_release)

DSNS = ('HEALTHCARE_TEST_ADMIN_DSN', 'HEALTHCARE_TEST_IMPORT_DSN', 'HEALTHCARE_TEST_READ_DSN')
AVAILABLE = all(os.environ.get(key) for key in DSNS)
_fixture = None


def database_fixture():
    global _fixture
    if _fixture is None:
        admin, writer, reader = [os.environ[key] for key in DSNS]
        with connect(admin) as conn:
            name = conn.execute('SELECT current_database() AS name').fetchone()['name']
            if not name.endswith('_test'):
                raise RuntimeError('Refusing to reset a database without the _test suffix')
            conn.execute('DROP SCHEMA IF EXISTS healthcare CASCADE')
        migrate(admin)
        data = load()
        receipt = import_release(writer, git_commit='a' * 40, allow_initial_baseline=True, data=data)
        publish_release(writer, receipt['release_id'], expected_current=None)
        _fixture = (admin, writer, reader, data, receipt['release_id'])
    return _fixture


@unittest.skipUnless(AVAILABLE, 'Real PostgreSQL test DSNs are required')
class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.admin, cls.writer, cls.reader, cls.data, cls.baseline = database_fixture()
        cls.store = PublicationStore(cls.reader)

    def setUp(self):
        current = self.store.active_release()
        if current != self.baseline:
            activate_release(self.writer, self.baseline, expected_current=current)

    def candidate(self, suffix):
        data = copy.deepcopy(self.data)
        data['project']['version'] = 'test-' + suffix
        return import_release(self.writer, git_commit='b' * 40, data=data)

    def test_exact_migration_and_idempotent_import(self):
        copied, checks = self.store.snapshot(self.baseline)
        self.assertEqual(canonical_hash(copied), canonical_hash(self.data))
        receipt = import_release(self.writer, git_commit='a' * 40, data=self.data)
        self.assertFalse(receipt['imported'])
        self.assertTrue(receipt['published'])
        self.assertEqual(receipt['release_id'], self.baseline)
        self.assertEqual(sum(len(m['entries']) for m in copied['knowledge'].values()), 56)

    def test_reader_has_no_write_permissions(self):
        with self.assertRaises(psycopg.errors.InsufficientPrivilege), connect(self.reader) as conn:
            conn.execute('UPDATE healthcare.publication_state SET active_release_id = active_release_id')
        with self.assertRaises(psycopg.errors.InsufficientPrivilege), connect(self.reader) as conn:
            conn.execute("INSERT INTO healthcare.content_revisions VALUES ('x','x',%s,'{}')", ('f' * 64,))

    def test_immutable_content_manifest_and_release(self):
        for sql, params in [
            ('UPDATE healthcare.content_revisions SET payload=payload', ()),
            ('DELETE FROM healthcare.release_items WHERE release_id=%s', (self.baseline,)),
            ('UPDATE healthcare.releases SET published_at=now() WHERE id=%s', (self.baseline,)),
            ('''INSERT INTO healthcare.release_items SELECT release_id,kind,id||'-extra',content_sha256
                FROM healthcare.release_items WHERE release_id=%s LIMIT 1''', (self.baseline,))]:
            with self.subTest(sql=sql), self.assertRaises(psycopg.Error), connect(self.writer) as conn:
                conn.execute(sql, params)

    def test_pending_candidate_hidden_then_publish_and_rollback(self):
        candidate = self.candidate('publish')
        rid = candidate['release_id']
        with self.assertRaises(ReleaseNotFound):
            self.store.release(rid)
        self.assertEqual(self.store.active_release(), self.baseline)
        publish_release(self.writer, rid, expected_current=self.baseline)
        self.assertEqual(self.store.active_release(), rid)
        self.assertEqual(self.store.document(self.baseline, 'config', 'guide')['project'], self.data['project'])
        activate_release(self.writer, self.baseline, expected_current=rid)
        self.assertEqual(self.store.active_release(), self.baseline)
        self.assertEqual(self.store.release(rid)['release_id'], rid)

    def test_stale_publication_does_not_replace_current(self):
        first, stale = self.candidate('first'), self.candidate('stale')
        publish_release(self.writer, first['release_id'], expected_current=self.baseline)
        with self.assertRaises(PublicationConflict):
            publish_release(self.writer, stale['release_id'], expected_current=self.baseline)
        self.assertEqual(self.store.active_release(), first['release_id'])
        with self.assertRaises(PublicationConflict):
            activate_release(self.writer, self.baseline, expected_current=stale['release_id'])

    def test_failed_import_keeps_current_and_does_not_leave_rows(self):
        data = copy.deepcopy(self.data)
        data['conditions'][0]['sections']['diet']['text']['en'] += '\n\nA changed clinical claim.'
        with connect(self.reader) as conn:
            before = conn.execute('SELECT count(*) AS n FROM healthcare.releases').fetchone()['n']
        with self.assertRaises(ValidationError):
            import_release(self.writer, git_commit='c' * 40, data=data, allow_initial_baseline=True)
        self.assertEqual(self.store.active_release(), self.baseline)
        with connect(self.reader) as conn:
            self.assertEqual(conn.execute('SELECT count(*) AS n FROM healthcare.releases').fetchone()['n'], before)

    def test_catalog_projection_and_parameterized_ids(self):
        page = self.store.catalog(self.baseline, 3, 5)
        self.assertEqual(len(page['items']), 5)
        self.assertEqual(page['total'], len(self.data['conditions']))
        for row in page['items']:
            self.assertEqual(set(row['sections']), {'summary'})
            self.assertNotIn('\n\n', row['sections']['summary']['text']['en'])
        with self.assertRaises(ReleaseNotFound):
            self.store.document(self.baseline, 'condition', "' OR TRUE --")
        with self.assertRaises(ReleaseNotFound):
            self.store.catalog('rel-' + '0' * 64, 0, 5)
        self.assertEqual(self.store.knowledge_catalog(self.baseline)['cancer']['id'], 'cancer')


if __name__ == '__main__':
    unittest.main()
