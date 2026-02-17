# Deep Dive: JTBD "YouTube-Quiz erstellen"

> **Zweck:** Exemplarischer Deep-Dive eines einzelnen Jobs über alle Dimensionen.
> Dient als Diskussionsvorlage für das Team (Steffen, Christopher, Michelle)
> und als Blaupause für die Operationalisierung aller weiteren Jobs.
>
> **Stand:** Februar 2026

---

## Der Job

> "Ich als Lehrkraft möchte aus einem YouTube-Video ein Quiz erstellen,
> das ich meinen Schülern als Übung geben kann."

Dieser eine Job berührt **12 Dimensionen** unseres Systems. Jede Dimension ist eigenständig testbar.

---

## Dimension 1: Intent-Erkennung

> Erkennt das System zuverlässig, was ich will — egal wie ich es formuliere?

| ID | Testfall | Prompt | Erwartung | Methode |
|----|----------|--------|-----------|---------|
| YQ-1.1 | Klarer Intent | `Erstelle ein Quiz zu diesem Video: https://youtube.com/watch?v=xyz` | System startet Quiz-Erstellung | Regex |
| YQ-1.2 | Impliziter Intent | `Ich hab dieses Video gefunden, können meine Schüler das bearbeiten? https://youtube.com/watch?v=xyz` | System schlägt Quiz-Erstellung vor (nicht nur Zusammenfassung) | LLM-Judge |
| YQ-1.3 | Umgangssprache | `Mach mal was mit dem Video hier https://youtu.be/xyz` | System fragt nach oder schlägt Quiz + Alternativen vor | LLM-Judge |
| YQ-1.4 | Nur Link, kein Text | `https://youtube.com/watch?v=xyz` | System fragt: "Was möchtest du mit dem Video machen?" oder schlägt Optionen vor | LLM-Judge |
| YQ-1.5 | Verwechslung mit anderem Video-Typ | `Erstelle ein Quiz zu diesem Vimeo-Video: https://vimeo.com/123` | Klarer Hinweis: "Ich kann aktuell nur YouTube-Videos verarbeiten" | Regex |
| YQ-1.6 | Quiz ohne Video | `Erstelle ein Quiz zum Thema Photosynthese` | System erstellt Quiz aus Wissen (NICHT YouTube-Workflow) — korrekte Unterscheidung | LLM-Judge |

**Was wir messen:** Trefferquote der Intent-Erkennung über 20+ Formulierungsvarianten.

---

## Dimension 2: Proaktivität

> Schlägt das System von sich aus sinnvolle Aktionen vor?

| ID | Testfall | Prompt | Erwartung | Methode |
|----|----------|--------|-----------|---------|
| YQ-2.1 | Video im Gespräch → Quiz-Vorschlag | `Ich nutze morgen dieses Video im Unterricht: [URL]` | System schlägt proaktiv vor: Quiz, Zusammenfassung, Arbeitsblatt | LLM-Judge |
| YQ-2.2 | Nach Quiz → Weiteres Material | Quiz wurde erstellt | System fragt: "Soll ich auch ein Arbeitsblatt / eine Zusammenfassung zum Video erstellen?" | LLM-Judge |
| YQ-2.3 | Kontext-basierter Vorschlag | Profil sagt: "Klasse 9, Physik". Lehrkraft teilt Physik-Video. | Vorschlag passt zum Fach/Niveau | LLM-Judge |
| YQ-2.4 | Nicht aufdringlich | Lehrkraft will nur über das Video reden, kein Material | System drängt kein Quiz auf, sondern reagiert auf die tatsächliche Anfrage | LLM-Judge |

**Was wir messen:** Proaktive Vorschläge kommen in ≥ 70% der passenden Situationen, aber in < 10% der unpassenden.

---

## Dimension 3: Smarte Rückfragen

> Fragt das System nur das, was es wirklich braucht — und nichts, was es schon weiß?

