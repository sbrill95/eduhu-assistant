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
            h5p_exercises = exercise_set_to_h5p(exercise_set)

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

            # Insert each question as separate exercise
            for h5p_content, h5p_type, title in h5p_exercises:
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
            page_url = f"https://eduhu-assistant.pages.dev/s/{access_code}"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={page_url}"
            return (
                f"**{len(h5p_exercises)} Übungen** erstellt: {exercise_set.title}\n\n"
                f"🔑 Zugangscode: **{access_code}**\n"
                f"🔗 Link für Schüler: {page_url}\n\n"
                f"📱 QR-Code zum Ausdrucken/Teilen:\n![QR-Code]({qr_url})"
            )
        except Exception as e:
            logger.error(f"Exercise generation failed: {e}")
            return f"Fehler bei der Übungserstellung: {str(e)}"

    # ── Tool: patch_material_task ──
    @agent.tool
    async def patch_material_task(
        ctx: RunContext[AgentDeps],
        material_id: str,
        task_index: int,
        anweisung: str,
    ) -> str:
        """Ändere eine EINZELNE Aufgabe in einer bestehenden Klausur.
        Nutze dieses Tool wenn die Lehrkraft sagt 'ändere Aufgabe X', 'mach Aufgabe X schwieriger/leichter',
        oder eine bestimmte Aufgabe überarbeiten möchte.
        task_index ist 0-basiert (Aufgabe 1 = Index 0, Aufgabe 2 = Index 1, etc.).
        Die restlichen Aufgaben bleiben EXAKT IDENTISCH — nur die genannte wird ersetzt."""
        import httpx
        base = ctx.deps.base_url or "http://localhost:8000"
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.patch(
                    f"{base}/api/materials/{material_id}/task/{task_index}",
                    params={"teacher_id": ctx.deps.teacher_id, "anweisung": anweisung},
                )
                if r.status_code != 200:
                    return f"Fehler beim Ändern der Aufgabe: {r.text[:200]}"
                data = r.json()
                alte = data["alte_aufgabe"]
                neue = data["neue_aufgabe"]
                dl = f"{base}/api/materials/{data['material_id']}/docx" if base else data["docx_url"]
                return (
                    f"Aufgabe {task_index + 1} wurde geändert. Alle anderen Aufgaben sind unverändert.\n\n"
                    f"**Vorher:** {alte.get('aufgabe','')} (AFB {alte.get('afb_level','')}, {alte.get('punkte',0)}P)\n"
                    f"**Nachher:** {neue.get('aufgabe','')} (AFB {neue.get('afb_level','')}, {neue.get('punkte',0)}P)\n"
                    f"Beschreibung: {neue.get('beschreibung','')}\n\n"
                    f"[📥 Aktualisierte Klausur herunterladen]({dl})"
                )
        except Exception as e:
            logger.error(f"Patch material task failed: {e}")
            return f"Fehler: {str(e)}"

    @agent.tool
    async def manage_todos(
        ctx: RunContext[AgentDeps],
        action: str,
        text: str = "",
        due_date: str = "",
        todo_id: str = "",
    ) -> str:
        """Verwalte die To-Do-Liste der Lehrkraft.

        Actions:
        - "list": Zeige alle offenen Todos
        - "add": Neues Todo erstellen (text required, due_date optional als YYYY-MM-DD)
        - "complete": Todo als erledigt markieren (todo_id required)
        - "delete": Todo löschen (todo_id required)

        Nutze dieses Tool wenn die Lehrkraft sagt: 'erinnere mich an...', 'ich muss noch...',
        'todo:', 'was steht an?', 'was muss ich noch machen?', oder ähnlich.
        """
        teacher_id = ctx.deps.teacher_id
        base = ctx.deps.base_url or "http://localhost:8000"

        import httpx
        headers = {"Content-Type": "application/json", "X-Teacher-ID": teacher_id}

        async with httpx.AsyncClient(timeout=15.0) as client:
            if action == "list":
                r = await client.get(f"{base}/api/todos?done=false", headers=headers)
                todos = r.json()
                if not todos:
                    return "Keine offenen Todos vorhanden. 🎉"
                lines = []
                for t in todos:
                    due = f" (bis {t['due_date']})" if t.get("due_date") else ""
                    prio = " ⚠️" if t.get("priority") == "high" else ""
                    lines.append(f"- [{t['id'][:8]}] {t['text']}{due}{prio}")
                return "Offene Todos:\n" + "\n".join(lines)

            elif action == "add":
                data: dict = {"text": text}
                if due_date:
                    data["due_date"] = due_date
                r = await client.post(f"{base}/api/todos", json=data, headers=headers)
                return f"✅ Todo erstellt: {text}" + (f" (bis {due_date})" if due_date else "")

            elif action == "complete":
                r = await client.patch(
                    f"{base}/api/todos/{todo_id}", json={"done": True}, headers=headers
                )
                return "Todo erledigt! ✅"

            elif action == "delete":
                r = await client.delete(f"{base}/api/todos/{todo_id}", headers=headers)
                return "Todo gelöscht."

            return f"Unbekannte Aktion: {action}"

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
