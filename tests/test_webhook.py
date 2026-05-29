"""Tests for webhook signature verification and event parsing."""

from __future__ import annotations  # PEP 563 — makes `str | bytes` annotations parse on Python 3.9

import hashlib
import hmac
import json

import pytest

from facevault import verify_signature, parse_event


def _sign(body: str | bytes, secret: str) -> str:
    """Sign the raw body bytes exactly as the server does."""
    body_bytes = body.encode() if isinstance(body, str) else body
    return hmac.new(secret.encode(), body_bytes, hashlib.sha256).hexdigest()


def test_verify_valid_signature():
    secret = "whsec_test123"
    body = '{"event":"session.completed","session_id":"sess_1","status":"completed"}'
    assert verify_signature(body, _sign(body, secret), secret) is True


def test_verify_valid_signature_bytes():
    secret = "whsec_test123"
    body = b'{"event":"session.completed","session_id":"sess_1"}'
    assert verify_signature(body, _sign(body, secret), secret) is True


def test_verify_invalid_signature():
    body = '{"event":"session.completed","session_id":"sess_1"}'
    assert verify_signature(body, "invalid_sig", "whsec_test123") is False


def test_verify_wrong_secret():
    body = '{"event":"session.completed","session_id":"sess_1"}'
    assert verify_signature(body, _sign(body, "correct_secret"), "wrong_secret") is False


def test_verify_tampered_body():
    """A single extra byte must invalidate the signature (raw-byte verification)."""
    secret = "whsec_test123"
    body = '{"event":"session.completed","status":"passed"}'
    sig = _sign(body, secret)
    assert verify_signature(body + " ", sig, secret) is False


def test_verify_non_ascii_raw_body():
    """Server signs raw bytes with ensure_ascii=True; verify must HMAC them as-is."""
    secret = "whsec_test123"
    # Exactly what the server sends: non-ASCII \uXXXX-escaped, float keeps .0
    body = '{"confirmed_data":{"name":"Jos\\u00e9 M\\u00fcller"},"event":"verification.completed","status":"passed","trust_score":1.0}'
    assert verify_signature(body, _sign(body, secret), secret) is True


def test_parse_event_minimal():
    body = json.dumps({"event": "session.completed", "session_id": "sess_1", "status": "completed"})
    event = parse_event(body)

    assert event.event == "session.completed"
    assert event.session_id == "sess_1"
    assert event.status == "completed"
    assert event.external_user_id is None
    assert event.face_match_passed is None


def test_parse_event_full():
    body = json.dumps({
        "event": "session.completed",
        "session_id": "sess_1",
        "status": "completed",
        "external_user_id": "user-42",
        "face_match_passed": True,
        "face_match_score": 0.95,
        "anti_spoofing_score": 0.88,
        "anti_spoofing_passed": True,
        "confirmed_data": {"full_name": "John Doe"},
        "completed_at": "2026-01-01T00:00:00Z",
        "document_check": {"mrz_valid": True},
        "trust_score": 85.0,
        "trust_decision": "accept",
        "sanctions_hit": False,
        "poa": {"status": "verified"},
    })
    event = parse_event(body)

    assert event.external_user_id == "user-42"
    assert event.face_match_passed is True
    assert event.face_match_score == 0.95
    assert event.anti_spoofing_score == 0.88
    assert event.anti_spoofing_passed is True
    assert event.confirmed_data == {"full_name": "John Doe"}
    assert event.completed_at == "2026-01-01T00:00:00Z"
    assert event.document_check == {"mrz_valid": True}
    assert event.trust_score == 85.0
    assert event.trust_decision == "accept"
    assert event.sanctions_hit is False
    assert event.poa == {"status": "verified"}


def test_parse_event_bytes():
    body = b'{"event": "session.failed", "session_id": "sess_2", "status": "failed"}'
    event = parse_event(body)
    assert event.event == "session.failed"


def test_parse_event_invalid_json():
    with pytest.raises(ValueError):
        parse_event("not json")
