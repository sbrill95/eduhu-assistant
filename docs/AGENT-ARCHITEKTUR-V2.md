# Agent-Architektur V2 — Wissenskarte + Multi-Turn Subagents

## Vision

Jeder Material-Agent (Klausur, Differenzierung, H5P) wird ein **autonomer Experte** mit eigenem Gedächtnis, Lazy-Loading-Tools und der Fähigkeit, Rückfragen zu stellen — ohne den bisherigen Kontext zu verlieren.

## Architektur-Übersicht

```
┌──────────────────────────────────────────────────────┐
│                    USER (Lehrer)                      │
└────────────────────────┬─────────────────────────────┘
                         │ Chat
                         ▼
┌──────────────────────────────────────────────────────┐
│              HAUPTAGENT (Sonnet)                      │
│                                                       │
│  Aufgaben:                                            │
│  - Gespräch führen                                    │
│  - Schärfungsfragen stellen                           │
│  - Auftrag formulieren (strukturiert + Freitext)      │
│  - Rückfragen vom Subagent an User weiterleiten       │
│  - Ergebnis präsentieren                              │
│                                                       │
│  Tools: remember, search_web, generate_material,      │
│         generate_exercise, patch_material_task         │
└────────────────────────┬─────────────────────────────┘
                         │ Tool-Call: generate_material(
                         │   fach, klasse, thema,
                         │   material_type, dauer,
                         │   zusatz_anweisungen)
                         ▼
┌──────────────────────────────────────────────────────┐
│              MATERIAL-ROUTER                          │
│              (Python, kein LLM)                       │
│                                                       │
│  1. Wissenskarte laden (SQL-Aggregation)              │
│  2. Teacher-Preferences laden (SQL)                   │
│  3. Subagent wählen (klausur/diff/h5p)                │
│  4. Subagent starten mit Kontext                      │
│  5. Multi-Turn-Loop verwalten                         │
│     → Rückfrage? → An Hauptagent zurückgeben          │
│     → Antwort? → Agent weiter mit message_history     │
│  6. Ergebnis → DOCX → Speichern → Return              │
└────────────────────────┬─────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│          KLAUSUR-AGENT (Sonnet, mit Tools)            │
│                                                       │
│  Bekommt:                                             │
│  - Strukturierter Auftrag (Parameter)                 │
│  - Wissenskarte (kompakter Index)                     │
│  - Teacher-Preferences                                │
│                                                       │
│  Tools (Lazy Loading):                                │
│  - get_full_context(conversation_id)                  │
│    → Letzten Chat-Verlauf nachlesen                   │
│  - search_curriculum(query)                           │
│    → Lehrplan-RAG (pgvector)                          │
│  - get_good_practices(fach, thema, afb_level, limit)  │
│    → Bewährte Aufgaben (pgvector)                     │
│  - get_example(fach, thema)                           │
│    → Lehrer-Upload laden                              │
│  - get_upload(upload_id)                              │
│    → Einzelne Datei/Bild aus Chat                     │
│                                                       │
│  Kann:                                                │
│  - Klausur generieren (ExamStructure)                 │
│  - ODER: Rückfrage stellen (ClarificationRequest)     │
│                                                       │
│  Multi-Turn: message_history bleibt erhalten          │
│  → Kein doppeltes RAG, kein Kontextverlust            │
└──────────────────────────────────────────────────────┘
```

## Datenmodell

### Neue Tabelle: `agent_knowledge`

```sql
CREATE TABLE agent_knowledge (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Zuordnung
  agent_type TEXT NOT NULL,              -- 'klausur', 'differenzierung', 'h5p'
  teacher_id UUID REFERENCES user_profiles(id),  -- NULL = global/generisch
  
  -- Inhalt
  fach TEXT NOT NULL,                    -- 'physik', 'biologie', 'deutsch'
  thema TEXT,                            -- Optional, NULL = fach-weit
  knowledge_type TEXT NOT NULL,          -- 'generic', 'example', 'good_practice', 'preference'
  
  -- Payload
  content JSONB NOT NULL,               -- Strukturierter Inhalt
  description TEXT,                      -- Menschenlesbare Kurzbeschreibung
  
  -- Qualität & Nutzung
  quality_score FLOAT DEFAULT 0.5,       -- 0.0-1.0
  times_used INT DEFAULT 0,
  source TEXT NOT NULL,                  -- 'system', 'upload', 'generated', 'conversation'
  
  -- RAG (für Good Practice Suche)
  embedding vector(1536),               -- text-embedding-3-small
  
  -- Meta
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indices
CREATE INDEX idx_ak_teacher ON agent_knowledge(teacher_id);
CREATE INDEX idx_ak_fach ON agent_knowledge(fach, thema);
CREATE INDEX idx_ak_type ON agent_knowledge(agent_type, knowledge_type);
CREATE INDEX idx_ak_quality ON agent_knowledge(quality_score DESC);
CREATE INDEX idx_ak_embedding ON agent_knowledge 
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 20);
```

### Wissenstypen

