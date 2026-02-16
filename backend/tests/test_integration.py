"""
Integration Tests — Ebene 2: API-Routen mit gemockter DB.

Testet die HTTP-Schicht (FastAPI Router) isoliert.
DB wird durch FakeDB ersetzt, LLM-Calls werden gemockt.
Diese Tests brauchen KEINEN laufenden Server und KEINE API-Keys.
"""

import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import ASGITransport, AsyncClient

from tests.conftest import TEACHER_ID, TEACHER_NAME, make_exam_structure

import os
os.environ.setdefault("SUPABASE_URL", "https://fake.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "fake-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "fake-anthropic-key")
os.environ.setdefault("OPENAI_API_KEY", "fake-openai-key")

from app.main import app


# ═══════════════════════════════════════
# 2.1 Health Check
# ═══════════════════════════════════════

class TestHealth:
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        r = await client.get("/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "version" in data


# ═══════════════════════════════════════
# 2.2 Auth — Login
# ═══════════════════════════════════════

class TestAuth:
    @pytest.mark.asyncio
    async def test_login_success(self, client, db_patch):
        r = await client.post("/api/auth/login", json={"password": "test123"})
        assert r.status_code == 200
        data = r.json()
        assert data["teacher_id"] == TEACHER_ID
        assert data["name"] == TEACHER_NAME

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, db_patch):
        r = await client.post("/api/auth/login", json={"password": "wrong"})
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_login_empty_password(self, client, db_patch):
        r = await client.post("/api/auth/login", json={"password": ""})
        assert r.status_code == 401


# ═══════════════════════════════════════
# 2.3 Profile CRUD
# ═══════════════════════════════════════

class TestProfile:
    @pytest.mark.asyncio
    async def test_get_own_profile(self, client, db_patch):
        r = await client.get(f"/api/profile/{TEACHER_ID}")
        assert r.status_code == 200
        data = r.json()
        assert data["bundesland"] == "Sachsen"
        assert "Physik" in data["faecher"]

    @pytest.mark.asyncio
    async def test_get_other_profile_forbidden(self, client, db_patch):
        r = await client.get("/api/profile/other-teacher-id")
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_update_profile(self, client, db_patch):
        r = await client.patch(
            f"/api/profile/{TEACHER_ID}",
            json={"bundesland": "NRW", "faecher": ["Bio", "Chemie"]},
        )
        assert r.status_code == 200

        # Verify update was applied
        profile = await db_patch.select("user_profiles", filters={"id": TEACHER_ID}, single=True)
        assert profile["bundesland"] == "NRW"
        assert "Bio" in profile["faecher"]

    @pytest.mark.asyncio
    async def test_update_other_profile_forbidden(self, client, db_patch):
        r = await client.patch(
            "/api/profile/other-id",
            json={"bundesland": "Bayern"},
        )
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_profile_partial_update(self, client, db_patch):
        """Only the provided fields should change."""
        r = await client.patch(
            f"/api/profile/{TEACHER_ID}",
            json={"schulform": "Realschule"},
        )
        assert r.status_code == 200
        profile = await db_patch.select("user_profiles", filters={"id": TEACHER_ID}, single=True)
        assert profile["schulform"] == "Realschule"
        # Other fields still intact
        assert profile["bundesland"] == "Sachsen"


# ═══════════════════════════════════════
# 2.4 Auth Gate — Missing X-Teacher-ID
# ═══════════════════════════════════════

