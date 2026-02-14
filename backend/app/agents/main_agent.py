"""Haupt-Agent — the central chat agent using Pydantic AI."""

import logging
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
import os
from pydantic_ai.models.anthropic import AnthropicModel

from app.config import get_settings
from app.agents.system_prompt import build_system_prompt
from app.agents.curriculum_agent import curriculum_search
from app.agents.research_agent import web_search
from app import db

logger = logging.getLogger(__name__)


@dataclass
class AgentDeps:
    """Dependencies injected into the agent at runtime."""
    teacher_id: str
    conversation_id: str


def create_agent() -> Agent[AgentDeps, str]:
    """Create the main eduhu agent with tools."""
    settings = get_settings()
    # Pydantic AI reads ANTHROPIC_API_KEY from env
    os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
    model = AnthropicModel("claude-sonnet-4-20250514")

    agent = Agent(
        model,
        deps_type=AgentDeps,
        output_type=str,
        instructions=_dynamic_system_prompt,
    )

    # ── Tool: curriculum_search ──
    @agent.tool
    async def search_curriculum(ctx: RunContext[AgentDeps], query: str) -> str:
        """Durchsuche den Lehrplan der Lehrkraft nach relevanten Inhalten.
        Nutze dieses Tool wenn nach Lehrplaninhalten, Kompetenzen oder
        Unterrichtsthemen gefragt wird."""
        logger.info(f"Curriculum search: {query}")
        return await curriculum_search(ctx.deps.teacher_id, query)

    # ── Tool: web_search ──
    @agent.tool
    async def search_web(ctx: RunContext[AgentDeps], query: str) -> str:
        """Recherchiere im Internet nach aktuellen Informationen.
        Nutze dieses Tool für Fakten, aktuelle Materialien, Methoden
        oder wenn die Lehrkraft nach externen Quellen fragt."""
        logger.info(f"Web search: {query}")
        return await web_search(query)

    # ── Tool: remember ──
    @agent.tool
    async def remember(ctx: RunContext[AgentDeps], key: str, value: str) -> str:
        """Merke dir etwas Wichtiges über die Lehrkraft oder ihre Klassen.
        Nutze dieses Tool wenn die Lehrkraft explizit sagt 'merk dir...'
        oder wenn eine wichtige Präferenz/Information erwähnt wird."""
        logger.info(f"Remember: {key} = {value}")
        await db.upsert(
            "user_memories",
            {
                "user_id": ctx.deps.teacher_id,
                "scope": "self",
                "category": "explicit",
                "key": key,
                "value": value,
                "importance": 0.9,
                "source": "explicit",
            },
            on_conflict="user_id,scope,category,key",
        )
        return f"Gemerkt: {key} = {value}"

    # ── Tool: generate_material ──
    @agent.tool
    async def generate_material(
        ctx: RunContext[AgentDeps],
        fach: str,
        klasse: str,
        thema: str,
        material_type: str = "klausur",
        dauer_minuten: int = 45,
        zusatz_anweisungen: str = "",
    ) -> str:
        """Erstelle Unterrichtsmaterial als DOCX-Dokument.
        material_type MUSS einer dieser Werte sein:
        - "klausur" für Klassenarbeiten, Klausuren, Tests, Prüfungen
        - "differenzierung" für differenziertes Material (Basis/Mittel/Erweitert)
        Gibt eine Zusammenfassung mit Download-Link zurück."""
        from app.models import MaterialRequest, ExamStructure, DifferenzierungStructure
        from app.agents.material_agent import run_material_agent
        from app.docx_generator import generate_exam_docx, generate_diff_docx
        from pathlib import Path
        import uuid

        # Normalize type
        type_map = {
            "klassenarbeit": "klausur",
            "test": "klausur",
            "prüfung": "klausur",
            "pruefung": "klausur",
            "klausur": "klausur",
            "differenzierung": "differenzierung",
            "differenziert": "differenzierung",
        }
        resolved_type = type_map.get(material_type.lower(), "klausur")
        logger.info(f"Generating material: {resolved_type} (from '{material_type}') {fach} {klasse} {thema}")

        request = MaterialRequest(
            type=resolved_type,
            fach=fach,
            klasse=klasse,
            thema=thema,
            teacher_id=ctx.deps.teacher_id,
            dauer_minuten=dauer_minuten,
            zusatz_anweisungen=zusatz_anweisungen or None,
        )

        try:
            result = await run_material_agent(request)
        except Exception as e:
            logger.error(f"Material generation failed: {e}")
            return f"Fehler bei der Materialerstellung: {str(e)}"

        # Save DOCX
        materials_dir = Path("/tmp/materials")
        materials_dir.mkdir(exist_ok=True)
        material_id = str(uuid.uuid4())

        if isinstance(result, ExamStructure):
            docx_bytes = generate_exam_docx(result)
            tasks_summary = "\n".join(
                f"  {i}. {t.aufgabe} (AFB {t.afb_level}, {t.punkte}P)"
                for i, t in enumerate(result.aufgaben, 1)
            )
            summary = (
                f"✅ Klassenarbeit erstellt!\n\n"
                f"**{result.fach} — {result.thema}** (Klasse {result.klasse})\n"
                f"Dauer: {result.dauer_minuten} Min. | Gesamtpunkte: {result.gesamtpunkte}\n\n"
                f"**Aufgaben:**\n{tasks_summary}\n\n"
                f"📥 Download: /api/materials/{material_id}/docx"
            )
        elif isinstance(result, DifferenzierungStructure):
            docx_bytes = generate_diff_docx(result)
            niveaus_summary = "\n".join(
                f"  • {n.niveau}: {len(n.aufgaben)} Aufgaben, {n.zeitaufwand_minuten} Min."
                for n in result.niveaus
            )
            summary = (
                f"✅ Differenziertes Material erstellt!\n\n"
                f"**{result.fach} — {result.thema}** (Klasse {result.klasse})\n\n"
                f"**Niveaustufen:**\n{niveaus_summary}\n\n"
                f"📥 Download: /api/materials/{material_id}/docx"
            )
        else:
            return "Fehler: Unbekannter Material-Typ"

        (materials_dir / f"{material_id}.docx").write_bytes(docx_bytes)
        return summary

    return agent


async def _dynamic_system_prompt(ctx: RunContext[AgentDeps]) -> str:
    """Called by Pydantic AI before each run to build the system prompt."""
    # Load conversation summary if exists
    summary = ""
    session_log = await db.select(
        "session_logs",
        columns="summary",
        filters={"conversation_id": ctx.deps.conversation_id},
        single=True,
    )
    if session_log and isinstance(session_log, dict):
        summary = session_log.get("summary", "")

    return await build_system_prompt(ctx.deps.teacher_id, summary)


# Singleton agent instance
_agent: Agent[AgentDeps, str] | None = None


def get_agent() -> Agent[AgentDeps, str]:
    global _agent
    if _agent is None:
        _agent = create_agent()
    return _agent
