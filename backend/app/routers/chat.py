from fastapi import APIRouter, HTTPException, Request, Depends
from starlette.responses import StreamingResponse
from app import db
from app.models import (
    ChatRequest, ChatResponse, ChatMessageOut, ConversationOut,
)
from app.agents.main_agent import get_agent, AgentDeps
from app.agents.memory_agent import run_memory_agent
# Material learning now triggered by download/iteration signals, not chat analysis
from app.agents.summary_agent import maybe_summarize
from app.deps import get_current_teacher_id
from datetime import datetime, timezone
import asyncio
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


async def _prepare_chat(req: ChatRequest, request: Request, teacher_id: str):
    # Verify the request body matches the authenticated user
    if req.teacher_id and req.teacher_id != teacher_id:
        raise HTTPException(403, "Zugriff verweigert (ID Mismatch)")

    if not req.message or not req.message.strip():
        raise HTTPException(400, "Nachricht darf nicht leer sein")

    conversation_id = req.conversation_id

    # Create conversation if new
    if not conversation_id:
        conv = await db.insert(
            "conversations",
            {"user_id": teacher_id, "title": req.message[:80]},
        )
        conversation_id = conv["id"]

    # Store user message
    await db.insert("messages", {
        "conversation_id": conversation_id,
        "role": "user",
        "content": req.message,
    })

    # Load history
    history = await db.select(
        "messages",
        columns="role, content",
        filters={"conversation_id": conversation_id},
        order="created_at.asc",
        limit=20,
    )
    messages = history if isinstance(history, list) else []

    # Maybe summarize if conversation is long
    await maybe_summarize(conversation_id, teacher_id, messages)

    # Fix #1: Load existing summary and prepend to history
    summary_record = await db.select(
        "session_logs",
        columns="summary",
        filters={"conversation_id": conversation_id},
        single=True,
    )
    if summary_record and summary_record.get("summary"):
        summary_text = f"[Zusammenfassung des bisherigen Gesprächs: {summary_record['summary']}]"
        messages = [{"role": "assistant", "content": summary_text}] + messages

    # Run the agent
    agent = get_agent()
    deps = AgentDeps(
        teacher_id=teacher_id,
        conversation_id=conversation_id,
        base_url=str(request.base_url).rstrip("/"),
    )

    # Build message history for Pydantic AI
    from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse
    from pydantic_ai.messages import UserPromptPart, TextPart

    # The agent.run() takes a user prompt + message_history
    # We pass all but the last message as history, last as prompt
    message_history: list[ModelMessage] = []
    for m in messages[:-1]:
        if m["role"] == "user":
            message_history.append(
                ModelRequest(parts=[UserPromptPart(content=m["content"])])
            )
        else:
            message_history.append(
                ModelResponse(parts=[TextPart(content=m["content"])])
            )

    # Build the user prompt — may include image or PDF text
    user_prompt = req.message
    user_prompt_parts: list = [UserPromptPart(content=req.message)]

    if req.attachment_base64 and req.attachment_type:
        if req.attachment_type.startswith("image/"):
            # Send image to Claude Vision
            import base64
            from pydantic_ai.messages import BinaryImage
            image_bytes = base64.b64decode(req.attachment_base64)
            user_prompt_parts.append(
                BinaryImage(data=image_bytes, media_type=req.attachment_type)
            )
            logger.info(f"Image attachment: {req.attachment_name} ({len(image_bytes)} bytes)")
        elif req.attachment_type == "application/pdf":
            # Extract text from PDF
            import base64
            try:
                import fitz  # PyMuPDF
                pdf_bytes = base64.b64decode(req.attachment_base64)
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                pdf_text = "\n".join(page.get_text() for page in doc)
                doc.close()
                if pdf_text.strip():
                    user_prompt = f"{req.message}\n\n--- Inhalt der Datei '{req.attachment_name}' ---\n{pdf_text[:15000]}"
                    user_prompt_parts = [UserPromptPart(content=user_prompt)]
                    logger.info(f"PDF extracted: {req.attachment_name} ({len(pdf_text)} chars)")
            except Exception as e:
                logger.error(f"PDF extraction failed: {e}")
                user_prompt = f"{req.message}\n\n[PDF '{req.attachment_name}' konnte nicht gelesen werden]"
                user_prompt_parts = [UserPromptPart(content=user_prompt)]
    
    has_image = req.attachment_type and req.attachment_type.startswith("image/")
    run_input = user_prompt_parts if has_image else user_prompt

    return {
        "conversation_id": conversation_id,
        "messages": messages,
        "agent": agent,
        "deps": deps,
        "message_history": message_history,
        "run_input": run_input,
    }


