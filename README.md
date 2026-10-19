# Gwent Beta Classic

Version **0.9.0** brings standalone Gwent Beta 0.9.24 into The Witcher 3, with separate PC packages for **Classic 1.32** and **Next-Gen 5.0+**. This source snapshot matches **final9**, **ui9** and clipboard bridge **r7**.

479 collectible cards, including 21 leaders, all five factions, 46 opponent archetypes, editable starter decks and eight custom deck slots, crafting, kegs, NPC matches and controller support. Ordinary card artwork is static; leader portraits are animated.

## New in 0.9.0

- Native Windows clipboard import and export through the optional r7 bridge. Without `Optional-CopyButton/bin`, both exchange buttons are hidden. Preview and explicitly craft missing cards before importing a draft; Save keeps it.
- Faction and rarity banners, corrected power placement, a larger card inspection view and improved deck previews. Battle previews retain their accepted proportions.
- Ten tutorial pages in all 13 text languages, including mulligans, rows, neighbours and card statuses.
- Explicit profile cleanup with a saved guard against reinitialization after cleanup; incomplete inventory removal produces a single failure result.
- Corrected Myrgtabrakke and Harald the Cripple hit counts, plus the existing AI, controller, weather, audio and Classic compatibility work.

The offline final9 audit passed 1,426 tactical scenarios, 414 row-choice cases, 46 self-play matches, profile and cleanup fixtures, and 344 isolated native clipboard checks. ZIP hashes and every packaged file were verified. This does not replace a clean-install test in both games. Remaining findings include missing embedded glyphs in some CJK tutorial text, the old standalone Verify default, and an older CleanBuild export; see the [audit](docs/reviews/2026-10-19-final9-audit.md).

## Languages and installation

Each platform package includes 13 text languages and five voice languages (RU, EN, DE, IT, PT-BR). Select text and voices independently in the mod menu; save the game normally to retain your choices. Some older hints use English fallback; some DE/IT keg-troll lines retain the Russian source fallback.

Back up saves and replace the previous folders of this mod. Copy `Mods` into the game directory. Classic also requires the archive's `DLC/dlcBetaGwentClassic132Assets`. Use only the package matching your game branch. Rebuild conflicting script merges after changing mods.

- [Full description and installation (EN)](docs/releases/0.9.0/nexus/en/description.md) / [RU](docs/releases/0.9.0/nexus/ru/description.md)
- [Complete Nexus description: 13 languages, BBCode](docs/releases/0.9.0/nexus/NEXUS_DESCRIPTION_0.9.0.bbcode.txt)
- [Changelog (EN)](docs/releases/0.9.0/nexus/en/changelog.md) / [RU](docs/releases/0.9.0/nexus/ru/changelog.md)
- [Regression scenarios (RU)](docs/releases/0.8.2/regression/SCENARIOS_RU.md)
- [0.9.0 release hashes](docs/releases/0.9.0/release.json), [build and resource guide (RU)](docs/BUILD_0.9.0_RESOURCE_HANDOFF_RU.md), [audit (RU)](docs/reviews/2026-10-19-final9-audit.md)

## Source and build scope

This repository contains source code, generators, tests and documentation. Game clients, original art, fonts, voices, native resource templates, SDKs, private Wwise projects, release ZIPs, memory dumps and saves are excluded. Building requires the configured local Windows/REDkit toolchain and prepared resource snapshots; a clean clone alone is insufficient. See the [local dependency guide](docs/LOCAL_INPUTS_0.6.1.md) and the current build record above. Older stage documents describe their historical versions.

Runtime sources are in `BetaGwent/development/scripts`, shared Next-Gen UI in `BetaGwent/ui/src`, and prepared Classic scripts/UI in `BetaGwent/platforms/classic132`. `BetaGwent/native/clipboard` contains the optional bridge source. `tools/features082` contains the 0.9.0 checks, publication generators and packaging tools. The exact source hashes are recorded in [github090-sources.json](docs/evidence/github090-sources.json). Prepared art, sound and frozen templates remain local build inputs; they are not included in this repository.

## Contributing

Report the exact game/mod versions, text/voice settings, input device, involved cards and reproduction steps. For AI reports include the round, crowns, score, hands, public board and expected alternative. Preserve saved profile fields and preset IDs; change generators alongside generated code where applicable.

Original project code is GPL-3.0-only; see [LICENSE](LICENSE) and [ATTRIBUTIONS.md](ATTRIBUTIONS.md). Original game assets belong to their respective owners and are not relicensed under GPL.
