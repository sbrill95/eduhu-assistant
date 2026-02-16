# MiniMax 2.5 — Code Quality Plan Review

# Code Quality Plan Review — eduhu-assistant

## 1. Vollständigkeit des Plans

Der Plan ist **strukturiert und gut durchdacht**, erfasst aber nicht alle kritischen Bereiche. Folgende Lücken fallen auf:

### Fehlende Prüfungen

| Bereich | Fehlt |
|---------|-------|
| **Supabase RLS** | Keine Erwähnung von Row Level Security Policies. Die `db.py` nutzt `supabase_service_role_key` – damit werden RLS komplett umgangen. Wer prüft, ob RLS правильно konfiguriert ist? |
| **Agent-Specific Logging** | Keine Prüfung auf **Prompt Injection** oder **System Prompt Leakage** – kritisch bei KI-Agents |
| **Knowledge Base Isolation** | Keine Prüfung, ob Daten zwischen Lehrern isoliert bleiben (Agent `knowledge.py` – was passiert bei falscher Teacher-ID?) |
| **Dependency Vulnerabilities** | Kein `pip-audit` oder `npm audit` – bei 90% KI-generiertem Code sind veraltete Dependencies wahrscheinlich |
| **Cron/Background Jobs** | Der Plan deckt API-Endpoints ab, aber nicht `memory_cleanup`, `knowledge_cleanup` – diese laufen manuell/admin-seitig |

---

## 2. TOP 5 – Konkrete Probleme die JETZT gefixt werden müssen

Basierend auf dem Code aus `deps.py`, `db.py`, `chat.py`:

### 🔴 P0-1: Auth-System ist unsicher (deps.py)

```python
async def get_current_teacher_id(
    request: Request, 
    x_teacher_id: str | None = Security(api_key_header)
) -> str:
    if not x_teacher_id:
        raise HTTPException(status_code=401, ...)
    return x_teacher_id  # Keine Verifikation!
```

**Problem:** Der Header `X-Teacher-ID` wird **nicht verifiziert**. Jeder Client kann sich als beliebiger Lehrer ausgeben. Die auskommentierte DB-Prüfung fehlt.

**Fix:** JWT aus `Authorization: Bearer <token>` dekodieren oder Teacher-ID gegen DB verifizieren.

---

### 🔴 P0-2: Hardcoded Admin Secret (deps.py)

```python
expected = os.environ.get("ADMIN_SECRET", "cleanup-2026")
```

**Problem:** Fallback-Secret im Code. Wenn Env-Var nicht gesetzt, ist Admin-Secret trivial erratbar.

**Fix:** Application Startup mit `raise ValueError` wenn `ADMIN_SECRET` fehlt.

---

### 🔴 P0-3: Service Role Key umgeht RLS (db.py)

```python
def _headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    h = {
        "apikey": s.supabase_service_role_key,  # RLS wird umgangen!
        "Authorization": f"Bearer {s.supabase_service_role_key}",
```

**Problem:** Alle DB-Operations nutzen `service_role_key`. Das bedeutet:
- Keine Isolation zwischen Lehrern
- Jeder Admin-Endpoint kann alle Daten lesen/schreiben
- RLS-Policies werden nie getestet

**Fix:** Service Role nur für Admin-Operations nutzen; für User-Data anon-Key mit RLS.

---

### 🟠 P1-4: Stilles Fehler-Schlucken (chat.py)

```python
except Exception as e:
    logger.error(f"Agent error: {type(e).__name__}: {e}", exc_info=True)
    raise HTTPException(500, f"KI-Antwort fehlgeschlagen: {type(e).__name__}")
```

**Problem:** Original-Fehler wird nicht zurückgegeben. User sieht nur generische Meldung; Debugging ist unmöglich.

**Fix:** Mindestens `detail=str(e)` oder einen Error-Code zurückgeben.

---

### 🟠 P5-5: SSE Stream ohne Client-Disconnect-Handling (chat.py)

