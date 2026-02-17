# JTBD-Benchmark — Team-Überblick

> Diskussionsvorlage für Steffen, Christopher, Michelle
> Ziel: Gemeinsames Verständnis, was eduhu können soll — messbar und automatisiert testbar.

---

## Die 15 Qualitätsdimensionen

Jeder Job (Klausur, Quiz, Escape Room, Podcast, ...) lässt sich an denselben 15 Dimensionen messen.
Die Dimensionen sind unser **gemeinsames Bewertungsraster**.

| # | Dimension | Kernfrage |
|---|-----------|-----------|
| 1 | **Intent-Erkennung** | Versteht das System, was ich will — egal wie ich es formuliere? |
| 2 | **Proaktivität** | Schlägt es von sich aus sinnvolle nächste Schritte vor? |
| 3 | **Smarte Rückfragen** | Fragt es nur was fehlt — nicht was es schon weiß? |
| 4 | **Technische Zuverlässigkeit** | Funktioniert die Pipeline (YouTube, DOCX, H5P, Audio)? |
| 5 | **Sprachkompetenz** | Erkennt es die richtige Sprache / Fremdsprachenkontext? |
| 6 | **Iterativer Workflow** | Entwurf → Feedback → Überarbeitung → Export? |
| 7 | **Zielgerichtete Überarbeitung** | Kann ich einzelne Teile ändern, ohne alles neu zu erstellen? |
| 8 | **Export-Flexibilität** | Bekomme ich das Material im richtigen Format? |
| 9 | **Material-Erweiterung** | Kann ich aus derselben Quelle weiteres Material machen? |
| 10 | **Kontextbewahrung** | Bleibt der Kontext über das ganze Gespräch erhalten? |
| 11 | **Präferenz-Lernen** | Merkt sich das System meine Vorlieben fürs nächste Mal? |
| 12 | **Pädagogische Qualität** | Sind die Inhalte didaktisch sinnvoll und altersgerecht? |
| 13 | **Fehlertoleranz** | Was passiert wenn etwas schiefgeht? |
| 14 | **Quellenreferenz** | Kann ich nachvollziehen, woher die Inhalte kommen? |
| 15 | **Teilbarkeit** | Wie kommt das Material zum Schüler? |

---

## Architektur: Was die Agents heute können

Bevor wir die Jobs durchgehen — das ist die Realität im Code:

### Agent-Inventar

| Agent | Modell | Aufgabe | Lernt? |
|-------|--------|---------|--------|
| **Main Agent** | Sonnet | Chat + 15 Tools dispatchen | ✅ Memory schreiben |
| **Klausur Agent** | Sonnet | Klausur mit AFB I-III → DOCX | ❌ |
| **Escape-Room Agent** | Sonnet | Narrative + Rätsel → DOCX | ❌ |
| **Podcast Agent** | Sonnet | Multi-Voice-Skript → DOCX (+Audio) | ❌ |
| **+ 9 weitere Material-Agents** | Sonnet/Haiku | Je ein Materialtyp | ❌ |
| **Memory Agent** | Haiku (async) | Präferenzen aus Chat extrahieren | ✅ → `user_memories` |
| **Summary Agent** | Haiku (async) | Chat komprimieren (>10 Msgs) | ✅ → `session_logs` |
| **Material-Learning Agent** | Haiku (async) | Feedback erkennen → Qualität speichern | ✅ → `agent_knowledge` |

### 3-Zonen-Kontext (was der Agent "weiß")

| Zone | Inhalt | Wann geladen |
|------|--------|-------------|
| **Zone 1 — immer da** | Profil, Memories, Todos, Session-Summaries | Jeder Request (~2K Tokens) |
| **Zone 2 — bei Bedarf** | Lehrplan-Chunks, Good Practices | Per Tool-Call |
| **Zone 3 — on demand** | Web-Recherche, Wikipedia, tiefe Analyse | Nur wenn explizit |

### 3-Schichten-Wissen (Wissenskarte)

| Schicht | Was | Quelle | Status |
|---------|-----|--------|--------|
| **Generisch** | Fach-Regeln ("Physik: 60% Rechnung, Einheiten angeben") | Von uns gepflegt | ⚠️ Geplant, nicht implementiert |
| **Bewährt** | Gute Aufgaben aus der Vergangenheit (Rating ≥ 4) | Feedback-Loop | ⚠️ Geplant, nicht implementiert |
| **Persönlich** | Lehrer-Präferenzen ("immer 5 Aufgaben, 45 Punkte") | Memory-Extraktion | ✅ Funktioniert |

