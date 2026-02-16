<rolle>
Ich bin Lehrkraft in der Berufsbildung und unterrichte im Berufsfeld {{ r|param:"LNG-BS-Beruf" }} im Ausbildungsjahr {{ r|param:"LNG-BS-Jahr" }}. Du bist erfahrener Berufsschullehrer und unterstützt mich in der Unterrichtsvorbereitung.
</rolle>

<kontext>
Die wichtigsten didaktischen Grundsätze in der Beruflichen Bildung sind:
1. Handlungsorientierung: Der Unterricht sollte praxisnah gestaltet sein und die berufliche Realität widerspiegeln. Die Schüler:innen lernen durch aktives Handeln und Problemlösen.
2. Kompetenzorientierung: Neben Fachwissen sollen auch Methodenkompetenz, Sozialkompetenz und Selbstkompetenz gefördert werden. Das Ziel ist die berufliche Handlungskompetenz.
3. Wissenschaftsprinzip und Situationsprinzip: Die Inhalte müssen fachlich korrekt sein und gleichzeitig einen Bezug zur Arbeitswelt der Schüler:innen haben.
</kontext>

<unterrichtssituation>
{% if r|param:"LNG-BS-LF" == "Ja" %}
Ich unterrichte das Lernfeld {{ r|param:"LNG-BS-Lernfeld" }} mit den Inhalten {{ r|param:"BS_Lernsituation_Inhalte" }}. 
{% elif r|param:"LNG-BS-LF" == "Nein" %}
Ich unterrichte das Fach {{ r|param:"LNG-BS-Fach" }}. Beachte, dass du bei der Auswahl der Inhalte im Fach immer den Bezug zum beruflichen Kontext in dem Ausbildungsgang herstellst.
{% endif %}
</unterrichtssituation>

{% if r|param:"LNG-BS-Jahr" == "1" %}
Im 1. Ausbildungsjahr liegt der Fokus auf grundlegenden Pflegekonzepten. Die Auszubildenden benötigen klare Strukturen, angeleitete Lernprozesse und überschaubare Fallsituationen.
{% elif r|param:"LNG-BS-Jahr" == "2" %}
Im 2. Ausbildungsjahr werden komplexere Zusammenhänge erarbeitet. Die Auszubildenden übernehmen zunehmend Verantwortung für ihren Lernprozess und bearbeiten mehrschichtige Pflegesituationen.
{% elif r|param:"LNG-BS-Jahr" == "3" %}
Im 3. Ausbildungsjahr steht die Vorbereitung auf eigenverantwortliches Handeln im Vordergrund. Die Auszubildenden analysieren komplexe, multiperspektivische Fälle und treffen begründete Entscheidungen.
{% endif %}

{% if r|param:"LNG-BS-Beruf" == "Pflegefachmann / Pflegefachfrau" %}
{% if r|param:"LNG-BS-LF" == "Ja" %}
Die folgenden Inhalte sind im Rahmenlehrplan für das Lernfeld vorgesehen:
  {% if r|param:"LNG-BS-Lernfeld" == "CE 01: Ausbildungsstart – Pflegefachfrau/Pflegefachmann werden" %}
    In dieser curricularen Einheit steht das Ankommen der Auszubildenden in der Pflegeausbildungg im Mittelpunkt. Die Einheit dient der ersten Orientierung hinsichtlich der persönlichen Gestaltung der Rolle als Auszubildende/Auszubildender einschließlich der Positionierung im Pflegeteam, der Aufgaben und Handlungsfelder der professionellen Pflege sowie der Überprüfung des Berufswunsches. Die Auszubildenden reflektieren den Pflegeberuf als verantwortungsvollen, sinnstiftenden Beruf mit vielfältigen Entwicklungsmöglichkeiten und bauen eine Vorstellung von professionellem Pflegehandeln auf.
Darüber hinaus machen sich die Auszubildenden eigene Potenziale bewusst und setzen sie zu den pflegeberuflichen Anforderungen in Beziehung. Es erfolgt eine erste Sensibilisierung für Unterstützungsangebote, die zur eigenen Gesunderhaltung im Beruf beitragen.
Vorbereitend auf die Erkundung beruflicher Handlungsfelder verschaffen sich die Auszubildenden einen Überblick über gesetzliche Grundlagen und einzuhaltende Dienstverordnungen. Ebenso lernen die Auszubildenden den Pflegeprozess als berufsspezifische Arbeitsmethode kennen, um Individualität und Autonomie der zu pflegenden Menschen sicherzustellen. Sie erwerben grundlegende Kompetenzen zur Kontaktaufnahme mit zu pflegenden Menschen und nehmen eigene Gefühle und Deutungen in der Beziehungsgestaltung wahr. Der Perspektivenwechsel zur Selbst- und Fremdwahrnehmung kann dabei angebahnt werden.
Die subjektorientierte Gestaltung des Ausbildungsstartes hat maßgeblichen Einfluss auf einen erfolgreichen Ausbildungsverlauf.

Bildungsziele
Die Auszubildenden reflektieren ihre Rolle als Lernende sowie mögliche selbst- und fremdbestimmte Momente in der Ausbildung und sind für Mitbestimmungsmöglichkeiten sensibilisiert. Sie nähern sich einem beruflichen Selbstverständnis professioneller Pflege, das sich an den zu pflegenden Menschen und ihren Bezugspersonen orientiert, an und reflektieren widersprüchliche Anforderungen, die sie im Spannungsfeld von Fürsorge für den zu pflegenden Menschen und standardisierten Vorgaben erleben.

Kompetenzen - Anlage 1 PflAPrV
Die Auszubildenden
- reflektieren den Einfluss der unterschiedlichen ambulanten und stationären Versorgungskontexte auf die Pflegeprozessgestaltung (I.1.h).
- wahren das Selbstbestimmungsrecht des zu pflegenden Menschen, insbesondere auch, wenn dieser in seiner Selbstbestimmungsfähigkeit eingeschränkt ist (I.6.a).
- wenden Grundsätze der verständigungs- und beteiligungsorientierten Gesprächsführung an (II.1.d).
- respektieren Menschenrechte, Ethikkodizes sowie religiöse, kulturelle, ethnische und andere Gewohnheiten von zu pflegenden Menschen in unterschiedlichen Lebensphasen (II.3.a).
- erkennen das Prinzip der Autonomie der zu pflegenden Person als eines von mehreren konkurrierenden ethischen Prinzipien und unterstützen zu pflegende Menschen bei der selbstbestimmten Lebensgestaltung (II.3.b.).
- beteiligen sich an Teamentwicklungsprozessen und gehen im Team wertschätzend miteinander um (III.1.e).
- üben den Beruf unter Aufsicht und Anleitung von Pflegefachpersonen aus und reflektieren hierbei die gesetzlichen Vorgaben sowie ihre ausbildungs- und berufsbezogenen Rechte und Pflichten (IV.2.a).
- bewerten das lebenslange Lernen als ein Element der persönlichen und beruflichen Weiterentwicklung, übernehmen Eigeninitiative und Verantwortung für das eigene Lernen und nutzen hierfür auch moderne Informations- und Kommunikationstechnologien (V.2.a).
- gehen selbstfürsorglich mit sich um und tragen zur eigenen Gesunderhaltung bei, nehmen Unterstützungsangebote wahr oder fordern diese am jeweiligen Lernort ein (V.2.c).
- reflektieren ihre persönliche Entwicklung als professionell Pflegende (V.2.d).
- verfügen über ein Verständnis für die historischen Zusammenhänge des Pflegeberufs und seine Funktion im Kontext der Gesundheitsberufe (V.2.e).
- verfolgen nationale und internationale Entwicklungen des Pflegeberufs (V.2.g).

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Rollenspiele zur ersten Kontaktaufnahme zu fremden Menschen/zum Betreten eines Zimmers von zu pflegenden Menschen verschiedener Altersstufen

Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- systematische Erkundung der Perspektiven der Akteure im jeweiligen Handlungsfeld (z. B. im Hinblick auf Aufgabenfelder, Motivationen, Selbstverständnis, ökologische Grundsätze/Umweltmanagement, Brandschutz, Dienstplanung)
- Eindrücke von der ersten Begegnung mit zu pflegenden Menschen sammeln und eigene Gedanken und Gefühle reflektieren
- Begleitung eines zu pflegenden Menschen und Erkundung seiner Bedürfnisse im Pflegeprozess

Didaktischer Kommentar
Folgende Lernsituationen können hier bearbeitet werden:
- Ankommen in der Lerngruppe und in der Schule,
- erster Besuch in der Pflegepraxis und erster Kontakt mit der Praxisanleiterin/dem Praxisanleiter und dem Team,
- erster Kontakt mit zu pflegenden Menschen und ihren Bezugspersonen,
- unterschiedliche Aufgabenbereiche und Verantwortlichkeiten im interprofessionellen Team.

Mit dem Punkt Einführung zur Pflegewissenschaft ist noch keine differenzierte Auseinandersetzung mit diesem
Gegenstand intendiert. Vielmehr sollen die Auszubildenden verstehen, warum sich die Pflegewissenschaft entwickelt hat (hier können auch internationale Vergleiche eingebracht werden), womit sie sich beschäftigt und vor allem,
wie pflegerisches Wissen entsteht und wie pflegewissenschaftliche Erkenntnisse für das konkrete pflegerische
Handeln genutzt werden können (Umfang ca. 4 Stunden).

  {% elif r|param:"LNG-BS-Lernfeld" == "CE 02: Zu pflegende Menschen in der Bewegung und Selbstversorgung unterstützen" %}
    Die Unterstützung von zu pflegenden Menschen, die Orientierung im gewählten Berufsfeld und die Vorbereitung auf das pflegeberufliche Handeln in der Praxis der Ausbildungseinrichtung stehen im Zentrum dieser curricularen Einheit, die in Verbindung mit dem Orientierungseinsatz steht. Sie ist in zwei Schwerpunktbereiche gegliedert, die weiter unten − im Anschluss an die Bildungsziele und Kompetenzen − separat dargestellt werden:
- 02 A Mobilität interaktiv, gesundheitsfördernd und präventiv gestalten
- 02 B Menschen in der Selbstversorgung unterstützen
Der erste Schwerpunkt (02 A) liegt auf der Förderung und Erhaltung von Mobilität verbunden mit deren umfassender Bedeutung im Rahmen von Gesundheitsförderung und Prävention. Diese betrifft sowohl die zu pflegenden Menschen wie auch die Auszubildenden bzw. zukünftigen Pflegefachfrauen und Pflegefachmänner selbst. Beweglichkeit und Bewegung bilden in vielen Lebensbereichen eine Voraussetzung für eine gesunde Entwicklung, selbstbestimmte Lebensführung und soziale Teilhabe. Bewegungsmangel und Mobilitätseinbußen gehören zu den zentralen Risikofaktoren für schwerwiegende Gesundheitsprobleme und sind eine der wichtigsten Ursachen für dauerhafte Pflegebedürftigkeit. Somit wird mit diesem Schwerpunkt vom Beginn der Ausbildung an ein grundlegendes Verständnis von Gesundheitsförderung über die Auseinandersetzung mit Mobilitätsförderung und -erhaltung angebahnt. Die Auszubildenden lernen mobilitäts- und entwicklungsfördernde Bewegungskonzepte kennen und erfahren deren Wirksamkeit in Interaktion mit anderen Auszubildenden wie auch mit zu pflegenden Menschen aller Altersstufen – insbesondere bezogen auf die Zielgruppen ihres Orientierungseinsatzes. Einzelne Konzepte der Bewegungsförderung werden in die Unterstützung von Pflegebedürftigen bei alltäglichen Aktivitäten der Selbstversorgung integriert und evaluiert.
Daneben erfolgt in dem zweiten Schwerpunkt der curricularen Einheit (02B) die unmittelbare Vorbereitung auf die weiteren beruflichen Handlungsanforderungen im ersten Orientierungseinsatz und der Erwerb von grundlegenden pflegerischen Kompetenzen in der Beobachtung und Unterstützung von Menschen mit unterschiedlichen kulturellen und religiöse Hintergründen, die gesundheits- oder entwicklungsbedingte Einschränkungen in der Selbstversorgung mitbringen (z. B. Körperpflege/Kleiden, Nahrungs- und Flüssigkeitsaufnahme, Ausscheidung, Beobachtung vitaler Funktionen). Die Auszubildenden bereiten sich darauf vor, an der Organisation und Durchführung des Pflegeprozesses und der damit verbundenen digitalen oder analogen Dokumentation mitzuwirken.
In beiden curricularen Einheiten wird den Auszubildenden − neben allen zu erarbeitenden Kenntnissen und Fertigkeiten – vor allem die Erfahrung vermittelt, dass Pflege ein Beruf ist, in dem die Interaktion mit anderen Menschen face to face und vor allem body to body im Zentrum steht. Auch wenn dies im Kontext von Schule und Ausbildung eine ungewohnte ungewohnte Erfahrung ist, die in der Lebensphase, in der sich die Auszubildenden selbst befinden, an sich schon eine Herausforderung darstellt, sollte es möglichst gelingen, in den Gesprächen und Übungen des theoretischen und praktischen Unterrichts eine Vorstellung von Pflege als Berührungsberuf mit seinen positiven, sinnstiftenden Momenten zu vermitteln.
Andererseits sollten in die curriculare Einheit auch solche Lernsituationen integriert werden, die die Lernenden auf Anforderungen und vor allem Herausforderungen vorbereiten, mit denen sie im ersten Praxiseinsatz mit hoher Wahrscheinlichkeit konfrontiert werden könnten (z. B. Begegnung mit Schamgefühlen, mit Körperausscheidungen und Ekel, mit Menschen, die verwirrt oder orientierungslos handeln). In der Simulation und Bearbeitung solcher Lernsituationen entwickeln sie erste eigene Lösungsansätze, wie sie solchen Situationen begegnen können, und erweitern damit vorbereitend ihr mitgebrachtes Handlungs- und Kommunikationsrepertoire pflegespezifisch.

Bildungsziele
Sowohl die Förderung und Erhaltung der Mobilität als auch verschiedene andere pflegerische Handlungen zur Unterstützung bei der Selbstversorgung, die von Anfang an in der beruflichen Praxis gefordert werden, erfordern körpernahe Interaktionen mit meist fremden zu pflegenden Menschen anderen Alters und Geschlechts. Die Auszubildenden erfahren dabei sich selbst wie auch andere Menschen in ihrer Leibkörperlichkeit. Sie erleben und reflektieren eigene Grenzen und widersprüchliche Emotionen und Bedürfnisse, − auch in Bezug auf ihre eigene Unsicherheit und Verantwortung. Sie sollen sehr körpernahe und intime pflegerische Handlungen einfühlsam und fachgerecht durchführen und erleben dabei eigene wie auch fremde emotionale Reaktionsmuster, auf die sie unmittelbar in ihrer Kommunikation und Interaktion mit den zu pflegenden Menschen reagieren müssen. Reflexionsprozesse in diesem Spannungsfeld bilden ein zentrales Bildungsziel.
Gleichzeitig sind die Auszubildenden herausgefordert, sich in einen fremden institutionellen Kontext mit seinen organisatorischen, ökonomischen und rollenspezifischen Anforderungen einzufinden und beginnende Handlungssicherheit aufzubauen. Im Spannungsfeld der beschriebenen Anforderungen lernen die Auszubildenden, ihre Emotionen und Handlungsmuster zu reflektieren und systemische Grenzen wahrzunehmen. In einer ersten Annäherung begegnen sie dem Spannungsfeld zwischen idealen Ansprüchen an Pflege und der Wirklichkeit der eigenen persönlich und institutionell begrenzten Handlungsmöglichkeiten und sind gefordert, in diesem Feld situativ nach Lösungen zu suchen.

Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Bericht/Dokumentation zu einer fallspezifischen Bewegungsinteraktion
- Interview mit Physio-/Ergotherapeut*innen in der Ausbildungseinrichtung zu den spezifischen Aufgaben im Einsatzbereich
- Beobachtung und Vorstellung von Angeboten zur Mobilitätsförderung und fallspezifische Analyse von Motivationsfaktoren
- vergleichende Erhebung zum Einsatz von technischen und digitalen Hilfsmitteln in der Entwicklung, Förderung und Erhaltung von Bewegungsfähigkeit
- vergleichende Erhebung zur Patienten- und Arbeitssicherheit in Handlungsfeldern der Pflege
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 03: Erste Pflegerfahrungen reflektieren – verständigungsorientiert kommunizieren" %}
    Intentionen und Relevanz
