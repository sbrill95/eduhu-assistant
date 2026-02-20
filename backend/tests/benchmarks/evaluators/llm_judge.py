"""LLM Judge Evaluator — Haiku bewertet Agent-Output inhaltlich."""

import os
import json
import httpx
from typing import Optional


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
JUDGE_MODEL = "claude-haiku-4-5-20251001"


async def judge(content: str, criteria: str, context: dict | None = None) -> dict:
    """
    Ask Haiku to evaluate content against criteria.
    
    Returns: {"score": 1-5, "passed": bool, "reason": str, "details": dict}
    Score: 1=schlecht, 2=mangelhaft, 3=akzeptabel, 4=gut, 5=sehr gut
    Passed: score >= 3
    """
    context_str = ""
    if context:
        context_str = f"\n\nKontext:\n- Fach: {context.get('fach', '?')}\n- Klasse: {context.get('klasse', '?')}\n- Thema: {context.get('thema', '?')}\n- Typ: {context.get('type', '?')}"

    prompt = f"""Du bist ein strenger Qualitätsprüfer für KI-generierte Lehrmaterialien.

Bewerte den folgenden Output anhand dieser Kriterien:
{criteria}
{context_str}

OUTPUT:
{content[:8000]}

Antworte AUSSCHLIESSLICH als JSON (kein Markdown, kein Text davor/danach):
{{
  "score": <1-5>,
  "passed": <true wenn score >= 3>,
  "reason": "<1-2 Sätze Begründung>",
  "strengths": ["<Stärke 1>", "<Stärke 2>"],
  "weaknesses": ["<Schwäche 1>", "<Schwäche 2>"]
}}"""

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": JUDGE_MODEL,
                    "max_tokens": 512,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            
            if r.status_code != 200:
                return {"score": 0, "passed": False, "reason": f"Judge API Error: {r.status_code}", "details": {}}

            text = r.json()["content"][0]["text"].strip()
            # Strip markdown wrapping if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            
            result = json.loads(text)
            result["passed"] = result.get("score", 0) >= 3
            return result

    except Exception as e:
        return {"score": 0, "passed": False, "reason": f"Judge Error: {e}", "details": {}}


# === Vorgefertigte Kriterien für verschiedene Material-Typen ===

CRITERIA_KLAUSUR = """
1. AFB-Verteilung: Sind Aufgaben aller 3 Anforderungsbereiche (I: Reproduktion, II: Transfer, III: Reflexion) vorhanden?
2. Fachliche Korrektheit: Sind die Inhalte zum Thema korrekt?
3. Altersangemessenheit: Passt der Schwierigkeitsgrad zur angegebenen Klassenstufe?
4. Vollständigkeit: Gibt es einen Erwartungshorizont / Musterlösungen / Punkteverteilung?
5. Struktur: Ist die Klausur klar gegliedert (Aufgabennummern, Punktangaben)?
"""

CRITERIA_DIFFERENZIERUNG = """
1. Drei Niveaus: Sind mindestens 3 klar unterscheidbare Schwierigkeitsstufen vorhanden?
2. Gleicher Kerninhalt: Behandeln alle Niveaus dasselbe Thema?
3. Progression: Steigt der Schwierigkeitsgrad erkennbar an?
4. Altersangemessenheit: Passt das einfachste Niveau zur Klassenstufe?
5. Didaktische Qualität: Sind die Aufgaben sinnvoll und lernförderlich?
"""

CRITERIA_STUNDENPLANUNG = """
1. Phasenstruktur: Enthält die Planung Einstieg, Erarbeitung, Sicherung (oder ähnlich)?
2. Zeitangaben: Sind Zeitangaben (Minuten) für jede Phase vorhanden?
3. Methodenvielfalt: Werden verschiedene Sozialformen/Methoden genutzt?
4. Lernziele: Sind Lernziele oder Kompetenzen benannt?
5. Praxistauglichkeit: Ist die Planung realistisch umsetzbar?
"""

CRITERIA_H5P = """
1. Fachbezug: Beziehen sich die Fragen/Übungen auf das angegebene Thema?
2. Altersangemessenheit: Passt der Schwierigkeitsgrad zur Klassenstufe?
3. Didaktische Qualität: Sind die Fragen/Aufgaben lernförderlich (nicht nur Faktenwissen)?
4. Vielfalt: Gibt es verschiedene Fragetypen oder Aufgabenformate?
5. Korrektheit: Sind die Lösungen / richtigen Antworten korrekt?
"""

CRITERIA_CHAT = """
1. Relevanz: Geht die Antwort auf die Frage ein?
2. Sprache: Ist die Antwort auf Deutsch und verständlich formuliert?
3. Hilfsbereitschaft: Bietet die Antwort konkreten Mehrwert für Lehrkräfte?
4. Tonalität: Ist der Ton professionell aber freundlich (nicht roboterhaft)?
5. Vollständigkeit: Beantwortet die Antwort die Frage ausreichend?
"""

CRITERIA_MEMORY = """
1. Bestätigung: Wird das Merken/Speichern bestätigt?
2. Kontext: Wird auf den gespeicherten Inhalt Bezug genommen?
3. Natürlichkeit: Klingt die Antwort natürlich und nicht generisch?
"""
