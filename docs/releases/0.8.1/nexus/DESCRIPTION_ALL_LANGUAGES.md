# Gwent Beta Classic 0.8.1 — English

> Version 0.8.1 for Next-Gen 5.0+ has been tested in-game. Classic 1.32 is being fixed and tested separately; its current archive is a test candidate.

## Important

Back up your saves before installing and before every update. The mod is in active development, so use a separate save for your first matches.

Translations are still a preview: card texts come from the official Beta localization, while the interface was translated with AI and may contain mistakes. New hints added since 0.6.6 exist only in English and Russian for now; other languages show them in English. Please report anything that reads wrong.

## About the mod

Gwent Beta Classic replaces vanilla Gwent in The Witcher 3 with the cards, rules and board of standalone Gwent Beta 0.9.24. Matches stay part of the Witcher world: play against NPCs, finish quests, buy kegs and build your own decks.

## Features

- 479 collectible cards, including 21 leaders, across all five factions
- Beta board, HUD, fonts, card frames, weather and effects; animated leaders
- Deck builder: five editable starter decks plus eight custom slots, filters and search
- Opponents with 46 Beta deck archetypes and three AI difficulty levels
- Kegs for 200 crowns from every innkeeper, opened Beta-style
- Scraps: craft cards for 30 / 80 / 200 / 800 by rarity; extra copies are milled automatically
- Tutorial, mulligan, graveyard and deck viewers, full card inspection
- Mouse, keyboard and controller support

## Changes since 0.7.3a

- All five voice languages and all 13 text languages are included in each platform package. Voice-only downloads are no longer needed.
- Separate adjacent Text and Voice buttons in the mod menu. Both settings can follow the game automatically or be selected manually.
- Automatic detection reads text and speech independently. Unsupported speech languages use English; unsupported text also uses English.
- Language preferences are stored with the game save. Existing manual text choices are retained when upgrading.
- Fixed keg definitions and stock recovery for New Game+. A failed item grant is no longer marked as completed, and sold stock is not refilled whenever the shop opens.
- Updated Jotunn's three projectiles, Kambi/Hemdall destruction, Ragh Nar Roog impacts, Golden Froth, status changes, timers and armour effects.
- Repacked interface resources to stay within the 63 MiB build budget without reducing texture resolution. Menu startup and stability remain part of the release checks.

## Languages

Text: English, Russian, German, French, Italian, Polish, Spanish (Spain), Spanish (Latin America), Portuguese (Brazil), Japanese, Korean, Simplified Chinese and Traditional Chinese. Switch any time with the text language button at the top left of the deck and collection menus or in the battle settings; your choice is saved.

Each package includes RU, EN, DE, IT and PT-BR voices. Select Text and Voice independently using the two adjacent buttons in the mod's deck/collection menu; the choices are also available in the match settings. Switching voices does not require reinstalling files. Auto follows the game's current text and speech languages separately; if a language is unavailable, English is used. Save the game normally after choosing: preferences belong to that save and remain when the mod files are updated. An existing manual text choice is preserved. In DE and IT, some keg-troll lines retain the Russian fallback from the source recordings. Native item names still follow the game language, and some notifications outside the mod UI remain RU/EN.

## Installation

1. Close the game and back up your saves. Download the package for your game branch: 1.32 or Next-Gen (5.0+). Install only one Beta Gwent version.

2. When updating, move the previous Beta Gwent mod folder outside Mods first. Do not remove the entire Mods folder or mix files from different versions.

3. Copy the archive's Mods folder into the game directory, next to bin and content. The resulting path is Mods/modBetaGwentClassic132/content for 1.32, or Mods/modBetaGwent0924/content for Next-Gen.

4. Load your save. Open the normal Gwent deck menu to edit decks and choose text/voices, or talk to a Gwent-playing NPC to start a match. Save normally to retain your preferences.

## Requirements

The Witcher 3 on PC. Choose the separate build for Classic 1.32 or Next-Gen (package labelled 5.0+). REDkit, Wwise and an EXE installer are not needed to play.

## Compatibility

Remove the obsolete modBetaGwentReduxCompat folder; the separate compatibility layer is no longer included. Compatibility with Redux/Redo Expansion has not been separately confirmed. Other Gwent overhauls and mods changing its menus, card trading or rewards may conflict. After changing your mod setup, merge scripts again with Script Merger.

## Bug reports

Found a problem? Please include the mod and exact game versions, selected text and voice languages (including Auto), whether this is New Game+, other mods, the cards/leaders and steps to reproduce. A screenshot and a save from before the problem are helpful. For a translation issue, name the language and screen and suggest a better wording.

### How to enable the log

1. Add -debugscripts after the closing quote in the shortcut target for the actual witcher3.exe. In Steam, use Properties → General → Launch Options. For GOG you can use a direct shortcut to witcher3.exe.

2. Start the game, reproduce the problem and close it. Copy scriptslog.txt immediately: the next launch overwrites it. If it contains only a header, mention that; extra logging configuration may be needed for that build.

3. If Windows created a crash dump, attach the latest relevant .dmp as well.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Credits

Thanks to CD Projekt for The Witcher and Gwent, LegacyGwent DIY for card and board assets, the Beta Gwent community for preserving historical material and archetype ideas, and everyone who tests the mod and sends detailed reports.

Unofficial fan project. Original mod code is GPL-3.0-only; original game assets belong to their owners.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)


---

# Gwent Beta Classic 0.8.1 — Русский

> Версия 0.8.1 для Next-Gen 5.0+ проверена в игре. Classic 1.32 исправляется и проверяется отдельно; её текущий архив предназначен для тестирования.

## Важно

Перед установкой и перед каждым обновлением делайте резервную копию сохранений. Мод в активной разработке, для первых партий используйте отдельное сохранение.

Переводы по-прежнему пробные: тексты карт взяты из официальной локализации беты, интерфейс переведён ИИ и может содержать ошибки. Новые подсказки, добавленные начиная с 0.6.6, пока есть только на русском и английском; в остальных языках они показываются по-английски. Пожалуйста, сообщайте обо всём, что звучит неправильно.

## О моде

Gwent Beta Classic заменяет встроенный гвинт в The Witcher 3 картами, правилами и полем самостоятельного Gwent Beta 0.9.24. Партии остаются частью мира Ведьмака: играйте с NPC, проходите квесты, покупайте бочки и собирайте свои колоды.

## Возможности

- 479 коллекционных карт, включая 21 лидера, все пять фракций
- Поле, интерфейс, шрифты, рамки карт, погода и эффекты беты; анимированные лидеры
- Редактор колод: пять стартовых колод, которые можно менять, и восемь своих слотов, фильтры и поиск
- Соперники с 46 архетипами колод беты и три уровня сложности ИИ
- Бочки за 200 крон у всех корчмарей, открываются как в бете
- Осколки: создание карт за 30 / 80 / 200 / 800 по редкости; лишние копии распыляются сами
- Обучение, замена карт, просмотр сбросов и колоды, подробный просмотр карт
- Мышь, клавиатура и контроллер

## Изменения после 0.7.3a

- В каждом платформенном пакете теперь все пять озвучек и все 13 языков текста. Отдельные загрузки по языкам голосов больше не нужны.
- В меню мода рядом расположены отдельные кнопки «Текст» и «Озвучка». Для каждой настройки доступны автоматический и ручной выбор.
- Автоопределение независимо получает язык текста и речи игры. Для неподдерживаемой озвучки используется английская; для неподдерживаемого текста — английский.
- Языковые настройки хранятся в игровом сохранении. При обновлении сохраняется прежний ручной выбор текста.
- Исправлены определения бочек и восстановление запаса в НГ+. Неудачная выдача предмета больше не считается выполненной; проданный запас не восстанавливается при каждом открытии магазина.
- Доработаны три снаряда Йотуна, уничтожение карт Камби/Хеймдаллем, попадания Рагнарёка, Golden Froth, статусы, таймеры и эффекты брони.
- Ресурсы интерфейса перепакованы в пределах бюджета сборки 63 МиБ без уменьшения разрешения текстур. Загрузка меню и стабильность остаются частью релизной проверки.

## Языки

Текст: английский, русский, немецкий, французский, итальянский, польский, испанский (Испания), испанский (Латинская Америка), португальский (Бразилия), японский, корейский, упрощённый и традиционный китайский. Язык меняется в любой момент кнопкой языка текста в левом верхнем углу меню колод и коллекции или в настройках боя; выбор сохраняется.

В каждом пакете есть озвучки RU, EN, DE, IT и PT-BR. Текст и голоса выбираются независимо двумя соседними кнопками в меню колод/коллекции мода; настройки также доступны в меню партии. Для смены голоса переустановка не нужна. «Авто» отдельно следует текущим языкам текста и речи игры; если язык не поддерживается, используется английский. После выбора штатно сохраните игру: настройки принадлежат этому сохранению и остаются при обновлении файлов мода. Старый ручной язык текста сохраняется. В DE и IT некоторые реплики тролля у бочек используют прежний русский резервный вариант исходных записей. Нативные названия предметов зависят от языка игры, часть уведомлений вне интерфейса мода остаётся на RU/EN.

## Установка

1. Закройте игру и сделайте резервную копию сохранений. Скачайте пакет для своей ветки: 1.32 или Next-Gen (5.0+). Устанавливайте только одну версию Beta Gwent.

2. При обновлении сначала перенесите прежнюю папку мода Beta Gwent за пределы Mods. Не удаляйте всю папку Mods и не смешивайте файлы разных версий.

3. Скопируйте папку Mods из архива в корень игры, рядом с bin и content. Итоговый путь для 1.32 — Mods/modBetaGwentClassic132/content, для Next-Gen — Mods/modBetaGwent0924/content.

4. Загрузите сохранение. Обычное меню колоды гвинта открывает редактор и выбор текста/озвучки; разговор с играющим NPC запускает партию. Для сохранения настроек штатно сохраните игру.

## Требования