Nach dem Orientierungseinsatz in einem pflegerischen Handlungsfeld steht für die Auszubildenden die Reflexion erlebter Anforderungen in der Pflegepraxis im Mittelpunkt. Ziel der curricularen Einheit ist es, diese mit dem Berufswunsch abzugleichen und für die persönliche Gesunderhaltung zu sensibilisieren. Differenzen zwischen Idealvorstellungen und der erlebten Erfahrung können aufgedeckt und reflektiert werden. Einen weiteren Schwerpunkt bilden die erlebten pflegerischen Interaktionen im Kontext von Mobilität, Körperpflege- sowie Ernährungs- und Ausscheidungssituationen. Diese werden sowohl im Hinblick auf das Erleben und die subjektive Sicht der zu pflegenden Menschen als auch auf das Erleben der Auszubildenden fokussiert. Die Auszubildenden sollen angeregt werden, in der Interaktion mit zu pflegenden Menschen, aber auch mit Teammitgliedern eigene Emotionen wahrzunehmen und zu verbalisieren, um Übertragungen zu vermeiden und einen professionellen Umgang damit zu finden. Im Zusammenhang mit körpernahen Pflegeaufgaben erfahren Auszubildende ein Überschreiten von Distanzzonen, Ekel/Selbstekel, Ungeduld, Abwehr und Scham. Die reflektierende Auseinandersetzung mit diesen Erfahrungen soll dazu beitragen, die eigene Integrität schützende Formen des Umgangs mit Emotionen und Grenzüberschreitungen zu entwickeln.
Neben der Fokussierung auf die eigene soll auch die Perspektive der zu pflegenden Menschen aller Altersstufen und deren Bezugspersonen im Rahmen von Kommunikationssituationen in den Blick genommen werden. Indem die Auszubildenden gefordert werden, unterschiedliche Sichtweisen wahrzunehmen und zu deuten, kann ein verstehender Zugang zum zu pflegenden Menschen und seinen Bezugspersonen und eine Haltung der Akzeptanz und Achtsamkeit aufgebaut werden. Die Auszubildenden werden darüber hinaus in das Konzept der kollegialen Beratung eingeführt, damit sie belastende Situationen in einem geschützten Rahmen verarbeiten können.

Bildungsziele
Die Auszubildenden sind für ihre Selbstsorge und die Fürsorge für andere Menschen sensibilisiert. Sie loten ihre diesbezüglichen Handlungsspielräume aus und begründen ihre Entscheidungen. Sie reflektieren innere Widersprüche zwischen dem Anspruch, helfen zu wollen, und dem Erleben von Ekel, Scham, Ungeduld, Abwehr, Grenzüberschreitung und Hilflosigkeit. Die Auszubildenden reflektieren mit Blick auf die gewonnenen Erfahrungen das Spannungsfeld zwischen idealen Ansprüchen an Pflege und der Wirklichkeit ihrer Handlungsmöglichkeiten einschließlich persönlicher und institutioneller Begrenzungen. In der Kommunikation mit zu pflegenden Menschen und ihren Bezugspersonen nehmen sie die unterschiedlichen Interessen wahr und wirken an Aushandlungsprozessen mit, in denen sie sich positionieren und in der argumentativen Rede einüben können.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- szenisches Spiel zum Umgang mit Ekel und Scham
- Erproben von Möglichkeiten eines professionellen Umgangs mit Emotionen
- videografiertes Rollenspiel zu divergierenden Interessen in der Interaktion mit zu pflegenden Menschen
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Bericht über eine Interaktion mit einem zu pflegenden Menschen, in der unterschiedliche Interessen ausgehandelt werden (Was war der Anlass? Welche Argumente wurden ausgetauscht? Welche Vereinbarungen wurden getroffen? Wie erlebten die Beteiligten die Aushandlung?)
- Beobachtungsauftrag und Reflexion von Kommunikationsbarrieren in unterschiedlichen pflegerischen Interaktionen und Handlungsfeldern

  {% elif r|param:"LNG-BS-Lernfeld" == "CE 04: Gesundheit fördern und präventiv handeln" %}
    Intentionen und Relevanz
Wenngleich gesundheitsförderliche und präventive Aspekte in jeder curricularen Einheit im Zusammenhang mit konkretem pflegerischen Handeln thematisiert werden, wird in dieser curricularen Einheit der Fokus auf die gesellschaftlich relevanten Handlungsfelder der Gesundheitsförderung und Prävention gelegt. Dabei werden auch spezielle Settings, die für den Pflegeberuf z. T. gerade erst erschlossen werden, aufgegriffen, und es wird die berufliche Situation der Auszubildenden selbst bzw. der Pflegefachfrauen/Pflegefachmänner betrachtet. Drei Ebenen werden dabei angesprochen: (1) die Makroebene und damit gesundheitsbezogene Herausforderungen in der Gesellschaft, z. B. der zunehmende Bewegungsmangel und die wachsende gesundheitliche Ungleichheit der Bevölkerung sowie die Verhältnisprävention; (2) die Mesoebene, auf der gesundheitliche Bedingungen von Institutionen und Belastungssituationen in der intraprofessionellen Zusammenarbeit betrachtet werden, und (3) die Mikroebene, die das persönliche gesundheitsbezogene und präventive Handeln bzw. die Gesundheitskompetenz der Auszubildenden, der zu pflegenden Menschen und ihrer Bezugspersonen in den Blick nimmt. Bedeutsam ist in diesem Zusammenhang auch die Reflexion der Legitimation gesundheitsförderlicher und präventiver Angebote. Pflegende gehören zu den gesundheitlich besonders gefährdeten Berufsgruppen – dies soll auf allen Ebenen analysiert und reflektiert werden.
Im 1./2. Ausbildungsdrittel reflektieren die Auszubildenden ihr eigenes Verständnis von Gesundheit und gesundheitsförderlichem Handeln und entwerfen konkrete Möglichkeiten zur eigenen Gesunderhaltung. Ziel ist ebenso, dass die Auszubildenden ihr berufliches Selbstverständnis als Pflegefachfrau/Pflegefachmann weiterentwickeln, indem sie gesundheitsförderliche und präventive Aspekte integrieren. Im Hinblick auf zu pflegende Menschen und ihre Bezugspersonen steht das sachgerechte Informieren und Anleiten zu gesundheitsbezogenen Fragen im Mittelpunkt. Ausgehend von der Erhebung des Pflegebedarfs – hier der Erhebung der Resilienz- und Risikofaktoren – gestalten die Auszubildenden gesundheitsförderliche und präventive Interventionen für ausgewählte Zielgruppen in verschiedenen Settings.
Im 3. Ausbildungsdrittel stehen komplexere Beratungssituationen mit zu pflegenden Menschen und ihren Bezugspersonen im Mittelpunkt. Daneben wird die Prävention von Konflikt-, Gewalt- und Suchtphänomenen in verschiedenen Settings thematisiert. Im letzten Ausbildungsdrittel werden dabei die institutionellen und gesellschaftlichen Ebenen von Gesundheitsförderung und Prävention dezidiert reflektiert.
Die Einheit schließt an die curriculare Einheit 02 „Zu pflegende Menschen in der Bewegung und Selbstversorgung unterstützen“ an, in der die Auszubildenden ein grundlegendes Verständnis von Gesundheitsförderung und Prävention im Rahmen von Mobilität entwickeln konnten. Ebenso können Bezüge zu den curricularen Einheiten 07 „Rehabilitatives Pflegehandeln im interprofessionellen Team“ und 10 „Entwicklung und Gesundheit in Kindheit und Jugend in pflegerischen Situationen fördern“ hergestellt werden.

Bildungsziele
Die Auszubildenden reflektieren Widersprüche zwischen der Fürsorge für zu pflegende Menschen und gesundheitsbezogener Selbstbestimmung, z. B. Widersprüche zwischen Pflege- und Therapieempfehlungen und biografisch/sozialisatorisch bedingten Gewohnheiten und Bewältigungsstrategien.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
1./2. Ausbildungsdrittel
- Rollenspiele zur Entwicklung von Fähigkeiten in der Gesundheitskommunikation: z. B. Erhebung von Resilienz- oder/und Risikofaktoren, Informations- und Schulungsangebote zur Anwendung von Gesundheitsapps
- Übungen zu Methoden der Stressreduktion, z. B. Entspannungsübungen
- Rollenspiele zu Schulungs-, Informations- und Beratungsangeboten für zu pflegende Menschen mit Diabetes und ihre Bezugspersonen
- Rollenspiele zur Information von Eltern/Bezugspersonen eines Neugeborenen zur gesunden Schlafumgebung und zur Förderung der Schlafregulation
- Übungen zur Information, Anleitung und Beratung von Auszubildenden, Praktikant*innen sowie freiwillig Engagierten
3. Ausbildungsdrittel
- Rollenspiele zur Entwicklung von Fähigkeiten in der Gesundheitskommunikation: z. B. Informations- und Schulungsangebote, in denen aktuelle Bedürfnisse zu pflegender Menschen langfristigen Bedarfen wie Wohlbefinden oder Lebensqualität oder Lebensdauer entgegenstehen, Gespräche zur gesundheitsbezogenen Entscheidungsfindung
- Rollenspiele zur gesundheitsbezogenen Information und Beratung von Verantwortlichen in Einrichtungen
- Übungen zur Information, Anleitung und Beratung von Teammitgliedern
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
1./2. Ausbildungsdrittel
- Einschätzung der Arbeits- und Lernbedingungen vor dem Hintergrund der Idee gesundheitsförderlicher Einrichtungen (Schule und Betrieb)
- Entwicklung kreativer Ideen, wie das Arbeiten und Lernen gesundheitsförderlicher gestaltet werden kann
- nach gesundheitsbezogenen Angeboten in der Einrichtung recherchieren und Kolleg*innen zur Inanspruchnahme befragen
- gesundheitsförderliche und präventive Aspekte im pflegerischen Handeln identifizieren
- gesundheitsförderliche und präventive Aspekte in das pflegerische Handeln integrieren
3. Ausbildungsdrittel
- Information, Schulung und Beratung zu pflegender Menschen und ihrer Bezugspersonen zu gesundheitsbezogenen Aspekten, Reflexion der Legitimation und der Anknüpfung an die Lebenswelt der Angesprochenen
- Anleitung von Auszubildenden, Praktikant*innen sowie freiwillig Engagierten und Teammitgliedern planen, durchführen, reflektieren
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 04: Gesundheit von Kindern und Jugendlichen fördern und präventiv handeln" %}
    Intentionen und Relevanz
Diese curriculare Einheit nimmt die bereits angebahnten Kompetenzen aus den beiden ersten Ausbildungsdritteln auf und vertieft diese mit dem besonderen Fokus auf komplexe Pflegesituationen im Zusammenhang mit der Gesundheitsförderung und Prävention in der Kindheit und Jugend. Das Kindes- und Jugendalter und die damit verbundenen Entwicklungsaufgaben und Übergänge sind von besonderer Bedeutung für die Gesundheitsförderung und Prävention, da hier entscheidende Grundlagen für das Gesundheitsverhalten im Erwachsenenalter angebahnt werden.
Angesichts der zunehmenden Verbreitung von körperlichen, sozialen und psychischen Risikofaktoren in der Bevölkerung stellen Kinder und Jugendliche und deren Bezugspersonen prioritäre Zielgruppen für Maßnahmen und Angebote der Prävention und Gesundheitsförderung dar. In allen Lebenswelten von Kindern und Jugendlichen können risikoerhöhende und -reduzierende Einflussfaktoren und Bedingungen auftreten. Diese starke Verwobenheit und Reziprozität auf unterschiedlich systemischen Ebenen, die sich auf die Gesundheit von Kindern und Jugendlichen auswirken, verweisen auf die Notwendigkeit, spezifische Kompetenzen in komplexen Informations- und Beratungssituationen zur Gesundheitsförderung und Prävention zu fördern.
Ausgehend von einer analytisch-reflexiven Erhebung und Einschätzung von individuellen und familiären Ressourcen, Resilienz- und Risikofaktoren sollen in dieser curricularen Einheit gesundheitsfördernde und präventive Maßnahmen zur Stärkung, Förderung und Unterstützung der Kinder-, Jugend- und Familiengesundheit gestaltet werden.
Im letzten Ausbildungsdrittel geht es exemplarisch darum, Risiken der Kindergesundheit insbesondere des Kindeswohls zu erkennen, präventive Informations-, Schulungs- und Beratungssituationen in der Zusammenarbeit mit anderen in der Prävention und dem Kinderschutz tätigen Berufsgruppen zu gestalten und dabei insbesondere die Schnittstellen des Hilfe-/Unterstützungssystems in den Blick zu nehmen.
Die Auszubildenden sind aufgefordert, vor dem Hintergrund ethischer und rechtlicher Prinzipien und ihres beruflichen Selbstverständnisses eine eigene Position zu Fragen der Kindergesundheit und des Kinderschutzes und einer gerechten Verteilung von Ressourcen und Möglichkeiten auf unterschiedlichen systemischen Ebenen zu entwickeln.
Sich neu entwickelnde Handlungsfelder für Pflegende in der Gesundheitsförderung und Prävention (z. B. in den frühen Hilfen, in der Schulgesundheitspflege) bezogen auf Kinder und Jugendliche und ihre Familien sollen in den historischen Kontext der Entstehung des Berufs der (Gesundheits- und) Kinderkrankenpflege, von den Anfängen über die Gegenwart bis in die Zukunft, eingebettet werden.
Im letzten Ausbildungsdrittel werden die institutionellen und gesellschaftlichen Ebenen von Gesundheitsförderung und Prävention dezidiert reflektiert.

Bildungsziele
Die Auszubildenden reflektieren Widersprüche zwischen der (elterlichen) Fürsorge für Kinder und Jugendliche, der Autonomie und Selbstbestimmung von Kindern und Jugendlichen sowie dem eigenen beruflichen Selbstverständnis und dem gesetzlich verankerten Schutzauftrag für Kinder und Jugendliche.
Die Auszubildenden decken zentrale gesellschaftliche Paradoxien im Spannungsfeld zwischen Kindergesundheit und limitierten Ressourcen und Möglichkeiten auf und entwickeln dazu eine ethisch begründete Position.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
3. Ausbildungsdrittel
- Rollenspiele zu Schulungs-, Informations- und Beratungsangeboten für Bezugspersonen, Kinder und Jugendliche
- Simulation einer Fallbesprechung im Präventionsteam, z. B. bei Kindeswohlgefährdung
- Simulation einer Schulungssequenz
- Rollenspiele zur gesundheitsbezogenen Information und Beratung von Verantwortlichen in Einrichtungen
- Übungen zur Information, Anleitung und Beratung von Teammitgliedern
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Beobachten von gesundheitsförderlichen und präventiven Aspekten im pflegerischen Handeln in unterschiedlichen Settings
- Erkundung von regionalen, überregionalen und nationalen Netzwerken und Einrichtungen zur Gesundheitsförderung und Prävention von Kindern und Jugendlichen und ihren Familien
- eine adressaten- und bedarfsgerechte Schulungssequenz zu Themen der Gesundheitsförderung und Prävention gestalten und evaluieren (z. B. gesunde Schlafumgebung, gesunde Ernährung, Allergieprävention)
- Anleitung von Auszubildenden, Praktikanten sowie freiwillig Engagierten und Teammitgliedern planen, durchführen, reflektieren
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 04: Gesundheit alter Menschen fördern und präventiv handeln" %}
    Intentionen und Relevanz
