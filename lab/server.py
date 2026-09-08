"""Local synthetic services: atomic storage, ticket mock, model fixtures, alert outbox.

n8n owns validation, safety rules, model prompts/output validation, and routing.
This small HTTP service owns durable state and test doubles. No third-party packages.
Do not expose this development server to the public internet.
"""
import hashlib
import hmac
import json
import os
import re
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DB = Path(os.environ.get("LAB_DB", ".local/lab.sqlite"))
KEY = os.environ.get("LAB_API_KEY", "")
FAULTS = {"model": "normal", "ticket": "normal", "finish": "normal"}
COUNTERS = {"model_calls": 0, "ticket_calls": 0}
LOCK = threading.Lock()


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def connect():
    db = sqlite3.connect(DB, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=10000")
    return db


def initialize():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.executescript("""
        CREATE TABLE IF NOT EXISTS events (
          event_id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, trace_id TEXT NOT NULL,
          status TEXT NOT NULL, context_json TEXT NOT NULL, classification_json TEXT,
          result_json TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS tickets (
          event_id TEXT PRIMARY KEY REFERENCES events(event_id), ticket_id TEXT UNIQUE NOT NULL,
          payload_json TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS reviews (
          event_id TEXT PRIMARY KEY REFERENCES events(event_id), reason TEXT NOT NULL,
          context_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending');
        CREATE TABLE IF NOT EXISTS dead_letters (
          recovery_id TEXT PRIMARY KEY, event_id TEXT, trace_id TEXT NOT NULL,
          stage TEXT NOT NULL, error_code TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open');
        CREATE TABLE IF NOT EXISTS audit (
          id INTEGER PRIMARY KEY, trace_id TEXT NOT NULL, event_id TEXT,
          outcome TEXT NOT NULL, reason TEXT NOT NULL, model_mode TEXT,
          latency_ms INTEGER NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS alerts (
          alert_key TEXT PRIMARY KEY, event_id TEXT, trace_id TEXT NOT NULL,
          reason TEXT NOT NULL, delivery TEXT NOT NULL DEFAULT 'mock_outbox', created_at TEXT NOT NULL);
        """)


class BadRequest(Exception):
    def __init__(self, code=400, reason="INVALID_SERVICE_REQUEST"):
        self.code, self.reason = code, reason


def require_owner(db, data):
    row = db.execute("SELECT * FROM events WHERE event_id=?", (data.get("event_id"),)).fetchone()
    if not row or row["trace_id"] != data.get("trace_id"):
        raise BadRequest(409, "EVENT_OWNERSHIP_MISMATCH")
    return row


def write_audit(db, data, outcome, reason):
    db.execute("INSERT INTO audit(trace_id,event_id,outcome,reason,model_mode,latency_ms,created_at) VALUES(?,?,?,?,?,?,?)",
               (str(data.get("trace_id", "unknown"))[:100], data.get("event_id"), outcome[:50], reason[:80],
                data.get("model_mode", "none"), max(0, int(data.get("latency_ms", 0))), now()))


def alert(db, event_id, trace_id, reason):
    db.execute("INSERT OR IGNORE INTO alerts VALUES(?,?,?,?,?,?)",
               (f"{event_id or trace_id}:{reason}", event_id, trace_id, reason, "mock_outbox", now()))


def claim(data):
    required = {"event_id", "fingerprint", "trace_id", "context"}
    if set(data) != required or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", str(data["event_id"])):
        raise BadRequest()
    if not re.fullmatch(r"[a-f0-9]{64}", str(data["fingerprint"])):
        raise BadRequest()
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT * FROM events WHERE event_id=?", (data["event_id"],)).fetchone()
        if row:
            if row["fingerprint"] != data["fingerprint"]:
                return {"acquired": False, "reason": "ID_CONTENT_CONFLICT", "http_status": 409}
            if row["status"] == "processing":
                if row["trace_id"] == data["trace_id"]:
                    return {"acquired": True, "reason": "CLAIM_RETRY"}
                return {"acquired": False, "reason": "IN_PROGRESS", "http_status": 202,
                        "result": {"status": "in_progress", "source_event_id": data["event_id"], "trace_id": row["trace_id"]}}
            return {"acquired": False, "reason": "DUPLICATE", "http_status": 200,
                    "result": json.loads(row["result_json"])}
        db.execute("INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?)",
                   (data["event_id"], data["fingerprint"], data["trace_id"], "processing",
                    canonical(data["context"]), None, None, now(), now()))
        return {"acquired": True, "reason": "NEW_EVENT"}


def checkpoint(data):
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = require_owner(db, data)
        if row["status"] != "processing":
            raise BadRequest(409, "EVENT_ALREADY_FINALIZED")
        db.execute("UPDATE events SET classification_json=?,updated_at=? WHERE event_id=?",
                   (canonical(data["classification"]), now(), data["event_id"]))
    return {"stored": True}


def finish(data):
    with LOCK:
        if FAULTS["finish"] == "unavailable":
            raise BadRequest(503, "FIXTURE_STORAGE_FAILURE")
    outcome = data.get("outcome")
    if outcome not in ("ticket_created", "human_review", "manual_recovery"):
        raise BadRequest()
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = require_owner(db, data)
        if row["result_json"]:
            return json.loads(row["result_json"])
        ticket = db.execute("SELECT ticket_id FROM tickets WHERE event_id=?", (data["event_id"],)).fetchone()
        if outcome == "ticket_created" and (not ticket or ticket["ticket_id"] != data.get("ticket_id")):
            raise BadRequest(409, "TICKET_NOT_CONFIRMED")
        response = {"status": outcome, "source_event_id": data["event_id"], "trace_id": data["trace_id"],
                    "reason": data["reason"], "synthetic": True, "model_mode": data.get("model_mode", "none")}
        if ticket:
            response["ticket_id"] = ticket["ticket_id"]
        if outcome == "ticket_created":
            response["message"] = "Mock maintenance ticket created. No real repair or dispatch was requested."
        else:
            response["message"] = "Request recorded in the local human-review queue. No real person has been notified."
            db.execute("INSERT OR IGNORE INTO reviews(event_id,reason,context_json) VALUES(?,?,?)",
                       (data["event_id"], data["reason"], row["context_json"]))
            alert(db, data["event_id"], data["trace_id"], data["reason"])
        if outcome == "manual_recovery":
            db.execute("INSERT OR IGNORE INTO dead_letters(recovery_id,event_id,trace_id,stage,error_code) VALUES(?,?,?,?,?)",
                       (data["event_id"], data["event_id"], data["trace_id"], data.get("stage", "unknown"), data["reason"]))
        db.execute("UPDATE events SET status=?,result_json=?,updated_at=? WHERE event_id=?",
                   (outcome, canonical(response), now(), data["event_id"]))
        write_audit(db, data, outcome, data["reason"])
        return response


def ticket_create(data):
    with LOCK:
        COUNTERS["ticket_calls"] += 1
        fault = FAULTS["ticket"]
        if fault == "unavailable":
            raise BadRequest(503, "FIXTURE_TICKET_FAILURE")
    required = {"event_id", "trace_id", "classification"}
    if set(data) != required:
        raise BadRequest()
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = require_owner(db, data)
        if not row["classification_json"] or canonical(data["classification"]) != row["classification_json"]:
            raise BadRequest(409, "UNAPPROVED_TICKET_PAYLOAD")
        old = db.execute("SELECT * FROM tickets WHERE event_id=?", (data["event_id"],)).fetchone()
        if old:
            if old["payload_json"] != canonical(data):
                raise BadRequest(409, "TICKET_CONTENT_CONFLICT")
            return {"ticket_id": old["ticket_id"], "synthetic": True, "duplicate": True}
        if row["status"] != "processing":
            raise BadRequest(409, "EVENT_NOT_PROCESSING")
        ticket_id = "MOCK-" + uuid.uuid4().hex[:12].upper()
        db.execute("INSERT INTO tickets VALUES(?,?,?,?)", (data["event_id"], ticket_id, canonical(data), now()))
    if fault == "after_commit":
        raise BadRequest(503, "FIXTURE_RESPONSE_LOSS_AFTER_COMMIT")
    return {"ticket_id": ticket_id, "synthetic": True, "duplicate": False}


def model_fixture(data):
    with LOCK:
        COUNTERS["model_calls"] += 1
        fault = FAULTS["model"]
        if fault == "once_429":
            FAULTS["model"] = "normal"
    if fault in ("unavailable", "once_429"):
        raise BadRequest(429 if fault == "once_429" else 503, "FIXTURE_MODEL_FAILURE")
    if fault == "timeout":
        time.sleep(12)
    text = data.get("messages", [{}])[0].get("content", "").lower()
    if "model_invalid" in text:
        content = '{"category":"plumbing","confidence":"high"}'
    else:
        category = "plumbing" if any(w in text for w in ("sink", "leak", "toilet")) else "general"
        ambiguous = "something is wrong" in text
        obj = {"category": "unknown" if ambiguous else category, "urgency": "routine",
               "confidence": 0.4 if ambiguous else 0.94,
               "summary": "Insufficient information to classify." if ambiguous else "Maintenance service requested.",
               "human_review_required": ambiguous,
               "policy_flags": ["insufficient_information"] if ambiguous else []}
        if "model_emergency" in text:
            obj["urgency"] = "emergency"
        content = canonical(obj)
    return {"id": "fixture-message", "type": "message", "role": "assistant", "model": "fixture-no-live-ai",
            "stop_reason": "end_turn", "content": [{"type": "text", "text": content}],
            "usage": {"input_tokens": 0, "output_tokens": 0}, "fixture": True}


def record_error(data):
    trace = str(data.get("trace_id", "unknown"))[:100]
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT * FROM events WHERE trace_id=?", (trace,)).fetchone()
        event_id = row["event_id"] if row else None
        db.execute("INSERT OR IGNORE INTO dead_letters(recovery_id,event_id,trace_id,stage,error_code) VALUES(?,?,?,?,?)",
                   ("error-" + trace, event_id, trace, "unexpected_workflow_error", "WORKFLOW_FAILED"))
        alert(db, event_id, trace, "WORKFLOW_FAILED")
        if row and row["status"] == "processing":
            response = {"status": "manual_recovery", "source_event_id": event_id, "trace_id": trace,
                        "reason": "WORKFLOW_FAILED", "synthetic": True,
                        "message": "Local recovery required; no automatic restart."}
            db.execute("UPDATE events SET status='manual_recovery',result_json=?,updated_at=? WHERE event_id=?",
                       (canonical(response), now(), event_id))
            db.execute("INSERT OR IGNORE INTO reviews(event_id,reason,context_json) VALUES(?,?,?)",
                       (event_id, "WORKFLOW_FAILED", row["context_json"]))
        return {"recorded": True, "delivery": "mock_outbox"}


def snapshot():
    with connect() as db:
        tables = {t: [dict(row) for row in db.execute(f"SELECT * FROM {t}")]
                  for t in ("events", "tickets", "reviews", "dead_letters", "audit", "alerts")}
    with LOCK:
        return {"tables": tables, "counters": dict(COUNTERS), "faults": dict(FAULTS)}


class Handler(BaseHTTPRequestHandler):
    server_version = "SyntheticLab/1"

    def log_message(self, *_):
        pass  # Deliberately do not log bodies, query strings, headers, or raw errors.

    def send_json(self, status, payload):
        body = canonical(payload).encode()
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def authorized(self):
        return hmac.compare_digest(self.headers.get("X-Lab-Key", ""), KEY)

    def do_GET(self):
        if self.path == "/health":
            return self.send_json(200, {"status": "ok", "synthetic": True})
        if not self.authorized():
            return self.send_json(401, {"error": "UNAUTHORIZED"})
        if self.path == "/admin/snapshot":
            return self.send_json(200, snapshot())
        return self.send_json(404, {"error": "NOT_FOUND"})

    def do_POST(self):
        if not self.authorized():
            return self.send_json(401, {"error": "UNAUTHORIZED"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 65536:
                raise BadRequest(413, "BODY_SIZE_LIMIT")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise BadRequest()
            routes = {"/events/claim": claim, "/events/checkpoint": checkpoint, "/events/finish": finish,
                      "/tickets": ticket_create, "/model/messages": model_fixture, "/errors": record_error}
            if self.path in routes:
                return self.send_json(200, routes[self.path](data))
            if self.path == "/audit":
                if data.get("reason") not in ("INVALID_INPUT", "ID_CONTENT_CONFLICT", "IN_PROGRESS", "DUPLICATE"):
                    raise BadRequest()
                with connect() as db:
                    write_audit(db, data, "intake_control", data["reason"])
                return self.send_json(200, {"recorded": True})
            if self.path == "/admin/faults":
                allowed = {"model": {"normal", "unavailable", "once_429", "timeout"},
                           "ticket": {"normal", "unavailable", "after_commit"},
                           "finish": {"normal", "unavailable"}}
                if not data or any(k not in allowed or v not in allowed[k] for k, v in data.items()):
                    raise BadRequest()
                with LOCK:
                    FAULTS.update(data)
                return self.send_json(200, {"configured": True})
            if self.path == "/admin/recover-ticket":
                # Only reconcile an existing ticket; do not repeat classification or dispatch.
                with connect() as db:
                    db.execute("BEGIN IMMEDIATE")
                    event = db.execute("SELECT * FROM events WHERE event_id=?", (data.get("event_id"),)).fetchone()
                    ticket = db.execute("SELECT ticket_id FROM tickets WHERE event_id=?", (data.get("event_id"),)).fetchone()
                    if not event or not ticket or event["status"] != "manual_recovery":
                        raise BadRequest(409, "NO_COMMITTED_TICKET_TO_RECONCILE")
                    result = {"status": "ticket_created", "source_event_id": event["event_id"],
                              "trace_id": event["trace_id"], "ticket_id": ticket["ticket_id"],
                              "synthetic": True, "reason": "OPERATOR_RECONCILED", "message": "Existing mock ticket reconciled."}
                    db.execute("UPDATE events SET status='ticket_created',result_json=?,updated_at=? WHERE event_id=?",
                               (canonical(result), now(), event["event_id"]))
                    db.execute("UPDATE dead_letters SET status='resolved' WHERE event_id=?", (event["event_id"],))
                    db.execute("UPDATE reviews SET status='resolved' WHERE event_id=?", (event["event_id"],))
                    write_audit(db, {"trace_id": event["trace_id"], "event_id": event["event_id"]}, "ticket_created", "OPERATOR_RECONCILED")
                return self.send_json(200, result)
            raise BadRequest(404, "NOT_FOUND")
        except BadRequest as exc:
            self.send_json(exc.code, {"error": exc.reason})
        except (ValueError, KeyError, TypeError):
            self.send_json(400, {"error": "INVALID_SERVICE_REQUEST"})
        except sqlite3.Error:
            self.send_json(503, {"error": "STORAGE_UNAVAILABLE"})


if __name__ == "__main__":
    if len(KEY) < 24 or KEY == "GENERATE_LOCALLY":
        raise SystemExit("Set LAB_API_KEY to a locally generated secret of at least 24 characters.")
    initialize()
    print("Synthetic lab services ready. No live ticketing or notifications.", flush=True)
    ThreadingHTTPServer((os.environ.get("LAB_HOST", "127.0.0.1"), int(os.environ.get("LAB_PORT", "8080"))), Handler).serve_forever()
