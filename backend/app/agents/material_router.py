"""Material Router — routes material generation requests to sub-agents.

Returns dict with type: "material" | "clarification"
Supports session continuation with message_history.
"""

import asyncio
import logging
import uuid
from typing import Any

from pydantic_ai.messages import ModelMessage

from app import db
from app.config import get_settings
from app.models import MaterialRequest
from app.agents.base import BaseMaterialDeps, ClarificationNeededError
from app.agents.klausur_agent import get_klausur_agent, KlausurDeps
from app.agents.differenzierung_agent import get_diff_agent, DiffDeps
from app.agents.hilfekarten_agent import get_hilfekarten_agent, HilfekarteDeps
from app.agents.escape_room_agent import get_escape_room_agent, EscapeRoomDeps
from app.agents.mystery_agent import get_mystery_agent, MysteryDeps
from app.agents.lernsituation_agent import get_lernsituation_agent, LernsituationDeps
from app.agents.lernspiel_agent import get_lernspiel_agent, LernspielDeps
from app.agents.versuchsanleitung_agent import get_versuchsanleitung_agent, VersuchsanleitungDeps
from app.agents.stundenplanung_agent import get_stundenplanung_agent, StundenplanungDeps
from app.agents.podcast_agent import get_podcast_agent, PodcastDeps
from app.agents.gespraechssimulation_agent import get_gespraechssimulation_agent, GespraechssimulationDeps
from app.agents.system_prompt import build_block3_context
from app.agents.knowledge import build_wissenskarte

logger = logging.getLogger(__name__)

SUPPORTED_TYPES = {
    "klausur", "klassenarbeit", "differenzierung",
    "hilfekarte", "escape_room", "mystery",
    "lernsituation", "lernspiel", "versuchsanleitung",
    "stundenplanung", "podcast", "gespraechssimulation",
}

TYPE_ALIASES = {
    "klassenarbeit": "klausur",
    "arbeitsblatt": "versuchsanleitung",
    "experiment": "versuchsanleitung",
    "unterrichtsplanung": "stundenplanung",
    "verlaufsplan": "stundenplanung",
}


def _normalize_type(material_type: str) -> str:
    t = material_type.lower().strip()
    return TYPE_ALIASES.get(t, t)


def _is_retryable(exc: Exception) -> bool:
    name = type(exc).__name__
    return any(
        keyword in name.lower() or keyword in str(exc).lower()
        for keyword in ("timeout", "connection", "server", "502", "503", "529", "429", "rate", "overloaded")
    )


def _get_agent_and_deps(material_type: str, common_deps: dict):
    """Return (agent, deps) for a given material type."""
    dispatch = {
        "klausur": (get_klausur_agent, KlausurDeps),
        "differenzierung": (get_diff_agent, DiffDeps),
        "hilfekarte": (get_hilfekarten_agent, HilfekarteDeps),
        "escape_room": (get_escape_room_agent, EscapeRoomDeps),
        "mystery": (get_mystery_agent, MysteryDeps),
        "lernsituation": (get_lernsituation_agent, LernsituationDeps),
        "lernspiel": (get_lernspiel_agent, LernspielDeps),
        "versuchsanleitung": (get_versuchsanleitung_agent, VersuchsanleitungDeps),
        "stundenplanung": (get_stundenplanung_agent, StundenplanungDeps),
        "podcast": (get_podcast_agent, PodcastDeps),
        "gespraechssimulation": (get_gespraechssimulation_agent, GespraechssimulationDeps),
    }
    if material_type not in dispatch:
        raise ValueError(f"Kein Agent für Typ '{material_type}'")
    get_agent, deps_cls = dispatch[material_type]
    return get_agent(), deps_cls(**common_deps)


def _serialize_messages(messages: list[ModelMessage]) -> list[dict]:
    """Serialize pydantic-ai messages to JSON-safe dicts."""
    result = []
    for msg in messages:
        try:
            if hasattr(msg, "model_dump"):
                result.append(msg.model_dump(mode="json"))
            else:
                result.append({"kind": "unknown", "content": str(msg)})
        except Exception as e:
            logger.debug(f"Could not serialize message: {e}")
    return result