**Zentrale Erkenntnis:** Die persönliche Schicht funktioniert. Die generische und bewährte Schicht sind designed aber noch nicht im Code. Das bedeutet: Sub-Agents (Klausur, Escape Room, Podcast) arbeiten aktuell **ohne Fach-Wissen und ohne Lern-Loop** — sie bekommen nur den Lehrer-Kontext und den Chat-Verlauf.

---

## Beispiel 1: Escape Room

> "Erstelle einen Escape Room zum Thema Französische Revolution für Geschichte Klasse 9"

### Flow durch die Architektur

```
Lehrkraft: "Mach einen Escape Room für Geschichte 9, Französische Revolution"
    │
    ▼
Main Agent (Sonnet) → erkennt Intent → ruft generate_material(type="escape_room")
    │
    ▼
Material-Router → lädt Lehrer-Kontext (Zone 1) → startet Escape-Room Agent
    │
    ▼
Escape-Room Agent (Sonnet) → generiert: Narrative + 5 Rätsel + Lösungskarten
    │
    ▼
DOCX-Generator → Escape-Room als Word-Dokument
    │
    ▼
Download-Link an Lehrkraft
    │
    ▼ (async)
Memory Agent: "Steffen hat Escape Rooms für Geschichte erstellt"
Material-Learning Agent: wartet auf Feedback
```

### Wie die 15 Dimensionen hier greifen

| Dim | Konkretes Szenario | Heute möglich? |
|-----|--------------------|----------------|
| **1. Intent** | "Mach was Spielerisches zur Franz. Revolution" → erkennt Escape Room | ✅ Main Agent routet korrekt |
| **2. Proaktivität** | Nach Escape Room: "Soll ich auch ein Quiz zur Sicherung erstellen?" | ⚠️ Muss Main Agent machen (kein Sub-Agent Vorschlag) |
| **3. Rückfragen** | "Wie viele Rätsel? Welche Schwierigkeit? Zeitrahmen?" — aber NUR wenn nicht aus Kontext ableitbar | ⚠️ Sub-Agent kann **keine Rückfragen** stellen (One-Shot) |
| **4. Technik** | DOCX-Export mit Rätselkarten-Layout | ✅ Funktioniert |
| **5. Sprache** | Escape Room auf Französisch (Fremdsprachenunterricht) | ⚠️ Muss explizit gesagt werden |
| **6. Iteration** | Erst Entwurf zeigen, dann exportieren | ❌ **Geht direkt zum DOCX** — kein Entwurf im Chat |
| **7. Überarbeitung** | "Ändere Rätsel 3, das ist zu leicht" | ❌ **patch_material_task nur für Klausuren**, nicht für Escape Rooms |
| **8. Export** | Als DOCX. H5P wäre cool (interaktiver Escape Room) aber nicht möglich | ⚠️ Nur DOCX |
| **9. Erweiterung** | "Erstelle auch ein Arbeitsblatt zum selben Thema" | ✅ Main Agent hat Kontext |
| **10. Kontext** | Multi-Turn: "Mach die Rätsel schwieriger" nach Erstellung | ⚠️ Nur über Neugenierung, kein Patch |
| **11. Präferenzen** | "Ich will immer 5 Rätsel" → nächstes Mal automatisch | ✅ Memory Agent extrahiert das |
| **12. Pädagogik** | Rätsel auf verschiedenen Schwierigkeitsstufen, Lernziel-Bezug | ⚠️ Keine Wissenskarte → Agent hat keine Fach-Didaktik |
| **13. Fehler** | Unklares Thema → was passiert? | ⚠️ Sub-Agent rät statt zu fragen (One-Shot) |
| **14. Quellen** | Lehrplanbezug in den Rätseln | ⚠️ Kein curriculum_search Tool im Escape-Room Agent |
| **15. Teilbarkeit** | Drucken und ausschneiden | ✅ DOCX ist druckfertig |

### Gaps beim Escape Room

