#!/usr/bin/env python3
"""Smoke Tests — Recurring QA for eduhu-assistant Production.

Usage:
    python3 scripts/smoke_tests.py [--base-url URL] [--teacher-id ID]

Runs against production by default. Uses a dedicated test teacher account.
"""

import asyncio
import httpx
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

# ── Config ──
BASE_URL = "https://eduhu-assistant.onrender.com"
# Steffen's test account
TEST_TEACHER_ID = "a4d218bd-4ac8-4ce3-8d41-c85db8be6e32"
TEST_TEACHER_PW = "krake26"
# A different teacher for cross-user tests
OTHER_TEACHER_ID = "demo-teacher-id"  # Will be resolved from login


@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: int = 0
    detail: str = ""
    
    def __str__(self):
        icon = "✅" if self.passed else "❌"
        time_str = f" ({self.duration_ms}ms)" if self.duration_ms else ""
        detail_str = f" — {self.detail}" if self.detail else ""
        return f"{icon} {self.name}{time_str}{detail_str}"


results: list[TestResult] = []


def headers(teacher_id: str = TEST_TEACHER_ID) -> dict:
    return {
        "Content-Type": "application/json",
        "X-Teacher-ID": teacher_id,
    }


async def timed(name: str, coro):
    """Run a test coroutine with timing."""
    start = time.monotonic()
    try:
        result = await coro
        ms = int((time.monotonic() - start) * 1000)
        results.append(TestResult(name, True, ms, result or ""))
    except Exception as e:
        ms = int((time.monotonic() - start) * 1000)
        results.append(TestResult(name, False, ms, str(e)[:200]))


# ═══════════════════════════════════════════════════
# 1. HEALTH & AUTH
# ═══════════════════════════════════════════════════

async def test_health(client: httpx.AsyncClient):
    r = await client.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200, f"Health: {r.status_code}"
    data = r.json()
    assert "version" in data, "No version in health"
    return f"v{data['version']}"


async def test_login_valid(client: httpx.AsyncClient):
    r = await client.post(f"{BASE_URL}/api/auth/login", json={"password": TEST_TEACHER_PW})
    assert r.status_code == 200, f"Login: {r.status_code} {r.text[:100]}"
    data = r.json()
    assert data.get("teacher_id"), "No teacher_id in login response"
    return f"teacher_id={data['teacher_id'][:8]}..."


async def test_login_invalid(client: httpx.AsyncClient):
    r = await client.post(f"{BASE_URL}/api/auth/login", json={"password": "falsches_passwort_xyz"})
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    return "401 as expected"


async def test_no_auth_header(client: httpx.AsyncClient):
    r = await client.get(f"{BASE_URL}/api/chat/conversations")
    assert r.status_code == 401, f"Expected 401 without header, got {r.status_code}"
    return "401 without X-Teacher-ID"


# ═══════════════════════════════════════════════════
# 2. CROSS-USER SECURITY
# ═══════════════════════════════════════════════════

async def test_cross_user_profile(client: httpx.AsyncClient):
    """Lehrer A versucht Profil von Lehrer B abzurufen."""
    # Login as demo teacher to get their ID
    r = await client.post(f"{BASE_URL}/api/auth/login", json={"password": "demo123"})
    if r.status_code != 200:
        return "SKIP: demo teacher not available"
    other_id = r.json()["teacher_id"]
    
    # Try to access other's profile with our header
    r = await client.get(
        f"{BASE_URL}/api/profile/{other_id}",
        headers=headers(TEST_TEACHER_ID),
    )
    assert r.status_code in (403, 404), f"Expected 403/404, got {r.status_code}"
    return f"Blocked access to {other_id[:8]}..."


