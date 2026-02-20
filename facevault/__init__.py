"""FaceVault Python SDK — privacy-first KYC & identity verification."""

from ._async_client import AsyncFaceVaultClient
from ._client import FaceVaultClient
from .exceptions import AuthError, FaceVaultError, NotFoundError, RateLimitError
from .models import Session, SessionStatus, WebhookEvent
from .webhook import parse_event, verify_signature

__all__ = [
    "AsyncFaceVaultClient",
    "AuthError",
    "FaceVaultClient",
    "FaceVaultError",
    "NotFoundError",
    "RateLimitError",
    "Session",
    "SessionStatus",
    "WebhookEvent",
    "parse_event",
    "verify_signature",
]