| ID | Testfall | Prompt | Erwartung | Methode |
|----|----------|--------|-----------|---------|
| YQ-3.1 | Minimale Info → gezielte Rückfragen | `Mach ein Quiz zu [URL]` | System fragt: Klasse/Niveau? Anzahl Fragen? Fragetyp? — aber NICHT: Fach (erkennt es aus Video) | LLM-Judge |
| YQ-3.2 | Kontext schon gegeben | `Ich bereite Physik Klasse 9 vor. Erstelle ein Quiz zu [URL]` | System fragt NICHT nach Fach und Klasse (hat es schon), fragt nur noch fehlende Infos | LLM-Judge |
| YQ-3.3 | Profil nutzen | Profil: Physik, Klasse 8-10, Gymnasium. `Quiz zu [URL]` | System nutzt Profil-Defaults, fragt nur noch nach Feinheiten | LLM-Judge |
| YQ-3.4 | Präferenzen nutzen | Memory: "bevorzugt 10 Fragen". `Quiz zu [URL]` | System schlägt 10 Fragen vor, statt zu fragen "Wie viele Fragen?" | LLM-Judge |
| YQ-3.5 | Maximal 3 Rückfragen | Lehrkraft gibt nur URL | System stellt max. 3 Rückfragen, bündelt sie in einer Nachricht | LLM-Judge |
| YQ-3.6 | Nie redundant fragen | T1: `Physik Klasse 9`. T2: `Quiz zu [URL]`. | "Für welche Klasse?" wird NICHT gefragt | Roundtrip + LLM-Judge |

**Was wir messen:** Redundante Rückfragen = 0. Notwendige Rückfragen werden gestellt. Max. 1 Rückfrage-Turn.

---

## Dimension 4: Technische Zuverlässigkeit

> Funktioniert die YouTube-Verarbeitung zuverlässig?

| ID | Testfall | Input | Erwartung | Methode |
|----|----------|-------|-----------|---------|
| YQ-4.1 | Standard YouTube-URL | `https://www.youtube.com/watch?v=dQw4w9WgXcQ` | Transkript wird extrahiert, Quiz wird erstellt | Struktur |
| YQ-4.2 | Kurzlink | `https://youtu.be/dQw4w9WgXcQ` | Funktioniert identisch | Struktur |
| YQ-4.3 | URL mit Timestamp | `https://youtube.com/watch?v=xyz&t=120` | Funktioniert, optional: Quiz ab Minute 2 | Struktur |
| YQ-4.4 | Playlist-URL | `https://youtube.com/playlist?list=PLxyz` | Hinweis: "Bitte einzelnes Video teilen" oder erstes Video nutzen | Regex |
| YQ-4.5 | Privates Video | URL zu privatem Video | Klare Fehlermeldung: "Das Video ist nicht öffentlich zugänglich" | Regex |
| YQ-4.6 | Video ohne Untertitel | Video ohne Auto-Captions | Klarer Hinweis: "Kein Transkript verfügbar" + Alternative vorschlagen | Regex |
| YQ-4.7 | Sehr langes Video (> 60 Min) | 90-Minuten-Vorlesung | System verarbeitet es oder sagt: "Video ist sehr lang, soll ich mich auf einen Abschnitt konzentrieren?" | LLM-Judge |
| YQ-4.8 | Sehr kurzes Video (< 1 Min) | 30-Sekunden-Clip | System erstellt kürzeres Quiz oder weist darauf hin | LLM-Judge |
| YQ-4.9 | Nicht-deutsches Video | Englisches YouTube-Video | Transkript wird korrekt verarbeitet (→ Dimension 5: Sprache) | Struktur |
| YQ-4.10 | Ungültiger Link | `https://youtube.com/watch?v=UNGUELTIG` | "Video nicht gefunden" statt Crash | Regex |

**Was wir messen:** Erfolgsquote der Transkript-Extraktion über 20 verschiedene Videos. Ziel: ≥ 85%.

---

## Dimension 5: Sprachkompetenz

> Erkennt das System die Sprache des Videos und handelt kontextgerecht?

