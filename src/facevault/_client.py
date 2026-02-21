"""Synchronous FaceVault API client."""

from __future__ import annotations

import httpx

from .exceptions import AuthError, FaceVaultError, NotFoundError, RateLimitError
from .models import Session, SessionStatus


_DEFAULT_BASE_URL = "https://api.facevault.id"
_DEFAULT_WEBAPP_BASE = "https://app.facevault.id"


def _validate_url(url: str, label: str) -> str:
    """Validate a URL uses HTTPS. Returns the cleaned URL."""
    url = url.rstrip("/")
    if not url.startswith("https://"):
        raise ValueError(
            f"{label} must use HTTPS (got {url!r}). "
            "This prevents API keys and session tokens from leaking over plaintext."
        )
    return url


def _validate_api_key(api_key: str) -> None:
    """Validate the API key is non-empty."""
    if not api_key or not api_key.strip():
        raise ValueError("api_key must be a non-empty string")


class FaceVaultClient:
    """Synchronous client for the FaceVault verification API.

    Args:
        api_key: Your FaceVault API key (``fv_live_...`` or ``fv_test_...``).
        base_url: API base URL. Defaults to ``https://api.facevault.id``.
            Must use HTTPS.
        webapp_base: Webapp base URL for constructing ``webapp_url``.
            Defaults to ``https://app.facevault.id``. Must use HTTPS.
        timeout: Request timeout in seconds. Defaults to 15.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        webapp_base: str = _DEFAULT_WEBAPP_BASE,
        timeout: float = 15,
    ):
        _validate_api_key(api_key)
        self._api_key = api_key
        self._base_url = _validate_url(base_url, "base_url")
        self._webapp_base = _validate_url(webapp_base, "webapp_base")
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={"X-FaceVault-Api-Key": api_key},
            timeout=timeout,
        )

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.is_success:
            return

        # Try to extract detail message from API error response
        detail = ""
        try:
            data = response.json()
            detail = data.get("detail", "") or data.get("error", "")
        except Exception:
            pass

        msg = detail or f"API error ({response.status_code})"

        if response.status_code == 401:
            raise AuthError(msg)
        elif response.status_code == 404:
            raise NotFoundError(msg)
        elif response.status_code == 429:
            raise RateLimitError(msg)
        else:
            raise FaceVaultError(msg, status_code=response.status_code)

    def create_session(self, external_user_id: str) -> Session:
        """Create a new verification session.

        Args:
            external_user_id: Your user identifier (e.g. Telegram chat ID).

        Returns:
            Session with ``session_id``, ``session_token``, and ``webapp_url``.
        """
        response = self._client.post(
            "/api/v1/sessions",
            params={"external_user_id": external_user_id},
        )
        self._raise_for_status(response)
        data = response.json()

        session_id = data["session_id"]
        session_token = data.get("session_token", "")

        return Session(
            session_id=session_id,
            session_token=session_token,
            steps=data.get("steps", []),
            webapp_url=f"{self._webapp_base}/?sid={session_id}&st={session_token}",
        )

    def get_session(self, session_id: str) -> SessionStatus:
        """Get the status of a verification session.

        Args:
            session_id: The session ID returned by ``create_session()``.

        Returns:
            SessionStatus with current state and results.
        """
        response = self._client.get(f"/api/v1/sessions/{session_id}")
        self._raise_for_status(response)
        data = response.json()

        return SessionStatus(
            session_id=data["session_id"],
            status=data["status"],
            steps=data.get("steps", {}),
            face_match_passed=data.get("face_match_passed"),
            error=data.get("error", ""),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> FaceVaultClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
