# Building Gwent Beta Classic

Read BUILD_RU.md for the detailed, confirmed sequence and ARCHITECTURE_AI_EN.md
for AI modifications. This repository contains source, generators and design
data. It does not contain game clients, a depot, copyrighted artwork/audio,
SDK binaries, native menu templates or a Wwise license.

Use Windows, Python 3.13 with UTF-8, Java, REDkit 5.0.1044630, Apache Royale
0.9.12 + playerglobal 0.9.12, and REDkit's GFx exporter. Asset tooling uses
Pillow and UnityPy. Audio rebuilding uses licensed Wwise 2023.1.19.8928,
vgmstream-r2117 and wwiser. Players need none of these tools.

Several historical recon/UI scripts still use the confirmed local installation
paths (D:/w3mod and D:/GOG Galaxy/Games/The Witcher 3 REDkit). Adjust these and
board-config.xml for your machine. A fully portable bootstrap is not provided
yet. A native resource template and editor project must be prepared in REDkit
or bootstrapped from the release bundle using Wcc unbundle. The packaging tool
currently needs BetaGwent/build/release87/project/BetaGwent0924 as its base.
Build directories and that native project are excluded from Git.

Canonical definitions are generated from locally available Beta 0.9.24 assets
by tools/import_beta924.py. Required normalized catalog SHA256:
022539802636cb45e92123a630c3788a0674c39b538fa1f69a64761a6b3ddbd3.
Current DIY definitions are not equivalent to the historical Beta rules.
DIY artwork and the original Beta client audio are external local inputs.

## Order

```powershell
python tools/build_progression.py
python tools/build_full_catalog.py
python tools/build_ai_rules.py
python tools/build_duel_catalog.py
python tools/build_full_catalog.py
python tools/build_shop_cards.py
```

Keep handwritten WS under BetaGwent/scripts and BetaGwent/development/scripts.
The development folder's name is historical; it contains release gameplay.
Do not edit generated duelCatalog, duelAICatalog or CardText tables by hand.
Copy both WS source sets and tools/core-check/src/coreChecks.ws to
BetaGwent/build/board-patch/game/betagwent and the project scripts folder.
Current complete compilation contains 60 WS files.

```powershell
python tools/recon/run_redkit_compile.py --out BetaGwent/build/board-compile89a --patch BetaGwent/build/board-patch --timeout 120 --terms-already-accepted
python tools/ui/build_menu_pack.py --apply
```

Use a fresh compile output directory and only pass the terms flag after a human
accepted the EULA. Check result.json AND explicit script compiler success;
the wrapper process itself can exit successfully even if Wcc reports an error.
The UI is compiled AS3 → SWF → GFx/DDS → validated CR2W/redswf. All three
entry movies and 44 bridge bindings are required.

For a full audio rebuild:

```powershell
python tools/recon/extract_beta_audio.py --decode-voices
python tools/ui/prepare_audio_import.py --full
python tools/ui/build_audio_bank.py --console "C:\Audiokinetic\Wwise_2023.1.19.8928\images\Authoring\x64\Release\bin\WwiseConsole.exe" --install
```

Original bank128 data is extraction input, not a runtime bank. Build the
additional BetaGwent79 bank; never replace the game's Init.bnk. Keep the license
local. After audio activation, synchronize and recompile the scripts.

For fixed-language packages:

```powershell
python tools/prepare_english89.py
python tools/merge_english89.py
python tools/localization89.py sources
python tools/ui/build_english_audio89.py
python tools/build_language_release.py prepare --language ru
python tools/prepare_en_ui89.py
```

The indexed translation helper is tied to the initial translation-index input.
For later strings, update english89.json directly. Original EN names, rule text,
tags and glossary come from en_us. The English preparation compiles EN scripts,
builds three EN movies, freezes the EN project, then restores the RU workspace.

For each language, run in order:

```powershell
python tools/build_language_release.py cook --language ru
python tools/build_language_release.py strings --language ru
python tools/build_language_release.py audio --language ru
python tools/build_language_release.py dependencies --language ru
python tools/build_language_release.py pack --language ru
python tools/build_language_release.py metadata --language ru
python tools/build_language_release.py archive --language ru
```

Repeat with en. Packaging freezes input hashes, cooks resources and item strings,
builds soundspc.cache, dep.cache, LZ4HC bundles and metadata.store, then adds the
appropriate compiled blob and docs. ZIP CRC and per-file SHA256 are checked.
Update stage/version and compiler paths for future revisions; do not overwrite
frozen inputs or mix scripts and movies from different revisions.

For focused AI checks, use check_ai_rules.py and check_pass_policy.py under
tools/core-check. Installed-game acceptance is still needed for UI, quest
integration, rewards, controller behavior and save/reload. Compilation and
isolated policy tests do not establish every card interaction.


0.2.1 / stage94: see [BUILD_POLISH94.md](BUILD_POLISH94.md), [Russian changes](PRESENTATION94_RU.md) and [English changes](PRESENTATION94_EN.md).
