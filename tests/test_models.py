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


def test_session_status_full():
    status = SessionStatus(
        session_id="sess_1",
        status="completed",
        steps={"liveness": True, "document": True},
        face_match_passed=True,
        error="",
        created_at="2026-01-01T00:00:00Z",
        completed_at="2026-01-01T00:05:00Z",
    )
    assert status.status == "completed"
    assert status.face_match_passed is True
    assert status.steps["liveness"] is True


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
    )
    assert event.face_match_score == 0.95
    assert event.confirmed_data["full_name"] == "Jane Doe"
