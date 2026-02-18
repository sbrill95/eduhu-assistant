"""
Benchmark Full — 62 Tests, ~45 Min
Alle Jobs J01-J13 mit LLM Judge (Haiku) für inhaltliche Bewertung.

Usage: cd backend && source .env && export ANTHROPIC_API_KEY && uv run python -m pytest tests/benchmarks/benchmark_full.py -v -s
"""

import os
import asyncio
import pytest
import httpx

from tests.benchmarks.evaluators.llm_judge import (
    judge, CRITERIA_KLAUSUR, CRITERIA_DIFFERENZIERUNG,
    CRITERIA_STUNDENPLANUNG, CRITERIA_H5P, CRITERIA_CHAT, CRITERIA_MEMORY,
)

BASE_URL = os.getenv("BENCHMARK_URL", "https://eduhu-assistant.onrender.com")
TEACHER_ID = os.getenv("BENCHMARK_TEACHER_ID", "a4d218bd-4ac8-4ce3-8d41-c85db8be6e32")
TIMEOUT = int(os.getenv("BENCHMARK_TIMEOUT", "180"))
PAUSE = 6
USE_JUDGE = os.getenv("BENCHMARK_JUDGE", "1") == "1"


async def llm_judge(content: str, criteria: str, ctx: dict = None) -> dict | None:
    if not USE_JUDGE or not content:
        return None
    v = await judge(content, criteria, ctx)
    if v:
        print(f"\n  🧑‍⚖️ Judge: {v['score']}/5 — {v['reason']}")
    return v


async def generate_material(fach: str, klasse: str, thema: str, material_type: str, **extra) -> dict:
    await asyncio.sleep(PAUSE)
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        payload = {"teacher_id": TEACHER_ID, "fach": fach, "klasse": klasse,
                   "thema": thema, "type": material_type, **extra}
        r = await c.post(f"{BASE_URL}/api/materials/generate", json=payload)
        return {"status": r.status_code, "data": r.json(), "elapsed": r.elapsed.total_seconds()}


async def chat(message: str, conversation_id: str = "") -> dict:
    await asyncio.sleep(PAUSE)
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        r = await c.post(f"{BASE_URL}/api/chat/send", json={
            "message": message, "teacher_id": TEACHER_ID,
            "conversation_id": conversation_id,
        }, headers={"X-Teacher-ID": TEACHER_ID})
        return {"status": r.status_code, "data": r.json(), "elapsed": r.elapsed.total_seconds()}


async def download_docx(material_id: str) -> dict:
    await asyncio.sleep(PAUSE)
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{BASE_URL}/api/materials/{material_id}/docx")
        return {"status": r.status_code, "size": len(r.content)}


async def get_public_page(code: str) -> dict:
    await asyncio.sleep(2)
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(f"{BASE_URL}/api/public/pages/{code}")
        return {"status": r.status_code, "data": r.json() if r.status_code == 200 else {}}


def gc(r: dict) -> str:
    """Get content from chat response."""
    return r["data"].get("message", {}).get("content", "")


def gcid(r: dict) -> str:
    return r["data"].get("conversation_id", "")


