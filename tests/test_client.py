"""Tests for FaceVaultClient and AsyncFaceVaultClient."""

import pytest
import respx

from facevault import (
    AsyncFaceVaultClient,
    AuthError,
    FaceVaultClient,
    NotFoundError,
    RateLimitError,
)


# ---------------------------------------------------------------------------
# Sync client tests
# ---------------------------------------------------------------------------


class TestFaceVaultClient:
    def test_create_session(self, api_key, base_url, webapp_base):
        with respx.mock(base_url=base_url) as mock:
            mock.post("/api/v1/sessions").respond(
                201,
                json={
                    "session_id": "abc123",
                    "session_token": "tok_xyz",
                    "steps": ["id", "straight"],
                },
            )

            client = FaceVaultClient(api_key, base_url=base_url, webapp_base=webapp_base)
            session = client.create_session("user_42")

            assert session.session_id == "abc123"
            assert session.session_token == "tok_xyz"
            assert session.steps == ["id", "straight"]
            assert session.webapp_url == f"{webapp_base}/?sid=abc123&st=tok_xyz"

            # Verify auth header was sent
            req = mock.calls[0].request
            assert req.headers["X-FaceVault-Api-Key"] == api_key

            # Verify external_user_id in query params
            assert "external_user_id=user_42" in str(req.url)

            client.close()

    def test_get_session(self, api_key, base_url, webapp_base):
        with respx.mock(base_url=base_url) as mock:
            mock.get("/api/v1/sessions/abc123").respond(
                200,
                json={
                    "session_id": "abc123",
                    "status": "passed",
                    "steps": {"id": True, "straight": True},
                    "face_match_passed": True,
                    "error": "",
                    "created_at": "2026-02-20T10:00:00Z",
                    "completed_at": "2026-02-20T10:01:00Z",
                },
            )

            client = FaceVaultClient(api_key, base_url=base_url, webapp_base=webapp_base)
            status = client.get_session("abc123")

            assert status.session_id == "abc123"
            assert status.status == "passed"
            assert status.face_match_passed is True
            assert status.steps == {"id": True, "straight": True}

            client.close()

    def test_auth_error(self, api_key, base_url, webapp_base):
        with respx.mock(base_url=base_url) as mock:
            mock.post("/api/v1/sessions").respond(
                401,
                json={"detail": "Invalid API key"},
            )

            client = FaceVaultClient(api_key, base_url=base_url, webapp_base=webapp_base)
            with pytest.raises(AuthError, match="Invalid API key"):
                client.create_session("user_42")

            client.close()

    def test_not_found_error(self, api_key, base_url, webapp_base):
        with respx.mock(base_url=base_url) as mock:
            mock.get("/api/v1/sessions/nonexistent").respond(
                404,
                json={"detail": "Session not found"},
            )

            client = FaceVaultClient(api_key, base_url=base_url, webapp_base=webapp_base)
            with pytest.raises(NotFoundError, match="Session not found"):
                client.get_session("nonexistent")

            client.close()

    def test_rate_limit_error(self, api_key, base_url, webapp_base):
        with respx.mock(base_url=base_url) as mock:
            mock.post("/api/v1/sessions").respond(
                429,
                json={"detail": "Rate limit exceeded"},
            )

            client = FaceVaultClient(api_key, base_url=base_url, webapp_base=webapp_base)
            with pytest.raises(RateLimitError):
                client.create_session("user_42")

            client.close()

    def test_context_manager(self, api_key, base_url, webapp_base):
        with respx.mock(base_url=base_url) as mock:
            mock.post("/api/v1/sessions").respond(
                201,
                json={
                    "session_id": "ctx123",
                    "session_token": "tok_ctx",
                    "steps": ["id", "straight"],
                },
            )

            with FaceVaultClient(api_key, base_url=base_url, webapp_base=webapp_base) as client:
                session = client.create_session("user_ctx")
                assert session.session_id == "ctx123"


# ---------------------------------------------------------------------------
# Async client tests
# ---------------------------------------------------------------------------


class TestAsyncFaceVaultClient:
    @pytest.mark.asyncio
    async def test_create_session(self, api_key, base_url, webapp_base):
        async with respx.mock(base_url=base_url) as mock:
            mock.post("/api/v1/sessions").respond(
                201,
                json={
                    "session_id": "async_abc",
                    "session_token": "tok_async",
                    "steps": ["id", "straight"],
                },
            )

            client = AsyncFaceVaultClient(api_key, base_url=base_url, webapp_base=webapp_base)
            session = await client.create_session("user_async")

            assert session.session_id == "async_abc"
            assert session.session_token == "tok_async"
            assert session.webapp_url == f"{webapp_base}/?sid=async_abc&st=tok_async"

            await client.close()

    @pytest.mark.asyncio
    async def test_auth_error(self, api_key, base_url, webapp_base):
        async with respx.mock(base_url=base_url) as mock:
            mock.post("/api/v1/sessions").respond(
                401,
                json={"detail": "Invalid API key"},
            )

            client = AsyncFaceVaultClient(api_key, base_url=base_url, webapp_base=webapp_base)
            with pytest.raises(AuthError):
                await client.create_session("user_async")

            await client.close()

    @pytest.mark.asyncio
    async def test_context_manager(self, api_key, base_url, webapp_base):
        async with respx.mock(base_url=base_url) as mock:
            mock.post("/api/v1/sessions").respond(
                201,
                json={
                    "session_id": "actx",
                    "session_token": "tok_actx",
                    "steps": ["id", "straight"],
                },
            )

            async with AsyncFaceVaultClient(api_key, base_url=base_url, webapp_base=webapp_base) as client:
                session = await client.create_session("user_actx")
                assert session.session_id == "actx"
