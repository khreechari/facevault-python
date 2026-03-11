"""Tests for FaceVault SDK data models."""

from facevault.models import Session, SessionStatus, WebhookEvent


def test_session_creation():
    session = Session(
        session_id="sess_1",
        session_token="tok_1",
        steps=["liveness", "document"],
        webapp_url="https://app.facevault.id/?sid=sess_1&st=tok_1",
    )
    assert session.session_id == "sess_1"
    assert session.session_token == "tok_1"
    assert session.steps == ["liveness", "document"]
    assert "sid=sess_1" in session.webapp_url


def test_session_repr_redacts_token():
    """Session.__repr__ must never leak the session_token or full webapp_url."""
    session = Session(
        session_id="sess_1",
        session_token="tok_secret_abc",
        steps=["liveness"],
        webapp_url="https://app.facevault.id/?sid=sess_1&st=tok_secret_abc",
    )
    r = repr(session)
    assert "tok_secret_abc" not in r
    assert "***" in r
    assert "sess_1" in r


def test_session_challenge_nonce_default():
    session = Session(
        session_id="sess_1",
        session_token="tok_1",
        steps=["liveness"],
        webapp_url="https://app.facevault.id/?sid=sess_1&st=tok_1",
    )
    assert session.challenge_nonce is None


def test_session_challenge_nonce_set():
    session = Session(
        session_id="sess_1",
        session_token="tok_1",
        steps=["liveness"],
        webapp_url="https://app.facevault.id/?sid=sess_1&st=tok_1",
        challenge_nonce="nonce_abc123",
    )
    assert session.challenge_nonce == "nonce_abc123"


def test_session_status_defaults():
    status = SessionStatus(
        session_id="sess_1",
        status="pending",
        steps={},
    )
    assert status.face_match_passed is None
    assert status.error == ""
    assert status.created_at is None
    assert status.completed_at is None
    assert status.trust_score is None
    assert status.trust_decision is None
    assert status.require_poa is False
    assert status.poa is None
    assert status.anti_spoofing is None
    assert status.credential is None


def test_session_status_full():
    status = SessionStatus(
        session_id="sess_1",
        status="completed",
        steps={"liveness": True, "document": True},
        face_match_passed=True,
        error="",
        created_at="2026-01-01T00:00:00Z",
        completed_at="2026-01-01T00:05:00Z",
        trust_score=85.5,
        trust_decision="accept",
        require_poa=True,
        poa={"status": "verified"},
        anti_spoofing={"score": 0.92, "passed": True},
        credential={"credential_id": "cred_1", "status": "active"},
    )
    assert status.status == "completed"
    assert status.face_match_passed is True
    assert status.steps["liveness"] is True
    assert status.trust_score == 85.5
    assert status.trust_decision == "accept"
    assert status.require_poa is True
    assert status.poa == {"status": "verified"}
    assert status.anti_spoofing == {"score": 0.92, "passed": True}
    assert status.credential == {"credential_id": "cred_1", "status": "active"}


def test_webhook_event_defaults():
    event = WebhookEvent(
        event="session.completed",
        session_id="sess_1",
        status="completed",
    )
    assert event.external_user_id is None
    assert event.face_match_passed is None
    assert event.face_match_score is None
    assert event.anti_spoofing_score is None
    assert event.anti_spoofing_passed is None
    assert event.confirmed_data is None
    assert event.completed_at is None
    assert event.document_check is None
    assert event.trust_score is None
    assert event.trust_decision is None
    assert event.sanctions_hit is None
    assert event.poa is None


def test_webhook_event_full():
    event = WebhookEvent(
        event="session.completed",
        session_id="sess_1",
        status="completed",
        external_user_id="user-42",
        face_match_passed=True,
        face_match_score=0.95,
        anti_spoofing_score=0.88,
        anti_spoofing_passed=True,
        confirmed_data={"full_name": "Jane Doe", "dob": "1990-01-01"},
        completed_at="2026-01-01T00:00:00Z",
        document_check={"mrz_valid": True},
        trust_score=82.3,
        trust_decision="accept",
        sanctions_hit=False,
        poa={"status": "pending"},
    )
    assert event.face_match_score == 0.95
    assert event.confirmed_data["full_name"] == "Jane Doe"
    assert event.trust_score == 82.3
    assert event.trust_decision == "accept"
    assert event.sanctions_hit is False
    assert event.poa == {"status": "pending"}