| ID | Testfall | Kontext | Erwartung | Methode |
|----|----------|---------|-----------|---------|
| YQ-5.1 | Deutsches Video → deutsches Quiz | Deutsches Physik-Video | Quiz ist auf Deutsch | LLM-Judge |
| YQ-5.2 | Englisches Video + Englisch-Unterricht | Profil: Englisch-Lehrer. Englisches Video. | Quiz ist auf Englisch (Fremdsprachenunterricht) | LLM-Judge |
| YQ-5.3 | Englisches Video + Sachfach | Profil: Biologie-Lehrer. Englisches Video über Zellen. | System fragt: "Quiz auf Deutsch oder Englisch?" ODER erkennt aus Kontext dass Deutsch | LLM-Judge |
| YQ-5.4 | Französisches Video | Profil: Französisch-Lehrer. Französisches Video. | Quiz auf Französisch | LLM-Judge |
| YQ-5.5 | Explizite Sprachangabe | `Erstelle ein Quiz auf Englisch zu [deutsches Video]` | Quiz ist auf Englisch, Inhalte basieren auf dem deutschen Video | LLM-Judge |
| YQ-5.6 | Mischsprache im Unterricht | `Erstelle ein Quiz, Fragen auf Deutsch, Fachbegriffe auf Englisch` | Fragen deutsch, Fachterminologie englisch | LLM-Judge |

**Was wir messen:** Korrekte Sprachzuordnung in ≥ 90% der Fälle. Unnötige Rückfragen zur Sprache ≤ 10%.

---

## Dimension 6: Iterativer Workflow (Entwurf → Feedback → Finalisierung)

> Bekomme ich erst einen Entwurf, den ich überarbeiten kann, bevor ich exportiere?

| ID | Testfall | Ablauf | Erwartung | Methode |
|----|----------|--------|-----------|---------|
| YQ-6.1 | Entwurf zuerst | Quiz-Erstellung angefragt | System zeigt Entwurf im Chat (Fragen + Antworten), NICHT sofort DOCX/H5P | LLM-Judge |
| YQ-6.2 | Feedback-Aufforderung | Nach Entwurf | System fragt: "Passt das so? Soll ich etwas ändern?" | LLM-Judge |
| YQ-6.3 | Export-Format am Ende | Nach Bestätigung des Entwurfs | System fragt: "In welchem Format? H5P (interaktiv) / DOCX / PDF" | LLM-Judge |
| YQ-6.4 | Direkt-Export wenn gewünscht | `Erstelle ein Quiz als H5P zu [URL]` | System überspringt Entwurf, generiert direkt H5P (Lehrkraft hat Format vorgegeben) | LLM-Judge |
| YQ-6.5 | Mehrfach iterieren | Entwurf → Feedback → neuer Entwurf → nochmal Feedback → Export | Funktioniert über 3+ Iterationsrunden | Roundtrip |

**Was wir messen:** Entwurf wird in ≥ 80% der Fälle vor Export gezeigt. Export-Format wird abgefragt (nicht angenommen).

---

## Dimension 7: Zielgerichtete Überarbeitung

> Kann ich präzise einzelne Teile ändern, ohne alles neu zu erstellen?

| ID | Testfall | Prompt (nach Entwurf) | Erwartung | Methode |
|----|----------|----------------------|-----------|---------|
| YQ-7.1 | Einzelne Frage ändern | `Ändere Frage 3 — die ist zu leicht` | Nur Frage 3 wird geändert, Rest bleibt identisch | Roundtrip + LLM-Judge |
| YQ-7.2 | Frage hinzufügen | `Füge noch eine Frage zum Schluss des Videos hinzu` | Neue Frage wird ergänzt, bestehende bleiben | Roundtrip + LLM-Judge |
| YQ-7.3 | Frage entfernen | `Lösche Frage 5, die passt nicht` | Frage 5 entfernt, Nummerierung angepasst | Roundtrip + LLM-Judge |
| YQ-7.4 | Schwerpunkt verschieben | `Mehr Fragen zum zweiten Teil des Videos` | Fragen-Balance verschiebt sich, aber gute Fragen vom Anfang bleiben | Roundtrip + LLM-Judge |
| YQ-7.5 | Schwierigkeit anpassen | `Mach das Quiz insgesamt leichter` | Fragen werden vereinfacht, aber thematisch bleibt alles gleich | Roundtrip + LLM-Judge |
| YQ-7.6 | Fragetyp ändern | `Mach aus den Multiple-Choice-Fragen Lückentexte` | Fragetyp ändert sich, Inhalt bleibt | Roundtrip + LLM-Judge |
| YQ-7.7 | Spezifisches Feedback | `Frage 2: Die richtige Antwort ist eigentlich B, nicht C` | System korrigiert die Frage basierend auf Lehrkraft-Input | Roundtrip + LLM-Judge |

