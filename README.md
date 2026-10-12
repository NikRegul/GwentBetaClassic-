# Gwent Beta Classic 0.6.1

Gwent Beta 0.9.24 inside The Witcher 3: 479 collectible cards including 21 leaders, five factions, 46 opponent archetypes, saved custom decks, crafting, kegs, NPC rewards, and mouse/keyboard/controller support. The current target is PC Next-Gen 5.01; a separate 1.32 version is planned for 1.0 and is not yet supported.

0.6.1 adds 13 selectable text languages and animated leader portraits on the battlefield and in card previews. Ordinary card portraits remain static. Large character entrance animations are a separate future feature. The leader crash hotfix removes unsafe disposal of engine-owned images and defers resource unloading; the user confirmed the corrected RU build no longer crashes in their retest.

## Languages and packages

Install **one** complete voice package: **EN, RU, DE, IT, or PT-BR**. Every package includes Russian, English, German, French, Italian, Polish, Spanish, Latin American Spanish, Brazilian Portuguese, Japanese, Korean, Simplified Chinese, and Traditional Chinese text. Text selection is independent of voices and persists with game saves. To change voices, install another voice package; runtime voice switching is not implemented. The keg troll uses Russian fallback in DE and IT.

Official beta card texts are used where available. New UI translations are a preview and need native-speaker feedback; ES-MX and Traditional Chinese UI include adaptations. Native inventory/merchant item names follow the game's text language.

## Build and test

From a configured local workspace, after any current build has finished:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\Build-0.6.1.ps1 -Language all -RebuildExisting
```

Use `-Language ru` for RU only. The full pipeline freezes source inputs, runs regressions, compiles native scripts and menus, packages the selected voices, and validates fresh archives, CRC, manifest and SHA-256. Existing selected archives and staging projects are preserved before rebuilding. Concurrent builds are locked. The script does not install or publish the mod.

- [Build instructions (RU)](docs/BUILD_0.6.1_RU.md)
- [Manual acceptance checklist (RU)](docs/TESTING_0.6.1_RU.md)
- [Installation and controls (EN)](BetaGwent/release/publish-0.6.1/README_EN.md) / [RU](BetaGwent/release/publish-0.6.1/README_RU.md)
- [Changelog (EN)](BetaGwent/release/publish-0.6.1/CHANGELOG_EN.md) / [RU](BetaGwent/release/publish-0.6.1/CHANGELOG_RU.md)
- [Leader crash diagnosis and retest (RU)](docs/reviews/2026-10-12-crash061-hotfix.md)
- [Roadmap (EN)](docs/ROADMAP.md) / [RU](docs/ROADMAP_1.0_RU.md)
- [Documentation index](docs/README.md)

Automated compilation and artifact checks do not establish complete in-game acceptance. The latest completed hotfix verification ran 49 regression suites and checked RU; the user's subsequent five-package build and the broader manual checklist require their own results. Do not distribute quarantined archives. The obsolete Redux compatibility layer is excluded.

## Repository scope

The public repository contains source code, generators, tests and documentation. Original clients, art, fonts, audio, native resource templates, SDKs, private Wwise projects and release archives are excluded. A fresh clone needs those local inputs and the configured Windows/REDkit/Wwise toolchain; the build is not yet a portable one-command setup. Prepared `BetaGwent/build/languages137` dictionaries/fonts/voice inputs are local dependencies; see [the dependency guide](docs/LOCAL_INPUTS_0.6.1.md).

The old experiment animating all premium cards remains separate in `codex/premium-card-previews` in the development workspace. The current pipeline permits only 21 leader portraits and rejects ordinary premium resources.

## Contributing

For a bug, include the exact package/version, voice and text language, leader pair/decks, round/turn, input device, relevant actions and expected behavior. Prefer a short reproducible scenario and relevant log excerpt. Preserve saved profile fields and preset IDs; change generators rather than generated catalogs. Add a regression for a reproduced defect and validate changed native behavior in-game.

Original project code is GPL-3.0-only; see LICENSE and ATTRIBUTIONS.md in the public repository. Gwent/The Witcher names and original texts, art, sound and game resources belong to their respective owners and are not relicensed under GPL.
