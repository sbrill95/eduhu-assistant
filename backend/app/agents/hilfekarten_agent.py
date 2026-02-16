"""Hilfekarten-Agent — generates step-by-step help cards for students."""

import logging
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app.agents.llm import get_haiku
from app.agents.knowledge import get_good_practices
from app.agents.curriculum_agent import curriculum_search

logger = logging.getLogger(__name__)


class HilfekarteStructure(BaseModel):
    titel: str
    thema: str
    niveau: str  # Basis / Erweitert / Experte
    kerninhalt: str
    hilfestellungen: list[str]
    beispiele: list[str]
    tipps: list[str]
    weiterfuehrend: str | None = None


SYSTEM_PROMPT = """\
Du erstellst kompakte Hilfekarten für Schüler — eine Seite, klar strukturiert.

## Qualitätskriterien
- Schrittweise Hilfen: Vom Einfachen zum Komplexen
- Konkrete Beispiele mit Lösungsweg
- Merksätze / Eselsbrücken als Tipps
- Niveau klar kennzeichnen (Basis/Erweitert/Experte)
- Sprache altersgerecht und ermutigend
- Max. 5-7 Hilfestellungen, 2-3 Beispiele, 2-3 Tipps

Nutze `search_curriculum_tool` für Lehrplaninhalte und `get_good_practices_tool` für bewährte Formate."""


@dataclass
class HilfekarteDeps:
    teacher_id: str
    fach: str = ""
    teacher_context: str = ""
    wissenskarte: str = ""


async def _system_prompt(ctx: RunContext[HilfekarteDeps]) -> str:
    prompt = SYSTEM_PROMPT
    if ctx.deps.wissenskarte:
        prompt += f"\n\n{ctx.deps.wissenskarte}"
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext\n{ctx.deps.teacher_context}"
    return prompt


def create_hilfekarten_agent() -> Agent[HilfekarteDeps, HilfekarteStructure]:
    agent = Agent(
        get_haiku(),
        deps_type=HilfekarteDeps,
        output_type=HilfekarteStructure,
        instructions=_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[HilfekarteDeps], query: str) -> str:
        """Durchsuche den Lehrplan nach relevanten Inhalten."""
        return await curriculum_search(ctx.deps.teacher_id, query)

    @agent.tool
    async def get_good_practices_tool(ctx: RunContext[HilfekarteDeps], thema: str) -> str:
        """Lade bewährte Hilfekarten-Beispiele."""
        practices = await get_good_practices(ctx.deps.teacher_id, "hilfekarte", ctx.deps.fach, thema, 2)
        if not practices:
            return "Keine Beispiele gefunden."
        return "\n".join(f"- {p.get('description', '')}" for p in practices)

    return agent


_agent = None

def get_hilfekarten_agent():
    global _agent
    if _agent is None:
        _agent = create_hilfekarten_agent()
    return _agent
