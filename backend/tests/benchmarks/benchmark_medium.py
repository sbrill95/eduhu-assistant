"""
Benchmark Medium — 30 Tests, ~20 Min
Tier 1+2 komplett: J01-J06, J11, J13 + globale Qualitätschecks.
Jetzt mit LLM Judge (Haiku) für inhaltliche Bewertung.

Usage: cd backend && uv run python -m pytest tests/benchmarks/benchmark_medium.py -v -s
"""

import os
import asyncio
import pytest
import httpx

from tests.benchmarks.evaluators.llm_judge import (
    judge, CRITERIA_KLAUSUR, CRITERIA_DIFFERENZIERUNG,
    CRITERIA_STUNDENPLANUNG, CRITERIA_CHAT, CRITERIA_MEMORY,
)

BASE_URL = os.getenv("BENCHMARK_URL", "https://eduhu-assistant.onrender.com")
TEACHER_ID = os.getenv("BENCHMARK_TEACHER_ID", "a4d218bd-4ac8-4ce3-8d41-c85db8be6e32")
TIMEOUT = int(os.getenv("BENCHMARK_TIMEOUT", "180"))
PAUSE = 6
USE_JUDGE = os.getenv("BENCHMARK_JUDGE", "1") == "1"  # LLM Judge an/aus


async def generate_material(fach: str = "", klasse: str = "", thema: str = "", material_type: str = "", **kwargs) -> dict:
    await asyncio.sleep(PAUSE)
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        r = await c.post(f"{BASE_URL}/api/materials/generate", json={
            "teacher_id": TEACHER_ID, "fach": fach, "klasse": klasse,
            "thema": thema, "type": material_type,
        })
        return {"status": r.status_code, "data": r.json(), "elapsed": r.elapsed.total_seconds()}


async def chat(message: str, conversation_id: str = "") -> dict:
    await asyncio.sleep(PAUSE)
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        payload = {"message": message, "teacher_id": TEACHER_ID}
        if conversation_id:
            payload["conversation_id"] = conversation_id
        r = await c.post(f"{BASE_URL}/api/chat/send", json=payload,
                         headers={"X-Teacher-ID": TEACHER_ID})
        return {"status": r.status_code, "data": r.json(), "elapsed": r.elapsed.total_seconds()}


async def download_docx(material_id: str) -> dict:
    await asyncio.sleep(PAUSE)
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{BASE_URL}/api/materials/{material_id}/docx")
        return {"status": r.status_code, "size": len(r.content), "content_type": r.headers.get("content-type", "")}


def get_content(r: dict) -> str:
    return r["data"].get("message", {}).get("content", "")


def get_conv_id(r: dict) -> str:
    return r["data"].get("conversation_id", "")


async def judge_if_enabled(content: str, criteria: str, context: dict = None) -> dict | None:
    """Run LLM Judge only if enabled. Returns None if disabled."""
    if not USE_JUDGE:
        return None
    return await judge(content, criteria, context)


