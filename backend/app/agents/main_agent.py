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
            qr_card = json.dumps({"title": exercise_set.title, "code": access_code, "url": page_url, "qr_url": qr_url, "count": len(h5p_exercises)}, ensure_ascii=False)
            return (
                f"**{len(h5p_exercises)} Übungen** erstellt: {exercise_set.title}\n\n"
                f"```qr-card\n{qr_card}\n```"
            )
        except Exception as e:
            logger.error(f"Exercise generation failed: {e}")
            return f"Fehler bei der Übungserstellung: {str(e)}"

    # ── Tool: generate_image ──
    @agent.tool
    async def generate_image(
        ctx: RunContext[AgentDeps],
        prompt: str,
        session_id: str = "",
    ) -> str:
        """Generiere ein Bild mit KI (Gemini Imagen).

        Nutze dieses Tool wenn die Lehrkraft ein Bild braucht, z.B. für Arbeitsblätter,
        Präsentationen oder Unterrichtsmaterialien.
        - prompt: Beschreibung des gewünschten Bildes (auf Englisch für beste Ergebnisse)
        - session_id: Leer für neues Bild, oder die ID vom vorherigen Bild für Anpassungen

        Beispiel: "Erstelle ein Bild vom Wasserkreislauf" → generate_image("educational diagram of the water cycle...")
        """
        from app.agents.image_agent import generate_image as _gen
        result = await _gen(ctx.deps.teacher_id, prompt, session_id or None)

        if "error" in result:
            return f"❌ {result['error']}"

        image_id = result["image_id"]
        sid = result["session_id"]
        text = result.get("text", "")

        # Build image URL (relative, frontend will resolve)
        image_url = f"/api/images/{image_id}"

        response = f"🎨 Bild generiert!\n\n"
        response += f'```image-card\n{{"image_url": "{image_url}", "session_id": "{sid}"}}\n```'
        if text:
            response += f"\n\n{text}"
        response += f"\n\nDu kannst das Bild anpassen — sag einfach was du ändern möchtest!"
        return response

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
    async def search_wikipedia(
        ctx: RunContext[AgentDeps],
        query: str,
        lang: str = "de",
    ) -> str:
        """Durchsuche Wikipedia nach Fachinhalten für den Unterricht.
        Nutze dieses Tool für Definitionen, Erklärungen, historische Fakten,
        wissenschaftliche Konzepte und alles wo enzyklopädisches Wissen hilft.
        """
        import httpx
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Search for page
                r = await client.get(
                    f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}",
                    headers={"User-Agent": "eduhu-assistant/1.0"},
                )
                if r.status_code == 200:
                    data = r.json()
                    title = data.get("title", "")
                    extract = data.get("extract", "")
                    url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
                    return f"**{title}**\n{extract}\n\nQuelle: {url}"

                # Fallback: search API
                r2 = await client.get(
                    f"https://{lang}.wikipedia.org/w/api.php",
                    params={"action": "opensearch", "search": query, "limit": 3, "format": "json"},
                )
                results = r2.json()
                if len(results) >= 4 and results[1]:
                    titles = results[1][:3]
                    urls = results[3][:3]
                    lines = [f"- [{t}]({u})" for t, u in zip(titles, urls)]
                    return "Wikipedia-Ergebnisse:\n" + "\n".join(lines)
                return "Keine Wikipedia-Ergebnisse gefunden."
        except Exception as e:
            return f"Wikipedia-Suche fehlgeschlagen: {str(e)}"

    @agent.tool
    async def search_images(
        ctx: RunContext[AgentDeps],
        query: str,
        count: int = 3,
    ) -> str:
        """Suche lizenzfreie Bilder auf Pixabay für Unterrichtsmaterialien.
        Nutze dieses Tool wenn die Lehrkraft Bilder für Arbeitsblätter,
        Präsentationen oder Materialien braucht.
        """
        from app.config import get_settings
        import httpx
        s = get_settings()
        if not s.pixabay_api_key:
            return "Pixabay API-Key nicht konfiguriert."
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    "https://pixabay.com/api/",
                    params={
                        "key": s.pixabay_api_key,
                        "q": query,
                        "per_page": min(count, 10),
                        "lang": "de",
                        "image_type": "photo",
                        "safesearch": "true",
                    },
                )
                data = r.json()
                hits = data.get("hits", [])
                if not hits:
                    return f"Keine Bilder für '{query}' gefunden."
                lines = []
                for h in hits:
                    lines.append(f"![{h.get('tags', query)}]({h['webformatURL']})")
                    lines.append(f"  *{h.get('tags', '')}* — [Pixabay]({h['pageURL']})")
                return f"**{len(hits)} Bilder** für '{query}':\n\n" + "\n".join(lines)
        except Exception as e:
            return f"Bildersuche fehlgeschlagen: {str(e)}"

    @agent.tool
    async def classroom_tools(
        ctx: RunContext[AgentDeps],
        action: str,
        count: int = 0,
        names: str = "",
        group_size: int = 0,
    ) -> str:
        """Classroom-Tools für den Unterrichtsalltag.

        Actions:
        - "random_student": Zufällig einen Schüler aus der Liste auswählen (names = kommagetrennte Namen)
        - "groups": Schüler in Gruppen einteilen (names = kommagetrennte Namen, group_size = Gruppengröße)
        - "random_number": Zufallszahl generieren (count = max. Zahl)
        - "dice": Würfeln (count = Anzahl Würfel, default 1)
        """
        import random

        if action == "random_student":
            name_list = [n.strip() for n in names.split(",") if n.strip()]
            if not name_list:
                return "Bitte gib eine kommagetrennte Liste von Schülernamen an."
            chosen = random.choice(name_list)
            return f"🎯 **{chosen}** ist dran!"

        elif action == "groups":
            name_list = [n.strip() for n in names.split(",") if n.strip()]
            if not name_list or group_size < 1:
                return "Bitte gib Namen und eine Gruppengröße an."
            random.shuffle(name_list)
            groups = [name_list[i:i + group_size] for i in range(0, len(name_list), group_size)]
            lines = [f"**Gruppe {i+1}:** {', '.join(g)}" for i, g in enumerate(groups)]
            return "🎲 Gruppen:\n\n" + "\n".join(lines)

        elif action == "random_number":
            max_num = max(count, 10)
            return f"🎲 Zufallszahl: **{random.randint(1, max_num)}** (1-{max_num})"

        elif action == "dice":
            num_dice = min(max(count, 1), 10)
            rolls = [random.randint(1, 6) for _ in range(num_dice)]
            return f"🎲 Gewürfelt: **{' '.join(str(r) for r in rolls)}**" + (f" = {sum(rolls)}" if len(rolls) > 1 else "")

        return f"Unbekannte Aktion: {action}"

    @agent.tool
    async def set_timer(
        ctx: RunContext[AgentDeps],
        minutes: int,
        label: str = "",
    ) -> str:
        """Starte einen Countdown-Timer für die Klasse.
        Nutze dieses Tool wenn die Lehrkraft sagt: 'Timer auf 5 Minuten',
        'Stell 10 Minuten ein', 'Countdown starten', etc.
        """
        seconds = max(1, minutes) * 60
        timer_label = label or f"{minutes}-Minuten-Timer"
        return f'⏱️ **{timer_label}** gestartet!\n\n{{{{TIMER:{seconds}:{timer_label}}}}}'

    @agent.tool
    async def create_poll(
        ctx: RunContext[AgentDeps],
        question: str,
        options: str,
    ) -> str:
        """Erstelle eine Quick-Poll-Abstimmung für die Klasse.
        options: Kommagetrennte Antwortmöglichkeiten (z.B. 'Ja, Nein, Vielleicht')
        Nutze dieses Tool wenn die Lehrkraft sagt: 'Abstimmung', 'Umfrage',
        'Wer hat...?', 'Quick Poll', etc.
        """
        import random
        option_list = [o.strip() for o in options.split(",") if o.strip()]
        if len(option_list) < 2:
            return "Bitte mindestens 2 Optionen angeben."

        _NOUNS = ["tiger", "wolke", "stern", "apfel", "vogel", "blume", "stein", "welle",
                   "fuchs", "regen", "sonne", "mond", "baum", "fisch", "adler", "palme"]
        access_code = f"{random.choice(_NOUNS)}{random.randint(10, 99)}"

        poll = await db.insert("polls", {
            "teacher_id": ctx.deps.teacher_id,
            "question": question,
            "options": option_list,
            "votes": {},
            "access_code": access_code,
        })

        poll_url = f"https://eduhu-assistant.pages.dev/poll/{access_code}"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={poll_url}"

        return (
            f"📊 **Abstimmung erstellt:** {question}\n\n"
            f"Optionen: {' | '.join(f'**{o}**' for o in option_list)}\n\n"
            f"🔑 Code: **{access_code}**\n"
            f"🔗 Link: {poll_url}\n\n"
            f"📱 QR-Code:\n![QR]({qr_url})\n\n"
            f"Frag mich nach den Ergebnissen wenn alle abgestimmt haben!"
        )

    @agent.tool
    async def poll_results(
        ctx: RunContext[AgentDeps],
        access_code: str = "",
    ) -> str:
        """Zeige die Ergebnisse einer Abstimmung.
        Nutze dieses Tool wenn die Lehrkraft nach Ergebnissen einer Abstimmung fragt.
        access_code: Der Zugangscode der Abstimmung (optional — nimmt die letzte wenn leer)
        """
        if access_code:
            poll = await db.select("polls", filters={"access_code": access_code, "teacher_id": ctx.deps.teacher_id}, single=True)
        else:
            polls = await db.select("polls", filters={"teacher_id": ctx.deps.teacher_id, "active": True}, order="created_at.desc", limit=1)
            poll = polls[0] if isinstance(polls, list) and polls else None

        if not poll:
            return "Keine aktive Abstimmung gefunden."

        question = poll["question"]
        options = poll["options"] if isinstance(poll["options"], list) else []
        votes = poll["votes"] if isinstance(poll["votes"], dict) else {}

        total = sum(votes.values()) if votes else 0
        lines = []
        for opt in options:
            count = votes.get(opt, 0)
            pct = round(count / total * 100) if total > 0 else 0
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            lines.append(f"**{opt}**: {bar} {count} ({pct}%)")

        return (
            f"📊 **Ergebnisse: {question}**\n"
            f"({total} Stimmen)\n\n" + "\n".join(lines)
        )

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
                import json as _json
                card_data = [{"id": t["id"], "text": t["text"], "done": t.get("done", False), "due_date": t.get("due_date"), "priority": t.get("priority", "normal")} for t in todos]
                return f"Hier sind deine offenen Todos:\n\n```todo-card\n{_json.dumps(card_data, ensure_ascii=False)}\n```"

            elif action == "add":
                data: dict = {"text": text}
                if due_date:
                    data["due_date"] = due_date
                r = await client.post(f"{base}/api/todos", json=data, headers=headers)
                # Show updated todo list as card
                r2 = await client.get(f"{base}/api/todos?done=false", headers=headers)
                all_todos = r2.json() if r2.status_code == 200 else []
                if all_todos:
                    import json as _json
                    card_data = [{"id": t["id"], "text": t["text"], "done": t.get("done", False), "due_date": t.get("due_date"), "priority": t.get("priority", "normal")} for t in all_todos]
                    return f"✅ Todo erstellt: {text}\n\n```todo-card\n{_json.dumps(card_data, ensure_ascii=False)}\n```"
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