The Witcher 3 на PC. Выберите отдельную сборку для Classic 1.32 или Next-Gen (пакет с обозначением 5.0+). Для игры не нужны REDkit, Wwise и установщик EXE.

## Совместимость

Удалите устаревшую папку modBetaGwentReduxCompat: отдельный слой совместимости больше не входит в мод. Совместимость с Redux/Redo Expansion отдельно не подтверждена. Другие переработки гвинта и моды, меняющие его меню, обмен карт или награды, могут конфликтовать. После изменения набора модов заново выполните объединение скриптов в Script Merger.

## Сообщения об ошибках

Есть проблема? Укажите версии мода и самой игры, выбранные текст и озвучку (в том числе режим «Авто»), обычное прохождение или НГ+, другие моды, карты/лидеров и шаги повторения. Помогут скриншот и сохранение перед ошибкой. Для замечания по переводу укажите язык и экран, предложите лучший вариант.

### Как включить лог

1. Добавьте -debugscripts после закрывающей кавычки в поле «Объект» ярлыка самого witcher3.exe. В Steam: Свойства → Общие → Параметры запуска. Для GOG можно использовать прямой ярлык witcher3.exe.

2. Запустите игру, повторите ошибку и закройте её. Сразу скопируйте scriptslog.txt: следующий запуск перезапишет файл. Если в нём только заголовок, сообщите об этом — для этой сборки может потребоваться дополнительная настройка логирования.

3. Если Windows создала дамп падения, приложите также последний относящийся к ошибке файл .dmp.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Благодарности

Спасибо CD Projekt за The Witcher и Gwent, LegacyGwent DIY за материалы карт и поля, сообществу Beta Gwent за сохранённые материалы и идеи архетипов, и всем, кто тестирует мод и присылает подробные отчёты.

Неофициальный фанатский проект. Авторский код мода распространяется по GPL-3.0-only; оригинальные игровые материалы принадлежат их владельцам.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)


---

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


---

# Gwent Beta Classic 0.8.1 — Français

> La version 0.8.1 pour Next-Gen 5.0+ a été testée en jeu. Classic 1.32 est corrigée et testée séparément ; son archive actuelle est une version de test.

## Important

Sauvegardez vos parties avant l'installation et avant chaque mise à jour. Le mod est en développement actif : utilisez une sauvegarde séparée pour vos premières parties.

Les traductions restent une préversion : les textes des cartes proviennent de la localisation officielle de la bêta, l'interface a été traduite par IA et peut contenir des erreurs. Les nouvelles indications ajoutées depuis la 0.6.6 n'existent pour l'instant qu'en anglais et en russe ; les autres langues les affichent en anglais. Signalez tout ce qui sonne faux.

## À propos

Gwent Beta Classic remplace le Gwynt de The Witcher 3 par les cartes, les règles et le plateau de Gwent Beta 0.9.24 autonome. Les parties restent intégrées au monde du Sorceleur : affrontez des PNJ, accomplissez des quêtes, achetez des tonneaux et construisez vos decks.

## Fonctionnalités

- 479 cartes à collectionner, dont 21 chefs, pour les cinq factions
- Plateau, interface, polices, cadres de cartes, météo et effets de la bêta ; chefs animés
- Éditeur de decks : cinq decks de départ modifiables et huit emplacements personnels, filtres et recherche
- Adversaires avec 46 archétypes de decks de la bêta et trois niveaux de difficulté de l'IA
- Tonneaux à 200 couronnes chez tous les aubergistes, ouverts comme dans la bêta
- Fragments : fabriquez des cartes pour 30 / 80 / 200 / 800 selon la rareté ; les exemplaires en trop sont recyclés automatiquement
- Tutoriel, mulligan, consultation des cimetières et du deck, fiche détaillée des cartes
- Souris, clavier et manette

## Changements depuis la 0.7.3a

- Chaque paquet contient les cinq doublages et les 13 langues de texte. Les téléchargements séparés par doublage ne sont plus nécessaires.
- Deux boutons voisins, Texte et Voix, dans le menu du mod, avec sélection automatique ou manuelle indépendante.
- Détection distincte des langues du texte et des voix du jeu. Une langue non prise en charge utilise l’anglais.
- Les préférences sont enregistrées dans la sauvegarde. L’ancienne sélection manuelle du texte est conservée après mise à jour.
- Définitions des tonneaux et récupération du stock corrigées en Nouvelle partie +. Un ajout échoué n’est plus marqué comme terminé ; le stock vendu ne revient pas à chaque ouverture de la boutique.
- Effets retravaillés pour les trois projectiles de Jotunn, Kambi/Hemdall, Ragh Nar Roog, Golden Froth, les statuts, les compteurs et l’armure.
- Ressources de l’interface réorganisées pour respecter le budget de compilation de 63 Mio sans réduire la résolution des textures. Le chargement des menus et la stabilité restent à valider.

## Langues

Texte : anglais, russe, allemand, français, italien, polonais, espagnol (Espagne), espagnol (Amérique latine), portugais (Brésil), japonais, coréen, chinois simplifié et chinois traditionnel. Changez-la à tout moment avec le bouton de langue du texte en haut à gauche des menus des decks et de la collection, ou dans les paramètres de combat ; le choix est enregistré.

Chaque paquet comprend les voix RU, EN, DE, IT et PT-BR. Choisissez séparément texte et voix avec deux boutons voisins dans le menu des decks/de la collection du mod, ou dans les paramètres de combat. Changer de voix ne demande aucune réinstallation. Automatique suit séparément les langues actuelles du texte et des voix du jeu ; si une langue manque, l’anglais est utilisé. Sauvegardez normalement après le choix : les préférences appartiennent à cette sauvegarde et restent après mise à jour des fichiers. L’ancien choix manuel du texte est conservé. Certaines répliques du troll des tonneaux en DE/IT gardent leur remplacement russe d’origine. Les noms natifs des objets suivent la langue du jeu ; certaines notifications hors de l’interface restent RU/EN.

## Installation

1. Fermez le jeu et sauvegardez vos parties. Téléchargez le paquet pour 1.32 ou Next-Gen (5.0+). N’installez qu’une version de Beta Gwent.

2. Pour une mise à jour, déplacez d’abord l’ancien dossier Beta Gwent hors de Mods. Ne supprimez pas tout le dossier Mods et ne mélangez pas les versions.

3. Copiez Mods depuis l’archive dans le dossier du jeu, à côté de bin et content. Chemin final : Mods/modBetaGwentClassic132/content pour 1.32, Mods/modBetaGwent0924/content pour Next-Gen.

4. Chargez une sauvegarde. Le menu habituel des decks de Gwynt ouvre l’éditeur et les langues ; parlez à un PNJ joueur pour lancer une partie. Sauvegardez normalement pour conserver vos choix.

## Configuration requise

The Witcher 3 sur PC. Choisissez la version distincte pour Classic 1.32 ou Next-Gen (paquet nommé 5.0+). REDkit, Wwise et un installateur EXE ne sont pas nécessaires pour jouer.

## Compatibilité

Supprimez l'ancien dossier modBetaGwentReduxCompat : la couche de compatibilité séparée n'est plus incluse. La compatibilité avec Redux/Redo Expansion n'a pas été confirmée séparément. Les autres refontes du Gwynt et les mods touchant ses menus, les échanges de cartes ou les récompenses peuvent entrer en conflit. Après avoir modifié vos mods, refaites la fusion des scripts avec Script Merger.

## Signaler un bug

Un problème ? Indiquez les versions du mod et du jeu, les langues choisies pour texte et voix (y compris Automatique), Nouvelle partie + ou non, les autres mods, les cartes/chefs et les étapes de reproduction. Une capture et une sauvegarde avant le problème sont utiles. Pour une traduction, précisez langue et écran et proposez une meilleure formulation.

### Activer le journal

1. Ajoutez -debugscripts après le guillemet fermant de la cible d’un raccourci vers witcher3.exe. Steam : Propriétés → Général → Options de lancement. Pour GOG, utilisez un raccourci direct vers witcher3.exe.

2. Lancez le jeu, reproduisez le problème puis fermez-le. Copiez immédiatement scriptslog.txt : le lancement suivant l’écrase. S’il ne contient qu’un en-tête, signalez-le ; une configuration supplémentaire peut être nécessaire.

3. Si Windows a créé un fichier de crash, joignez aussi le dernier .dmp correspondant.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Remerciements

Merci à CD Projekt pour The Witcher et Gwent, à LegacyGwent DIY pour les ressources des cartes et du plateau, à la communauté Beta Gwent pour la préservation des archives et les idées d'archétypes, et à tous ceux qui testent le mod et envoient des rapports détaillés.

Projet de fan non officiel. Le code original du mod est sous licence GPL-3.0-only ; les contenus originaux du jeu appartiennent à leurs propriétaires.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)


---

# Gwent Beta Classic 0.8.1 — Italiano

> La versione 0.8.1 per Next-Gen 5.0+ è stata provata nel gioco. Classic 1.32 viene corretta e verificata separatamente; l’archivio attuale è una versione di prova.

## Importante

Esegui un backup dei salvataggi prima dell'installazione e prima di ogni aggiornamento. La mod è in sviluppo attivo: per le prime partite usa un salvataggio separato.

Le traduzioni restano un'anteprima: i testi delle carte provengono dalla localizzazione ufficiale della beta, l'interfaccia è stata tradotta con IA e può contenere errori. I nuovi suggerimenti aggiunti dalla 0.6.6 esistono per ora solo in inglese e russo; nelle altre lingue compaiono in inglese. Segnala tutto ciò che suona sbagliato.

## La mod

Gwent Beta Classic sostituisce il Gwent di The Witcher 3 con le carte, le regole e il tabellone di Gwent Beta 0.9.24 standalone. Le partite restano parte del mondo di The Witcher: sfida i PNG, completa missioni, compra barili e costruisci i tuoi mazzi.

## Caratteristiche

