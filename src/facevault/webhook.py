"""Webhook signature verification and event parsing.

The FaceVault API signs webhook payloads with HMAC-SHA256. This module
provides helpers to verify the signature and parse the payload into a
typed WebhookEvent.
"""

from __future__ import annotations

import hashlib
import hmac
import json

from .models import WebhookEvent


def verify_signature(body: str | bytes, signature: str, secret: str) -> bool:
    """Verify HMAC-SHA256 signature of a webhook payload.

    The server computes:
        hmac.new(secret, json.dumps(payload, separators=(",",":"), sort_keys=True), sha256).hexdigest()

    Args:
        body: Raw request body (str or bytes).
        signature: Value of the ``X-Signature`` header.
        secret: Your webhook secret (from API dashboard).

    Returns:
        True if the signature is valid.
    """
    if isinstance(body, str):
        body_bytes = body.encode()
    else:
        body_bytes = body

    # Re-serialize to match the server's canonical form
    try:
        parsed = json.loads(body_bytes)
        canonical = json.dumps(parsed, separators=(",", ":"), sort_keys=True).encode()
    except (json.JSONDecodeError, TypeError):
        return False

    expected = hmac.new(
        secret.encode(),
        canonical,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


def parse_event(body: str | bytes) -> WebhookEvent:
    """Parse a webhook payload into a WebhookEvent.

    Args:
        body: Raw request body (str or bytes).

    Returns:
        Parsed WebhookEvent dataclass.

    Raises:
        ValueError: If the body is not valid JSON.
    """
    if isinstance(body, bytes):
        body = body.decode()

    data = json.loads(body)

    return WebhookEvent(
        event=data.get("event", ""),
        session_id=data.get("session_id", ""),
        status=data.get("status", ""),
        external_user_id=data.get("external_user_id"),
        face_match_passed=data.get("face_match_passed"),
        face_match_score=data.get("face_match_score"),
        anti_spoofing_score=data.get("anti_spoofing_score"),
        anti_spoofing_passed=data.get("anti_spoofing_passed"),
        confirmed_data=data.get("confirmed_data"),
        completed_at=data.get("completed_at"),
        document_check=data.get("document_check"),
    )
