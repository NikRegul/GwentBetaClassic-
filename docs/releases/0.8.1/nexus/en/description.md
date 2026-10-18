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