- 479 carte collezionabili, tra cui 21 comandanti, per tutte e cinque le fazioni
- Tabellone, interfaccia, caratteri, cornici delle carte, clima ed effetti della beta; comandanti animati
- Editor dei mazzi: cinque mazzi iniziali modificabili e otto slot personali, filtri e ricerca
- Avversari con 46 archetipi di mazzi della beta e tre livelli di difficoltà dell'IA
- Barili da 200 corone da tutti i locandieri, aperti come nella beta
- Frammenti: crea carte per 30 / 80 / 200 / 800 in base alla rarità; le copie in eccesso vengono macinate automaticamente
- Tutorial, mulligan, visualizzazione dei cimiteri e del mazzo, scheda dettagliata delle carte
- Mouse, tastiera e controller

## Novità dalla 0.7.3a

- Ogni pacchetto include tutti e cinque i doppiaggi e tutte le 13 lingue del testo. Non servono più download separati per le voci.
- Due pulsanti affiancati, Testo e Voci, nel menu della mod, con scelta automatica o manuale indipendente.
- Rilevamento separato delle lingue del testo e del parlato del gioco. Le lingue non supportate usano l’inglese.
- Preferenze salvate nella partita. La precedente scelta manuale del testo rimane dopo l’aggiornamento.
- Corretti definizioni dei barili e recupero delle scorte in Nuova partita +. Un’aggiunta fallita non risulta completata; le scorte vendute non si ripristinano a ogni apertura del negozio.
- Rivisti i tre proiettili di Jotunn, Kambi/Hemdall, Ragh Nar Roog, Golden Froth, stati, timer ed effetti dell’armatura.
- Risorse dell’interfaccia riorganizzate entro il budget di 63 MiB senza ridurre la risoluzione delle texture. Avvio dei menu e stabilità restano da verificare.

## Lingue

Testo: inglese, russo, tedesco, francese, italiano, polacco, spagnolo (Spagna), spagnolo (America Latina), portoghese (Brasile), giapponese, coreano, cinese semplificato e cinese tradizionale. Cambiala in qualsiasi momento con il pulsante della lingua del testo in alto a sinistra nei menu dei mazzi e della collezione, oppure nelle impostazioni di battaglia; la scelta viene salvata.

Ogni pacchetto contiene le voci RU, EN, DE, IT e PT-BR. Testo e voci si scelgono separatamente con due pulsanti affiancati nel menu dei mazzi/della collezione della mod o nelle impostazioni della partita. Non serve reinstallare per cambiare voci. Automatico segue separatamente le lingue attuali del testo e del parlato del gioco; se una lingua manca, usa l’inglese. Salva normalmente dopo la scelta: le preferenze appartengono al salvataggio e restano aggiornando i file della mod. La vecchia scelta manuale del testo viene mantenuta. Alcune battute del troll dei barili in DE/IT mantengono il russo sostitutivo delle registrazioni originali. I nomi nativi degli oggetti seguono la lingua del gioco; alcune notifiche esterne restano RU/EN.

## Installazione

1. Chiudi il gioco e fai un backup dei salvataggi. Scarica il pacchetto per 1.32 o Next-Gen (5.0+). Installa una sola versione di Beta Gwent.

2. Per aggiornare, sposta prima la vecchia cartella della mod Beta Gwent fuori da Mods. Non eliminare tutta Mods e non mescolare versioni diverse.

3. Copia Mods dall’archivio nella cartella del gioco, accanto a bin e content. Percorso finale: Mods/modBetaGwentClassic132/content per 1.32, Mods/modBetaGwent0924/content per Next-Gen.

4. Carica un salvataggio. Il normale menu dei mazzi di Gwent apre editor e scelta delle lingue; parla con un PNG che gioca per iniziare una partita. Salva normalmente per mantenere le preferenze.

## Requisiti

The Witcher 3 su PC. Scegli la build separata per Classic 1.32 o Next-Gen (pacchetto indicato come 5.0+). Per giocare non servono REDkit, Wwise o un programma d’installazione EXE.

## Compatibilità

Elimina la vecchia cartella modBetaGwentReduxCompat: il livello di compatibilità separato non è più incluso. La compatibilità con Redux/Redo Expansion non è stata confermata separatamente. Altre revisioni di Gwent e mod che cambiano menu, scambi di carte o ricompense possono causare conflitti. Dopo aver cambiato le mod installate, ripeti l'unione degli script con Script Merger.

## Segnalazione bug

Hai trovato un problema? Indica versioni di mod e gioco, lingue scelte per testo e voci (anche Automatico), uso di Nuova partita +, altre mod, carte/leader e passaggi per riprodurlo. Sono utili uno screenshot e un salvataggio precedente al problema. Per le traduzioni indica lingua e schermata e proponi una formulazione migliore.

### Come attivare il log

1. Aggiungi -debugscripts dopo le virgolette finali nella destinazione di un collegamento a witcher3.exe. Steam: Proprietà → Generali → Opzioni di avvio. Con GOG puoi usare un collegamento diretto a witcher3.exe.

2. Avvia il gioco, riproduci il problema e chiudilo. Copia subito scriptslog.txt: l’avvio successivo lo sovrascrive. Se contiene solo l’intestazione, segnalalo; potrebbe servire una configurazione aggiuntiva.

3. Se Windows ha creato un dump dell’arresto, allega anche l’ultimo .dmp pertinente.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Ringraziamenti

Grazie a CD Projekt per The Witcher e Gwent, a LegacyGwent DIY per le risorse di carte e tabellone, alla community di Beta Gwent per aver conservato il materiale storico e le idee per gli archetipi, e a tutti coloro che testano la mod e inviano segnalazioni dettagliate.

Progetto amatoriale non ufficiale. Il codice originale della mod è distribuito con licenza GPL-3.0-only; i contenuti originali del gioco appartengono ai rispettivi proprietari.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)


---

# Gwent Beta Classic 0.8.1 — Polski

> Wersja 0.8.1 dla Next-Gen 5.0+ została przetestowana w grze. Classic 1.32 jest poprawiana i sprawdzana osobno; obecne archiwum jest wersją testową.

## Ważne

Przed instalacją i przed każdą aktualizacją zrób kopię zapasową zapisów. Mod jest w aktywnym rozwoju, więc do pierwszych partii użyj osobnego zapisu.

Tłumaczenia nadal są wersją testową: teksty kart pochodzą z oficjalnej lokalizacji bety, a interfejs przetłumaczono za pomocą AI i może zawierać błędy. Nowe podpowiedzi dodane od wersji 0.6.6 są na razie tylko po angielsku i rosyjsku; w pozostałych językach wyświetlają się po angielsku. Zgłaszaj wszystko, co brzmi źle.

## O modzie

Gwent Beta Classic zastępuje gwinta z Wiedźmina 3 kartami, zasadami i planszą samodzielnej wersji Gwent Beta 0.9.24. Partie pozostają częścią świata Wiedźmina: graj z NPC, wykonuj zadania, kupuj beczki i buduj własne talie.

## Funkcje

- 479 kart kolekcjonerskich, w tym 21 dowódców, wszystkie pięć frakcji
- Plansza, interfejs, czcionki, ramki kart, pogoda i efekty z bety; animowani dowódcy
- Edytor talii: pięć edytowalnych talii startowych i osiem własnych miejsc, filtry i wyszukiwanie
- Przeciwnicy z 46 archetypami talii z bety i trzy poziomy trudności SI
- Beczki za 200 koron u wszystkich karczmarzy, otwierane jak w becie
- Skrawki: twórz karty za 30 / 80 / 200 / 800 zależnie od rzadkości; nadmiarowe kopie są mielone automatycznie
- Samouczek, mulligan, podgląd cmentarzy i talii, szczegółowy podgląd kart
- Mysz, klawiatura i kontroler

## Zmiany od 0.7.3a

- Każdy pakiet zawiera pięć wersji głosowych i wszystkie 13 języków tekstu. Osobne pobieranie według języka głosów nie jest już potrzebne.
- Dwa sąsiednie przyciski Tekst i Głosy w menu moda, z niezależnym wyborem automatycznym lub ręcznym.
- Osobne wykrywanie języka tekstu i mowy gry. Nieobsługiwane języki są zastępowane angielskim.
- Preferencje są przechowywane w zapisie gry. Poprzedni ręczny wybór języka tekstu pozostaje po aktualizacji.
- Poprawiono definicje beczek i odzyskiwanie zapasów w Nowej Grze +. Nieudane dodanie nie jest oznaczane jako wykonane; sprzedane beczki nie wracają przy każdym otwarciu sklepu.
- Dopracowano trzy pociski Jotunna, Kambi/Hemdalla, Ragh Nar Roog, Golden Froth, statusy, liczniki i efekty pancerza.
- Zasoby interfejsu przepakowano do budżetu kompilacji 63 MiB bez obniżania rozdzielczości tekstur. Uruchamianie menu i stabilność nadal podlegają testom.

## Języki

Tekst: angielski, rosyjski, niemiecki, francuski, włoski, polski, hiszpański (Hiszpania), hiszpański (Ameryka Łacińska), portugalski (Brazylia), japoński, koreański, chiński uproszczony i chiński tradycyjny. Język zmienisz w każdej chwili przyciskiem języka tekstu w lewym górnym rogu menu talii i kolekcji lub w ustawieniach bitwy; wybór jest zapisywany.

Każdy pakiet zawiera głosy RU, EN, DE, IT i PT-BR. Tekst i głosy wybierasz niezależnie dwoma sąsiednimi przyciskami w menu talii/kolekcji moda lub w ustawieniach partii. Zmiana nie wymaga ponownej instalacji. Automatycznie śledzi osobno bieżący język tekstu i mowy gry; brakujący język zastępuje angielskim. Po wyborze zapisz grę normalnie: ustawienia należą do tego zapisu i pozostają po aktualizacji plików moda. Poprzedni ręczny wybór tekstu jest zachowany. Niektóre kwestie trolla od beczek w DE/IT zachowują rosyjskie nagranie zastępcze. Natywne nazwy przedmiotów zależą od języka gry; część komunikatów poza interfejsem pozostaje RU/EN.

