"""Shared local lab client. Never prints authentication headers."""
import json
from datetime import datetime, timezone
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def key():
    for line in (ROOT/'.env').read_text().splitlines():
        if line.startswith('LAB_API_KEY='):
            return line.split('=',1)[1]
    raise RuntimeError('Run scripts/configure.py first.')


def call(path, data=None, *, port=8080, authorized=True, raw=False, timeout=100):
    headers = {'Content-Type':'application/json'}
    if authorized:
        headers['X-Lab-Key']=key()
    payload = data if raw else json.dumps(data).encode() if data is not None else None
    req=urllib.request.Request(f'http://127.0.0.1:{port}{path}',data=payload,headers=headers)
    try:
        response=urllib.request.urlopen(req,timeout=timeout)
    except urllib.error.HTTPError as exc:
        response=exc
    body=response.read().decode()
    try:body=json.loads(body)
    except ValueError:body={'unparsed_response':body[:300]}
    return response.status,body


def request(event_id, message='Water leaking beneath the kitchen sink.'):
    return {'source_event_id':event_id,'property_id':'PROP-DEMO-001','unit':'2B','message':message,
            'contact_preference':'none','submitted_at':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'synthetic':True}

