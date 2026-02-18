"""Token usage tracking — logs all LLM calls with cost calculation."""

import logging
from datetime import datetime, timezone

from app import db

logger = logging.getLogger(__name__)

# USD per 1M tokens
MODEL_PRICES: dict[str, dict[str, float]] = {
    "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
    "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.0},
}

# Aliases
MODEL_PRICES["claude-sonnet-4"] = MODEL_PRICES["claude-sonnet-4-20250514"]
MODEL_PRICES["claude-3-5-haiku"] = MODEL_PRICES["claude-3-5-haiku-20241022"]


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float | None:
    """Calculate USD cost for a model call. Returns None if model unknown."""
    prices = MODEL_PRICES.get(model)
    if not prices:
        # Try partial match
        for key, p in MODEL_PRICES.items():
            if key in model or model in key:
                prices = p
                break
    if not prices:
        return None
    return (input_tokens * prices["input"] / 1_000_000) + (output_tokens * prices["output"] / 1_000_000)


async def log_usage(
    teacher_id: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    agent_type: str = "main",
    request_id: str | None = None,
) -> None:
    """Log token usage to DB. Fire-and-forget safe."""
    try:
        cost = calculate_cost(model, input_tokens, output_tokens)
        if cost is None:
            logger.warning(f"Unknown model for pricing: {model}, storing cost as 0")
            cost = 0.0
        await db.insert("token_usage", {
            "teacher_id": teacher_id,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
            "agent_type": agent_type,
            "request_id": request_id,
        })
    except Exception as e:
        logger.warning(f"Token tracking failed: {e}")


async def get_usage_summary(teacher_id: str, days: int = 7, agent_type: str | None = None) -> dict:
    """Get aggregated usage stats for a teacher."""
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    # Server-side filtering via Supabase
    filters: dict[str, str] = {"teacher_id": teacher_id}
    if agent_type:
        filters["agent_type"] = agent_type

    # Use httpx directly for gte filter (db.select only supports eq)
    import httpx
    from app.config import get_settings
    s = get_settings()
    params: dict[str, str] = {
        "teacher_id": f"eq.{teacher_id}",
        "created_at": f"gte.{cutoff}",
        "order": "created_at.desc",
        "limit": "5000",
    }
    if agent_type:
        params["agent_type"] = f"eq.{agent_type}"

    headers = {
        "apikey": s.supabase_service_role_key,
        "Authorization": f"Bearer {s.supabase_service_role_key}",
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(f"{s.supabase_url}/rest/v1/token_usage", params=params, headers=headers)
        r.raise_for_status()
        filtered = r.json()

    if not filtered:
        return {"daily": [], "total": {"input_tokens": 0, "output_tokens": 0, "calls": 0, "cost_usd": 0}}

    # Aggregate by day + model
    from collections import defaultdict
    daily_map: dict[str, dict] = defaultdict(lambda: defaultdict(lambda: {
        "input_tokens": 0, "output_tokens": 0, "calls": 0, "cost_usd": 0.0,
    }))

    total = {"input_tokens": 0, "output_tokens": 0, "calls": 0, "cost_usd": 0.0}

    for r in filtered:
        date = str(r.get("created_at", ""))[:10]
        model = r.get("model", "unknown")
        inp = r.get("input_tokens", 0) or 0
        out = r.get("output_tokens", 0) or 0
        cost = float(r.get("cost_usd") or 0)

        daily_map[date][model]["input_tokens"] += inp
        daily_map[date][model]["output_tokens"] += out
        daily_map[date][model]["calls"] += 1
        daily_map[date][model]["cost_usd"] += cost

        total["input_tokens"] += inp
        total["output_tokens"] += out
        total["calls"] += 1
        total["cost_usd"] += cost

    # Flatten to list
    daily = []
    for date, models in sorted(daily_map.items(), reverse=True):
        for model, stats in models.items():
            stats["cost_usd"] = round(stats["cost_usd"], 6)
            daily.append({
                "date": date,
                "model": model,
                **stats,
            })

    total["cost_usd"] = round(total["cost_usd"], 6)
    return {"daily": daily, "total": total}
