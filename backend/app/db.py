"""PostgreSQL async client — asyncpg, zero ORM."""

import json
import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

import asyncpg

from app.config import get_settings

logger = logging.getLogger(__name__)

# ══════════════════════════════════════
# Connection Pool
# ══════════════════════════════════════

_pool: asyncpg.Pool | None = None


async def init_pool() -> None:
    """Create the asyncpg connection pool. Call from app lifespan startup."""
    global _pool
    s = get_settings()
    _pool = await asyncpg.create_pool(
        s.database_url,
        min_size=2,
        max_size=10,
        init=_init_connection,
    )
    logger.info("Database pool created")


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Register pgvector codec on each new connection."""
    await conn.set_type_codec(
        "vector",
        encoder=lambda v: v if isinstance(v, str) else "[" + ",".join(str(x) for x in v) + "]",
        decoder=lambda v: v,
        schema="public",
        format="text",
    )


async def close_pool() -> None:
    """Close the pool. Call from app lifespan shutdown."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database pool closed")


def _get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_pool() first.")
    return _pool


# ══════════════════════════════════════
# Internal Helpers
# ══════════════════════════════════════

_OPERATORS = {"eq": "=", "lt": "<", "gt": ">", "lte": "<=", "gte": ">=", "neq": "!="}


def _parse_value(val: Any) -> Any:
    """Convert special string values to Python equivalents."""
    if isinstance(val, str) and val == "now()":
        return datetime.now(timezone.utc)
    return val


def _build_where(
    filters: dict[str, Any] | None,
    offset: int = 0,
) -> tuple[str, list[Any]]:
    """Build WHERE clause from filter dict.

    Supports:
      {"col": value}          → col = $N
      {"col.lt": value}       → col < $N
      {"col.gt": value}       → col > $N  (etc.)
    """
    if not filters:
        return "", []

    clauses: list[str] = []
    values: list[Any] = []

    for key, val in filters.items():
        parts = key.rsplit(".", 1)
        if len(parts) == 2 and parts[1] in _OPERATORS:
            col, op_key = parts
            operator = _OPERATORS[op_key]
        else:
            col = key
            operator = "="

        values.append(_parse_value(val))
        clauses.append(f"{col} {operator} ${len(values) + offset}")

    return "WHERE " + " AND ".join(clauses), values


def _build_order(order: str | None) -> str:
    """Parse PostgREST-style order string to SQL ORDER BY.

    'created_at.desc' → 'ORDER BY created_at DESC'
    'due_date.asc.nullslast,created_at.desc' → 'ORDER BY due_date ASC NULLS LAST, created_at DESC'
    """
    if not order:
        return ""

    parts: list[str] = []
    for segment in order.split(","):
        tokens = segment.strip().split(".")
        col = tokens[0]
        direction = ""
        nulls = ""
        for t in tokens[1:]:
            tl = t.lower()
            if tl == "desc":
                direction = "DESC"
            elif tl == "asc":
                direction = "ASC"
            elif tl == "nullslast":
                nulls = "NULLS LAST"
            elif tl == "nullsfirst":
                nulls = "NULLS FIRST"
        parts.append(f"{col} {direction} {nulls}".strip())

    return "ORDER BY " + ", ".join(parts)


def _record_to_dict(record: asyncpg.Record) -> dict[str, Any]:
    """Convert asyncpg Record to dict, serialising non-JSON-native types
    to strings so callers get the same shapes as the old PostgREST API."""
    out: dict[str, Any] = {}
    for key, val in record.items():
        if isinstance(val, UUID):
            out[key] = str(val)
        elif isinstance(val, datetime):
            out[key] = val.isoformat()
        elif isinstance(val, date):
            out[key] = val.isoformat()
        elif isinstance(val, Decimal):
            out[key] = float(val)
        else:
            out[key] = val
    return out


def _jsonb_encode(val: Any) -> Any:
    """Encode dicts/lists as JSON strings for asyncpg JSONB columns."""
    if isinstance(val, (dict, list)):
        return json.dumps(val)
    return val


# ══════════════════════════════════════
# Public API — same signatures as before
# ══════════════════════════════════════


