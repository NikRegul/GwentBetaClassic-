# Gwent Beta Classic 0.9.0 — Deutsch

> Version 0.9.0 — separate Pakete für Classic 1.32 und Next-Gen 5.0+.

## Wichtig

Sichere vor der Installation und vor jedem Update deine Spielstände. Die Mod befindet sich in aktiver Entwicklung, nutze für die ersten Partien einen separaten Spielstand.

Kartentexte stammen aus der offiziellen Beta-Lokalisierung. Die Oberfläche wurde mit KI-Unterstützung übersetzt und kann sprachliche Fehler enthalten. Meldungen zum Deckaustausch gibt es in allen 13 Textsprachen; einige ältere Hinweise erscheinen ersatzweise auf Englisch. Verbesserungsvorschläge sind willkommen.

**Steam Deck:** Die Mod läuft auf dem Steam Deck (vom Autor getestet).

## Neu in 0.9.0

- Export zeigt einen BG1-Textcode.
- Konsolenbefehle für Sammlungsressourcen, Kartensuche, Fraktionssammlungen und den Fassbestand beim Gastwirt.
- Karten, die auf den Friedhof kommen, fliegen nun zum tatsächlichen Friedhof; ausgespielte Spezialkarten ebenso nach ihrer Auflösung. Verbannung und Auflösungseffekte bleiben erhalten.
- Integrierte Definitionen alter Redux-Gegenstände helfen, Inventar- und Körperverlust beim Laden älterer Spielstände nach dem Wechsel zu verhindern. Bereits verlorene und gespeicherte Inventardaten werden nicht wiederhergestellt.
- Überarbeitete Menüabstände, Deckstatus und Aktionsschaltflächen; mit dem Controller gelangt man vom sichtbaren Kartenregal zu Speichern und zurück.
- Anführerporträts bleiben nach ihrem VS-Auftritt animiert. Der Auftritt der Krabbspinnenkönigin beginnt mit ihrer Sprachausgabe. Classic 1.32 enthält Korrekturen für Frost und Angriffseffekte.
- Vollständige Kartenansicht im Beta-Stil: große Karte mit dem originalen Fraktionsbanner aus Beta 0.9.24 (Fraktionen, neutrale Karten und Anführer), Grundstärke, lesbarer Zitattext, hervorgehobene Schlüsselwörter und Blättern mit ←/→.
- Deckcode aus der Windows-Zwischenablage im Import einfügen (Schaltfläche „Einfügen“ oder Strg+V; erfordert Optional-CopyButton).
- Tutorial auf 10 Seiten erweitert: Mulligan und Nachziehen, Reihen und Nachbarn, Kartenstatus.
- Kartenkorrekturen wie in der Beta: Myrgtabrakke verursacht dreimal 2 Schaden, die Fähigkeit von Harald dem Krüppel trifft zehnmal.


## KI und Oberfläche

Igni, Yrden, Birnas Wetterprognose und die Rüstungsfähigkeiten von Redanischem Ritter, Elite und Knappen werden besser bewertet. Nach einem Pass berücksichtigt das Aufholen echte Spielzüge und Zugwechsel. Ein letzter Pass erzeugt keinen zusätzlichen Effekt. In Runde eins ist eine Karte Nachteil vertretbar; zwei erfordern Abwägung, drei werden beim freiwilligen Aufholen vermieden. Ein drohender Matchverlust hat Vorrang. Übersetzte Schaltflächen und Fensterabstände wurden überarbeitet.

Isengrim: Gesetzloser vergleicht nun Sonderkarte und Erschaffen, auch nach Königlichem Erlass. Die KI vermeidet eine Vogelscheuche ohne gültiges verbündetes Bronze- oder Silberziel und bewertet die zufällige Auswahl aus drei Karten, ohne künftige Zufallsergebnisse zu kennen.

## Über die Mod

Gwent Beta Classic ersetzt das Gwint aus The Witcher 3 durch die Karten, Regeln und das Spielbrett der eigenständigen Gwent Beta 0.9.24. Die Partien bleiben Teil der Witcher-Welt: Spiele gegen NPCs, erledige Quests, kaufe Fässer und baue deine eigenen Decks.

## Funktionen

- 479 Sammelkarten, darunter 21 Anführer, alle fünf Fraktionen
- Spielbrett, HUD, Schriften, Kartenrahmen, Wetter und Effekte der Beta; animierte Anführer
- Deck-Editor: fünf veränderbare Startdecks und acht eigene Plätze, Filter und Suche
- Gegner mit 46 Deck-Archetypen der Beta und drei KI-Schwierigkeitsstufen
- Fässer für 200 Kronen bei allen Wirten, geöffnet wie in der Beta
- Fetzen: Karten für 30 / 80 / 200 / 800 je nach Seltenheit herstellen; überzählige Exemplare werden automatisch zermahlen
- Tutorial, Mulligan, Ansicht von Friedhöfen und Deck, ausführliche Kartenansicht
- Maus, Tastatur und Controller

## Decks teilen