**Was wir messen:** Änderungen treffen genau das angesprochene Element. Nicht-betroffene Fragen bleiben zu 100% unverändert.

---

## Dimension 8: Export-Flexibilität

> Kann ich das Quiz in verschiedenen Formaten bekommen?

| ID | Testfall | Prompt | Erwartung | Methode |
|----|----------|--------|-----------|---------|
| YQ-8.1 | H5P-Export | `Exportiere als H5P` | H5P-Übungen erstellt, Zugangscode + QR-Code generiert | Struktur |
| YQ-8.2 | DOCX-Export | `Exportiere als Word` | DOCX mit Fragen, Antwortoptionen, Lösungsblatt | Struktur |
| YQ-8.3 | PDF-Vorschlag | `Gib mir das als PDF` | System generiert DOCX und weist darauf hin, oder generiert direkt druckbares Format | LLM-Judge |
| YQ-8.4 | Format-Wechsel | Erst H5P, dann: `Gib mir das auch als Word` | DOCX mit identischen Fragen wie das H5P | Roundtrip + Struktur |
| YQ-8.5 | Beides gleichzeitig | `Erstelle H5P für die Schüler und ein Word-Dokument für meine Unterlagen` | Beide Formate generiert | Struktur |

---

## Dimension 9: Material-Erweiterung (Cross-Material)

> Kann ich aus demselben Video noch mehr machen?

| ID | Testfall | Prompt (nach Quiz-Erstellung) | Erwartung | Methode |
|----|----------|-------------------------------|-----------|---------|
| YQ-9.1 | Zusammenfassung | `Erstelle auch eine Zusammenfassung des Videos` | Zusammenfassung basiert auf demselben Transkript | Roundtrip + LLM-Judge |
| YQ-9.2 | Arbeitsblatt | `Erstelle ein Arbeitsblatt zum Video` | Arbeitsblatt mit Aufgaben, die über Quiz hinausgehen (offene Fragen, Analyse) | Roundtrip + LLM-Judge |
| YQ-9.3 | Vokabelliste (Fremdsprache) | `Erstelle eine Vokabelliste zum Video` (englisches Video) | Liste mit relevanten Vokabeln + Übersetzungen | Roundtrip + LLM-Judge |
| YQ-9.4 | Lückentext | `Mach einen Lückentext basierend auf dem Video` | Lückentext nutzt Kerninhalte des Videos | Roundtrip + LLM-Judge |
| YQ-9.5 | Stundenplanung | `Plane eine Stunde rund um das Video` | Verlaufsplan mit Video als Kernmedium + Quiz als Sicherung | Roundtrip + LLM-Judge |

**Was wir messen:** System nutzt denselben Video-Kontext weiter (kein erneutes Transkript-Laden nötig). Materialien sind inhaltlich konsistent.

---

## Dimension 10: Kontextbewahrung (Multi-Turn)

> Bleibt der Kontext über das ganze Gespräch erhalten?

| ID | Testfall | Ablauf | Erwartung | Methode |
|----|----------|--------|-----------|---------|
| YQ-10.1 | Video-Kontext bleibt | T1: Quiz erstellen. T5: `Welches Video haben wir nochmal benutzt?` | System nennt korrekt das Video | Roundtrip |
| YQ-10.2 | Änderungen kumulieren | T1: Quiz. T2: Frage 3 ändern. T3: Frage 5 hinzufügen. T4: `Zeig mir den aktuellen Stand` | Alle Änderungen sind berücksichtigt | Roundtrip |
| YQ-10.3 | Neues Thema → zurück | T1: Quiz zum Video. T2-T4: Anderes Thema. T5: `Zurück zum Video-Quiz — exportiere als H5P` | System hat Quiz noch im Kontext | Roundtrip |
| YQ-10.4 | Session-übergreifend | Session 1: Quiz erstellt. Session 2: `Letzte Woche hab ich ein Quiz zu einem YouTube-Video gemacht...` | System findet es über Memory/History | Roundtrip |