| knowledge_type | source | teacher_id | Beschreibung |
|---|---|---|---|
| `generic` | `system` | NULL | Von uns gepflegte Fach-Defaults ("So sieht eine gute Physik-Klausur aus") |
| `generic` | `system` | NULL | Wird ggf. überschrieben wenn wir aus Nutzerverhalten bessere Muster erkennen |
| `example` | `upload` | teacher_id | Vom Lehrer hochgeladene Beispiel-Klausur, -Aufgabe, -Seite |
| `good_practice` | `generated` | teacher_id | Vom Lehrer positiv bewertete generierte Aufgaben |
| `good_practice` | `system` | NULL | Von uns kuratierte Best-Practice-Beispiele |
| `preference` | `conversation` | teacher_id | Extrahierte Lehrer-Präferenzen pro Fach |

### Content-Beispiele (JSONB)

**Generic — Physik-Klausur-Profil:**
```json
{
  "beschreibung": "Physik-Klausuren basieren auf Berechnungen und Theorieaufgaben.",
  "aufgabenformate": ["Berechnung mit Einheiten", "Diagramm auswerten", "Experiment bewerten", "Formel herleiten"],
  "afb_operatoren": {
    "I": ["Nennen", "Angeben", "Beschreiben", "Berechnen (Einsetzen)"],
    "II": ["Erklären", "Berechnen (Herleitung)", "Vergleichen", "Analysieren (Diagramm)"],
    "III": ["Beurteilen", "Entwickeln (Versuchsaufbau)", "Diskutieren (Modell)"]
  },
  "erwartungshorizont_stil": "calculation_steps",
  "typische_verteilung": {"rechnung": 60, "theorie": 30, "experiment": 10},
  "besonderheiten": [
    "Einheiten immer angeben und prüfen",
    "Formeln entweder bereitstellen oder herleiten lassen (nicht beides)",
    "Diagramme als Aufgabenmaterial einsetzen",
    "Physikalische Größen mit Formelzeichen und Einheit"
  ]
}
```

**Good Practice — Einzelne Aufgabe:**
```json
{
  "aufgabe": "Berechnen Sie den Brechungswinkel, wenn Licht unter einem Einfallswinkel von 30° von Luft (n=1,0) in Glas (n=1,5) übergeht.",
  "beschreibung": "Snellius-Aufgabe mit konkreten Werten",
  "afb_level": "II",
  "punkte": 8,
  "erwartung": [
    "Snellius-Gesetz: n₁·sin(α) = n₂·sin(β)",
    "Einsetzen: 1,0 · sin(30°) = 1,5 · sin(β)",
    "sin(β) = 0,5/1,5 = 0,333",
    "β = arcsin(0,333) ≈ 19,5°"
  ],
  "material_id": "uuid-der-original-klausur",
  "lehrer_rating": 5,
  "iteration_count": 0,
  "kontext": "Klasse 10, Optik, wurde ohne Änderung übernommen"
}
```

**Preference:**
```json
{
  "aufgaben_anzahl": 5,
  "teilaufgaben": true,
  "bonusaufgabe": false,
  "rechnung_theorie_ratio": "60:40",
  "notenschluessel": "standard",
  "stil": "Klare, kurze Aufgabenstellungen. Diagramme als Material.",
  "dinge_vermeiden": "Keine Multiple-Choice in Klausuren"
}
```

## Multi-Turn Subagent — Pydantic AI Implementierung

### Output-Typ mit Rückfrage-Option

```python
from pydantic import BaseModel
from typing import Optional

class ClarificationRequest(BaseModel):
    """Subagent braucht mehr Info vom Lehrer."""
    frage: str
    kontext: str  # Warum wird gefragt
    vorschlaege: list[str] = []  # Antwortoptionen

class KlausurResult(BaseModel):
    """Union-Type: Entweder Klausur ODER Rückfrage."""
    klausur: Optional[ExamStructure] = None
    clarification: Optional[ClarificationRequest] = None
    
    @property
    def needs_clarification(self) -> bool:
        return self.clarification is not None
```

### Multi-Turn Loop im Material-Router

```python
async def _generate_klausur(request: MaterialRequest) -> ExamStructure:
    agent = get_klausur_agent()  # Jetzt Sonnet, nicht Haiku
    
    # Kontext vorbereiten (kein LLM, nur DB)
    wissenskarte = await _build_wissenskarte(request.teacher_id, "klausur", request.fach)
    preferences = await _load_preferences(request.teacher_id, "klausur", request.fach)
    
    deps = KlausurDeps(
        teacher_id=request.teacher_id,
        conversation_id=request.conversation_id,  # NEU
        wissenskarte=wissenskarte,
        preferences=preferences,
    )
    
    prompt = _build_klausur_prompt(request)
    message_history = None
    
    # Multi-Turn Loop (max 3 Rückfragen)
    for turn in range(4):
        result = await agent.run(
            prompt,
            deps=deps,
            message_history=message_history,
        )
        
        output = result.output
        
        if not output.needs_clarification:
            # Klausur fertig!
            return output.klausur
        
        # Rückfrage → An Hauptagent zurückgeben
        # Der Hauptagent fragt den Lehrer und gibt uns die Antwort
        user_answer = await _relay_clarification(
            request.conversation_id,
            output.clarification,
        )
        
        # Weiter im selben Kontext
        prompt = user_answer
        message_history = result.all_messages()  # ← Alles bleibt erhalten
    
    raise TimeoutError("Zu viele Rückfragen")
```

### Agent System-Prompt (Klausur-Agent, Sonnet)

