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

## Anforderungsbereiche (AFB)
- **AFB I (Reproduktion):** Wiedergeben, Nennen, Beschreiben — ca. 30% der Punkte
- **AFB II (Reorganisation/Transfer):** Erklären, Vergleichen, Analysieren — ca. 40% der Punkte
- **AFB III (Reflexion/Problemlösung):** Beurteilen, Bewerten, Gestalten — ca. 30% der Punkte

## Regeln
- Jede Aufgabe hat eine klare Operatorenformulierung
- Erwartungshorizont: Stichpunktartig, was für volle Punktzahl erwartet wird
- Notenschlüssel: Standard (sehr gut ab 87%, gut ab 73%, befriedigend ab 59%, ausreichend ab 45%, mangelhaft ab 20%, ungenügend unter 20%)
- Hinweise: Erlaubte Hilfsmittel, Bearbeitungszeit, allgemeine Hinweise
- Sprache: Deutsch, klar und präzise
- Aufgaben aufsteigend nach Schwierigkeit ordnen

Erstelle eine vollständige, realistische Klassenarbeit mit allen Bestandteilen.
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