---

## Dimension 11: Präferenz-Lernen

> Merkt sich das System meine Vorlieben für zukünftige Quiz-Erstellungen?

| ID | Testfall | Ablauf | Erwartung | Methode |
|----|----------|--------|-----------|---------|
| YQ-11.1 | Anzahl merken | Lehrkraft sagt: `Ich möchte immer mindestens 10 Fragen`. Nächstes Quiz. | System schlägt 10 Fragen vor (nicht 5) | Roundtrip + DB-Check |
| YQ-11.2 | Fragetyp merken | Lehrkraft nutzt 3x Multiple-Choice. Nächstes Quiz ohne Angabe. | System wählt MC als Default | Roundtrip + LLM-Judge |
| YQ-11.3 | Schwierigkeit merken | Lehrkraft korrigiert 2x "zu leicht". | System erstellt schwierigere Fragen beim nächsten Mal | LLM-Judge |
| YQ-11.4 | Format-Präferenz | Lehrkraft wählt 3x H5P. | System schlägt H5P als Default-Format vor | Roundtrip + LLM-Judge |
| YQ-11.5 | Nicht über-generalisieren | Lehrkraft sagt "10 Fragen" für Klasse 10. Erstellt Quiz für Klasse 5. | System fragt nach oder passt an (10 Fragen ist vielleicht zu viel für Klasse 5) | LLM-Judge |

**Was wir messen:** Nach 3 gleichen Entscheidungen wird die Präferenz als Default übernommen. Aber: kontextsensitiv, nicht blind.

---

## Dimension 12: Pädagogische Qualität

> Sind die generierten Fragen didaktisch sinnvoll?

| ID | Testfall | Kriterium | Erwartung | Methode |
|----|----------|-----------|-----------|---------|
| YQ-12.1 | Kognitive Niveaus | Quiz zu einem Erklärvideo | Fragen decken verschiedene Bloomsche Taxonomiestufen ab (Wissen, Verstehen, Anwenden) — nicht nur Faktenwissen | LLM-Judge |
| YQ-12.2 | Gute Distraktoren | Multiple-Choice-Fragen | Falsche Antworten sind plausibel (nicht offensichtlich falsch), basieren auf typischen Fehlvorstellungen | LLM-Judge |
| YQ-12.3 | Video-Bezug | Quiz basierend auf Video | Fragen beziehen sich auf konkrete Inhalte des Videos, nicht auf allgemeines Vorwissen | LLM-Judge |
| YQ-12.4 | Altersgerecht | Quiz für Klasse 5 vs. Klasse 12 | Sprache und Komplexität passen zur Altersstufe | LLM-Judge |
| YQ-12.5 | Keine Trivialfragen | Quiz mit 10 Fragen | Weniger als 20% der Fragen sind reine "Was hat der Sprecher gesagt?"-Reproduktion | LLM-Judge |
| YQ-12.6 | Lernziel-Orientierung | Fragen im Quiz | Fragen prüfen Verständnis des Kernthemas, nicht Randdetails | LLM-Judge |

**Was wir messen:** LLM-Judge bewertet jede Frage auf einer Skala 1-5 (didaktische Qualität). Ziel: Durchschnitt ≥ 3.5.

---

## Dimension 13: Fehlertoleranz & Edge Cases

> Was passiert, wenn etwas schiefgeht?