| Gap | Impact | Aufwand |
|-----|--------|---------|
| Kein Entwurf vor Export (Dim 6) | Lehrkraft sieht Material erst nach DOCX-Generierung | Mittel |
| Kein Einzel-Rätsel-Patch (Dim 7) | Alles oder nichts — kein gezieltes Überarbeiten | Hoch |
| Keine Sub-Agent-Rückfragen (Dim 3) | Agent rät bei Unklarheit statt zu fragen | Hoch (Multi-Turn Subagent nötig) |
| Kein Curriculum-Tool (Dim 14) | Escape Room ist nicht lehrplanbezogen | Niedrig (Tool hinzufügen) |
| Keine Wissenskarte (Dim 12) | Kein Fach-Wissen, keine bewährten Rätsel-Muster | Hoch (Wissenskarte bauen) |

---

## Beispiel 2: Podcast

> "Erstelle einen 5-Minuten-Podcast zum Klimawandel für Bio Klasse 9"

### Flow durch die Architektur

```
Lehrkraft: "Mach einen Podcast zum Klimawandel, Bio 9, 5 Minuten"
    │
    ▼
Main Agent (Sonnet) → erkennt Intent → ruft generate_material(type="podcast")
    │
    ▼
Material-Router → lädt Lehrer-Kontext → startet Podcast Agent
    │
    ▼
Podcast Agent (Sonnet) → generiert: Multi-Voice-Skript mit Regieanweisungen
    │
    ▼
DOCX-Generator → Skript als Word
    │
    ▼ (optional, wenn ElevenLabs konfiguriert)
TTS-Pipeline → ElevenLabs Multilingual v2 → Audio-Dateien
    │
    ▼
Audio-Sharing → Zugangscode (z.B. "stern47") + QR-Code
    │
    ▼
Download-Link(s) an Lehrkraft
```

### Wie die 15 Dimensionen hier greifen

| Dim | Konkretes Szenario | Heute möglich? |
|-----|--------------------|----------------|
| **1. Intent** | "Mach was zum Anhören über Klimawandel" → erkennt Podcast | ✅ Material-Router erkennt "podcast" |
| **2. Proaktivität** | Nach Podcast: "Soll ich ein Quiz zum Hörverständnis erstellen?" | ⚠️ Muss Main Agent machen |
| **3. Rückfragen** | "Wie viele Sprecher? Welcher Stil? (Interview, Reportage, Dialog?)" | ❌ One-Shot, keine Rückfragen |
| **4. Technik** | Skript → DOCX ✅. Audio → ElevenLabs ✅. Aber: Audio-Generierung kann fehlschlagen (API-Limits) | ⚠️ Fehlertoleranz bei TTS |
| **5. Sprache** | Podcast auf Englisch für Englisch-Unterricht | ⚠️ Muss explizit gesagt werden. ElevenLabs unterstützt Multilingual |
| **6. Iteration** | Erst Skript zeigen, dann Audio generieren | ⚠️ Unklar ob Skript vor Audio gezeigt wird |
| **7. Überarbeitung** | "Ändere den Einstieg, der ist zu langweilig" | ❌ Kein Szenen-Patch. Nur komplett neu. |
| **8. Export** | Skript als DOCX ✅. Audio als MP3 ✅. Beides teilbar via Code | ✅ |
| **9. Erweiterung** | "Erstelle auch ein Arbeitsblatt zum Podcast" | ✅ Main Agent hat Kontext |
| **10. Kontext** | "Mach den Podcast kürzer" nach Erstellung | ⚠️ Nur über Neugenierung |
| **11. Präferenzen** | "Ich will immer Interview-Format" → nächstes Mal automatisch | ✅ Memory Agent |
| **12. Pädagogik** | Altersgerechte Sprache, fachlich korrekt, verschiedene Perspektiven | ⚠️ Ohne Wissenskarte kein Fach-Didaktik-Wissen |
| **13. Fehler** | ElevenLabs API down → nur Skript ausgeben | ⚠️ Muss getestet werden |
| **14. Quellen** | Fachliche Aussagen im Podcast → woher? | ❌ Kein Quellennachweis im Skript |
| **15. Teilbarkeit** | Audio per Zugangscode + QR-Code | ✅ Audio-Sharing implementiert |

### Gaps beim Podcast

| Gap | Impact | Aufwand |
|-----|--------|---------|
| Keine Sub-Agent-Rückfragen (Dim 3) | Agent rät Stil/Format statt zu fragen | Hoch |
| Kein Szenen-Patch (Dim 7) | "Ändere den Einstieg" → komplette Neugenerierung | Hoch |
| Skript vor Audio? (Dim 6) | Unklar ob Lehrkraft Skript prüfen kann bevor Audio generiert wird | Mittel |
| Keine Quellenangaben (Dim 14) | Fachliche Behauptungen im Podcast ohne Nachweis | Niedrig |
| TTS-Fehlerhandling (Dim 13) | Was wenn ElevenLabs ausfällt? Graceful Degradation? | Niedrig |

