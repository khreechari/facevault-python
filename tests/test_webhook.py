"""Tests for webhook signature verification and event parsing."""

import hashlib
import hmac
import json

import pytest

from facevault import verify_signature, parse_event


def _make_signature(payload: dict, secret: str) -> str:
    """Generate a valid HMAC-SHA256 signature for a payload."""
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return hmac.new(secret.encode(), canonical, hashlib.sha256).hexdigest()


def test_verify_valid_signature():
    payload = {"event": "session.completed", "session_id": "sess_1", "status": "completed"}
    secret = "whsec_test123"
    sig = _make_signature(payload, secret)
    body = json.dumps(payload)

    assert verify_signature(body, sig, secret) is True


def test_verify_valid_signature_bytes():
    payload = {"event": "session.completed", "session_id": "sess_1"}
    secret = "whsec_test123"
    sig = _make_signature(payload, secret)
    body = json.dumps(payload).encode()

    assert verify_signature(body, sig, secret) is True


def test_verify_invalid_signature():
    payload = {"event": "session.completed", "session_id": "sess_1"}
    secret = "whsec_test123"
    body = json.dumps(payload)

    assert verify_signature(body, "invalid_sig", secret) is False


def test_verify_wrong_secret():
    payload = {"event": "session.completed", "session_id": "sess_1"}
    sig = _make_signature(payload, "correct_secret")
    body = json.dumps(payload)

    assert verify_signature(body, sig, "wrong_secret") is False


def test_verify_invalid_json():
    assert verify_signature("not json", "some_sig", "secret") is False


def test_verify_reordered_keys():
    """Signature should match regardless of key order in body."""
    payload = {"session_id": "sess_1", "event": "session.completed", "status": "completed"}
    secret = "whsec_test123"
    sig = _make_signature(payload, secret)

    # Send body with different key ordering
    reordered = json.dumps({"status": "completed", "event": "session.completed", "session_id": "sess_1"})

    assert verify_signature(reordered, sig, secret) is True


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


def test_parse_event_bytes():
    body = b'{"event": "session.failed", "session_id": "sess_2", "status": "failed"}'
    event = parse_event(body)
    assert event.event == "session.failed"


def test_parse_event_invalid_json():
    with pytest.raises(ValueError):
        parse_event("not json")
