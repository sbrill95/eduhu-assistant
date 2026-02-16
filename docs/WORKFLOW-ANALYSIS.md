# Workflow-Analyse: Längere Szenarien

## Szenario 1: Lehrer mit 50+ Nachrichten in einer Konversation

**Flow:** User → chat/send → DB (last 20 msgs) → System Prompt (50 memories) → Agent → Response

**Probleme:**
1. **History-Limit = 20 Messages:** Nur die letzten 20 werden geladen. Bei Turn 25 hat der Agent keinen Kontext mehr von Turn 1-5. 
   - **Mitigation:** `maybe_summarize()` läuft bei >10 Messages, aber die Summary wird NICHT in den Agent-Kontext eingebaut — sie wird nur in `session_logs` gespeichert und nie gelesen!
   - **Fix nötig:** Summary als Teil des System-Prompts oder als erstes Message in die History einbauen.

2. **Token-Budget:** 20 Messages × ~500 Tokens + System Prompt (~2K) + 50 Memories (~850 Tokens) = ~13K Input-Tokens. Machbar für Sonnet (200K Kontext), aber bei Tool-Calls mit langen Outputs (Material, DOCX) kann es 30-50K werden.
   - **Risiko:** Gering, Sonnet handled das.

3. **Memory-Agent Fire-and-Forget:** Bei 50 Nachrichten wird der Memory-Agent 50x getriggert. Jeder Call erzeugt Haiku-API-Kosten + DB-Writes.
   - **Risiko:** Memory-Duplikation (bekanntes Problem, 231→174 nach Cleanup)
   - **Fix:** Memory-Agent nur alle 5 Nachrichten triggern, nicht bei jeder.

## Szenario 2: Material erstellen → iterieren → nochmal → nochmal (5+ Iterationen)

**Flow:** generate_material → agent_sessions (state) → continue_material × N

**Probleme:**
1. **agent_sessions wachsen:** Jede Iteration speichert die komplette `material_structure` (kann 5-10KB JSON sein). Nach 5 Iterationen = 50KB in agent_sessions.
   - **Risiko:** Gering für DB, aber der GESAMTE vorherige Output wird als Kontext an den Sub-Agent geschickt.
   - **Problem:** Bei Iteration 5 bekommt der Sub-Agent den Output von Iteration 4 als Kontext + Feedback. Das sind ~10K Tokens nur für den Kontext. Plus System-Prompt + Wissenskarte = 15K+.

2. **Session-Findung:** `continue_material` sucht die "latest active session". Was wenn der Lehrer zwischendurch ein anderes Material erstellt?
   - **Bug:** Es wird das LETZTE Material gefunden, nicht das worauf sich "ändere Aufgabe 2" bezieht.
   - **Fix:** Session-ID im Chat-Kontext mitführen oder explizit referenzieren.

3. **DOCX wird jedes Mal neu in DB gespeichert:** Jede Iteration = neuer base64-Blob in `generated_materials`. Bei 5 Iterationen = 5 × 38KB = 190KB in PostgreSQL.
   - **Langfristig:** Supabase Storage statt DB.

## Szenario 3: Lehrer hat 10 Konversationen, wechselt ständig

**Flow:** Sidebar → load conversation → load history → send message

**Probleme:**
1. **Memory ist konversationsübergreifend:** Gut — Memory bleibt über Konversationen hinweg.
2. **agent_sessions sind konversationsunabhängig:** `continue_material` sucht nach teacher_id, nicht nach conversation_id.
   - **Bug:** Lehrer erstellt Klausur in Konversation A, wechselt zu Konversation B, sagt "ändere Aufgabe 2" → findet die Klausur aus A.
   - **Das ist actually ein Feature** — aber unklar für den Lehrer.

3. **Conversation Sidebar:** Lädt nur Titel + updated_at. Kein Indikator ob Material-Sessions aktiv sind.

## Szenario 4: Zwei Lehrer gleichzeitig (Christopher + Michelle)

