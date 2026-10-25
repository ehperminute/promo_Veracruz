"""OPTIONAL local/hosted submission receiver for the static site.

This is a teaching/pilot backend, not a public production service. Before internet
exposure add CAPTCHA, abuse checks, secure transport, monitoring and retention policies.
No public read or approval endpoints are exposed.
"""
from pathlib import Path
import hashlib
import json
import os
import sqlite3
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from community_trips.tools.publish_reviewed_trip import validate, MAX_PAYLOAD

ROOT = Path(os.environ.get('VX_PRIVATE_SUBMISSION_DIR', './.private_trip_submissions')).resolve()
DB = ROOT / 'pending.sqlite'
MAX_SUBMISSIONS_PER_DAY = 12

app = FastAPI(title='Veracruz trip submission receiver - pilot')
origin = os.environ.get('VX_ALLOWED_ORIGIN', '')
if origin.startswith('https://'):
    app.add_middleware(CORSMiddleware, allow_origins=[origin], allow_credentials=False,
                       allow_methods=['POST'], allow_headers=['Content-Type'])


def initdb():
    ROOT.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(DB) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS submissions(
          submission_id TEXT PRIMARY KEY, received_at INTEGER NOT NULL,
          status TEXT NOT NULL CHECK(status IN ('pending','approved','rejected')),
          document_json TEXT NOT NULL
        )''')
        con.execute('CREATE INDEX IF NOT EXISTS idx_status_received ON submissions(status,received_at)')
        con.execute('''CREATE TABLE IF NOT EXISTS rate_log(
          ip_hash TEXT NOT NULL, created_at INTEGER NOT NULL
        )''')


@app.post('/api/trip-submissions', status_code=202)
async def receive(request: Request):
    length = request.headers.get('content-length')
    if length and (not length.isdigit() or int(length)>MAX_PAYLOAD):
        raise HTTPException(413,'Submission too large')
    raw = await request.body()
    if len(raw)>MAX_PAYLOAD:
        raise HTTPException(413,'Submission too large')
    try:
        obj = json.loads(raw)
        validate(obj)
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        raise HTTPException(422, 'Invalid submission') from exc
    # Minimal pilot throttling. Behind a proxy, do not trust X-Forwarded-For.
    ip = request.client.host if request.client else 'unknown'
    ip_hash=hashlib.sha256((os.getenv('VX_IP_HASH_SALT','local-pilot-only')+ip).encode()).hexdigest()
    submission_id = hashlib.sha256(raw).hexdigest()[:24]
    now=int(time.time())
    initdb()
    with sqlite3.connect(DB) as con:
        con.execute('DELETE FROM rate_log WHERE created_at<?',(now-24*3600,))
        n=con.execute('SELECT COUNT(*) FROM rate_log WHERE ip_hash=?',(ip_hash,)).fetchone()[0]
        if n>=MAX_SUBMISSIONS_PER_DAY:
            raise HTTPException(429, 'Too many submissions')
        existing=con.execute('SELECT submission_id FROM submissions WHERE submission_id=?',(submission_id,)).fetchone()
        if not existing:
            con.execute('INSERT INTO submissions VALUES (?, ?, ?, ?)',(submission_id,now,'pending',json.dumps(obj,ensure_ascii=False)))
            con.execute('INSERT INTO rate_log VALUES(?,?)',(ip_hash,now))
    return {'status':'pending_review','submission_id':submission_id}
