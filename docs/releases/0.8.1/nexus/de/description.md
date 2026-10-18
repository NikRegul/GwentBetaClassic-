# Gwent Beta Classic 0.8.1 — Deutsch

> Version 0.8.1 für Next-Gen 5.0+ wurde im Spiel getestet. Classic 1.32 wird separat korrigiert und geprüft; das aktuelle Archiv ist eine Testversion.

## Wichtig

Sichere vor der Installation und vor jedem Update deine Spielstände. Die Mod befindet sich in aktiver Entwicklung, nutze für die ersten Partien einen separaten Spielstand.

Die Übersetzungen sind weiterhin eine Vorschau: Die Kartentexte stammen aus der offiziellen Lokalisierung der Beta, die Oberfläche wurde mit KI übersetzt und kann Fehler enthalten. Neue Hinweise seit 0.6.6 gibt es vorerst nur auf Englisch und Russisch; in den anderen Sprachen erscheinen sie auf Englisch. Bitte melde alles, was falsch klingt.

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

## Änderungen seit 0.7.3a

- Jedes Plattformpaket enthält alle fünf Sprachausgaben und alle 13 Textsprachen. Separate Downloads nach Sprachausgabe entfallen.
- Zwei benachbarte Schaltflächen für Text und Sprachausgabe im Mod-Menü, jeweils mit automatischer oder manueller Auswahl.
- Die automatische Erkennung liest Text- und Sprachsprache unabhängig voneinander. Nicht unterstützte Sprachen verwenden Englisch.
- Die Auswahl wird im Spielstand gespeichert. Eine bisher manuell gewählte Textsprache bleibt beim Update erhalten.
- Fassdefinitionen und Wiederherstellung des Vorrats in Neues Spiel + korrigiert. Fehlgeschlagene Vergaben gelten nicht mehr als abgeschlossen; verkaufte Fässer werden nicht bei jedem Ladenbesuch aufgefüllt.
- Überarbeitete Effekte für Jotunns drei Geschosse, Kambi/Hemdall, Ragh Nar Roog, Golden Froth, Statusänderungen, Timer und Rüstung.
- Oberflächenressourcen ohne geringere Texturauflösung für das Build-Budget von 63 MiB neu gepackt. Menüstart und Stabilität bleiben Teil der Abnahme.

## Sprachen

Text: Englisch, Russisch, Deutsch, Französisch, Italienisch, Polnisch, Spanisch (Spanien), Spanisch (Lateinamerika), Portugiesisch (Brasilien), Japanisch, Koreanisch, vereinfachtes und traditionelles Chinesisch. Jederzeit umschaltbar über die Textsprache-Schaltfläche oben links in den Deck- und Sammlungsmenüs oder in den Kampfeinstellungen; die Wahl wird gespeichert.

Jedes Paket enthält RU, EN, DE, IT und PT-BR. Text und Stimmen lassen sich unabhängig über zwei benachbarte Schaltflächen im Deck-/Sammlungsmenü der Mod wählen, auch in den Kampfeinstellungen. Ein Wechsel erfordert keine Neuinstallation. Automatisch folgt getrennt den aktuellen Text- und Spracheinstellungen des Spiels; fehlt eine Sprache, wird Englisch verwendet. Speichere danach regulär: Die Auswahl gehört zum Spielstand und bleibt beim Austausch der Mod-Dateien erhalten. Eine alte manuelle Textauswahl bleibt bestehen. Einige Fass-Troll-Zeilen in DE/IT behalten die russische Ersatzaufnahme. Native Gegenstandsnamen folgen der Spielsprache; manche Meldungen außerhalb der Mod-Oberfläche bleiben RU/EN.

## Installation

1. Schließe das Spiel und sichere die Spielstände. Lade das Paket für 1.32 oder Next-Gen (5.0+) herunter. Installiere nur eine Beta-Gwent-Version.

2. Verschiebe beim Update zuerst den bisherigen Beta-Gwent-Modordner aus Mods heraus. Entferne nicht den gesamten Mods-Ordner und mische keine Versionsdateien.

3. Kopiere Mods aus dem Archiv in den Spielordner neben bin und content. Ziel: Mods/modBetaGwentClassic132/content für 1.32, Mods/modBetaGwent0924/content für Next-Gen.

4. Lade deinen Spielstand. Das normale Gwint-Deckmenü öffnet den Editor und die Sprachauswahl; bei Gwint-NPCs startest du Partien. Speichere regulär, um die Auswahl zu behalten.

## Voraussetzungen

The Witcher 3 auf PC. Wähle den separaten Build für Classic 1.32 oder Next-Gen (Paketbezeichnung 5.0+). REDkit, Wwise und ein EXE-Installationsprogramm werden zum Spielen nicht benötigt.

## Kompatibilität

Entferne den veralteten Ordner modBetaGwentReduxCompat; die separate Kompatibilitätsschicht ist nicht mehr enthalten. Die Kompatibilität mit Redux/Redo Expansion wurde nicht separat bestätigt. Andere Gwint-Überarbeitungen und Mods für Gwint-Menüs, Kartenhandel oder Belohnungen können Konflikte verursachen. Führe nach Änderungen an der Mod-Auswahl die Skriptzusammenführung in Script Merger erneut aus.

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
