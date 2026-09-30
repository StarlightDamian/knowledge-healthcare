"""PostgreSQL publication snapshots. Git remains the only content editing input.

Imports and pointer changes use the writer DSN. The web process uses an independent
SELECT-only DSN and never reads article JSON from disk as a runtime fallback.
"""
from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Iterator

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .model import ROOT, ValidationError, canonical_hash, load, read_json, validate

MIGRATION = ROOT / 'migrations/001_publication.sql'
RELEASE_RE = re.compile(r'^rel-[0-9a-f]{64}$')
_UNSET = object()


class ReleaseNotFound(LookupError):
    """Unknown, unpublished or unavailable release/content."""


class PublicationConflict(ValidationError):
    """The active version changed since the candidate was prepared."""


def connect(dsn: str):
    return psycopg.connect(dsn, row_factory=dict_row, connect_timeout=5,
                           options='-c statement_timeout=15000')


def migrate(admin_dsn: str) -> None:
    with connect(admin_dsn) as conn:
        conn.execute(MIGRATION.read_text(encoding='utf-8'))


def _editorial_records(root: Path) -> list:
    from .editorial import load_editorial_records
    return load_editorial_records(root)


def _check_changes(data: dict, baseline: dict, records: list, root: Path) -> dict:
    from .editorial import require_editorial_changes
    return require_editorial_changes(data, baseline, root=root, records=records)


def publication_records(data: dict, editorial_records: list | None = None, root: Path = ROOT) -> list[dict]:
    """Derived manifest entries; no second hand-maintained summaries or search text."""
    stats = validate(data)
    # Editorial due-date warnings are evaluated by maintenance checks. They are
    # clock-dependent and must not change an otherwise identical manifest hash.
    stats.pop('warnings', None)
    records = []
    def add(kind, rid, payload):
        records.append({'kind': kind, 'id': rid, 'sha256': canonical_hash(payload), 'payload': payload})
    for kind, key in [('condition', 'conditions'), ('source', 'sources')]:
        for item in data[key]:
            add(kind, item['id'], item)
    for key, module in data['knowledge'].items():
        add('knowledge', key, module)
    add('config', 'guide', {k: v for k, v in data.items() if k not in ('conditions', 'sources', 'knowledge')})
    add('config', 'stats', stats)
    add('config', 'editorial-checks', editorial_records or [])
    add('config', 'record-order', {key: [item['id'] for item in data[key]]
                                 for key in ('conditions', 'sources')})
    from .editorial import editorial_audit
    from .icd import coverage_icd
    editorial = editorial_audit(root=root, data=data, records=editorial_records or [])
    coverage = coverage_icd(data, root=root, editorial=editorial)
    # The complete decisions/gaps stay in the versioned Git audit. Bind their
    # hashes and taxonomy inputs to this release; bootstrap returns a small summary.
    add('config', 'editorial-summary', {
        key: value for key, value in editorial.items()
        if key not in ('targets', 'records', 'issues', 'qualified_condition_ids')
    } | {'audit_sha256': canonical_hash(editorial), 'issue_count': len(editorial['issues']),
         'qualified_conditions': len(editorial['qualified_condition_ids'])})
    add('config', 'coverage-icd', {
        key: value for key, value in coverage.items() if key not in ('category_states', 'gaps')
    } | {'audit_sha256': canonical_hash(coverage),
         'category_states_sha256': canonical_hash(coverage['category_states']),
         'gaps_sha256': canonical_hash(coverage['gaps'])})
    add('config', 'icd-definition', {key: read_json(Path(root) / 'data/icd' / (key + '.json'))
                                     for key in ('manifest', 'rules', 'mappings')})
    return sorted(records, key=lambda row: (row['kind'], row['id']))


def manifest_hash(records: list[dict]) -> str:
    return canonical_hash([{k: row[k] for k in ('kind', 'id', 'sha256')}
                           for row in sorted(records, key=lambda row: (row['kind'], row['id']))])