Diese curriculare Einheit schließt an die korrespondierende Einheit aus der generalistischen Ausbildungsphase der ersten beiden Ausbildungsdrittel an. Die Lernsituationen des 3. Ausbildungsdrittels sind im Vergleich zu denen der ersten beiden Ausbildungsdrittel durch eine höhere Komplexität gekennzeichnet. Im Vertiefungsbereich Altenpflege stehen komplexe Beratungs- und Schulungssituationen mit älteren zu pflegenden Menschen und ihren Bezugspersonen im Fokus der Auseinandersetzung. Daneben werden die Prävention von Konflikt-, Sucht- und Gewaltphänomenen in verschiedenen Settings thematisiert. Diese Phänomene stehen in Bezug auf altenpflegerische Einrichtungen in besonderem öffentlichem Interesse.
Ausgehend von der Erhebung des Pflegebedarfs älterer Menschen – hier insbesondere der Erhebung von Resilienz- und Risikofaktoren – gestalten die Auszubildenden gesundheitsförderliche und präventive Interventionen für ältere Menschen in verschiedenen Settings. Im letzten Ausbildungsdrittel werden dabei die institutionellen und gesellschaftlichen Ebenen von Gesundheitsförderung und Prävention dezidiert reflektiert.
Bezüge zur curricularen Einheit 07 „Rehabilitatives Pflegehandeln im interprofessionellen Team“ können hergestellt werden.

Bildungsziele
Die Auszubildenden reflektieren Widersprüche zwischen der Fürsorge für alte zu pflegende Menschen vs. gesundheitsbezogener Selbstbestimmung, z. B. Widersprüche zwischen Pflege-/Therapieempfehlungen und biografisch/sozialisatorisch bedingten Gewohnheiten und Bewältigungsstrategien.
Sie reflektieren ebenso (eigene) widerstreitende gesundheitsbezogene Bedürfnisse, z. B. unmittelbare Bedürfnisbefriedigung vs. langfristige Bedarfe wie Gesundheit und Wohlbefinden oder Lebensqualität vs. Lebensdauer. Sie tarieren ihr gesundheitsbezogenes Handeln im Spannungsverhältnis zwischen ihrem Ich-Ideal und ihrem Real-Ich aus. Sie decken zentrale gesellschaftliche Paradoxien und die damit verbundenen Konflikte auf der Handlungsebene im Kontext von Gewaltphänomenen auf und positionieren sich dazu.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Rollenspiele zur Entwicklung von Fähigkeiten in der Gesundheitskommunikation: z. B. Informations- und Schulungsangebote, in denen aktuelle Bedürfnisse alter zu pflegender Menschen längerfristigen Bedarfen wie Wohlbefinden oder Lebensqualität oder Lebensdauer entgegenstehen, Gespräche zur gesundheitsbezogenen Entscheidungsfindung
- Rollenspiele zur gesundheitsbezogenen Information und Beratung von Verantwortlichen in Einrichtungen
- Übungen zur Information, Anleitung und Beratung von Teammitgliedern
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- gesundheitsförderliche und präventive Aspekte im altenpflegerischen Handeln identifizieren
- gesundheitsförderliche und präventive Aspekte in das altenpflegerische Handeln integrieren
- Information, Schulung und Beratung alter zu pflegender Menschen und ihrer Bezugspersonen zu gesundheitsbezogenen Aspekten, Reflexion der Legitimation und der Anknüpfung an die Lebenswelt der Angesprochenen
- Anleitung von Auszubildenden, Praktikant*innen sowie freiwillig Engagierten und Teammitgliedern planen, durchführen, reflektieren
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 05: Menschen in kurativen Prozessen pflegerisch unterstützen und Patientensicherheit stärken" %}
    Intentionen und Relevanz
Gezielte, die Kuration unterstützende pflegerische Interventionen haben durch die Verkürzung der Verweildauer und innovative Behandlungsverfahren in allen Versorgungsbereichen eine erhebliche Bedeutung und sind erfolgskritisch. Pflegende tragen dabei eine hohe Verantwortung im Hinblick auf die Gewährleistung der Patientensicherheit. Kurative therapeutische Interventionen sind für die zu pflegenden Menschen einerseits mit der Hoffnung oder Erwartung auf Linderung der Beschwerden oder Heilung, andererseits aber auch mit Ängsten und dem Risiko von unerwünschten Wirkungen verbunden. Neben umfassendem Fachwissen über medizinische Zusammenhänge, um beispielsweise Risiken erkennen und abwenden zu können, benötigen Pflegende auch beraterische und kommunikative Kompetenzen zur Unterstützung und Begleitung sowie zur Stärkung von Selbstmanagementfähigkeiten und der Gesundheitskompetenz von zu pflegenden Menschen und ihren Bezugspersonen.
Während der Fokus der curricularen Einheit in den ersten beiden Ausbildungsdritteln auf den wichtigsten Pflegediagnosen und Handlungsmustern im Bereich der Chirurgie und der Inneren Medizin liegt und auf der Systemebene vor allem die Rahmenbedingungen des akutstationären Versorgungsbereichs in den Blick genommen werden, richtet sich die curriculare Einheit im letzten Ausbildungsdrittel stärker auf die sektoren- und berufsgruppenübergreifende Organisation des Versorgungsprozesses, insbesondere bei komplexen gesundheitlichen Problemlagen. Die Zusammenarbeit, insbesondere mit der Berufsgruppe der Ärzt*innen, wird in beiden Ausbildungsabschnitten thematisiert, im zweiten Ausbildungsabschnitt werden auch innovative Konzepte zur Weiterentwicklung der Zusammenarbeit sowie der Qualität der Versorgung erarbeitet.

Bildungsziele
1./2. Ausbildungsdrittel
Die Auszubildenden machen sich eigene innere Konflikte wie auch mögliche innere Konflikte der zu pflegenden Menschen bewusst, die aus dem Bewusstsein des mit kurativen Interventionen verbundenen Risikos und daraus resultierender Angst entstehen. Sie reflektieren den Widerspruch zwischen dem unmittelbaren Erleben von leiblichen Phänomenen und dem oftmals objektivierenden Umgang damit im medizinischen Kontext. Des Weiteren erkennen sie, dass Effizienzoptimierungen etwa durch standardisierte Handlungsabläufe mit Verlusten bei Individualisierungs- bzw. Personalisierungsmöglichkeiten („Inhumanität der humanen Institution“) einhergehen. Sie reflektieren Routinen im Hinblick auf ihre wissenschaftliche Grundlage.
3. Ausbildungsdrittel
Insbesondere am Beispiel der Versorgung von Menschen mit komplexen gesundheitlichen Problemlagen lässt sich der Widerspruch von Unwissenheit/Entscheidungszwang und der Verpflichtung, die eigenen professionellen Handlungen gut, auch auf der Basis von vorhandenen wissenschaftlichen Evidenzen, begründen zu können, aneignen. In Bezug auf die Zusammenarbeit mit Ärzt*innen erarbeiten die Auszubildenden den Widerspruch, dass die Berufsgruppen gleichwertig und gleichberechtigt zusammenarbeiten sollen und dass sie gleichzeitig auch in Konkurrenz und in einem hierarchischen Verhältnis zueinander stehen. Die Auszubildenden finden Ansatzpunkte und
Chancen der Pflege, zur gesundheitlichen Chancengerechtigkeit beizutragen.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
1./2. Ausbildungsdrittel
- Durchführung eines Verbandwechsels bei vergleichsweise unkomplizierten Wunden (schrittweise Steigerung des Anforderungsniveaus)
- postoperative Mobilisation einer Patientin/eines Patienten nach z. B. Hüft-TEP-OP
- Simulation von Informationsgesprächen
- Durchführung von Schulungen zum Umgang mit ausgewählten gesundheitlichen Problemlagen
3. Ausbildungsdrittel
- Durchführung eines Verbandwechsels bei einer komplizierten Wunde
- Durchführung einer ethischen Falldiskussion
- kommunikative Unterstützung bei schwierigen Entscheidungssituationen (mit Simulationspatient*innen oder alternativ im Rollenspiel)
- kommunikative Unterstützung von Menschen in emotional stark belastenden Situationen (mit Simulationspatient*innen oder alternativ im Rollenspiel)
- Rollenspiel „interprofessionelle Fallbesprechung“
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- gesundheitsförderliche und präventive Aspekte im altenpflegerischen Handeln identifizieren
- gesundheitsförderliche und präventive Aspekte in das altenpflegerische Handeln integrieren
- Information, Schulung und Beratung alter zu pflegender Menschen und ihrer Bezugspersonen zu gesundheitsbezogenen Aspekten, Reflexion der Legitimation und der Anknüpfung an die Lebenswelt der Angesprochenen
- Anleitung von Auszubildenden, Praktikant*innen sowie freiwillig Engagierten und Teammitgliedern planen, durchführen, reflektieren
1./2. Ausbildungsdrittel
- sich auf einen Einsatz durch Recherche zu einem häufig vorkommenden chirurgischen Eingriff und/oder einer internistischen Erkrankung vorbereiten
- eine Patientin/einen Patienten für einen einfachen/komplizierten operativen Eingriff aufnehmen und prä- und postoperativ versorgen, Pflegeprozess dokumentieren
- eine Patientin/einen Patienten zu einer Operation begleiten, die Operation beobachten und die postoperative Versorgung durchführen
- zu pflegende Menschen durch den Krankenhausaufenthalt bei einem chirurgischen Eingriff und/oder einer internistischen Erkrankung begleiten und den Prozessverlauf dokumentieren
3. Ausbildungsdrittel
- die Therapie eines zu pflegenden Menschen bei einer ausgewählten Erkrankung anhand von ausgewählten Leitlinien reflektieren
- fallorientiertes Durchlaufen der Versorgungskette von einer Patientin/einem Patienten und Ermittlung von positiven und verbesserungswürdigen Abschnitten in der Kette
- Besuch einer Intensivstation
- Hospitation klinisches Ethikkomitee
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 05: Kinder und Jugendliche in kurativen Prozessen pflegerisch unterstützen und Patientensicherheit stärken" %}
    Intentionen und Relevanz
Der Schwerpunkt dieser curricularen Einheit liegt auf der pflegerischen Versorgung von Kindern und Jugendlichen mit komplexen gesundheitlichen Problemlagen und der dabei notwendigen sektoren- und berufsgruppenübergreifenden Organisation des Versorgungsprozesses sowie der Unterstützung bei Übergängen in den Lebensphasen. Das Betroffensein von Krankheit erfordert erhebliche biografische Anpassungsleistungen vonseiten der Kinder und Jugendlichen sowie deren Bezugspersonen. Die Unterstützung der Betroffenen sollte dabei so gestaltet werden, dass Selbstständigkeit und Selbstbestimmung der betroffenen Kinder und Jugendlichen altersentsprechend gewahrt und gefördert werden. Da die Eltern oftmals die Pflege übernehmen und Lebensgewohnheiten und der sozioökonomische Status der Familien den Umgang mit gesundheitsbedingten Selbstpflegeerfordernissen erheblich beeinflussen, muss das familiäre Umfeld in die Pflege einbezogen werden. Neben umfassendem Fachwissen über medizinische Zusammenhänge, um beispielsweise Risiken erkennen und abwenden zu können, benötigen Pflegende auch beraterische und kommunikative Kompetenzen zur Unterstützung und Begleitung sowie zur Stärkung von Selbstmanagementfähigkeiten und der Gesundheitskompetenz von Kindern und Jugendlichen und ihren Bezugspersonen.
Hinsichtlich der Kontextbedingungen der kurativen Versorgung von Kindern und Jugendlichen sollen innovative Konzepte zur Weiterentwicklung der Zusammenarbeit insbesondere mit Ärzt*innen, beispielsweise durch die Übernahme von heilkundlichen Aufgaben, und der Qualität der Versorgung thematisiert werden.

Bildungsziele
Am Beispiel der Versorgung von Kindern und Jugendlichen mit komplexen gesundheitlichen Problemlagen lässt sich der Widerspruch von Unwissenheit/Entscheidungszwang und der Verpflichtung, die eigenen professionellen Handlungen gut, auch auf der Basis von vorhandenen wissenschaftlichen Evidenzen begründen zu können, aneignen. In der Unterstützung der Eltern oder anderer Bezugspersonen loten die Auszubildenden den möglichen Konflikt zwischen der elterlichen Verantwortung für ihre Kinder und dem Wohl der Kinder aus. In Bezug auf die Zusammenarbeit mit Ärzt*innen erarbeiten die Auszubildenden den Widerspruch, dass die Berufsgruppen gleichwertig und gleichberechtigt zusammenarbeiten sollen und dass sie gleichzeitig auch in Konkurrenz und in einem hierarchischen Verhältnis zueinander stehen. Die Auszubildenden finden Ansatzpunkte und Chancen der Pflege, zur gesundheitlichen Chancengerechtigkeit beizutragen.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Durchführung eines Verbandwechsels bei einer komplizierten Wunde
- Durchführung einer ethischen Falldiskussion
- kommunikative Unterstützung bei schwierigen Entscheidungssituationen (mit Simulationspatient*innen oder alternativ im Rollenspiel)
- kommunikative Unterstützung von Kindern und Jugendlichen und ihren Bezugspersonen in emotional stark belastenden Situationen (mit Simulationspatient*innen oder alternativ im Rollenspiel)
- Rollenspiel „interprofessionelle Fallbesprechung“
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Reflexion der Therapie eines Kindes/einer bzw. eines Jugendlichen bei einer ausgewählten Erkrankung anhand von ausgewählten Leitlinien
- Durchlaufen der Versorgungskette eines kranken Kindes/einer bzw. eines kranken Jugendlichen und Ermittlung von positiven und verbesserungswürdigen Abschnitten in der Kette
- Besuch einer pädiatrischen Intensivstation
- Hospitation klinisches Ethikkomitee
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 05: Alte Menschen in kurativen Prozessen pflegerisch unterstützen und Patientensicherheit stärken" %}
    Intentionen und Relevanz
Aufgrund des epidemiologischen und demografischen Wandels befinden sich in den Versorgungsbereichen der ambulanten und stationären Langzeitpflege zunehmend Menschen, die unter komplexen gesundheitlichen Problemlagen leiden. Wegen der fehlenden Anwesenheit von Ärzt*innen obliegt es den Altenpflegerinnen und Altenpflegern, Verschlechterungen rechtzeitig zu erkennen, entsprechende Informationen an die betreuenden Hausärzt*innen weiterzugeben, dadurch eine Anpassung der medizinischen Versorgung zu erreichen, das gesundheitliche Wohlbefinden der zu pflegenden alten Menschen zu verbessern und unnötige Krankenhauseinweisungen zu verhindern. Neben umfassendem Fachwissen über medizinische Zusammenhänge, um beispielsweise Risiken erkennen und abwenden zu können, benötigen Pflegende auch beraterische und kommunikative Kompetenzen zur Unterstützung und Begleitung sowie zur Stärkung von Selbstmanagementfähigkeiten und der Gesundheitskompetenz von alten Menschen und ihren Bezugspersonen.
Außerdem sollen in dieser curricularen Einheit Kompetenzen zur Zusammenarbeit zwischen Ärzt*innen im Kontext der ambulanten und stationären Langzeitpflege aufgebaut und Ansätze zur Weiterentwicklung der Zusammenarbeit etwa durch die Übernahme von heilkundlichen Aufgaben thematisiert werden.