def _deserialize_messages(data: list[dict]) -> list[ModelMessage] | None:
    """Deserialize messages back. Returns None on failure (session expired)."""
    if not data:
        return None
    try:
        from pydantic_ai.messages import ModelMessage
        results = []
        for d in data:
            kind = d.get("kind", "")
            # Use pydantic-ai's model_validate for each message type
            if kind == "request":
                from pydantic_ai.messages import ModelRequest
                results.append(ModelRequest.model_validate(d))
            elif kind == "response":
                from pydantic_ai.messages import ModelResponse
                results.append(ModelResponse.model_validate(d))
            else:
                logger.warning(f"Unknown message kind: {kind}")
        return results if results else None
    except Exception as e:
        logger.warning(f"Message deserialization failed (session expired): {e}")
        return None


async def run_material_agent(request: MaterialRequest) -> dict[str, Any]:
    """Route to the correct sub-agent. Returns dict with type and payload.
    
    Returns:
        {"type": "material", "output": <structure>, "session_id": str, "message_history": [...]}
        {"type": "clarification", "question": str, "session_id": str, "message_history": [...]}
    """
    material_type = _normalize_type(request.type)

    if material_type not in SUPPORTED_TYPES:
        raise ValueError(
            f"Material-Typ '{request.type}' wird nicht unterstützt. "
            f"Verfügbar: {', '.join(sorted(SUPPORTED_TYPES))}"
        )

    settings = get_settings()
    timeout = settings.sub_agent_timeout_seconds
    max_retries = settings.sub_agent_max_retries

    teacher_context = await build_block3_context(request.teacher_id)
    wissenskarte = await build_wissenskarte(request.teacher_id, material_type, request.fach)

    prompt = _build_prompt(request, material_type)

    common_deps = dict(
        teacher_id=request.teacher_id,
        conversation_id=request.conversation_id,
        fach=request.fach,
        teacher_context=teacher_context,
        wissenskarte=wissenskarte,
    )

    agent, deps = _get_agent_and_deps(material_type, common_deps)

    logger.info(f"Running {material_type} agent: {request.fach} {request.klasse} {request.thema}")

    session_id = str(uuid.uuid4())

    last_error: Exception | None = None
    for attempt in range(1 + max_retries):
        try:
            result = await asyncio.wait_for(
                agent.run(prompt, deps=deps),
                timeout=timeout,
            )
            messages = _serialize_messages(result.all_messages())

            # Save session
            await _save_session(
                session_id=session_id,
                conversation_id=request.conversation_id,
                teacher_id=request.teacher_id,
                agent_type=material_type,
                material_structure=result.output.model_dump() if hasattr(result.output, "model_dump") else {},
                message_history=messages,
            )

            return {
                "type": "material",
                "output": result.output,
                "session_id": session_id,
                "message_history": messages,
            }
        except ClarificationNeededError as e:
            # Agent needs more info — save partial state and return question
            messages = _serialize_messages(e.message_history) if e.message_history else []
            await _save_session(
                session_id=session_id,
                conversation_id=request.conversation_id,
                teacher_id=request.teacher_id,
                agent_type=material_type,
                material_structure={},
                message_history=messages,
                status="clarification",
            )
            return {
                "type": "clarification",
                "question": e.question,
                "session_id": session_id,
                "message_history": messages,
            }
        except asyncio.TimeoutError:
            logger.warning(f"{material_type} agent timeout, Versuch {attempt + 1}")
            last_error = TimeoutError(f"{material_type}-Agent hat nach {timeout}s nicht geantwortet")
        except Exception as e:
            if _is_retryable(e) and attempt < max_retries:
                logger.warning(f"{material_type} agent error (retryable), Versuch {attempt + 1}: {e}")
                await asyncio.sleep(2 ** attempt)
                last_error = e
            else:
                raise

    raise last_error  # type: ignore[misc]