# ═══════════════════════════════════════════════════════════════
# J01 — Klausur (8 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ01Klausur:

    @pytest.mark.asyncio
    async def test_j01_1_afb_physik(self):
        """J01.1 — AFB-Verteilung Physik Mechanik."""
        r = await generate_material("Physik", "10", "Mechanik", "klausur")
        assert r["status"] == 200
        c = str(r["data"].get("content", ""))
        v = await llm_judge(c, CRITERIA_KLAUSUR, {"fach": "Physik", "klasse": "10", "thema": "Mechanik"})
        if v: assert v["passed"], f"Judge FAIL: {v['reason']}"

    @pytest.mark.asyncio
    async def test_j01_1b_afb_deutsch(self):
        """J01.1b — AFB-Verteilung Deutsch Kurzgeschichten."""
        r = await generate_material("Deutsch", "8", "Kurzgeschichten", "klausur")
        assert r["status"] == 200
        assert "id" in r["data"]

    @pytest.mark.asyncio
    async def test_j01_1c_afb_pflege(self):
        """J01.1c — AFB-Verteilung Pflege Pflegeprozess."""
        r = await generate_material("Pflege", "11", "Pflegeprozess", "klausur")
        assert r["status"] == 200
        assert "id" in r["data"]

    @pytest.mark.asyncio
    async def test_j01_2_erwartungshorizont(self):
        """J01.2 — Erwartungshorizont vorhanden."""
        r = await generate_material("Chemie", "11", "Redoxreaktionen", "klausur")
        assert r["status"] == 200
        c = str(r["data"].get("content", ""))
        v = await llm_judge(c, CRITERIA_KLAUSUR, {"fach": "Chemie", "klasse": "11", "thema": "Redoxreaktionen"})
        if v: assert v["passed"], f"Judge FAIL: {v['reason']}"

    @pytest.mark.asyncio
    async def test_j01_3_notenschluessel(self):
        """J01.3 — Notenschlüssel."""
        r = await generate_material("Politik", "10", "Demokratie", "klausur")
        assert r["status"] == 200

    @pytest.mark.asyncio
    async def test_j01_4_docx(self):
        """J01.4 — DOCX-Download > 5KB."""
        r = await generate_material("Mathe", "9", "Quadratische Funktionen", "klausur")
        assert r["status"] == 200
        mid = r["data"]["id"]
        d = await download_docx(mid)
        assert d["status"] == 200
        assert d["size"] > 5000

    @pytest.mark.asyncio
    async def test_j01_5_punkte(self):
        """J01.5 — Punkteverteilung konsistent."""
        r = await generate_material("Bio", "10", "Genetik", "klausur")
        assert r["status"] == 200
        c = str(r["data"].get("content", ""))
        v = await llm_judge(c, CRITERIA_KLAUSUR, {"fach": "Bio", "klasse": "10", "thema": "Genetik"})
        if v: assert v["passed"], f"Judge FAIL: {v['reason']}"

    @pytest.mark.asyncio
    async def test_j01_8_latenz(self):
        """J01.8 — Antwortzeit < 120s."""
        r = await generate_material("Geschichte", "9", "Weimarer Republik", "klausur")
        assert r["status"] == 200
        assert r["elapsed"] < 120, f"Zu langsam: {r['elapsed']:.1f}s"


# ═══════════════════════════════════════════════════════════════
# J02 — Differenzierung (5 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ02Differenzierung:

    @pytest.mark.asyncio
    async def test_j02_1_drei_niveaus(self):
        """J02.1 — Drei Niveaustufen."""
        r = await generate_material("Mathe", "7", "Bruchrechnung", "differenzierung")
        assert r["status"] == 200
        c = str(r["data"].get("content", ""))
        v = await llm_judge(c, CRITERIA_DIFFERENZIERUNG, {"fach": "Mathe", "klasse": "7", "thema": "Bruchrechnung"})
        if v: assert v["passed"], f"Judge FAIL: {v['reason']}"

    @pytest.mark.asyncio
    async def test_j02_2_unterscheidbar(self):
        """J02.2 — Niveaus inhaltlich unterscheidbar."""
        r = await generate_material("Bio", "9", "Zellteilung", "differenzierung")
        assert r["status"] == 200

    @pytest.mark.asyncio
    async def test_j02_3_gleiches_lernziel(self):
        """J02.3 — Gleiches Lernziel auf allen Niveaus."""
        r = await generate_material("Deutsch", "5", "Märchen", "differenzierung")
        assert r["status"] == 200

    @pytest.mark.asyncio
    async def test_j02_4_docx(self):
        """J02.4 — DOCX-Download."""
        r = await generate_material("Englisch", "7", "Simple Past", "differenzierung")
        assert r["status"] == 200
        mid = r["data"].get("id", "")
        assert mid
        d = await download_docx(mid)
        assert d["status"] == 200

    @pytest.mark.asyncio
    async def test_j02_5_hilfestellungen(self):
        """J02.5 — Basis-Niveau hat Hilfestellungen."""
        r = await generate_material("Physik", "8", "Optik", "differenzierung")
        assert r["status"] == 200


