# Overnight Plan — 2026-02-16

## Steffens Aufträge (gesammelt aus der Session)

### Neue Features (heute gebaut)
1. ✅ **Visuelle Todo-Cards** im Chat (todo-card Code-Block → React Component)
2. ✅ **Visuelle QR-Cards** im Chat (qr-card Code-Block → React Component)
3. ✅ **Diktier-Button** (🎤 Mic → Whisper → Text)
4. ✅ **Interaktive Checkboxen** (Todos abhaken)
5. ✅ **Neues Todo hinzufügen** direkt in der Card
6. ✅ **Datumspicker** beim Todo-Hinzufügen
7. ✅ **Sekundärfarben** aus Pitch Deck (sage, salmon, gold, sky)

### Bugs gefixt
1. ✅ TypeScript Build-Errors (blockierten Cloudflare Deploy)
2. ✅ `settings` → `get_settings()` Import-Fehler
3. ✅ Regex `\w+` → `[\w-]+` für todo-card/qr-card Erkennung
4. ✅ System-Prompt: Agent muss Code-Blocks durchreichen
5. ✅ SSE Streaming Cutoff (PartStartEvent fehlte)
6. ✅ CSS var() mit /opacity funktioniert nicht in Tailwind
7. ✅ Volle UUIDs statt gekürzte 8-Char IDs
8. 🔧 Schwarzer Hintergrund (pre-Wrapper) → Fix gepusht, noch zu verifizieren

### Noch offen (Steffens Wünsche)
- [ ] **Farbsystem nochmal sauber durchziehen** (Steffen schickt nochmal Details)
- [ ] **Scope definieren**: Was soll die App können? Feature-Liste
- [ ] **Alles selbst testen** mit Gemini/MiniMax
- [ ] **Iterieren bis perfekt** — Prototyp muss morgen früh einwandfrei laufen

## Testplan

### 1. Frontend Visual Tests (Playwright)
- [ ] Login funktioniert
- [ ] Chat-Eingabe: 📎 Attach, 🎤 Mic, Textarea, ⬆ Send — alle sichtbar
- [ ] Todo: "Zeige meine Todos" → Card rendert (NICHT raw JSON)
- [ ] Todo: Card hat weißen Hintergrund (kein schwarz)
- [ ] Todo: Checkbox klickbar, togglet ✅/☐
- [ ] Todo: Neues Todo hinzufügen via ＋ Feld
- [ ] Todo: Datumspicker funktioniert
- [ ] H5P: Übung erstellen → QR-Card rendert
- [ ] SSE Streaming: Antwort beginnt vollständig (kein abgeschnittener Anfang)

### 2. Backend API Tests
- [ ] POST /api/transcribe — Endpoint existiert (nicht 404)
- [ ] GET /api/todos — Returns todo list
- [ ] POST /api/todos — Creates todo with due_date
- [ ] PATCH /api/todos/{id} — Toggles done
- [ ] POST /api/chat/send-stream — SSE stream, erster Delta enthält vollen Text
- [ ] POST /api/chat/send — Non-streaming fallback works

### 3. E2E Flows
- [ ] Login → Chat → "Erstelle eine Physik-Übung für Klasse 8" → QR-Card
- [ ] Login → Chat → "Erstelle mir eine Klausur" → Schärfungsfragen → Material + DOCX Link
- [ ] Login → Chat → "Erinnere mich an Elternabend" → Todo-Card
- [ ] Login → Chat → Todo abhaken → Card updated
- [ ] Login → Chat → Neues Todo in Card hinzufügen → erscheint

## Execution Order
1. Warte auf Render + Cloudflare Deploy (~10 Min)
2. Playwright Visual Tests
3. API Tests via curl
4. Gemini Pro Review des gesamten Codes
5. Fixes iterieren
6. Finale E2E Tests
7. Zusammenfassung für Steffen