```python
KLAUSUR_SYSTEM_PROMPT = """\
Du bist ein Experte für Klassenarbeiten und Klausuren im deutschen Schulsystem.

## Dein Workflow
1. Lies den Auftrag und die Wissenskarte
2. Entscheide: Hast du genug Info? 
   → Nein: Stelle eine GEZIELTE Rückfrage (ClarificationRequest)
   → Ja: Weiter mit Schritt 3
3. Nutze deine Tools um Kontext zu laden:
   - get_full_context: Wenn du den Chat-Verlauf verstehen willst
   - search_curriculum: Wenn du Lehrplaninhalte brauchst
   - get_good_practices: Wenn du bewährte Aufgaben als Inspiration willst
   - get_example: Wenn der Lehrer ein Beispiel hochgeladen hat
4. Generiere die Klausur

## Rückfragen
- Stelle maximal 1-2 Rückfragen pro Durchgang
- Formuliere konkret mit Vorschlägen: 
  "Soll der Schwerpunkt auf Stromkreise (Ohm, Kirchhoff) oder 
   elektromagnetische Induktion liegen? Oder beides gleichmäßig?"
- Nutze dein Wissen über den Lehrer für intelligente Vorschläge

## Wissenskarte
{wissenskarte}

## Lehrer-Präferenzen
{preferences}

## AFB-Regeln
[... bestehender AFB-Prompt ...]
"""
```

## Wissenskarte — Aufbau & Darstellung

### SQL-Aggregation (kein LLM)

```python
async def _build_wissenskarte(teacher_id: str, agent_type: str, fach: str) -> str:
    """Baut die Wissenskarte als Text für den System-Prompt."""
    
    # Alle Einträge für diesen Lehrer + globale (teacher_id IS NULL)
    entries = await db.select(
        "agent_knowledge",
        filters={"agent_type": agent_type, "fach": fach},
        # Braucht erweiterten Filter: teacher_id = X OR teacher_id IS NULL
    )
    
    # Gruppieren nach knowledge_type
    generics = [e for e in entries if e["knowledge_type"] == "generic"]
    examples = [e for e in entries if e["knowledge_type"] == "example" and e.get("teacher_id") == teacher_id]
    good_practices = [e for e in entries if e["knowledge_type"] == "good_practice"]
    preferences = [e for e in entries if e["knowledge_type"] == "preference" and e.get("teacher_id") == teacher_id]
    
    parts = [f"### Wissensbasis: {fach.title()}"]
    
    if generics:
        g = generics[0]["content"]
        parts.append(f"**Fach-Profil:** {g.get('beschreibung', '')}")
        if g.get("aufgabenformate"):
            parts.append(f"Typische Formate: {', '.join(g['aufgabenformate'])}")
    
    if examples:
        parts.append(f"**{len(examples)} Beispiel(e) vom Lehrer** — nutze get_example() zum Laden")
    else:
        parts.append("**Keine Beispiele** vom Lehrer hochgeladen")
    
    teacher_gp = [g for g in good_practices if g.get("teacher_id") == teacher_id]
    global_gp = [g for g in good_practices if g.get("teacher_id") is None]
    if teacher_gp:
        parts.append(f"**{len(teacher_gp)} bewährte Aufgaben** (persönlich) — nutze get_good_practices()")
    if global_gp:
        parts.append(f"**{len(global_gp)} Good-Practice-Vorlagen** (allgemein)")
    if not teacher_gp and not global_gp:
        parts.append("**Keine Good-Practice-Aufgaben** vorhanden")
    
    if preferences:
        p = preferences[0]["content"]
        pref_items = [f"{k}: {v}" for k, v in p.items()]
        parts.append(f"**Präferenzen:** {', '.join(pref_items)}")
    
    return "\n".join(parts)
```

### Darstellung im Prompt (~100-200 Tokens)

```
### Wissensbasis: Physik
**Fach-Profil:** Physik-Klausuren basieren auf Berechnungen und Theorieaufgaben.
Typische Formate: Berechnung mit Einheiten, Diagramm auswerten, Experiment bewerten
**1 Beispiel** vom Lehrer — nutze get_example() zum Laden
**3 bewährte Aufgaben** (persönlich) — nutze get_good_practices()
**2 Good-Practice-Vorlagen** (allgemein)
**Präferenzen:** aufgaben_anzahl: 5, teilaufgaben: true, rechnung_theorie_ratio: 60:40
```

## Good-Practice-RAG

Für die Suche nach passenden bewährten Aufgaben nutzen wir dasselbe pgvector-Pattern wie bei Curriculum:

```python
# Supabase RPC Function
CREATE OR REPLACE FUNCTION match_good_practices(
  query_embedding vector(1536),
  p_teacher_id UUID,
  p_agent_type TEXT,
  p_fach TEXT,
  match_count INT DEFAULT 3
)
RETURNS TABLE (id UUID, content JSONB, description TEXT, quality_score FLOAT, similarity FLOAT)
AS $$
  SELECT id, content, description, quality_score,
         1 - (embedding <=> query_embedding) AS similarity
  FROM agent_knowledge
  WHERE knowledge_type = 'good_practice'
    AND agent_type = p_agent_type
    AND fach = p_fach
    AND (teacher_id = p_teacher_id OR teacher_id IS NULL)
    AND embedding IS NOT NULL
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
$$ LANGUAGE sql;
```