---

## Muster: Was bei ALLEN Material-Jobs fehlt

Aus beiden Beispielen kristallisieren sich **4 architektonische Gaps**, die jeden Material-Job betreffen:

| # | Gap | Betroffene Dimensionen | Architektur-Lösung |
|---|-----|----------------------|-------------------|
| **A** | Sub-Agents können keine Rückfragen stellen | 3, 6, 13 | Multi-Turn Subagent (agent_sessions) — designed, nicht implementiert |
| **B** | Kein Enzel-Element-Patch außer Klausuren | 7, 10 | Patch-Logik generalisieren (Rätsel, Szenen, Fragen) |
| **C** | Keine Wissenskarte aktiv | 11, 12 | agent_knowledge Tabelle + build_wissenskarte implementieren |
| **D** | Kein Entwurf-vor-Export Workflow | 6 | Main Agent zeigt Sub-Agent-Output im Chat, fragt "Passt das?" |

### Prioritäten-Vorschlag

```
Schnellste Wirkung (Tage):
  → Gap D: Entwurf im Chat zeigen (nur Main-Agent-Logik ändern)
  → Gap C teilweise: Generische Fach-Profile seeden

Mittlerer Aufwand (Wochen):
  → Gap B: Patch-Logik für Escape Room + Podcast
  → Gap C komplett: Wissenskarte + Learning-Loop

Größter Aufwand (Sprint):
  → Gap A: Multi-Turn Subagent Rückfragen
```

---

## Die Wissenskarte — 3 Schichten im Detail

Jeder Material-Agent soll Zugriff auf 3 Wissensschichten haben:

```
┌─────────────────────────────────────────────┐
│  Schicht 3: PERSÖNLICH (Teacher Preferences) │  ← Memory Agent schreibt
│  "Steffen will immer 5 Rätsel"               │  ← ✅ Funktioniert heute
│  "Michelle bevorzugt Interview-Format"        │
├─────────────────────────────────────────────┤
│  Schicht 2: BEWÄHRT (Good Practices)         │  ← Material-Learning Agent schreibt
│  "Dieses Rätsel bekam Rating 5/5"            │  ← ⚠️ Designed, nicht implementiert
│  "Dieser Podcast-Einstieg funktionierte gut"  │
├─────────────────────────────────────────────┤
│  Schicht 1: GENERISCH (Fach-Profile)         │  ← Von uns manuell gepflegt
│  "Geschichte: Quellenkritik ist zentral"      │  ← ⚠️ Designed, nicht implementiert
│  "Bio: Experimente und Alltagsbezüge"         │
└─────────────────────────────────────────────┘
```

**Escape Room Beispiel:**
- Generisch: "Geschichte-Escape-Rooms brauchen authentische Quellen als Rätsel-Basis"
- Bewährt: "Rätsel mit Bildanalyse funktionieren besser als reine Textaufgaben"
- Persönlich: "Steffen will immer eine Lösungskarte für die Lehrkraft"

**Podcast Beispiel:**
- Generisch: "Bio-Podcasts profitieren von Alltagsbezügen im Einstieg"
- Bewährt: "Interview-Format mit Experte + Schüler-Perspektive funktioniert gut"
- Persönlich: "Michelle will immer Regieanweisungen für Pausen"

---

## Entscheidungsfragen fürs Team

- [ ] Stimmen die 15 Dimensionen? Fehlt etwas? Ist etwas unwichtig?
- [ ] Welche der 4 Gaps (A-D) sind Dealbreaker für den Launch?
- [ ] Sollen Sub-Agents Rückfragen stellen können (Gap A) — oder reicht es wenn der Main Agent das übernimmt?
- [ ] Welche Material-Typen brauchen Einzel-Element-Patch (Gap B)? Alle oder nur die wichtigsten?
- [ ] Wer pflegt die generischen Fach-Profile (Schicht 1 der Wissenskarte)?
- [ ] Ab welcher Qualitätsstufe gehen wir live? (Vorschlag: Dim 1-4 + 12 müssen ≥ 80% Pass-Rate haben)
