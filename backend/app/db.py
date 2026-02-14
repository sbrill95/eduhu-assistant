"""Supabase REST client — lightweight, async, zero ORM."""

import httpx
from typing import Any
from app.config import get_settings


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

    async with httpx.AsyncClient() as client:
        r = await client.get(_url(table), params=params, headers=headers)
        if r.status_code == 406 and single:
            return None
        r.raise_for_status()
        return r.json()


async def insert(table: str, data: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.post(_url(table), json=data, headers=_headers())
        r.raise_for_status()
        result = r.json()
        return result[0] if isinstance(result, list) else result


async def upsert(
    table: str, data: dict[str, Any] | list[dict[str, Any]], on_conflict: str = ""
) -> Any:
    url = _url(table)
    if on_conflict:
        url += f"?on_conflict={on_conflict}"
    headers = _headers({"Prefer": "resolution=merge-duplicates,return=representation"})
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=data, headers=headers)
        r.raise_for_status()
        return r.json()
