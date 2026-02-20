"""FaceVault SDK data models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Session:
    """Returned by create_session(). Contains the session ID and webapp URL."""

    session_id: str
    session_token: str
    steps: list[str]
    webapp_url: str


@dataclass
class SessionStatus:
    """Returned by get_session(). Full session status."""

    session_id: str
    status: str
    steps: dict[str, bool]
    face_match_passed: bool | None = None
    error: str = ""
    created_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class WebhookEvent:
    """Parsed webhook payload."""

    event: str
    session_id: str
    status: str
    external_user_id: str | None = None
    face_match_passed: bool | None = None
    face_match_score: float | None = None
    anti_spoofing_score: float | None = None
    anti_spoofing_passed: bool | None = None
    confirmed_data: dict | None = None
    completed_at: str | None = None
    document_check: dict | None = None
