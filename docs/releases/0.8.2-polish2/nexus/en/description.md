# Gwent Beta Classic 0.8.2 — English

> Version 0.8.2 — separate packages for Classic 1.32 and Next-Gen 5.0+.

## Important

Back up your saves before installing and before every update. The mod is in active development, so use a separate save for your first matches.

Card texts use the official Beta localization. The mod interface includes AI-assisted translations and may contain wording errors. Deck exchange messages are available in all 13 text languages; some older hints still fall back to English. Suggestions for better translations are welcome.

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

## New in 0.8.2

- Import and export decks as BG1 text codes through the clipboard, with a list of missing cards and an explicit crafting action.
- Console commands for collection resources, card lookup, faction collections and innkeeper keg stock.
- Cards sent to the graveyard now fly toward their actual graveyard; resolved special cards do the same. Banish and dissolve effects are preserved.
- Built-in definitions for legacy Redux inventory items help prevent inventory/body loss when loading an older save after switching mods. They cannot recover inventory already lost and saved.
- Reworked menu spacing, deck status text and action buttons; controller navigation can reach Save from the visible card shelf and return to cards.
- Leader portraits continue animating after their VS entrance. Arachas Queen's entrance starts with her voice playback. Classic 1.32 includes the frost and attack effect fixes.

## Sharing decks

Open Export in the deck editor to copy the BG1 code, then share it as text. Import is available in both the deck list and editor. Paste the complete code; an invalid code changes nothing. If clipboard access is unavailable, use Ctrl+C/Ctrl+V in the text field. BG1 codes belong to this mod and are independent of the interface language.

Missing cards, including the leader, are listed with the total scrap cost. Crafting requires a separate confirmation and enough scraps. Import builds a draft: use Save Deck to keep it. Import from the deck list uses a free custom slot and does not overwrite occupied slots. In training, the existing unrestricted collection is used.

## Console commands

Use bg_help() for help and bg_status() for your collection, kegs and scraps. bg_find('Imlerith') searches card names and IDs; bg_card(132102,1) grants a card, bg_faction('monsters') grants a faction, and bg_leaders() / bg_allcards() fill the leader/full collection up to normal copy limits. bg_kegs(10) and bg_scraps(1000) add resources. Resource grants require a loaded save outside menus and matches; save the game normally afterward. With an innkeeper's shop open, bg_shopcheck() diagnoses keg stock and bg_shoprefill(5) brings it up to five rather than adding five on every call. The game console must already be enabled.

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

## Languages

Text: English, Russian, German, French, Italian, Polish, Spanish (Spain), Spanish (Latin America), Portuguese (Brazil), Japanese, Korean, Simplified Chinese and Traditional Chinese. Switch any time with the text language button at the top left of the deck and collection menus or in the battle settings; your choice is saved.

Each package includes RU, EN, DE, IT and PT-BR voices. Select Text and Voice independently using the two separate buttons in the mod's deck/collection menu; the choices are also available in the match settings. Switching voices does not require reinstalling files. Auto follows the game's current text and speech languages separately; if a language is unavailable, English is used. Save the game normally after choosing: preferences belong to that save and remain when the mod files are updated. An existing manual text choice is preserved. In DE and IT, some keg-troll lines retain the Russian fallback from the source recordings. Native item names still follow the game language, and some notifications outside the mod UI remain RU/EN.

## Installation

1. Close the game and back up your saves. Download the package for your game branch: 1.32 or Next-Gen (5.0+). Install only one Beta Gwent version.

2. When updating, move the previous Beta Gwent mod folder outside Mods first. Do not remove the entire Mods folder or mix files from different versions.

3. Copy Mods from the archive into the game directory, next to bin and content. For Classic 1.32, also copy the included DLC folder. Paths: Mods/modBetaGwentClassic132/content and DLC/dlcBetaGwentClassic132Assets for 1.32; Mods/modBetaGwent0924/content for Next-Gen. Replace only this mod's previous folders, keeping your other mods and DLC.

4. Load your save. Open the normal Gwent deck menu to edit decks and choose text/voices, or talk to a Gwent-playing NPC to start a match. Save normally to retain your preferences.

## Requirements

The Witcher 3 on PC. Choose the separate build for Classic 1.32 or Next-Gen (package labelled 5.0+). REDkit, Wwise and an EXE installer are not needed to play.

## Compatibility

Legacy Redux item definitions are included for save loading; remove the obsolete modBetaGwentReduxCompat folder. When switching from Redux, use a backed-up save from before any inventory/body loss: definitions cannot restore data already lost. Redux cards are not converted into the Beta collection, and this is not a promise of compatibility with every Redux/Redo Expansion feature. Other Gwent overhauls and mods changing its menus, trading or rewards may conflict. After changing mods, rebuild conflicting script merges with Script Merger.

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