async def continue_agent_session(session_id: str, user_input: str) -> dict[str, Any]:
    """Continue an existing agent session (after clarification or for iteration).
    
    Returns same dict format as run_material_agent.
    """
    # Load session
    session = await db.select(
        "agent_sessions",
        filters={"id": session_id},
        single=True,
    )
    if not session:
        raise ValueError("Session nicht gefunden. Bitte starte eine neue Materialerstellung.")

    agent_type = session.get("agent_type", "klausur")
    conversation_id = session.get("conversation_id", "")
    teacher_id = session.get("teacher_id", "")

    # Restore message history
    raw_history = session.get("message_history", [])
    message_history = _deserialize_messages(raw_history)
    if message_history is None:
        raise ValueError("Session abgelaufen. Bitte starte eine neue Materialerstellung.")

    # Build deps
    settings = get_settings()
    teacher_context = await build_block3_context(teacher_id)
    wissenskarte = await build_wissenskarte(teacher_id, agent_type, session.get("fach", ""))

    common_deps = dict(
        teacher_id=teacher_id,
        conversation_id=conversation_id,
        fach=session.get("material_structure", {}).get("fach", ""),
        teacher_context=teacher_context,
        wissenskarte=wissenskarte,
    )

    agent, deps = _get_agent_and_deps(agent_type, common_deps)

    logger.info(f"Continuing {agent_type} session {session_id}: {user_input[:100]}")

    try:
        result = await asyncio.wait_for(
            agent.run(user_input, deps=deps, message_history=message_history),
            timeout=settings.sub_agent_timeout_seconds,
        )
        messages = _serialize_messages(result.all_messages())

        # Update session
        structure = result.output.model_dump() if hasattr(result.output, "model_dump") else {}
        await db.update(
            "agent_sessions",
            {
                "material_structure": structure,
                "message_history": messages,
                "status": "active",
                "updated_at": "now()",
            },
            filters={"id": session_id},
        )

        return {
            "type": "material",
            "output": result.output,
            "session_id": session_id,
            "message_history": messages,
        }
    except ClarificationNeededError as e:
        messages = _serialize_messages(e.message_history) if e.message_history else []
        await db.update(
            "agent_sessions",
            {
                "message_history": messages,
                "status": "clarification",
                "updated_at": "now()",
            },
            filters={"id": session_id},
        )
        return {
            "type": "clarification",
            "question": e.question,
            "session_id": session_id,
            "message_history": messages,
        }


async def _save_session(
    session_id: str,
    conversation_id: str,
    teacher_id: str,
    agent_type: str,
    material_structure: dict,
    message_history: list,
    status: str = "active",
) -> None:
    """Save a new agent session."""
    try:
        data = {
            "teacher_id": teacher_id,
            "agent_type": agent_type,
            "material_structure": material_structure,
            "status": status,
            "state": {},
        }
        if session_id:
            data["id"] = session_id
        if conversation_id:
            data["conversation_id"] = conversation_id
        # message_history: try with it first, fall back without
        if message_history:
            data["message_history"] = message_history
        result = await db.insert("agent_sessions", data)
        logger.info(f"Session saved: {session_id}")
    except Exception as e:
        # Retry without message_history (PostgREST schema cache may be stale)
        if "message_history" in data:
            try:
                data.pop("message_history")
                await db.insert("agent_sessions", data)
                logger.info(f"Session saved (without message_history): {session_id}")
                return
            except Exception:
                pass
        logger.error(f"Failed to save session {session_id}: {e}")


def _build_prompt(request: MaterialRequest, material_type: str) -> str:
    """Build the generation prompt from the request."""
    type_labels = {
        "klausur": "eine Klassenarbeit/Klausur",
        "differenzierung": "differenziertes Material in 3 Niveaustufen",
        "hilfekarte": "eine Hilfekarte für Schüler",
        "escape_room": "einen Escape Room für den Unterricht",
        "mystery": "ein Mystery-Material mit Informationskarten",
        "lernsituation": "eine Lernsituation für die berufliche Bildung",
        "lernspiel": "ein Lernspiel",
        "versuchsanleitung": "eine Versuchsanleitung / ein Arbeitsblatt",
        "stundenplanung": "einen Stundenverlaufsplan",
        "podcast": "ein Podcast-Skript",
        "gespraechssimulation": "eine Gesprächssimulation",
    }

    parts = [
        f"Erstelle {type_labels.get(material_type, material_type)}:",
        f"- Fach: {request.fach}",
        f"- Klasse/Jahrgang: {request.klasse}",
        f"- Thema: {request.thema}",
    ]
    if request.dauer_minuten:
        parts.append(f"- Dauer/Zeitrahmen: {request.dauer_minuten} Minuten")
    if request.afb_verteilung:
        parts.append(f"- AFB-Verteilung: {request.afb_verteilung}")
    if request.zusatz_anweisungen:
        parts.append(f"- Zusätzliche Anweisungen: {request.zusatz_anweisungen}")

    return "\n".join(parts)