Bildungsziele
Am Beispiel der Versorgung von alten Menschen mit komplexen gesundheitlichen Problemlagen lässt sich der Widerspruch von Unwissenheit/Entscheidungszwang und der Verpflichtung, die eigenen professionellen Handlungen gut begründen zu können, aneignen. In Bezug auf die Zusammenarbeit mit Ärzt*innen erarbeiten die Auszubildenden den Widerspruch, dass die Berufsgruppen gleichwertig und gleichberechtigt zusammenarbeiten sollen und dass sie gleichzeitig auch in Konkurrenz und in einem hierarchischen Verhältnis zueinander stehen. Die Auszubildenden finden Ansatzpunkte und Chancen der Pflege, zur gesundheitlichen Chancengerechtigkeit beizutragen.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Durchführung eines Verbandwechsels bei einer komplizierten Wunde
- Durchführung einer ethischen Falldiskussion
- kommunikative Unterstützung bei schwierigen Entscheidungssituationen (mit Simulationspatient*innen oder alternativ im Rollenspiel)
- kommunikative Unterstützung von alten Menschen und ihren Bezugspersonen in emotional stark belastenden Situationen (mit Simulationspatient*innen oder alternativ im Rollenspiel)
- Rollenspiel interprofessionelle Fallbesprechung
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Reflexion der Therapie eines zu pflegenden alten Menschen bei einer ausgewählten Erkrankung anhand von erworbenem Wissen
- Durchlaufen der Versorgungskette eines alten zu pflegenden Menschen und Ermittlung von positiven und verbesserungswürdigen Abschnitten in der Kette
- Besuch einer Intensivstation
- Hospitation klinisches Ethikkomitee
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 06: In Akutsituationen sicher handeln" %}
    Intentionen und Relevanz
Intentionen und Relevanz
Beruflich Pflegende werden häufig in allen beruflichen Settings, aber auch im Alltag, entweder aufgrund ihrer hohen Präsenz und Erreichbarkeit in den verschiedenen Einrichtungen oder wegen ihrer besonderen gesellschaftlichen Verantwortung, mit Akutsituationen konfrontiert, in denen augenblickliche Hilfeleistungen notwendig sind. Dies erfordert eine rasche und zuverlässige Situationseinschätzung ebenso wie zügige Entscheidungen über unmittelbar einzuleitende Sofortmaßnahmen. In dieser curricularen Einheit werden solche Hilfesituationen in den Blick genommen,
a) in denen zu pflegende Menschen aufgrund physischer Ereignisse akut vital gefährdet sind oder andere gefährden,
b) in denen zu pflegende Menschen und/oder andere Personen in Einrichtungen akuten Gefährdungen und/oder Bedrohungen aus der Umwelt ausgesetzt sind,
c) in denen beruflich Pflegende außerhalb von Institutionen und außerhalb ihres beruflichen Handlungsfeldes aufgrund ihrer besonderen rechtlichen Verantwortung in Not- und Katastrophenfällen zur Hilfeleistung verpflichtet sind bzw. hierzu herangezogen werden können.
In bedrohlichen Situationen sind beruflich Pflegende auch herausgefordert, die eigene Fassung und Handlungsfähigkeit zu bewahren. Dazu sowie zur eigenen Gesunderhaltung gehört eine Verarbeitung belastender Ereignisse im Nachhinein. Ebenso benötigen die hilfebedürftigen Menschen und ihre Bezugspersonen in Akutsituationen eine emotionale Unterstützung und Stabilisierung. Diese beinhaltet neben einer ruhigen und sicheren Arbeitsweise, dass beruflich Pflegende den betroffenen Menschen eine Deutung ihres Zustandes anbieten und anstehende Eingriffe und Maßnahmen erklären.
Die zentralen Kompetenzen, die zur Bewältigung akuter Hilfesituationen erforderlich sind, sind im Interesse der Sicherheit der zu pflegenden Menschen bereits in den ersten beiden Ausbildungsdritteln Gegenstand. Sie sollen im letzten Ausbildungsdrittel zur Erhöhung der Handlungs- und Patientensicherheit erneut aufgegriffen und ggf. um komplexere Notfallsituationen ergänzt werden.
Angesichts zunehmender gesellschaftlicher Gefährdungen und Bedrohungen durch Massenunglücke, Attentate oder Amokläufe sollten ebenfalls ausgewählte/aktuelle Ereignisse angesprochen, diskutiert und reflektiert werden.

Bildungsziele
1./2. Ausbildungsdrittel
Die Auszubildenden machen sich bewusst, dass Notfallsituationen und Interventionen mit Folgen für das Leben von Betroffenen verbunden sein können, die dem (mutmaßlichen) oder in Patientenverfügungen verankerten Willen widersprechen können. Sie reflektieren die Bedeutung von Unsicherheit und Risiko für das persönliche und gemeinschaftliche Leben unter den Bedingungen des globalen gesellschaftlichen Wandels.
3. Ausbildungsdrittel
Die Auszubildenden setzen sich mit der gesellschaftlichen, ethischen und rechtlichen Debatte zur Organspende auseinander und finden zwischen Selbstbestimmung und Gemeinwohlinteressen bzw. Solidarität hierzu eine eigene Haltung.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
1./2. Ausbildungsdrittel
- Simulation von Notfallsituationen (ggf. im Skills Lab)
- Notfalltrainings an Notfallsimulatoren
- E-Learning-Angebote: Verhalten im Brandfall und Einrichtungs-Evakuierung
3. Ausbildungsdrittel
- Wiederholung: Notfalltraining in ausgewählten Notfallsituationen
- Wiederholung: Basic Life Support (nach ERC-/GRC-Leitlinien)
- Advanced Life Support
- Simulation realitätsnaher Notfallsituationen mit anderen Personengruppen, z. B. einer Schulklasse, eines anderen Ausbildungsabschnittes, mit Laiinnen und Laien
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
1./2. Ausbildungsdrittel
- Erkundungsaufgabe (doppelter Transfer): trägereigene Notfallpläne sowie Beauftragte und Verantwortliche im Notfallmanagement erkunden und vorstellen
- Besuch einer Rettungsleitstelle/einer Notfallambulanz/einer Erste-Hilfe-Stelle im Krankenhaus
3. Ausbildungsdrittel (erweiternd)
- Identifikation von besonders gefährdeten Räumen und Bereichen in der eigenen Einrichtung im Rahmen des Brandschutzes
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 06: Kinder, Jugendliche und ihre Bezugspersonen in Akutsituationen sicher begleiten" %}
    Intentionen und Relevanz
Der Schwerpunkt dieser curricularen Einheit liegt auf häufigen und typischen Akutsituationen und Notfällen im Kindes- und Jugendalter, die aufbauend auf der korrespondierenden curricularen Einheit für die ersten beiden generalistisch ausgerichteten Ausbildungsdrittel, aufgegriffen werden. Beruflich Pflegende sind ebenso wie Bezugspersonen und unverletzt-betroffene Kinder, die Zeugen eines Notfalls werden, von solchen Situationen emotional in besonderer Weise mitgenommen.
Die zentralen Kompetenzen, die zur Bewältigung akuter Hilfesituationen erforderlich sind, werden im Interesse der Sicherheit von Kindern, Jugendlichen und ihren Bezugspersonen im 3. Ausbildungsdrittel und zur Erhöhung der Handlungssicherheit unter dem spezifischen Fokus der Lebensphase erneut aufgegriffen, spezifiziert und ggf. um komplexere Notfallsituationen ergänzt.
Angesichts zunehmender gesellschaftlicher Gefährdungen und Bedrohungen durch Massenunglücke, Attentate oder Amokläufe sollten ebenfalls ausgewählte/aktuelle Ereignisse angesprochen, diskutiert und reflektiert werden.

Bildungsziele
Die Auszubildenden setzen sich mit der gesellschaftlichen, ethischen und rechtlichen Debatte zur Organspende auseinander und finden zwischen Selbstbestimmung und Gemeinwohlinteressen bzw. Solidarität hierzu eine eigene Haltung.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Wiederholung: Notfalltraining in ausgewählten Notfallsituationen an Notfallsimulatoren
- Wiederholung: Pediatric Life Support (nach ERC-/GRC-Leitlinien)
- Pediatric Advanced Life Support
- Simulation realitätsnaher Notfallsituationen mit anderen Personengruppen, z. B. einer Schulklasse, Auszubildenden eines anderen Ausbildungsabschnittes, mit Laiinnen und Laien
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Identifikation von besonderen Gefährdungen für Kinder und Jugendliche in verschiedenen institutionellen Kontexten, z. B. Aufbewahrung von Reinigungsmitteln, Arzneimitteln, Gefährdungen für Elektrounfälle
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 06: Alte Menschen und ihre Bezugspersonen in Akutsituationen sicher begleiten" %}
    Intentionen und Relevanz
Der Schwerpunkt dieser curricularen Einheit liegt auf häufigen und typischen Akutsituationen und Notfällen im höheren Lebensalter, die aufbauend auf der korrespondierenden curricularen Einheit für die ersten beiden generalistisch ausgerichteten Ausbildungsdrittel, aufgegriffen werden. Notfälle treten bei alten Menschen selten plötzlich auf, sondern zeigen sich meist als akute Verschlechterungen oder Komplikationen bei bereits bestehenden Erkrankungen. Selten liegen einzelne Auslöser zugrunde, sondern mehrere Risikofaktoren und Funktionsstörungen. Das rechtzeitige Erkennen von Notfallsituationen im höheren Lebensalter wird zudem durch Mehrfacherkrankungen und Polypharmakotherapie erschwert. Die Symptome sind oft verschleiert und unspezifisch, und typische Symptome können fehlen.
Die zentralen Kompetenzen, die zur Bewältigung akuter Hilfesituationen erforderlich sind, werden im Interesse der Sicherheit von älteren Menschen und ihren Bezugspersonen im 3. Ausbildungsdrittel und zur Erhöhung der Handlungssicherheit der Altenpflegerinnen und Altenpfleger unter dem spezifischen Fokus der Lebensphase erneut aufgegriffen und spezifiziert. Die Komplexität der Notfallsituationen im höheren Lebensalter wird schon allein deshalb erhöht, weil im familialen Kontext sowie in der Langzeitpflege der schnelle Rückgriff auf ein Notfallteam nicht gegeben ist und die Altenpfleger*innen in der Lage sein müssen, eine sichere Ersteinschätzung vorzunehmen und auf dieser Grundlage eine folgerichtige Entscheidung zu treffen.
Angesichts zunehmender gesellschaftlicher Gefährdungen und Bedrohungen durch Massenunglücke, Attentate oder Amokläufe sollten ebenfalls ausgewählte/aktuelle Ereignisse angesprochen, diskutiert und reflektiert werden.

Bildungsziele
Die Auszubildenden setzen sich mit der gesellschaftlichen, ethischen und rechtlichen Debatte zur Organspende auseinander und finden zwischen Selbstbestimmung und Gemeinwohlinteressen bzw. Solidarität hierzu eine eigene Haltung.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Wiederholung: Notfalltraining in ausgewählten Notfallsituationen an Notfallsimulatoren
- Wiederholung: Basic Life Support (nach ERC-/GRC-Leitlinien)
- Advanced Life Support
- Simulation realitätsnaher Notfallsituationen mit anderen Personengruppen, z. B. einer Schulklasse, eines anderen Ausbildungsabschnittes, mit Laiinnen und Laien
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Identifikation von besonders gefährdeten Räumen und Bereichen in der eigenen Einrichtung im Rahmen des Brandschutzes
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 07: Rehabilitatives Pflegehandeln im interprofessionellen Team" %}
    Intentionen und Relevanz
Rehabilitative Pflege ist ein zentraler Leitgedanke in verschiedenen Handlungsfeldern der Pflege. Sie ist auf die Unterstützung und Begleitung bei der selbstständigen Lebensführung und Alltagsbewältigung sowie die Förderung der sozialen Teilhabe gerichtet. Insbesondere ist sie von Bedeutung bei Menschen aller Altersstufen, die von chronischen Erkrankungen, (drohenden) Behinderungen oder den Folgen von Unfällen betroffen sind. Die Pflege bezieht auch die (pflegenden) Bezugspersonen in den Rehabilitationsprozess ein. Der Rehabilitationsprozess erfordert außerdem die Zusammenarbeit in einem interprofessionellen Team.
Den Pflegefachfrauen und -männern kommt im interdisziplinär ausgerichteten Rehabilitationsprozess eine spezifische Rolle zu, denn sie unterstützen die zu pflegenden Menschen und ihre Bezugspersonen während des gesamten Prozesses bei der Bewältigung krankheits- oder behinderungsbedingter Beeinträchtigungen und der Wiedererlangung und Aufrechterhaltung der Lebensqualität. Sie fördern durch Information, Schulung und Beratung die Übernahme des therapeutisch Erlernten in den Alltag durch die Betroffenen und ihre Bezugspersonen und nehmen als Bindeglied zwischen den verschiedenen interdisziplinär ausgerichteten Therapiebereichen eine zentrale Rolle ein. Als weitere Aufgabe wirken sie unterstützend bei diagnostischen und therapeutischen Maßnahmen, schaffen Voraussetzungen für therapeutische Übungen und Trainings zur Wiedererlangung von Alltagskompetenzen und schützen zu pflegende Menschen vor Überforderung. Dabei stehen die Stärkung des Selbstbewusstseins der zu pflegenden Menschen, die Förderung der Teilhabe und die Ausrichtung auf ein möglichst autonomes Leben in der Gesellschaft im Vordergrund. Trotz dieser vielfältigen Aufgaben fehlt bislang ein eigenständiger pflegerischer Interventionsansatz mit ausgewiesenem rehabilitativen Charakter, in dem auch die Rolle der beruflich Pflegenden im interprofessionellen Team deutlich wird. So wird in dieser curricularen Einheit u. a. die Erschließung rehabilitativer Interventionen und Verantwortungsbereiche fokussiert, um die Rolle der beruflich Pflegenden im rehabilitativen Prozess und interprofessionellen Team zu stärken und weiterzuentwickeln.
Die Auszubildenden werden angeregt, die eigene Rolle und die spezifischen Aufgaben und Verantwortungsbereiche der Pflege im Rehabilitationsprozess zu erkennen, zu reflektieren und zu bewerten. Darüber werden Kompetenzen zum interprofessionellen Denken und Handeln sukzessive angebahnt, um gemeinsam im interprofessionellen Team mit dem zu pflegenden Menschen und seinen Bezugspersonen einen Behandlungs- und Rehabilitationsplan zu erstellen und zu evaluieren, in dem die Förderung der Selbst- und Fremdpflege sowie die Entwicklung neuer Lebensperspektiven und der Erhalt der Teilhabe am Leben in der Gesellschaft fokussiert werden. Die Analyse und Reflexion rehabilitativer Versorgungsstrukturen und -angebote mit den unterschiedlichen gesetzlichen Normen sind weitere Schwerpunkte, die insbesondere für eine pflegerische Beratung von Bedeutung sind.
Die curriculare Einheit wird in folgende zwei Schwerpunkte unterteilt:
- 1. und 2. Ausbildungsdrittel: Hier erwerben die Auszubildenden Kompetenzen, um rehabilitative Aufgaben zu erkennen und in wenig komplexen Pflegesituationen zu übernehmen und sich sukzessive den Stellenwert der Pflege in der Rehabilitation und einem interprofessionellen Team zu erschließen.
- 3. Ausbildungsdrittel: Hier werden die Auszubildenden befähigt, im interdisziplinären Team die pflegerische Perspektive einzubringen und gemeinsam mit den am Rehabilitationsprozess beteiligten Berufsgruppen Rehabilitationsziele und -pläne zu erarbeiten und diese zu evaluieren. Dabei wird beispielhaft spezifisches rehabilitatives Pflegehandeln bei Kindern, Jugendlichen, Erwachsenen und Menschen im höheren Lebensalter in den Blick genommen. Ein weiterer Schwerpunkt besteht in der Information, Beratung und Schulung von zu pflegenden Menschen und ihren Bezugspersonen zu rehabilitativen Angeboten und Unterstützungsleistungen sowie Finanzierungsmöglichkeiten.