## Instalacja

1. Zamknij grę i wykonaj kopię zapisów. Pobierz pakiet dla 1.32 lub Next-Gen (5.0+). Instaluj tylko jedną wersję Beta Gwent.

2. Przy aktualizacji najpierw przenieś poprzedni folder moda Beta Gwent poza Mods. Nie usuwaj całego Mods ani nie mieszaj plików wersji.

3. Skopiuj Mods z archiwum do katalogu gry, obok bin i content. Ścieżka docelowa: Mods/modBetaGwentClassic132/content dla 1.32 lub Mods/modBetaGwent0924/content dla Next-Gen.

4. Wczytaj zapis. Zwykłe menu talii Gwinta otwiera edytor i wybór języków; rozmowa z grającym NPC rozpoczyna partię. Zapisz grę, aby zachować wybór.

## Wymagania

The Witcher 3 na PC. Wybierz osobną kompilację Classic 1.32 albo Next-Gen (pakiet oznaczony 5.0+). Do gry nie są potrzebne REDkit, Wwise ani instalator EXE.

## Kompatybilność

Usuń stary folder modBetaGwentReduxCompat: osobna warstwa zgodności nie jest już dołączana. Zgodność z Redux/Redo Expansion nie została osobno potwierdzona. Inne przeróbki gwinta oraz mody zmieniające jego menu, handel kartami lub nagrody mogą powodować konflikty. Po zmianie zestawu modów ponownie scal skrypty w Script Merger.

## Zgłaszanie błędów

Problem? Podaj wersję moda i dokładną wersję gry, wybrany tekst i głosy (także Automatycznie), informację o Nowej Grze +, inne mody, karty/dowódców i kroki odtworzenia. Pomogą zrzut ekranu i zapis sprzed problemu. Przy błędach tłumaczenia podaj język, ekran i propozycję poprawki.

### Włączanie dziennika

1. Dodaj -debugscripts po końcowym cudzysłowie w polu celu skrótu do witcher3.exe. Steam: Właściwości → Ogólne → Opcje uruchamiania. W GOG możesz użyć bezpośredniego skrótu do witcher3.exe.

2. Uruchom grę, odtwórz błąd i zamknij ją. Od razu skopiuj scriptslog.txt: następny start nadpisze plik. Jeśli zawiera tylko nagłówek, zgłoś to; może być potrzebna dodatkowa konfiguracja.

3. Jeżeli Windows utworzył zrzut awarii, dołącz też najnowszy pasujący plik .dmp.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Podziękowania

Dziękujemy CD Projekt za Wiedźmina i Gwinta, LegacyGwent DIY za materiały kart i planszy, społeczności Beta Gwent za zachowanie archiwalnych materiałów i pomysły na archetypy oraz wszystkim, którzy testują moda i przysyłają szczegółowe zgłoszenia.

Nieoficjalny projekt fanowski. Oryginalny kod moda jest udostępniony na licencji GPL-3.0-only; oryginalne materiały z gry należą do ich właścicieli.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)


---

# Gwent Beta Classic 0.8.1 — Español (España)

> La versión 0.8.1 para Next-Gen 5.0+ se ha probado en el juego. Classic 1.32 se está corrigiendo y probando por separado; su archivo actual es una versión de prueba.

## Importante

Haz una copia de seguridad de tus partidas guardadas antes de instalar y antes de cada actualización. El mod está en desarrollo activo: usa una partida aparte para tus primeras partidas de Gwent.

Las traducciones siguen siendo una versión de prueba: los textos de las cartas proceden de la localización oficial de la beta y la interfaz se ha traducido con IA, por lo que puede contener errores. Las nuevas indicaciones añadidas desde la 0.6.6 solo existen por ahora en inglés y ruso; en los demás idiomas se muestran en inglés. Avísanos de todo lo que suene mal.

## Sobre el mod

Gwent Beta Classic sustituye el Gwent de The Witcher 3 por las cartas, las reglas y el tablero de Gwent Beta 0.9.24 independiente. Las partidas siguen formando parte del mundo de The Witcher: juega contra PNJ, completa misiones, compra barriles y crea tus propios mazos.

## Características

- 479 cartas coleccionables, incluidos 21 líderes, de las cinco facciones
- Tablero, interfaz, fuentes, marcos de cartas, clima y efectos de la beta; líderes animados
- Editor de mazos: cinco mazos iniciales editables y ocho huecos propios, filtros y búsqueda
- Rivales con 46 arquetipos de mazos de la beta y tres niveles de dificultad de la IA
- Barriles por 200 coronas en todos los posaderos, que se abren como en la beta
- Fragmentos: fabrica cartas por 30 / 80 / 200 / 800 según su rareza; las copias sobrantes se muelen automáticamente
- Tutorial, mulligan, consulta de cementerios y del mazo, vista detallada de las cartas
- Ratón, teclado y mando

## Cambios desde 0.7.3a

- Cada paquete incluye los cinco doblajes y los 13 idiomas de texto. Ya no hacen falta descargas separadas por idioma de voz.
- Dos botones contiguos, Texto y Voces, en el menú del mod, con selección automática o manual independiente.
- Detección separada del idioma del texto y de las voces del juego. Los idiomas no disponibles utilizan inglés.
- Las preferencias se guardan con la partida. La selección manual anterior del texto se mantiene al actualizar.
- Corregidas las definiciones de los barriles y la recuperación de existencias en Nueva partida +. Una entrega fallida ya no se marca como completada; los barriles vendidos no reaparecen cada vez que se abre la tienda.
- Revisados los tres proyectiles de Jotunn, Kambi/Hemdall, Ragh Nar Roog, Golden Froth, estados, temporizadores y efectos de armadura.
- Recursos de interfaz reorganizados dentro del presupuesto de compilación de 63 MiB sin reducir la resolución de las texturas. La carga de menús y la estabilidad siguen pendientes de validación.

## Idiomas

Texto: inglés, ruso, alemán, francés, italiano, polaco, español (España), español (Latinoamérica), portugués (Brasil), japonés, coreano, chino simplificado y chino tradicional. Cámbialo cuando quieras con el botón de idioma del texto, arriba a la izquierda en los menús de mazos y colección, o en los ajustes de combate; la elección se guarda.

Cada paquete incluye voces RU, EN, DE, IT y PT-BR. El texto y las voces se eligen por separado con dos botones contiguos en el menú de mazos/colección del mod o en los ajustes de la partida. Cambiar las voces no requiere reinstalar archivos. Automático sigue por separado los idiomas actuales de texto y voz del juego; si falta un idioma, utiliza inglés. Guarda la partida normalmente después de elegir: las preferencias pertenecen a ese guardado y se mantienen al actualizar los archivos del mod. Se conserva la selección manual anterior del texto. Algunas frases del trol de los barriles en DE/IT mantienen el reemplazo ruso de las grabaciones originales. Los nombres nativos de objetos siguen el idioma del juego; algunas notificaciones externas siguen en RU/EN.

## Instalación

1. Cierra el juego y haz una copia de seguridad de las partidas. Descarga el paquete para 1.32 o Next-Gen (5.0+). Instala una sola versión de Beta Gwent.

2. Al actualizar, mueve primero la carpeta anterior del mod Beta Gwent fuera de Mods. No elimines toda la carpeta Mods ni mezcles versiones.

3. Copia Mods desde el archivo al directorio del juego, junto a bin y content. Ruta final: Mods/modBetaGwentClassic132/content para 1.32 o Mods/modBetaGwent0924/content para Next-Gen.

4. Carga una partida. El menú habitual de mazos de Gwynt abre el editor y los idiomas; habla con un PNJ que juegue para comenzar una partida. Guarda normalmente para conservar tus preferencias.

## Requisitos

The Witcher 3 para PC. Elige la compilación separada de Classic 1.32 o Next-Gen (paquete marcado 5.0+). No necesitas REDkit, Wwise ni un instalador EXE para jugar.

## Compatibilidad

Elimina la carpeta antigua modBetaGwentReduxCompat: la capa de compatibilidad independiente ya no se incluye. La compatibilidad con Redux/Redo Expansion no se ha confirmado por separado. Otras revisiones de Gwent y mods que cambien sus menús, el intercambio de cartas o las recompensas pueden causar conflictos. Tras cambiar los mods instalados, vuelve a combinar los scripts con Script Merger.

## Informar de errores

¿Has encontrado un problema? Indica las versiones del mod y del juego, los idiomas elegidos para texto y voces (incluido Automático), si usas Nueva partida +, otros mods, cartas/líderes y los pasos para reproducirlo. Ayudan una captura y un guardado anterior al problema. Para traducciones, indica idioma y pantalla y sugiere una redacción mejor.

### Cómo activar el registro

1. Añade -debugscripts después de las comillas de cierre del destino de un acceso directo a witcher3.exe. Steam: Propiedades → General → Parámetros de lanzamiento. En GOG puedes usar un acceso directo al propio witcher3.exe.

2. Inicia el juego, reproduce el problema y ciérralo. Copia scriptslog.txt inmediatamente: el siguiente inicio lo sobrescribe. Si solo contiene una cabecera, indícalo; puede hacer falta una configuración adicional.

3. Si Windows ha creado un volcado del fallo, adjunta también el último archivo .dmp correspondiente.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Agradecimientos

Gracias a CD Projekt por The Witcher y Gwent, a LegacyGwent DIY por los recursos de cartas y tablero, a la comunidad de Beta Gwent por conservar el material histórico y las ideas de arquetipos, y a todos los que prueban el mod y envían informes detallados.

Proyecto de fans no oficial. El código original del mod se distribuye bajo GPL-3.0-only; los recursos originales del juego pertenecen a sus propietarios.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)


---

# Gwent Beta Classic 0.8.1 — Español (Latinoamérica)

> La versión 0.8.1 para Next-Gen 5.0+ ya se probó dentro del juego. Classic 1.32 se está corrigiendo y probando por separado; su archivo actual es una versión de prueba.