class TestAuthGate:
    @pytest_asyncio.fixture
    async def unauthenticated_client(self, db_patch):
        """Client WITHOUT X-Teacher-ID header."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_profile_requires_auth(self, unauthenticated_client):
        r = await unauthenticated_client.get(f"/api/profile/{TEACHER_ID}")
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_chat_requires_auth(self, unauthenticated_client):
        r = await unauthenticated_client.post(
            "/api/chat/send",
            json={"message": "Hallo", "teacher_id": TEACHER_ID},
        )
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_conversations_requires_auth(self, unauthenticated_client):
        r = await unauthenticated_client.get("/api/chat/conversations")
        assert r.status_code == 401


# ═══════════════════════════════════════
# 2.5 Chat API (with mocked LLM)
# ═══════════════════════════════════════

class TestChatAPI:
    @pytest.mark.asyncio
    async def test_chat_send_creates_conversation(self, client, db_patch):
        """A chat message without conversation_id should create a new conversation."""
        # Mock the agent to return a simple response
        mock_result = MagicMock()
        mock_result.output = "Hallo! Wie kann ich dir helfen?"
        
        with patch("app.routers.chat.get_agent") as mock_get_agent:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=mock_result)
            mock_get_agent.return_value = mock_agent
            
            # Also mock the background tasks (memory, learning)
            with patch("app.routers.chat.run_memory_agent", new_callable=AsyncMock):
                r = await client.post(
                    "/api/chat/send",
                    json={"message": "Hallo", "teacher_id": TEACHER_ID},
                )

        assert r.status_code == 200
        data = r.json()
        assert "conversation_id" in data
        assert data["message"]["role"] == "assistant"
        assert len(data["message"]["content"]) > 0

    @pytest.mark.asyncio
    async def test_conversations_list_empty(self, client, db_patch):
        r = await client.get("/api/chat/conversations")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ═══════════════════════════════════════
# 2.6 Curriculum API
# ═══════════════════════════════════════

class TestCurriculumAPI:
    @pytest.mark.asyncio
    async def test_list_curricula_empty(self, client, db_patch):
        r = await client.get(f"/api/curriculum/list?teacher_id={TEACHER_ID}")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert len(r.json()) == 0

    @pytest.mark.asyncio
    async def test_upload_non_pdf_rejected(self, client, db_patch):
        """Only PDFs should be accepted."""
        r = await client.post(
            "/api/curriculum/upload",
            files={"file": ("test.txt", b"Not a PDF", "text/plain")},
            data={"teacher_id": TEACHER_ID, "fach": "Physik"},
        )
        assert r.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_oversized_rejected(self, client, db_patch):
        """Files > 20MB should be rejected."""
        # Create a fake 21MB "PDF"
        big_data = b"%PDF-" + b"x" * (21 * 1024 * 1024)
        r = await client.post(
            "/api/curriculum/upload",
            files={"file": ("huge.pdf", big_data, "application/pdf")},
            data={"teacher_id": TEACHER_ID, "fach": "Physik"},
        )
        assert r.status_code == 400


# ═══════════════════════════════════════
# 2.7 Material API (with mocked service)
# ═══════════════════════════════════════

class TestMaterialAPI:
    @pytest.mark.asyncio
    async def test_generate_material_returns_structure(self, client, db_patch):
        """POST /api/materials/generate should return MaterialResponse."""
        from app.services.material_service import MaterialResult
        
        exam = make_exam_structure()
        mock_result = MaterialResult(
            material_id="mat-123",
            structure=exam,
            docx_bytes=b"fake-docx",
            summary="Klausur erstellt",
        )

        with patch("app.routers.materials.gen_mat", new_callable=AsyncMock, return_value=mock_result):
            r = await client.post(
                "/api/materials/generate",
                json={
                    "type": "klausur",
                    "fach": "Physik",
                    "klasse": "9",
                    "thema": "Mechanik",
                    "teacher_id": TEACHER_ID,
                },
            )

        assert r.status_code == 200
        data = r.json()
        assert data["type"] == "klausur"
        assert data["id"] == "mat-123"
        assert "/api/materials/" in data["docx_url"]
        assert "aufgaben" in data["content"]

    @pytest.mark.asyncio
    async def test_download_nonexistent_material_404(self, client, db_patch):
        """GET /api/materials/{id}/docx should return 404 for unknown material."""
        with patch("app.routers.materials.load_docx_from_db", new_callable=AsyncMock, return_value=None):
            r = await client.get("/api/materials/nonexistent-id/docx")
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_generate_invalid_type_defaults_to_klausur(self, client, db_patch):
        """Unknown material type should default to klausur."""
        from app.services.material_service import MaterialResult
        exam = make_exam_structure()
        mock_result = MaterialResult(
            material_id="mat-456",
            structure=exam,
            docx_bytes=b"fake-docx",
            summary="Klausur erstellt",
        )

        with patch("app.routers.materials.gen_mat", new_callable=AsyncMock, return_value=mock_result):
            r = await client.post(
                "/api/materials/generate",
                json={
                    "type": "blabla",
                    "fach": "Physik",
                    "klasse": "9",
                    "thema": "Kräfte",
                    "teacher_id": TEACHER_ID,
                },
            )
        
        assert r.status_code == 200
        data = r.json()
        assert data["type"] == "klausur"  # Should have been normalized


# ═══════════════════════════════════════
# 2.8 Error Handling
# ═══════════════════════════════════════

class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_material_service_error_returns_500(self, client, db_patch):
        """Internal errors should return 500, NOT leak details."""
        with patch("app.routers.materials.gen_mat", new_callable=AsyncMock, side_effect=RuntimeError("LLM crashed")):
            r = await client.post(
                "/api/materials/generate",
                json={
                    "type": "klausur",
                    "fach": "Physik",
                    "klasse": "9",
                    "thema": "Mechanik",
                    "teacher_id": TEACHER_ID,
                },
            )
        assert r.status_code == 500
        # Should NOT contain the internal error message
        assert "LLM crashed" not in r.json().get("detail", "")

    @pytest.mark.asyncio
    async def test_material_value_error_returns_400(self, client, db_patch):
        """ValueError from service should return 400."""
        with patch("app.routers.materials.gen_mat", new_callable=AsyncMock, side_effect=ValueError("Ungültiger Typ")):
            r = await client.post(
                "/api/materials/generate",
                json={
                    "type": "klausur",
                    "fach": "Physik",
                    "klasse": "9",
                    "thema": "Test",
                    "teacher_id": TEACHER_ID,
                },
            )
        assert r.status_code == 400
