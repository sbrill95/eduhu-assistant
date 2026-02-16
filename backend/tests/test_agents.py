"""
Agent-Logik-Tests — Ebene 2b: Testen der Agent-Hilfslogik OHNE echte LLM-Calls.

Testet:
- System Prompt Assembly (build_system_prompt)
- Context Block Construction (build_block3_context)
- Memory Extraction Pipeline (run_memory_agent)
- Material Service Pipeline (generate_material)
"""

import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock

from tests.conftest import (
    TEACHER_ID, make_memory,
    make_exam_structure, make_diff_structure,
    FakeDB,
)


# ═══════════════════════════════════════
# 3.1 System Prompt Construction
# ═══════════════════════════════════════

class TestSystemPrompt:
    """build_system_prompt assembles all 4 blocks correctly."""

    @pytest.fixture
    def fake_db(self):
        db = FakeDB()
        # Add some memories
        db.tables["user_memories"] = [
            make_memory(scope="class", category="curriculum", key="Thema", value="Optik"),
            make_memory(scope="self", category="preference", key="Stil", value="praxisnah"),
        ]
        db.tables["session_logs"] = [
            {"conversation_id": "c1", "user_id": TEACHER_ID, "summary": "Klausur Optik erstellt", "created_at": "2026-02-15T10:00:00Z"},
        ]
        db.tables["user_curricula"] = [
            {"id": "cur-1", "user_id": TEACHER_ID, "fach": "Physik", "jahrgang": "9", "status": "active", "wissenskarte": {"Optik": "Lichtbrechung, Reflexion"}},
        ]
        return db

    @pytest.mark.asyncio
    async def test_prompt_contains_identity(self, fake_db):
        from app.agents.system_prompt import build_system_prompt

        with patch("app.agents.system_prompt.db.select", side_effect=fake_db.select):
            prompt = await build_system_prompt(TEACHER_ID)

        assert "Du bist eduhu" in prompt
        assert "Rückfragen" in prompt or "Schärfungsfragen" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_profile_data(self, fake_db):
        from app.agents.system_prompt import build_system_prompt

        with patch("app.agents.system_prompt.db.select", side_effect=fake_db.select):
            prompt = await build_system_prompt(TEACHER_ID)

        assert "Sachsen" in prompt  # Bundesland from profile
        assert "Physik" in prompt   # Fach from profile

    @pytest.mark.asyncio
    async def test_prompt_contains_memories(self, fake_db):
        from app.agents.system_prompt import build_system_prompt

        with patch("app.agents.system_prompt.db.select", side_effect=fake_db.select):
            prompt = await build_system_prompt(TEACHER_ID)

        assert "Optik" in prompt  # From memories
        assert "praxisnah" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_session_summary(self, fake_db):
        from app.agents.system_prompt import build_system_prompt

        with patch("app.agents.system_prompt.db.select", side_effect=fake_db.select):
            prompt = await build_system_prompt(TEACHER_ID, conversation_summary="Wir haben über Optik gesprochen.")

        assert "Wir haben über Optik gesprochen" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_curriculum_wissenskarte(self, fake_db):
        from app.agents.system_prompt import build_block3_context

        with patch("app.agents.system_prompt.db.select", side_effect=fake_db.select):
            block3 = await build_block3_context(TEACHER_ID)

        assert "Lichtbrechung" in block3 or "Physik" in block3

    @pytest.mark.asyncio
    async def test_prompt_empty_for_new_teacher(self):
        """New teacher with no data should still get a valid prompt."""
        from app.agents.system_prompt import build_system_prompt

        empty_db = FakeDB()
        empty_db.tables["user_profiles"] = []
        empty_db.tables["user_memories"] = []
        empty_db.tables["session_logs"] = []
        empty_db.tables["user_curricula"] = []

        with patch("app.agents.system_prompt.db.select", side_effect=empty_db.select):
            prompt = await build_system_prompt("new-teacher-id")

        assert "Du bist eduhu" in prompt
        assert len(prompt) > 100

    @pytest.mark.asyncio
    async def test_prompt_tools_block_present(self, fake_db):
        from app.agents.system_prompt import build_system_prompt

        with patch("app.agents.system_prompt.db.select", side_effect=fake_db.select):
            prompt = await build_system_prompt(TEACHER_ID)

        assert "generate_material" in prompt
        assert "curriculum_search" in prompt


# ═══════════════════════════════════════
# 3.2 Memory Agent Pipeline
# ═══════════════════════════════════════