## Importante

Haz un respaldo de tus partidas guardadas antes de instalar y antes de cada actualización. El mod está en desarrollo activo: usa una partida aparte para tus primeros juegos de Gwent.

Las traducciones siguen siendo una versión de prueba: los textos de las cartas vienen de la localización oficial de la beta y la interfaz se tradujo con IA, así que puede tener errores. Las nuevas indicaciones agregadas desde la 0.6.6 por ahora solo existen en inglés y ruso; en los demás idiomas aparecen en inglés. Avísanos de todo lo que suene raro.

## Acerca del mod

Gwent Beta Classic reemplaza el Gwent de The Witcher 3 con las cartas, las reglas y el tablero de Gwent Beta 0.9.24 independiente. Las partidas siguen siendo parte del mundo de The Witcher: juega contra NPC, completa misiones, compra barriles y arma tus propios mazos.

## Características

- 479 cartas coleccionables, incluidos 21 líderes, de las cinco facciones
- Tablero, interfaz, fuentes, marcos de cartas, clima y efectos de la beta; líderes animados
- Editor de mazos: cinco mazos iniciales editables y ocho espacios propios, filtros y búsqueda
- Rivales con 46 arquetipos de mazos de la beta y tres niveles de dificultad de la IA
- Barriles por 200 coronas con todos los posaderos, que se abren como en la beta
- Fragmentos: fabrica cartas por 30 / 80 / 200 / 800 según su rareza; las copias sobrantes se muelen automáticamente
- Tutorial, mulligan, consulta de cementerios y del mazo, vista detallada de las cartas
- Mouse, teclado y control

## Cambios desde 0.7.3a

- Cada paquete incluye los cinco doblajes y los 13 idiomas de texto. Ya no hacen falta descargas separadas por idioma de voz.
- Dos botones contiguos, Texto y Voces, en el menú del mod, con selección automática o manual independiente.
- Detección separada del idioma del texto y de las voces del juego. Los idiomas no disponibles utilizan inglés.
- Las preferencias se guardan con la partida. La selección manual anterior del texto se mantiene al actualizar.
- Corregidas las definiciones de los barriles y la recuperación de existencias en Nueva partida +. Una entrega fallida ya no se marca como completada; los barriles vendidos no reaparecen cada vez que se abre la tienda.
- Revisados los tres proyectiles de Jotunn, Kambi/Hemdall, Ragh Nar Roog, Golden Froth, estados, temporizadores y efectos de armadura.
- Recursos de interfaz reorganizados dentro del presupuesto de compilación de 63 MiB sin reducir la resolución de las texturas. La carga de menús y la estabilidad siguen pendientes de validación.

## Idiomas

Texto: inglés, ruso, alemán, francés, italiano, polaco, español (España), español (Latinoamérica), portugués (Brasil), japonés, coreano, chino simplificado y chino tradicional. Cámbialo cuando quieras con el botón de idioma del texto, arriba a la izquierda en los menús de mazos y colección, o en la configuración de combate; la elección se guarda.

Cada paquete incluye voces RU, EN, DE, IT y PT-BR. El texto y las voces se eligen por separado con dos botones contiguos en el menú de mazos/colección del mod o en los ajustes de la partida. Cambiar las voces no requiere reinstalar archivos. Automático sigue por separado los idiomas actuales de texto y voz del juego; si falta un idioma, utiliza inglés. Guarda la partida normalmente después de elegir: las preferencias pertenecen a ese guardado y se mantienen al actualizar los archivos del mod. Se conserva la selección manual anterior del texto. Algunas frases del trol de los barriles en DE/IT mantienen el reemplazo ruso de las grabaciones originales. Los nombres nativos de objetos siguen el idioma del juego; algunas notificaciones externas siguen en RU/EN.

## Instalación

1. Cierra el juego y haz un respaldo de tus partidas. Descarga el paquete para 1.32 o Next-Gen (5.0+). Instala solo una versión de Beta Gwent.

2. Para actualizar, mueve primero la carpeta anterior del mod Beta Gwent fuera de Mods. No borres toda la carpeta Mods ni mezcles archivos de versiones distintas.

3. Copia Mods del archivo a la carpeta del juego, junto a bin y content. Ruta final: Mods/modBetaGwentClassic132/content para 1.32 o Mods/modBetaGwent0924/content para Next-Gen.

4. Carga tu partida. El menú normal de mazos de Gwent abre el editor y la selección de idiomas; habla con un NPC que juegue para iniciar una partida. Guarda normalmente para conservar tus preferencias.

## Requisitos

The Witcher 3 para PC. Elige la compilación separada de Classic 1.32 o Next-Gen (paquete marcado 5.0+). No necesitas REDkit, Wwise ni un instalador EXE para jugar.

## Compatibilidad

Elimina la carpeta anterior modBetaGwentReduxCompat: la capa de compatibilidad independiente ya no se incluye. La compatibilidad con Redux/Redo Expansion no se confirmó por separado. Otras modificaciones de Gwent y mods que cambien sus menús, el intercambio de cartas o las recompensas pueden causar conflictos. Después de cambiar los mods instalados, vuelve a combinar los scripts con Script Merger.

## Reportar errores

¿Has encontrado un problema? Indica las versiones del mod y del juego, los idiomas elegidos para texto y voces (incluido Automático), si usas Nueva partida +, otros mods, cartas/líderes y los pasos para reproducirlo. Ayudan una captura y un guardado anterior al problema. Para traducciones, indica idioma y pantalla y sugiere una redacción mejor.

### Cómo activar el registro

1. Añade -debugscripts después de las comillas de cierre del destino de un acceso directo a witcher3.exe. Steam: Propiedades → General → Parámetros de lanzamiento. En GOG puedes usar un acceso directo al propio witcher3.exe.

2. Inicia el juego, reproduce el problema y ciérralo. Copia scriptslog.txt inmediatamente: el siguiente inicio lo sobrescribe. Si solo contiene una cabecera, indícalo; puede hacer falta una configuración adicional.

3. Si Windows ha creado un volcado del fallo, adjunta también el último archivo .dmp correspondiente.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Agradecimientos

Gracias a CD Projekt por The Witcher y Gwent, a LegacyGwent DIY por los recursos de cartas y tablero, a la comunidad de Beta Gwent por conservar el material histórico y las ideas de arquetipos, y a todos los que prueban el mod y mandan reportes detallados.

Proyecto de fans no oficial. El código original del mod se distribuye bajo GPL-3.0-only; los recursos originales del juego pertenecen a sus dueños.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)


---

# Gwent Beta Classic 0.8.1 — Português (Brasil)

> A versão 0.8.1 para Next-Gen 5.0+ foi testada no jogo. Classic 1.32 está sendo corrigida e testada separadamente; o arquivo atual é uma versão de teste.

## Importante

Faça backup dos seus saves antes de instalar e antes de cada atualização. O mod está em desenvolvimento ativo, então use um save separado nas primeiras partidas.

As traduções continuam em prévia: os textos das cartas vêm da localização oficial do beta e a interface foi traduzida com IA, podendo conter erros. As novas dicas adicionadas desde a 0.6.6 existem por enquanto só em inglês e russo; nos demais idiomas aparecem em inglês. Avise sobre tudo o que soar errado.

## Sobre o mod

Gwent Beta Classic substitui o Gwent de The Witcher 3 pelas cartas, regras e tabuleiro do Gwent Beta 0.9.24 independente. As partidas continuam fazendo parte do mundo de The Witcher: jogue contra NPCs, conclua missões, compre barris e monte seus próprios baralhos.

## Recursos

- 479 cartas colecionáveis, incluindo 21 líderes, das cinco facções
- Tabuleiro, interface, fontes, molduras de cartas, clima e efeitos do beta; líderes animados
- Editor de baralhos: cinco baralhos iniciais editáveis e oito espaços próprios, filtros e busca
- Oponentes com 46 arquétipos de baralho do beta e três níveis de dificuldade da IA
- Barris por 200 coroas com todos os taverneiros, abertos como no beta
- Fragmentos: crie cartas por 30 / 80 / 200 / 800 conforme a raridade; cópias excedentes são moídas automaticamente
- Tutorial, mulligan, visualização dos cemitérios e do baralho, detalhes completos das cartas
- Mouse, teclado e controle

## Mudanças desde a 0.7.3a

- Cada pacote inclui as cinco dublagens e os 13 idiomas de texto. Não é mais preciso baixar um pacote diferente para cada voz.
- Dois botões lado a lado, Texto e Vozes, no menu do mod, com seleção automática ou manual independente.
- Detecção separada dos idiomas de texto e fala do jogo. Idiomas não disponíveis usam inglês.
- As preferências ficam no save. A escolha manual anterior do texto é mantida ao atualizar.
- Corrigidas as definições de barris e a recuperação do estoque no Novo Jogo +. Uma entrega que falhou não é mais marcada como concluída; barris vendidos não voltam toda vez que a loja abre.
- Revisados os três projéteis de Jotunn, Kambi/Hemdall, Ragh Nar Roog, Golden Froth, status, contadores e efeitos de armadura.
- Recursos da interface reorganizados dentro do orçamento de compilação de 63 MiB sem reduzir a resolução das texturas. Carregamento dos menus e estabilidade continuam na validação.

## Idiomas

Texto: inglês, russo, alemão, francês, italiano, polonês, espanhol (Espanha), espanhol (América Latina), português (Brasil), japonês, coreano, chinês simplificado e chinês tradicional. Troque a qualquer momento pelo botão de idioma do texto no canto superior esquerdo dos menus de baralhos e coleção, ou nas configurações de batalha; a escolha fica salva.

Cada pacote inclui vozes RU, EN, DE, IT e PT-BR. Texto e vozes são escolhidos separadamente por dois botões lado a lado no menu de baralhos/coleção do mod ou nas configurações da partida. Trocar as vozes não exige reinstalar arquivos. Automático segue separadamente os idiomas atuais de texto e fala do jogo; se um idioma não estiver disponível, usa inglês. Salve normalmente depois da escolha: as preferências pertencem a esse save e permanecem ao atualizar os arquivos do mod. A seleção manual anterior do texto é mantida. Algumas falas do troll dos barris em DE/IT continuam usando a substituição russa das gravações originais. Os nomes nativos dos itens seguem o idioma do jogo; algumas notificações externas continuam em RU/EN.