async def select(
    table: str,
    *,
    columns: str = "*",
    filters: dict[str, Any] | None = None,
    order: str | None = None,
    limit: int | None = None,
    single: bool = False,
    count: bool = False,
) -> list[dict[str, Any]] | dict[str, Any] | int | None:
    pool = _get_pool()

    if count:
        where_clause, values = _build_where(filters)
        sql = f"SELECT COUNT(*) FROM {table} {where_clause}"
        async with pool.acquire() as conn:
            result = await conn.fetchval(sql, *values)
        return result or 0

    where_clause, values = _build_where(filters)
    order_clause = _build_order(order)
    limit_clause = f"LIMIT {limit}" if limit else ""

    sql = f"SELECT {columns} FROM {table} {where_clause} {order_clause} {limit_clause}"

    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *values)

    if single:
        return _record_to_dict(rows[0]) if rows else None

    return [_record_to_dict(r) for r in rows]


async def insert(table: str, data: dict[str, Any]) -> dict[str, Any]:
    pool = _get_pool()
    cols = list(data.keys())
    placeholders = ", ".join(f"${i + 1}" for i in range(len(cols)))
    col_names = ", ".join(cols)
    values = [_parse_value(data[c]) for c in cols]

    sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) RETURNING *"

    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, *values)

    return _record_to_dict(row)


async def update(
    table: str,
    data: dict[str, Any],
    filters: dict[str, Any],
) -> Any:
    """Update rows matching filters."""
    pool = _get_pool()
    set_cols = list(data.keys())
    set_parts = [f"{col} = ${i + 1}" for i, col in enumerate(set_cols)]
    set_values = [_parse_value(data[c]) for c in set_cols]

    where_clause, where_values = _build_where(filters, offset=len(set_values))

    sql = f"UPDATE {table} SET {', '.join(set_parts)} {where_clause} RETURNING *"

    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *set_values, *where_values)

    return [_record_to_dict(r) for r in rows]


async def upsert(
    table: str,
    data: dict[str, Any] | list[dict[str, Any]],
    on_conflict: str = "",
) -> Any:
    pool = _get_pool()

    if isinstance(data, list):
        results = []
        for d in data:
            r = await upsert(table, d, on_conflict)
            results.extend(r if isinstance(r, list) else [r])
        return results

    cols = list(data.keys())
    placeholders = ", ".join(f"${i + 1}" for i in range(len(cols)))
    col_names = ", ".join(cols)
    values = [_parse_value(data[c]) for c in cols]

    if on_conflict:
        conflict_cols = on_conflict.strip()
        update_cols = [c for c in cols if c not in conflict_cols.split(",")]
        update_parts = [f"{c} = EXCLUDED.{c}" for c in update_cols]
        conflict_clause = f"ON CONFLICT ({conflict_cols}) DO UPDATE SET {', '.join(update_parts)}" if update_parts else f"ON CONFLICT ({conflict_cols}) DO NOTHING"
    else:
        conflict_clause = ""

    sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) {conflict_clause} RETURNING *"

    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, *values)

    if row is None:
        return [data]
    return [_record_to_dict(row)]


async def delete(table: str, filters: dict[str, Any]) -> Any:
    """Delete rows matching filters."""
    pool = _get_pool()
    where_clause, values = _build_where(filters)
    sql = f"DELETE FROM {table} {where_clause} RETURNING *"

    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *values)

    return [_record_to_dict(r) for r in rows] if rows else None


async def delete_by_ids(table: str, ids: list[str]) -> None:
    """Delete rows by list of IDs in a single request."""
    if not ids:
        return
    pool = _get_pool()
    # Convert string IDs to UUID objects for asyncpg
    uuid_ids = [UUID(i) if isinstance(i, str) else i for i in ids]
    sql = f"DELETE FROM {table} WHERE id = ANY($1::uuid[])"

    async with pool.acquire() as conn:
        await conn.execute(sql, uuid_ids)


async def insert_batch(table: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Insert multiple rows in a single request."""
    if not rows:
        return []

    pool = _get_pool()
    cols = list(rows[0].keys())
    col_names = ", ".join(cols)

    results: list[dict[str, Any]] = []
    async with pool.acquire() as conn:
        # Use a prepared statement for batch efficiency
        placeholders = ", ".join(f"${i + 1}" for i in range(len(cols)))
        sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) RETURNING *"
        stmt = await conn.prepare(sql)

        for row_data in rows:
            values = [_parse_value(row_data[c]) for c in cols]
            record = await stmt.fetchrow(*values)
            if record:
                results.append(_record_to_dict(record))

    return results


async def raw_fetch(sql: str, *args: Any) -> list[dict[str, Any]]:
    """Execute raw SQL query and return list of dicts.

    Use for complex queries that don't fit the CRUD helpers
    (e.g. pgvector similarity search, JOINs).
    """
    pool = _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *args)
    return [_record_to_dict(r) for r in rows]