def _active(conn, *, lock=False):
    row = conn.execute('SELECT active_release_id FROM healthcare.publication_state WHERE singleton = true'
                       + (' FOR UPDATE' if lock else '')).fetchone()
    return row['active_release_id'] if row else None


def _release(conn, release_id: str, *, published: bool = True):
    if not RELEASE_RE.fullmatch(release_id):
        raise ReleaseNotFound('Release not found')
    row = conn.execute('SELECT * FROM healthcare.releases WHERE id = %s'
                       + (' AND published_at IS NOT NULL' if published else ''), (release_id,)).fetchone()
    if row is None:
        raise ReleaseNotFound('Release not found')
    return row


def _read_records(conn, release_id: str) -> list[dict]:
    return conn.execute('''SELECT c.kind, c.id, c.sha256, c.payload
        FROM healthcare.release_items i JOIN healthcare.content_revisions c
        ON (c.kind,c.id,c.sha256) = (i.kind,i.id,i.content_sha256)
        WHERE i.release_id = %s ORDER BY c.kind,c.id''', (release_id,)).fetchall()


def _inflate(records: list[dict]) -> tuple[dict, list]:
    configs = {r['id']: r['payload'] for r in records if r['kind'] == 'config'}
    data = copy.deepcopy(configs['guide'])
    for kind, key in [('condition', 'conditions'), ('source', 'sources')]:
        values = {row['id']: row['payload'] for row in records if row['kind'] == kind}
        data[key] = [values[rid] for rid in configs['record-order'][key]]
    data['knowledge'] = {r['id']: r['payload'] for r in records if r['kind'] == 'knowledge'}
    return data, configs['editorial-checks']


def _verify_snapshot(conn, release_id: str) -> tuple[dict, list]:
    release = _release(conn, release_id, published=False)
    records = _read_records(conn, release_id)
    if len(records) != release['record_count'] or manifest_hash(records) != release['manifest_sha256']:
        raise ValidationError('Database release manifest does not match the imported manifest')
    if any(canonical_hash(r['payload']) != r['sha256'] for r in records):
        raise ValidationError('Database content hash mismatch')
    data, checks = _inflate(records)
    validate(data)
    return data, checks


def import_release(dsn: str, root: Path = ROOT, *, git_commit: str,
                   allow_initial_baseline: bool = False, data: dict | None = None,
                   editorial_records: list | None = None) -> dict:
    """Atomically import and read back a candidate, without publishing it.

    The explicit baseline flag migrates existing content without inventing an
    editorial approval. Subsequent additions/changes must pass editorial checks.
    `data` and `editorial_records` also allow deterministic migration/integration fixtures.
    """
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', git_commit):
        raise ValidationError('A full Git commit SHA is required')
    root = Path(root)
    data = load(root) if data is None else data
    checks = _editorial_records(root) if editorial_records is None else editorial_records
    records = publication_records(data, checks, root=root)
    digest = manifest_hash(records)
    release_id = 'rel-' + digest
    with connect(dsn) as conn:
        # Serializes import/publication decisions, not ordinary public reads.
        conn.execute('SELECT pg_advisory_xact_lock(734622101)')
        existing = conn.execute('SELECT id, published_at FROM healthcare.releases WHERE id = %s', (release_id,)).fetchone()
        if existing:
            _verify_snapshot(conn, release_id)
            return {'release_id': release_id, 'manifest_sha256': digest, 'imported': False,
                    'published': existing['published_at'] is not None, 'record_count': len(records)}
        base_id = _active(conn, lock=True)
        if base_id:
            baseline, _ = _verify_snapshot(conn, base_id)
            _check_changes(data, baseline, checks, root)
        elif not allow_initial_baseline:
            raise ValidationError('An empty publication store requires an explicit initial baseline import')
        conn.execute('''INSERT INTO healthcare.releases
            (id,manifest_sha256,git_commit,base_release_id,record_count,baseline_import)
            VALUES (%s,%s,%s,%s,%s,%s)''',
            (release_id, digest, git_commit, base_id, len(records), base_id is None))
        # psycopg pipelines executemany: large catalogs do not need two network
        # round trips for each immutable document during an import.
        with conn.cursor() as cursor:
            cursor.executemany('''INSERT INTO healthcare.content_revisions(kind,id,sha256,payload)
                VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING''',
                [(row['kind'], row['id'], row['sha256'], Jsonb(row['payload'])) for row in records])
            cursor.executemany('''INSERT INTO healthcare.release_items(release_id,kind,id,content_sha256)
                VALUES (%s,%s,%s,%s)''',
                [(release_id, row['kind'], row['id'], row['sha256']) for row in records])
        _verify_snapshot(conn, release_id)
        return {'release_id': release_id, 'manifest_sha256': digest, 'imported': True,
                'published': False, 'record_count': len(records), 'base_release_id': base_id}


