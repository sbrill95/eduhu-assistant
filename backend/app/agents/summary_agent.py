"""Conversation Summary — compresses long conversations.

Triggered when message count > 10. Uses Sonnet with a short prompt.
"""

import logging
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from app.config import get_settings
from app import db

logger = logging.getLogger(__name__)

SUMMARY_PROMPT = """Fasse das folgende Gespräch zwischen einer Lehrkraft und dem KI-Assistenten eduhu in 3-5 Sätzen zusammen. Fokus auf: Was wurde besprochen? Was wurde erstellt? Welche Entscheidungen wurden getroffen?

Antworte NUR mit der Zusammenfassung, kein JSON, keine Überschrift."""


async def maybe_summarize(
    conversation_id: str,
    teacher_id: str,
    messages: list[dict[str, str]],
) -> str | None:
    """Summarize if conversation is getting long (>10 messages).
    
    Returns the summary text, or None if no summary needed.
    """
    if len(messages) <= 10:
        return None

    logger.info(f"Summarizing conversation {conversation_id} ({len(messages)} msgs)")

    # Format messages for summarization
    text = "\n".join(
        f"{'Lehrkraft' if m['role'] == 'user' else 'eduhu'}: {m['content']}"
        for m in messages[:-2]  # Summarize all but last 2 messages
    )

    import os
    settings = get_settings()
    os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
    model = AnthropicModel("claude-sonnet-4-20250514")
    agent = Agent(model, instructions=SUMMARY_PROMPT, output_type=str)

    try:
        result = await agent.run(text)
        summary = result.output

        # Store summary
        await db.upsert(
            "session_logs",
            {
                "conversation_id": conversation_id,
                "user_id": teacher_id,
                "summary": summary,
            },
            on_conflict="conversation_id",
        )

        logger.info(f"Summary stored: {len(summary)} chars")
        return summary

    except Exception as e:
        logger.error(f"Summary failed: {e}")
        return None
