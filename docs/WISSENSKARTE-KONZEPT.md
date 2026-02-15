# Wissenskarte-Konzept — Selbstlernendes Agent-Gedächtnis

## Vision

Jeder Agent (Klausur, Differenzierung, H5P) pflegt eine eigene **Wissenskarte** — einen strukturierten Index über sein Wissen. Die Wissenskarte zeigt dem Agent, was er zu jedem Fach/Thema weiß, woher es kommt und wo Lücken sind.

Der Agent startet mit **generischem Grundwissen** (von uns), lernt aus **Lehrer-Interaktionen**, speichert **gute Beispiele** und wird mit jeder Nutzung besser.

## Architektur

### Drei Wissensquellen (eine Tabelle)

```
agent_knowledge
├── generic      (source: system)       ← Wir seeden: "So sieht eine gute Physik-Klausur aus"
├── example      (source: upload)       ← Lehrer lädt Beispiel-Klausur hoch
├── good_practice (source: generated)   ← Agent-Output den der Lehrer gut fand
└── preference   (source: conversation) ← "Steffen will immer 60/40 Rechnung/Theorie"
```

### Wissenskarte = Aggregierter Index

Die Wissenskarte ist KEIN eigener LLM-Call, sondern ein **DB-Query** der dem Agent am Anfang mitgegeben wird:

```sql
SELECT fach, thema, knowledge_type, COUNT(*), MAX(quality_score)
FROM agent_knowledge
WHERE teacher_id = $1 OR teacher_id IS NULL  -- persönlich + global
GROUP BY fach, thema, knowledge_type
```

Ergebnis für den System-Prompt:
```
## Deine Wissensbasis
Physik / Optik:
  ✅ Generisches Profil (Berechnungen, Einheiten, Diagramme)
  ✅ 1 Beispiel-Klausur (Upload vom 12.02.)
  ✅ 2 Good-Practice-Aufgaben (Bewertung 4/5, 5/5)
  ✅ Präferenzen: 60% Rechnung, 40% Theorie, immer Diagramm
Bio / Ökologie:
  ✅ Generisches Profil (Materialauswertung, Schemata)
  ❌ Kein Beispiel
  ❌ Keine Good-Practice-Aufgaben
  ❌ Keine Präferenzen
```

## Datenbank-Schema

### Neue Tabelle: `agent_knowledge`

```sql
CREATE TABLE agent_knowledge (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Zuordnung
  agent_type TEXT NOT NULL,           -- 'klausur', 'differenzierung', 'h5p'
  teacher_id UUID REFERENCES user_profiles(id),  -- NULL = global/generisch
  
  -- Inhalt
  fach TEXT NOT NULL,                 -- 'physik', 'biologie', 'deutsch', ...
  thema TEXT,                         -- Optional: 'optik', 'ökologie', NULL für fach-weit
  knowledge_type TEXT NOT NULL,       -- 'generic', 'example', 'good_practice', 'preference'
  
  -- Payload
  content JSONB NOT NULL,             -- Strukturierter Inhalt (siehe unten)
  description TEXT,                   -- Menschenlesbare Kurzbeschreibung
  
  -- Qualität
  quality_score FLOAT DEFAULT 0.5,    -- 0.0-1.0
  times_used INT DEFAULT 0,           -- Wie oft referenziert
  source TEXT NOT NULL,               -- 'system', 'upload', 'generated', 'conversation'
  
  -- Meta
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indices
CREATE INDEX idx_ak_teacher ON agent_knowledge(teacher_id);
CREATE INDEX idx_ak_fach ON agent_knowledge(fach, thema);
CREATE INDEX idx_ak_type ON agent_knowledge(agent_type, knowledge_type);
CREATE INDEX idx_ak_quality ON agent_knowledge(quality_score DESC);
```

### Content-Strukturen (JSONB)