Export zeigt einen sprachunabhängigen BG1-Code. Kopieren legt ihn direkt in die Windows-Zwischenablage; mit Strg+V überall einfügen. Dafür den optionalen Ordner Optional-CopyButton nutzen: dessen bin-Ordner ins Spielverzeichnis kopieren (dinput8.dll und plugins/GwentBetaClipboard.asi neben witcher3.exe). Der Mod selbst funktioniert auch ohne ihn. Hat ein anderer Mod bereits eine eigene dinput8.dll, diese behalten und GwentBetaClipboard.asi über dessen ASI-Loader laden. Ohne diese Dateien sind die Schaltflächen Import und Export ausgeblendet. Import nimmt den vollständigen BG1-Code im Textfeld an.

Fehlende Karten einschließlich Anführer werden mit den gesamten Herstellungskosten angezeigt. Herstellung benötigt eine gesonderte Bestätigung und genügend Scraps. Der Import erstellt einen Entwurf: anschließend das Deck speichern. In der Deckliste wird ein freier eigener Platz verwendet, belegte Plätze werden nicht überschrieben. Im Training gilt die vorhandene unbegrenzte Sammlung.

## Konsolenbefehle

bg_help() zeigt die Hilfe, bg_status() Sammlung, Fässer und Scraps. bg_find('Imlerith') sucht Namen und IDs; bg_card(132102,1) gibt eine Karte, bg_faction('monsters') eine Fraktion. bg_leaders() / bg_allcards() ergänzen Anführer bzw. die gesamte Sammlung bis zum normalen Kopienlimit. bg_kegs(10) und bg_scraps(1000) fügen Ressourcen hinzu. Dafür muss ein Spielstand geladen und jedes Menü sowie jede Partie geschlossen sein; danach regulär speichern. Im geöffneten Gastwirtladen prüft bg_shopcheck() den Fassbestand, bg_shoprefill(5) füllt ihn auf fünf auf, statt jedes Mal fünf hinzuzufügen. Die Spielkonsole muss bereits aktiviert sein.

```text
bg_help()
bg_status()
bg_find('Imlerith')
bg_card(132102,1)
bg_faction('monsters')
bg_leaders()
bg_allcards()
bg_kegs(10)
bg_scraps(1000)
bg_shopcheck()
bg_shoprefill(5)
```

## Sprachen

Text: Englisch, Russisch, Deutsch, Französisch, Italienisch, Polnisch, Spanisch (Spanien), Spanisch (Lateinamerika), Portugiesisch (Brasilien), Japanisch, Koreanisch, vereinfachtes und traditionelles Chinesisch. Jederzeit umschaltbar über die Textsprache-Schaltfläche oben links in den Deck- und Sammlungsmenüs oder in den Kampfeinstellungen; die Wahl wird gespeichert.

Jedes Paket enthält RU, EN, DE, IT und PT-BR. Text und Stimmen lassen sich unabhängig über zwei benachbarte Schaltflächen im Deck-/Sammlungsmenü der Mod wählen, auch in den Kampfeinstellungen. Ein Wechsel erfordert keine Neuinstallation. Automatisch folgt getrennt den aktuellen Text- und Spracheinstellungen des Spiels; fehlt eine Sprache, wird Englisch verwendet. Speichere danach regulär: Die Auswahl gehört zum Spielstand und bleibt beim Austausch der Mod-Dateien erhalten. Eine alte manuelle Textauswahl bleibt bestehen. Einige Fass-Troll-Zeilen in DE/IT behalten die russische Ersatzaufnahme. Native Gegenstandsnamen folgen der Spielsprache; manche Meldungen außerhalb der Mod-Oberfläche bleiben RU/EN.

## Installation

1. Schließe das Spiel und sichere die Spielstände. Lade das Paket für 1.32 oder Next-Gen (5.0+) herunter. Installiere nur eine Beta-Gwent-Version.

2. Verschiebe beim Update zuerst den bisherigen Beta-Gwent-Modordner aus Mods heraus. Entferne nicht den gesamten Mods-Ordner und mische keine Versionsdateien.

3. Mods aus dem Archiv ins Spielverzeichnis neben bin und content kopieren. Für Classic 1.32 auch den enthaltenen DLC-Ordner kopieren. Pfade: Mods/modBetaGwentClassic132/content und DLC/dlcBetaGwentClassic132Assets für 1.32; Mods/modBetaGwent0924/content für Next-Gen. Nur die bisherigen Ordner dieser Mod ersetzen; andere Mods und DLC behalten.

4. Lade deinen Spielstand. Das normale Gwint-Deckmenü öffnet den Editor und die Sprachauswahl; bei Gwint-NPCs startest du Partien. Speichere regulär, um die Auswahl zu behalten.

## Classic 1.32: Größe und DLC

Classic benötigt etwa 623 MB, Next-Gen 448 MB bei denselben Karten und Regeln. Das alte Ressourcenformat und die Grenze von etwa 32 MiB pro asynchron geladener Ressource erfordern getrennte Grafikseiten. Für Classic beide Ordner Mods und DLC installieren: DLC/dlcBetaGwentClassic132Assets enthält notwendige Grafik und deren Registrierung, keine neue Handlung. Etwa 105 MB des Downloads entfallen darauf; der Rest des Größenunterschieds entsteht durch die Aufbereitung für die alte Engine.

