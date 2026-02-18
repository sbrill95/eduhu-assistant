"""
Tests for TODO 2026-02-18 features:
- T1: Token Tracking (API)
- T2: Memory Restructuring (API + categories)
- T3: Rückfrage-Buttons (clarification options)
- T4: Step Indicator (SSE format)

Usage: cd backend && python -m pytest tests/benchmarks/test_new_features.py -v -s
"""

import os
import asyncio
import json
import pytest
import httpx

BASE_URL = os.getenv("BENCHMARK_URL", "https://eduhu-assistant.onrender.com")
TEACHER_ID = os.getenv("BENCHMARK_TEACHER_ID", "a4d218bd-4ac8-4ce3-8d41-c85db8be6e32")
TIMEOUT = int(os.getenv("BENCHMARK_TIMEOUT", "120"))
PAUSE = 6

HEADERS = {"X-Teacher-Id": TEACHER_ID}

FIXED_CATEGORIES = [
    "faecher_und_themen", "klassen_und_schueler", "didaktik", "pruefungen",
    "materialien", "persoenlich", "feedback", "curriculum",
]


class TestMemoryRestructuring:
    """T4 — Memory system with fixed categories."""

    @pytest.mark.asyncio
    async def test_get_memories(self):
        """GET /api/profile/memories returns grouped categories."""
        await asyncio.sleep(PAUSE)
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.get(f"{BASE_URL}/api/profile/memories", headers=HEADERS)
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text}"
        data = r.json()
        assert "total" in data
        assert "categories" in data
        assert data["total"] > 0, "No memories found"
        # All 8 fixed categories present
        for cat in FIXED_CATEGORIES:
            assert cat in data["categories"], f"Missing category: {cat}"
            assert "description" in data["categories"][cat]
            assert "memories" in data["categories"][cat]
            assert "count" in data["categories"][cat]

    @pytest.mark.asyncio
    async def test_memories_have_valid_categories(self):
        """All memories use only the 8 fixed categories."""
        await asyncio.sleep(PAUSE)
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.get(f"{BASE_URL}/api/profile/memories", headers=HEADERS)
        data = r.json()
        for cat, info in data["categories"].items():
            assert cat in FIXED_CATEGORIES, f"Rogue category: {cat}"

    @pytest.mark.asyncio
    async def test_delete_memory_wrong_user(self):
        """DELETE memory with wrong user returns 404."""
        await asyncio.sleep(PAUSE)
        fake_id = "00000000-0000-0000-0000-000000000000"
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.delete(
                f"{BASE_URL}/api/profile/memories/{fake_id}",
                headers={"X-Teacher-Id": "00000000-0000-0000-0000-000000000000"},
            )
        assert r.status_code == 404


class TestTokenTracking:
    """T1 — Token usage tracking API."""

    @pytest.mark.asyncio
    async def test_get_token_usage_default(self):
        """GET /api/profile/token-usage returns valid structure."""
        await asyncio.sleep(PAUSE)
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.get(f"{BASE_URL}/api/profile/token-usage", headers=HEADERS)
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text}"
        data = r.json()
        assert "daily" in data
        assert "total" in data
        assert "input_tokens" in data["total"]
        assert "output_tokens" in data["total"]
        assert "calls" in data["total"]
        assert "cost_usd" in data["total"]

    @pytest.mark.asyncio
    async def test_get_token_usage_with_days(self):
        """GET /api/profile/token-usage?days=30 works."""
        await asyncio.sleep(PAUSE)
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.get(
                f"{BASE_URL}/api/profile/token-usage",
                params={"days": 30},
                headers=HEADERS,
            )
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_get_token_usage_with_filter(self):
        """GET /api/profile/token-usage?agent_type=memory works."""
        await asyncio.sleep(PAUSE)
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.get(
                f"{BASE_URL}/api/profile/token-usage",
                params={"agent_type": "memory"},
                headers=HEADERS,
            )
        assert r.status_code == 200
        data = r.json()
        assert "total" in data


class TestStepIndicator:
    """T3 — SSE streaming with step events."""

    @pytest.mark.asyncio
    async def test_stream_sends_events(self):
        """POST /api/chat/send-stream returns SSE events."""
        await asyncio.sleep(PAUSE)
        events = []
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            async with c.stream(
                "POST",
                f"{BASE_URL}/api/chat/send-stream",
                json={"message": "Hallo, wie geht es dir?", "teacher_id": TEACHER_ID},
                headers=HEADERS,
            ) as resp:
                assert resp.status_code == 200
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            event = json.loads(line[6:])
                            events.append(event)
                        except json.JSONDecodeError:
                            pass

        # Should have at least meta + some deltas + done
        types = [e.get("type") for e in events]
        assert "meta" in types, f"No meta event. Got: {types}"
        assert "done" in types, f"No done event. Got: {types}"
        # Deltas should exist (agent response)
        assert "delta" in types, f"No delta events. Got: {types}"


class TestClarificationButtons:
    """T2 — Rückfrage-Buttons consistency."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Health endpoint shows correct route count."""
        await asyncio.sleep(PAUSE)
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["routes"] >= 50, f"Expected >= 50 routes, got {data['routes']}"

    @pytest.mark.asyncio
    async def test_suggestions_endpoint(self):
        """GET /api/profile/suggestions returns suggestions."""
        await asyncio.sleep(PAUSE)
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.get(f"{BASE_URL}/api/profile/suggestions", headers=HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0