**Generic (Fach-Profil):**
```json
{
  "aufgabenformate": ["Berechnung mit Einheiten", "Diagramm auswerten", "Experiment bewerten"],
  "afb_operatoren": {
    "I": ["Nennen", "Angeben", "Berechnen (einfach)"],
    "II": ["Erklären", "Berechnen (komplex)", "Vergleichen", "Analysieren"],
    "III": ["Beurteilen", "Entwickeln (Versuchsaufbau)", "Diskutieren"]
  },
  "erwartungshorizont_stil": "calculation",
  "typische_verteilung": {"rechnung": 60, "theorie": 40},
  "besonderheiten": ["Einheiten immer angeben", "Formeln bereitstellen oder ableiten lassen"],
  "beispiel_operatoren_mapping": {
    "Berechne den Brechungswinkel": "AFB II",
    "Beurteile die Eignung von Glasfasern": "AFB III"
  }
}
```

**Example (Upload):**
```json
{
  "original_filename": "Physik_Klasse10_Optik_KA2.pdf",
  "extracted_structure": { ... },  -- Parsed ExamStructure
  "aufgaben_count": 5,
  "afb_verteilung": {"I": 30, "II": 40, "III": 30},
  "gesamtpunkte": 45,
  "lehrer_kommentar": "Das war eine gute Klausur, hat gut funktioniert"
}
```

**Good Practice (bewertete generierte Aufgabe):**
```json
{
  "aufgabe": "Berechnen Sie den Brechungswinkel...",
  "afb_level": "II",
  "punkte": 8,
  "erwartung": ["Snellius anwenden...", "Winkel = 23.4°..."],
  "material_id": "uuid-of-original-klausur",
  "lehrer_rating": 5,
  "iteration_count": 0
}
```

**Preference:**
```json
{
  "aufgaben_anzahl": 5,
  "afb_verteilung": {"I": 30, "II": 40, "III": 30},
  "bonusaufgabe": true,
  "teilaufgaben": true,
  "rechnung_theorie_ratio": "60:40",
  "notenschluessel": "standard"
}
```

## Bestehender Code — Was sich ändert

### Ersetzt wird:

| Aktuell | Neu | Warum |
|---------|-----|-------|
| `material_preferences` (Tabelle, existiert nicht) | `agent_knowledge` (type=preference) | Vereinheitlicht |
| `material_templates` (Tabelle, existiert nicht) | `agent_knowledge` (type=example/good_practice) | Vereinheitlicht |
| `good_practice_materials` (Tabelle, existiert nicht) | `agent_knowledge` (type=good_practice) | Vereinheitlicht |

→ Drei geplante Tabellen werden EINE. Der Code in `material_router.py` referenziert sie schon, muss nur auf `agent_knowledge` umgestellt werden.

### Bleibt:

| Komponente | Änderung |
|-----------|----------|
| `user_memories` | Bleibt für allgemeine Memories (Scope: self/class/school) |
| `memory_agent.py` | Bleibt für Chat-Kontext-Extraktion |
| `material_learning_agent.py` | Schreibt jetzt in `agent_knowledge` statt 3 separate Tabellen |
| `curriculum_chunks` | Bleibt für Lehrplan-RAG |
| `generated_materials` | Bleibt als Materialspeicher inkl. DOCX |
| `session_logs` | Bleibt für Conversation-Summaries |

### Anpassungen:

1. **`material_router.py`** `_load_material_context()`:
   - Statt 3 Tabellen-Queries → 1 Query auf `agent_knowledge` mit Filtern
   - Wissenskarte als Prompt-Abschnitt generieren

2. **`material_learning_agent.py`**:
   - `_update_preferences()` → Schreibt in `agent_knowledge` (type=preference)
   - `_save_as_template()` → Schreibt in `agent_knowledge` (type=good_practice)

3. **`klausur_agent.py`** System-Prompt:
   - Generischer AFB-Teil bleibt (ist korrekt und stabil)
   - NEU: Fach-spezifischer Abschnitt aus `agent_knowledge` (type=generic)
   - NEU: Beispiel-Aufgaben aus `agent_knowledge` (type=good_practice)

4. **`system_prompt.py`** `build_block3_context()`:
   - NEU: Wissenskarte-Abschnitt laden und dem Main-Agent mitgeben
   - Main-Agent sieht: "Für Physik/Optik habe ich 2 gute Aufgaben und dein Beispiel"

5. **`differenzierung_agent.py`** + **`h5p_agent.py`**:
   - Gleiche Struktur: `agent_knowledge` nach Fach+Thema+agent_type abfragen
   - H5P-Agent: type=good_practice für bewährte Quiz-Fragen

