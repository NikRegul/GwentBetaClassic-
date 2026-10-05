# Gwent Beta Classic

The Witcher 3 Gwent replacement based on Gwent Beta **0.9.24**.
Russian and English packages, 479 collectible cards including 21 leaders,
five factions, saved deck builder, collection, NPC rewards, kegs and controller.

- [Русское описание и установка](BetaGwent/release/README_RU.md)
- [English description and installation](BetaGwent/release/README_EN.md)
- [Сборка](docs/BUILD_RU.md) / [Build guide](docs/BUILD_EN.md)
- [Устройство ИИ](docs/ARCHITECTURE_AI_RU.md) / [AI architecture](docs/ARCHITECTURE_AI_EN.md)
- [Контроллер](BetaGwent/release/CONTROLS_RU.md) / [Controls](BetaGwent/release/CONTROLS_EN.md)
- [Изменения 0.2.0](BetaGwent/release/CHANGELOG_RU.md) / [Changes](BetaGwent/release/CHANGELOG_EN.md)

**You must back up your saves before installing the mod and before every update. Bugs can still occur; use a separate test save for your first matches.**

Install **one** full RU or EN package under Mods/modBetaGwent0924. Source
checkout alone is not an installable mod. See Releases for packaged downloads
once uploaded. Players do not need REDkit or Wwise.

The owner installed and accepted the previous Russian battle build. This
revision fixes choice focus and adds four ordinary-NPC rewards plus English.
Its new gameplay paths need an installed-game acceptance pass. Current artwork,
animations and archetype heuristics will be refined towards the historical Beta.

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