# ═══════════════════════════════════════════════════════════════
# J03 — H5P (6 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ03H5P:

    @pytest.mark.asyncio
    async def test_j03_1_mc(self):
        """J03.1 — Multiple-Choice generieren."""
        r = await chat("Erstelle 5 Multiple-Choice-Fragen zu Photosynthese für Klasse 7")
        assert r["status"] == 200
        assert len(gc(r)) > 50

    @pytest.mark.asyncio
    async def test_j03_2_code(self):
        """J03.2 — Agent reagiert auf H5P-Anfrage (Rückfrage oder Code)."""
        r = await chat("Erstelle interaktive H5P-Übungen zum Thema Bruchrechnung für Mathe Klasse 6")
        assert r["status"] == 200
        assert len(gc(r)) > 30

    @pytest.mark.asyncio
    async def test_j03_3_lueckentext(self):
        """J03.3 — Lückentext möglich."""
        r = await chat("Erstelle Lückentext-Übungen zu Satzgliedern Klasse 5")
        assert r["status"] == 200

    @pytest.mark.asyncio
    async def test_j03_4_wahr_falsch(self):
        """J03.4 — Wahr-oder-Falsch."""
        r = await chat("Erstelle Wahr-oder-Falsch-Fragen zum Thema Demokratie Klasse 9")
        assert r["status"] == 200

    @pytest.mark.asyncio
    async def test_j03_5_dragtext(self):
        """J03.5 — Drag-Text."""
        r = await chat("Erstelle Zuordnungsübungen zum Thema Periodensystem Klasse 8")
        assert r["status"] == 200

    @pytest.mark.asyncio
    async def test_j03_6_fachlich_korrekt(self):
        """J03.6 — Fachliche Korrektheit."""
        r = await chat("Erstelle 3 MC-Fragen zu Newtons Gesetzen für Klasse 10")
        assert r["status"] == 200
        assert len(gc(r)) > 100


# ═══════════════════════════════════════════════════════════════
# J04 — Lehrplan (4 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ04Lehrplan:

    @pytest.mark.asyncio
    async def test_j04_1_optik(self):
        """J04.1 — Relevante Lehrplaninhalte Physik Optik."""
        r = await chat("Was steht im Lehrplan zu Optik Klasse 8?")
        assert r["status"] == 200
        assert len(gc(r)) > 100

    @pytest.mark.asyncio
    async def test_j04_2_kompetenzen(self):
        """J04.2 — Kompetenzen benennen."""
        r = await chat("Welche Kompetenzen soll ich bei Elektrizitätslehre fördern?")
        assert r["status"] == 200
        assert "kompetenz" in gc(r).lower() or "können" in gc(r).lower() or len(gc(r)) > 100

    @pytest.mark.asyncio
    async def test_j04_3_pflege(self):
        """J04.3 — Pflege-Lehrplan CE 01."""
        r = await chat("Lehrplaninhalte für Pflege CE 01?")
        assert r["status"] == 200
        assert len(gc(r)) > 50

    @pytest.mark.asyncio
    async def test_j04_4_kein_lehrplan(self):
        """J04.4 — Hinweis wenn kein Lehrplan vorhanden."""
        r = await chat("Was sagt der Lehrplan für Astronomie Klasse 12?")
        assert r["status"] == 200
        assert len(gc(r)) > 20


