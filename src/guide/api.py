"""Same-origin, read-only HTTP interface to immutable PostgreSQL publications."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Annotated
from urllib.parse import parse_qs, urlsplit

import psycopg
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from .model import ROOT, ID_RE, ValidationError
from .store import PublicationStore, ReleaseNotFound

PREFIX = '/healthcare'
API = PREFIX + '/api/v1'


class BatchRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    release_id: str = Field(max_length=68)
    ids: list[Annotated[str, Field(max_length=128, pattern=ID_RE.pattern)]] = Field(max_length=100)


def csv_cell(value) -> str:
    text = '' if value is None else str(value)
    if re.match(r'^[\s\ufeff]*[=+@\-＝＋＠－]', text) or text.startswith(('\t', '\r', '\n')):
        text = "'" + text
    return '"' + text.replace('"', '""') + '"'


def csv_rows(store: PublicationStore, release_id: str, ids: list[str], fields: list,
             sources: list, locale: str):
    """The existing 22-column contract, with complete text and embedded newlines."""
    source_urls = {source['id']: source['url'] for source in sources}
    headers = ['id', 'name', 'kind', 'primary_domain', 'review_status', 'clinical_region',
               'editorial_updated_at', *[field['id'] for field in fields], 'source_urls']
    yield '\ufeff' + ','.join(csv_cell(value) for value in headers)
    for condition in store.iter_conditions(release_id, ids):
        names = condition['names']
        cells = [condition['id'], names.get(locale, names['en']), condition['kind'],
                 condition['primary_domain'], condition['review']['status'], condition['clinical_region'],
                 condition['review']['editorial_updated_at']]
        cells.extend(condition['sections'][field['id']]['text'].get(
            locale, condition['sections'][field['id']]['text']['en']) for field in fields)
        cells.append(' | '.join(source_urls[sid] for sid in condition['source_ids']))
        yield '\r\n' + ','.join(csv_cell(value) for value in cells)


def _ids(ids: list[str]) -> list[str]:
    if any(not isinstance(cid, str) or not ID_RE.fullmatch(cid) for cid in ids):
        raise HTTPException(422, 'Invalid condition ID')
    return list(dict.fromkeys(ids))


def create_app(read_dsn: str | None = None, root: Path = ROOT) -> FastAPI:
    """Factory also used by the integration/browser tests with their isolated DB."""
    dsn = read_dsn or os.environ.get('HEALTHCARE_READ_DSN')
    if not dsn:
        raise RuntimeError('HEALTHCARE_READ_DSN is required')
    root = Path(root)
    store = PublicationStore(dsn)
    app = FastAPI(title='Open Medical Guide', docs_url=None, redoc_url=None, openapi_url=None)
    app.state.store = store

    @app.middleware('http')
    async def same_origin(request: Request, call_next):
        # No CORS permissions are granted. Browser POSTs also receive an explicit
        # origin check, including HTML form exports (which can bypass CORS reads).
        if request.method not in ('GET', 'HEAD'):
            origin = request.headers.get('origin')
            try:
                parsed_origin = urlsplit(origin) if origin else None
                origin_matches = not parsed_origin or (
                    parsed_origin.netloc == request.headers.get('host')
                    and parsed_origin.scheme == request.url.scheme)
                # Chromium's privacy-preserving native download form can send
                # Origin:null under Referrer-Policy:no-referrer. Fetch Metadata
                # still proves that this browser navigation is same-origin.
                if origin == 'null' and request.headers.get('sec-fetch-site') == 'same-origin':
                    origin_matches = True
            except ValueError:
                origin_matches = False
            if request.headers.get('sec-fetch-site') == 'cross-site' or (
                not origin_matches
            ):
                return JSONResponse({'detail': 'Same-origin request required'}, status_code=403)
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Cache-Control'] = 'no-store, no-transform'
        return response

    @app.exception_handler(ReleaseNotFound)
    async def missing_release(request, exc):
        return JSONResponse({'detail': str(exc)}, status_code=404)

    @app.exception_handler(ValidationError)
    async def invalid_data(request, exc):
        return JSONResponse({'detail': str(exc)}, status_code=422)

    @app.exception_handler(psycopg.Error)
    async def database_unavailable(request, exc):
        # Database messages can contain connection details; expose no DSN/SQL.
        return JSONResponse({'detail': 'Content service temporarily unavailable'}, status_code=503)

    def config(release_id):
        return store.document(release_id, 'config', 'guide')

    def referenced(conditions, guide, release_id):
        ids = list(dict.fromkeys(sid for condition in conditions for sid in condition['source_ids']))
        study_ids = {sid for condition in conditions for sid in condition['study_ids']}
        return {'sources': store.documents(release_id, 'source', ids),
                'studies': [study for study in guide['studies'] if study['id'] in study_ids]}

    @app.get(PREFIX, include_in_schema=False)
    def redirect():
        return RedirectResponse(PREFIX + '/', status_code=308)

    @app.get(PREFIX + '/', include_in_schema=False)
    @app.get(PREFIX + '/index.html', include_in_schema=False)
    def index():
        return FileResponse(root / 'index.html', media_type='text/html')

    @app.get(API + '/bootstrap')
    def bootstrap():
        release_id = store.active_release()
        guide = config(release_id)
        payload = {key: value for key, value in guide.items() if key not in ('backlog', 'reviewers')}
        source_ids = {sid for rule in guide['rules']['rules'] for sid in rule['source_ids']}
        source_ids.update(study['id'] for study in guide['studies'])
        payload.update(store.release(release_id))
        payload['sources'] = store.documents(release_id, 'source', sorted(source_ids))
        payload['stats'] = store.document(release_id, 'config', 'stats')
        payload['coverage'] = store.document(release_id, 'config', 'coverage-icd')
        payload['editorial'] = store.document(release_id, 'config', 'editorial-summary')
        payload['knowledge'] = store.knowledge_catalog(release_id)
        return payload

    @app.get(API + '/catalog')
    def catalog(release_id: str, offset: int = Query(0, ge=0), limit: int = Query(1000, ge=1, le=1000)):
        return store.catalog(release_id, offset, limit)

    # Register the literal batch route before the variable condition path.
    @app.post(API + '/conditions/batch')
    def batch(body: BatchRequest):
        ids = _ids(body.ids)
        conditions = store.documents(body.release_id, 'condition', ids)
        return {'release_id': body.release_id, 'conditions': conditions,
                **referenced(conditions, config(body.release_id), body.release_id)}

    @app.get(API + '/conditions/{condition_id}')
    def condition(condition_id: str, release_id: str):
        _ids([condition_id])
        item = store.document(release_id, 'condition', condition_id)
        return {'release_id': release_id, 'condition': item,
                **referenced([item], config(release_id), release_id)}

    @app.get(API + '/knowledge/{module_id}')
    def knowledge(module_id: str, release_id: str):
        _ids([module_id])
        return {'release_id': release_id, 'module': store.document(release_id, 'knowledge', module_id)}

    @app.post(API + '/exports/conditions.csv')
    async def export(request: Request):
        # Native forms stream a download without retaining the whole CSV in JS.
        if request.headers.get('content-type', '').split(';')[0] != 'application/x-www-form-urlencoded':
            raise HTTPException(415, 'Use a URL-encoded export form')
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 2_000_000:
                raise HTTPException(413, 'Export selection is too large')
        try:
            form = parse_qs(body.decode('utf-8'), keep_blank_values=True, max_num_fields=4)
            if set(form) != {'release_id', 'locale', 'scope', 'ids'} or any(len(v) != 1 for v in form.values()):
                raise ValueError()
            release_id, locale, scope = (form[key][0] for key in ('release_id', 'locale', 'scope'))
            requested = json.loads(form['ids'][0])
            if not isinstance(requested, list) or scope not in ('all', 'ids'):
                raise ValueError()
        except (ValueError, UnicodeDecodeError):
            raise HTTPException(422, 'Invalid export selection') from None
        _ids(requested)
        guide = config(release_id)
        if locale not in guide['locales']:
            raise HTTPException(422, 'Unsupported interface language')
        available = store.condition_ids(release_id)
        ids = available if scope == 'all' else _ids(requested)
        if set(ids) - set(available):
            raise HTTPException(404, 'Some conditions are absent from this release')
        sources = store.documents(release_id, 'source')
        medical_locale = guide['locales'][locale]['medical_locale']
        return StreamingResponse(csv_rows(store, release_id, ids, guide['fields'], sources, medical_locale),
            media_type='text/csv; charset=utf-8', headers={
                'Content-Disposition': 'attachment; filename="medical-conditions.csv"',
                'X-Healthcare-Release': release_id})

    @app.get(API + '/healthz')
    def health():
        release_id = store.active_release()
        return {'status': 'ok', 'database': 'ok', **store.release(release_id)}

    return app
