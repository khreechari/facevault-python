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
    """Verify the HMAC-SHA256 signature of a webhook.

    The server signs the exact bytes it sends, so verification HMACs the **raw
    request body** as received — do not parse and re-serialize it first.
    Re-serializing can change the bytes (e.g. non-ASCII escaping or number
    formatting) and would reject valid webhooks.

        sig = hmac.new(secret, raw_body, sha256).hexdigest()  # matches X-FaceVault-Signature

    Args:
        body: Raw request body, exactly as received (str or bytes).
        signature: Value of the ``X-FaceVault-Signature`` header.
        secret: Your webhook secret (from the API dashboard).

    Returns:
        True if the signature is valid.
    """
    if not isinstance(signature, str) or not signature:
        return False

    body_bytes = body.encode() if isinstance(body, str) else body
    expected = hmac.new(secret.encode(), body_bytes, hashlib.sha256).hexdigest()
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
        trust_score=data.get("trust_score"),
        trust_decision=data.get("trust_decision"),
        sanctions_hit=data.get("sanctions_hit"),
        poa=data.get("poa"),
    )
