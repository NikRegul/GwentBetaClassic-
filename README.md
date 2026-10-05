# Gwent Beta Classic

The Witcher 3 Gwent replacement based on Gwent Beta **0.9.24**.
Russian and English packages, 479 collectible cards including 21 leaders,
five factions, saved deck builder, collection, NPC rewards, kegs and controller.

- [Русское описание и установка](BetaGwent/release/README_RU.md)
- [English description and installation](BetaGwent/release/README_EN.md)
- [Сборка](docs/BUILD_RU.md) / [Build guide](docs/BUILD_EN.md)
- [Устройство ИИ](docs/ARCHITECTURE_AI_RU.md) / [AI architecture](docs/ARCHITECTURE_AI_EN.md)
- [Контроллер](BetaGwent/release/CONTROLS_RU.md) / [Controls](BetaGwent/release/CONTROLS_EN.md)
- [Изменения 0.2.1](BetaGwent/release/CHANGELOG_RU.md) / [Changes](BetaGwent/release/CHANGELOG_EN.md)

**You must back up your saves before installing the mod and before every update. Bugs can still occur; use a separate test save for your first matches.**

Install **one** full RU or EN package under Mods/modBetaGwent0924. Source
checkout alone is not an installable mod. See Releases for packaged downloads
once uploaded. Players do not need REDkit or Wwise.

## 0.2.1

HD Beta boards and deck-builder skins, 384x540 artwork, source-resolution
weather/hit frames, separate death/consume effects, White Frost presentation
fix, conservative leader/pass ordering and armor-aware Seltkirk estimates,
controller hand/placement/target navigation, transparent HD target highlights,
native RMB inspection/cancel routing and Aglais replay/banish ordering.
Save schema and deck IDs preserved.

Fresh RU/EN script compilation, six native menu builds, DDS/ABC/bridge checks,
25 policy cases,10 Aglais sequencing cases and package integrity checks passed.
Installed-game visual,
controller and battle acceptance of this revision remains pending.

- [Changes and acceptance: Russian](docs/PRESENTATION94_RU.md)
- [Changes and acceptance: English](docs/PRESENTATION94_EN.md)
- [Current build sequence and AI details](docs/BUILD_POLISH94.md)

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
