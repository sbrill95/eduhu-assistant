# Architektur-Entscheidungen (2026-02-16)

## Gemini Pro Review — Steffens Kommentare

### 1. Latenz (Kette User→Hauptagent→Router→Subagent)
**Entscheidung:** Akzeptabel. SSE Step-Labels zeigen dem User was gerade passiert ("📝 Material wird erstellt..."). Kein Handlungsbedarf.

### 2. Wissenskarte
**Entscheidung:** VERWENDEN. Wissenskarte wird in den System-Prompt des Sub-Agents injiziert.

### 3. get_full_context
**Entscheidung:** Nur als Fallback. Jeder Sub-Agent bekommt eine **Zusammenfassung der wichtigsten Infos** vom Hauptagent als Übergabe (ist schon so implementiert via MaterialRequest). `get_full_context` nur wenn der Sub-Agent aus der Zusammenfassung nicht schlau wird.

### 4. Konflikte Defaults/Preferences/Good Practices — Priorisierung
**Entscheidung:** Nutzerwissen (Teacher Preferences) > Generische Good Practices. ABER: Agent darf und soll selbständig lernen — Trial & Error. Er entscheidet selbst, wie er aus den verschiedenen Quellen etwas Gutes zusammenbaut. Keine starre Priorisierungsregel. Geminis Kritik (zu rigide Hierarchie) → widersprochen: Agent soll iterieren und eigene Entscheidungen treffen.

### 5. Quality Score + Feedback-Loop
**Entscheidung:** Erstmal KEIN explizites Rating (kein 👍/👎 Button). Implizit: Download/Weiterverwendung = positiv. 
**Zusätzlich:** Wenn User im Hauptagent-Chat Feedback gibt ("gefällt mir nicht, mach das anders"), fließt dieses Feedback an den Sub-Agent zurück. Der Hauptagent leitet Korrekturen/Preferences aus dem Gespräch ab → speichert in `agent_knowledge`. So lernt der Sub-Agent aus dem Dialog, ohne expliziten Rating-Button.

### 6. Router-Starrheit
**Entscheidung:** Akzeptabel für Prototyp. Hauptagent klassifiziert den material_type, Router dispatcht deterministisch. Falls nötig, kann Hauptagent bei Unklarheit den User fragen.
