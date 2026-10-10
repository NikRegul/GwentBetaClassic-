# Gwent Beta Classic 0.4.3

Gwent Beta 0.9.24 inside The Witcher 3: 479 collectible cards, 21 leaders,
five factions, editable saved decks, NPC matches, card collecting and controller support.
Targets PC game version 5.01. Install one language package at a time.

0.4.3 prevents self-consumption and fixes Morkvarg returning with zero strength.
Shuffling a weakened card preserves its strength. AI target selection, Vran food
chains, spy placement, empty Ointment choices and weather replacement are corrected.
The 46-deck opponent rotation persists with saves, and Cursed Adda has two tactics.

Ability choices use the mulligan-style grid with board inspection during a pending
choice. Craft buttons appear directly on cards and work before NPC matches;
controller focus and row
navigation are corrected, and frost/rain presentation and timer alignment improved.
The local changelog also records the preceding 0.4.2 fixes.

- [0.4.3 changelog / English](BetaGwent/release/publish-0.4.3/CHANGELOG_EN.md)
- [0.4.3 changelog / Russian](BetaGwent/release/publish-0.4.3/CHANGELOG_RU.md)
- [0.4.3 validation / English](docs/PRESENTATION123_EN.md)
- [0.4.3 validation / Russian](docs/PRESENTATION123_RU.md)
- [PowerShell build script](tools/Build-0.4.3.ps1)
- [AI comparison script](tools/Compare-AI.ps1)
- [Completed 0.4.1 vs 0.4.2 comparison](docs/AI_COMPARISON_041_042_REVIEW_RU.md)
- [Build guide / Russian](docs/BUILD_RU.md) / [English](docs/BUILD_EN.md)

The completed 0.4.2 versus 0.4.1 comparison scored 50.35% over 1,840 games;
this does not establish overall superiority. 0.4.3 regression checks validate
corrected situations, not an overall playing-strength improvement.

Native script/menu compilation and archive checks are verified during the build.
Installed-game visuals, controller operation and native save round trips still
require acceptance testing. Back up saves before installation and updates.

This repository contains source code and documentation. Original clients,
textures, fonts, audio, native templates, tool SDKs and Wwise license keys are
excluded. A fresh clone needs those local build inputs. Original code is GPL-3.0-only.

## Contributing

Use Issues for bugs and strategy examples; include language/version, deck,
round, score, controller/mouse, recent actions and expected behavior. Submit
focused PRs. Modify generators instead of generated tables, preserve saved
field/preset identities, compile with REDkit and describe relevant validation.
Source-only publication intentionally excludes original clients, depot,
art/audio assets, SDKs, native resource templates and Wwise licenses. A fresh
clone needs those local build inputs; current setup is not fully portable.

Original project code is GPL-3.0-only; see LICENSE and ATTRIBUTIONS.md.
Gwent/The Witcher names, original card texts, art, sound and game resources
belong to their respective owners and are not relicensed under GPL.