# ═══════════════════════════════════════════════════════════════
# J01 — Klausur (5 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ01Klausur:

    @pytest.mark.asyncio
    async def test_j01_1_afb_verteilung(self):
        """J01.1 — Klausur mit AFB I, II, III."""
        ctx = {"fach": "Physik", "klasse": "10", "thema": "Mechanik", "material_type": "klausur"}
        r = await generate_material(**ctx)
        assert r["status"] == 200
        content = str(r["data"].get("content", ""))

        verdict = await judge_if_enabled(content, CRITERIA_KLAUSUR, ctx)
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")
            assert verdict["passed"], f"Judge FAIL: {verdict['reason']}"

    @pytest.mark.asyncio
    async def test_j01_2_erwartungshorizont(self):
        """J01.2 — Erwartungshorizont mit Musterlösungen."""
        ctx = {"fach": "Chemie", "klasse": "11", "thema": "Redoxreaktionen", "material_type": "klausur"}
        r = await generate_material(**ctx)
        assert r["status"] == 200
        content = str(r["data"].get("content", ""))

        verdict = await judge_if_enabled(content, CRITERIA_KLAUSUR, ctx)
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")
            assert verdict["passed"], f"Judge FAIL: {verdict['reason']}"

    @pytest.mark.asyncio
    async def test_j01_3_notenschluessel(self):
        """J01.3 — Notenschlüssel / Bewertung beigefügt."""
        ctx = {"fach": "Deutsch", "klasse": "8", "thema": "Kurzgeschichten", "material_type": "klausur"}
        r = await generate_material(**ctx)
        assert r["status"] == 200
        content = str(r["data"].get("content", ""))
        assert len(content) > 200, "Klausur zu kurz"

        verdict = await judge_if_enabled(content, CRITERIA_KLAUSUR, ctx)
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")
            assert verdict["passed"], f"Judge FAIL: {verdict['reason']}"

    @pytest.mark.asyncio
    async def test_j01_4_docx_download(self):
        """J01.4 — DOCX-Download funktioniert."""
        r = await generate_material("Mathe", "9", "Quadratische Funktionen", "klausur")
        assert r["status"] == 200
        mid = r["data"].get("id", "")
        assert mid, "Keine Material-ID"
        d = await download_docx(mid)
        assert d["status"] == 200
        assert d["size"] > 5000, f"DOCX zu klein: {d['size']} bytes"

    @pytest.mark.asyncio
    async def test_j01_5_punkte_konsistent(self):
        """J01.5 — Punkteverteilung vorhanden."""
        ctx = {"fach": "Bio", "klasse": "10", "thema": "Genetik", "material_type": "klausur"}
        r = await generate_material(**ctx)
        assert r["status"] == 200
        content = str(r["data"].get("content", ""))

        verdict = await judge_if_enabled(content, CRITERIA_KLAUSUR, ctx)
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")
            assert verdict["passed"], f"Judge FAIL: {verdict['reason']}"


# ═══════════════════════════════════════════════════════════════
# J02 — Differenzierung (3 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ02Differenzierung:

    @pytest.mark.asyncio
    async def test_j02_1_drei_niveaus(self):
        """J02.1 — Drei Niveaustufen generieren (LLM Judge statt Keyword)."""
        ctx = {"fach": "Mathe", "klasse": "7", "thema": "Bruchrechnung", "material_type": "differenzierung"}
        r = await generate_material(**ctx)
        assert r["status"] == 200
        content = str(r["data"].get("content", ""))
        assert len(content) > 200, "Differenzierung zu kurz"

        # LLM Judge statt fragiler Keyword-Suche
        verdict = await judge_if_enabled(content, CRITERIA_DIFFERENZIERUNG, ctx)
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")
            assert verdict["passed"], f"Judge FAIL: {verdict['reason']}"

    @pytest.mark.asyncio
    async def test_j02_2_unterscheidbar(self):
        """J02.2 — Niveaus inhaltlich unterscheidbar."""
        ctx = {"fach": "Bio", "klasse": "9", "thema": "Zellteilung", "material_type": "differenzierung"}
        r = await generate_material(**ctx)
        assert r["status"] == 200
        content = str(r["data"].get("content", ""))

        verdict = await judge_if_enabled(content, CRITERIA_DIFFERENZIERUNG, ctx)
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")
            assert verdict["passed"], f"Judge FAIL: {verdict['reason']}"

    @pytest.mark.asyncio
    async def test_j02_3_docx(self):
        """J02.3 — DOCX-Download."""
        r = await generate_material("Deutsch", "5", "Märchen", "differenzierung")
        assert r["status"] == 200
        mid = r["data"].get("id", "")
        assert mid
        d = await download_docx(mid)
        assert d["status"] == 200
        assert d["size"] > 3000