Tool im Klausur-Agent:
```python
@agent.tool
async def get_good_practices(ctx, fach: str, thema: str, limit: int = 3) -> str:
    """Lade bewährte Aufgaben als Inspiration. Nutze bei jeder Klausur-Erstellung."""
    embedding = await generate_embedding(f"{fach} {thema}")
    results = await db.rpc("match_good_practices", {
        "query_embedding": embedding,
        "p_teacher_id": ctx.deps.teacher_id,
        "p_agent_type": "klausur",
        "p_fach": fach,
        "match_count": limit,
    })
    if not results:
        return "Keine bewährten Aufgaben gefunden."
    
    parts = []
    for r in results:
        c = r["content"]
        parts.append(f"- {c['aufgabe']} (AFB {c['afb_level']}, {c['punkte']}P, Score {r['quality_score']:.1f})")
    return "Bewährte Aufgaben:\n" + "\n".join(parts)
```

## Vollständiger Flow — Walkthrough

### Szenario: "Ich brauche eine E-Lehre-Klausur für die 10a"

```
1. ONBOARDING (einmalig, schon passiert):
   - Lehrer hat Curriculum hochgeladen → ingestet → curriculum_chunks (pgvector)
   - Lehrer hat Profil: Physik, Klasse 10, Sachsen
   - Wissenskarte seeded: generisches Physik-Profil (von uns)

2. CHAT (Hauptagent, Sonnet):
   User: "Ich brauche ne Klausur E-Lehre für die 10a"
   
   Sonnet sieht in Memories: "Letzte Woche Optik-Klausur erstellt"
   Sonnet: "Für die 10a — soll der Schwerpunkt auf Stromkreise 
            (Ohm, Kirchhoff) oder elektromagnetische Induktion liegen?
            Dauer 45 oder 90 Minuten?"
   
   User: "Stromkreise, 45 Min, aber bitte eine Aufgabe Induktion als AFB III"
   
   Sonnet ruft auf: generate_material(
     fach="physik", klasse="10", thema="E-Lehre Stromkreise",
     material_type="klausur", dauer_minuten=45,
     zusatz_anweisungen="Schwerpunkt Stromkreise (Ohm, Kirchhoff). 
       Eine Aufgabe zu elektromagnetischer Induktion als AFB III."
   )

3. MATERIAL-ROUTER (Python, kein LLM):
   - Lädt Wissenskarte für physik/klausur → "1 Generic, 0 Examples, 3 Good Practices"
   - Lädt Preferences → "5 Aufgaben, Teilaufgaben, 60:40 Rechnung/Theorie"
   - Startet Klausur-Agent (Sonnet) mit Kontext

4. KLAUSUR-AGENT (Sonnet, Turn 1):
   Sieht Wissenskarte: "3 bewährte Aufgaben vorhanden"
   
   → Ruft get_good_practices("physik", "stromkreise") 
     Ergebnis: 2 Aufgaben zu Ohm'sches Gesetz (Rating 4/5, 5/5)
   
   → Ruft search_curriculum("Stromkreise Kirchhoff Induktion Klasse 10")
     Ergebnis: SchiC-Chunks mit Kompetenzerwartungen + Bepunktungshinweise
   
   → Generiert Klausur (ExamStructure)
     5 Aufgaben, 45P, AFB 30/40/30
     Aufgabe 1-2: Ohm (inspiriert von Good Practice)
     Aufgabe 3-4: Kirchhoff (aus Curriculum abgeleitet)
     Aufgabe 5: Induktion AFB III (wie angefragt)

5. ERGEBNIS:
   - material_router: DOCX generieren, in DB speichern
   - Hauptagent: Zusammenfassung + Download-Link an User
   
6. FEEDBACK & LERNEN:
   User: "Super, genau so!"
   → material_learning_agent erkennt: Rating 5/5
   → Speichert Aufgabe 5 (Induktion) als neue Good Practice
   → Speichert Preference: "E-Lehre: Rechnung+Theorie gemischt"
   → Wissenskarte wächst: jetzt 4 Good Practices

7. NÄCHSTES MAL:
   User: "Nochmal eine E-Lehre-Klausur, diesmal für die 10b"
   → Agent sieht: 4 Good Practices, kennt den Stil
   → Bessere Klausur, weniger Rückfragen nötig
```

## Abgrenzung bestehender Systeme

| System | Zweck | Bleibt? |
|---|---|---|
| `user_memories` | Chat-Kontext (Präferenzen, Klassen, Schule) | ✅ Bleibt unverändert |
| `memory_agent.py` | Extrahiert Memories aus Chat | ✅ Bleibt unverändert |
| `material_learning_agent.py` | Erkennt Material-Feedback | ✅ Schreibt jetzt in `agent_knowledge` |
| `curriculum_chunks` | Lehrplan-RAG | ✅ Bleibt, wird vom Subagent per Tool genutzt |
| `generated_materials` | Materialspeicher + DOCX | ✅ Bleibt unverändert |
| `session_logs` | Conversation-Summaries | ✅ Bleibt unverändert |
| `material_preferences` (geplant) | → Wird `agent_knowledge` (type=preference) | ❌ Entfällt |
| `material_templates` (geplant) | → Wird `agent_knowledge` (type=example) | ❌ Entfällt |
| `good_practice_materials` (geplant) | → Wird `agent_knowledge` (type=good_practice) | ❌ Entfällt |

## Modell-Zuordnung