@router.post("/send", response_model=ChatResponse)
async def chat_send(
    req: ChatRequest, 
    request: Request,
    teacher_id: str = Depends(get_current_teacher_id)
):
    prepared_chat = await _prepare_chat(req, request, teacher_id)
    conversation_id = prepared_chat["conversation_id"]
    messages = prepared_chat["messages"]
    agent = prepared_chat["agent"]
    deps = prepared_chat["deps"]
    message_history = prepared_chat["message_history"]
    run_input = prepared_chat["run_input"]
    
    # Fix #3: Retry on rate limit / overload
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            result = await agent.run(
                run_input,
                deps=deps,
                message_history=message_history,
            )
            assistant_text = result.output
            break
        except Exception as e:
            err_str = f"{type(e).__name__}: {e}".lower()
            is_retryable = any(k in err_str for k in ("429", "rate", "overloaded", "503", "529"))
            if is_retryable and attempt < max_retries:
                wait_time = 2 ** (attempt + 1)  # 2s, 4s
                logger.warning(f"Agent rate limited, retry {attempt + 1} in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
                continue
            logger.error(f"Agent error: {type(e).__name__}: {e}", exc_info=True)
            raise HTTPException(500, f"KI-Antwort fehlgeschlagen: {type(e).__name__}")

    # Store assistant message
    saved = await db.insert("messages", {
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": assistant_text,
    })

    # Update conversation timestamp
    await db.update(
        "conversations",
        {"updated_at": datetime.now(timezone.utc).isoformat()},
        filters={"id": conversation_id},
    )

    # Fire-and-forget: memory agent — Fix #5: only on substantial messages (every 3rd or >50 chars)
    full_messages = messages + [{"role": "assistant", "content": assistant_text}]
    msg_count = len([m for m in messages if m["role"] == "user"])
    user_msg_substantial = len(req.message.strip()) > 50

    if user_msg_substantial or msg_count % 3 == 0:
        def _on_memory_done(task: asyncio.Task):
            if task.exception():
                logger.error(f"Memory agent failed: {task.exception()}")

        mem_task = asyncio.create_task(
            run_memory_agent(teacher_id, conversation_id, full_messages)
        )
        mem_task.add_done_callback(_on_memory_done)

    return ChatResponse(
        conversation_id=conversation_id,
        message=ChatMessageOut(
            id=saved.get("id", f"msg-{conversation_id}"),
            role="assistant",
            content=assistant_text,
            timestamp=saved.get("created_at", ""),
        ),
    )


@router.post("/send-stream")
async def chat_send_stream(req: ChatRequest, request: Request, teacher_id: str = Depends(get_current_teacher_id)):
    prepared_chat = await _prepare_chat(req, request, teacher_id)
    conversation_id = prepared_chat["conversation_id"]
    messages = prepared_chat["messages"]
    agent = prepared_chat["agent"]
    deps = prepared_chat["deps"]
    message_history = prepared_chat["message_history"]
    run_input = prepared_chat["run_input"]

    async def event_generator():
        # Send conversation_id first
        yield f"data: {json.dumps({'type': 'meta', 'conversation_id': conversation_id})}\n\n"
        
        # Human-readable labels for tool calls
        _TOOL_LABELS = {
            "search_curriculum": "📚 Lehrplan wird durchsucht…",
            "search_web": "🔍 Recherche im Internet…",
            "remember": "💾 Wird gespeichert…",
            "generate_material": "📝 Material wird erstellt…",
            "generate_exercise": "🎯 Übung wird generiert…",
            "patch_material_task": "✏️ Aufgabe wird angepasst…",
            "manage_todos": "📋 To-Do-Liste wird aktualisiert…",
            "search_wikipedia": "📖 Wikipedia wird durchsucht…",
            "search_images": "🔍 Bilder werden gesucht…",
            "classroom_tools": "🎲 Classroom-Tool wird gestartet…",
            "set_timer": "⏱️ Timer wird gestellt…",
            "create_poll": "📊 Abstimmung wird erstellt…",
            "poll_results": "📊 Ergebnisse werden geladen…",
            "generate_image": "🎨 Bild wird generiert…",
            "continue_material": "✏️ Material wird überarbeitet…",
            "youtube_quiz": "🎬 YouTube-Quiz wird erstellt…",
            "text_to_speech_tool": "🔊 Audio wird generiert…",
            "generate_audio_dialogue": "🎙️ Dialog wird vertont…",
        }

        full_text = ""
        try:
            async for event in agent.run_stream_events(run_input, deps=deps, message_history=message_history):
                from pydantic_ai.messages import (
                    FunctionToolCallEvent, PartDeltaEvent, PartStartEvent,
                    TextPartDelta, TextPart,
                )
                from pydantic_ai.run import AgentRunResultEvent

                if isinstance(event, FunctionToolCallEvent):
                    tool_name = event.part.tool_name
                    label = _TOOL_LABELS.get(tool_name, f"⚙️ {tool_name}…")
                    yield f"data: {json.dumps({'type': 'step', 'text': label})}\n\n"
                elif isinstance(event, PartStartEvent):
                    if isinstance(event.part, TextPart) and event.part.content:
                        delta_text = event.part.content
                        full_text += delta_text
                        yield f"data: {json.dumps({'type': 'delta', 'text': delta_text})}\n\n"
                elif isinstance(event, PartDeltaEvent):
                    if isinstance(event.delta, TextPartDelta):
                        delta_text = event.delta.content_delta
                        full_text += delta_text
                        yield f"data: {json.dumps({'type': 'delta', 'text': delta_text})}\n\n"
                elif isinstance(event, AgentRunResultEvent):
                    if not full_text:
                        full_text = str(event.result.output or "")
        except Exception as e:
            logger.error(f"Agent stream error: {type(e).__name__}: {e}", exc_info=True)
            # Yield an error message if something goes wrong during the stream
            error_payload = {'type': 'error', 'message': f"KI-Antwort fehlgeschlagen: {type(e).__name__}"}
            yield f"data: {json.dumps(error_payload)}\n\n"
            return

        # Save message to DB after stream completes
        saved = await db.insert("messages", {
            "conversation_id": conversation_id,
            "role": "assistant", 
            "content": full_text,
        })
        
        # Send final event with message ID
        yield f"data: {json.dumps({'type': 'done', 'message_id': saved.get('id', '')})}\n\n"
        
        # Update conversation timestamp
        await db.update(
            "conversations",
            {"updated_at": datetime.now(timezone.utc).isoformat()},
            filters={"id": conversation_id},
        )
        
        # Fire-and-forget memory + learning agents — Fix #5: throttled
        full_messages = messages + [{"role": "assistant", "content": full_text}]
        msg_count = len([m for m in messages if m["role"] == "user"])
        user_msg_substantial = len(req.message.strip()) > 50

        if user_msg_substantial or msg_count % 3 == 0:
            def _on_memory_done(task: asyncio.Task):
                if task.exception():
                    logger.error(f"Memory agent failed: {task.exception()}")

            mem_task = asyncio.create_task(
                run_memory_agent(teacher_id, conversation_id, full_messages)
            )
            mem_task.add_done_callback(_on_memory_done)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/history")
async def chat_history(
    conversation_id: str, 
    teacher_id: str = Depends(get_current_teacher_id)
):
    # BUG-003 fix: Verify conversation belongs to requesting teacher
    conv = await db.select(
        "conversations",
        columns="id, user_id",
        filters={"id": conversation_id},
        single=True,
    )
    if not conv or conv.get("user_id") != teacher_id:
        raise HTTPException(status_code=403, detail="Zugriff verweigert")
    messages = await db.select(
        "messages",
        columns="id, role, content, created_at",
        filters={"conversation_id": conversation_id},
        order="created_at.asc",
    )
    return {
        "messages": [
            {"id": m["id"], "role": m["role"], "content": m["content"], "timestamp": m["created_at"]}
            for m in (messages if isinstance(messages, list) else [])
        ]
    }

@router.get("/conversations")
async def chat_conversations(teacher_id: str = Depends(get_current_teacher_id)):
    convs = await db.select(
        "conversations",
        columns="id, title, updated_at",
        filters={"user_id": teacher_id},
        order="updated_at.desc",
        limit=20,
    )
    return [
        ConversationOut(id=c["id"], title=c.get("title"), updated_at=c["updated_at"])
        for c in (convs if isinstance(convs, list) else [])
    ]

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str, 
    teacher_id: str = Depends(get_current_teacher_id)
):
    """Delete a conversation and its messages."""
    # Verify ownership before deletion!
    conv = await db.select(
        "conversations", 
        columns="user_id", 
        filters={"id": conversation_id}, 
        single=True
    )
    if not conv or conv.get("user_id") != teacher_id:
        raise HTTPException(403, "Zugriff verweigert")

    await db.delete("messages", {"conversation_id": conversation_id})
    await db.delete("session_logs", {"conversation_id": conversation_id})
    await db.delete("conversations", {"id": conversation_id})
    return {"deleted": True}

@router.patch("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str, 
    title: str = "", 
    teacher_id: str = Depends(get_current_teacher_id)
):
    conv = await db.select(
        "conversations",
        columns="id, user_id",
        filters={"id": conversation_id},
        single=True,
    )
    if not conv or conv.get("user_id") != teacher_id:
        raise HTTPException(status_code=403, detail="Zugriff verweigert")
    if title:
        await db.update(
            "conversations",
            {"title": title[:80]},
            filters={"id": conversation_id},
        )
    return {"updated": True}
