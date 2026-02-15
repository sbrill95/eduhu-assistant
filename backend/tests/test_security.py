"""
Security Tests — Ebene 2c: Autorisierung, Isolation, Input-Sanitization.

Testet Sicherheitsaspekte isoliert.
"""

import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import ASGITransport, AsyncClient

from tests.conftest import TEACHER_ID, FakeDB

import os
os.environ.setdefault("SUPABASE_URL", "https://fake.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "fake-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "fake-anthropic-key")

from app.main import app


# ═══════════════════════════════════════
# 4.1 Authorization Checks
# ═══════════════════════════════════════

class TestAuthorization:
    """Every protected endpoint must reject unauthorized access."""

    @pytest_asyncio.fixture
    async def no_auth_client(self, db_patch):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    @pytest_asyncio.fixture
    async def other_teacher_client(self, db_patch):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            ac.headers["X-Teacher-ID"] = "other-teacher-id"
            yield ac

    @pytest.mark.asyncio
    async def test_no_header_rejected(self, no_auth_client):
        endpoints = [
            ("GET", f"/api/profile/{TEACHER_ID}"),
            ("PATCH", f"/api/profile/{TEACHER_ID}"),
            ("POST", "/api/chat/send"),
            ("GET", "/api/chat/conversations"),
        ]
        for method, url in endpoints:
            if method == "GET":
                r = await no_auth_client.get(url)
            elif method == "PATCH":
                r = await no_auth_client.patch(url, json={})
            elif method == "POST":
                r = await no_auth_client.post(url, json={"message": "test", "teacher_id": "t"})
            assert r.status_code == 401, f"{method} {url} should require auth"

    @pytest.mark.asyncio
    async def test_cross_teacher_profile_forbidden(self, other_teacher_client):
        r = await other_teacher_client.get(f"/api/profile/{TEACHER_ID}")
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_cross_teacher_profile_update_forbidden(self, other_teacher_client):
        r = await other_teacher_client.patch(
            f"/api/profile/{TEACHER_ID}",
            json={"bundesland": "Bayern"},
        )
        assert r.status_code == 403


# ═══════════════════════════════════════
# 4.2 Input Sanitization
# ═══════════════════════════════════════

class TestInputSanitization:
    """Malicious inputs should be handled safely."""

    @pytest_asyncio.fixture
    async def client(self, db_patch):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            ac.headers["X-Teacher-ID"] = TEACHER_ID
            yield ac

    @pytest.mark.asyncio
    async def test_very_long_message_handled(self, client):
        """Extremely long message shouldn't crash the server."""
        # Mock the agent to avoid actual LLM call
        mock_result = MagicMock()
        mock_result.output = "OK"
        
        with patch("app.routers.chat.get_agent") as mock_get_agent:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=mock_result)
            mock_get_agent.return_value = mock_agent
            with patch("app.routers.chat.run_memory_agent", new_callable=AsyncMock):
                r = await client.post(
                    "/api/chat/send",
                    json={"message": "A" * 50000, "teacher_id": TEACHER_ID},
                )
        # Should not crash — either 200 or 400, not 500
        assert r.status_code in (200, 400, 422)

    @pytest.mark.asyncio
    async def test_sql_injection_in_filters(self, client):
        """SQL-like input in teacher_id should not cause issues."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            ac.headers["X-Teacher-ID"] = "'; DROP TABLE teachers; --"
            r = await ac.get("/api/chat/conversations")
        # Should work fine (Supabase uses parameterized queries)
        assert r.status_code in (200, 401, 403)


# ═══════════════════════════════════════
# 4.3 Error Leakage
# ═══════════════════════════════════════

class TestErrorLeakage:
    """Internal errors should not leak implementation details."""

    @pytest_asyncio.fixture
    async def client(self, db_patch):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            ac.headers["X-Teacher-ID"] = TEACHER_ID
            yield ac

    @pytest.mark.asyncio
    async def test_material_error_no_stacktrace(self, client):
        with patch("app.routers.materials.gen_mat", new_callable=AsyncMock, side_effect=RuntimeError("Internal LLM error with API key abc123")):
            r = await client.post(
                "/api/materials/generate",
                json={"type": "klausur", "fach": "Physik", "klasse": "9", "thema": "Test", "teacher_id": TEACHER_ID},
            )
        assert r.status_code == 500
        body = r.text
        assert "abc123" not in body  # API key should not leak
        assert "Traceback" not in body

    @pytest.mark.asyncio
    async def test_profile_not_found_clean_error(self, client, db_patch):
        """Profile 404 should be clean."""
        # Remove all profiles
        db_patch.tables["user_profiles"] = []

        r = await client.get(f"/api/profile/{TEACHER_ID}")
        assert r.status_code == 404
        assert "nicht gefunden" in r.json()["detail"].lower() or "not found" in r.json()["detail"].lower()