| Agent | Modell | Begründung |
|---|---|---|
| Hauptagent (Chat) | Sonnet | Gesprächsführung, Tool-Routing |
| Klausur-Agent | **Sonnet** (↑ von Haiku) | Komplexer Workflow, Tool-Nutzung, Rückfragen |
| Differenzierung-Agent | **Sonnet** (↑ von Haiku) | Drei Niveaus + Fachspezifik |
| H5P-Agent | Haiku | Einfachere Aufgaben, strukturiert |
| Memory-Agent | Haiku | Extraction, einfach |
| Summary-Agent | Haiku | Zusammenfassung, einfach |
| Material-Learning-Agent | Haiku | Signal-Erkennung, einfach |

## Kosten-Schätzung

| Aktion | Tokens (Input) | Tokens (Output) | Kosten |
|---|---|---|---|
| Chat-Nachricht (Sonnet) | ~2K | ~500 | ~$0.01 |
| Klausur-Generierung (Sonnet) | ~5-8K (mit Tools) | ~2K | ~$0.03-0.04 |
| Klausur mit 1 Rückfrage | ~10-12K | ~3K | ~$0.05-0.06 |
| Memory-Extraktion (Haiku) | ~1K | ~300 | ~$0.001 |
| Material-Learning (Haiku) | ~1K | ~200 | ~$0.001 |
| **Gesamt pro Klausur-Session** | | | **~$0.06-0.08** |

→ ~12-16 Klausuren pro Dollar. Akzeptabel für High-Value-Output.

## Implementierungs-Reihenfolge

1. **DB**: `agent_knowledge` Tabelle + RPC `match_good_practices` erstellen
2. **Seed**: Generische Fach-Profile für Top-8-Fächer (Physik, Bio, Deutsch, Mathe, Geschichte, Geo, Englisch, Chemie)
3. **material_router.py**: Wissenskarte-Loader + Multi-Turn-Loop
4. **klausur_agent.py**: Auf Sonnet upgraden, Tools hinzufügen, KlausurResult Output-Typ
5. **material_learning_agent.py**: Auf `agent_knowledge` umstellen
6. **db.py**: Erweitern um `or`-Filter und `rpc()`-Methode
7. **Test**: E2E mit Steffens Account (Physik Optik)
8. **Diff-Agent + H5P-Agent**: Gleiche Architektur übernehmen

## Multi-Turn Rückfragen — State Machine Design

### Das Problem (von Gemini identifiziert)

Der Hauptagent ist in einem **blockierenden Tool-Call** wenn der Subagent läuft.
Er kann nicht "pausieren", den User fragen und den Tool-Call fortsetzen.
Ein naiver `await`-Loop funktioniert nicht.

### Lösung: Two-Phase Tool Pattern

Der Material-Flow wird in **zwei Tools** aufgeteilt:

```python
# Tool 1: Material-Generierung starten
@agent.tool
async def generate_material(...) -> str:
    """Startet die Generierung. Kann entweder:
    - Fertiges Material zurückgeben (mit Download-Link)
    - ODER eine Rückfrage zurückgeben mit session_id"""
    
    result = await material_router.start_generation(request)
    
    if result.needs_clarification:
        # State persistieren
        session_id = await save_agent_session(
            message_history=result.message_history,
            deps=result.deps,
            request=request,
        )
        return (
            f"RÜCKFRAGE_AN_LEHRER: {result.clarification.frage}\n"
            f"Kontext: {result.clarification.kontext}\n"
            f"Vorschläge: {', '.join(result.clarification.vorschlaege)}\n"
            f"[session:{session_id}]"
        )
    
    # Fertig → DOCX + Summary
    return result.summary

# Tool 2: Generierung fortsetzen (nach User-Antwort)
@agent.tool
async def continue_material_generation(
    ctx: RunContext[AgentDeps],
    session_id: str,
    user_answer: str,
) -> str:
    """Setzt eine pausierte Material-Generierung fort.
    Nutze dieses Tool wenn der Lehrer auf eine Rückfrage 
    des Material-Agents geantwortet hat."""
    
    # State laden
    session = await load_agent_session(session_id)
    
    # Subagent mit voller message_history fortsetzen
    result = await material_router.continue_generation(
        session=session,
        user_answer=user_answer,
    )
    
    if result.needs_clarification:
        # Noch eine Rückfrage → State updaten
        await update_agent_session(session_id, result.message_history)
        return f"RÜCKFRAGE_AN_LEHRER: {result.clarification.frage}..."
    
    # Fertig
    await delete_agent_session(session_id)
    return result.summary
```

### State-Persistierung

```sql
CREATE TABLE agent_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  teacher_id UUID NOT NULL,
  conversation_id UUID NOT NULL,
  agent_type TEXT NOT NULL,           -- 'klausur', 'differenzierung'
  message_history JSONB NOT NULL,     -- Pydantic AI messages (serialisiert)
  request JSONB NOT NULL,             -- Original-Request
  deps JSONB NOT NULL,                -- Serialisierte Dependencies
  status TEXT DEFAULT 'waiting',      -- 'waiting', 'completed', 'expired'
  created_at TIMESTAMPTZ DEFAULT now(),
  expires_at TIMESTAMPTZ DEFAULT now() + INTERVAL '1 hour'
);
```

### Flow mit Rückfrage

