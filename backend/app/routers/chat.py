from fastapi import APIRouter, HTTPException, Request, Depends
from app import db
from app.models import (
    ChatRequest, ChatResponse, ChatMessageOut, ConversationOut,
)
from app.agents.main_agent import get_agent, AgentDeps
from app.agents.memory_agent import run_memory_agent
from app.agents.material_learning_agent import run_material_learning
from app.agents.summary_agent import maybe_summarize
from app.config import get_settings
from app.deps import get_current_teacher_id
from datetime import datetime, timezone
import asyncio
import logging
import httpx

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/send", response_model=ChatResponse)
async def chat_send(
    req: ChatRequest, 
    request: Request,
    teacher_id: str = Depends(get_current_teacher_id)
):
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
    summary = await maybe_summarize(conversation_id, teacher_id, messages)

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

    try:
        # Use parts if we have an image, otherwise plain text
        has_image = req.attachment_type and req.attachment_type.startswith("image/")
        run_input = user_prompt_parts if has_image else user_prompt
        result = await agent.run(
            run_input,
            deps=deps,
            message_history=message_history,
        )
        assistant_text = result.output
    except Exception as e:
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

    # Fire-and-forget: memory agent (with error logging)
    def _on_memory_done(task: asyncio.Task):
        if task.exception():
            logger.error(f"Memory agent failed: {task.exception()}")

    full_messages = messages + [{"role": "assistant", "content": assistant_text}]

    mem_task = asyncio.create_task(
        run_memory_agent(teacher_id, conversation_id, full_messages)
    )
    mem_task.add_done_callback(_on_memory_done)

    # Fire-and-forget: material learning agent
    def _on_learning_done(task: asyncio.Task):
        if task.exception():
            logger.error(f"Material learning agent failed: {task.exception()}")

    learn_task = asyncio.create_task(
        run_material_learning(teacher_id, conversation_id, full_messages)
    )
    learn_task.add_done_callback(_on_learning_done)

    return ChatResponse(
        conversation_id=conversation_id,
        message=ChatMessageOut(
            id=saved.get("id", f"msg-{conversation_id}"),
            role="assistant",
            content=assistant_text,
            timestamp=saved.get("created_at", ""),
        ),
    )

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

    settings = get_settings()
    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
    }
    base = settings.supabase_url
    
    async with httpx.AsyncClient() as client:
        # Delete messages first
        await client.delete(
            f"{base}/rest/v1/messages?conversation_id=eq.{conversation_id}",
            headers=headers,
        )
        # Delete session logs
        await client.delete(
            f"{base}/rest/v1/session_logs?conversation_id=eq.{conversation_id}",
            headers=headers,
        )
        # Delete conversation
        await client.delete(
            f"{base}/rest/v1/conversations?id=eq.{conversation_id}",
            headers=headers,
        )
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
