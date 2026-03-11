"""Tests for the async FaceVault client."""

import httpx
import pytest
import respx

from facevault import AsyncFaceVaultClient, AuthError, NotFoundError, RateLimitError


BASE_URL = "https://api.facevault.id"


@pytest.mark.asyncio
@respx.mock
async def test_create_session():
    respx.post(f"{BASE_URL}/api/v1/sessions").mock(
        return_value=httpx.Response(200, json={
            "session_id": "sess_async",
            "session_token": "tok_async",
            "steps": ["liveness"],
            "challenge_nonce": "nonce_async",
        })
    )

    client = AsyncFaceVaultClient("fv_live_test")
    session = await client.create_session("user-42")

    assert session.session_id == "sess_async"
    assert session.session_token == "tok_async"
    assert session.steps == ["liveness"]
    assert "sid=sess_async" in session.webapp_url
    assert session.challenge_nonce == "nonce_async"
    await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_create_session_with_require_poa():
    route = respx.post(f"{BASE_URL}/api/v1/sessions").mock(
        return_value=httpx.Response(200, json={
            "session_id": "sess_poa",
            "session_token": "tok_poa",
            "steps": ["liveness", "poa"],
        })
    )

    client = AsyncFaceVaultClient("fv_live_test")
    session = await client.create_session("user-42", require_poa=True)

    assert session.session_id == "sess_poa"
    request = route.calls[0].request
    assert "require_poa=true" in str(request.url)
    await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_get_session():
    respx.get(f"{BASE_URL}/api/v1/sessions/sess_async").mock(
        return_value=httpx.Response(200, json={
            "session_id": "sess_async",
            "status": "completed",
            "steps": {"liveness": True},
            "face_match_passed": True,
            "error": "",
            "created_at": None,
            "completed_at": None,
            "trust_score": 72.0,
            "trust_decision": "accept",
            "require_poa": True,
            "poa": {"status": "verified"},
            "anti_spoofing": {"score": 0.88},
            "credential": {"credential_id": "cred_async"},
        })
    )

    client = AsyncFaceVaultClient("fv_live_test")
    status = await client.get_session("sess_async")

    assert status.session_id == "sess_async"
    assert status.status == "completed"
    assert status.face_match_passed is True
    assert status.trust_score == 72.0
    assert status.trust_decision == "accept"
    assert status.require_poa is True
    assert status.poa == {"status": "verified"}
    assert status.anti_spoofing == {"score": 0.88}
    assert status.credential == {"credential_id": "cred_async"}
    await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_auth_error():
    respx.post(f"{BASE_URL}/api/v1/sessions").mock(
        return_value=httpx.Response(401, json={"detail": "Invalid API key"})
    )

    client = AsyncFaceVaultClient("fv_live_bad")
    with pytest.raises(AuthError):
        await client.create_session("user-1")
    await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_not_found_error():
    respx.get(f"{BASE_URL}/api/v1/sessions/nope").mock(
        return_value=httpx.Response(404, json={"detail": "Not found"})
    )

    client = AsyncFaceVaultClient("fv_live_test")
    with pytest.raises(NotFoundError):
        await client.get_session("nope")
    await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_rate_limit_error():
    respx.post(f"{BASE_URL}/api/v1/sessions").mock(
        return_value=httpx.Response(429, json={"detail": "Too many requests"})
    )

    client = AsyncFaceVaultClient("fv_live_test")
    with pytest.raises(RateLimitError):
        await client.create_session("user-1")
    await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_async_context_manager():
    respx.post(f"{BASE_URL}/api/v1/sessions").mock(
        return_value=httpx.Response(200, json={
            "session_id": "sess_ctx",
            "session_token": "tok_ctx",
            "steps": [],
        })
    )

    async with AsyncFaceVaultClient("fv_live_test") as client:
        session = await client.create_session("user-1")
        assert session.session_id == "sess_ctx"


# ── Security: HTTPS enforcement ─────────────────────────────

def test_async_http_base_url_rejected():
    with pytest.raises(ValueError, match="HTTPS"):
        AsyncFaceVaultClient("fv_live_test", base_url="http://evil.example.com")


def test_async_http_webapp_base_rejected():
    with pytest.raises(ValueError, match="HTTPS"):
        AsyncFaceVaultClient("fv_live_test", webapp_base="http://evil.example.com")


# ── Security: API key validation ─────────────────────────────

def test_async_empty_api_key_rejected():
    with pytest.raises(ValueError, match="non-empty"):
        AsyncFaceVaultClient("")


def test_async_whitespace_api_key_rejected():
    with pytest.raises(ValueError, match="non-empty"):
        AsyncFaceVaultClient("   ")