```
1. User: "Klausur E-Lehre für die 10a"
2. Sonnet (Hauptagent): Schärfungsfragen → User bestätigt
3. Sonnet ruft generate_material(fach="physik", ...)
4. material_router startet Klausur-Agent (Sonnet)
5. Klausur-Agent:
   → Lädt Wissenskarte (im System-Prompt)
   → Ruft get_good_practices("physik", "e-lehre") 
   → Merkt: AFB-Verteilung unklar
   → Return: ClarificationRequest("30/40/30 oder eher 20/50/30?")
6. material_router: State speichern → session_id zurück
7. Hauptagent bekommt: "RÜCKFRAGE_AN_LEHRER: 30/40/30 oder 20/50/30?"
8. Hauptagent stellt die Frage an User (natürlich formuliert)
9. User: "30/40/30 bitte"
10. Hauptagent erkennt: offene Session → ruft continue_material_generation(session_id, "30/40/30")
11. material_router: State laden, Agent fortsetzen mit message_history
12. Klausur-Agent hat ALLES noch: Good Practices, Curriculum, bisherige Überlegungen
13. → Generiert Klausur
14. material_router: DOCX → DB → Summary zurück
15. Hauptagent: Download-Link an User
```

### Warum das funktioniert

- **Kein blockierender Loop** — jeder Tool-Call ist atomar
- **State bleibt erhalten** — `message_history` enthält alle bisherigen Tool-Calls und Überlegungen
- **Pydantic AI native** — `agent.run(prompt, message_history=...)` ist eingebautes Feature
- **Hauptagent bleibt frei** — kann zwischen Tool-Calls normal mit User chatten
- **Timeout/Cleanup** — Sessions verfallen nach 1h automatisch
- **Max 2-3 Rückfragen** — Counter in Session, danach generieren mit dem was da ist

### Serialisierung von message_history

Pydantic AI Messages sind Pydantic-Modelle → `model_dump()` / `model_validate()`:

```python
from pydantic_ai.messages import ModelMessage

async def save_agent_session(message_history: list[ModelMessage], ...) -> str:
    session_id = str(uuid.uuid4())
    await db.insert("agent_sessions", {
        "id": session_id,
        "message_history": [m.model_dump() for m in message_history],
        ...
    })
    return session_id

async def load_agent_session(session_id: str) -> AgentSession:
    data = await db.select("agent_sessions", filters={"id": session_id}, single=True)
    messages = [ModelMessage.model_validate(m) for m in data["message_history"]]
    return AgentSession(messages=messages, ...)
```

## Kontext-Tools — Dynamisches Nachladen

### Prinzip: Lazy Loading mit Granularität

Der Subagent bekommt NICHT alles vorab. Er hat Tools mit **einstellbarer Tiefe**:

```python
@agent.tool
async def get_context(
    ctx: RunContext[KlausurDeps],
    scope: str,
    depth: str = "summary",
) -> str:
    """Lade zusätzlichen Kontext nach Bedarf.
    
    scope: Was laden?
      - "conversation" → Chat-Verlauf
      - "curriculum" → Lehrplan-Chunks
      - "examples" → Lehrer-Uploads
      - "good_practices" → Bewährte Aufgaben
      - "memories" → Lehrer-Erinnerungen
    
    depth: Wie viel?
      - "summary" → Kurze Übersicht (~100 Tokens)
      - "relevant" → Nur zum Thema passend (~300-500 Tokens)
      - "full" → Alles verfügbare (~1000+ Tokens)
    """
    
    if scope == "conversation":
        if depth == "summary":
            # Nur die Session-Summary
            return await _get_conversation_summary(ctx.deps.conversation_id)
        elif depth == "relevant":
            # Letzte 5 Nachrichten
            return await _get_recent_messages(ctx.deps.conversation_id, limit=5)
        else:
            # Kompletter Verlauf
            return await _get_recent_messages(ctx.deps.conversation_id, limit=20)
    
    elif scope == "curriculum":
        if depth == "summary":
            # Wissenskarte-Auszug
            return await _get_curriculum_overview(ctx.deps.teacher_id)
        else:
            # RAG-Suche nach aktuellem Thema
            query = f"{ctx.deps.fach} {ctx.deps.thema}"
            return await curriculum_search(ctx.deps.teacher_id, query)
    
    elif scope == "good_practices":
        limit = {"summary": 1, "relevant": 3, "full": 5}[depth]
        return await _get_good_practices_rag(
            ctx.deps.teacher_id, ctx.deps.fach, ctx.deps.thema, limit
        )
    
    elif scope == "examples":
        return await _get_teacher_examples(
            ctx.deps.teacher_id, ctx.deps.fach, ctx.deps.thema
        )
    
    elif scope == "memories":
        return await _get_teacher_memories(ctx.deps.teacher_id)
```

### Warum ein Tool statt fünf?

- **Agent entscheidet**: "Brauche ich den ganzen Chat oder reicht die Summary?"
- **Token-Kontrolle**: `depth="summary"` kostet ~100 Tokens, `"full"` ~1000+
- **Erweiterbar**: Neuer Scope = neue if-Clause, kein neues Tool-Registration
- **Sonnet ist schlau genug**: Versteht scope + depth und nutzt es sinnvoll

### Typischer Tool-Nutzung eines smarten Subagents