class TestMemoryAgent:
    """run_memory_agent extracts and stores memories."""

    @pytest.mark.asyncio
    async def test_memory_agent_stores_memories(self):
        """When the LLM extracts memories, they should be stored in DB."""
        from app.agents.memory_agent import run_memory_agent

        fake_db = FakeDB()
        fake_llm_response = json.dumps({
            "memories": [
                {"scope": "class", "category": "info", "key": "Klasse", "value": "8a", "importance": 0.9, "source": "explicit"},
            ],
            "session_summary": "Lehrkraft hat über ihre Klasse 8a gesprochen.",
        })

        mock_result = MagicMock()
        mock_result.output = fake_llm_response

        with patch("app.agents.memory_agent.Agent") as MockAgent, \
             patch("app.agents.memory_agent.db.upsert", side_effect=fake_db.upsert) as mock_upsert:
            mock_agent_instance = MagicMock()
            mock_agent_instance.run = AsyncMock(return_value=mock_result)
            MockAgent.return_value = mock_agent_instance

            await run_memory_agent(
                teacher_id=TEACHER_ID,
                conversation_id="conv-123",
                recent_messages=[
                    {"role": "user", "content": "Meine Klasse 8a hat große Schwierigkeiten mit Brüchen."},
                    {"role": "assistant", "content": "Verstehe, ich merke mir das über deine 8a."},
                ],
            )

        # upsert should have been called for the memory AND session summary
        assert mock_upsert.call_count >= 1

    @pytest.mark.asyncio
    async def test_memory_agent_empty_messages(self):
        """With no messages, memory agent should exit early."""
        from app.agents.memory_agent import run_memory_agent

        # This should NOT raise
        await run_memory_agent(TEACHER_ID, "conv-1", [])

    @pytest.mark.asyncio
    async def test_memory_agent_handles_llm_failure(self):
        """If LLM fails, memory agent should log error but not crash."""
        from app.agents.memory_agent import run_memory_agent

        with patch("app.agents.memory_agent.Agent") as MockAgent:
            mock_agent_instance = MagicMock()
            mock_agent_instance.run = AsyncMock(side_effect=RuntimeError("LLM timeout"))
            MockAgent.return_value = mock_agent_instance

            # Should NOT raise
            await run_memory_agent(
                TEACHER_ID, "conv-1",
                [{"role": "user", "content": "Test"}],
            )


# ═══════════════════════════════════════
# 3.3 Material Service Pipeline
# ═══════════════════════════════════════

class TestMaterialService:
    """Material generation pipeline: type resolution → agent → docx → store."""

    @pytest.mark.asyncio
    async def test_full_pipeline_klausur(self):
        from app.services.material_service import generate_material

        exam = make_exam_structure()

        with patch("app.services.material_service.run_material_agent", new_callable=AsyncMock, return_value=exam), \
             patch("app.services.material_service.db.upsert", new_callable=AsyncMock, return_value=[{}]):

            result = await generate_material(
                teacher_id=TEACHER_ID,
                fach="Physik",
                klasse="9",
                thema="Mechanik",
            )

        assert result.material_id  # UUID generated
        assert result.structure == exam
        assert isinstance(result.docx_bytes, bytes)
        assert len(result.docx_bytes) > 0
        assert "Mechanik" in result.summary or "Physik" in result.summary

    @pytest.mark.asyncio
    async def test_full_pipeline_differenzierung(self):
        from app.services.material_service import generate_material

        diff = make_diff_structure()

        with patch("app.services.material_service.run_material_agent", new_callable=AsyncMock, return_value=diff), \
             patch("app.services.material_service.db.upsert", new_callable=AsyncMock, return_value=[{}]):

            result = await generate_material(
                teacher_id=TEACHER_ID,
                fach="Deutsch",
                klasse="5",
                thema="Fabeln",
                material_type="differenzierung",
            )

        assert isinstance(result.docx_bytes, bytes)
        assert "Fabeln" in result.summary or "Deutsch" in result.summary
        assert "Basis" in result.summary or "Niveau" in result.summary

    @pytest.mark.asyncio
    async def test_pipeline_stores_in_db(self):
        from app.services.material_service import generate_material

        exam = make_exam_structure()

        with patch("app.services.material_service.run_material_agent", new_callable=AsyncMock, return_value=exam), \
             patch("app.services.material_service.db.upsert", new_callable=AsyncMock) as mock_upsert:

            await generate_material(
                teacher_id=TEACHER_ID,
                fach="Physik",
                klasse="9",
                thema="Mechanik",
            )

        mock_upsert.assert_called_once()
        call_args = mock_upsert.call_args
        assert call_args[0][0] == "generated_materials"
        stored = call_args[0][1]
        assert stored["teacher_id"] == TEACHER_ID
        assert stored["type"] == "klausur"
        assert "docx_base64" in stored

    @pytest.mark.asyncio
    async def test_type_aliases_resolve(self):
        from app.services.material_service import generate_material

        exam = make_exam_structure()

        with patch("app.services.material_service.run_material_agent", new_callable=AsyncMock, return_value=exam), \
             patch("app.services.material_service.db.upsert", new_callable=AsyncMock, return_value=[{}]):

            # "test" should map to "klausur"
            result = await generate_material(
                teacher_id=TEACHER_ID,
                fach="Physik",
                klasse="9",
                thema="Kräfte",
                material_type="test",
            )

        assert result.material_id  # Should succeed


# ═══════════════════════════════════════
# 3.4 DOCX Download with DB Fallback
# ═══════════════════════════════════════

class TestDocxDownloadFallback:
    """When DOCX not on disk, it should be loaded from DB."""

    @pytest.mark.asyncio
    async def test_load_from_db_fallback(self):
        from app.services.material_service import load_docx_from_db
        import base64

        fake_docx = b"PK\x03\x04fake-docx-content"
        encoded = base64.b64encode(fake_docx).decode("ascii")

        fake_db = FakeDB()
        fake_db.tables["generated_materials"] = [{"id": "mat-1", "docx_base64": encoded}]

        with patch("app.services.material_service.db.select", side_effect=fake_db.select):
            result = await load_docx_from_db("mat-1")

        assert result == fake_docx

    @pytest.mark.asyncio
    async def test_load_nonexistent_returns_none(self):
        from app.services.material_service import load_docx_from_db

        fake_db = FakeDB()
        with patch("app.services.material_service.db.select", side_effect=fake_db.select):
            result = await load_docx_from_db("nonexistent")

        assert result is None