## Update-Flow

### Nach Material-Generierung (existiert schon in material_learning_agent):
```
1. Lehrer sagt "Super, genau so!" (rating >= 4)
2. material_learning_agent erkennt Signal
3. → Einzelne Aufgaben als good_practice in agent_knowledge speichern
4. → Präferenzen als preference speichern
5. Wissenskarte wächst automatisch
```

### Nach Upload (NEU):
```
1. Lehrer lädt Beispiel-Klausur hoch (PDF/DOCX)
2. OCR/Parser extrahiert Struktur
3. → Als example in agent_knowledge speichern
4. → Fach + Thema automatisch taggen
```

### Seed (einmalig, von uns):
```
1. Wir erstellen generic-Einträge pro Fach
2. teacher_id = NULL (global für alle)
3. Physik, Bio, Deutsch, Mathe, Geschichte, ... (Top 8 Fächer)
4. agent_type = 'klausur' + 'differenzierung' + 'h5p'
```

## Wissenskarte im Prompt — Beispiel

```
## Deine Wissensbasis für diese Anfrage

### Fach: Physik (Klasse 10, Optik)

**Fach-Profil:** Physik-Klausuren basieren auf Berechnungen (60%), 
Theorie (40%). Einheiten immer angeben. Formeln bereitstellen ODER 
herleiten lassen. Diagramme als Material einsetzen.

**Steffens Präferenzen:** 5 Aufgaben, immer Teilaufgaben (a/b/c), 
Bonusaufgabe optional, Standardnotenschlüssel.

**Bewährte Aufgaben (nutze als Inspiration):**
1. "Berechnen Sie den Brechungswinkel..." (AFB II, 8P, Rating 5/5)
2. "Erklären Sie das Zustandekommen der Totalreflexion..." (AFB II, 6P, Rating 4/5)

**Beispiel-Klausur von Steffen:**
Optik KA2 — 5 Aufgaben, 45P, AFB 30/40/30, mit Diagramm als Material.
→ Orientiere dich an diesem Stil und Format!
```

## Für alle Agents? — Analyse

| Agent | Profitiert? | Wie? |
|-------|-------------|------|
| **Klausur** | ✅ Maximal | Fach-Profile, Aufgabenbank, Präferenzen, Beispiele |
| **Differenzierung** | ✅ Stark | Fach-Profile, Niveaustufen-Muster, Scaffolding-Beispiele |
| **H5P** | ✅ Mittel | Bewährte Fragen wiederverwenden, Fach-angepasste Fragetypen |
| **Main-Agent** | ✅ Indirekt | Sieht Wissenskarte → kann sagen "Für Physik hab ich schon 3 gute Aufgaben" |
| **Memory-Agent** | ❌ Nicht nötig | Arbeitet auf Chat-Kontext, nicht auf Fachwissen |

→ `agent_knowledge` passt für ALLE Material-Agents. `agent_type`-Feld erlaubt agent-spezifische Einträge.

## Migration

1. Tabelle `agent_knowledge` erstellen (SQL oben)
2. Seed-Script für generische Fach-Profile (8 Fächer × 3 Agents = 24 Einträge)
3. `material_router.py` auf `agent_knowledge` umstellen (statt 3 nicht-existierende Tabellen)
4. `material_learning_agent.py` auf `agent_knowledge` umstellen
5. Klausur-Agent + Diff-Agent: Wissenskarte in System-Prompt einbauen
6. H5P-Agent: Wissenskarte optional einbauen

Kein Breaking Change — alles additive Erweiterung.

## Offene Fragen

1. **Upload-Parser**: Wie extrahieren wir Struktur aus hochgeladenen PDFs? (Separates Feature)
2. **Quality-Score-Algorithmus**: Einfach Lehrer-Rating? Oder auch "wurde wiederverwendet" einbeziehen?
3. **Globale Good Practices**: Teilen wir anonymisierte gute Aufgaben zwischen Lehrern? (Datenschutz!)
4. **Wissenskarte-Größe**: Bei vielen Fächern/Themen → Token-Budget. Nur relevante Fächer laden?
5. **SchiC-Integration**: `curriculum_chunks` mit `agent_knowledge` verknüpfen? Oder reicht RAG-Suche?