Im Stream-Endpoint fehlt:
- Kein `await request.cliente.disconnect` Check
- Kein `try/finally` für Resource-Cleanup
- Agent läuft weiter, auch wenn Client weg ist

---

## 3. Falsch priorisierte / überflüssige Stufen

| Stufe | Problem | Empfehlung |
|-------|---------|------------|
| **Stufe 5 (Typ-Sicherheit)** | Niedrig priorisiert, aber bei 90% KI-Code kritisch. KI neigt zu `Any`, `dict` ohne Typ-Parameter | **Vorziehen** auf Stufe 2-3 |
| **Stufe 8 (Performance)** | Nimmt an, dass System funktioniert. Bei 12 Agents + SSE + DB sind Performance-Probleme aber sekundär | Erst nach Stufe 3 (Error Handling) sinnvoll |
| **Stufe 9 (Frontend UX)** | Gut, aber **vor** Stufe 7 (Concurrency) fehlplatziert. Race Conditions cause mehr Bugs als fehlende Loading-Spinner | Reihenfolge: 1→2→3→4→**7**→5→6→9→8→10 |
| **Stufe 10 (E2E)** | Gut am Ende, aber **ohne stabile API** (Stufe 6) sinnlos | Korrekt am Ende |

**Korrigierte Priorisierung:**
1. **SOFORT:** Security (2) → Error Handling (3) → Dead Code (4)
2. **DIESE WOCHE:** Concurrency (7) → Type Safety (5)
3. **VOR BETA:** API Contracts (6) → Frontend UX (9)
4. **ITERATIV:** Performance (8) → E2E (10)

---

## 4. Agent-spezifische Fehlerquellen die fehlen

Der Plan listet bekannte Agent-Fehler, deckt aber folgende **nicht** ab:

### 1. **System Prompt Leakage**
Wenn der Agent im Response unbeabsichtigt Teile des System-Prompts zurückgibt. Prüfen: Regex-Match auf typische Prompt-Marker (`"Du bist"`, `"Du sollst"`, `<system>`).

### 2. **Tool Definition Drift**
Die 12 Agents haben verschiedene Tools. Keine Prüfung ob:
- Tool-Parameter tatsächlich zum Schema passen
- Fehlende Required-Fields zu Runtime-Fehlern führen
- Veraltete Tool-Definitionen (Agent aktualisiert, Frontend nicht)

### 3. **Memory Agent Race Conditions**
`run_memory_agent` wird fire-and-forget gestartet. Was passiert bei:
- Gleichzeitigen Requests desselben Lehrers?
- Konflikt beim Schreiben in `agent_knowledge`?

### 4. **Knowledge Base Cross-Contamination**
Prüfen: Kann Teacher A durch manipulierte Inputs Daten in Teacher Bs Knowledge Base schreiben?

### 5. **Rate Limiting pro Modell**
12 Agents → mehrere API-Calls. Keine Erwähnung von:
- Rate Limit Detection (429 Handling)
- Fallback zu günstigeren Modellen
- Queue/Retry-Logic

### 6. **SSE Memory Leaks**
Bei `agent.run_stream_events()`: Wenn Client disconnected, läuft Stream evtl. weiter. Kein `async with` oder Cancellation-Handling.

---

## Fazit

Der Plan ist **ein guter Start**, aber für 90% KI-generierten Code zu wenig fokussiert auf:
1. **Security-First** (Auth, RLS, Secrets)
2. **Agent-Spezifika** (Prompts, Tools, Isolation)
3. **Concurrency** (Fire-and-forget Tasks)

**Empfohlene erste Aktionen:**
- `deps.py` fixen (JWT-Verifikation + Admin-Secret)
- `db.py` auf anon-Key + RLS umstellen
- Error-Responses mit Detail-Informationen versehen
- Startup-Checks für fehlende Env-Vars einbauen

Dann kann der Plan abgearbeitet werden – in der korrigierten Priorisierung.