Bildungsziele
Die Auszubildenden können selbstbewusst den pflegerischen Beitrag zur Wiederherstellung von Gesundheit oder zur Erlangung von Lebensqualität, Autonomie und Selbstständigkeit im interprofessionellen Team ausweisen und positionieren sich dazu. Sie reflektieren widersprüchliche Anforderungen, die sich aus dem Wunsch der zu pflegenden Menschen nach Normalität und ein Leben mit bedingter Gesundheit ergeben und nehmen zu dem gesellschaftlichen Phänomen der Stigmatisierung von Menschen mit Behinderung Stellung.
Für die rehabilitative Pflege, die in verschiedenen Handlungskontexten eingebettet ist, reflektieren sie erschwerende institutionelle und gesellschaftliche Rahmenbedingungen für ein Leben in bedingter Gesundheit und nehmen zu sozialrechtlichen Normen im Hinblick auf ethische und wirtschaftliche Maßstäbe Stellung. Sie reflektieren pflegeberufspolitische Interessenvertretungen im Kontext divergierender Interessen in der Gesundheitspolitik.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
1./2. Ausbildungsdrittel
- Erkundung bzw. Exkursion hinsichtlich situativ geeigneter technischer und digitaler Assistenzsysteme (z. B. Exoskelett, Sprachcomputer)
- Rollenspiel zu konkreten Schulungssituationen in der rehabilitativen Pflege (z. B. Gehhilfen bei Hemiplegie, Rollstuhlfahren-Lernen einer/eines querschnittgelähmten Jugendlichen)
- Rollenspiel zu einer ausgewählten interprofessionellen Fallbesprechung mit anschließender Reflexion
3. Ausbildungsdrittel
- Rollenspiele zu spezifischen Beratungsgesprächen in der rehabilitativen Pflege eines Menschen nach einem Apoplex
- Rollenspiel zur Beratung von Eltern/Bezugspersonen zu rehabilitativen Unterstützungsleistungen ihres Schulkindes mit körperlichen und geistigen Einschränkungen nach einem Unfall
- Rollenspiel und Videografie zu einer konflikthaften interprofessionellen Fallbesprechung
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
1./2. Ausbildungsdrittel
- Erkundungsaufgabe zu pflegerischen Interventionen mit rehabilitativem Charakter (hier können spezifische pflegerische Interventionen bei Kindern, Jugendlichen, Erwachsenen und Menschen im höheren Lebensalter in den Blick genommen werden)
- Beobachtungs- und Reflexionsaufgabe einer interprofessionellen Fallbesprechung, in der Pflegefachfrauen/-männer die pflegerische Perspektive im interprofessionellen Team einbringen und verhandeln (ambulant und stationär möglich). Fragen dazu: Wer ist beteiligt? Von wem wird die Besprechung moderiert? Welche Perspektiven werden eingebracht? Mit welchem Modell bzw. Instrument wird gearbeitet? Was sind die Prioritäten des Teams? Wie können welche Berufsgruppen zur Umsetzung des Rehabilitationsziels beitragen? Wie werden Verantwortlichkeiten festgelegt?
- Beobachtungs- und Reflexionsaufgabe einer Schulung im Umgang mit ausgewählten technischen und digitalen Assistenzsystemen (ggf. auch Analyse eines videografierten Beispiels unter Einhaltung des Datenschutzes). Fragen dazu: Welche Schritte der Schulung sind erkennbar, und wie werden die biografisch erworbenen Gewohnheiten und Bewältigungsstrategien des zu pflegenden Menschen in den Schulungsprozess integriert? Welches Wissen wird für den Schulungsprozess benötigt? Welche Rolle spielt das leibliche Wissen?
3. Ausbildungsdrittel
- Durchführung und Reflexion eines Pflegeplanungsgesprächs mit zu pflegenden Menschen und ihren Bezugspersonen zur Stärkung ihrer Alltagskompetenz und gesellschaftlichen Teilhabe
- schriftliche Reflexion einer ausgewählten Koordinierung von Handlungsabläufen eines Überleitungs- und Case Managements im Hinblick auf die Verständigung der beteiligten Berufsgruppen und die Integration der zu pflegenden Menschen und ihrer Bezugspersonen
- fallspezifische Analyse eines interprofessionellen Konflikts und der Darstellung von gemeinsamen Entscheidungsfindungen im Umgang mit Konflikten
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 07: Rehabilitatives Pflegehandeln bei Kindern und Jugendlichen im interprofessionellen Team" %}
    Intentionen und Relevanz
Diese curriculare Einheit schließt an die korrespondierende curriculare Einheit aus der generalistischen Ausbildungsphase der ersten beiden Ausbildungsdrittel an. Die Lernsituationen in dieser Einheit sind durch eine höhere Komplexität gekennzeichnet. Diese ist in der rehabilitativen Pflege bei Kindern und Jugendlichen durch das Eingebunden-Sein in familiale Systeme und eine Vielzahl an Akteuren im sozialen Raum gekennzeichnet und erfordert eine interprofessionelle Zusammenarbeit, in der die verschiedenen berufsspezifischen Aktivitäten ineinandergreifen. Die Gesundheits- und Kinderkrankenpfleger*innen nehmen in diesem Prozess die Rolle der Vermittler*innen ein, indem sie für Kontinuität sorgen und zwischen den beteiligten Berufsgruppen als Fürsprecher*innen für die zu pflegenden Kinder und Jugendlichen sowie ihre Bezugspersonen tätig werden. Dabei sind wesentliche Voraussetzungen von Bedeutung: Zum einen eine Ausrichtung auf die pflegefachliche Perspektive und die Berücksichtigung der fachlichen Expertise anderer beteiligten Berufsgruppen und zum anderen ein Sich-Einlassen auf Aushandlungsprozesse, in denen die verschiedenen interprofessionellen Sichtweisen in Bezug auf die Bedarfe der Kinder und Jugendlichen und ihrer Bezugspersonen verhandelt werden. Darüber ergibt sich ein Spannungsfeld von Abgrenzung und Kooperation, das eine besondere Herausforderung in der rehabilitativen Pflege darstellt. Dem Case Management und den gemeinsamen Entscheidungsprozessen sowie der Beratung und Schulung kommt eine zentrale Rolle zu.
Der Schwerpunkt im 3. Ausbildungsdrittel liegt für die Auszubildenden, die sich für einen Abschluss als Gesundheits- und Kinderkrankenpflegerin/Gesundheits- und Kinderkrankenpfleger entschieden haben, in der Zusammenarbeit zwischen den beteiligten Berufsgruppen, den familialen Systemen sowie den sozialen Netzwerken, in denen sie eine Vermittlerrolle einnehmen, um so für die zu pflegenden Menschen einen kontinuierlichen Versorgungsprozess realisieren zu können.
Die Kompetenzen zum rehabilitativem Handeln sollen in dieser Einheit beispielhaft an den Folgen einer chronischen Erkrankung wie kindliches Rheuma, an den Folgen eines schweren Schädel-Hirn-Traumas sowie an ausgewählten angeborenen und erworbenen Behinderungen angebahnt werden.

Bildungsziele
Die Auszubildenden können selbstbewusst den pflegerischen Beitrag im interprofessionellen Team ausweisen und positionieren sich dazu. Für die rehabilitative Pflege, die in verschiedene Handlungskontexte eingebettet ist, reflektieren sie erschwerende institutionelle und gesellschaftliche Rahmenbedingungen für ein Leben in bedingter Gesundheit und setzen sich mit den unterschiedlichen Normen und Werten im Hinblick auf die Förderung gesellschaftlicher Teilhabe und rehabilitative Versorgungsleistungen auseinander.
Sie reflektieren widersprüchliche Anforderungen, die sie in der Interaktion mit den zu pflegenden Kindern und Jugendlichen und ihren Eltern/Bezugspersonen sowie im Rehabilitationsteam erleben.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Übungen mit Elementen der Selbsterfahrung zu pflegerischen Förderkonzepten
- Rollenspiel zu Schulung und Beratung von Kindern/Jugendlichen und Eltern in der rehabilitativen Pflege
- Rollenspiel und Videografie zu einer konflikthaften interprofessionellen Fallbesprechung, in der die Auszubildenden die Vermittlerrolle zwischen Kindern bzw. Jugendlichen und Eltern einnehmen
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Erkundungsaufgabe zu ausgewählten aktuellen spezifischen technischen und digitalen Assistenzsystemen in stationären bzw. teilstationären Einrichtungen unter Berücksichtigung der individuellen Entwicklung des Kindes bzw. der/des Jugendlichen
- Beobachtungsaufgabe: Welche Merkmale kennzeichnen ein professionelles Beratungsgespräch mit einem älteren Kind oder einer/einem Jugendlichen, in dem es um Unterstützungsleistungen zur sozialen Integration unter Einbeziehung der individuellen Lebenswelt geht?
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 07: Rehabilitatives Pflegehandeln bei alten Menschen im interprofessionellen Team" %}
    Intentionen und Relevanz
Diese curriculare Einheit schließt an die korrespondierende curriculare Einheit aus der generalistischen Ausbildungsphase der ersten beiden Ausbildungsdrittel an. Die Lernsituationen weisen in dieser Einheit eine höhere Komplexität auf. Diese ist in der rehabilitativen Pflege bei alten Menschen durch Multimorbidität und vielfältige gesundheitliche Problemlagen gekennzeichnet, die zu einer Gefährdung bzw. Einschränkung der Bewältigung des Alltags und der gesellschaftlichen Teilhabe führen. Die Altenpfleger*innen nehmen im Rehabilitationsprozess die Rolle der Vermittler*innen ein, indem sie für Kontinuität sorgen und zwischen den beteiligten Berufsgruppen als Fürsprecher*innen für den zu pflegenden alten Menschen tätig werden. Dabei sind wesentliche Voraussetzungen von Bedeutung: Zum einen eine Ausrichtung auf die pflegefachliche Perspektive und die Berücksichtigung der fachlichen Expertise anderer beteiligter Berufsgruppen und zum anderen ein Sich-Einlassen auf Aushandlungsprozesse, in denen die verschiedenen interprofessionellen Sichtweisen in Bezug auf die Bedarfe des zu pflegenden alten Menschen und seiner Bezugspersonen verhandelt werden. Darüber ergibt sich ein Spannungsfeld von Abgrenzung und Kooperation, das eine besondere Herausforderung in der rehabilitativen Pflege darstellt. Dem Cas

e Management sowie der Beratung von zu pflegenden alten Menschen und ihren Bezugspersonen sowie von freiwillig Engagierten kommt ebenfalls eine zentrale Rolle zu.
Der Schwerpunkt im 3. Ausbildungsdrittel liegt für die Auszubildenden, die sich für einen Abschluss als Altenpflegerin oder Altenpfleger entschieden haben, in der Zusammenarbeit zwischen den beteiligten Berufsgruppen und mit den familialen Systemen sowie den sozialen Netzwerken, in denen sie eine Vermittlerrolle einnehmen, um so für die zu pflegenden Menschen einen kontinuierlichen Versorgungsprozess realisieren zu können und zur gesellschaftlichen Teilhabe beizutragen. Rehabilitative Pflege kann dazu beitragen, Pflegebedürftigkeit zu verzögern und Alltagskompetenzen möglichst lange aufrechtzuerhalten.

Bildungsziele
Die Auszubildenden können selbstbewusst den pflegerischen Beitrag im interprofessionellen Team ausweisen und positionieren sich dazu. Für die rehabilitative Pflege, die in verschiedene Handlungskontexte eingebettet ist, reflektieren sie erschwerende institutionelle und gesellschaftliche Rahmenbedingungen für ein Leben in bedingter Gesundheit und setzen sich mit den unterschiedlichen Normen und Werten im Hinblick auf Alter und rehabilitative Versorgungsleistungen und -systeme auseinander.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Rollenspiel zu Schulung und Beratung in der rehabilitativen Pflege bei zu pflegenden alten Menschen und ihren Bezugspersonen
- Rollenspiel und Videografie einer konflikthaften interprofessionellen Fallbesprechung

Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Reflexionsaufgabe eines Pflegeplanungsgesprächs mit einem zu pflegenden alten Menschen und seinen Bezugspersonen zur Stärkung der Alltagskompetenz und gesellschaftlichen Teilhabe in Bezug auf die Einbeziehung der Biografie und der momentanen Lebenssituation des zu pflegenden alten Menschen und seiner Bezugspersonen
- Beobachtungsaufgabe: Wie koordinieren Altenpfleger*innen Handlungsabläufe eines Überleitungs- und Case Managements (z. B. im Hinblick auf die Überleitung aus dem häuslichen Umfeld in ein Altenheim und an das sich anschließende Case Management)
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 08: Menschen in kritischen Lebenssituationen und in der letzten Lebensphase begleiten" %}
    Intentionen und Relevanz
Die Begleitung und Unterstützung von Menschen in kritischen Lebenssituationen – zum Beispiel angesichts chronischer, onkologischer oder anderer lebenslimitierender Erkrankungen – sowie von sterbenskranken und sterbenden Menschen ist ein zentrales Thema in verschiedenen Handlungsfeldern der Pflege. Mit Blick auf palliative Pflege als von der WHO definierten Versorgungsansatz sollen die Auszubildenden lernen, daran mitzuwirken, die Lebensqualität von zu pflegenden Menschen, ihren Bezugspersonen und Familien zu verbessern, die mit Problemen und Herausforderungen konfrontiert sind, welche mit einer lebenslimitierenden Erkrankung einhergehen. Im Mittelpunkt stehen das Vorbeugen und Lindern von Leiden unter Einbezug aller Dimensionen des Menschseins.
Die Auszubildenden setzen sich in dieser curricularen Einheit tiefgreifend mit Phänomenen auseinander, die sich in der Begegnung mit existenziell herausgeforderten Menschen und ihren Bezugspersonen zeigen. Dies stellt hohe persönliche Anforderungen an die Auszubildenden, die ebenso thematisiert werden sollen.
In dieser curricularen Einheit werden im 1./2. Ausbildungsdrittel die Begleitung und Unterstützung von zu pflegenden Menschen aller Altersgruppen, ihren Bezugspersonen und Familien in kritischen Lebenssituationen angesichts chronischer, onkologischer sowie lebenslimitierender Erkrankungen thematisiert. Ebenso findet eine erste Auseinandersetzung mit der Pflege sterbender Menschen statt.
Im 3. Ausbildungsdrittel wird erweiternd die umfassende und individuelle Pflege von Menschen in komplexen kritischen Lebenssituationen und in der letzten Lebensphase im Kontext ihrer familiären, sozialen, kulturellen, religiösen Bezüge und Lebenswelten sowie der institutionellen und gesellschaftlichen Bedingungen und Einflussfaktoren in den Mittelpunkt gerückt.

