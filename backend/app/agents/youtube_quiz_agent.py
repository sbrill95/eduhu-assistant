"""YouTube-Quiz-Agent — extracts transcripts and generates quizzes."""

import logging
import re
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app.agents.llm import get_haiku

logger = logging.getLogger(__name__)


class QuizFrage(BaseModel):
    nummer: int
    frage: str
    typ: str  # "multiple_choice", "true_false", "lueckentext"
    optionen: list[str] | None = None  # For MC
    richtige_antwort: str
    erklaerung: str  # Why this answer is correct
    zeitstempel: str | None = None  # Relevant timestamp in video


class YouTubeQuizStructure(BaseModel):
    titel: str
    video_url: str
    video_titel: str
    schwerpunkt: str
    fragen: list[QuizFrage]
    zusammenfassung: str  # Brief summary of the video content


SYSTEM_PROMPT = """\
Du erstellst Quiz-Fragen basierend auf YouTube-Video-Transkripten.

## Qualitätskriterien
- Fragen prüfen Verständnis, nicht nur Wiedergabe
- Mix aus Multiple-Choice, Wahr/Falsch und Lückentext
- Jede Frage hat eine kurze Erklärung der richtigen Antwort
- Bei MC: 4 Optionen, genau 1 richtig, Distraktoren plausibel
- Zeitstempel angeben wenn möglich (wo im Video wird das Thema behandelt)
- 5-10 Fragen je nach Videolänge
- Zusammenfassung des Videoinhalts als Kontext

Sprache: Deutsch. Fragen klar und eindeutig formuliert."""


@dataclass
class YouTubeQuizDeps:
    teacher_id: str
    transcript: str = ""
    video_url: str = ""
    video_title: str = ""


async def _system_prompt(ctx: RunContext[YouTubeQuizDeps]) -> str:
    return SYSTEM_PROMPT


def create_youtube_quiz_agent() -> Agent[YouTubeQuizDeps, YouTubeQuizStructure]:
    agent = Agent(
        get_haiku(),
        deps_type=YouTubeQuizDeps,
        output_type=YouTubeQuizStructure,
        instructions=_system_prompt,
    )
    return agent


_agent = None

def get_youtube_quiz_agent():
    global _agent
    if _agent is None:
        _agent = create_youtube_quiz_agent()
    return _agent


async def extract_transcript(video_url: str) -> tuple[str, str, str]:
    """Extract transcript from YouTube video using youtube-transcript-api.
    
    Returns (transcript_text, video_title, video_url).
    """
    import asyncio

    def _extract():
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # Extract video ID from URL
        video_id = video_url
        if "youtube.com/watch" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1].split("?")[0]
        
        ytt = YouTubeTranscriptApi()
        transcript_obj = ytt.fetch(video_id, languages=['de', 'en'])
        
        text = ' '.join(s.text for s in transcript_obj.snippets)
        
        # Clean up
        text = re.sub(r'\s+', ' ', text).strip()
        # Limit to ~10000 chars for LLM context
        if len(text) > 10000:
            text = text[:10000] + "..."
        
        # Try to get title via oEmbed (no API key needed)
        title = "YouTube Video"
        try:
            import httpx
            r = httpx.get(f"https://www.youtube.com/oembed?url={video_url}&format=json", timeout=5)
            if r.status_code == 200:
                title = r.json().get("title", title)
        except Exception:
            pass
        
        clean_url = f"https://www.youtube.com/watch?v={video_id}"
        return text, title, clean_url

    return await asyncio.to_thread(_extract)


async def generate_youtube_quiz(
    teacher_id: str,
    video_url: str,
    schwerpunkt: str = "",
    num_questions: int = 7,
) -> YouTubeQuizStructure:
    """Full pipeline: extract transcript → generate quiz."""
    transcript, video_title, clean_url = await extract_transcript(video_url)

    if not transcript:
        raise ValueError("Kein Transkript verfügbar für dieses Video. Evtl. keine Untertitel vorhanden.")

    agent = get_youtube_quiz_agent()
    deps = YouTubeQuizDeps(
        teacher_id=teacher_id,
        transcript=transcript,
        video_url=clean_url,
        video_title=video_title,
    )

    prompt = f"""Erstelle ein Quiz mit {num_questions} Fragen basierend auf diesem YouTube-Video:

**Video:** {video_title}
**URL:** {clean_url}
{f'**Schwerpunkt:** {schwerpunkt}' if schwerpunkt else ''}

**Transkript:**
{transcript[:8000]}"""

    result = await agent.run(prompt, deps=deps)
    return result.output