## Instalação

1. Feche o jogo e faça backup dos saves. Baixe o pacote para 1.32 ou Next-Gen (5.0+). Instale apenas uma versão de Beta Gwent.

2. Ao atualizar, primeiro mova a pasta antiga do mod Beta Gwent para fora de Mods. Não apague toda a pasta Mods nem misture arquivos de versões diferentes.

3. Copie Mods do arquivo para a pasta do jogo, ao lado de bin e content. Caminho final: Mods/modBetaGwentClassic132/content para 1.32 ou Mods/modBetaGwent0924/content para Next-Gen.

4. Carregue seu save. O menu normal de baralhos de Gwent abre o editor e os idiomas; converse com um NPC que joga para iniciar uma partida. Salve normalmente para manter suas preferências.

## Requisitos

The Witcher 3 para PC. Escolha a versão separada para Classic 1.32 ou Next-Gen (pacote identificado como 5.0+). REDkit, Wwise e instalador EXE não são necessários para jogar.

## Compatibilidade

Remova a pasta antiga modBetaGwentReduxCompat: a camada de compatibilidade separada não é mais incluída. A compatibilidade com Redux/Redo Expansion não foi confirmada separadamente. Outras reformulações do Gwent e mods que alterem seus menus, trocas de cartas ou recompensas podem causar conflitos. Depois de mudar os mods instalados, refaça a mesclagem dos scripts com Script Merger.

## Relatar bugs

Encontrou um problema? Informe as versões do mod e do jogo, os idiomas escolhidos para texto e vozes (inclusive Automático), se é Novo Jogo +, outros mods, cartas/líderes e os passos para reproduzir. Uma captura e um save anterior ao problema ajudam. Para traduções, indique idioma, tela e uma sugestão de texto melhor.

### Como ativar o log

1. Adicione -debugscripts depois das aspas finais no destino de um atalho para witcher3.exe. Steam: Propriedades → Geral → Opções de inicialização. No GOG, use um atalho direto para witcher3.exe.

2. Inicie o jogo, reproduza o problema e feche-o. Copie scriptslog.txt imediatamente: a próxima inicialização substitui o arquivo. Se houver apenas um cabeçalho, avise; pode ser necessária uma configuração adicional.

3. Se o Windows criou um dump da falha, anexe também o último .dmp correspondente.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Agradecimentos

Obrigado à CD Projekt por The Witcher e Gwent, ao LegacyGwent DIY pelos recursos de cartas e tabuleiro, à comunidade do Beta Gwent por preservar o material histórico e as ideias de arquétipos, e a todos que testam o mod e enviam relatórios detalhados.

Projeto de fã não oficial. O código original do mod é distribuído sob GPL-3.0-only; os recursos originais do jogo pertencem aos seus donos.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)


---

# Gwent Beta Classic 0.8.1 — 日本語

> Next-Gen 5.0+向けのバージョン0.8.1はゲーム内で動作確認済みです。Classic 1.32向けは別途修正・検証中で、現在のアーカイブはテスト版です。

## 重要

インストール前と毎回のアップデート前に、必ずセーブデータをバックアップしてください。MODは開発中のため、最初の数試合は別のセーブデータで遊ぶことをおすすめします。

翻訳は引き続きプレビュー版です。カードのテキストはベータ版の公式ローカライズから取り込んでいますが、インターフェースはAIで翻訳しているため、誤りがあるかもしれません。0.6.6以降に追加された新しいヒントは現在英語とロシア語のみで、他の言語では英語で表示されます。おかしな表現を見つけたらお知らせください。

## MODについて

Gwent Beta Classicは、The Witcher 3のグウェントを、単体版Gwent Beta 0.9.24のカード、ルール、盤面に置き換えるMODです。試合はウィッチャーの世界の一部のまま：NPCと対戦し、クエストをこなし、樽を買い、自分のデッキを組みましょう。

## 主な機能

- 全5勢力、リーダー21枚を含む収集カード479枚
- ベータ版の盤面、HUD、フォント、カードフレーム、天候、エフェクト。リーダーはアニメーション付き
- デッキエディター：編集可能なスターターデッキ5つと自由に使える8枠、フィルターと検索
- ベータ版の46種類のデッキアーキタイプを使う対戦相手、AIの難易度は3段階
- すべての宿屋の主人から200クラウンで買える樽。ベータ版と同じ演出で開封
- スクラップ：レアリティに応じて30 / 80 / 200 / 800でカードを作成。余分な枚数は自動で分解
- チュートリアル、マリガン、墓地とデッキの確認、カードの詳細表示
- マウス、キーボード、コントローラーに対応

## 0.7.3aからの変更点

- 各パッケージに5種類の音声と13種類のテキスト言語を同梱。音声ごとに別のファイルをダウンロードする必要がなくなりました。
- MODメニューに「テキスト」と「音声」のボタンを並べて配置。それぞれ自動または手動で選択できます。
- ゲームのテキスト言語と音声言語を個別に検出。未対応の言語では英語を使用します。
- 言語設定はセーブデータに保存。以前に手動で選んだテキスト言語は更新後も維持されます。
- ニューゲーム＋の樽定義と在庫復旧を修正。アイテム追加が失敗しても完了扱いにせず、販売済みの在庫を店を開くたびに補充しないようにしました。
- Jotunnの3発の投射物、Kambi/Hemdall、Ragh Nar Roog、Golden Froth、状態変化、タイマー、アーマーの演出を調整。
- テクスチャ解像度を下げずにインターフェースリソースを再配置し、ビルド予算63 MiBに収めました。メニュー起動と安定性の検証は引き続き必要です。

## 言語

テキスト：英語、ロシア語、ドイツ語、フランス語、イタリア語、ポーランド語、スペイン語（スペイン）、スペイン語（中南米）、ポルトガル語（ブラジル）、日本語、韓国語、簡体字中国語、繁体字中国語。デッキ／コレクション画面の左上にあるテキスト言語ボタン、または対戦中の設定からいつでも切り替えられ、選択は保存されます。

全パッケージにRU、EN、DE、IT、PT-BRの音声を収録しています。MODのデッキ／コレクションメニューで隣り合う2つのボタンから、テキストと音声を別々に選べます。対戦設定からも変更でき、音声を変えるための再インストールは不要です。「自動」はゲームの現在のテキスト言語と音声言語を個別に参照し、対応する言語がなければ英語を使用します。選択後は通常の方法でゲームを保存してください。設定はそのセーブデータに記録され、MODファイルを更新しても維持されます。以前の手動テキスト設定も引き継ぎます。DE／ITの樽トロールの一部の台詞は、元の音源にあるロシア語の代替音声を使用します。ゲーム本来のアイテム名はゲーム側の言語に従い、一部のMOD画面外の通知はRU／ENのままです。

## インストール

1. ゲームを終了し、セーブデータをバックアップします。1.32またはNext-Gen（5.0+）に合うパッケージを1つだけダウンロードしてください。Beta Gwentを複数同時に導入しないでください。

2. 更新時は、古いBeta GwentのMODフォルダーを先にModsの外へ移動します。Mods全体を削除したり、異なるバージョンのファイルを混在させたりしないでください。

3. アーカイブ内のModsを、binとcontentがあるゲームフォルダーへコピーします。1.32ではMods/modBetaGwentClassic132/content、Next-GenではMods/modBetaGwent0924/contentになります。

4. セーブデータをロードします。通常のグウェントのデッキメニューから編集と言語選択ができ、グウェントを遊ぶNPCとの会話から対戦を始められます。設定を残すには通常の方法で保存してください。

## 動作環境

PC版The Witcher 3。Classic 1.32用またはNext-Gen用（5.0+表記）の別ビルドを選んでください。プレイにREDkit、Wwise、EXEインストーラーは不要です。

## 互換性

古いmodBetaGwentReduxCompatフォルダを削除してください。独立した互換レイヤーは含まれなくなりました。Redux/Redo Expansionとの互換性は個別には確認されていません。他のグウェント改変MODや、メニュー、カード取引、報酬を変更するMODとは競合する可能性があります。MOD構成を変更した後はScript Mergerでスクリプトを再マージしてください。

## バグ報告

問題を見つけた場合は、MODとゲームの正確なバージョン、選択したテキストと音声（自動も含む）、ニューゲーム＋かどうか、他のMOD、カード／リーダー、再現手順を教えてください。スクリーンショットと問題発生前のセーブデータがあると助かります。翻訳の問題は言語と画面、より自然な訳の提案を添えてください。

### ログを有効にする方法

1. witcher3.exeへの直接ショートカットのリンク先で、閉じ引用符の後に -debugscripts を追加します。Steamではプロパティ → 一般 → 起動オプションに追加できます。GOGでもwitcher3.exeへの直接ショートカットを使用できます。

2. ゲームを起動して問題を再現し、終了します。次回の起動で上書きされるため、scriptslog.txtをすぐにコピーしてください。ヘッダーしか記録されていない場合は、その旨もお知らせください。追加のログ設定が必要なことがあります。

3. Windowsがクラッシュダンプを作成した場合は、該当する最新の.dmpファイルも添付してください。

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## クレジット

The WitcherとGwentを生んだCD Projekt、カードと盤面の素材を提供してくれたLegacyGwent DIY、資料を保存しアーキタイプのアイデアを共有してくれたBeta Gwentコミュニティ、そしてテストと詳しい報告をしてくれるすべての方に感謝します。

非公式のファンプロジェクトです。MOD独自のコードはGPL-3.0-onlyで公開しています。ゲームのオリジナル素材の権利は各権利者に帰属します。

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)


---

# Gwent Beta Classic 0.8.1 — 한국어

