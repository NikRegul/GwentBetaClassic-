# Rebuilding 0.2.1 / stage94

This extends the HD pipeline in HD_PRESENTATION_PIPELINE93.md. Source-only Git
excludes original game/DIY assets, depot, resource templates, compiled outputs,
SDK binaries, audio and license keys. Keep these local prerequisites.

1. From the repository root, run `python -X utf8 tools/ui/prepare_board_scripts.py`.
   It stages 60 current WitcherScript files and checks for unprepared project edits.
2. For artwork generation use `python -X utf8 tools/ui/build_card_art.py`.
   It now calls `build_hd_art94.py`: cards384×540 (70/page), original boards2048×708,
   native-size Beta UI and49 original weather/hit frames. With existing extraction
   manifests, `build_hd_art94.py` alone is enough.
3. Run `python -X utf8 tools/build_presentation94.py` sequentially. It prepares
   isolated English text/voice lookup sources, builds all three EN then RU movies,
   verifies44 bridge bindings and embeds DDS by actual exporter image IDs. RU
   resources are installed only into the REDkit project. Do not edit UI while it runs.
4. Freshly compile both script sets with `tools/recon/run_redkit_compile.py`:
   RU patch `BetaGwent/build/board-patch`; EN patch
   `BetaGwent/build/stage94/en/en-source/scripts`; output to fresh directories
   `BetaGwent/build/board-compile94ru` and `board-compile94en`. Add
   `--terms-already-accepted` only when the human accepted the Wcc terms.
   A clean script-success marker, no Script errors and60 matching source hashes
   are required. Do not reuse the stage90 blob: gameplay changed.
5. Run `python -X utf8 tools/package_presentation94.py`. It freezes language
   projects, runs native cook/dependencies/pack/metadata, adds matching compiled
   scripts, compares unchanged strings/audio against verified0.2.0 payloads,
   and checks every archive entry/CRC/SHA. New archives are0.2.1-RU/EN;
   existing archives are never overwritten. Use a new version/output stage for
   subsequent changes. Licensed banks remain1418 media; no Wwise rebuild is
   needed for this update because all selected effect events already exist.
6. Run `tools/finalize_polish94.py` to check package/source/HD evidence and
   append the completion record. This does not certify native rendering or input.

There are12 HD pages (9 card pages,1 board,2 UI/FX) plus the small legacy particle
atlas. Identical exporter aliases share native DDS chunks; they must not duplicate
GPU textures. Every movie must have identical texture hashes across RU/EN.
Alpha/light conversion matches the original extraction. Original bundles and
source images are never modified. Runtime visual quality and controller/AI
acceptance remain separate, documented in PRESENTATION94_RU.md / _EN.md.

AI changes are in duelSession.ws and duelAIPass.ws. AiDuelTarget/AiDuelGain read
only own snapshots and public field units, calculate first-strike armor exchange,
and influence both choice ordering and immediate chase tempo. TimingReserve saves
reactive abilities; reserve never becomes extra score. EarlyPass uses an enemy
burst floor25 and requires two retained cards of advantage. Ordinary legal plays
are not discarded solely because their ordering score is negative. Passive duel
reactions are not simulated. Add exact counterexamples before extending estimates.

The one-time source migration prepare_polish94.py is historical; a clone already
contains its resulting sources. Do not run old style_presentation93.py after new
edits: it uses a local before-stage93 baseline, not the current source.

Aglais replays transfer the enemy graveyard card before applying Doomed;
otherwise Card.Move(to32) banishes it before the nested play starts.
`python -X utf8 tools/core-check/check_aglais94.py` executes the actual WS
selection branch and Move body as C# for10 own/enemy and invalid-pick cases.
This covers the sequencing seam, not all native special-card reactions.

Raw original additive textures are RGB-on-black with opaque alpha. HD generation
must use `light_alpha` just like the thumbnail extractor and crop frame-101 to
its alpha bounds. The exporter DDS centre must stay transparent. Native mouse
inspection uses MouseEventEx.buttonIdx, as stock CardSlot does; the stage capture
handler intercepts RMB before drag/row/target actions. It cancels only uncommitted
hand/leader placement; committed ability choices remain pending while inspected.