| ID | Testfall | Input | Erwartung | Methode |
|----|----------|-------|-----------|---------|
| YQ-13.1 | Transkript-Extraktion scheitert | Video ohne Untertitel | Klare Meldung + Alternative (z.B. "Beschreibe mir den Inhalt, dann erstelle ich ein Quiz") | LLM-Judge |
| YQ-13.2 | Video nicht erreichbar | URL existiert nicht mehr | "Das Video ist nicht verfügbar" — kein Crash | Regex |
| YQ-13.3 | Altersbeschränktes Video | YouTube-Video mit Altersbeschränkung | Hinweis, dass das Video nicht verarbeitet werden kann | Regex |
| YQ-13.4 | Extrem schlechtes Transkript | Auto-generierte Untertitel mit vielen Fehlern | System erkennt schlechte Qualität und warnt: "Das Transkript hat möglicherweise Fehler" | LLM-Judge |
| YQ-13.5 | Unangemessener Inhalt | Video mit problematischem Inhalt | System warnt oder lehnt ab | LLM-Judge |
| YQ-13.6 | Timeout bei langen Videos | 2-Stunden-Vorlesung | System gibt Zwischenstatus oder schlägt Abschnitt vor, statt einfach zu hängen | Latenz + LLM-Judge |

---

## Dimension 14: Quellenreferenz & Timestamps

> Kann ich nachvollziehen, woher die Fragen kommen?

| ID | Testfall | Kriterium | Erwartung | Methode |
|----|----------|-----------|-----------|---------|
| YQ-14.1 | Timestamps zu Fragen | Quiz mit 5 Fragen | Jede Frage hat einen ungefähren Timestamp (z.B. "Minute 3:20") | Regex |
| YQ-14.2 | Video-Titel in Quellenangabe | Quiz-Export (DOCX) | Dokument enthält Video-Titel und URL als Quellenangabe | Struktur |
| YQ-14.3 | Timestamp-Links | Im Chat-Entwurf | Timestamps sind klickbar (Link zum Video an der Stelle) | Regex |

---

## Dimension 15: Teilbarkeit

> Wie teile ich das Quiz mit meinen Schülern?

| ID | Testfall | Kriterium | Erwartung | Methode |
|----|----------|-----------|-----------|---------|
| YQ-15.1 | Zugangscode (H5P) | H5P-Export | Code wie `tiger42` wird generiert | Regex |
| YQ-15.2 | QR-Code | H5P-Export | QR-Code-Bild wird angezeigt | Regex |
| YQ-15.3 | Schülerseite funktioniert | Code aus YQ-15.1 über Browser aufrufen | Seite zeigt Quiz, ohne Login | Struktur |
| YQ-15.4 | DOCX ist druckfertig | DOCX-Export | Sauberes Layout, Seitennummerierung, Platz für Name/Datum | Struktur |

---

## Zusammenfassung: Alle Dimensionen auf einen Blick

| # | Dimension | Kernfrage | Anzahl Tests | Prüfmethoden |
|---|-----------|-----------|-------------|--------------|
| 1 | **Intent-Erkennung** | Versteht es mich? | 6 | Regex, LLM-Judge |
| 2 | **Proaktivität** | Schlägt es Sinnvolles vor? | 4 | LLM-Judge |
| 3 | **Smarte Rückfragen** | Fragt es nur was nötig ist? | 6 | LLM-Judge, Roundtrip |
| 4 | **Technische Zuverlässigkeit** | Funktioniert die YouTube-Pipeline? | 10 | Struktur, Regex |
| 5 | **Sprachkompetenz** | Erkennt es die richtige Sprache? | 6 | LLM-Judge |
| 6 | **Iterativer Workflow** | Entwurf → Feedback → Export? | 5 | LLM-Judge, Roundtrip |
| 7 | **Zielgerichtete Überarbeitung** | Kann ich gezielt ändern? | 7 | Roundtrip, LLM-Judge |
| 8 | **Export-Flexibilität** | H5P, DOCX, PDF? | 5 | Struktur |
| 9 | **Material-Erweiterung** | Weiteres Material aus gleichem Video? | 5 | Roundtrip, LLM-Judge |
| 10 | **Kontextbewahrung** | Bleibt alles im Gedächtnis? | 4 | Roundtrip |
| 11 | **Präferenz-Lernen** | Merkt es sich meine Vorlieben? | 5 | Roundtrip, DB-Check |
| 12 | **Pädagogische Qualität** | Sind die Fragen didaktisch gut? | 6 | LLM-Judge |
| 13 | **Fehlertoleranz** | Was passiert bei Problemen? | 6 | Regex, LLM-Judge, Latenz |
| 14 | **Quellenreferenz** | Woher kommen die Fragen? | 3 | Regex, Struktur |
| 15 | **Teilbarkeit** | Wie kommt es zum Schüler? | 4 | Regex, Struktur |
| | **Gesamt** | | **82** | |

