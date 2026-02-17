"""Mystery-Agent — generates mystery method materials with information cards."""

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


class MysteryKarte(BaseModel):
    nummer: int
    inhalt: str
    kategorie: str  # Fakt, Hinweis, Irreführung
    schwierigkeit: str  # leicht, mittel, schwer


class MysteryStructure(BaseModel):
    titel: str
    thema: str
    leitfrage: str
    hintergrund: str
    karten: list[MysteryKarte]
    loesung: str
    differenzierung: str
    lehrkraft_hinweise: str


SYSTEM_PROMPT = """\
Du erstellst Mystery-Materialien — Schüler erschließen sich ein Thema durch Informationskarten.

## Qualitätskriterien
- Fesselnde Leitfrage, die zum Nachdenken anregt
- 15-25 Informationskarten in 3 Kategorien: Fakten, Hinweise, Irreführungen
- Fakten: ~60%, Hinweise: ~25%, Irreführungen: ~15%
- Karten müssen kombinierbar sein — kein einzelnes Kärtchen enthält die Lösung
- Differenzierung: Basis-Set (nur Fakten+Hinweise), Erweitertes Set (alle Karten)
- Realitätsbezug — Szenario aus der Lebenswelt
- Klare Lösung, die sich logisch aus den Karten ergibt

Nutze `search_curriculum_tool` und `get_good_practices_tool`."""


# Use BaseMaterialDeps directly
MysteryDeps = BaseMaterialDeps


async def _system_prompt(ctx: RunContext[MysteryDeps]) -> str:
    prompt = SYSTEM_PROMPT
    if ctx.deps.wissenskarte:
        prompt += f"\n\n{ctx.deps.wissenskarte}"
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext\n{ctx.deps.teacher_context}"
    return prompt


def create_mystery_agent() -> Agent[MysteryDeps, MysteryStructure]:
    agent = Agent(
        get_sonnet(),
        deps_type=MysteryDeps,
        output_type=MysteryStructure,
        instructions=_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[MysteryDeps], query: str) -> str:
        """Durchsuche den Lehrplan."""
        return await curriculum_search(ctx.deps.teacher_id, query)

    @agent.tool
    async def get_good_practices_tool(ctx: RunContext[MysteryDeps], thema: str) -> str:
        """Lade bewährte Mystery-Beispiele."""
        practices = await get_good_practices(ctx.deps.teacher_id, "mystery", ctx.deps.fach, thema, 2)
        if not practices:
            return "Keine Beispiele gefunden."
        return "\n".join(f"- {p.get('description', '')}" for p in practices)


    @agent.tool
    async def get_conversation_context_tool(
        ctx: RunContext[MysteryDeps], depth: str = "summary"
    ) -> str:
        """Lies den bisherigen Chat-Verlauf nach.
        depth='summary': Kompakte Übersicht (~100-200 Tokens)
        depth='full': Letzte 10 Nachrichten (~500-1000 Tokens)"""
        logger.info(f"mystery agent conversation context: depth={depth}")
        return await get_conversation_context(ctx.deps.conversation_id, depth=depth)

    @agent.tool
    async def get_teacher_preferences_tool(ctx: RunContext[MysteryDeps]) -> str:
        """Lade explizite Präferenzen dieser Lehrkraft."""
        logger.info(f"mystery agent teacher preferences")
        prefs = await get_teacher_preferences(
            teacher_id=ctx.deps.teacher_id,
            agent_type="mystery",
            fach=ctx.deps.fach,
        )
        if not prefs:
            return "Keine gespeicherten Präferenzen."
        parts = [f"- {p.get('description', '')}" for p in prefs if p.get("description")]
        return "Lehrkraft-Präferenzen:\n" + "\n".join(parts) if parts else "Keine Präferenzen."

    register_ask_teacher_tool(agent)

    return agent


_agent = None

def get_mystery_agent():
    global _agent
    if _agent is None:
        _agent = create_mystery_agent()
    return _agent
