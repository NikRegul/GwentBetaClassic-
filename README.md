# Gwent Beta Classic 0.6.2

Gwent Beta 0.9.24 inside The Witcher 3: 479 collectible cards including 21 leaders, five factions, 46 opponent archetypes, saved custom decks, crafting, kegs, NPC rewards, and mouse/keyboard/controller support. The current target is PC Next-Gen 5.01; a separate 1.32 version is planned for 1.0 and is not yet supported.

0.6.2 adds action history, ability-chain highlights, smoother hand and controller focus, a large 2D leader scene, deck-editor explanations and undo, faster keg reveals, and session effect settings. It restores the Cursed Ships and Foltest deck-boost rosters and adjusts draw-spy scoring. The release retains 13 selectable text languages and animated portraits for 21 leaders. Ordinary card portraits remain static; original 3D leader entrances are still planned. The user confirmed the preceding 0.6.1 leader crash fix on RU.

## Languages and packages

Install **one** complete voice package: **EN, RU, DE, IT, or PT-BR**. Every package includes Russian, English, German, French, Italian, Polish, Spanish, Latin American Spanish, Brazilian Portuguese, Japanese, Korean, Simplified Chinese, and Traditional Chinese text. Text selection is independent of voices and persists with game saves. To change voices, install another voice package; runtime voice switching is not implemented. The keg troll uses Russian fallback in DE and IT.

Official beta card texts are used where available. New UI translations are a preview and need native-speaker feedback; ES-MX and Traditional Chinese UI include adaptations. Native inventory/merchant item names follow the game's text language.

## Build and test

From a configured local workspace, after any current build has finished:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\Build-All-0.6.2.ps1
```

Use `Build-0.6.2.ps1 -Language ru` for RU only. The full pipeline freezes source inputs, runs regressions, compiles native scripts and menus, packages the selected voices, and validates fresh archives, CRC, manifest and SHA-256. Existing selected archives and staging projects are preserved before rebuilding. Concurrent builds are locked. The script does not install or publish the mod.

- [Build instructions (RU)](docs/BUILD_0.6.2_RU.md)
- [New UI and manual checks (RU)](docs/UI_0.6.2_RU.md)
- [Manual acceptance checklist (RU)](docs/TESTING_0.6.1_RU.md)
- [Installation and controls (EN)](BetaGwent/release/publish-0.6.2/README_EN.md) / [RU](BetaGwent/release/publish-0.6.2/README_RU.md)
- [Changelog since 0.4.5 (EN)](BetaGwent/release/publish-0.6.2/CHANGELOG_0.4.5_to_0.6.2_EN.md) / [RU](BetaGwent/release/publish-0.6.2/CHANGELOG_0.4.5_to_0.6.2_RU.md)
- [Nexus description, 13 languages](BetaGwent/release/publish-0.6.2/NEXUS_DESCRIPTION_0.6.2.txt)
- [Leader crash diagnosis and retest (RU)](docs/reviews/2026-10-12-crash061-hotfix.md)
- [Roadmap (EN)](docs/ROADMAP.md) / [RU](docs/ROADMAP_1.0_RU.md)
- [Documentation index](docs/README.md)

The completed 0.6.2 RU build passed 52 regression suites, native compilation of 70 scripts and four menus, and ZIP/manifest/SHA-256 verification. The other four 0.6.2 voice packages have not yet been verified. In-game acceptance and comparison of the old and new AI remain separate work; no AI strength improvement is established by these build checks. Do not distribute quarantined archives. The obsolete Redux compatibility layer is excluded.

## Repository scope

The public repository contains source code, generators, tests and documentation. Original clients, art, fonts, audio, native resource templates, SDKs, private Wwise projects and release archives are excluded. A fresh clone needs those local inputs and the configured Windows/REDkit/Wwise toolchain; the build is not yet a portable one-command setup. Prepared `BetaGwent/build/languages137` dictionaries/fonts/voice inputs are local dependencies; see [the dependency guide](docs/LOCAL_INPUTS_0.6.1.md).

The old experiment animating all premium cards remains separate in `codex/premium-card-previews` in the development workspace. The current pipeline permits only 21 leader portraits and rejects ordinary premium resources.

## Contributing

For a bug, include the exact package/version, voice and text language, leader pair/decks, round/turn, input device, relevant actions and expected behavior. Prefer a short reproducible scenario and relevant log excerpt. Preserve saved profile fields and preset IDs; change generators rather than generated catalogs. Add a regression for a reproduced defect and validate changed native behavior in-game.

Original project code is GPL-3.0-only; see LICENSE and ATTRIBUTIONS.md in the public repository. Gwent/The Witcher names and original texts, art, sound and game resources belong to their respective owners and are not relicensed under GPL.
