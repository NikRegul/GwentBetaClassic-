# Gwent Beta Classic 0.2.6

Gwent Beta 0.9.24 inside The Witcher 3: 479 collectible cards, 21 leaders,
five factions, saved decks, NPC rewards, kegs and controller support.

**Back up saves before installation and every update. Bugs can still occur.**

Russian 0.2.5 editor/NPC startup was accepted in the installed game. Compact
native menus remain below 55 MiB; cards are 288×405 and faction board halves
1536×531. Game memory settings are unchanged. 0.2.6 changes atlas sampling,
the native Bitmap fallback, card selection borders and controller body bounds.
Visual flicker/border acceptance and English acceptance still need testing.

Both packages retain the nested-play/cursor fixes from 0.2.4. Card rules and AI
are unchanged. RU sources match the reused stage97 compilation; EN voice durations
are synchronized with the English bank and freshly compiled in stage99. Six
native menus are rebuilt. Package checks do not replace native battle tests.
Original images, audio and Wwise keys are excluded. Original code is GPL-3.0-only.

- [Current build sequence](docs/BUILD99.md)
- [Russian acceptance notes](docs/PRESENTATION99_RU.md)
- [English acceptance notes](docs/PRESENTATION99_EN.md)
- [Manual AI editing / Russian](docs/AI_MANUAL95_RU.md)
- [Nexus and Steam preparation](docs/PUBLISH99_RU.md)

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