def publish_release(dsn: str, release_id: str, *, expected_current=_UNSET, root: Path = ROOT) -> dict:
    """Validate a candidate again and atomically publish/activate it."""
    with connect(dsn) as conn:
        conn.execute('SELECT pg_advisory_xact_lock(734622101)')
        current = _active(conn, lock=True)
        release = _release(conn, release_id, published=False)
        if expected_current is not _UNSET and current != expected_current:
            raise PublicationConflict('Active release changed; re-read the publication state')
        if current == release_id:
            return {'release_id': release_id, 'previous_release_id': current, 'changed': False}
        if release['published_at'] is not None:
            raise PublicationConflict('Use activate_release to roll back to an already published release')
        if release['base_release_id'] != current:
            raise PublicationConflict('Candidate was prepared against another active release')
        data, checks = _verify_snapshot(conn, release_id)
        if current:
            baseline, _ = _verify_snapshot(conn, current)
            _check_changes(data, baseline, checks, Path(root))
        elif not release['baseline_import']:
            raise ValidationError('Initial migration was not explicitly authorized')
        conn.execute('UPDATE healthcare.releases SET published_at = now() WHERE id = %s', (release_id,))
        conn.execute('UPDATE healthcare.publication_state SET active_release_id = %s WHERE singleton = true', (release_id,))
        return {'release_id': release_id, 'previous_release_id': current, 'changed': True}


def activate_release(dsn: str, release_id: str, *, expected_current: str | None) -> dict:
    """Explicit, optimistic rollback to a previously published immutable version."""
    with connect(dsn) as conn:
        conn.execute('SELECT pg_advisory_xact_lock(734622101)')
        current = _active(conn, lock=True)
        if current != expected_current:
            raise PublicationConflict('Active release changed; rollback was not applied')
        _release(conn, release_id)
        _verify_snapshot(conn, release_id)
        conn.execute('UPDATE healthcare.publication_state SET active_release_id = %s WHERE singleton = true', (release_id,))
        return {'release_id': release_id, 'previous_release_id': current, 'changed': current != release_id}


