# Gwent Beta Classic

Version **0.8.2** brings standalone Gwent Beta 0.9.24 into The Witcher 3, with separate PC packages for **Classic 1.32** and **Next-Gen 5.0+**.

479 collectible cards, including 21 leaders, all five factions, 46 opponent archetypes, editable starter decks and eight custom deck slots, crafting, kegs, NPC matches and controller support. Ordinary card artwork is static; leader portraits are animated.

## New in 0.8.2

- Share decks through clipboard BG1 codes, preview missing cards and craft them explicitly. Import builds a draft; Save keeps it. Invalid codes change nothing.
- Console commands for card search, collections, scraps, kegs and innkeeper stock; start with `bg_help()`.
- Cards travel to their actual graveyard after death or special-card resolution.
- Improved menu spacing, translated exchange dialogs, and controller access from the visible card shelf to Save and back.
- Continuous leader portraits after VS entrances and voice-timed Arachas Queen entrances.
- Legacy Redux inventory definitions for loading older saves after switching mods; already lost inventory cannot be recovered.
- Accepted Classic frost and attack-effect fixes included.

## Languages and installation

Each platform package includes 13 text languages and five voice languages (RU, EN, DE, IT, PT-BR). Select text and voices independently in the mod menu; save the game normally to retain your choices. Some older hints use English fallback; some DE/IT keg-troll lines retain the Russian source fallback.

Back up saves and replace the previous folders of this mod. Copy `Mods` into the game directory. Classic also requires the archive's `DLC/dlcBetaGwentClassic132Assets`. Use only the package matching your game branch. Rebuild conflicting script merges after changing mods.

- [Full description and installation (EN)](docs/releases/0.8.2/nexus/en/description.md) / [RU](docs/releases/0.8.2/nexus/ru/description.md)
- [Complete Nexus description: 13 languages, BBCode](docs/releases/0.8.2/nexus/NEXUS_DESCRIPTION_0.8.2.txt)
- [Changelog (EN)](docs/releases/0.8.2/nexus/en/changelog.md) / [RU](docs/releases/0.8.2/nexus/ru/changelog.md)
- [Regression scenarios (RU)](docs/releases/0.8.2/regression/SCENARIOS_RU.md)
- [Build record, archive hashes and local-input requirements (RU)](docs/releases/0.8.2/BUILD_RU.md)

## Source and build scope

This repository contains source code, generators, tests and documentation. Game clients, original art, fonts, voices, native resource templates, SDKs, private Wwise projects, release ZIPs, memory dumps and saves are excluded. Building requires the configured local Windows/REDkit toolchain and prepared resource snapshots; a clean clone alone is insufficient. See the [local dependency guide](docs/LOCAL_INPUTS_0.6.1.md) and the current build record above. Older stage documents describe their historical versions.

Runtime sources are in `BetaGwent/development/scripts`, shared Next-Gen UI in `BetaGwent/ui/src`, and prepared Classic scripts/UI in `BetaGwent/platforms/classic132`. `tools/features082` contains the 0.8.2 checks, publication generators and packaging tools. Source snapshots and completed archives are preserved rather than overwritten.

## Contributing

Report the exact game/mod versions, text/voice settings, input device, involved cards and reproduction steps. For AI reports include the round, crowns, score, hands, public board and expected alternative. Preserve saved profile fields and preset IDs; change generators alongside generated code where applicable.

Original project code is GPL-3.0-only; see [LICENSE](LICENSE) and [ATTRIBUTIONS.md](ATTRIBUTIONS.md). Original game assets belong to their respective owners and are not relicensed under GPL.