# ═══════════════════════════════════════════════════════════════
# J03 — H5P Übungen (4 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ03H5P:

    @pytest.mark.asyncio
    async def test_j03_1_mc_fragen(self):
        """J03.1 — Multiple-Choice-Fragen generieren."""
        r = await chat("Erstelle 5 Multiple-Choice-Fragen zu Photosynthese für Klasse 7")
        assert r["status"] == 200
        content = get_content(r)
        assert len(content) > 50

        verdict = await judge_if_enabled(content, CRITERIA_CHAT,
            {"fach": "Bio", "klasse": "7", "thema": "Photosynthese", "type": "h5p"})
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")

    @pytest.mark.asyncio
    async def test_j03_2_zugangscode(self):
        """J03.2 — Agent reagiert auf Übungsanfrage (Rückfrage oder Code)."""
        r = await chat("Erstelle interaktive H5P-Übungen zum Thema Bruchrechnung für Mathe Klasse 6")
        assert r["status"] == 200
        content = get_content(r)
        # Agent darf Rückfrage stellen ODER direkt Code liefern — beides OK
        assert len(content) > 30, "Keine sinnvolle Antwort"

    @pytest.mark.asyncio
    async def test_j03_3_verschiedene_typen(self):
        """J03.3 — Lückentext-Übungen möglich."""
        r = await chat("Erstelle Lückentext-Übungen zum Thema Satzglieder für Deutsch Klasse 5")
        assert r["status"] == 200
        assert len(get_content(r)) > 50

    @pytest.mark.asyncio
    async def test_j03_4_schuelerseite(self):
        """J03.4 — Wahr-oder-Falsch-Fragen."""
        r = await chat("Erstelle 3 Wahr-oder-Falsch-Fragen zum Thema Demokratie für PolBil Klasse 9")
        assert r["status"] == 200
        assert len(get_content(r)) > 50


# ═══════════════════════════════════════════════════════════════
# J04 — Lehrplan (3 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ04Lehrplan:

    @pytest.mark.asyncio
    async def test_j04_1_relevante_chunks(self):
        """J04.1 — Relevante Lehrplaninhalte finden."""
        r = await chat("Was steht im Lehrplan zu Optik Klasse 8?")
        assert r["status"] == 200
        content = get_content(r)
        assert len(content) > 100

        verdict = await judge_if_enabled(content, CRITERIA_CHAT,
            {"fach": "Physik", "klasse": "8", "thema": "Optik (Lehrplan)", "type": "lehrplan"})
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")
            assert verdict["passed"], f"Judge FAIL: {verdict['reason']}"

    @pytest.mark.asyncio
    async def test_j04_2_kompetenzen(self):
        """J04.2 — Kompetenzen benennen."""
        r = await chat("Welche Kompetenzen soll ich bei Elektrizitätslehre fördern?")
        assert r["status"] == 200
        content = get_content(r)
        assert len(content) > 100

        verdict = await judge_if_enabled(content, CRITERIA_CHAT,
            {"fach": "Physik", "klasse": "?", "thema": "Elektrizitätslehre (Kompetenzen)", "type": "lehrplan"})
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")

    @pytest.mark.asyncio
    async def test_j04_3_pflege_lehrplan(self):
        """J04.3 — Pflege-Lehrplan BIBB."""
        r = await chat("Lehrplaninhalte für Pflege CE 01?")
        assert r["status"] == 200
        assert len(get_content(r)) > 50


# ═══════════════════════════════════════════════════════════════
# J05 — Stundenplanung (3 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ05Stundenplanung:

    @pytest.mark.asyncio
    async def test_j05_1_phasen(self):
        """J05.1 — Verlaufsplan mit Phasen und Zeitangaben."""
        ctx = {"fach": "Physik", "klasse": "9", "thema": "Elektrizität", "material_type": "stundenplanung"}
        r = await generate_material(**ctx)
        assert r["status"] == 200
        content = str(r["data"].get("content", ""))

        verdict = await judge_if_enabled(content, CRITERIA_STUNDENPLANUNG, ctx)
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")
            assert verdict["passed"], f"Judge FAIL: {verdict['reason']}"

    @pytest.mark.asyncio
    async def test_j05_2_methoden(self):
        """J05.2 — Methodenvielfalt."""
        ctx = {"fach": "Mathe", "klasse": "7", "thema": "Bruchrechnung", "material_type": "stundenplanung"}
        r = await generate_material(**ctx)
        assert r["status"] == 200
        content = str(r["data"].get("content", ""))

        verdict = await judge_if_enabled(content, CRITERIA_STUNDENPLANUNG, ctx)
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")
            assert verdict["passed"], f"Judge FAIL: {verdict['reason']}"

    @pytest.mark.asyncio
    async def test_j05_3_docx(self):
        """J05.3 — DOCX mit Verlaufsplan."""
        r = await generate_material("Sport", "8", "Basketball", "stundenplanung")
        assert r["status"] == 200
        mid = r["data"].get("id", "")
        assert mid
        d = await download_docx(mid)
        assert d["status"] == 200