## AI catch-up, engines and weather

After the opponent passes, catch-up uses real play simulation: targets, armour, damage, deaths, ability chains, turn-end effects and the next turn-start weather. The final pass ends the round without another AfterTurn tick. When the human is still playing, their next card is unknown; public board effects and plausible replies inform evaluation.

Igni compares the row threshold and actual burn targets. Yrden evaluates resets on both sides. Birna forecasts available turns, armour depletion, deaths and shifting row order, including Redanian Knight armour renewal, Redanian Elite's +5 and the Squire's adjacent boosts. Removing armour can benefit the enemy. Traps consider row capacity; weather movement includes the effect lost at the origin and replaced at the destination.

Winning round one one card down is acceptable; two cards down requires context. Optional post-pass chasing stops at a three-card disadvantage. Avoiding match defeat overrides resource preservation. These policies do not promise perfect play in every possible state.

## Why the Classic 1.32 download is larger and needs DLC

Classic and Next-Gen use different native resource formats and loaders. Classic has an approximately 32 MiB limit per asynchronously loaded resource. Large menus and graphics therefore need a layout suitable for the old engine, separate pages and additional texture bindings. Compressing the ZIP cannot bypass the engine's resource-size check.

DLC/dlcBetaGwentClassic132Assets is an essential technical asset package, including leader entrance pages and Classic loader registration. It adds no story content and does not replace either official expansion. Install it into the game's DLC directory, alongside Mods/modBetaGwentClassic132. Missing it can leave interface or animation resources unavailable. Next-Gen uses Mods/modBetaGwent0924; install only the package for your game version.

The preceding 0.8.2 rebuild measured about 623 MB for Classic and 448 MB for Next-Gen (decimal MB). About 105 MB of Classic's compressed archive was its DLC folder. That DLC bundle holds 336 entries and is about 191 MB before ZIP compression. The remaining difference comes from old-engine resource preparation and packaging, not extra cards or different AI rules. See Files and checksums for exact current sizes. Players do not need REDkit, Wwise or build tools.

## Redux inventory compatibility: exact scope

Loading an old save requires definitions for item names already stored in its inventory. Removing a mod that supplied those names could corrupt loading, including disappearing inventory/body symptoms. The audited list covers 400 names: 197 already have native definitions, while 203 missing names receive inert placeholders in both items and items_plus for ordinary play and NG+.

Native definitions are not replaced. Placeholders have no equipment/hold slot, entity template, actions or abilities; they are hidden, weightless and have no value. This supports deserialization of legacy items. It does not convert Redux cards into the Beta Gwent collection or guarantee compatibility with every Redux/Redo Expansion feature.

Load a backup from BEFORE the loss. Already lost and saved items cannot be recovered by these definitions. The old separate modBetaGwentReduxCompat folder is unnecessary beside full 0.8.2. Other Gwent/menu/trading/reward overhauls can still conflict; update Script Merger merges after changing mods.

## Updating, saves and uninstalling

Back up saves first. Replace only this mod's own folders completely, using the correct platform package; update its DLC folder on Classic too. Do not mix versions or delete unrelated Mods/DLC.

Collection, decks, scraps, kegs, settings and rewards have saved fields and facts mirrors. Removing the mod alone does not erase that progress: reinstalling can restore it. A separate temporary cleaner and instructions are provided; cleanup requires an explicit console command and never runs merely by installing the main mod. Completed quests, achievements and spent crowns are not rolled back.

Orphaned NPC reward facts require the optional read-only save fact scanner and its generated cleanup commands. It does not edit or upload the save. Without checking those keys, complete physical removal of historical records cannot be guaranteed. If legacy Redux inventory items remain after uninstalling these definitions, reinstall their original definition provider, such as Redux, before loading.

## Validation limits

Checks target 0.8.2: all 46 decks, targets/rows, round economy, hidden information, card chains, weather and the three Redanian abilities. UI checks cover compilation, bindings, resource budgets, source mirrors, layout and translated button fitting after font loading.

Native compilation, container checks and host scenarios do not replace gameplay acceptance: loading your save, an NPC match, saving/restarting and visual checks at your resolution. No finite test suite covers every game state. Bug reports should include game/mod versions, decks/cards, move order, languages, other mods and a screenshot; a save immediately before the issue is especially useful.

## Credits

Thanks to CD Projekt for The Witcher and Gwent, LegacyGwent DIY for card and board assets, the Beta Gwent community for preserving historical material and archetype ideas, and everyone who tests the mod and sends detailed reports.

Unofficial fan project. Original mod code is GPL-3.0-only; original game assets belong to their owners.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)