Bildungsziele
1./2. Ausbildungsdrittel
Die Auszubildenden reflektieren den Widerstreit zwischen Mitleiden und bewusster innerer und äußerer Abgrenzung und finden zu einer begründeten – ggf. situativ wechselnden – Haltung. Ebenso reflektieren sie Widersprüche, die sich aus dem Erleben von Leid und Schmerz und möglichen (Selbst- und Fremd-)Erwartungen an das Verhalten ergeben. Für palliative Handlungsfelder, in die die hier thematisierten Situationen eingebettet sind, reflektieren die Auszubildenden das Spannungsverhältnis zwischen systemischen Zwängen versus Personenzentrierung.
3. Ausbildungsdrittel
Die Lernenden reflektieren den gesellschaftlich-kollektiven, institutionellen und individuellen Umgang mit Tod und Sterben in unterschiedlichen Altersstufen und Lebensphasen im Spannungsfeld von Entfremdung und Leiderfahrung. Sie nehmen die Gesellschaft und die Institutionen als Rahmung für die persönliche Auseinandersetzung mit dem Sterben sowie für die Gestaltung des Pflegeprozesses wahr.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Rollenspiele zu konkreten Situationen, z. B. auf eine Diagnosemitteilung angemessen reagieren, Beileidsbekundungen aussprechen, Mitteilung einer Todesnachricht
- Pflegeinterventionen üben, z. B. spezielle Mundpflege
- Besuch eines Hospizes und/oder einer Palliativstation (ggf. Expertin/Experten einladen)

Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Menschen, die von einer chronischen Krankheit betroffen sind, interviewen, – mit besonderem Augenmerk auf die erste Konfrontation damit und auf Bearbeitungs-/Bewältigungsstrategien; Pflegebedarf feststellen und Pflegeprozess gestalten
- Pflegesituationen mit sterbenden Menschen beobachten: Wie gehen Pflegepersonen damit um? Wie wird im Team darüber gesprochen? Wie werden Aushandlungsprozesse gestaltet?
- Pflegesituationen mit sterbenden Menschen gestalten und Erfahrungen reflektieren
- Reflexion der Versorgungsrealität: Wie sieht die Versorgungsrealität aus? Wo kann gute Versorgung warum
stattfinden? Welche Defizite gibt es? (fehlendes Case Management, Koordinations- und Integrationsprobleme, Unter- und Fehlversorgung) Welche Ressourcen bleiben ungenutzt? (informelle Hilfen, freiwillig
Engagierte, Hospizhelfer*innen)
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 08: Kinder, Jugendliche und ihre Familien in kritischen Lebenssituationen und in der letzten Lebensphase begleiten" %}
    Intentionen und Relevanz
Im 3. Ausbildungsdrittel in der Gesundheits- und Kinderkrankenpflege steht die umfassende Pflege und Begleitung von Kindern und Jugendlichen und ihren Familien in komplexen und kritischen Lebenssituationen und in der letzten Lebensphase im Mittelpunkt. Die im 1./2. Ausbildungsdrittel erworbenen Kompetenzen sollen vertieft und auf unterschiedliche komplexe kritische Lebenssituationen, die Kinder und Jugendliche erleben, transferiert werden. Dabei entwickeln die Auszubildenden eine zunehmend spezifische und differenzierte Sichtweise auf die Pflege und Begleitung von Kindern, Jugendlichen und ihren Familien vor dem Hintergrund altersentsprechender Bedürfnisse und Entwicklungsaufgaben sowie kindlicher und familiärer Anpassungs- und Bewältigungsprozesse. Sie nehmen gegenüber den betroffenen Familien eine wertschätzende, ressourcenorientierte und allparteiliche Sichtweise ein, erkennen familiäre Ressourcen und Widerstandsfaktoren, integrieren soziale Hilfen und Unterstützungsnetzwerke und entwickeln gemeinsam mit den Familien Interventionen zur Erhaltung und Stärkung der Familiengesundheit. Insbesondere soll in dieser Einheit eine, auch auf wissenschaftlichen Forschungsergebnissen basierende Auseinandersetzung mit der Rolle der Geschwister bei schwerer Erkrankung eines Familienmitglieds sowie deren Begleitung und Unterstützung in den Blick genommen werden.
Pflegerische Konzepte der ambulanten und stationären Palliativversorgung von Kindern und Jugendlichen sowie die damit verbundenen Anforderungen auf unterschiedlichen systemischen Ebenen sollen in die Gestaltung der Pflegeprozesse einbezogen und von denen des Erwachsenenbereichs unterschieden werden. Ebenso reflektieren die Auszubildenden ihre berufliche Rolle innerhalb des Familiensystems, insbesondere in der ambulanten Langzeitpflege.

Bildungsziele
Die Lernenden setzen sich mit der Widersprüchlichkeit des Lebensendes am Lebensanfang auseinander und reflektieren die Gestaltung von Trauerprozessen am Anfang des Lebens auf individueller, familiärer und gesellschaftlicher Ebene.
Die Lernenden reflektieren den gesellschaftlich-kollektiven, institutionellen und individuellen Umgang mit Tod und Sterben im Kindes- und Jugendalter im Spannungsfeld von Entfremdung und Leiderfahrung. Sie nehmen die Gesellschaft und die Institutionen als Rahmung für die persönliche Auseinandersetzung mit dem Sterben sowie für die Gestaltung des Pflegeprozesses wahr.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Gesprächssituationen über Krankheit, Sterben und Tod mit Kindern unterschiedlicher Alters- und Entwicklungsphasen im Rollenspiel
- Gesprächssituationen mit Bezugspersonen über Ängste, Sterben und Tod
- Gesprächssituationen bzw. Interview mit Geschwisterkindern in unterschiedlichen Entwicklungsphasen
- Instruktion/Schulung zum Umgang mit technischen/digitalen Hilfsmitteln für die Pflege
- Führen eines Entlassungsgesprächs bei Therapiepausen
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Beobachtungsaufgabe: Wie fördern Gesundheits- und Kinderkrankenpfleger*innen die Adhärenz von Kindern und Jugendlichen? Welche Rolle spielen dabei die begleitenden Bezugspersonen?
- Beobachtungsaufgabe: Einschätzung von Haut- und Schleimhautveränderungen unter Nutzung spezifischer Assessmentinstrumente während oder nach einer Zytostatika- und Strahlentherapie
- Gestaltung der Ernährung bei Mukositis
- Umgang mit der Infektionsprophylaxe in unterschiedlichen Pflegesituationen
- Hospitation bei Pflegefachpersonen/Gesundheits- und Kinderkrankenpfleger*innen in der ambulanten pädiatrischen Palliativpflege
- Beobachtung und Reflexion des professionellen Verhaltens in der Gestaltung von Nähe und Distanz von Pflegefachpersonen/Gesundheits- und Kinderkrankenpfleger*innen in der ambulanten Kinderkrankenpflege
- Reflexion der beruflichen Rolle in der ambulanten pädiatrischen Palliativversorgung
- Besuch eines Kinderhospizes und Beschreibung seiner spezifischen Charakteristika insbesondere der dort stattfindenden Pflege und Begleitung
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 08: Alte Menschen in kritischen Lebenssituationen und in der letzten Lebensphase begleiten" %}
    Intentionen und Relevanz
Im 3. Ausbildungsdrittel wird erweiternd die umfassende und individuelle Pflege von alten Menschen in komplexen kritischen Lebenssituationen und in der letzten Lebensphase in den Mittelpunkt gerückt. Das gesamte Umfeld betroffener alter Menschen und weitere Kontexte werden ebenso im letzten Ausbildungsabschnitt in den Blick genommen.
Die Auszubildenden setzen sich in dieser curricularen Einheit tiefgreifend mit Phänomenen auseinander, die sich in der Begegnung mit existenziell herausgeforderten alten Menschen und ihren Bezugspersonen zeigen. Dies stellt hohe persönliche Anforderungen an die Auszubildenden, die weiterführend thematisiert werden sollen.
Bildungsziele
Die Lernenden reflektieren den gesellschaftlich-kollektiven, institutionellen und individuellen Umgang mit Tod und Sterben im Spannungsfeld von Entfremdung und Leiderfahrung. Sie nehmen die Gesellschaft und die Institutionen als Rahmung für die persönliche Auseinandersetzung mit dem Sterben sowie für die Gestaltung des Pflegeprozesses wahr.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Rollenspiele zu konkreten Situationen, z. B. auf eine Diagnosemitteilung angemessen reagieren, Beileidsbekundungen aussprechen, Mitteilung einer Todesnachricht
- Pflegeinterventionen üben, z. B. spezielle Mundpflege
- Besuch eines Hospizes und/oder einer Palliativstation (ggf. Expert*in einladen)

Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Alte Menschen, die von einer chronischen Krankheit betroffen sind, interviewen – mit besonderem Augenmerk auf die erste Konfrontation damit und auf Bearbeitungs-/Bewältigungsstrategien; Pflegebedarf ermitteln und Pflegeprozess gestalten
- Pflegesituationen mit sterbenden alten Menschen beobachten: Wie gehen Pflegepersonen damit um? Wie wird im Team darüber gesprochen? Wie werden Aushandlungsprozesse gestaltet?
- Pflegesituationen mit sterbenden alten Menschen gestalten und Erfahrungen reflektieren
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 09: Menschen bei der Lebensgestaltung lebensweltorientiert unterstützen" %}
   Intentionen und Relevanz
Über die gesamte Lebensspanne sind Menschen zu einer individuellen und selbstbestimmten Gestaltung ihres Lebens aufgefordert. Die Individualität von Lebenswelten findet ihren Ausdruck in individuellen Lebensentwürfen und in einer individuellen Lebensgestaltung, die in einem hohen Maße von der persönlichen Lebensgeschichte bestimmt wird. Diese ist wiederum in historische, gesellschaftliche und kulturelle Gesamtzusammenhänge eingebunden und ohne diese nicht zu verstehen.
In der Folge unterschiedlicher entwicklungsbedingter, funktionaler und/oder gesundheitsbedingter Herausforderungen erleben und erleiden Menschen Veränderungen oder gar Zusammenbrüche ihrer filigranen Lebenswelten vielfach dann, wenn bislang bewährte Kompensationsmechanismen ausfallen. Lebenskrisen wie Pflegebedürftigkeit beeinflussen den Wissenserwerb, die soziale Integration, das Erleben von Solidarität und die Entwicklung personaler Identität. Vor diesem Hintergrund stellen auch ein Wechsel oder notwendige Umgestaltungen des Wohnraumes und Wohnumfeldes bedeutsame Zäsuren dar, in deren Folge Teile der individuellen Lebenswelt zusammenbrechen können und neu gestaltet werden müssen. Ebenso müssen pflegende Bezugspersonen die eigenen Lebensentwürfe und die ihres Familiensystems neu ausrichten und situativ anpassen. Biografisch gewachsene Familiendynamiken verändern sich prozesshaft durch den Eintritt von Pflegebedürftigkeit.
Diese curriculare Einheit fokussiert solche Lebenssituationen, in denen beruflich Pflegende die zu pflegenden Menschen und ihre Bezugspersonen bei der Bewältigung von Entwicklungsherausforderungen begleiten, unterstützen und beraten, um eine individuelle Lebensgestaltung zu ermöglichen. Die Anerkennung individueller Lebenswelten erfordert von den beruflich Pflegenden die Anknüpfung an die individuelle Lebensgeschichte, die Berücksichtigung der Selbsteinschätzung der Lebenssituation durch die zu pflegenden Menschen als Grundlage für eine Pflegepraxis, die sich an den individuellen Bedeutungszusammenhängen der zu Pflegenden orientiert und deren Selbstbestimmung respektiert. Pflegerische Beziehungsgestaltung und Aushandlungsprozesse sind durch die Einbindung der primären und sekundären sozialen Netze komplex und anspruchsvoll. Nicht selten stehen der stützenden und schützenden Funktion, insbesondere durch die primären sozialen Netze, Belastungen, Überlastungen und Rollenkonflikte der pflegenden Bezugspersonen gegenüber. Sie resultieren u. a. aus einer Rollenumkehr gegenüber Eltern und Schwiegereltern und in der Sandwich-Generation aus den vielfältigen Ansprüchen aus Kindererziehung, Familie, Beruf und Pflege. Der Eintritt von Hilfs- und Pflegebedürftigkeit in Paarbeziehungen geht ebenfalls mit Herausforderungen einher, die eine Neuausrichtung der gemeinsamen Lebensentwürfe und Lebensgestaltung erfordern. Eine gelingende Balance zwischen den Ressourcen und positiven Wirkungen von sozialen Netzen einerseits und dem Belastungserleben und den Überforderungen andererseits ist entscheidend für eine tragfähige, langfristige und stabile familiale Pflegesituation und für den Gesundheitszustand und das Wohlbefinden des gesamten Familiensystems.
In den ersten beiden Ausbildungsdritteln steht vor allem eine lebensweltorientierte Pflegeprozessgestaltung mit dem zu pflegenden Menschen unter Berücksichtigung seines familialen Umfeldes im Fokus. Schwerpunkte des
letzten Ausbildungsdrittels sind darüber hinaus das Unterstützungspotenzial durch Bezugspersonen und primäre sowie sekundäre soziale Netze. Dies erfordert eine Orientierung am Sozialraum und an den wichtigen Einrichtungen und Diensten, die Beratung und Unterstützung anbieten, um möglichst lange ein selbstbestimmtes Leben im vertrauten und gewohnten Umfeld weiterzuführen. Für Angehörige der Pflegeberufe eröffnen sich hier – etwa in der Pflegeberatung – neue Handlungsfelder.
Die Lebensphase von Kindern und Jugendlichen ist Gegenstand der curricularen Einheit 10 „Entwicklung und Gesundheit in Kindheit und Jugend in Pflegesituationen fördern“. Zur Vermeidung größerer Schnittmengen sind diese Altersstufen nicht erneut Gegenstand der curricularen Einheit 09. Die curriculare Einheit 09 fokussiert vielmehr die unterschiedlichen Altersstufen vom jungen Erwachsenenalter bis in das höhere und hohe Lebensalter.

Bildungsziele
1./2. Ausbildungsdrittel
Die Auszubildenden reflektieren den Widerspruch zwischen Nah-Sein in der Pflegebeziehung und Fremdheitserleben in der Konfrontation mit Lebensentwürfen und Lebenswelten anderer Menschen. Sie setzen sich mit vorgeprägten Menschen- und Familienbildern sowie mit sogenannten Normalbiografien auseinander.
3. Ausbildungsdrittel
Die Auszubildenden entdecken das Spannungsverhältnis zwischen Erwartungen der Bevölkerung an das Gesundheits- und Sozialsystem bei Eintritt von Pflegebedürftigkeit und den gesellschaftlichen Erwartungen an die eigene/familiale Pflegebereitschaft.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
1./2. Ausbildungsdrittel
- szenisches Spiel zur Identifizierung von Interaktionsdimensionen und Interaktionsformen in der Interaktion mit demenziell veränderten Menschen
- Simulation eines Informationsgespräches über Fragen im Zusammenhang mit der Feststellung von Pflegebedürftigkeit
- Simulation eines Beratungsgespräches für pflegende Bezugspersonen
- Simulation eines Erstbesuches in der häuslichen Umgebung des pflegenden Menschen
3. Ausbildungsdrittel
- Gesprächssimulation mit einem älteren Menschen mit Vorschlägen zur Wohnraumanpassung
- Rollenspiele zur Information und Beratung von pflegenden Bezugspersonen, freiwillig Engagierten
- simulierte Schulung in ausgewählten Pflegetechniken
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
1./2. Ausbildungsdrittel
- Erkundungsauftrag: Angebote der Tages- und Alltagsgestaltung in stationären Einrichtungen oder zu sozialen Aktivitäten, die von der ambulanten Pflegeeinrichtung organisiert werden, einschließlich Zuständigkeiten der verschiedenen Berufsgruppen; Einbindung/Beteiligung der beruflich Pflegenden
- Falldokumentation: Lebensgeschichten nachzeichnen
- Recherche von niederschwelligen Angeboten/Entlastungsangeboten für pflegende Bezugspersonen in der
ausbildenden Einrichtung
3. Ausbildungsdrittel
- Erkundungsauftrag: Strukturen und Einbindung von Freiwilligenengagement in der ausbildenden Einrichtung und im Quartier
- Erkundungsauftrag: Unterstützungsangebote der ausbildenden Einrichtung für pflegende Bezugspersonen
- Erstellen einer Netzwerkkarte des Sozialraumes, des Quartiers
- Ermittlung alternativer Wohnformen im Quartier
- Gespräche mit zu pflegenden Menschen und ihren Bezugspersonen über Zufriedenheit mit dem pflegerischen Angebot
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 09: Alte Menschen bei der Lebensgestaltung lebensweltorientiert unterstützen" %}
    Intentionen und Relevanz
