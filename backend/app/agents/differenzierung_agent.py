"""Differenzierungs-Agent — generates multi-level differentiated materials."""

import logging

from pydantic_ai import Agent, RunContext

from app.agents.base import BaseMaterialDeps, register_ask_teacher_tool, DIRECT_GENERATION_DIRECTIVE
from app.agents.knowledge import (
    get_good_practices,
    get_conversation_context,
    get_teacher_preferences,
)

from app.agents.llm import get_haiku
from app.models import DifferenzierungStructure
from app.agents.curriculum_agent import curriculum_search

logger = logging.getLogger(__name__)

DIFF_SYSTEM_PROMPT = """\
Du bist ein Experte für binnendifferenziertes Unterrichtsmaterial im deutschen Schulsystem.

## Niveaustufen
Du erstellst Material in drei Niveaustufen:

### Basis (Grundniveau)
- Einfache Sprache, kurze Sätze
- Scaffolding: Schritt-für-Schritt-Anleitungen, Lückentexte, Zuordnungsaufgaben
- Hilfestellungen: Wortlisten, Beispielantworten, visuelle Hilfen
- Fokus auf AFB I (Reproduktion)

### Mittel (Regelniveau)
- Standardsprache, moderate Komplexität
- Mix aus gelenkten und offenen Aufgaben
- Einige Hilfestellungen, aber mehr Eigenleistung
- Fokus auf AFB I + II

### Erweitert (Expertenniveau)
- Anspruchsvolle Sprache, komplexe Zusammenhänge
- Offene, transferorientierte Aufgaben
- Minimale Hilfestellung, hohe Eigenleistung
- Fokus auf AFB II + III

## Regeln
- Alle drei Niveaus behandeln DASSELBE Thema
- Aufgabenstellungen verwenden passende Operatoren
- Basis-Aufgaben sind NICHT einfach gekürzte Erweitert-Aufgaben — sie sind anders konzipiert
- Jede Niveaustufe hat 3-5 Aufgaben
- Zeitaufwand pro Niveau angeben
- Sprache: Deutsch, klar und schülergerecht
"""


# Use BaseMaterialDeps directly
DiffDeps = BaseMaterialDeps


async def _diff_system_prompt(ctx: RunContext[DiffDeps]) -> str:
    prompt = DIFF_SYSTEM_PROMPT + DIRECT_GENERATION_DIRECTIVE
    if ctx.deps.wissenskarte:
        prompt += f"\n\n{{ctx.deps.wissenskarte}}"
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext der Lehrkraft\n{ctx.deps.teacher_context}"
    return prompt


def create_diff_agent() -> Agent[DiffDeps, DifferenzierungStructure]:
    model = get_haiku()

    agent = Agent(
        model,
        deps_type=DiffDeps,
        output_type=DifferenzierungStructure,
        instructions=_diff_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[DiffDeps], query: str) -> str:
        """Durchsuche den Lehrplan nach relevanten Inhalten."""
        logger.info(f"Differenzierung agent curriculum search: {query}")
        return await curriculum_search(ctx.deps.teacher_id, query)

    @agent.tool
    async def get_good_practices_tool(ctx: RunContext[DiffDeps], thema: str) -> str:
        """Lade bewährte Differenzierungs-Beispiele aus der Wissensdatenbank."""
        logger.info(f"Differenzierung agent good practices: {thema}")
        practices = await get_good_practices(
            teacher_id=ctx.deps.teacher_id,
            agent_type="differenzierung",
            fach=ctx.deps.fach,
            thema=thema,
            limit=2,
        )
        if not practices:
            return "Keine bewährten Beispiele gefunden."
        parts = []
        for p in practices:
            desc = p.get("description", "")
            score = p.get("quality_score", 0)
            parts.append(f"- {desc} (Qualität: {score:.1f})")
        return "\n".join(parts)

    @agent.tool
    async def get_conversation_context_tool(
        ctx: RunContext[DiffDeps], depth: str = "summary"
    ) -> str:
        """Lies den bisherigen Chat-Verlauf nach.
        depth='summary': Kompakte Übersicht (~100-200 Tokens)
        depth='full': Letzte 10 Nachrichten (~500-1000 Tokens)"""
        logger.info(f"differenzierung agent conversation context: depth={depth}")
        return await get_conversation_context(ctx.deps.conversation_id, depth=depth)

    @agent.tool
    async def get_teacher_preferences_tool(ctx: RunContext[DiffDeps]) -> str:
        """Lade explizite Präferenzen dieser Lehrkraft."""
        logger.info(f"differenzierung agent teacher preferences")
        prefs = await get_teacher_preferences(
            teacher_id=ctx.deps.teacher_id,
            agent_type="differenzierung",
            fach=ctx.deps.fach,
        )
        if not prefs:
            return "Keine gespeicherten Präferenzen."
        parts = [f"- {p.get('description', '')}" for p in prefs if p.get("description")]
        return "Lehrkraft-Präferenzen:\n" + "\n".join(parts) if parts else "Keine Präferenzen."

    register_ask_teacher_tool(agent)

    return agent


_diff_agent: Agent[DiffDeps, DifferenzierungStructure] | None = None


def get_diff_agent() -> Agent[DiffDeps, DifferenzierungStructure]:
    global _diff_agent
    if _diff_agent is None:
        _diff_agent = create_diff_agent()
    return _diff_agent
