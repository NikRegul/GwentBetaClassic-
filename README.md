# Gwent Beta Classic 0.3.0

Gwent Beta 0.9.24 inside The Witcher 3: 479 collectible cards, 21 leaders,
five factions, saved decks, NPC rewards, kegs and controller support.

**Back up saves before installation and every update. Bugs can still occur.**

0.3.0 brings the battlefield close to the original Beta (fonts, card frames, HUD,
mulligan screen, leader intro, row weather, simultaneous multi-target effects,
spying/revealed tokens, widescreen panels) and a new AI that simulates its
candidate plays on a cloned session before choosing. See
[the changelog](BetaGwent/release/CHANGELOG_EN.md).

AI development: `tools/ai` transpiles the WitcherScript rules to JavaScript
(`ws2js.py`, `build_js.py`) for headless self-play, A/B tests (`jshost/ab.js`)
and tuning runs (`Train-AI-JS.ps1`, Node.js required). `gen_clone.py` generates
the session cloner used by the in-game lookahead.

Original images, audio, fonts and Wwise keys are excluded. Original code is GPL-3.0-only.

- [Build guide / Russian](docs/BUILD_RU.md) · [English](docs/BUILD_EN.md)
- [AI architecture / Russian](docs/ARCHITECTURE_AI_RU.md) · [English](docs/ARCHITECTURE_AI_EN.md)

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