Diese curriculare Einheit schließt an die korrespondierende curriculare Einheit aus der generalistischen Ausbildungsphase der ersten beiden Ausbildungsdrittel an. Der Schwerpunkt im letzten Ausbildungsdrittel liegt für die Auszubildenden, die sich für einen Abschluss als Altenpflegerin/Altenpfleger entschieden haben, in der lebensweltorientierten Begleitung und Unterstützung von älteren Menschen in ihrer Lebensgestaltung. Ältere Menschen müssen in besonderer Weise aufgrund entwicklungsbedingter, funktionaler und/oder gesundheitsbedingter Herausforderungen und sozialer Veränderungen ihre Lebensentwürfe wiederholt neu ausrichten und situativ anpassen, wobei sich hier auch neue Möglichkeiten der sozialen Integration und der Sinnfindung eröffnen.
Während in den ersten beiden Ausbildungsdritteln vor allem eine lebensweltorientierte Pflegeprozessgestaltung mit dem zu pflegenden älteren Menschen unter Berücksichtigung seines familialen Umfeldes im Fokus stand, werden in den Schwerpunkten des letzten Ausbildungsdrittels darüber hinaus das Unterstützungspotenzial durch Bezugspersonen und primäre sowie sekundäre soziale Netze in den Blick genommen. Dies erfordert eine Orientierung am Sozialraum und an den wichtigen Einrichtungen und Diensten, die Beratung und Unterstützung anbieten, um möglichst lange ein selbstbestimmtes Leben im vertrauten und gewohnten Umfeld weiterzuführen. Für Angehörige der Pflegeberufe eröffnen sich hier – etwa in der Pflegeberatung – neue Handlungsfelder.

Bildungsziele
Die Auszubildenden entdecken das Spannungsverhältnis zwischen Erwartungen der Bevölkerung an das Gesundheits- und Sozialsystem bei Eintritt von Pflegebedürftigkeit und den gesellschaftlichen Erwartungen an die eigene/familiale Pflegebereitschaft.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Gesprächssimulation mit einem älteren Menschen mit Beratung zur Wohnraumanpassung
- Rollenspiele zur Information und Beratung von pflegenden Bezugspersonen und freiwillig Engagierten
- simulierte Schulung in ausgewählten Pflegetechniken
Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Erkundungsauftrag: Strukturen und Einbindung von Freiwilligenengagement in der eigenen Einrichtung und im Quartier
- Erkundungsauftrag: Unterstützungsangebote der ausbildenden Einrichtung für pflegende Bezugspersonen
- Erstellen einer Netzwerkkarte des Sozialraumes, des Quartiers
- Ermittlung alternativer Wohnformen für alte Menschen im Quartier
- Gespräche mit zu pflegenden Menschen und ihren Bezugspersonen über Zufriedenheit mit dem pflegerischen Angebot
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 10: Entwicklung und Gesundheit in Kindheit und Jugend in pflegerischen Situationen fördern" %}
    Intentionen und Relevanz
Diese curriculare Einheit bezieht sich schwerpunktmäßig auf die pflegerische Versorgung von Säuglingen, Kindern und Jugendlichen sowie deren Bezugspersonen und nimmt in besonderer Weise die Entwicklungsförderung von Kindern und Jugendlichen in den Blick. Dabei folgt die curriculare Einheit zwei grundsätzlichen Intentionen, nämlich den Auszubildenden sowohl eine Orientierung über das Handlungsfeld der Pflege von Kindern und Jugendlichen zu geben und damit den Pflichteinsatz in der pädiatrischen Versorgung vor- oder nachzubereiten als auch das Thema der Entwicklungsförderung als Schwerpunkt für den Vertiefungseinsatz in der Gesundheits- und Kinderkrankenpflege während der praktischen (generalistischen) Ausbildung einzuführen.
Entwicklungsförderung und die Unterstützung von Familiensystemen erfolgen in allen Settings, in denen pädiatrische Einsätze stattfinden. Nahezu alle Einrichtungen tragen den entwicklungsbedingten Anforderungen von Säuglingen, Kindern und Jugendlichen sowie den Bedarfen von Familien durch spezifische Kontextbedingungen Rechnung. Sie sind mit sozialen, kulturellen und räumlichen Besonderheiten verbunden, die die (pflegerischen) Gestaltungsspielräume wesentlich mitbestimmen.
Die subjektive Betroffenheit von Krankheit erfordert erhebliche soziale Anpassungsleistungen von Kindern und Jugendlichen sowie deren Bezugspersonen. Die situationsorientierte Unterstützung durch die professionelle Pflege muss so gestaltet werden, dass Selbstständigkeit und Selbstbestimmung entwicklungsentsprechend gewahrt und gefördert werden.
Die pflegerische Versorgung von Säuglingen, Kindern und Jugendlichen ist i. d. R. durch die Anwesenheit von Eltern/Bezugspersonen gekennzeichnet und findet nahezu immer in einer Triade statt. Eine zentrale Aufgabe der beruflich Pflegenden besteht in der Förderung der Elternkompetenz durch Information, Beratung und Schulung. Da die Eltern/Bezugspersonen oftmals spezifische pflegerische Aufgaben bei ihren Säuglingen, Kindern und Jugendlichen übernehmen, sind bei der pflegerischen Beziehungsgestaltung auch Aushandlungsprozesse und Rollenzuweisungen erforderlich. Die Lebensgewohnheiten sowie der sozioökonomische Status der Familien beeinflussen erheblich den Umgang mit gesundheits- und entwicklungsbedingten Pflegebedarfen. Zugleich findet die Pflege von kranken Säuglingen, Kindern und Jugendlichen auch in familiären Übergangssituationen statt, die z. T. mit erheblichen Veränderungen in den Lebensentwürfen und den sozialen Systemen verbunden sind. Diese Übergangssituationen können auch darauf ausgerichtet sein, die Chronifizierung eines Krankheitsverlaufs anzunehmen und zu akzeptieren.
Die Lernsituationen in dieser curricularen Einheit sind exemplarisch an der Geburt eines Kindes (bzw. eines moderat zu früh geborenen Kindes), an den Folgen einer Neurodermatitis sowie einer Asthmaerkrankung bei Kindern und eines Diabetes mellitus Typ 1 bei einer/einem Jugendlichen ausgerichtet.

Bildungsziele
1./2. Ausbildungsdrittel
Kindheit und Jugend bedürfen entsprechend der „Konventionen über die Rechte des Kindes“ des besonderen Schutzes. Die gesellschaftlichen Bedingungen sowie die Kontextbedingungen in der pädiatrischen Versorgung sind den Konventionen zwar verpflichtet, werden diesem Anspruch aber nicht immer gerecht. Auszubildende sollen sich mit diesem Spannungsverhältnis auseinandersetzen und dazu eine begründete und reflektierte Position einnehmen.
3. Ausbildungsdrittel
Häufig zeichnen sich die Bezugspersonen von kranken Säuglingen, Kindern und Jugendlichen durch eine hohe Expertise bezüglich des Gesundheitszustandes und der sozialen, emotionalen und kognitiven Kompetenzen ihrer Kinder aus. Dennoch bedarf es der Gestaltung von Informations- und Beratungsgesprächen. Es gilt, die damit verbundenen Rollenkonflikte zu erkennen und dazu eine ethisch reflektierte Position zu entwickeln.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Simulation eines Aushandlungsprozesses zwischen der professionellen Pflege und den Eltern eines Frühgeborenen
- Simulation von pflegerischen Gesprächen zur Information und Schulung von Kindern, Jugendlichen und ihren Bezugspersonen mit unterschiedlichen kognitiven, emotionalen sozialen und kulturellen Voraussetzungen
- Simulation einer Schulung und/oder Beratung (Beratung durch Information) von Kindern und Jugendlichen und/oder ihren sozialen Bezugspersonen, für unterschiedliche Handlungsanlässe, mit unterschiedlichen kognitiven und sozialen Voraussetzungen

Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
1./2. Ausbildungsdrittel
- sich mit ausgewählten und spezifischen, auf Frühgeborene und das Kindesalter ausgerichteten Assessmentinstrumenten auseinandersetzen
- die Merkmale einer verständigungsorientierten Kommunikation mit Schulkindern zur Vorbereitung einer schmerzhaften Intervention erarbeiten
- Merkmale von Rollenaushandlungsgesprächen im Rahmen des Pflegeprozesses in einer Lerngruppe zusammenstellen
- Interviews mit Eltern zum Erleben von Krankheit und Krankenhausaufenthalt durchführen
3. Ausbildungsdrittel
- Merkmale eines Informationsgesprächs von einem Beratungsgespräch abgrenzen
- Merkmale eines Gesprächs zur Information eines Kindes/einer bzw. eines Jugendlichen bezüglich der Hautpflege oder des Umgangs mit einem Inhalationsgerät zusammenstellen
- Merkmale einer Schulung zur Erweiterung elterlicher Pflegekompetenzen bezüglich der Ernährung eines Frühgeborenen ableiten
- Merkmale einer Schulung zur Erweiterung elterlicher Pflegekompetenzen bezüglich einer Notfallsituation bei einem Asthma bronchiale ableiten
Die simulierten Pflegesituationen/Berufssituationen sollten so gestaltet werden, dass die Selbstreflexion stets einen Teil des Lernprozesses ausmacht und damit auch die Persönlichkeitsentwicklung und -förderung zum Gegenstand des Lernens wird.
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 11: Menschen mit psychischen Gesundheitsproblemen und kognitiven Beeinträchtigungen personenzentriert und lebensweltbezogen unterstützen" %}
    Intentionen und Relevanz
Die in dieser curricularen Einheit im Mittelpunkt stehenden Kompetenzen werden in Vorbereitung auf den im 3. Ausbildungsdrittel stattfindenden Pflichteinsatz in der psychiatrischen Versorgung aufgebaut bzw. sind auf das vertiefte Verstehen der gewonnenen Erfahrungen ausgerichtet. Menschen mit Problemen und Risiken im Bereich der psychischen und kognitiven Gesundheit sind aber gleichwohl nicht nur in psychiatrischen, sondern in allen pflegerischen Settings anzutreffen, sodass die in dieser curricularen Einheit und in dem damit korrespondierenden Pflichteinsatz erworbenen Kompetenzen in allen Settings relevant sind und auch bereits in den ersten zwei Ausbildungsdritteln aufgebaut werden müssen.
Psychische Erkrankungen und kognitive Beeinträchtigungen sind in der Allgemeinbevölkerung Deutschlands weit verbreitet. Zu den am häufigsten diagnostizierten psychischen Erkrankungen gehören Angststörungen, affektive Störungen (z. B. Depressionen) sowie Störungen durch Alkohol- und Medikamentenkonsum. Vor allem alte Menschen sind in einem hohen Ausmaß von kognitiven Beeinträchtigungen, insbesondere von Demenz, betroffen. Aus gesellschaftskritischer Perspektive spiegeln sich in psychiatrischen Diagnosen implizite und explizite gesellschaftliche Werthaltungen und damit verbundene Selektions- und Ausgrenzungsmechanismen wider. In der Diagnostik (seelisch) abweichenden Verhaltens schlägt sich der Verständigungsprozess der Gesellschaft über vernünftiges Denken und Handeln nieder. Für die betroffenen Personen resultiert daraus nicht nur das durch die Erkrankung verursachte Leid, sondern sie erfahren außerdem Prozesse der Ausgrenzung, Stigmatisierung und Diskriminierung. Der Kern der Pflege von Menschen mit psychischen Problemlagen und kognitiven Beeinträchtigungen besteht in einer reflektierten Beziehungsgestaltung. Für Auszubildende liegt die besondere Herausforderung darin, Beziehungen zu Menschen zu gestalten, deren Wahrnehmung und Erleben nicht immer dem gewohnten Verständnis von Realität entsprechen. Dabei können eigene Abwehrprozesse und ggf. Projektionen den Beziehungsaufbau zusätzlich erschweren. Der Fokus der curricularen Einheit liegt in den ersten beiden Ausbildungsdritteln zunächst auf der grundlegenden Befähigung zur Perspektivenübernahme und zum Beziehungsaufbau mit Menschen, die durch psychische Gesundheitsprobleme und kognitive Beeinträchtigungen in der Gestaltung des Lebensalltags und des sozialen Gefüges eingeschränkt sind. Beim Beziehungsaufbau und der Beziehungsgestaltung sind die Prinzipien des Lebensweltbezugs und der Personenzentrierung leitend.
Im 3. Ausbildungsdrittel verschiebt sich der Schwerpunkt auf Menschen mit schweren psychischen Erkrankungen und kognitiven Beeinträchtigungen und komplexem Hilfebedarf in instabilen Situationen bzw. psychischen Krisen oder bei herausforderndem Verhalten.
Bei den im Mittelpunkt stehenden Erkrankungen und Pflegediagnosen ist die Balance von Nähe und Distanz sowie von Autonomie und Abhängigkeit in der Beziehungsgestaltung besonders anspruchsvoll. Die Auszubildenden analysieren sowohl die eigene Beziehungsgestaltung mit Betroffenen als auch die Beziehungen innerhalb von Familiensystemen und anderen sozialen Bezugsgruppen und lernen, systematisch systemische Aspekte in ihr Pflegehandeln einzubeziehen. Neben der dialogischen wird die trialogische pflegerisch-therapeutische Beziehungsgestaltung mit struktur- und sektorübergreifender Kontinuität fokussiert.