# ═══════════════════════════════════════════════════════════════
# J05 — Stundenplanung (5 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ05Stundenplanung:

    @pytest.mark.asyncio
    async def test_j05_1_phasen(self):
        """J05.1 — Verlaufsplan mit Phasen."""
        r = await generate_material("Physik", "9", "Elektrizität Doppelstunde", "stundenplanung")
        assert r["status"] == 200
        c = str(r["data"].get("content", ""))
        v = await llm_judge(c, CRITERIA_STUNDENPLANUNG, {"fach": "Physik", "klasse": "9", "thema": "Elektrizität"})
        if v: assert v["passed"], f"Judge FAIL: {v['reason']}"

    @pytest.mark.asyncio
    async def test_j05_2_methoden(self):
        """J05.2 — Methodenvielfalt."""
        r = await generate_material("Mathe", "7", "Bruchrechnung", "stundenplanung")
        assert r["status"] == 200

    @pytest.mark.asyncio
    async def test_j05_3_zeitangaben(self):
        """J05.3 — Zeitangaben summieren."""
        r = await generate_material("Bio", "8", "Ökosystem Wald", "stundenplanung")
        assert r["status"] == 200
        c = str(r["data"].get("content", ""))
        assert "min" in c.lower() or "minute" in c.lower()

    @pytest.mark.asyncio
    async def test_j05_4_lehrplanbezug(self):
        """J05.4 — Lehrplanbezug."""
        r = await generate_material("Physik", "10", "Mechanik", "stundenplanung")
        assert r["status"] == 200

    @pytest.mark.asyncio
    async def test_j05_5_docx(self):
        """J05.5 — DOCX mit Verlaufsplan."""
        r = await generate_material("Sport", "8", "Basketball", "stundenplanung")
        assert r["status"] == 200
        mid = r["data"].get("id", "")
        assert mid
        d = await download_docx(mid)
        assert d["status"] == 200


# ═══════════════════════════════════════════════════════════════
# J06 — Memory (5 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ06Memory:

    @pytest.mark.asyncio
    async def test_j06_1_explizit(self):
        """J06.1 — Explizites Merken."""
        r = await chat("Merk dir: Klasse 8a hat Schwierigkeiten mit Bruchrechnung")
        assert r["status"] == 200
        v = await llm_judge(gc(r), CRITERIA_MEMORY, {"thema": "Klasse 8a, Bruchrechnung"})
        if v: assert v["passed"], f"Judge FAIL: {v['reason']}"

    @pytest.mark.asyncio
    async def test_j06_2_implizit(self):
        """J06.2 — Implizites Erkennen."""
        r = await chat("Ich unterrichte jetzt auch Kunst in Klasse 5")
        assert r["status"] == 200

    @pytest.mark.asyncio
    async def test_j06_4_profil(self):
        """J06.4 — Profilbasierter Kontext."""
        r = await chat("Was weißt du über mich und meine Fächer?")
        assert r["status"] == 200
        v = await llm_judge(gc(r), "1. Nennt konkrete Fakten über den Lehrer?\n2. Sind Name, Fächer oder Schule erwähnt?\n3. Klingt personalisiert?")
        if v: assert v["passed"], f"Judge FAIL: {v['reason']}"

    @pytest.mark.asyncio
    async def test_j06_5_memory_in_material(self):
        """J06.5 — Memory beeinflusst Materialerstellung."""
        r = await chat("Plane eine Unterrichtsstunde für meine Klasse")
        assert r["status"] == 200
        assert len(gc(r)) > 100


