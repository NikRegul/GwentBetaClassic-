# Gwent Beta Classic 0.4.1

Gwent Beta 0.9.24 inside The Witcher 3: 479 collectible cards, 21 leaders,
five factions, editable saved decks, NPC matches, card collecting and controller support.

**Back up saves before installation and every update. Bugs can still occur.**

0.4.1 restores gold ornaments and fittings by baking the camera-facing surfaces
of all ten original faction board halves. It retains the single horizontal
reflection, adds original hand/leader separators, improves score typography,
animates the original hit sheet and routes weather impacts to dedicated sounds.
Locked cards retain and display their lock in the graveyard. Atlas dimensions
and card resolution are unchanged. Packages target PC game version 5.01.

Changes since 0.3.4 also include researched deck rosters and AI strategies,
46-archetype checks, decision logging, reproducible AI comparison, action previews,
animation settings and unified card/deck/graveyard selection screens.

- [Cumulative changelog / English](BetaGwent/release/publish-0.4.1/CHANGELOG_0.3.4_to_0.4.1_EN.md)
- [Cumulative changelog / Russian](BetaGwent/release/publish-0.4.1/CHANGELOG_0.3.4_to_0.4.1_RU.md)
- [0.4.1 build and acceptance notes / English](docs/PRESENTATION120_EN.md)
- [0.4.1 build and acceptance notes / Russian](docs/PRESENTATION120_RU.md)
- [0.4.0 AI tools and configuration](docs/PRESENTATION119_EN.md)
- [PowerShell build script](tools/Build-0.4.1.ps1)
- [Build guide / Russian](docs/BUILD_RU.md) / [English](docs/BUILD_EN.md)
- [AI architecture / Russian](docs/ARCHITECTURE_AI_RU.md) / [English](docs/ARCHITECTURE_AI_EN.md)

Native menus, script compilation and archive checks are verified during the
build. Visual, audio and controller acceptance still require installed-game
testing. A literal recreation of Unity shaders/particles is not claimed.

This repository contains source code and documentation. Original clients,
textures, fonts, audio, native templates, tool SDKs and Wwise license keys are
excluded. The local build needs those inputs; a fresh clone is not a complete
standalone build environment. Original code is GPL-3.0-only.

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
