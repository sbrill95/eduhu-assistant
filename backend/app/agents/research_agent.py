"""Research-Agent — web search via Brave API."""

import logging
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)


async def web_search(query: str, count: int = 5) -> str:
    """Search the web using Brave Search API."""
    settings = get_settings()
    if not settings.brave_api_key:
        return "Web-Suche ist nicht konfiguriert (kein API-Key)."

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": count, "search_lang": "de"},
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": settings.brave_api_key,
                },
                timeout=10.0,
            )
            r.raise_for_status()
            data = r.json()

        results = data.get("web", {}).get("results", [])
        if not results:
            return f"Keine Ergebnisse für '{query}' gefunden."

        formatted = []
        sources = []
        for i, item in enumerate(results[:count], 1):
            title = item.get("title", "")
            url = item.get("url", "")
            snippet = item.get("description", "")
            formatted.append(f"[{i}] **{title}**: {snippet}")
            sources.append(f"[{i}] [{title}]({url})")

        return "\n".join(formatted) + "\n\n---\n**Quellen:**\n" + "\n".join(sources)

    except Exception as e:
        logger.error(f"Brave search failed: {e}")
        return f"Web-Suche fehlgeschlagen: {str(e)}"
