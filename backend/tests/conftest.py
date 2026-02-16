"""
Shared test fixtures for the eduhu-assistant test suite.

Provides:
- Fake DB layer (no Supabase needed)
- Fake LLM (no Anthropic/OpenAI API needed)
- FastAPI TestClient
- Sample data factories
"""

import os
import uuid
import pytest
import pytest_asyncio
from unittest.mock import patch

# ── Set test environment BEFORE any app imports ──
os.environ.setdefault("SUPABASE_URL", "https://fake.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "fake-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "fake-anthropic-key")
os.environ.setdefault("OPENAI_API_KEY", "fake-openai-key")
os.environ.setdefault("BRAVE_API_KEY", "fake-brave-key")

from httpx import ASGITransport, AsyncClient
from app.main import app
from app.models import (
    ExamStructure, ExamTask,
    DifferenzierungStructure, DiffNiveau, DiffTask,
)


# ═══════════════════════════════════════
# Data Factories
# ═══════════════════════════════════════

TEACHER_ID = "test-teacher-00000000-0000-0000-0000-000000000001"
TEACHER_NAME = "Test-Lehrer"

def make_teacher_profile(**overrides):
    """Create a sample teacher profile dict."""
    base = {
        "id": TEACHER_ID,
        "name": TEACHER_NAME,
        "bundesland": "Sachsen",
        "schulform": "Gymnasium",
        "faecher": ["Physik", "Mathematik"],
        "jahrgaenge": [8, 9, 10],
        "preferences": {},
        "class_summary": {},
    }
    base.update(overrides)
    return base


def make_exam_structure(**overrides):
    """Create a sample ExamStructure."""
    base = {
        "fach": "Physik",
        "klasse": "9",
        "thema": "Mechanik",
        "dauer_minuten": 45,
        "aufgaben": [
            ExamTask(
                aufgabe="Kräftezerlegung",
                beschreibung="Zerlege die Kraft F=50N in ihre Komponenten.",
                afb_level="I",
                punkte=10,
                erwartung=["Korrekte Zerlegung", "Richtige Einheiten"],
            ),
            ExamTask(
                aufgabe="Newton II Anwendung",
                beschreibung="Ein Auto (m=1200kg) beschleunigt mit a=2m/s². Berechne F.",
                afb_level="II",
                punkte=15,
                erwartung=["F=m*a", "F=2400N"],
            ),
        ],
        "gesamtpunkte": 25,
        "notenschluessel": {"1": "24-25", "2": "20-23", "3": "15-19", "4": "10-14", "5": "5-9", "6": "0-4"},
        "hinweise": ["Taschenrechner erlaubt"],
    }
    base.update(overrides)
    return ExamStructure(**base)


def make_diff_structure(**overrides):
    """Create a sample DifferenzierungStructure."""
    base = {
        "fach": "Deutsch",
        "klasse": "5",
        "thema": "Fabeln",
        "niveaus": [
            DiffNiveau(
                niveau="Basis",
                aufgaben=[DiffTask(aufgabe="Lesen", beschreibung="Lies die Fabel.", punkte=5)],
                zeitaufwand_minuten=15,
                hinweise=["Wörterbuch nutzen"],
            ),
            DiffNiveau(
                niveau="Mittel",
                aufgaben=[DiffTask(aufgabe="Analyse", beschreibung="Welche Moral hat die Fabel?", punkte=10)],
                zeitaufwand_minuten=20,
                hinweise=[],
            ),
            DiffNiveau(
                niveau="Erweitert",
                aufgaben=[DiffTask(aufgabe="Transfer", beschreibung="Schreibe eine eigene Fabel.", punkte=20)],
                zeitaufwand_minuten=30,
                hinweise=[],
            ),
        ],
        "allgemeine_hinweise": ["Einzelarbeit"],
    }
    base.update(overrides)
    return DifferenzierungStructure(**base)


def make_memory(scope="self", category="preference", key="Stil", value="praxisnah", **overrides):
    """Create a sample memory dict."""
    base = {
        "user_id": TEACHER_ID,
        "scope": scope,
        "category": category,
        "key": key,
        "value": value,
        "importance": 0.8,
        "source": "explicit",
    }
    base.update(overrides)
    return base


def make_curriculum_chunk(curriculum_id="cur-1", text="Optik: Lichtbrechung und Reflexion", **overrides):
    """Create a sample curriculum chunk dict."""
    base = {
        "id": str(uuid.uuid4()),
        "curriculum_id": curriculum_id,
        "chunk_text": text,
        "chunk_index": 0,
        "section_path": "Lernbereich 1",
    }
    base.update(overrides)
    return base


# ═══════════════════════════════════════
# Fake DB Layer
# ═══════════════════════════════════════

class FakeDB:
    """In-memory fake for app.db module. No network calls."""

    def __init__(self):
        self.tables: dict[str, list[dict]] = {
            "teachers": [{"id": TEACHER_ID, "name": TEACHER_NAME, "password": "test123"}],
            "user_profiles": [make_teacher_profile()],
            "user_memories": [],
            "conversations": [],
            "messages": [],
            "user_curricula": [],
            "curriculum_chunks": [],
            "generated_materials": [],
            "session_logs": [],
        }

    async def select(self, table, *, columns="*", filters=None, order=None, limit=None, single=False):
        rows = self.tables.get(table, [])
        if filters:
            for col, val in filters.items():
                rows = [r for r in rows if r.get(col) == val]
        if order:
            # Simple sort by first field
            field = order.split(".")[0]
            desc = order.endswith(".desc")
            rows = sorted(rows, key=lambda r: r.get(field, ""), reverse=desc)
        if limit:
            rows = rows[:limit]
        if single:
            return rows[0] if rows else None
        return rows

    async def insert(self, table, data):
        if "id" not in data:
            data["id"] = str(uuid.uuid4())
        self.tables.setdefault(table, []).append(data)
        return data

    async def update(self, table, data, filters):
        rows = self.tables.get(table, [])
        updated = []
        for r in rows:
            if all(r.get(k) == v for k, v in filters.items()):
                r.update(data)
                updated.append(r)
        return updated

    async def upsert(self, table, data, on_conflict=""):
        if isinstance(data, list):
            for d in data:
                await self.upsert(table, d, on_conflict)
            return data
        
        # Try to find existing
        conflict_cols = on_conflict.split(",") if on_conflict else ["id"]
        rows = self.tables.get(table, [])
        for r in rows:
            if all(r.get(c) == data.get(c) for c in conflict_cols if c in data):
                r.update(data)
                return [r]
        
        return [await self.insert(table, data)]

    async def insert_batch(self, table, rows):
        for r in rows:
            await self.insert(table, r)
        return rows


@pytest.fixture
def fake_db():
    """Provide a fresh FakeDB instance."""
    return FakeDB()


@pytest.fixture
def db_patch(fake_db):
    """Patch app.db with a FakeDB for all tests using this fixture."""
    with patch("app.db.select", side_effect=fake_db.select), \
         patch("app.db.insert", side_effect=fake_db.insert), \
         patch("app.db.update", side_effect=fake_db.update), \
         patch("app.db.upsert", side_effect=fake_db.upsert), \
         patch("app.db.insert_batch", side_effect=fake_db.insert_batch):
        yield fake_db


# ═══════════════════════════════════════
# FastAPI Test Client
# ═══════════════════════════════════════

@pytest_asyncio.fixture
async def client(db_patch):
    """Async HTTP client talking to the FastAPI app with mocked DB."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.headers["X-Teacher-ID"] = TEACHER_ID
        yield ac
