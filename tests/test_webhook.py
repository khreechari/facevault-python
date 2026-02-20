"""Tests for webhook signature verification and event parsing."""

import hashlib
import hmac
import json

import pytest

from facevault import WebhookEvent, parse_event, verify_signature


SAMPLE_PAYLOAD = {
    "event": "verification.completed",
    "session_id": "abc123",
    "status": "passed",
    "external_user_id": "user_42",
    "face_match_passed": True,
    "face_match_score": 0.012,
    "anti_spoofing_score": 0.82,
    "anti_spoofing_passed": True,
    "confirmed_data": {"full_name": "John Smith", "date_of_birth": "15/03/1990"},
    "completed_at": "2026-02-20T10:01:00Z",
    "document_check": {"name_match": True, "dob_match": True},
}

SECRET = "whsec_test_secret_123"


def _compute_signature(payload: dict, secret: str) -> str:
    """Compute HMAC-SHA256 matching the server implementation."""
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return hmac.new(secret.encode(), canonical, hashlib.sha256).hexdigest()


class TestVerifySignature:
    def test_valid_signature(self):
        body = json.dumps(SAMPLE_PAYLOAD)
        sig = _compute_signature(SAMPLE_PAYLOAD, SECRET)

        assert verify_signature(body, sig, SECRET) is True

    def test_valid_signature_bytes(self):
        body = json.dumps(SAMPLE_PAYLOAD).encode()
        sig = _compute_signature(SAMPLE_PAYLOAD, SECRET)

        assert verify_signature(body, sig, SECRET) is True

    def test_invalid_signature(self):
        body = json.dumps(SAMPLE_PAYLOAD)
        assert verify_signature(body, "bad_signature", SECRET) is False

    def test_wrong_secret(self):
        body = json.dumps(SAMPLE_PAYLOAD)
        sig = _compute_signature(SAMPLE_PAYLOAD, SECRET)

        assert verify_signature(body, sig, "wrong_secret") is False

    def test_invalid_json_body(self):
        assert verify_signature("not json", "any_sig", SECRET) is False

    def test_whitespace_insensitive(self):
        """Body with extra whitespace should still verify (re-serialized)."""
        body_pretty = json.dumps(SAMPLE_PAYLOAD, indent=2)
        sig = _compute_signature(SAMPLE_PAYLOAD, SECRET)

        assert verify_signature(body_pretty, sig, SECRET) is True


class TestParseEvent:
    def test_parse_full_payload(self):
        body = json.dumps(SAMPLE_PAYLOAD)
        event = parse_event(body)

        assert isinstance(event, WebhookEvent)
        assert event.event == "verification.completed"
        assert event.session_id == "abc123"
        assert event.status == "passed"
        assert event.external_user_id == "user_42"
        assert event.face_match_passed is True
        assert event.face_match_score == 0.012
        assert event.anti_spoofing_score == 0.82
        assert event.anti_spoofing_passed is True
        assert event.confirmed_data == {"full_name": "John Smith", "date_of_birth": "15/03/1990"}
        assert event.completed_at == "2026-02-20T10:01:00Z"
        assert event.document_check == {"name_match": True, "dob_match": True}

    def test_parse_bytes(self):
        body = json.dumps(SAMPLE_PAYLOAD).encode()
        event = parse_event(body)
        assert event.session_id == "abc123"

    def test_parse_minimal_payload(self):
        body = json.dumps({"event": "verification.completed", "session_id": "min", "status": "failed"})
        event = parse_event(body)

        assert event.session_id == "min"
        assert event.status == "failed"
        assert event.face_match_passed is None
        assert event.confirmed_data is None

    def test_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            parse_event("not json")