# ═══════════════════════════════════════════════════════════════
# J06 — Memory (3 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ06Memory:

    @pytest.mark.asyncio
    async def test_j06_1_explizit_merken(self):
        """J06.1 — Explizites Merken bestätigen."""
        r = await chat("Merk dir: Meine Klasse 9b hat 28 Schüler")
        assert r["status"] == 200
        content = get_content(r)

        verdict = await judge_if_enabled(content, CRITERIA_MEMORY,
            {"type": "memory", "thema": "Klasse 9b, 28 Schüler"})
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")
            assert verdict["passed"], f"Judge FAIL: {verdict['reason']}"

    @pytest.mark.asyncio
    async def test_j06_2_implizit(self):
        """J06.2 — Implizites Erkennen von Informationen."""
        r = await chat("Ich unterrichte jetzt auch Informatik in Klasse 11")
        assert r["status"] == 200
        assert len(get_content(r)) > 20

    @pytest.mark.asyncio
    async def test_j06_3_profilkontext(self):
        """J06.3 — Profilbasierter Kontext."""
        r = await chat("Was weißt du über mich?")
        assert r["status"] == 200
        content = get_content(r)

        verdict = await judge_if_enabled(content,
            "1. Nennt die Antwort konkrete Fakten über den Lehrer?\n2. Sind Name, Fächer oder Schule erwähnt?\n3. Klingt die Antwort personalisiert (nicht generisch)?",
            {"type": "memory"})
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")
            assert verdict["passed"], f"Judge FAIL: {verdict['reason']}"


# ═══════════════════════════════════════════════════════════════
# J11 — Multi-Turn (4 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ11MultiTurn:

    @pytest.mark.asyncio
    async def test_j11_1_zwei_turns(self):
        """J11.1 — 2-Turn Kontextbewahrung."""
        r1 = await chat("Ich plane eine Stunde zu Optik für Klasse 8")
        assert r1["status"] == 200
        cid = get_conv_id(r1)

        r2 = await chat("Erstelle dafür 3 Aufgaben", conversation_id=cid)
        assert r2["status"] == 200
        content = get_content(r2)
        assert len(content) > 50

        verdict = await judge_if_enabled(content,
            "1. Bezieht sich die Antwort auf Optik/Licht?\n2. Enthält sie 3 Aufgaben?\n3. Passt das Niveau zu Klasse 8?",
            {"fach": "Physik", "klasse": "8", "thema": "Optik", "type": "multi-turn"})
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")

    @pytest.mark.asyncio
    async def test_j11_2_fuenf_turns(self):
        """J11.2 — 5-Turn Kontextbewahrung."""
        r1 = await chat("Ich plane eine Stunde zu Elektrizität für Klasse 9")
        cid = get_conv_id(r1)

        r2 = await chat("Was sind die Lernziele dafür?", conversation_id=cid)
        assert r2["status"] == 200

        r3 = await chat("Erstelle 3 Aufgaben dazu", conversation_id=cid)
        assert r3["status"] == 200

        r4 = await chat("Mach Aufgabe 2 schwieriger", conversation_id=cid)
        assert r4["status"] == 200

        r5 = await chat("Fasse zusammen was wir besprochen haben", conversation_id=cid)
        assert r5["status"] == 200
        content = get_content(r5)

        verdict = await judge_if_enabled(content,
            "1. Fasst die Antwort das bisherige Gespräch zusammen?\n2. Werden Elektrizität und Klasse 9 erwähnt?\n3. Werden die erstellten Aufgaben und Lernziele referenziert?",
            {"fach": "Physik", "klasse": "9", "thema": "Elektrizität (Zusammenfassung)", "type": "multi-turn"})
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")
            assert verdict["passed"], f"Judge FAIL: {verdict['reason']}"

    @pytest.mark.asyncio
    async def test_j11_3_material_iteration(self):
        """J11.3 — Material erstellen und iterieren."""
        r1 = await chat("Erstelle eine Klausur für Bio Klasse 10, Thema Ökologie, 45 Minuten")
        assert r1["status"] == 200
        cid = get_conv_id(r1)

        r2 = await chat("Füge eine Aufgabe zum Thema Nahrungskette hinzu", conversation_id=cid)
        assert r2["status"] == 200
        content = get_content(r2)
        assert len(content) > 50

    @pytest.mark.asyncio
    async def test_j11_4_kontext_bewahrt(self):
        """J11.4 — Kontext über 3 Nachrichten erhalten."""
        r1 = await chat("Ich bereite eine Projektwoche zum Thema Nachhaltigkeit vor")
        cid = get_conv_id(r1)

        r2 = await chat("Welche Fächer könnte ich einbinden?", conversation_id=cid)
        assert r2["status"] == 200

        r3 = await chat("Erstelle einen Zeitplan für 5 Tage", conversation_id=cid)
        assert r3["status"] == 200
        content = get_content(r3)
        assert len(content) > 100