## Voraussetzungen

The Witcher 3 auf PC. Wähle den separaten Build für Classic 1.32 oder Next-Gen (Paketbezeichnung 5.0+). REDkit, Wwise und ein EXE-Installationsprogramm werden zum Spielen nicht benötigt.

## Kompatibilität

Definitionen alter Redux-Gegenstände sind zum Laden von Spielständen integriert; den veralteten Ordner modBetaGwentReduxCompat entfernen. Beim Wechsel von Redux eine Sicherung vor dem Inventar-/Körperverlust laden: verlorene Daten lassen sich damit nicht wiederherstellen. Redux-Karten werden nicht in die Beta-Sammlung umgewandelt; eine umfassende Kompatibilität mit Redux/Redo Expansion wird nicht zugesichert. Andere Gwent-Überarbeitungen und Änderungen an Menüs, Handel oder Belohnungen können kollidieren. Konfliktbehaftete Skripte nach Änderungen erneut mit Script Merger zusammenführen.

## Redux

Von 400 geprüften alten Gegenstandsnamen behalten 197 ihre nativen Definitionen; 203 fehlende erhalten in normalen Spielen und NG+ inerte Definitionen. Sie sind unsichtbar, gewichtlos und wertlos. Bereits verlorenes Inventar wird nicht zurückgeholt. Beim Entfernen braucht verbleibendes Redux-Inventar wieder den ursprünglichen Anbieter seiner Definitionen.

## Integrierte Bereinigung vor dem Entfernen

Kein separater Cleaner nötig. Spielstand sichern, Partie beenden, Kampf und Menüs verlassen. bg_clean_preview() zeigt nur Hinweise. Mit installiertem Hauptmod ausdrücklich bestätigen:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

Sammlung, Decks, Ressourcen, Einstellungen, bekannte Belohnungen, Sicherungsspiegel und betagwent_*-Gegenstände im Spielerinventar werden gelöscht. Eine gespeicherte Sperre verhindert die Wiederherstellung, auch nach erneutem Laden. In NEUEM Slot speichern, Spiel beenden, Mod samt Classic-DLC entfernen, Script Merger aktualisieren, neuen Slot laden und erneut speichern. Quests, Erfolge und ausgegebene Kronen bleiben. Unbeladene Händler, Lager und Weltbehälter werden nicht durchsucht. Für verwaiste Belohnungsfakten stehen save_fact_index.py und bg_clean_keys('…') nach Bestätigung bereit. Eine vollständige physische Löschung jeder historischen Speicherstelle wird nicht zugesichert. Lassen sich einige Beta-Gegenstände nicht entfernen, erscheint INCOMPLETE statt der Erfolgsmeldung: diese wegwerfen oder verkaufen und den Befehl wiederholen. Beim Deinstallieren auch die Optional-CopyButton-Dateien löschen, falls installiert: bin\…\plugins\GwentBetaClipboard.asi und die dinput8.dll dieses Mods (nicht die eines anderen).

## Bis 1.0

Bis 1.0 stehen Übersetzungen und Fehlerkorrekturen sowie weitere KI- und Oberflächenverbesserungen im Mittelpunkt. Automatische Tests ersetzen keine Prüfung im Spiel oder einen echten Speicher-/Ladedurchlauf nach der Bereinigung.

## Fehlermeldungen

Problem gefunden? Nenne Mod-Version, genaue Spielversion, gewählte Textsprache und Sprachausgabe (auch Automatisch), Neues Spiel +, weitere Mods, Karten/Anführer und Schritte zum Nachstellen. Screenshot und Spielstand vor dem Fehler helfen. Bei Übersetzungsfehlern bitte Sprache, Bildschirm und eine bessere Formulierung angeben.

### Protokoll aktivieren

1. Füge -debugscripts hinter dem schließenden Anführungszeichen im Ziel eines direkten witcher3.exe-Shortcuts hinzu. Steam: Eigenschaften → Allgemein → Startoptionen. Bei GOG funktioniert ein direkter Shortcut zu witcher3.exe.

2. Starte das Spiel, stelle den Fehler nach und beende es. Kopiere scriptslog.txt sofort: Der nächste Start überschreibt die Datei. Enthält sie nur eine Kopfzeile, melde das; zusätzliche Protokolleinstellungen können nötig sein.

3. Falls Windows einen Absturzbericht erstellt hat, füge die passende neueste .dmp-Datei bei.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Danksagung

Danke an CD Projekt für The Witcher und Gwent, an LegacyGwent DIY für Karten- und Spielbrettmaterial, an die Beta-Gwent-Community für bewahrtes Material und Archetyp-Ideen und an alle, die die Mod testen und ausführliche Berichte schicken.

Inoffizielles Fanprojekt. Der eigene Code der Mod steht unter GPL-3.0-only; die Originalinhalte des Spiels gehören ihren Rechteinhabern.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)