> Next-Gen 5.0+용 0.8.1은 게임 내에서 테스트되었습니다. Classic 1.32용은 별도로 수정 및 검증 중이며, 현재 배포 파일은 테스트 버전입니다.

## 중요

설치 전과 업데이트할 때마다 반드시 세이브 파일을 백업하세요. 모드는 개발 중이므로 처음 몇 판은 별도의 세이브로 플레이하는 것을 권장합니다.

번역은 여전히 미리보기 단계입니다. 카드 텍스트는 베타의 공식 현지화를 사용했고 인터페이스는 AI로 번역해 오류가 있을 수 있습니다. 0.6.6부터 추가된 새 안내 문구는 현재 영어와 러시아어로만 제공되며, 다른 언어에서는 영어로 표시됩니다. 어색한 표현이 있으면 알려 주세요.

## 모드 소개

Gwent Beta Classic은 The Witcher 3의 궨트를 독립형 Gwent Beta 0.9.24의 카드, 규칙, 게임판으로 바꿉니다. 대결은 그대로 위쳐 세계의 일부입니다. NPC와 대결하고, 퀘스트를 진행하고, 통을 사고, 나만의 덱을 만들어 보세요.

## 주요 기능

- 다섯 진영 전부, 리더 21장을 포함한 수집 카드 479장
- 베타의 게임판, HUD, 글꼴, 카드 테두리, 날씨와 효과, 움직이는 리더
- 덱 편집기: 수정 가능한 시작 덱 5개와 개인 슬롯 8개, 필터와 검색
- 베타의 덱 아키타입 46종을 사용하는 상대, AI 난이도 3단계
- 모든 여관 주인에게서 200크라운에 사는 통, 베타처럼 개봉
- 조각: 희귀도에 따라 30 / 80 / 200 / 800으로 카드 제작, 초과 사본은 자동으로 분쇄
- 튜토리얼, 멀리건, 무덤과 덱 보기, 카드 상세 보기
- 마우스, 키보드, 컨트롤러 지원

## 0.7.3a 이후 변경 사항

- 각 패키지에 음성 5종과 텍스트 언어 13종을 모두 포함했습니다. 음성별로 별도 파일을 받을 필요가 없습니다.
- 모드 메뉴에 텍스트와 음성 버튼을 나란히 배치했습니다. 각각 자동 또는 수동으로 선택할 수 있습니다.
- 게임의 텍스트 언어와 음성 언어를 따로 감지합니다. 지원하지 않는 언어는 영어로 대체합니다.
- 언어 설정을 게임 세이브에 저장합니다. 이전에 수동으로 선택한 텍스트 언어도 업데이트 후 유지됩니다.
- 새 게임 +의 통 정의와 재고 복구를 수정했습니다. 아이템 지급 실패를 완료로 기록하지 않으며, 상점을 열 때마다 판매한 재고가 다시 채워지지 않습니다.
- Jotunn의 투사체 3개, Kambi/Hemdall, Ragh Nar Roog, Golden Froth, 상태 변화, 타이머, 방어구 효과를 다듬었습니다.
- 텍스처 해상도를 낮추지 않고 인터페이스 리소스를 다시 묶어 빌드 예산 63 MiB에 맞췄습니다. 메뉴 시작과 안정성은 계속 검증해야 합니다.

## 언어

텍스트: 영어, 러시아어, 독일어, 프랑스어, 이탈리아어, 폴란드어, 스페인어(스페인), 스페인어(중남미), 포르투갈어(브라질), 일본어, 한국어, 중국어 간체, 중국어 번체. 덱/컬렉션 메뉴 왼쪽 위의 텍스트 언어 버튼이나 전투 설정에서 언제든지 바꿀 수 있으며, 선택은 저장됩니다.

각 패키지에는 RU, EN, DE, IT, PT-BR 음성이 모두 들어 있습니다. 모드의 덱/컬렉션 메뉴에 나란히 있는 두 버튼으로 텍스트와 음성을 각각 선택하며, 대결 설정에서도 변경할 수 있습니다. 음성을 바꾸려고 재설치할 필요는 없습니다. 자동은 게임의 현재 텍스트와 음성 언어를 따로 따르며, 지원하지 않는 언어는 영어를 사용합니다. 선택 후 정상적으로 게임을 저장하세요. 설정은 해당 세이브에 기록되어 모드 파일을 업데이트해도 유지됩니다. 기존 수동 텍스트 선택도 보존됩니다. DE/IT의 통 트롤 대사 일부는 원본 녹음의 러시아어 대체 음성을 유지합니다. 게임 기본 아이템 이름은 게임 언어를 따르고, 모드 화면 밖의 알림 일부는 RU/EN으로 남아 있습니다.

## 설치

1. 게임을 종료하고 세이브를 백업하세요. 1.32 또는 Next-Gen(5.0+)에 맞는 패키지를 받으세요. Beta Gwent는 한 버전만 설치하세요.

2. 업데이트할 때는 이전 Beta Gwent 모드 폴더를 먼저 Mods 밖으로 옮기세요. Mods 전체를 삭제하거나 다른 버전의 파일을 섞지 마세요.

3. 압축 파일의 Mods를 bin과 content가 있는 게임 폴더에 복사하세요. 최종 경로는 1.32의 경우 Mods/modBetaGwentClassic132/content, Next-Gen은 Mods/modBetaGwent0924/content입니다.

4. 세이브를 불러오세요. 기존 궨트 덱 메뉴에서 편집과 언어 선택을 할 수 있고, 궨트를 하는 NPC와 대화하면 대결을 시작합니다. 설정을 유지하려면 정상적으로 저장하세요.

## 요구 사항

PC용 The Witcher 3. Classic 1.32 또는 Next-Gen(5.0+로 표시된 패키지)용 별도 빌드를 선택하세요. 플레이에 REDkit, Wwise, EXE 설치 프로그램은 필요하지 않습니다.

## 호환성

예전 modBetaGwentReduxCompat 폴더를 삭제하세요. 별도의 호환 계층은 더 이상 포함되지 않습니다. Redux/Redo Expansion과의 호환성은 별도로 확인되지 않았습니다. 다른 궨트 개편 모드나 메뉴, 카드 거래, 보상을 변경하는 모드는 충돌할 수 있습니다. 설치한 모드 구성을 바꾼 후 Script Merger로 스크립트를 다시 병합하세요.

## 버그 제보

문제를 발견했나요? 모드와 게임의 정확한 버전, 선택한 텍스트/음성 언어(자동 포함), 새 게임 + 여부, 다른 모드, 카드/리더와 재현 절차를 알려 주세요. 스크린샷과 문제 발생 전 세이브가 도움이 됩니다. 번역 문제라면 언어와 화면, 더 나은 표현도 제안해 주세요.

### 로그 활성화 방법

1. witcher3.exe 바로가기의 대상에서 닫는 따옴표 뒤에 -debugscripts를 추가하세요. Steam은 속성 → 일반 → 시작 옵션을 사용합니다. GOG에서도 witcher3.exe에 직접 연결되는 바로가기를 사용할 수 있습니다.

2. 게임을 실행해 문제를 재현하고 종료하세요. 다음 실행 때 덮어쓰므로 scriptslog.txt를 즉시 복사하세요. 헤더만 있다면 알려 주세요. 추가 로그 설정이 필요할 수 있습니다.

3. Windows가 크래시 덤프를 생성했다면 해당하는 최신 .dmp 파일도 첨부하세요.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## 감사의 말

The Witcher와 Gwent를 만든 CD Projekt, 카드와 게임판 자료를 제공한 LegacyGwent DIY, 자료를 보존하고 아키타입 아이디어를 나눠 준 Beta Gwent 커뮤니티, 그리고 모드를 테스트하고 자세한 제보를 보내 주시는 모든 분께 감사드립니다.

비공식 팬 프로젝트입니다. 모드 고유 코드는 GPL-3.0-only로 배포되며, 게임 원본 자료의 권리는 각 소유자에게 있습니다.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)


---

# Gwent Beta Classic 0.8.1 — 简体中文

> 适用于 Next-Gen 5.0+ 的 0.8.1 已完成游戏内测试。Classic 1.32 版本正在单独修复和测试，目前的压缩包为测试版本。

## 重要

安装前以及每次更新前，请务必备份存档。模组仍在积极开发中，前几局建议使用单独的存档。

翻译仍为预览版：卡牌文本来自 Beta 的官方本地化，界面由 AI 翻译，可能存在错误。0.6.6 以来新增的提示目前只有英语和俄语，其他语言会以英语显示。发现不通顺的地方请告诉我们。

## 关于模组

Gwent Beta Classic 将《巫师 3》的昆特牌替换为独立版 Gwent Beta 0.9.24 的卡牌、规则和牌桌。对局依然是巫师世界的一部分：与 NPC 对战、完成任务、购买桶、组建自己的牌组。

## 主要功能

- 五大阵营共 479 张可收集卡牌，其中包括 21 张领袖牌
- Beta 的牌桌、HUD、字体、卡框、天气和特效；领袖牌带动画
- 牌组编辑器：五套可修改的初始牌组和八个自定义栏位，支持筛选和搜索
- 对手使用 46 种 Beta 牌组原型，AI 难度分三档
- 所有旅店老板出售 200 克朗的桶，开桶方式与 Beta 相同
- 碎片：按稀有度花费 30 / 80 / 200 / 800 合成卡牌，多余副本会自动分解
- 教程、调度、查看墓地和牌库、卡牌详情
- 支持鼠标、键盘和手柄

## 0.7.3a 之后的变化

- 每个版本包均包含全部 5 种语音和 13 种文字语言，无须再按语音分别下载。
- 模组菜单新增并排的文字和语音按钮，两者均可独立选择自动或手动模式。
- 分别读取游戏当前的文字和语音语言；不支持的语言使用英语。
- 语言设置随游戏存档保存，更新后保留此前手动选择的文字语言。
- 修复新游戏＋的桶定义和库存恢复。物品添加失败不再被标记为完成，已售出的桶不会每次打开商店都重新补满。
- 调整 Jotunn 的三发投射物、Kambi/Hemdall、Ragh Nar Roog、Golden Froth、状态变化、计时器和护甲效果。
- 在不降低纹理分辨率的前提下重新打包界面资源，使其符合 63 MiB 的构建预算。菜单加载和稳定性仍属于验收内容。