---

## Diese Dimensionen sind universell

Die 15 Dimensionen gelten nicht nur für YouTube-Quiz. Sie lassen sich auf **jeden JTBD** anwenden:

| Dimension | YouTube-Quiz | Klausur erstellen | Differenzierung | Stundenplanung |
|-----------|-------------|-------------------|-----------------|----------------|
| Intent-Erkennung | ✅ | ✅ | ✅ | ✅ |
| Proaktivität | ✅ | ✅ | ✅ | ✅ |
| Smarte Rückfragen | ✅ | ✅ | ✅ | ✅ |
| Technische Zuverlässigkeit | YouTube-API | DOCX-Export | DOCX-Export | — |
| Sprachkompetenz | ✅ | ✅ | ✅ | ✅ |
| Iterativer Workflow | ✅ | ✅ | ✅ | ✅ |
| Zielgerichtete Überarbeitung | ✅ | ✅ | ✅ | ✅ |
| Export-Flexibilität | H5P/DOCX/PDF | DOCX | DOCX | DOCX |
| Material-Erweiterung | Video→Quiz→AB | Klausur→Übung | Diff→H5P | Plan→Material |
| Kontextbewahrung | ✅ | ✅ | ✅ | ✅ |
| Präferenz-Lernen | ✅ | ✅ | ✅ | ✅ |
| Pädagogische Qualität | ✅ | ✅ | ✅ | ✅ |
| Fehlertoleranz | ✅ | ✅ | ✅ | ✅ |
| Quellenreferenz | Timestamps | Lehrplanbezug | — | Lehrplanbezug |
| Teilbarkeit | QR/Code | Druck | Druck | — |

**Erkenntnis:** Wenn wir die 15 Dimensionen einmal sauber für YouTube-Quiz operationalisieren, haben wir eine Schablone für alle weiteren Jobs. Die jobspezifischen Unterschiede liegen hauptsächlich in Dimension 4 (Technische Zuverlässigkeit) und den konkreten Testprompts.

---

## Vorschlag für das Team-Meeting

### Agenda (60 Min)

1. **(10 Min)** Dieses Dokument durchgehen — stimmen die 15 Dimensionen?
2. **(15 Min)** YouTube-Quiz Beispiel diskutieren — fehlt etwas? Ist etwas unwichtig?
3. **(15 Min)** Priorisierung der Dimensionen:
   - Welche Dimensionen sind **Dealbreaker** (muss perfekt funktionieren)?
   - Welche sind **Differenzierungsmerkmale** (besser als Wettbewerb)?
   - Welche sind **Nice-to-have** (später)?
4. **(10 Min)** Zweiten Job auswählen und gegen die Dimensionen halten
5. **(10 Min)** Nächste Schritte: Wer schreibt die Testsets? Wann erste Baseline?

### Entscheidungsfragen fürs Team

- [ ] Soll das System **immer** einen Entwurf zeigen, oder ist "direkt exportieren" OK?
- [ ] Wie viele Rückfragen sind akzeptabel? (Vorschlag: max. 1 Turn mit gebündelten Fragen)
- [ ] Welche Export-Formate sind Pflicht für MVP? (Vorschlag: H5P + DOCX)
- [ ] Sollen Timestamps Pflicht sein? (Aufwand vs. Nutzen)
- [ ] Ab welcher Qualitätsstufe gehen wir live? (Vorschlag: ≥ 80% Pass-Rate auf Tier-1-Dimensionen)