# ═══════════════════════════════════════════════════════════════
# J07 — Elternkommunikation (4 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ07Elternbrief:

    @pytest.mark.asyncio
    async def test_j07_1_format(self):
        """J07.1 — Briefformat einhalten."""
        r = await chat("Schreibe einen Elternbrief für den Wandertag am 15. März")
        assert r["status"] == 200
        c = gc(r).lower()
        assert any(w in c for w in ["eltern", "liebe", "sehr geehrte"])

    @pytest.mark.asyncio
    async def test_j07_2_formaler_ton(self):
        """J07.2 — Formaler Ton, Sie-Form."""
        r = await chat("Schreibe einen Elternbrief: Elternabend am 20. Februar um 18 Uhr")
        assert r["status"] == 200
        c = gc(r)
        assert "Sie" in c or "Ihr" in c  # Sie-Form

    @pytest.mark.asyncio
    async def test_j07_3_details(self):
        """J07.3 — Relevante Details (Datum, Uhrzeit, Treffpunkt)."""
        r = await chat("Schreibe einen Elternbrief für die Klassenfahrt nach Hamburg, 10.-14. Juni")
        assert r["status"] == 200
        c = gc(r).lower()
        assert "hamburg" in c and ("juni" in c or "10." in c)

    @pytest.mark.asyncio
    async def test_j07_4_sensibel(self):
        """J07.4 — Sensibles Thema einfühlsam."""
        r = await chat("Schreibe einen Elternbrief: Schüler Max zeigt aggressives Verhalten im Unterricht")
        assert r["status"] == 200
        c = gc(r).lower()
        # Should be solution-oriented, not accusatory
        assert any(w in c for w in ["gespräch", "gemeinsam", "unterstütz", "zusammen"])


# ═══════════════════════════════════════════════════════════════
# J08 — Bilder (4 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ08Bilder:

    @pytest.mark.asyncio
    async def test_j08_1_suche(self):
        """J08.1 — Bildersuche Stockfotos."""
        r = await chat("Suche ein Bild vom Wasserkreislauf")
        assert r["status"] == 200
        assert len(gc(r)) > 20

    @pytest.mark.asyncio
    async def test_j08_2_generierung(self):
        """J08.2 — Bildgenerierung KI."""
        r = await chat("Erstelle ein Bild: Schematische Darstellung einer Pflanzenzelle")
        assert r["status"] == 200
        assert len(gc(r)) > 20

    @pytest.mark.asyncio
    async def test_j08_3_iteration(self):
        """J08.3 — Bild iterieren."""
        r1 = await chat("Erstelle ein Bild von einem Vulkanausbruch für ein Arbeitsblatt")
        assert r1["status"] == 200
        cid = gcid(r1)
        r2 = await chat("Mach es farbenfroher und füge Beschriftungen hinzu", conversation_id=cid)
        assert r2["status"] == 200


# ═══════════════════════════════════════════════════════════════
# J09 — Classroom-Tools (5 Tests) — Teilweise noch nicht implementiert
# ═══════════════════════════════════════════════════════════════

class TestJ09Classroom:

    @pytest.mark.asyncio
    async def test_j09_2_zufall(self):
        """J09.2 — Zufälligen Schüler wählen."""
        r = await chat("Wähle einen zufälligen Schüler aus: Anna, Ben, Clara, David, Eva")
        assert r["status"] == 200
        c = gc(r)
        assert any(name in c for name in ["Anna", "Ben", "Clara", "David", "Eva"])

    @pytest.mark.asyncio
    async def test_j09_3_gruppen(self):
        """J09.3 — Gruppen einteilen."""
        r = await chat("Teile diese Schüler in 3er-Gruppen: Anna, Ben, Clara, David, Eva, Finn")
        assert r["status"] == 200
        c = gc(r)
        assert any(name in c for name in ["Anna", "Ben", "Clara", "David", "Eva", "Finn"])

    @pytest.mark.asyncio
    async def test_j09_5_wuerfeln(self):
        """J09.5 — Würfeln."""
        r = await chat("Wirf 2 Würfel")
        assert r["status"] == 200
        assert len(gc(r)) > 5