async def test_cross_user_conversations(client: httpx.AsyncClient):
    """Lehrer A versucht Conversation-History von Lehrer B zu laden."""
    # Get our own conversations first
    r = await client.get(
        f"{BASE_URL}/api/chat/conversations",
        headers=headers(TEST_TEACHER_ID),
    )
    if r.status_code != 200 or not r.json():
        return "SKIP: no conversations to test"
    
    our_conv_id = r.json()[0]["id"]
    
    # Login as demo to get their ID
    r2 = await client.post(f"{BASE_URL}/api/auth/login", json={"password": "demo123"})
    if r2.status_code != 200:
        return "SKIP: demo teacher not available"
    other_id = r2.json()["teacher_id"]
    
    # Other teacher tries to access our conversation
    r3 = await client.get(
        f"{BASE_URL}/api/chat/history?conversation_id={our_conv_id}",
        headers=headers(other_id),
    )
    assert r3.status_code in (403, 404), f"Expected 403/404, got {r3.status_code}"
    return "Cross-user conversation access blocked"


# ═══════════════════════════════════════════════════
# 3. CHAT
# ═══════════════════════════════════════════════════

async def test_chat_send(client: httpx.AsyncClient) -> str:
    """Sende eine Nachricht und prüfe Antwort."""
    r = await client.post(
        f"{BASE_URL}/api/chat/send",
        headers=headers(),
        json={
            "message": "Antworte nur mit dem Wort 'Ping'.",
            "conversation_id": None,
            "teacher_id": TEST_TEACHER_ID,
        },
        timeout=60,
    )
    assert r.status_code == 200, f"Chat send: {r.status_code} {r.text[:100]}"
    data = r.json()
    assert data.get("conversation_id"), "No conversation_id"
    assert data.get("message", {}).get("content"), "Empty response"
    content = data["message"]["content"]
    return f"Conv {data['conversation_id'][:8]}..., {len(content)} chars"


async def test_chat_empty_message(client: httpx.AsyncClient):
    """Leere Nachricht darf keinen 500er geben."""
    r = await client.post(
        f"{BASE_URL}/api/chat/send",
        headers=headers(),
        json={
            "message": "",
            "conversation_id": None,
            "teacher_id": TEST_TEACHER_ID,
        },
        timeout=30,
    )
    assert r.status_code in (400, 422), f"Expected 400/422 for empty message, got {r.status_code}"
    return f"{r.status_code} for empty message"


async def test_conversations_list(client: httpx.AsyncClient):
    r = await client.get(
        f"{BASE_URL}/api/chat/conversations",
        headers=headers(),
    )
    assert r.status_code == 200, f"Conversations: {r.status_code}"
    data = r.json()
    assert isinstance(data, list), "Expected list"
    return f"{len(data)} conversations"


# ═══════════════════════════════════════════════════
# 4. MEMORY SYSTEM
# ═══════════════════════════════════════════════════

async def test_memory_storage(client: httpx.AsyncClient):
    """Sende einen Fakt, prüfe ob Memory in DB ankommt."""
    unique_fact = f"smoke_test_{int(time.time())}"
    
    # Send message with unique fact
    r = await client.post(
        f"{BASE_URL}/api/chat/send",
        headers=headers(),
        json={
            "message": f"Merke dir bitte: Mein Lieblingswort ist {unique_fact}",
            "conversation_id": None,
            "teacher_id": TEST_TEACHER_ID,
        },
        timeout=60,
    )
    assert r.status_code == 200, f"Chat send: {r.status_code}"
    
    # Wait for async memory agent
    await asyncio.sleep(15)
    
    # Check DB directly via profile endpoint (memories are in system prompt)
    # We can't query memories directly via API, but we can check if a new chat knows it
    r2 = await client.post(
        f"{BASE_URL}/api/chat/send",
        headers=headers(),
        json={
            "message": f"Was ist mein Lieblingswort?",
            "conversation_id": None,  # New conversation!
            "teacher_id": TEST_TEACHER_ID,
        },
        timeout=60,
    )
    assert r2.status_code == 200, f"Recall: {r2.status_code}"
    content = r2.json().get("message", {}).get("content", "").lower()
    
    if unique_fact in content:
        return f"Memory recalled: '{unique_fact}' found in response"
    else:
        # Not a hard fail — LLM might paraphrase
        return f"WARN: '{unique_fact}' not literally found, but memory agent may have stored it"


# ═══════════════════════════════════════════════════
# 5. PROFILE
# ═══════════════════════════════════════════════════