# ═══════════════════════════════════════════════════════════════
# J13 — Todos (2 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ13Todos:

    @pytest.mark.asyncio
    async def test_j13_1_erstellen(self):
        """J13.1 — Todo erstellen."""
        r = await chat("Erinnere mich daran, morgen die Klausuren zurückzugeben")
        assert r["status"] == 200
        content = get_content(r)
        assert len(content) > 20

    @pytest.mark.asyncio
    async def test_j13_2_liste(self):
        """J13.2 — Todo-Liste anzeigen."""
        r = await chat("Was steht auf meiner Todo-Liste?")
        assert r["status"] == 200
        content = get_content(r)
        assert len(content) > 20


# ═══════════════════════════════════════════════════════════════
# Q — Globale Qualitätschecks (3 Tests)
# ═══════════════════════════════════════════════════════════════

class TestQualitaet:

    @pytest.mark.asyncio
    async def test_q01_sprache_deutsch(self):
        """Q01 — Antwort ist auf Deutsch."""
        r = await chat("Erkläre mir den Aufbau einer Unterrichtsstunde")
        assert r["status"] == 200
        content = get_content(r)
        assert any(w in content.lower() for w in ["die", "der", "und", "eine", "ist"])

        verdict = await judge_if_enabled(content,
            "1. Ist die Antwort auf Deutsch?\n2. Erklärt sie den Aufbau einer Unterrichtsstunde?\n3. Ist sie hilfreich für Lehrkräfte?")
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")

    @pytest.mark.asyncio
    async def test_q03_rueckfrage_bei_unklarheit(self):
        """Q03 — Bei vagem Prompt Rückfrage stellen."""
        r = await chat("Mach was")
        assert r["status"] == 200
        content = get_content(r)
        assert len(content) > 20

        verdict = await judge_if_enabled(content,
            "1. Stellt die Antwort eine klärende Rückfrage?\n2. Bietet sie Optionen an?\n3. Reagiert sie angemessen auf den vagen Prompt?")
        if verdict:
            print(f"\n  🧑‍⚖️ Judge: {verdict['score']}/5 — {verdict['reason']}")

    @pytest.mark.asyncio
    async def test_q06_robustheit(self):
        """Q06 — System crasht nicht bei ungewöhnlichem Input."""
        r = await chat("🎭🎪🎨 !!!??? 42 €€€ <script>alert('xss')</script>")
        assert r["status"] == 200
        assert len(get_content(r)) > 10