class PublicationStore:
    """Read API using a SELECT-only database login and immutable release IDs."""
    def __init__(self, dsn: str):
        self.dsn = dsn

    def active_release(self) -> str:
        with connect(self.dsn) as conn:
            rid = _active(conn)
            if rid is None:
                raise ReleaseNotFound('No published release')
            _release(conn, rid)
            return rid

    def release(self, release_id: str) -> dict:
        with connect(self.dsn) as conn:
            row = _release(conn, release_id)
            return {'release_id': row['id'], 'manifest_sha256': row['manifest_sha256'],
                    'git_commit': row['git_commit'], 'published_at': row['published_at'].isoformat()}

    def document(self, release_id: str, kind: str, rid: str):
        with connect(self.dsn) as conn:
            _release(conn, release_id)
            row = conn.execute('''SELECT c.payload FROM healthcare.release_items i
                JOIN healthcare.content_revisions c ON (c.kind,c.id,c.sha256)=(i.kind,i.id,i.content_sha256)
                WHERE i.release_id=%s AND i.kind=%s AND i.id=%s''', (release_id, kind, rid)).fetchone()
            if row is None:
                raise ReleaseNotFound('Content not found in this release')
            return row['payload']

    def documents(self, release_id: str, kind: str, ids: list[str] | None = None) -> list[dict]:
        with connect(self.dsn) as conn:
            _release(conn, release_id)
            sql = '''SELECT c.id,c.payload FROM healthcare.release_items i
                JOIN healthcare.content_revisions c ON (c.kind,c.id,c.sha256)=(i.kind,i.id,i.content_sha256)
                WHERE i.release_id=%s AND i.kind=%s'''
            params = [release_id, kind]
            if ids is not None:
                sql += ' AND i.id = ANY(%s)'
                params.append(ids)
            rows = conn.execute(sql + ' ORDER BY c.id', params).fetchall()
            if ids is None:
                return [r['payload'] for r in rows]
            values = {r['id']: r['payload'] for r in rows}
            if set(ids) - values.keys():
                raise ReleaseNotFound('Some content IDs are not present in this release')
            return [values[rid] for rid in dict.fromkeys(ids)]

    def condition_ids(self, release_id: str) -> list[str]:
        with connect(self.dsn) as conn:
            _release(conn, release_id)
            rows = conn.execute("SELECT id FROM healthcare.release_items WHERE release_id=%s AND kind='condition' ORDER BY id", (release_id,)).fetchall()
            return [row['id'] for row in rows]

    def knowledge_catalog(self, release_id: str) -> dict:
        with connect(self.dsn) as conn:
            _release(conn, release_id)
            rows = conn.execute('''SELECT c.id, c.payload->'title' AS title,
                (SELECT jsonb_agg(jsonb_build_object('id', entry->'id', 'title', entry->'title'))
                 FROM jsonb_array_elements(c.payload->'entries') entry) AS entry_index
                FROM healthcare.release_items i JOIN healthcare.content_revisions c
                ON (c.kind,c.id,c.sha256)=(i.kind,i.id,i.content_sha256)
                WHERE i.release_id=%s AND i.kind='knowledge' ORDER BY i.id''', (release_id,)).fetchall()
            return {row['id']: row for row in rows}

    def catalog(self, release_id: str, offset: int, limit: int) -> dict:
        if offset < 0 or not 1 <= limit <= 1000:
            raise ValidationError('Catalog offset/limit out of range')
        with connect(self.dsn) as conn:
            _release(conn, release_id)
            total = conn.execute("SELECT count(*) AS n FROM healthcare.release_items WHERE release_id=%s AND kind='condition'", (release_id,)).fetchone()['n']
            # Projection happens in SQL: long article bodies do not travel to the API process.
            rows = conn.execute('''SELECT c.payload->'id' AS id, c.payload->'kind' AS kind,
                c.payload->'names' AS names, c.payload->'aliases' AS aliases,
                c.payload->'symptom_terms' AS symptom_terms, c.payload->'departments' AS departments,
                c.payload->'primary_domain' AS primary_domain, c.payload->'reference_urgency' AS reference_urgency,
                c.payload#>'{sections,summary,text}' AS summary
                FROM healthcare.release_items i JOIN healthcare.content_revisions c
                ON (c.kind,c.id,c.sha256)=(i.kind,i.id,i.content_sha256)
                WHERE i.release_id=%s AND i.kind='condition' ORDER BY i.id LIMIT %s OFFSET %s''',
                (release_id, limit, offset)).fetchall()
        items = []
        for row in rows:
            summary = row.pop('summary')
            row['sections'] = {'summary': {'text': {lang: re.split(r'\n\s*\n', text.strip(), maxsplit=1)[0]
                                                  for lang, text in summary.items()}}}
            items.append(row)
        return {'release_id': release_id, 'total': total, 'offset': offset, 'limit': limit, 'items': items}

    def snapshot(self, release_id: str) -> tuple[dict, list]:
        with connect(self.dsn) as conn:
            _release(conn, release_id)
            return _verify_snapshot(conn, release_id)

    def iter_conditions(self, release_id: str, ids: list[str]) -> Iterator[dict]:
        # Small independent reads avoid a transaction held open by a slow download.
        for offset in range(0, len(ids), 100):
            yield from self.documents(release_id, 'condition', ids[offset:offset + 100])