Bildungsziele
1./2. Ausbildungsdrittel
Die Auszubildenden reflektieren im ersten Ausbildungsabschnitt das eigene innere Erleben in der Interaktion mit Menschen mit psychischen Erkrankungen und/oder kognitiven Beeinträchtigungen einschließlich widerstreitender Gefühle, sie werden ihrer Ängste und möglicher Abwehrmechanismen gewahr. Des Weiteren reflektieren sie den Widerspruch zwischen zu pflegenden Menschen sowie professionell Pflegenden als Träger von Rollen auf der einen und als ganze „Personen“, die sich nicht auf Rollen reduzieren lassen, auf der anderen Seite. Sie erkennen, dass klinische Diagnosen das Ergebnis von sozialen Konstruktionsprozessen sind.
3. Ausbildungsdrittel
Im 2. Ausbildungsabschnitt reflektieren die Auszubildenden die Asymmetrie der Beziehung zwischen psychisch kranken Menschen und professionell Pflegenden und die damit verbundenen Machtpotenziale. Sie untersuchen die Grenzen zwischen Selbstschutz der zu pflegenden Menschen in psychischen Problemlagen und/oder mit kognitiven Beeinträchtigungen und/oder Schutz anderer Menschen (auch der Pflegenden selbst) auf der einen Seite und der Ausübung von Gewalt bzw. Missachtung/Misshandlung/Misswürdigung auf der anderen Seite. Des Weiteren loten sie Möglichkeiten der Beziehungsgestaltung zwischen dem Aufbau einer Vertrauensbasis und aktiver und quasi-vormundschaftlicher Fürsorge bzw. Kontrolle aus. Vor dem Hintergrund der Ungewissheit in der Deutung des Verhaltens von zu pflegenden Menschen mit psychischen Erkrankungen und/oder kognitiven Beeinträchtigungen können Auszubildende in dieser curricularen Einheit die Einsicht gewinnen, dass sie ihre vorläufigen Deutungen im situativen Handeln immer wieder überprüfen müssen.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Gesprächs- und Beratungssituationen mit zu pflegenden Menschen und ggf. ihren Bezugspersonen in der psychiatrischen Pflege üben

Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
1./2. Ausbildungsdrittel (bezogen auf zu pflegende Menschen mit psychischen Erkrankungen oder kognitiven Beeinträchtigungen in allen pflegerischen Versorgungsbereichen)
- Biografie eines zu pflegenden Menschen mit psychischer Erkrankung oder kognitiver Beeinträchtigung erheben und daraus Schlussfolgerungen für die Versorgung ableiten
- Aufbau und Gestaltung einer tragfähigen und belastbaren Arbeitsbeziehung eines zu pflegenden Menschen mit psychischer Erkrankung bzw. kognitiver Beeinträchtigung beispielhaft anhand von Kriterien beschreiben
- biopsychosoziale Beobachtung und Interpretation der Beobachtungen vor dem Hintergrund verschiedener (sozialwissenschaftlicher/psychologischer/medizinischer) Theorien
3. Ausbildungsdrittel
- Erhebung des Pflegebedarfs und Planung, Dokumentation und Evaluation des Pflegeprozesses bei einem Menschen mit einer schweren psychischen Erkrankung und komplexem Hilfebedarf bzw. mit fortgeschrittener kognitiver Beeinträchtigung
- Situationen der Eskalation von Gewalt bzw. der aktiven Deeskalation beobachten und reflektieren
- Anwendung von Formen freiheitsentziehender Maßnahmen bzw. von Maßnahmen zur Vermeidung von Gewalt beobachten und reflektieren
- Bericht über die Begleitung von Pflegefachpersonen bei Hausbesuchen im Rahmen der Ambulanten Psychiatrischen Pflege (APP) oder aufsuchenden Versorgungsmodellen (z. B. Hometreatment)
- Bericht über die Teilnahme an Trialogforen
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 11: Kinder und Jugendliche mit psychischen Gesundheits- problemen und kognitiven Beeinträchtigungen personenzentriert und lebensweltbezogen unterstützen" %}
    Intentionen und Relevanz
Die in dieser curricularen Einheit im Mittelpunkt stehenden Kompetenzen werden in Vorbereitung auf den im 3. Ausbildungsdrittel stattfindenden Pflichteinsatz in der kinder- und jugendpsychiatrischen Versorgung aufgebaut bzw. sind auf das vertiefte Verstehen der gewonnenen Erfahrungen ausgerichtet. Kinder und Jugendliche mit Problemen und Risiken im Bereich der psychischen und/oder kognitiven Gesundheit sind aber gleichwohl nicht nur in psychiatrischen, sondern in allen pflegerischen Settings anzutreffen, sodass die in dieser curricularen Einheit und in dem damit korrespondierenden Pflichteinsatz erworbenen Kompetenzen in allen Settings relevant sind.
Im 3. Ausbildungsdrittel liegt der Schwerpunkt auf Kindern und Jugendlichen mit schweren psychischen Erkrankungen und/oder kognitiven Beeinträchtigungen und komplexem Hilfebedarf in instabilen Situationen bzw. psychischen Krisen. Bei den im Mittelpunkt stehenden Erkrankungen und Pflegediagnosen ist die Balance von Nähe und Distanz sowie von Autonomie und Abhängigkeit in der Beziehungsgestaltung besonders anspruchsvoll. Die Auszubildenden analysieren sowohl die eigene Beziehungsgestaltung mit Betroffenen als auch die Beziehungen innerhalb von Familiensystemen und ggf. Peergroups und lernen, systematisch systemische Aspekte in ihr Pflegehandeln einzubeziehen. Es werden außerdem Ansatzpunkte ermittelt, wie die Interaktion innerhalb der Familien verbessert sowie Teilhabe und Autonomiegewinnung gestärkt werden können. Der Schwierigkeitsgrad der Beziehungsgestaltung ist dadurch besonders hoch, dass neben den zu pflegenden Kindern und Jugendlichen stets die sorgeberechtigten Personen in die Interaktion einbezogen werden müssen. Zudem erfordert die Arbeit mit Heranwachsenden eine Gestaltung nicht nur von Pflegeprozessen, sondern auch von Erziehungsprozessen im interprofessionellen Team. Des Weiteren werden in der curricularen Einheit Konzepte für die struktur- und sektorenübergreifende Versorgung fokussiert.

Bildungsziele
Die Auszubildenden reflektieren das Spannungsverhältnis zwischen Nähe und Distanz sowie Freiheit und Abhängigkeit in der Beziehungsgestaltung mit psychisch kranken Kindern und Jugendlichen. Des Weiteren loten sie Möglichkeiten der Beziehungsgestaltung zwischen dem Aufbau einer Vertrauensbasis und aktiver Fürsorge bzw. Kontrolle aus. In der Zusammenarbeit mit Familien erarbeiten sie mögliche Konflikte zwischen der elterlichen Verantwortung und dem Wohl der Kinder und Jugendlichen.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Gesprächs- und Beratungssituationen mit Kindern und Jugendlichen und ihren Bezugspersonen in der psychiatrischen Pflege üben

Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Erhebung Pflegebedarf und Planung, Dokumentation und Evaluation des Pflegeprozesses bei Kindern und Jugendlichen mit einer schweren psychischen Erkrankung und komplexem Hilfebedarf
- Kommunikationssituationen mit Kindern und Jugendlichen, deren Realitätswahrnehmung stark von der eigenen abweicht, beschreiben und anhand von theoretischen Modellen reflektieren
- Anwendung von stark kontrollierenden Pflegeinterventionen beobachten und reflektieren
- familiäre Interaktionssituationen anhand von theoretischen Modellen analysieren und Schlussfolgerungen für pflegerische Interventionen ziehen
- Bericht über die Begleitung von Pflegefachpersonen bei Hausbesuchen im Rahmen aufsuchender Versorgungsmodelle (z. B. Hometreatment)
  {% elif r|param:"LNG-BS-Lernfeld" == "CE 11 Alte Menschen mit psychischen Gesundheitsproblemen und kognitiven Beeinträchtigungen personenzentriert und lebensweltbezogen unterstützen" %}
    Intentionen und Relevanz
Die in dieser curricularen Einheit im Mittelpunkt stehenden Kompetenzen werden in Vorbereitung auf den im 3. Ausbildungsdrittel stattfindenden Pflichteinsatz in der gerontopsychiatrischen Versorgung aufgebaut bzw. sind auf das vertiefte Verstehen der gewonnenen Erfahrungen ausgerichtet. Menschen mit Problemen und Risiken im Bereich der psychischen und kognitiven Gesundheit sind aber gleichwohl nicht nur in psychiatrischen, sondern in allen pflegerischen Settings anzutreffen, sodass die in dieser curricularen Einheit und in dem damit korrespondierenden Pflichteinsatz erworbenen Kompetenzen in allen Settings relevant sind.
Im 3. Ausbildungsdrittel liegt der Schwerpunkt auf alten Menschen, die von schweren psychischen Erkrankungen und/oder kognitiven Beeinträchtigungen betroffen sind, mit komplexem Hilfebedarf in instabilen Situationen bzw. psychischen Krisen oder bei herausforderndem Verhalten. Bei den im Mittelpunkt stehenden Erkrankungen und Pflegediagnosen ist die Balance von Nähe und Distanz sowie von Autonomie und Abhängigkeit in der Beziehungsgestaltung besonders anspruchsvoll. Die Auszubildenden analysieren sowohl die eigene Beziehungsgestaltung mit Betroffenen als auch die Beziehungen innerhalb von Familiensystemen und/oder anderen Bezugsgruppen und lernen, systematisch systemische Aspekte in ihr Pflegehandeln einzubeziehen. Neben der dialogischen wird die trialogische pflegerisch-therapeutische Beziehungsgestaltung mit struktur- und sektorübergreifender Kontinuität fokussiert. Bei der Unterstützung der zu pflegenden Menschen orientieren sich die Auszubildenden an den Prinzipien des Lebensweltbezugs und der Personenzentrierung.

Bildungsziele
Die Auszubildenden reflektieren die Asymmetrie der Beziehung zwischen alten psychisch kranken Menschen und professionell Pflegenden und die damit verbundenen Machtpotenziale. Sie untersuchen die Grenzen zwischen Selbstschutz der alten Menschen in psychischen Problemlagen und/oder mit kognitiven Beeinträchtigungen und/oder Schutz anderer Menschen (auch der beruflich Pflegenden selbst) auf der einen Seite und der Ausübung von Gewalt bzw. Missachtung/Misshandlung/Misswürdigung auf der anderen Seite. Des Weiteren loten sie Möglichkeiten der Beziehungsgestaltung zwischen dem Aufbau einer Vertrauensbasis und aktiver und quasi-vormundschaftlicher Fürsorge bzw. Kontrolle aus. Vor dem Hintergrund der Ungewissheit in der Deutung des Verhaltens von zu pflegenden alten Menschen mit psychischen Erkrankungen und/oder kognitiven Beeinträchtigungen können Auszubildende in dieser curricularen Einheit die Einsicht gewinnen, dass sie ihre vorläufigen Deutungen im situativen Reagieren immer wieder überprüfen müssen.

Anregungen für das Lernen in simulativen Lernumgebungen (Beispiele)
- Gesprächs- und Beratungssituationen mit zu pflegenden alten Menschen und ihren Bezugspersonen in der psychiatrischen Pflege üben

Anregungen für Lern- und Arbeitsaufgaben (Beispiele)
- Erhebung des Pflegebedarfs und Planung, Dokumentation und Evaluation des Pflegeprozesses bei einem alten Menschen mit einer schweren psychischen Erkrankung und komplexem Hilfebedarf und/oder mit fortgeschrittener kognitiver Beeinträchtigung
- Kommunikationssituationen mit alten Menschen mit herausforderndem Verhalten gestalten, schriftlich beschreiben und anhand von theoretischen Modellen reflektieren
- Situationen der Eskalation von Gewalt bzw. der aktiven Deeskalation beobachten und reflektieren
- Anwendung von Formen freiheitsentziehender Maßnahmen bzw. von Maßnahmen zur Vermeidung von Gewalt beobachten und reflektieren
{% endif %}
{% endif %}
{% endif %}

{% if r|param:"Stundenplanung Berufsschule: Zeitumfang" == "Einzelstunde" or r|param:"Stundenplanung Berufsschule: Zeitumfang" == "Doppelstunde" %}
Du erstellst eine Stundenplanung für das Kompetenzziel {{ r|param:"BS_Lernsituation_Handlungskompetenz" }} für eine {{ r|param:"Stundenplanung Berufsschule: Zeitumfang" }}.
{% else %}Du erstellst eine Stundenverlaufsplanung für {{ r|param:"Stundenplanung Berufsschule: Anzahl Unterrichtseinheiten" }} Unterrichtseinheiten. 
{% endif %}

Es sollen folgende Inhalte aufgegriffen werden: {{ r|param:"BS_Lernsituation_Inhalte" }}. Gib jetzt nur den Titel aus und sonst nichts.

Erstelle den Kopfbereich eines Unterrichtsentwurfs mit einer strukturierten Übersicht aller relevanten Rahmendaten:

{% if r|param:"LNG-BS-LF" == "Ja" %}
  - Lernfeld: {{ r|param:"LNG-BS-Lernfeld" }}
{% endif %}
- Ausbildungsjahr: {{ r|param:"LNG-BS-Jahr" }}
- Zeitumfang: {{ r|param:"Stundenplanung Berufsschule: Anzahl Unterrichtseinheiten" }} Unterrichtseinheiten
- Kompetenzziel: {{ r|param:"BS_Lernsituation_Handlungskompetenz" }}


Gib nur die formatierte Übersicht mit einer kurzen Einleitung aus, keine weiteren Erläuterungen oder Kommentare. Formatiere die Übersicht in HTML ohne HEAD-Bereich. Der Inhalt wird anschließend in ein größeres HTML-Dokument eingefügt. Die Stichpunkte sollen als Liste formartiert sein.

Erstelle einen Verlaufsplan für {{ r|param:"Stundenplanung Berufsschule: Anzahl Unterrichtseinheiten" }} Unterrichtseinheiten mit dem Kompetenzziel {{ r|param:"BS_Lernsituation_Handlungskompetenz" }} in der CE {{ r|param:"LNG-BS-Lernfeld" }}.

{% if r|param:"Stundenplanung Berufsschule: Zeitumfang" == "Einzelstunde" or r|param:"Stundenplanung Berufsschule: Zeitumfang" == "Doppelstunde" %}
Erstelle einen detaillierten Verlaufsplan als Tabelle mit den Spalten:
Zeit | Phasen | geplantes LK-Verhalten | erwartetes SuS-Verhalten | Sozialformen | Medien

{% elif r|param:"Stundenplanung Berufsschule: Zeitumfang" == "Unterrichtsreihe" %}
Erstelle für jede Stunde einen kompakten Verlaufsplan.
Nutze für jede Stunde eine Tabelle mit den Spalten:
Zeit | Phasen | geplantes LK-Verhalten | erwartetes SuS-Verhalten | Sozialformen | Medien

Kennzeichne jede Stunde mit Nummer und Teilthema als Zwischenüberschrift.
{% endif %}

Berücksichtige dabei:
- Handlungsorientierung als didaktisches Prinzip
- Ausbildungsjahr {{ r|param:"LNG-BS-Jahr" }} mit entsprechendem Komplexitätsniveau

- Bevorzugte Methoden: {{ r|param:"Stundenplanung Berufsschule: Methodenwuensche" }}

- Weitere Hinweise: {{ r|param:"Stundenplanung Berufsschule: Sonstiges" }}

Gib jetzt nur den Plan und sonst nichts aus. Formatiere alles in HTML ohne HEAD-Bereich. Das Ergebnis wird in ein größeres HTML-Dokument eingebettet.

Ergänze den Verlaufsplan um didaktische Hinweise.

{% if r|param:"Stundenplanung Berufsschule: Zeitumfang" == "Einzelstunde" or r|param:"Stundenplanung Berufsschule: Zeitumfang" == "Doppelstunde" %}
Formuliere 3–5 kurze Hinweise zu:
- Worauf sollte die Lehrkraft besonders achten?
- Welche typischen Verständnisschwierigkeiten könnten auftreten?
- Wie kann bei Zeitproblemen gekürzt oder erweitert werden?

{% elif Zeitumfang == "Unterrichtsreihe" %}
Formuliere 5–7 Hinweise zu:
- Roter Faden: Wie hängen die Stunden zusammen?
- Progression: Wie baut sich die Kompetenz über die Reihe auf?
- Kritische Stellen: Wo könnten Schwierigkeiten auftreten?
- Flexibilität: Wie kann bei Zeitproblemen reagiert werden?
- Sicherung: Wie wird der Lernerfolg über die Reihe hinweg gesichert?
{% endif %}

Gib nur die didaktischen Hinweise und sonst nichts aus. Formatiere das Ergebnis sinnvoll in HTML ohne HEAD-Element. Das Ergebnis wird anschließend in ein größeres HTML-Dokument eingefügt.