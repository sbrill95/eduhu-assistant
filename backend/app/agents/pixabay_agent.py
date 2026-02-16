"""Pixabay Agent — search free stock images."""
import logging
import urllib.parse

import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)


async def search_images(query: str, count: int = 5, lang: str = "de") -> str:
    """Search Pixabay for free stock images."""
    settings = get_settings()
    if not settings.pixabay_api_key:
        return "Pixabay API Key nicht konfiguriert."

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://pixabay.com/api/",
                params={
                    "key": settings.pixabay_api_key,
                    "q": query,
                    "lang": lang,
                    "image_type": "photo",
                    "per_page": count,
                    "safesearch": "true",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        hits = data.get("hits", [])
        if not hits:
            return f"Keine Bilder für '{query}' gefunden."

        results = []
        for i, hit in enumerate(hits, 1):
            tags = hit.get("tags", "")
            preview = hit.get("webformatURL", "")
            page_url = hit.get("pageURL", "")
            user = hit.get("user", "")
            results.append(
                f"[{i}] {tags}\n"
                f"![Bild {i}]({preview})\n"
                f"📷 von {user} auf Pixabay | [Originalseite]({page_url})"
            )

        return f"**{data.get('totalHits', 0)} Ergebnisse** für \"{query}\":\n\n" + "\n\n".join(results)

    except Exception as e:
        logger.error(f"Pixabay search failed: {e}")
        return f"Pixabay-Suche fehlgeschlagen: {str(e)}"
