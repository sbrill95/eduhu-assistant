"""Haupt-Agent — the central chat agent using Pydantic AI."""

import logging
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from app.agents.llm import get_sonnet
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
    base_url: str = ""


def create_agent() -> Agent[AgentDeps, str]:
    """Create the main eduhu agent with tools."""
    model = get_sonnet()

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
        from app.services.material_service import generate_material as gen_mat

        try:
            result = await gen_mat(
                teacher_id=ctx.deps.teacher_id,
                fach=fach,
                klasse=klasse,
                thema=thema,
                material_type=material_type,
                dauer_minuten=dauer_minuten,
                zusatz_anweisungen=zusatz_anweisungen,
            )
            summary = result.summary
            if ctx.deps.base_url:
                summary = summary.replace("Download: /api/", f"[📥 Download DOCX]({ctx.deps.base_url}/api/")
                if summary != result.summary:
                    summary = summary.replace("/docx", "/docx)")
            return summary
        except Exception as e:
            logger.error(f"Material generation failed: {e}")
            return f"Fehler bei der Materialerstellung: {str(e)}"

    # ── Tool: generate_exercise ──
    @agent.tool
    async def generate_exercise(
        ctx: RunContext[AgentDeps],
        fach: str,
        klasse: str,
        thema: str,
        exercise_type: str = "auto",
        num_questions: int = 5,
    ) -> str:
        """Erstelle interaktive H5P-Übungen (Multiple Choice, Lückentext, Wahr/Falsch, Drag-Text).
        exercise_type: "multichoice", "blanks", "truefalse", "dragtext" oder "auto" (automatische Wahl).
        Die Übung wird auf einer Schüler-Seite veröffentlicht, die per Zugangscode erreichbar ist."""
        from app.agents.h5p_agent import run_h5p_agent
        from app.h5p_generator import exercise_set_to_h5p
        from app import db
        import json, uuid, random
        _NOUNS = [
            "tiger", "wolke", "stern", "apfel", "vogel", "blume", "stein", "welle", "fuchs", "regen",
            "sonne", "mond", "baum", "fisch", "adler", "birne",
        ]
        try:
            exercise_set = await run_h5p_agent(fach, klasse, thema, exercise_type, num_questions)
            h5p_content, h5p_type = exercise_set_to_h5p(exercise_set)
            title = exercise_set.title

            # Find or create exercise page for this teacher
            pages = await db.select("exercise_pages", filters={"teacher_id": ctx.deps.teacher_id}, limit=1)
            if pages and isinstance(pages, list) and len(pages) > 0:
                page = pages[0]
                page_id = page["id"]
                access_code = page["access_code"]
            else:
                page_id = str(uuid.uuid4())
                access_code = f"{random.choice(_NOUNS)}{random.randint(10, 99)}"
                await db.insert("exercise_pages", {
                    "id": page_id,
                    "teacher_id": ctx.deps.teacher_id,
                    "access_code": access_code,
                    "title": f"{fach} Klasse {klasse}",
                })

            # Insert exercise
            exercise_id = str(uuid.uuid4())
            await db.insert("exercises", {
                "id": exercise_id,
                "page_id": page_id,
                "teacher_id": ctx.deps.teacher_id,
                "title": title,
                "h5p_type": h5p_type,
                "h5p_content": h5p_content,
            })

            base = ctx.deps.base_url or ""
            page_url = f"{base}/s/{access_code}" if base else f"/s/{access_code}"
            return (
                f"Übung erstellt: **{title}**\n"
                f"Typ: {h5p_type}\n"
                f"Zugangscode: **{access_code}**\n"
                f"Link für Schüler: {page_url}\n"
            )
        except Exception as e:
            logger.error(f"Exercise generation failed: {e}")
            return f"Fehler bei der Übungserstellung: {str(e)}"

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
