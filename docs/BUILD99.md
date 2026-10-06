# Stage 99 / 0.2.6: rendering and fixed focus bounds

Base: 0.2.5 Russian installed-game startup accepted by the user. This build
changes presentation only. Native visual acceptance of 0.2.6 is pending.

On the existing compact98 source tree:

1. `python -X utf8 tools/ui/prepare_render99.py`
2. `python -X utf8 tools/build_presentation94.py --stage 99`
3. `python -X utf8 tools/package_presentation94.py --stage 99 --version 0.2.6 --language ru --compiled BetaGwent/build/board-compile97ru-final`
4. `python -X utf8 tools/recon/run_redkit_compile.py --out BetaGwent/build/board-compile99en-final --patch BetaGwent/build/stage99/en/en-source/scripts --timeout 120 --terms-already-accepted`
5. `python -X utf8 tools/package_presentation94.py --stage 99 --version 0.2.6 --language en --compiled BetaGwent/build/board-compile99en-final`
6. `python -X utf8 tools/finalize_release97.py --stage 99 --version 0.2.6 --compiled-stage 97 --compiled-en BetaGwent/build/board-compile99en-final`
7. `python -X utf8 tools/prepare_distribution97.py --stage 99 --version 0.2.6`

For a source rebuild with original assets, run the compact98 builder before
prepare_render99. Never run it after the stage99 patch, because it regenerates
the AS sources from pre-compact backups. Source-only GitHub excludes the
original game images and audio; see asset extraction guides for prerequisites.

No card-rule or AI change: all 61 RU patch sources match stage97 and its blob
is reused. EN restores the duration constants belonging to the verified English
voice bank from stage89, so it requires a fresh stage99 compilation. All 61 EN
sources must match that new blob. Six native movies are rebuilt and checked.
Package cooking strips only editor-only authoring data and verifies
native movies and texture pixels. Pack uses `-compression=None`, with a strict
55 MiB limit per GUI. ZIP CRC and per-file hashes are checked.

`BetaGwentHDArt.as` owns atlas sampling and the conservative native fallback.
`BetaGwentController.as` owns body bounds and the rotated focus outline.
`BetaGwentBoard.as` supplies explicit card/button dimensions and selection
borders. Original compact PNGs and original HD PNGs are unchanged.

For manual AI changes, see `docs/AI_MANUAL95_RU.md`. Those need a fresh script
compilation and a new stage/version; do not reuse stage97 blobs after WS edits.
