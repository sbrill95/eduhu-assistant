"""
Benchmark Quick — 10 Tests, ~2 Min
Schneller Smoke-Test, 1 Test pro Kernfunktion.

Usage: cd backend && python -m pytest tests/benchmarks/benchmark_quick.py -v -s
"""

import os
import time
import asyncio
import pytest
import httpx

BASE_URL = os.getenv("BENCHMARK_URL", "https://eduhu-assistant.onrender.com")
TEACHER_ID = os.getenv("BENCHMARK_TEACHER_ID", "a4d218bd-4ac8-4ce3-8d41-c85db8be6e32")
TIMEOUT = int(os.getenv("BENCHMARK_TIMEOUT", "120"))
PAUSE = 6  # seconds between API calls


async def generate_material(fach: str, klasse: str, thema: str, material_type: str) -> dict:
    """POST /api/materials/generate and return response dict."""
    await asyncio.sleep(PAUSE)
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        r = await c.post(f"{BASE_URL}/api/materials/generate", json={
            "teacher_id": TEACHER_ID, "fach": fach, "klasse": klasse,
            "thema": thema, "type": material_type,
        })
        return {"status": r.status_code, "data": r.json(), "elapsed": r.elapsed.total_seconds()}


async def chat(message: str, conversation_id: str = "") -> dict:
    """POST /api/chat/send and return response dict."""
    await asyncio.sleep(PAUSE)
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        r = await c.post(f"{BASE_URL}/api/chat/send", json={
            "message": message, "teacher_id": TEACHER_ID,
            "conversation_id": conversation_id,
        }, headers={"X-Teacher-ID": TEACHER_ID})
        return {"status": r.status_code, "data": r.json(), "elapsed": r.elapsed.total_seconds()}


class TestQuick:
    """10 Smoke Tests — je 1 pro Kernfunktion."""

    @pytest.mark.asyncio
    async def test_j01_klausur(self):
        """J01 — Klausur generieren."""
        r = await generate_material("Physik", "10", "Mechanik", "klausur")
        assert r["status"] == 200, f"HTTP {r['status']}: {r['data']}"
        d = r["data"]
        assert "id" in d, f"Keine Material-ID: {d}"
        content = str(d.get("content", ""))
        assert "afb" in content.lower() or "AFB" in content, "Kein AFB in Klausur"

    @pytest.mark.asyncio
    async def test_j02_differenzierung(self):
        """J02 — Differenziertes Material (3 Niveaus)."""
        r = await generate_material("Mathe", "7", "Bruchrechnung", "differenzierung")
        assert r["status"] == 200, f"HTTP {r['status']}: {r['data']}"
        assert "id" in r["data"]

    @pytest.mark.asyncio
    async def test_j03_h5p(self):
        """J03 — H5P interaktive Übungen."""
        r = await chat("Erstelle 5 Multiple-Choice-Fragen zu Photosynthese für Klasse 7")
        assert r["status"] == 200
        content = r["data"].get("message", {}).get("content", "")
        # Should contain access code or exercise link
        assert any(w in content.lower() for w in ["code", "/s/", "übung", "fragen"]), \
            f"Keine Übungs-Referenz: {content[:200]}"

    @pytest.mark.asyncio
    async def test_j04_lehrplan(self):
        """J04 — Lehrplan durchsuchen."""
        r = await chat("Was steht im Lehrplan zu Optik Klasse 8?")
        assert r["status"] == 200
        content = r["data"].get("message", {}).get("content", "")
        assert len(content) > 50, f"Zu kurze Antwort: {content}"

    @pytest.mark.asyncio
    async def test_j05_stundenplanung(self):
        """J05 — Stundenplanung erstellen."""
        r = await generate_material("Sport", "9", "Volleyball", "stundenplanung")
        assert r["status"] == 200
        assert "id" in r["data"]

    @pytest.mark.asyncio
    async def test_j06_memory(self):
        """J06 — Memory: Sich etwas merken."""
        r = await chat("Merk dir: Klasse 8a hat Schwierigkeiten mit Bruchrechnung")
        assert r["status"] == 200
        content = r["data"].get("message", {}).get("content", "")
        assert any(w in content.lower() for w in ["merk", "gespeichert", "notier", "8a", "bruch"]), \
            f"Keine Bestätigung: {content[:200]}"

    @pytest.mark.asyncio
    async def test_j07_elternbrief(self):
        """J07 — Elternbrief schreiben."""
        r = await chat("Schreibe einen Elternbrief für den Wandertag am 15. März")
        assert r["status"] == 200
        content = r["data"].get("message", {}).get("content", "")
        assert any(w in content.lower() for w in ["eltern", "wandertag", "märz"]), \
            f"Kein Elternbrief: {content[:200]}"

    @pytest.mark.asyncio
    async def test_j08_bildersuche(self):
        """J08 — Bildersuche."""
        r = await chat("Suche ein Bild vom Wasserkreislauf")
        assert r["status"] == 200
        content = r["data"].get("message", {}).get("content", "")
        assert len(content) > 20, f"Zu kurze Antwort: {content}"

    @pytest.mark.asyncio
    async def test_j10_podcast(self):
        """J10 — Podcast-Skript erstellen."""
        r = await generate_material("Ethik", "10", "Künstliche Intelligenz", "podcast")
        assert r["status"] == 200
        assert "id" in r["data"]

    @pytest.mark.asyncio
    async def test_j11_multiturn(self):
        """J11 — Multi-Turn Kontext (2 Turns)."""
        r1 = await chat("Ich plane eine Stunde zu Optik für Klasse 8")
        assert r1["status"] == 200
        conv_id = r1["data"].get("conversation_id", "")

        r2 = await chat("Erstelle dafür 3 Aufgaben", conversation_id=conv_id)
        assert r2["status"] == 200
        content = r2["data"].get("message", {}).get("content", "")
        # Should reference Optik or Klasse 8 from Turn 1
        assert any(w in content.lower() for w in ["optik", "klasse 8", "aufgabe", "licht"]), \
            f"Kein Kontextbezug: {content[:200]}"
