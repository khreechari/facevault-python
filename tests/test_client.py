"""Tests for the synchronous FaceVault client."""

import httpx
import pytest
import respx

from facevault import FaceVaultClient, AuthError, NotFoundError, RateLimitError, FaceVaultError


BASE_URL = "https://api.facevault.id"


@respx.mock
def test_create_session():
    respx.post(f"{BASE_URL}/api/v1/sessions").mock(
        return_value=httpx.Response(200, json={
            "session_id": "sess_123",
            "session_token": "tok_abc",
            "steps": ["liveness", "document"],
        })
    )

    client = FaceVaultClient("fv_live_test")
    session = client.create_session("user-42")

    assert session.session_id == "sess_123"
    assert session.session_token == "tok_abc"
    assert session.steps == ["liveness", "document"]
    assert "sid=sess_123" in session.webapp_url
    assert "st=tok_abc" in session.webapp_url
    client.close()


@respx.mock
def test_get_session():
    respx.get(f"{BASE_URL}/api/v1/sessions/sess_123").mock(
        return_value=httpx.Response(200, json={
            "session_id": "sess_123",
            "status": "completed",
            "steps": {"liveness": True, "document": True},
            "face_match_passed": True,
            "error": "",
            "created_at": "2026-01-01T00:00:00Z",
            "completed_at": "2026-01-01T00:05:00Z",
        })
    )

    client = FaceVaultClient("fv_live_test")
    status = client.get_session("sess_123")

    assert status.session_id == "sess_123"
    assert status.status == "completed"
    assert status.face_match_passed is True
    assert status.steps == {"liveness": True, "document": True}
    client.close()


@respx.mock
def test_auth_error():
    respx.post(f"{BASE_URL}/api/v1/sessions").mock(
        return_value=httpx.Response(401, json={"detail": "Invalid API key"})
    )

    client = FaceVaultClient("fv_live_bad")
    with pytest.raises(AuthError, match="Invalid API key"):
        client.create_session("user-1")
    client.close()


@respx.mock
def test_not_found_error():
    respx.get(f"{BASE_URL}/api/v1/sessions/nonexistent").mock(
        return_value=httpx.Response(404, json={"detail": "Session not found"})
    )

    client = FaceVaultClient("fv_live_test")
    with pytest.raises(NotFoundError, match="Session not found"):
        client.get_session("nonexistent")
    client.close()


@respx.mock
def test_rate_limit_error():
    respx.post(f"{BASE_URL}/api/v1/sessions").mock(
        return_value=httpx.Response(429, json={"detail": "Rate limit exceeded"})
    )

    client = FaceVaultClient("fv_live_test")
    with pytest.raises(RateLimitError, match="Rate limit exceeded"):
        client.create_session("user-1")
    client.close()


@respx.mock
def test_generic_error():
    respx.post(f"{BASE_URL}/api/v1/sessions").mock(
        return_value=httpx.Response(500, json={"detail": "Internal server error"})
    )

    client = FaceVaultClient("fv_live_test")
    with pytest.raises(FaceVaultError, match="Internal server error"):
        client.create_session("user-1")
    client.close()


@respx.mock
def test_context_manager():
    respx.post(f"{BASE_URL}/api/v1/sessions").mock(
        return_value=httpx.Response(200, json={
            "session_id": "sess_ctx",
            "session_token": "tok_ctx",
            "steps": [],
        })
    )

    with FaceVaultClient("fv_live_test") as client:
        session = client.create_session("user-1")
        assert session.session_id == "sess_ctx"


@respx.mock
def test_custom_base_url():
    respx.post("https://custom.api/api/v1/sessions").mock(
        return_value=httpx.Response(200, json={
            "session_id": "sess_custom",
            "session_token": "tok_custom",
            "steps": [],
        })
    )

    client = FaceVaultClient("fv_live_test", base_url="https://custom.api")
    session = client.create_session("user-1")
    assert session.session_id == "sess_custom"
    client.close()


@respx.mock
def test_custom_webapp_base():
    respx.post(f"{BASE_URL}/api/v1/sessions").mock(
        return_value=httpx.Response(200, json={
            "session_id": "sess_1",
            "session_token": "tok_1",
            "steps": [],
        })
    )

    client = FaceVaultClient("fv_live_test", webapp_base="https://myapp.example.com")
    session = client.create_session("user-1")
    assert session.webapp_url.startswith("https://myapp.example.com/")
    client.close()


# ── Security: HTTPS enforcement ─────────────────────────────

def test_http_base_url_rejected():
    with pytest.raises(ValueError, match="HTTPS"):
        FaceVaultClient("fv_live_test", base_url="http://evil.example.com")


def test_http_webapp_base_rejected():
    with pytest.raises(ValueError, match="HTTPS"):
        FaceVaultClient("fv_live_test", webapp_base="http://evil.example.com")


def test_trailing_slash_stripped():
    """HTTPS URLs with trailing slashes should be accepted and cleaned."""
    client = FaceVaultClient("fv_live_test", base_url="https://api.facevault.id/")
    assert client._base_url == "https://api.facevault.id"
    client.close()


# ── Security: API key validation ─────────────────────────────

def test_empty_api_key_rejected():
    with pytest.raises(ValueError, match="non-empty"):
        FaceVaultClient("")


def test_whitespace_api_key_rejected():
    with pytest.raises(ValueError, match="non-empty"):
        FaceVaultClient("   ")