async def test_profile_get(client: httpx.AsyncClient):
    r = await client.get(
        f"{BASE_URL}/api/profile/{TEST_TEACHER_ID}",
        headers=headers(),
    )
    assert r.status_code == 200, f"Profile: {r.status_code}"
    data = r.json()
    assert data.get("name"), "No name in profile"
    return f"Name: {data['name']}"


async def test_profile_update_integrity(client: httpx.AsyncClient):
    """Update EIN Feld, prüfe dass andere unverändert bleiben."""
    # Get current state
    r1 = await client.get(f"{BASE_URL}/api/profile/{TEST_TEACHER_ID}", headers=headers())
    before = r1.json()
    
    # Update only bundesland
    test_value = "Sachsen" if before.get("bundesland") != "Sachsen" else "Berlin"
    r2 = await client.patch(
        f"{BASE_URL}/api/profile/{TEST_TEACHER_ID}",
        headers=headers(),
        json={"bundesland": test_value},
    )
    assert r2.status_code == 200, f"Update: {r2.status_code}"
    
    # Verify only bundesland changed
    r3 = await client.get(f"{BASE_URL}/api/profile/{TEST_TEACHER_ID}", headers=headers())
    after = r3.json()
    
    assert after.get("bundesland") == test_value, f"bundesland not updated"
    assert after.get("name") == before.get("name"), f"name changed unexpectedly!"
    
    # Restore original
    await client.patch(
        f"{BASE_URL}/api/profile/{TEST_TEACHER_ID}",
        headers=headers(),
        json={"bundesland": before.get("bundesland")},
    )
    return f"Updated bundesland→{test_value}, name unchanged ✓, restored"


# ═══════════════════════════════════════════════════
# 6. MATERIAL GENERATION
# ═══════════════════════════════════════════════════

async def test_material_klausur(client: httpx.AsyncClient):
    """Klausur generieren + DOCX Download."""
    r = await client.post(
        f"{BASE_URL}/api/materials/generate",
        headers=headers(),
        json={
            "type": "klausur",
            "fach": "Physik",
            "klasse": "10",
            "thema": "Optik Brechung",
            "teacher_id": TEST_TEACHER_ID,
            "dauer_minuten": 45,
        },
        timeout=120,
    )
    assert r.status_code == 200, f"Material: {r.status_code} {r.text[:200]}"
    data = r.json()
    material_id = data.get("id")
    assert material_id, "No material ID"
    
    # Check DOCX download
    r2 = await client.get(
        f"{BASE_URL}/api/materials/{material_id}/docx",
        headers=headers(),
        timeout=30,
    )
    assert r2.status_code == 200, f"DOCX: {r2.status_code}"
    assert len(r2.content) > 5000, f"DOCX too small: {len(r2.content)} bytes"
    
    # Check structure
    content = data.get("content", {})
    aufgaben = content.get("aufgaben", [])
    assert len(aufgaben) >= 3, f"Only {len(aufgaben)} tasks"
    
    return f"ID={material_id[:8]}..., {len(aufgaben)} Aufgaben, DOCX={len(r2.content)}B"


# ═══════════════════════════════════════════════════
# 7. H5P EXERCISES
# ═══════════════════════════════════════════════════

async def test_h5p_access_code(client: httpx.AsyncClient):
    """Prüfe ob eine existierende Schülerseite erreichbar ist."""
    # Check known access code
    r = await client.get(
        f"{BASE_URL}/api/public/page/palme78",
        timeout=15,
    )
    if r.status_code == 404:
        return "SKIP: palme78 not found (test data missing)"
    assert r.status_code == 200, f"Page: {r.status_code}"
    data = r.json()
    assert data.get("exercises"), "No exercises on page"
    return f"{len(data['exercises'])} exercises on palme78"


# ═══════════════════════════════════════════════════
# 8. RESPONSE TIME MONITORING
# ═══════════════════════════════════════════════════

