# Gwent Beta Classic 0.2.4

Gwent Beta 0.9.24 inside The Witcher 3, with 479 collectible cards, 21 leaders,
five factions, saved decks, NPC rewards, kegs and controller support.

**Back up saves before installation and every update. Bugs can still occur.**

0.2.4 repairs Bloodcurdling Roar/Bear creation, stale pile choices, cyclic
resurrection candidates, full preferred rows, row-side validation and cursor
request ownership. Native menus use inline HD textures and an uncompressed
bundle. 0.2.3 opened in the installed game but did not render external textures;
installed-game acceptance of this new packaging hypothesis remains pending.

Fresh RU/EN script compilation, six menu builds and focused source checks are
separate from native battle/rendering acceptance. Original assets and Wwise
keys are excluded from this source repository; original code is GPL-3.0-only.

- [Current build sequence](docs/BUILD97.md)
- [Acceptance / Russian](docs/PRESENTATION97_RU.md)
- [Acceptance / English](docs/PRESENTATION97_EN.md)
- [Manual AI editing / Russian](docs/AI_MANUAL95_RU.md)
- [Nexus and Steam preparation](docs/PUBLISH97_RU.md)

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
