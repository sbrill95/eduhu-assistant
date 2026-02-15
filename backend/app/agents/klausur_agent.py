"""Klausur-Agent — generates structured exams with AFB I-III tasks."""

import logging
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from app.agents.llm import get_haiku
from app.models import ExamStructure
from app.agents.curriculum_agent import curriculum_search

logger = logging.getLogger(__name__)

KLAUSUR_SYSTEM_PROMPT = """\
Du bist ein Experte für die Erstellung von Klassenarbeiten und Klausuren im deutschen Schulsystem.

## Anforderungsbereiche (AFB) — KORREKTE Zuordnung ist KRITISCH!

### AFB I (Reproduktion) — ca. 30% der Punkte
Operatoren: Nennen, Angeben, Beschreiben, Wiedergeben, Definieren, Darstellen, Aufzählen
Beispiel: "Nenne drei Eigenschaften des Lichts." / "Beschreibe den Aufbau eines Prismas."
→ Wissen abrufen und wiedergeben, KEIN Erklären oder Begründen!

### AFB II (Reorganisation/Transfer) — ca. 40% der Punkte
Operatoren: Erklären, Erläutern, Vergleichen, Anwenden, Berechnen, Analysieren, Einordnen, Zuordnen
Beispiel: "Erklären Sie das Zustandekommen der Totalreflexion." / "Berechnen Sie den Brechungswinkel."
→ Gelerntes auf neue Situationen anwenden, Zusammenhänge herstellen.
WICHTIG: "Erklären" und "Erläutern" sind AFB II, NICHT AFB III!

### AFB III (Reflexion/Problemlösung) — ca. 30% der Punkte
Operatoren: Beurteilen, Bewerten, Stellung nehmen, Diskutieren, Entwickeln, Entwerfen, Überprüfen
Beispiel: "Beurteilen Sie die Eignung von Glasfaserkabeln gegenüber Kupferkabeln." / "Entwickeln Sie einen Versuchsaufbau."
→ Eigenständig urteilen, begründet Position beziehen, kreativ Lösungen entwickeln.

## KRITISCHE REGELN
- AFB-Verteilung MUSS bei ca. 30% I / 40% II / 30% III liegen. NICHT mehr als 35% AFB III!
- Ordne Operatoren KORREKT zu: "Erklären" = AFB II, "Beurteilen" = AFB III
- Zeitbudget: Klasse 5-10: ca. 1 Punkt pro Minute. 45 Min → 40-45 Punkte, NICHT mehr!
- Klasse 11-13: ca. 1-1.2 Punkte pro Minute.
- Mindestens 4 Aufgaben, besser 5-6 (auch Teilaufgaben a/b/c zählen)
- Jede Aufgabe MUSS konkrete Angaben enthalten:
  - Bei Berechnungen: Konkrete Zahlenwerte angeben!
  - Bei Erklärungen: Klar definiertes Phänomen benennen, nicht vage!
  - Teilaufgaben (a, b, c) mit einzelnen Punktwerten
- Erwartungshorizont: Pro Teilaufgabe mind. 3-4 Stichpunkte, bei Berechnungen den Lösungsweg
- Notenschlüssel: Standard (sehr gut ab 87%, gut ab 73%, befriedigend ab 59%, ausreichend ab 45%, mangelhaft ab 20%, ungenügend unter 20%)
- Hinweise: Erlaubte Hilfsmittel, Bearbeitungszeit, allgemeine Hinweise
- Sprache: Deutsch, klar und präzise
- Aufgaben aufsteigend nach Schwierigkeit ordnen (AFB I → AFB II → AFB III)

Erstelle eine vollständige, realistische Klassenarbeit mit allen Bestandteilen.
PRÜFE VOR DER AUSGABE: Stimmt die AFB-Verteilung? Sind alle Aufgaben konkret genug? Passt das Zeitbudget?
"""


@dataclass
class KlausurDeps:
    teacher_id: str
    teacher_context: str = ""


async def _klausur_system_prompt(ctx: RunContext[KlausurDeps]) -> str:
    prompt = KLAUSUR_SYSTEM_PROMPT
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext der Lehrkraft\n{ctx.deps.teacher_context}"
    return prompt


def create_klausur_agent() -> Agent[KlausurDeps, ExamStructure]:
    model = get_haiku()

    agent = Agent(
        model,
        deps_type=KlausurDeps,
        output_type=ExamStructure,
        instructions=_klausur_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[KlausurDeps], query: str) -> str:
        """Durchsuche den Lehrplan nach relevanten Inhalten für die Klausur."""
        logger.info(f"Klausur agent curriculum search: {query}")
        return await curriculum_search(ctx.deps.teacher_id, query)

    return agent


_klausur_agent: Agent[KlausurDeps, ExamStructure] | None = None


def get_klausur_agent() -> Agent[KlausurDeps, ExamStructure]:
    global _klausur_agent
    if _klausur_agent is None:
        _klausur_agent = create_klausur_agent()
    return _klausur_agent