## 语言

文字：英语、俄语、德语、法语、意大利语、波兰语、西班牙语（西班牙）、西班牙语（拉丁美洲）、葡萄牙语（巴西）、日语、韩语、简体中文、繁体中文。可随时通过牌组和收藏菜单左上角的文字语言按钮或战斗设置切换，选择会被保存。

每个包都包含 RU、EN、DE、IT、PT-BR 语音。通过模组牌组／收藏菜单中并排的两个按钮，分别选择文字和语音；对局设置中也可更改。切换语音无须重新安装文件。自动模式分别跟随游戏当前的文字和语音语言；缺少相应语言时使用英语。选择后请正常保存游戏：设置属于该存档，更新模组文件后仍会保留，此前手动选择的文字语言也会继承。DE／IT 的酒桶巨魔部分台词仍使用原始录音中的俄语替代版本。游戏原生物品名称跟随游戏语言，部分模组界面外的通知仍为 RU／EN。

## 安装

1. 关闭游戏并备份存档。下载适合 1.32 或 Next-Gen（5.0+）的包，只安装一个 Beta Gwent 版本。

2. 更新时，先将旧的 Beta Gwent 模组文件夹移到 Mods 之外。不要删除整个 Mods 文件夹，也不要混用不同版本的文件。

3. 把压缩包内的 Mods 复制到游戏根目录，与 bin 和 content 同级。1.32 的最终路径为 Mods/modBetaGwentClassic132/content；Next-Gen 为 Mods/modBetaGwent0924/content。

4. 读取存档。原有昆特牌牌组菜单可打开编辑器和语言选择；与会玩昆特牌的 NPC 对话即可开始对局。正常保存游戏以保留设置。

## 系统要求

PC 版《巫师 3》。请选择 Classic 1.32 或 Next-Gen（标有 5.0+）对应的独立构建包。游玩不需要 REDkit、Wwise 或 EXE 安装程序。

## 兼容性

请删除旧的 modBetaGwentReduxCompat 文件夹，独立兼容层已不再附带。与 Redux/Redo Expansion 的兼容性尚未单独确认。其他昆特牌改动模组，以及修改菜单、卡牌交易或奖励的模组可能产生冲突。更改模组组合后，请用 Script Merger 重新合并脚本。

## 反馈问题

发现问题？请提供模组与游戏的准确版本、选择的文字和语音语言（包括自动模式）、是否为新游戏＋、其他模组、涉及的卡牌／领袖及复现步骤。截图和问题发生前的存档有助于排查。翻译问题请注明语言和界面，并提出更合适的表达。

### 如何启用日志

1. 在指向 witcher3.exe 的快捷方式目标中，结束引号后添加 -debugscripts。Steam：属性 → 通用 → 启动选项。GOG 也可使用直接指向 witcher3.exe 的快捷方式。

2. 启动游戏，复现问题后关闭游戏。立即复制 scriptslog.txt，下次启动会覆盖它。如果文件只有标题，请说明；该构建可能还需要额外的日志设置。

3. 如果 Windows 生成了崩溃转储，请同时附上最新的相关 .dmp 文件。

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## 致谢

感谢 CD Projekt 带来《巫师》和昆特牌，感谢 LegacyGwent DIY 提供卡牌和牌桌素材，感谢 Beta Gwent 社区保存历史资料并分享牌组原型思路，也感谢每一位测试模组并提交详细报告的玩家。

非官方粉丝项目。模组原创代码以 GPL-3.0-only 许可发布；游戏原始素材归各自所有者所有。

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)


---

# Gwent Beta Classic 0.8.1 — 繁體中文

> 適用於 Next-Gen 5.0+ 的 0.8.1 已完成遊戲內測試。Classic 1.32 版本正在另行修正與測試，目前的壓縮檔為測試版本。

## 重要

安裝前以及每次更新前，請務必備份存檔。模組仍在積極開發中，前幾局建議使用另外的存檔。

翻譯仍為預覽版：卡牌文字來自 Beta 的官方在地化，介面由 AI 翻譯，可能有錯誤。0.6.6 以來新增的提示目前只有英文和俄文，其他語言會以英文顯示。發現不通順的地方請告訴我們。

## 關於模組

Gwent Beta Classic 將《巫師 3》的昆特牌替換為獨立版 Gwent Beta 0.9.24 的卡牌、規則和牌桌。對局依然是巫師世界的一部分：與 NPC 對戰、完成任務、購買桶、組建自己的牌組。

## 主要功能

- 五大陣營共 479 張可收集卡牌，其中包括 21 張領導牌
- Beta 的牌桌、HUD、字型、卡框、天氣和特效；領導牌附動畫
- 牌組編輯器：五套可修改的初始牌組和八個自訂欄位，支援篩選和搜尋
- 對手使用 46 種 Beta 牌組原型，AI 難度分三級
- 所有旅店老闆販售 200 克朗的桶，開桶方式與 Beta 相同
- 碎片：依稀有度花費 30 / 80 / 200 / 800 合成卡牌，多餘副本會自動分解
- 教學、調度、檢視墓地和牌庫、卡牌詳情
- 支援滑鼠、鍵盤和控制器

## 0.7.3a 之後的變更

- 每個版本包均包含全部 5 種語音和 13 種文字語言，不必再依語音分別下載。
- 模組選單新增並排的文字與語音按鈕，兩者都能獨立選擇自動或手動模式。
- 分別讀取遊戲目前的文字與語音語言；不支援的語言使用英語。
- 語言設定隨遊戲存檔儲存，更新後保留先前手動選擇的文字語言。
- 修正新遊戲＋的桶定義與庫存復原。物品新增失敗不再標記為完成，已售出的桶不會在每次開啟商店時重新補滿。
- 調整 Jotunn 的三發投射物、Kambi/Hemdall、Ragh Nar Roog、Golden Froth、狀態變化、計時器和護甲效果。
- 在不降低紋理解析度的前提下重新封裝介面資源，使其符合 63 MiB 的建置預算。選單載入與穩定性仍屬於驗收項目。

## 語言

文字：英文、俄文、德文、法文、義大利文、波蘭文、西班牙文（西班牙）、西班牙文（拉丁美洲）、葡萄牙文（巴西）、日文、韓文、簡體中文、繁體中文。可隨時透過牌組和收藏選單左上角的文字語言按鈕或戰鬥設定切換，選擇會被保存。

每個包都包含 RU、EN、DE、IT、PT-BR 語音。透過模組牌組／收藏選單中並排的兩個按鈕，分別選擇文字與語音；對局設定中也能變更。切換語音不必重新安裝檔案。自動模式分別跟隨遊戲目前的文字與語音語言；缺少對應語言時使用英語。選擇後請正常儲存遊戲：設定屬於該存檔，更新模組檔案後仍會保留，先前手動選擇的文字語言也會繼承。DE／IT 的酒桶巨魔部分台詞仍使用原始錄音中的俄語替代版本。遊戲原生物品名稱跟隨遊戲語言，部分模組介面外的通知仍為 RU／EN。

## 安裝

1. 關閉遊戲並備份存檔。下載適合 1.32 或 Next-Gen（5.0+）的包，只安裝一個 Beta Gwent 版本。

2. 更新時，先將舊的 Beta Gwent 模組資料夾移到 Mods 之外。不要刪除整個 Mods 資料夾，也不要混用不同版本的檔案。

3. 將壓縮檔內的 Mods 複製到遊戲根目錄，與 bin 和 content 同層。1.32 的最終路徑為 Mods/modBetaGwentClassic132/content；Next-Gen 為 Mods/modBetaGwent0924/content。

4. 讀取存檔。原有的昆特牌牌組選單可開啟編輯器與語言選擇；與會玩昆特牌的 NPC 對話即可開始對局。正常儲存遊戲以保留設定。

## 系統需求

PC 版《巫師 3》。請選擇 Classic 1.32 或 Next-Gen（標示 5.0+）對應的獨立建置包。遊玩不需要 REDkit、Wwise 或 EXE 安裝程式。

## 相容性

請刪除舊的 modBetaGwentReduxCompat 資料夾，獨立相容層已不再附帶。與 Redux/Redo Expansion 的相容性尚未單獨確認。其他昆特牌改動模組，以及修改選單、卡牌交易或獎勵的模組可能產生衝突。更改模組組合後，請用 Script Merger 重新合併指令碼。

## 回報問題

發現問題？請提供模組與遊戲的確切版本、選擇的文字與語音語言（包含自動模式）、是否為新遊戲＋、其他模組、涉及的卡牌／領導牌及重現步驟。截圖與問題發生前的存檔有助於排查。翻譯問題請註明語言與畫面，並提出更合適的表達。

### 如何啟用日誌

1. 在指向 witcher3.exe 的捷徑目標中，結尾引號後加入 -debugscripts。Steam：內容 → 一般 → 啟動選項。GOG 也能使用直接指向 witcher3.exe 的捷徑。

2. 啟動遊戲，重現問題後關閉遊戲。立即複製 scriptslog.txt，下次啟動會覆寫它。如果檔案只有標題，請說明；該建置可能還需要額外的日誌設定。

3. 若 Windows 產生了當機傾印，請同時附上最新的相關 .dmp 檔案。

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## 致謝

感謝 CD Projekt 帶來《巫師》和昆特牌，感謝 LegacyGwent DIY 提供卡牌和牌桌素材，感謝 Beta Gwent 社群保存歷史資料並分享牌組原型構想，也感謝每一位測試模組並提交詳細回報的玩家。

非官方粉絲專案。模組原創程式碼以 GPL-3.0-only 授權發布；遊戲原始素材歸各自所有者所有。

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)
