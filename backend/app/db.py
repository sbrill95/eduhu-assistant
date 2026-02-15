"""Supabase REST client — lightweight, async, zero ORM."""

import httpx
from typing import Any
from app.config import get_settings

# Shared client — reuses TCP connections (BUG-007 fix)
_client: httpx.AsyncClient | None = None

def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client


def _headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    s = get_settings()
    h = {
        "apikey": s.supabase_service_role_key,
        "Authorization": f"Bearer {s.supabase_service_role_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    if extra:
        h.update(extra)
    return h


def _url(table: str) -> str:
    return f"{get_settings().supabase_url}/rest/v1/{table}"


async def select(
    table: str,
    *,
    columns: str = "*",
    filters: dict[str, str] | None = None,
    order: str | None = None,
    limit: int | None = None,
    single: bool = False,
) -> list[dict[str, Any]] | dict[str, Any] | None:
    params: dict[str, str] = {"select": columns}
    if filters:
        for col, val in filters.items():
            params[col] = f"eq.{val}"
    if order:
        params["order"] = order
    if limit:
        params["limit"] = str(limit)

    headers = _headers({"Accept": "application/vnd.pgrst.object+json"} if single else None)

    client = _get_client()
    r = await client.get(_url(table), params=params, headers=headers)
    if r.status_code == 406 and single:
        return None
    r.raise_for_status()
    return r.json()


async def insert(table: str, data: dict[str, Any]) -> dict[str, Any]:
    client = _get_client()
    r = await client.post(_url(table), json=data, headers=_headers())
    r.raise_for_status()
    result = r.json()
    return result[0] if isinstance(result, list) else result


async def update(
    table: str, data: dict[str, Any], filters: dict[str, str],
) -> Any:
    """Update rows matching filters."""
    url = _url(table)
    params = {}
    for col, val in filters.items():
        params[col] = f"eq.{val}"
    client = _get_client()
    r = await client.patch(url, json=data, params=params, headers=_headers())
    r.raise_for_status()
    return r.json()


async def upsert(
    table: str, data: dict[str, Any] | list[dict[str, Any]], on_conflict: str = ""
) -> Any:
    url = _url(table)
    if on_conflict:
        url += f"?on_conflict={on_conflict}"
    headers = _headers({"Prefer": "resolution=merge-duplicates,return=representation"})
    client = _get_client()
    r = await client.post(url, json=data, headers=headers)
    r.raise_for_status()
    return r.json()


async def insert_batch(table: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Insert multiple rows in a single request (much faster than N individual inserts)."""
    if not rows:
        return []
    client = _get_client()
    r = await client.post(_url(table), json=rows, headers=_headers())
    r.raise_for_status()
    return r.json()
