"""Differenzierungs-Agent — generates multi-level differentiated materials."""

import logging
import os
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.anthropic import AnthropicModel

from app.config import get_settings
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


@dataclass
class DiffDeps:
    teacher_id: str


def create_diff_agent() -> Agent[DiffDeps, DifferenzierungStructure]:
    settings = get_settings()
    os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
    model = AnthropicModel("claude-3-5-haiku-20241022")

    agent = Agent(
        model,
        deps_type=DiffDeps,
        output_type=DifferenzierungStructure,
        system_prompt=DIFF_SYSTEM_PROMPT,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[DiffDeps], query: str) -> str:
        """Durchsuche den Lehrplan nach relevanten Inhalten."""
        logger.info(f"Differenzierung agent curriculum search: {query}")
        return await curriculum_search(ctx.deps.teacher_id, query)

    return agent


_diff_agent: Agent[DiffDeps, DifferenzierungStructure] | None = None


def get_diff_agent() -> Agent[DiffDeps, DifferenzierungStructure]:
    global _diff_agent
    if _diff_agent is None:
        _diff_agent = create_diff_agent()
    return _diff_agent
