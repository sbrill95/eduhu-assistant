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
    """Extract transcript from YouTube video.
    
    Returns (transcript_text, video_title, video_url).
    """
    import asyncio
    import yt_dlp

    def _extract():
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['de', 'de-DE', 'en'],
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        title = info.get('title', 'Unbekanntes Video')
        url = info.get('webpage_url', video_url)

        # Try to get subtitles (manual first, then auto)
        subs = info.get('subtitles', {})
        auto_subs = info.get('automatic_captions', {})

        transcript_data = None
        for lang in ['de', 'de-DE', 'en']:
            if lang in subs:
                transcript_data = subs[lang]
                break
            if lang in auto_subs:
                transcript_data = auto_subs[lang]
                break

        if not transcript_data:
            # Try any available language
            all_subs = {**subs, **auto_subs}
            if all_subs:
                first_lang = next(iter(all_subs))
                transcript_data = all_subs[first_lang]

        if not transcript_data:
            return "", title, url

        # Find a text format (json3, srv3, vtt, etc.)
        text_url = None
        for fmt in transcript_data:
            if fmt.get('ext') in ('json3', 'srv3', 'vtt', 'ttml'):
                text_url = fmt.get('url')
                break
        if not text_url and transcript_data:
            text_url = transcript_data[0].get('url')

        if not text_url:
            return "", title, url

        # Download and parse transcript
        import httpx
        with httpx.Client(timeout=30) as client:
            r = client.get(text_url)
            r.raise_for_status()
            raw = r.text

        # Parse different formats
        if 'json3' in str(text_url) or raw.strip().startswith('{'):
            import json
            data = json.loads(raw)
            events = data.get('events', [])
            lines = []
            for event in events:
                segs = event.get('segs', [])
                text = ''.join(s.get('utf8', '') for s in segs).strip()
                if text and text != '\n':
                    lines.append(text)
            transcript = ' '.join(lines)
        else:
            # VTT/SRT format — strip timestamps
            lines = []
            for line in raw.split('\n'):
                line = line.strip()
                if not line or '-->' in line or line.isdigit() or line.startswith('WEBVTT'):
                    continue
                # Remove HTML tags
                line = re.sub(r'<[^>]+>', '', line)
                if line:
                    lines.append(line)
            transcript = ' '.join(lines)

        # Clean up
        transcript = re.sub(r'\s+', ' ', transcript).strip()
        # Limit to ~10000 chars for LLM context
        if len(transcript) > 10000:
            transcript = transcript[:10000] + "..."

        return transcript, title, url

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
