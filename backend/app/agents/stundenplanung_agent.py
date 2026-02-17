"""Stundenplanung-Agent — generates lesson plans with Verlaufsplan tables."""

import logging
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app.agents.base import BaseMaterialDeps, register_ask_teacher_tool, register_ask_teacher_tool

from app.agents.llm import get_sonnet
from app.agents.knowledge import (
    get_good_practices,
    get_conversation_context,
    get_teacher_preferences,
)
from app.agents.curriculum_agent import curriculum_search

logger = logging.getLogger(__name__)


class VerlaufsplanPhase(BaseModel):
    phase: str  # Einstieg, Erarbeitung, Sicherung, etc.
    zeit_minuten: int
    lehreraktivitaet: str
    schueleraktivitaet: str
    sozialform: str  # Plenum, Einzel, Partner, Gruppe
    medien: str


class StundenplanungStructure(BaseModel):
    titel: str
    fach_thema: str
    lernziel: str
    zeitrahmen_minuten: int
    phasen: list[VerlaufsplanPhase]
    didaktische_hinweise: str
    materialien: list[str]


SYSTEM_PROMPT = """\
Du erstellst detaillierte Stundenverlaufspläne mit tabellarischer Struktur.

## Qualitätskriterien
- Logischer Aufbau: Einstieg → Erarbeitung → Sicherung (+ optional Vertiefung)
- Realistische Zeitplanung (Summe = Gesamtzeit)
- Methodenvielfalt und Sozialformenwechsel
- Schüleraktivierung > Lehrerinput
- Klar formuliertes Lernziel (beobachtbar, überprüfbar)
- Handlungsorientierung als Prinzip
- Medien/Materialien konkret benennen

Nutze `search_curriculum_tool` und `get_good_practices_tool`."""


# Use BaseMaterialDeps directly
StundenplanungDeps = BaseMaterialDeps


async def _system_prompt(ctx: RunContext[StundenplanungDeps]) -> str:
    prompt = SYSTEM_PROMPT
    if ctx.deps.wissenskarte:
        prompt += f"\n\n{ctx.deps.wissenskarte}"
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext\n{ctx.deps.teacher_context}"
    return prompt


def create_stundenplanung_agent() -> Agent[StundenplanungDeps, StundenplanungStructure]:
    agent = Agent(
        get_sonnet(),
        deps_type=StundenplanungDeps,
        output_type=StundenplanungStructure,
        instructions=_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[StundenplanungDeps], query: str) -> str:
        """Durchsuche den Lehrplan."""
        return await curriculum_search(ctx.deps.teacher_id, query)

    @agent.tool
    async def get_good_practices_tool(ctx: RunContext[StundenplanungDeps], thema: str) -> str:
        """Lade bewährte Stundenplanungen."""
        practices = await get_good_practices(ctx.deps.teacher_id, "stundenplanung", ctx.deps.fach, thema, 2)
        if not practices:
            return "Keine Beispiele gefunden."
        return "\n".join(f"- {p.get('description', '')}" for p in practices)


    @agent.tool
    async def get_conversation_context_tool(
        ctx: RunContext[StundenplanungDeps], depth: str = "summary"
    ) -> str:
        """Lies den bisherigen Chat-Verlauf nach.
        depth='summary': Kompakte Übersicht (~100-200 Tokens)
        depth='full': Letzte 10 Nachrichten (~500-1000 Tokens)"""
        logger.info(f"stundenplanung agent conversation context: depth={depth}")
        return await get_conversation_context(ctx.deps.conversation_id, depth=depth)

    @agent.tool
    async def get_teacher_preferences_tool(ctx: RunContext[StundenplanungDeps]) -> str:
        """Lade explizite Präferenzen dieser Lehrkraft."""
        logger.info(f"stundenplanung agent teacher preferences")
        prefs = await get_teacher_preferences(
            teacher_id=ctx.deps.teacher_id,
            agent_type="stundenplanung",
            fach=ctx.deps.fach,
        )
        if not prefs:
            return "Keine gespeicherten Präferenzen."
        parts = [f"- {p.get('description', '')}" for p in prefs if p.get("description")]
        return "Lehrkraft-Präferenzen:\n" + "\n".join(parts) if parts else "Keine Präferenzen."

    register_ask_teacher_tool(agent)

    return agent


_agent = None

def get_stundenplanung_agent():
    global _agent
    if _agent is None:
        _agent = create_stundenplanung_agent()
    return _agent
