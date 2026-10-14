# Gwent Beta Classic

RU test build **0.6.6 / Stage 142** is ready: [archive](BetaGwent/release/GwentBetaClassic-0.6.6-RU.zip), [changes and game checks](docs/PRESENTATION142_RU.md), [effect catalog](docs/SPECIAL_VFX_0.6.6_RU.md), [build](docs/BUILD_0.6.6_RU.md). Includes special-card effects, unified weather casts, simultaneous triggered boosts, 12 original leader entrance clips with nine animated loop fallbacks, a stable leader preview, history/target hints, kegs at all innkeepers and the combined AI fixes. 50 regression suites, native compilation of 70 scripts and four menus, and archive/source/resource/audio checks passed (`docs/evidence/validation142.json`). In-game acceptance is pending. The complete five-voice release remains 0.6.3.

Gwent Beta 0.9.24 inside The Witcher 3: 479 collectible cards including 21 leaders, five factions, 46 opponent archetypes, saved custom decks, crafting, kegs, NPC rewards, and mouse/keyboard/controller support. The current target is PC Next-Gen 5.01; a separate 1.32 version is planned for 1.0 and is not yet supported.

0.6.3 fixes the AI spending a rare card after a pass when a cheap winning answer was excluded by the search cap. Card movement between rows and sides now follows an arc; flips keep a fixed center, departing cards retain their frames, and arrival effects, numbers and audio share the correct timing during accelerated chains. Text, voices, rosters and card rules are unchanged from 0.6.2, which passed the user's initial in-game check. The release retains animated portraits for 21 leaders; ordinary card artwork remains static.

## Languages and packages

Install **one** complete voice package: **EN, RU, DE, IT, or PT-BR**. Every package includes Russian, English, German, French, Italian, Polish, Spanish, Latin American Spanish, Brazilian Portuguese, Japanese, Korean, Simplified Chinese, and Traditional Chinese text. Text selection is independent of voices and persists with game saves. To change voices, install another voice package; runtime voice switching is not implemented. The keg troll uses Russian fallback in DE and IT.

Official beta card texts are used where available. New UI translations are a preview and need native-speaker feedback; ES-MX and Traditional Chinese UI include adaptations. Native inventory/merchant item names follow the game's text language.

## Build and test

From a configured local workspace, after any current build has finished:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\Build-0.6.3.ps1 -Language all
```

Use `-Language ru` for RU only, or `-Step verify -Language all` to check existing packages. This pipeline requires the prepared stage139 snapshots and regression reports; run `tools/check_work139.py` separately when preparing them. It checks those inputs, compiles native scripts and menus, packages the selected voices, and validates archives, CRC, manifest and SHA-256. Existing 0.6.3 archives cannot be overwritten; a new revision needs a new version. Concurrent builds are locked. The script does not install or publish the mod.

- [Build instructions (RU)](docs/BUILD_0.6.3_RU.md)
- [AI, animation changes and manual checks (RU)](docs/AI_ANIMATIONS_0.6.3_RU.md)
- [Manual acceptance checklist (RU)](docs/TESTING_0.6.1_RU.md)
- [Installation and controls (EN)](BetaGwent/release/publish-0.6.3/README_EN.md) / [RU](BetaGwent/release/publish-0.6.3/README_RU.md)
- [0.6.3 changelog (EN)](BetaGwent/release/publish-0.6.3/CHANGELOG_EN.md) / [RU](BetaGwent/release/publish-0.6.3/CHANGELOG_RU.md)
- [Changelog since 0.4.5 (EN)](BetaGwent/release/publish-0.6.2/CHANGELOG_0.4.5_to_0.6.2_EN.md) / [RU](BetaGwent/release/publish-0.6.2/CHANGELOG_0.4.5_to_0.6.2_RU.md)
- [Historical 0.6.2 Nexus description, 13 languages](BetaGwent/release/publish-0.6.2/NEXUS_DESCRIPTION_0.6.2.txt)
- [Leader crash diagnosis and retest (RU)](docs/reviews/2026-10-12-crash061-hotfix.md)
- [Roadmap (EN)](docs/ROADMAP.md) / [RU](docs/ROADMAP_1.0_RU.md)
- [Documentation index](docs/README.md)

0.6.3 passed 39 regression suites, including 1,070 animation checks and 36 checks of the reproduced AI defect. A paired comparison across 184 games and all 46 archetypes ended 92:92 with no errors; it does not establish an overall AI strength improvement. Native compilation passed for all five sets of 70 scripts and four menus. All five packages passed ZIP/manifest/SHA-256 and source/resource verification; the completed report is `docs/evidence/validation139.json`. Previous 0.6.2 archives are unchanged. In-game acceptance of the new visual behavior remains open. The obsolete Redux compatibility layer is excluded.

## Repository scope

The public repository contains source code, generators, tests and documentation. Original clients, art, fonts, audio, native resource templates, SDKs, private Wwise projects and release archives are excluded. A fresh clone needs those local inputs and the configured Windows/REDkit/Wwise toolchain; the build is not yet a portable one-command setup. Prepared `BetaGwent/build/languages137` dictionaries/fonts/voice inputs are local dependencies; see [the dependency guide](docs/LOCAL_INPUTS_0.6.1.md).

The old experiment animating all premium cards remains separate in `codex/premium-card-previews` in the development workspace. The current pipeline permits only 21 leader portraits and rejects ordinary premium resources.

## Contributing

For a bug, include the exact package/version, voice and text language, leader pair/decks, round/turn, input device, relevant actions and expected behavior. Prefer a short reproducible scenario and relevant log excerpt. Preserve saved profile fields and preset IDs; change generators rather than generated catalogs. Add a regression for a reproduced defect and validate changed native behavior in-game.

Original project code is GPL-3.0-only; see LICENSE and ATTRIBUTIONS.md in the public repository. Gwent/The Witcher names and original texts, art, sound and game resources belong to their respective owners and are not relicensed under GPL.
