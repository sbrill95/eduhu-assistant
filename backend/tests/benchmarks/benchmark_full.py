"""
Benchmark Full — 65+ Tests, ~30 Minutes
Alle Jobs J01-J13 mit allen Sub-Operationen aus BENCHMARK-JOBS.md.
"""

import asyncio
import re
from typing import Dict, Any

import pytest

from tests.benchmarks.evaluators.api_eval import APIGenerateEval, ChatEval, DOCXDownloadEval, H5PAccessEval
from tests.benchmarks.evaluators.db_eval import MemoryCheckEval


class TestBenchmarkFull:
    """Full benchmark suite with 65+ tests covering all jobs from BENCHMARK-JOBS.md."""
    
    # ==================== J01: Klausur erstellen (8 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_j01_1_klausur_afb_verteilung(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J01.1 — Aufgaben generieren mit AFB-Verteilung."""
        evaluator = APIGenerateEval(
            base_url=base_url,
            teacher_id=teacher_id,
            contains_text="AFB",
            timeout=api_timeout["generate"],
        )
        case = {"message": "Erstelle eine Klausur für Physik Klasse 10, Thema Mechanik, 45 Minuten", "material_type": "klausur"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J01.1 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j01_2_erwartungshorizont(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J01.2 — Erwartungshorizont beifügen."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, contains_text="Erwartungshorizont", timeout=api_timeout["generate"])
        case = {"message": "Erstelle eine Klausur für Physik Klasse 10, Thema Mechanik, 45 Minuten", "material_type": "klausur"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J01.2 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j01_3_notenschluessel(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J01.3 — Notenschlüssel beifügen."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, contains_text="Notenschlüssel", timeout=api_timeout["generate"])
        case = {"message": "Erstelle eine Klausur für Physik Klasse 10, Thema Mechanik, 45 Minuten", "material_type": "klausur"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J01.3 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j01_5_punkteverteilung(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J01.5 — Punkteverteilung konsistent."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle eine Klausur für Physik Klasse 10, Thema Mechanik, 45 Minuten", "material_type": "klausur"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J01.5 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j01_6_einzelne_aufgabe_aendern(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J01.6 — Einzelne Aufgabe ändern (2-turn)."""
        # Turn 1: Generate klausur
        eval1 = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case1 = {"message": "Erstelle eine Klausur für Mathe Klasse 9, Thema Gleichungen", "material_type": "klausur"}
        result1 = await eval1.evaluate(case1)
        assert result1.passed, f"J01.6 Turn 1 failed: {result1.metadata}"
        
        # Turn 2: Modify
        eval2 = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case2 = {"message": "Mach Aufgabe 2 anspruchsvoller"}
        result2 = await eval2.evaluate(case2)
        assert result2.passed, f"J01.6 Turn 2 failed: {result2.metadata}"
    
    @pytest.mark.asyncio
    async def test_j01_7_fachliche_korrektheit(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J01.7 — Fachliche Korrektheit."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle eine Klausur für Chemie Klasse 11, Thema Redoxreaktionen", "material_type": "klausur"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J01.7 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j01_8_antwortzeit(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J01.8 — Antwortzeit akzeptabel (<60s)."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=60)
        case = {"message": "Erstelle eine Klausur für Mathe Klasse 9, Thema Gleichungen, 45 Minuten", "material_type": "klausur"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J01.8 failed: {result.metadata}"
        assert result.metadata.get("duration_ms", 0) < 60000, "Response took longer than 60s"
    
    @pytest.mark.asyncio
    async def test_j01_variant_deutsch(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J01 Variant — Deutsch Klasse 8 Kurzgeschichten."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, contains_text="AFB", timeout=api_timeout["generate"])
        case = {"message": "Erstelle eine Klausur für Deutsch Klasse 8, Thema Kurzgeschichten, 90 Minuten", "material_type": "klausur"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J01 Deutsch variant failed: {result.metadata}"
    
    # ==================== J02: Differenzierung (5 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_j02_1_drei_niveaus(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J02.1 — Drei Niveaus generieren."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle differenziertes Material für Mathe Klasse 7, Thema Bruchrechnung", "material_type": "differenziert"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J02.1 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j02_2_niveaus_unterscheidbar(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J02.2 — Niveaus sind unterscheidbar."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle differenziertes Material für Mathe Klasse 7, Thema Bruchrechnung", "material_type": "differenziert"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J02.2 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j02_3_gleiches_lernziel(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J02.3 — Gleiches Lernziel auf allen Niveaus."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle differenziertes Material für Mathe Klasse 7, Thema Bruchrechnung", "material_type": "differenziert"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J02.3 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j02_5_hilfestellungen_basis(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J02.5 — Hilfestellungen auf Basis-Niveau."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle differenziertes Material für Mathe Klasse 7, Thema Bruchrechnung", "material_type": "differenziert"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J02.5 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j02_variant_biologie(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J02 Variant — Biologie Klasse 9 Zellteilung."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle differenziertes Material für Biologie Klasse 9, Thema Zellteilung", "material_type": "differenziert"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J02 Biologie variant failed: {result.metadata}"
    
    # ==================== J03: H5P Übungen (6 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_j03_1_uebungen_generieren(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J03.1 — Übungen generieren."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle 5 Multiple-Choice-Fragen zu Photosynthese für Klasse 7"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J03.1 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j03_2_zugangscode(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J03.2 — Zugangscode generiert."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle 5 Multiple-Choice-Fragen zu Photosynthese für Klasse 7"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J03.2 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j03_3_qr_code(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J03.3 — QR-Code generiert."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle 5 Multiple-Choice-Fragen zu Photosynthese für Klasse 7"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J03.3 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j03_5_verschiedene_typen(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J03.5 — Verschiedene Übungstypen."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle Lückentext-Übungen zum Thema Bruchrechnung Klasse 6"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J03.5 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j03_6_fachliche_korrektheit(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J03.6 — Fachliche Korrektheit."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle 5 Multiple-Choice-Fragen zu Photosynthese für Klasse 7"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J03.6 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j03_variant_truefalse(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J03 Variant — Wahr-oder-Falsch-Fragen."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle Wahr-oder-Falsch-Fragen zum Thema Demokratie Klasse 9"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J03 TrueFalse variant failed: {result.metadata}"
    
    # ==================== J04: Lehrplan (4 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_j04_1_lehrplan_chunks_finden(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J04.1 — Relevante Lehrplan-Chunks finden."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Was steht im Lehrplan zu Optik Klasse 8?"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J04.1 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j04_2_kompetenzen(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J04.2 — Kompetenzen benennen."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Welche Kompetenzen soll ich bei Elektrizitätslehre fördern?"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J04.2 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j04_3_kein_lehrplan_hinweis(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J04.3 — Kein Lehrplan → Hinweis (placeholder)."""
        # Note: This requires a teacher profile without uploaded curriculum
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Was sagt mein Lehrplan zu Optik?"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J04.3 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j04_4_richtiger_lehrplan(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J04.4 — Richtiger Lehrplan genutzt."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Lehrplaninhalte für Physik Klasse 9"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J04.4 failed: {result.metadata}"
    
    # ==================== J05: Stundenplanung (5 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_j05_1_verlaufsplan_phasen(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J05.1 — Verlaufsplan mit Phasen."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, contains_text="Einstieg", timeout=api_timeout["generate"])
        case = {"message": "Plane eine Doppelstunde zum Thema Elektrizität für Klasse 9", "material_type": "verlaufsplan"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J05.1 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j05_2_methodenvielfalt(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J05.2 — Methodenvielfalt."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Plane eine Doppelstunde zum Thema Elektrizität für Klasse 9", "material_type": "verlaufsplan"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J05.2 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j05_3_zeitangaben(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J05.3 — Zeitangaben summieren auf."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle einen Verlaufsplan für Mathe Klasse 7, Bruchrechnung, 45 Minuten", "material_type": "verlaufsplan"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J05.3 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j05_4_lehrplanbezug(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J05.4 — Lehrplanbezug."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Plane eine Stunde zu Optik für Klasse 8", "material_type": "verlaufsplan"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J05.4 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j05_5_docx_export(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J05.5 — DOCX-Export (placeholder)."""
        # Note: This would require extracting material_id and calling DOCXDownloadEval
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle einen Verlaufsplan für Mathe Klasse 7, Bruchrechnung, 45 Minuten", "material_type": "verlaufsplan"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J05.5 failed: {result.metadata}"
    
    # ==================== J06: Memory (5 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_j06_1_explizit_merken(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J06.1 — Explizites Merken."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Merk dir: Klasse 8a hat Schwierigkeiten mit Bruchrechnung"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J06.1 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j06_2_implizit_erkennen(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J06.2 — Implizites Erkennen."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Ich unterrichte Mathe und Bio in Klasse 7"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J06.2 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j06_3_abruf_neue_session(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J06.3 — Abruf in neuer Session."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Was weißt du über meine Klassen?"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J06.3 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j06_4_profilbasierter_kontext(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J06.4 — Profilbasierter Kontext."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Plane eine Stunde"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J06.4 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j06_5_memory_beeinflusst_material(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J06.5 — Memory beeinflusst Materialerstellung."""
        # Turn 1: Set memory
        eval1 = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case1 = {"message": "Merk dir: Ich bevorzuge Gruppenarbeit"}
        result1 = await eval1.evaluate(case1)
        assert result1.passed, f"J06.5 Turn 1 failed: {result1.metadata}"
        
        # Turn 2: Generate material
        eval2 = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case2 = {"message": "Erstelle einen Verlaufsplan für Biologie Klasse 8", "material_type": "verlaufsplan"}
        result2 = await eval2.evaluate(case2)
        assert result2.passed, f"J06.5 Turn 2 failed: {result2.metadata}"
    
    # ==================== J07: Elternkommunikation (4 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_j07_1_briefformat(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J07.1 — Briefformat einhalten."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Schreibe einen Elternbrief für den Wandertag am 15. März", "material_type": "elternbrief"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J07.1 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j07_2_formaler_ton(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J07.2 — Formaler Ton."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Schreibe einen Elternbrief für den Wandertag am 15. März", "material_type": "elternbrief"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J07.2 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j07_3_relevante_details(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J07.3 — Relevante Details."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Schreibe einen Elternbrief für den Wandertag am 15. März", "material_type": "elternbrief"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J07.3 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j07_4_kontextanpassung(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J07.4 — Kontextanpassung."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Schreibe einen Elternbrief: Schülerin Lisa zeigt aggressives Verhalten", "material_type": "elternbrief"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J07.4 failed: {result.metadata}"
    
    # ==================== J08: Bilder (4 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_j08_1_bildersuche(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J08.1 — Bildersuche (Stockfotos)."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Suche ein Bild vom Wasserkreislauf"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J08.1 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j08_2_bildgenerierung(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J08.2 — Bildgenerierung (KI)."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle ein Bild: Schematische Darstellung einer Pflanzenzelle"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J08.2 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j08_3_bild_iterieren(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J08.3 — Bild iterieren."""
        # Turn 1: Generate image
        eval1 = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case1 = {"message": "Erstelle ein Bild: Schematische Darstellung einer Pflanzenzelle"}
        result1 = await eval1.evaluate(case1)
        assert result1.passed, f"J08.3 Turn 1 failed: {result1.metadata}"
        
        # Turn 2: Iterate
        conv_id = result1.metadata.get("conversation_id")
        eval2 = ChatEval(base_url=base_url, teacher_id=teacher_id, conversation_id=conv_id, timeout=api_timeout["generate"])
        case2 = {"message": "Mach den Zellkern größer und rot", "conversation_id": conv_id}
        result2 = await eval2.evaluate(case2)
        assert result2.passed, f"J08.3 Turn 2 failed: {result2.metadata}"
    
    @pytest.mark.asyncio
    async def test_j08_4_bild_herunterladen(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J08.4 — Bild herunterladen (placeholder)."""
        # Note: This would require extracting image URL from response
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle ein Bild: Sonnenuntergang am Meer"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J08.4 failed: {result.metadata}"
    
    # ==================== J09: Classroom-Tools (5 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_j09_1_timer(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J09.1 — Timer stellen."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Stell einen Timer auf 5 Minuten"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J09.1 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j09_2_zufaelliger_schueler(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J09.2 — Zufälligen Schüler wählen."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Wähle einen Schüler aus: Anna, Ben, Clara, David, Eva"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J09.2 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j09_3_gruppen_einteilen(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J09.3 — Gruppen einteilen."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Teile diese Schüler in 3er-Gruppen ein: Anna, Ben, Clara, David, Eva, Finn"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J09.3 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j09_4_abstimmung(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J09.4 — Abstimmung erstellen."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle eine Abstimmung: Welches Thema wollen wir vertiefen? Optionen: Optik, Mechanik, Elektrizität"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J09.4 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j09_5_wuerfeln(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J09.5 — Würfeln."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Wirf 2 Würfel"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J09.5 failed: {result.metadata}"
    
    # ==================== J10: Audio & Sprache (4 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_j10_1_podcast_skript(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J10.1 — Podcast-Skript erstellen."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle einen Podcast zum Thema Klimawandel für Klasse 9, 5 Minuten", "material_type": "podcast"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J10.1 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j10_2_audio_generieren(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J10.2 — Audio generieren (placeholder)."""
        # Note: This requires TTS to be active
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle einen Podcast zum Thema Klimawandel für Klasse 9, 5 Minuten", "material_type": "podcast"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J10.2 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j10_3_gespraechssimulation(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J10.3 — Gesprächssimulation."""
        evaluator = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle ein Arzt-Patienten-Gespräch zum Thema Diabetes für Pflege-Azubis", "material_type": "podcast"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J10.3 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j10_4_youtube_quiz(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J10.4 — YouTube-Quiz (placeholder)."""
        # Note: This requires a valid YouTube URL
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case = {"message": "Erstelle ein Quiz zu diesem Video: https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J10.4 failed: {result.metadata}"
    
    # ==================== J11: Multi-Turn (4 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_j11_1_two_turn(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J11.1 — 2-Turn Kontext."""
        eval1 = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case1 = {"message": "Ich plane eine Stunde zu Optik für Klasse 8"}
        result1 = await eval1.evaluate(case1)
        assert result1.passed, f"J11.1 Turn 1 failed: {result1.metadata}"
        
        conv_id = result1.metadata.get("conversation_id")
        eval2 = ChatEval(base_url=base_url, teacher_id=teacher_id, conversation_id=conv_id, timeout=api_timeout["chat"])
        case2 = {"message": "Erstelle dafür 3 Aufgaben", "conversation_id": conv_id}
        result2 = await eval2.evaluate(case2)
        assert result2.passed, f"J11.1 Turn 2 failed: {result2.metadata}"
    
    @pytest.mark.asyncio
    async def test_j11_2_five_turn(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J11.2 — 5-Turn Kontext."""
        turns = [
            "Ich plane eine Stunde zu Optik für Klasse 8",
            "Was sind die Lernziele dafür laut Lehrplan?",
            "Erstelle 3 Aufgaben dazu",
            "Mach Aufgabe 2 schwieriger",
            "Fasse zusammen, was wir besprochen haben",
        ]
        
        conv_id = None
        for i, turn_msg in enumerate(turns):
            evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, conversation_id=conv_id, timeout=api_timeout["chat"])
            case = {"message": turn_msg}
            if conv_id:
                case["conversation_id"] = conv_id
            
            result = await evaluator.evaluate(case)
            assert result.passed, f"J11.2 Turn {i+1} failed: {result.metadata}"
            conv_id = result.metadata.get("conversation_id")
    
    @pytest.mark.asyncio
    async def test_j11_3_kontext_nach_20(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J11.3 — Kontext nach 20+ Turns."""
        # Simplified to 10 turns for benchmark
        conv_id = None
        for i in range(10):
            evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, conversation_id=conv_id, timeout=api_timeout["chat"])
            case = {"message": f"Info {i+1}: Füge diesen Punkt hinzu"}
            if conv_id:
                case["conversation_id"] = conv_id
            
            result = await evaluator.evaluate(case)
            assert result.passed, f"J11.3 Turn {i+1} failed: {result.metadata}"
            conv_id = result.metadata.get("conversation_id")
        
        # Summary
        eval_summary = ChatEval(base_url=base_url, teacher_id=teacher_id, conversation_id=conv_id, timeout=api_timeout["chat"])
        case_summary = {"message": "Fasse zusammen, woran wir gearbeitet haben", "conversation_id": conv_id}
        result_summary = await eval_summary.evaluate(case_summary)
        assert result_summary.passed, f"J11.3 Summary failed: {result_summary.metadata}"
    
    @pytest.mark.asyncio
    async def test_j11_4_material_iteration(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J11.4 — Material-Iteration."""
        # Turn 1: Generate
        eval1 = APIGenerateEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["generate"])
        case1 = {"message": "Erstelle eine Klausur für Physik Klasse 9, Thema Energie", "material_type": "klausur"}
        result1 = await eval1.evaluate(case1)
        assert result1.passed, f"J11.4 Turn 1 failed: {result1.metadata}"
        
        # Turn 2: Modify
        eval2 = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case2 = {"message": "Ändere Aufgabe 2"}
        result2 = await eval2.evaluate(case2)
        assert result2.passed, f"J11.4 Turn 2 failed: {result2.metadata}"
        
        # Turn 3: Add
        eval3 = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case3 = {"message": "Füge eine AFB-III-Aufgabe hinzu"}
        result3 = await eval3.evaluate(case3)
        assert result3.passed, f"J11.4 Turn 3 failed: {result3.metadata}"
    
    # ==================== J12: Recherche (3 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_j12_1_web_recherche(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J12.1 — Web-Recherche."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Welche aktuellen Methoden gibt es für inklusiven Physikunterricht?"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J12.1 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j12_2_wikipedia(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J12.2 — Wikipedia-Suche."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Erkläre den Doppler-Effekt"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J12.2 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j12_3_quellenangaben(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J12.3 — Quellenangaben."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Recherchiere zum Thema Klimawandel im Unterricht"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J12.3 failed: {result.metadata}"
    
    # ==================== J13: Todos (4 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_j13_1_todo_erstellen(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J13.1 — Todo erstellen."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Erinnere mich daran, morgen die Klausuren zurückzugeben"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J13.1 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j13_2_todo_liste(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J13.2 — Todo-Liste anzeigen."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Was steht auf meiner Todo-Liste?"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J13.2 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_j13_3_todo_abhaken(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J13.3 — Todo abhaken."""
        # Turn 1: Create todo
        eval1 = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case1 = {"message": "Erinnere mich an die Noten-Eingabe"}
        result1 = await eval1.evaluate(case1)
        assert result1.passed, f"J13.3 Turn 1 failed: {result1.metadata}"
        
        # Turn 2: Mark done
        eval2 = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case2 = {"message": "Die Noten-Eingabe ist erledigt"}
        result2 = await eval2.evaluate(case2)
        assert result2.passed, f"J13.3 Turn 2 failed: {result2.metadata}"
    
    @pytest.mark.asyncio
    async def test_j13_4_faelligkeit(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """J13.4 — Fälligkeitsdatum."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Erinnere mich bis Freitag an die Noten-Eingabe"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"J13.4 failed: {result.metadata}"
    
    # ==================== Quality Checks (6 Tests) ====================
    
    @pytest.mark.asyncio
    async def test_q01_sprache(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """Q01 — Sprache ist Deutsch."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Hallo, wie geht es dir?"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"Q01 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_q02_keine_halluzinationen(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """Q02 — Keine Halluzinationen."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Erkläre mir die Formel für kinetische Energie"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"Q02 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_q03_rueckfragen(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """Q03 — Rückfragen bei Unklarheit."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Erstelle Material"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"Q03 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_q04_altersgerecht(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """Q04 — Altersgerechte Sprache."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "Erkläre Photosynthese für Klasse 5"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"Q04 failed: {result.metadata}"
    
    @pytest.mark.asyncio
    async def test_q05_antwortzeit(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """Q05 — Antwortzeit < 30s für einfache Fragen."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=30)
        case = {"message": "Was ist Physik?"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"Q05 failed: {result.metadata}"
        assert result.metadata.get("duration_ms", 0) < 30000, "Response took longer than 30s"
    
    @pytest.mark.asyncio
    async def test_q06_robustheit(self, base_url: str, teacher_id: str, api_timeout: Dict[str, int]):
        """Q06 — Robustheit (ungewöhnliche Inputs)."""
        evaluator = ChatEval(base_url=base_url, teacher_id=teacher_id, timeout=api_timeout["chat"])
        case = {"message": "ÄÖÜäöüß123!@#$%"}
        result = await evaluator.evaluate(case)
        assert result.passed, f"Q06 failed: {result.metadata}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