async def test_response_times(client: httpx.AsyncClient):
    """Prüfe ob Render aus dem Cold Start raus ist."""
    start = time.monotonic()
    r = await client.get(f"{BASE_URL}/api/health")
    health_ms = int((time.monotonic() - start) * 1000)
    
    start = time.monotonic()
    r = await client.get(f"{BASE_URL}/api/chat/conversations", headers=headers())
    conv_ms = int((time.monotonic() - start) * 1000)
    
    warnings = []
    if health_ms > 5000:
        warnings.append(f"health={health_ms}ms (Cold Start?)")
    if conv_ms > 3000:
        warnings.append(f"conversations={conv_ms}ms (slow)")
    
    if warnings:
        return f"WARN: {', '.join(warnings)}"
    return f"health={health_ms}ms, conversations={conv_ms}ms"


# ═══════════════════════════════════════════════════
# 9. MEMORY COUNT MONITORING
# ═══════════════════════════════════════════════════

async def test_memory_count(client: httpx.AsyncClient):
    """Warnung wenn Memory-Count zu hoch (Cleanup nötig)."""
    # We can't query memories directly, but we can trigger cleanup
    r = await client.post(
        f"{BASE_URL}/api/admin/memory-cleanup",
        params={"teacher_id": TEST_TEACHER_ID},
        timeout=30,
    )
    if r.status_code != 200:
        return f"SKIP: cleanup endpoint returned {r.status_code}"
    data = r.json()
    stats = data.get("stats", {})
    removed = sum(stats.values())
    if removed > 10:
        return f"WARN: Cleaned {removed} entries (dupes={stats.get('duplicates_removed',0)}, merged={stats.get('merged',0)})"
    return f"Clean: only {removed} entries cleaned up"


# ═══════════════════════════════════════════════════
# NEW TESTS
# ═══════════════════════════════════════════════════

async def test_sql_injection(client: httpx.AsyncClient):
    """Sende SQL-Injection-String als X-Teacher-ID, erwarte keinen 500er."""
    sql_injection_id = "'; DROP TABLE users; --"
    r = await client.get(
        f"{BASE_URL}/api/health",
        headers=headers(teacher_id=sql_injection_id),
    )
    assert r.status_code != 500, f"SQL Injection with {sql_injection_id} caused 500"
    return f"No 500 for SQL injection (got {r.status_code})"

async def test_conversation_delete(client: httpx.AsyncClient):
    """Erstelle Konversation, lösche sie, prüfe ob sie weg ist."""
    # 1. Create a conversation
    r_create = await client.post(
        f"{BASE_URL}/api/chat/send",
        headers=headers(),
        json={
            "message": "Testnachricht für Löschtest.",
            "conversation_id": None,
            "teacher_id": TEST_TEACHER_ID,
        },
        timeout=60,
    )
    assert r_create.status_code == 200, f"Create conversation failed: {r_create.status_code}"
    conversation_id = r_create.json()["conversation_id"]
    assert conversation_id, "No conversation_id returned"

    # 2. Delete the conversation
    r_delete = await client.delete(
        f"{BASE_URL}/api/chat/conversations/{conversation_id}",
        headers=headers(),
        timeout=30,
    )
    assert r_delete.status_code == 200, f"Delete conversation failed: {r_delete.status_code}"
    
    # 3. Verify it's gone (try to get history, expect 403/404)
    r_verify = await client.get(
        f"{BASE_URL}/api/chat/history?conversation_id={conversation_id}",
        headers=headers(),
        timeout=30,
    )
    assert r_verify.status_code in (403, 404), f"Expected 403/404 after delete, got {r_verify.status_code}"
    return f"Conversation {conversation_id[:8]}... deleted and verified gone"

async def test_curriculum_list(client: httpx.AsyncClient):
    """GET curriculum list returns list structure."""
    r = await client.get(
        f"{BASE_URL}/api/curriculum/list?teacher_id={TEST_TEACHER_ID}",
        headers=headers(),
        timeout=30,
    )
    assert r.status_code == 200, f"Curriculum list: {r.status_code}"
    data = r.json()
    assert isinstance(data, list), "Expected list for curriculum list"
    return f"{len(data)} curricula listed"