**Probleme:**
1. **Kein Rate Limiting:** Beide schicken gleichzeitig Material-Requests. Beide triggern Sonnet-API-Calls. Bei Anthropic-Rate-Limit (50 RPM) → einer wartet.
   - **Kein 429-Handling im Code** — Agent crasht mit unhandled error.
   - **Fix:** Retry-Logic mit exponential backoff.

2. **Memory-Agent Race:** Beide schreiben gleichzeitig Memories. Supabase upsert auf `user_memories` ist safe (different teacher_ids), ABER:
   - `agent_knowledge` hat `scope_type=teacher, scope_id=teacher_id` — korrekt isoliert.
   - **Kein Problem** bei unterschiedlichen Lehrern.

3. **Knowledge Cleanup:** Wenn beide gleichzeitig Material erstellen, triggert der Learning-Agent für beide. Bulk-Writes an `agent_knowledge` sind unkoordiniert.
   - **Risiko:** Gering, da scope isoliert.

## Szenario 5: Lehrer lädt 5 PDFs hoch + chattet gleichzeitig

**Flow:** Upload → Claude Vision / PyMuPDF → Text extraction → Chat

**Probleme:**
1. **File Upload ist synchron:** Der Upload-Handler extrahiert Text und sendet alles als eine Nachricht. Kein Queuing.
   - **Risiko:** Große PDFs (50+ Seiten) → lange Extraktion → Timeout.
   - **Fix:** Max File Size prüfen (aktuell kein Limit?).

2. **Vision API Kosten:** Jedes Bild → Claude Vision Call. 5 Bilder = 5 API-Calls vor dem eigentlichen Chat.

## Szenario 6: H5P Übungen mit 100 Schülern gleichzeitig

**Flow:** Schüler → /s/{code} → Frontend → /api/public/h5p/{id}/h5p.json + content.json

**Probleme:**
1. **Jeder Schüler-Pageload = 2 Supabase REST Calls** (h5p.json + content.json).
   - Bei 100 Schülern = 200 DB-Calls in kurzer Zeit.
   - **Render Free Tier:** Single Worker, ~100 concurrent connections max.
   - **Fix:** Static JSON-Files servieren oder CDN-Cache.

2. **Kein Caching:** Weder Backend noch Cloudflare cached die H5P-Responses.
   - **Fix:** `Cache-Control: public, max-age=3600` Header setzen — H5P-Content ändert sich nicht.

## Szenario 7: Lehrplan-Upload (großes PDF) + sofort RAG-Suche

**Flow:** Upload PDF → PyMuPDF extract → Chunk → Embed → pgvector → Suche

**Probleme:**
1. **Ingestion ist synchron:** Upload-Endpoint wartet bis alle Chunks embedded + gespeichert sind.
   - Bei 300-Seiten-PDF = 200+ Chunks × OpenAI Embedding Call = 2-3 Minuten.
   - **User sieht**: Spinner. Timeout möglich.
   - **Fix:** Background-Task mit Status-Polling.

2. **Embedding-Kosten:** `text-embedding-3-small` ist billig ($0.02/1M tokens), aber bei 200 Chunks × 500 Tokens = 100K Tokens = $0.002. Vernachlässigbar.

---

## Zusammenfassung: TOP 5 Workflow-Risiken

| # | Risiko | Schwere | Fix-Aufwand |
|---|--------|---------|-------------|
| 1 | **Summary wird nie gelesen** — nach 20+ Nachrichten fehlt Kontext | P0 | Klein — Summary in System-Prompt einbauen |
| 2 | **continue_material findet falsches Material** — keine conversation_id-Bindung | P1 | Mittel — Session an Konversation binden |
| 3 | **Kein 429 Retry** bei Anthropic Rate Limit | P1 | Klein — tenacity/backoff Decorator |
| 4 | **H5P kein Caching** — 100 Schüler = 200 DB-Calls | P2 | Klein — Cache-Header setzen |
| 5 | **Memory-Agent bei JEDER Nachricht** — unnötige Kosten + Duplikation | P2 | Klein — nur alle 5 Nachrichten |