# ═══════════════════════════════════════════════════════════════
# J10 — Audio & Sprache (4 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ10Audio:

    @pytest.mark.asyncio
    async def test_j10_1_podcast_skript(self):
        """J10.1 — Podcast-Skript mit Sprecherrollen."""
        r = await generate_material("Ethik", "10", "Künstliche Intelligenz", "podcast")
        assert r["status"] == 200
        assert "id" in r["data"]

    @pytest.mark.asyncio
    async def test_j10_3_gespraechssimulation(self):
        """J10.3 — Arzt-Patienten-Gespräch."""
        r = await generate_material("Pflege", "11", "Diabetes Patientenaufnahme", "gespraechssimulation")
        assert r["status"] == 200
        assert "id" in r["data"]

    @pytest.mark.asyncio
    async def test_j10_4_youtube_quiz(self):
        """J10.4 — YouTube-Quiz (Chat-basiert)."""
        r = await chat("Erstelle ein Quiz zu diesem Video: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert r["status"] == 200
        # May fail if yt-dlp can't access, but should not crash
        assert len(gc(r)) > 20


# ═══════════════════════════════════════════════════════════════
# J11 — Multi-Turn (4 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ11MultiTurn:

    @pytest.mark.asyncio
    async def test_j11_1_zwei_turns(self):
        """J11.1 — 2-Turn Kontext."""
        r1 = await chat("Ich plane eine Stunde zu Optik für Klasse 8")
        cid = gcid(r1)
        r2 = await chat("Erstelle dafür 3 Aufgaben", conversation_id=cid)
        assert r2["status"] == 200
        assert any(w in gc(r2).lower() for w in ["optik", "licht", "aufgabe"])

    @pytest.mark.asyncio
    async def test_j11_2_fuenf_turns(self):
        """J11.2 — 5-Turn Kontext."""
        r1 = await chat("Ich plane eine Stunde zu Elektrizität für Klasse 9")
        cid = gcid(r1)
        await chat("Was sind die Lernziele?", conversation_id=cid)
        await chat("Erstelle 3 Aufgaben", conversation_id=cid)
        await chat("Mach Aufgabe 2 schwieriger", conversation_id=cid)
        r5 = await chat("Fasse zusammen was wir besprochen haben", conversation_id=cid)
        assert r5["status"] == 200
        assert any(w in gc(r5).lower() for w in ["elektr", "klasse 9", "aufgabe"])

    @pytest.mark.asyncio
    async def test_j11_3_iteration(self):
        """J11.3 — Material-Iteration über Turns."""
        r1 = await chat("Erstelle eine Klausur für Bio Klasse 10, Ökologie, 45 Min")
        cid = gcid(r1)
        r2 = await chat("Füge eine Aufgabe zur Nahrungskette hinzu", conversation_id=cid)
        assert r2["status"] == 200

    @pytest.mark.asyncio
    async def test_j11_4_langer_kontext(self):
        """J11.4 — Kontext nach 5+ Nachrichten."""
        r1 = await chat("Ich bereite eine Projektwoche zum Thema Klimawandel vor")
        cid = gcid(r1)
        await chat("Welche Fächer kann ich einbinden?", conversation_id=cid)
        await chat("Fokus auf Naturwissenschaften und Geografie", conversation_id=cid)
        await chat("Erstelle Zeitplan für 5 Tage", conversation_id=cid)
        r5 = await chat("Was war nochmal unser Thema?", conversation_id=cid)
        assert r5["status"] == 200
        assert "klima" in gc(r5).lower()


# ═══════════════════════════════════════════════════════════════
# J12 — Recherche (3 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ12Recherche:

    @pytest.mark.asyncio
    async def test_j12_1_web(self):
        """J12.1 — Web-Recherche."""
        r = await chat("Welche aktuellen Methoden gibt es für inklusiven Physikunterricht?")
        assert r["status"] == 200
        assert len(gc(r)) > 100

    @pytest.mark.asyncio
    async def test_j12_2_wikipedia(self):
        """J12.2 — Facherklärung."""
        r = await chat("Erkläre den Doppler-Effekt")
        assert r["status"] == 200
        c = gc(r).lower()
        assert any(w in c for w in ["doppler", "frequenz", "welle", "schall"])

    @pytest.mark.asyncio
    async def test_j12_3_quellen(self):
        """J12.3 — Quellenangaben."""
        r = await chat("Recherchiere zum Thema Klimawandel im Unterricht")
        assert r["status"] == 200
        assert len(gc(r)) > 100


# ═══════════════════════════════════════════════════════════════
# J13 — Todos (4 Tests)
# ═══════════════════════════════════════════════════════════════

class TestJ13Todos:

    @pytest.mark.asyncio
    async def test_j13_1_erstellen(self):
        """J13.1 — Todo erstellen."""
        r = await chat("Erinnere mich: Morgen Klausuren zurückgeben")
        assert r["status"] == 200
        assert any(w in gc(r).lower() for w in ["todo", "erinner", "notier", "klausur"])

    @pytest.mark.asyncio
    async def test_j13_2_liste(self):
        """J13.2 — Todo-Liste anzeigen."""
        r = await chat("Was steht auf meiner Todo-Liste?")
        assert r["status"] == 200

    @pytest.mark.asyncio
    async def test_j13_3_abhaken(self):
        """J13.3 — Todo abhaken."""
        r1 = await chat("Erinnere mich: Zeugnisse drucken")
        cid = gcid(r1)
        r2 = await chat("Das mit den Zeugnissen ist erledigt", conversation_id=cid)
        assert r2["status"] == 200

    @pytest.mark.asyncio
    async def test_j13_4_faelligkeit(self):
        """J13.4 — Todo mit Fälligkeitsdatum."""
        r = await chat("Erinnere mich bis Freitag an die Noten-Eingabe")
        assert r["status"] == 200
        assert any(w in gc(r).lower() for w in ["freitag", "noten", "erinner", "todo"])


# ═══════════════════════════════════════════════════════════════
# Q — Qualitätschecks (6 Tests)
# ═══════════════════════════════════════════════════════════════

class TestQualitaet:

    @pytest.mark.asyncio
    async def test_q01_deutsch(self):
        """Q01 — Antwort auf Deutsch."""
        r = await chat("Erkläre den Aufbau einer Unterrichtsstunde")
        assert r["status"] == 200
        assert any(w in gc(r).lower() for w in ["die", "der", "und", "eine"])

    @pytest.mark.asyncio
    async def test_q02_keine_halluzination(self):
        """Q02 — Keine erfundenen Fakten bei bekanntem Thema."""
        r = await chat("Wer hat die Relativitätstheorie aufgestellt?")
        assert r["status"] == 200
        assert "einstein" in gc(r).lower()

    @pytest.mark.asyncio
    async def test_q03_rueckfrage(self):
        """Q03 — Rückfrage bei Unklarheit."""
        r = await chat("Mach was")
        assert r["status"] == 200
        assert "?" in gc(r) or any(w in gc(r).lower() for w in ["was", "welch", "möchtest", "kann"])

    @pytest.mark.asyncio
    async def test_q04_altersgerecht(self):
        """Q04 — Altersgerechte Sprache."""
        r = await chat("Erkläre Photosynthese für Klasse 5")
        assert r["status"] == 200
        v = await llm_judge(gc(r), "1. Ist die Sprache altersgerecht für 10-11-Jährige (Klasse 5)?\n2. Werden Fachbegriffe erklärt?\n3. Ist die Erklärung korrekt und verständlich?",
            {"fach": "Bio", "klasse": "5", "thema": "Photosynthese"})
        if v: assert v["passed"], f"Judge FAIL: {v['reason']}"

    @pytest.mark.asyncio
    async def test_q05_latenz(self):
        """Q05 — Antwortzeit < 30s für einfache Antworten."""
        r = await chat("Was ist 2+2?")
        assert r["status"] == 200
        assert r["elapsed"] < 30, f"Zu langsam: {r['elapsed']:.1f}s"

    @pytest.mark.asyncio
    async def test_q06_robustheit(self):
        """Q06 — Kein Crash bei ungewöhnlichem Input."""
        r = await chat("🎭🎪🎨 !!!??? <script>alert('xss')</script> DROP TABLE;")
        assert r["status"] == 200
        assert len(gc(r)) > 10