```
Klausur-Agent denkt:
  "Auftrag: Physik E-Lehre, Klasse 10, 45 Min.
   Wissenskarte zeigt: 2 Good Practices, 1 Beispiel, Curriculum vorhanden.
   
   1. Lass mich die Good Practices laden (relevant)
   2. Lass mich ins Curriculum schauen (relevant)
   3. Die Conversation-Summary reicht mir, den Chat brauche ich nicht komplett"

→ get_context("good_practices", "relevant")  # ~300 Tokens
→ get_context("curriculum", "relevant")       # ~500 Tokens
→ Generiert Klausur mit dem Wissen
```

Kein unnötiges Nachladen. Agent entscheidet selbst. Token-effizient.

## Design-Entscheidung: Spezialisten vs. Monolith

### Geminis Einwand
"Wäre es nicht einfacher, ALLE Rückfragen im Hauptagent zu machen und den Subagent nur als One-Shot zu nutzen?"

### Unsere Antwort: Spezialisten. Aus folgenden Gründen:

**1. Prompt-Fokus schlägt Generalismus**
Ein Klausur-Agent mit 2K Tokens System-Prompt der NUR Klausuren kann, schlägt einen Hauptagent mit 8K Tokens der alles können muss. Weniger Kontext = weniger Konfusion = bessere Qualität.

**2. Tool-Isolation**
Der Klausur-Agent braucht `get_context`, `search_curriculum`. Der Hauptagent braucht `remember`, `web_search`, `generate_material`. Getrennte Tool-Sets = weniger falsche Tool-Calls.

**3. Modell-Austauschbarkeit**
In 6 Monaten gibt es vielleicht spezialisierte Bildungs-Modelle. Mit Spezialisten tauscht man ein Modell aus. Beim Monolith geht das nicht.

**4. Wissenskarte skaliert nur mit Spezialisten**
Wenn der Hauptagent ALLES macht, muss er ALLES wissen — Klausur-Good-Practices, Differenzierungs-Muster, H5P-Templates. Das explodiert. Spezialisten sehen nur ihr Fachgebiet.

### Klare Verantwortungsteilung

| Verantwortung | Wer | Warum |
|---|---|---|
| Gespräch führen, Ton, Empathie | Hauptagent | Kennt den Lehrer, hat Chat-Historie |
| Vorklärung: Fach, Klasse, Thema, Wünsche | Hauptagent | Ist Gesprächspartner, stellt natürliche Fragen |
| Schärfungsfragen (konversational) | Hauptagent | "Schwerpunkt Stromkreise oder Induktion?" |
| Fachliche Rückfragen beim Generieren | **Subagent** | "SchiC sagt 60P, du willst 45 Min — weniger Aufgaben?" |
| Curriculum-RAG, Good Practices laden | **Subagent** | Braucht die Details, nicht der Hauptagent |
| Material generieren | **Subagent** | Fokussierter Prompt, spezialisierte Tools |
| Ergebnis präsentieren, Download-Link | Hauptagent | Gespräch abschließen |

→ Hauptagent = **Konversation + Vorklärung**
→ Subagent = **Fachliche Tiefe + Generierung**

## Skalierbarkeit — Über Material-Agents hinaus

### Agent-Roadmap

| Phase | Agent | Wissenskarte-Scope | Modell |
|---|---|---|---|
| **Jetzt** | Klausur | Fach × Lehrer | Sonnet |
| **Jetzt** | Differenzierung | Fach × Lehrer | Sonnet |
| **Jetzt** | H5P | Fach × Lehrer | Haiku |
| **Bald** | Unterrichtsplanung | Fach × Lehrer | Sonnet |
| **Bald** | Feedback (Schülertexte bewerten) | Fach × Lehrer | Sonnet |
| **Bald** | Elternbrief | Klasse × Lehrer | Haiku |
| **Mittel** | Diagnose (Lernstand-Analyse) | Fach × **Klasse** | Sonnet |
| **Mittel** | Förderplan | Fach × **Schüler** | Sonnet |
| **Mittel** | Fortbildungs-Empfehlungen | Lehrer-übergreifend | Haiku |
| **Später** | Prüfungs-Analyse | Fach × **Klasse** | Sonnet |
| **Später** | Kollegiums-Agent (Material teilen) | **Schule** | Sonnet |
| **Später** | Schulentwicklung (Fachschaft beraten) | **Schule** | Sonnet |

### Das Schema muss über `teacher_id` hinauswachsen

Material-Agents arbeiten auf der Achse **Fach × Lehrer**. Aber:
- **Diagnose-Agent**: Braucht Wissen über *Klassen* ("10a hat Probleme mit Bruchrechnung")
- **Förderplan-Agent**: Braucht Wissen über *einzelne Schüler*
- **Schulentwicklung**: Braucht schulweites Wissen, mehrere Lehrer greifen zu
- **Kollegiums-Agent**: Globale Good Practices, anonymisiert geteilt

### Lösung: Scope-Erweiterung

Statt `teacher_id` als einziger Zuordnung → `scope_type` + `scope_id`:

```sql
CREATE TABLE agent_knowledge (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Agent-Zuordnung
  agent_type TEXT NOT NULL,

  -- Scope: WER sieht dieses Wissen?
  scope_type TEXT NOT NULL DEFAULT 'teacher',  -- 'teacher', 'class', 'school', 'global'
  scope_id UUID,                               -- teacher_id, class_id, school_id, oder NULL
  owner_id UUID NOT NULL,                      -- Wer hat es erstellt (immer teacher_id)
  
  -- Inhalt
  fach TEXT NOT NULL,
  thema TEXT,
  knowledge_type TEXT NOT NULL,    -- 'generic', 'example', 'good_practice', 'preference'
  
  -- Payload
  content JSONB NOT NULL,
  description TEXT,
  
  -- Qualität
  quality_score FLOAT DEFAULT 0.5,
  times_used INT DEFAULT 0,
  source TEXT NOT NULL,            -- 'system', 'upload', 'generated', 'conversation'
  
  -- RAG
  embedding vector(1536),
  
  -- Meta
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### Sichtbarkeits-Logik

```python
async def get_visible_knowledge(
    agent_type: str,
    fach: str,
    teacher_id: str,
    class_id: str | None = None,
    school_id: str | None = None,
) -> list[dict]:
    """Lade alles Wissen das dieser Agent sehen darf."""
    # Sichtbar: eigenes + klassen + schul + global
    visible_scopes = [
        ("teacher", teacher_id),
        ("global", None),
    ]
    if class_id:
        visible_scopes.append(("class", class_id))
    if school_id:
        visible_scopes.append(("school", school_id))
    
    # Supabase RPC oder OR-Query
    return await db.rpc("get_visible_knowledge", {
        "p_agent_type": agent_type,
        "p_fach": fach,
        "p_scopes": visible_scopes,
    })
```

### Beispiel: Diagnose-Agent

```
Wissenskarte für Diagnose-Agent (Physik, Klasse 10a):

scope=teacher:  Steffens Bewertungspräferenzen
scope=class:    "10a: 40% haben Probleme mit Einheiten-Umrechnung"
scope=class:    "10a: Letzte Klausur Ø 3,2 — Optik war schwach"  
scope=school:   "Physik-Fachschaft: Einheiten ab Klasse 7 systematisch üben"
scope=global:   "Typische Physik-Fehler Klasse 10: Vorzeichenfehler, Einheiten vergessen"
```

Der Agent sieht alle vier Ebenen und kann sie kombinieren.

### Was gleich bleibt, was sich ändert

| Komponente | Material-Agents | Schüler-/Klassen-Agents | Änderung |
|---|---|---|---|
| `agent_knowledge` Tabelle | ✅ | ✅ | scope_type/scope_id statt teacher_id |
| Wissenskarte (SQL-Aggregation) | ✅ | ✅ | Filter erweitert um scope |
| `get_context` Tool | ✅ | ✅ | Neuer scope: "class_data", "student_data" |
| `material_router` | ✅ | ✅ (wird "agent_router") | Agent-Typ-Routing bleibt gleich |
| Multi-Turn Rückfragen | ✅ | ✅ | Identisch |
| `material_learning_agent` | ✅ | ✅ (wird "learning_agent") | Gleiches Pattern |

→ **Die Architektur ist ein generisches Agent-Framework.** Material-Agents sind nur die erste Instanz. Neue Agents = System-Prompt + Output-Modell + Seed-Daten. Infrastruktur steht.

## Implementierungs-Phasen

### Phase 1: Wissenskarte + Sonnet-Subagent (One-Shot mit Tools)
- `agent_knowledge` Tabelle erstellen
- Seed: Generische Fach-Profile (Top 8 Fächer)
- Klausur-Agent auf Sonnet upgraden
- `get_context` Tool mit scope+depth
- `material_router.py` umbauen: Wissenskarte vorladen
- `material_learning_agent.py` auf `agent_knowledge` umstellen
- `db.py` erweitern: `rpc()` + `or`-Filter
- **Kein Multi-Turn** — Subagent generiert mit dem was er hat
- E2E-Test mit Steffens Account

### Phase 2: Multi-Turn Rückfragen
- `agent_sessions` Tabelle für State-Persistierung
- Two-Phase Tool Pattern: `generate_material` → `continue_material_generation`
- Pydantic AI `message_history` Serialisierung + Schema-Versionierung
- System-Prompt Hauptagent: Regel für `continue`-Aufruf
- Robuste De-Serialisierung (ValidationError → expired, nicht crash)
- Race-Condition-Handling (User schickt Nachrichten zwischen generate und continue)
- **Erst wenn Phase 1 nachweislich Qualitätslücken zeigt**

### Phase 3: Erweiterte Features
- Upload-Parsing (PDF/DOCX → Struktur → `agent_knowledge` type=example)
- Conversation-Attachments (Bilder/PDFs im Chat → Subagent-Zugriff)
- Good-Practice-RAG mit pgvector (wenn Aufgabenbank >50 Einträge)
- Globale Good Practices (anonymisiert zwischen Lehrern, Datenschutz klären)
- `pydantic-graph` evaluieren als Alternative zur manuellen State Machine
- Diff-Agent + H5P-Agent: Gleiche Architektur übernehmen

## Offene Fragen

1. **Upload-Parsing**: Wie extrahieren wir Struktur aus hochgeladenen PDFs? (Phase 3)
2. **Quality-Score-Algorithmus**: Lehrer-Rating (1-5) → quality_score (0-1)? Oder auch Wiederverwendung?
3. **Globale Good Practices teilen**: Anonymisiert zwischen Lehrern? Datenschutz-Implikationen?
4. **Embedding-Generierung**: Bei jedem Insert automatisch? Oder Batch-Job?
5. **Render Cold-Start + Sonnet-Subagent**: Timeout-Budget? Sonnet braucht ~10-20s für Klausur + Tool-Calls. Render Free Tier hat 30s Timeout?