async def test_cors_headers(client: httpx.AsyncClient):
    """Prüfe Access-Control-Headers via OPTIONS preflight."""
    r = await client.options(
        f"{BASE_URL}/api/health",
        headers={"Origin": "https://eduhu-assistant.pages.dev", "Access-Control-Request-Method": "GET"},
    )
    # CORS middleware should respond to preflight
    has_cors = "access-control-allow-origin" in r.headers
    if not has_cors:
        # Some setups only add CORS headers on actual requests
        r2 = await client.get(
            f"{BASE_URL}/api/health",
            headers={"Origin": "https://eduhu-assistant.pages.dev"},
        )
        has_cors = "access-control-allow-origin" in r2.headers
    
    assert has_cors, "No CORS headers on preflight or GET"
    return "CORS headers present"

async def test_long_message(client: httpx.AsyncClient):
    """Sende >10000 Zeichen Nachricht, erwarte keinen Crash (non-500)."""
    long_message = "A" * 10001  # > 10000 characters
    r = await client.post(
        f"{BASE_URL}/api/chat/send",
        headers=headers(),
        json={
            "message": long_message,
            "conversation_id": None,
            "teacher_id": TEST_TEACHER_ID,
        },
        timeout=60,
    )
    assert r.status_code != 500, f"Long message caused 500: {r.status_code}"
    return f"Long message handled (got {r.status_code})"

async def test_invalid_conversation_id(client: httpx.AsyncClient):
    """Sende Chat mit conversation_id='not-a-uuid', erwarte 4xx."""
    r = await client.post(
        f"{BASE_URL}/api/chat/send",
        headers=headers(),
        json={
            "message": "Test with invalid conversation ID",
            "conversation_id": "not-a-uuid",
            "teacher_id": TEST_TEACHER_ID,
        },
        timeout=30,
    )
    assert r.status_code >= 400 and r.status_code < 500, f"Expected 4xx for invalid conversation_id, got {r.status_code}"
    return f"Invalid conversation_id handled (got {r.status_code})"

# ═══════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════

async def main():
    base = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].startswith("http") else BASE_URL
    
    print(f"🔬 eduhu-assistant Smoke Tests")
    print(f"   Target: {base}")
    print(f"   Time:   {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'─' * 60}")
    
    async with httpx.AsyncClient(timeout=30) as client:
        # Fast tests first
        await timed("1. Health Check", test_health(client))
        await timed("2. Login (valid)", test_login_valid(client))
        await timed("3. Login (invalid)", test_login_invalid(client))
        await timed("4. No Auth Header → 401", test_no_auth_header(client))
        await timed("5. Cross-User Profile", test_cross_user_profile(client))
        await timed("6. Cross-User Conversations", test_cross_user_conversations(client))
        await timed("7. Conversations List", test_conversations_list(client))
        await timed("8. Profile Get", test_profile_get(client))
        await timed("9. Profile Update Integrity", test_profile_update_integrity(client))
        await timed("10. Response Times", test_response_times(client))
        await timed("11. H5P Access Code", test_h5p_access_code(client))
        await timed("12. Memory Cleanup", test_memory_count(client))
        await timed("13. SQL Injection", test_sql_injection(client))
        await timed("14. Conversation Delete", test_conversation_delete(client))
        await timed("15. Curriculum List", test_curriculum_list(client))
        await timed("16. CORS Headers", test_cors_headers(client))
        await timed("17. Long Message", test_long_message(client))
        await timed("18. Invalid Conversation ID", test_invalid_conversation_id(client))
        
        # Slow tests (LLM calls)
        await timed("19. Chat Send + Response", test_chat_send(client))
        await timed("20. Chat Empty Message", test_chat_empty_message(client))
        
        # Very slow tests (multiple LLM calls)
        # await timed("15. Material Klausur + DOCX", test_material_klausur(client))
        # await timed("16. Memory Storage + Recall", test_memory_storage(client))
    
    print(f"{'─' * 60}")
    for r in results:
        print(r)
    
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    skipped = sum(1 for r in results if "SKIP" in r.detail)
    total_ms = sum(r.duration_ms for r in results)
    
    print(f"{'─' * 60}")
    print(f"{'✅' if failed == 0 else '❌'} {passed}/{len(results)} passed, {failed} failed, {skipped} skipped ({total_ms}ms total)")
    
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    asyncio.run(main())
