# Compact presentation build, stage 98

Stage 97 / 0.2.4 failed installed-game startup according to the user. Stage 98
retains inline native textures but reduces raster dimensions. Runtime acceptance
is pending. Only the Russian candidate is requested at this stage.

1. `python -X utf8 tools/ui/build_compact_art98.py`
2. `python -X utf8 tools/build_presentation94.py --stage 98 --language ru`
3. `python -X utf8 tools/package_presentation94.py --stage 98 --version 0.2.5 --language ru --compiled BetaGwent/build/board-compile97ru-final`
4. `python -X utf8 tools/finalize_compact98.py`

The compact builder writes `BetaGwent/ui/assets/compact98`. Original HD atlases
and DIY images remain unchanged. It keeps logical slot rectangles and restores
their scale using the bitmap transform; animation crop coordinates are unchanged.
Card raster size is 288×405, faction half-board size is 1536×531. HD pages use
0.75 scaling; optional DIY backdrops use 0.5. Native opaque card pages retain
BC1 and translucent pages retain BC3 compression.

The original AS source backups are in `BetaGwent/build/compact98`. Do not run
the old HD generator after the compact builder: that would restore HD embeds.

The packaging guard rejects shipping menus of 55 MiB or larger. Editor-only
authoring data is stripped only from release copies. Native cook, image links,
pixel blocks, uncompressed bundle contents, archive hashes and CRC must pass.
The 61 unchanged gameplay patch sources must exactly match the verified stage97
Russian compilation before reusing its blob; no claim of fresh compilation.

No game configuration, installed mod, Nexus upload or Steam upload is changed
by these commands. Installed-game pause editor and NPC startup remain the
acceptance gate. English packaging and publication are deferred by the user.

Completed RU candidate: 156417988-byte ZIP. Three cooked menus are
56517464 / 56517576 / 56517596 bytes (about 53.9 MiB each). Native movie and
all texture pixel blocks match the prepared input. Raw bundle contents, ZIP CRC,
SHA hashes, original image hashes and 61 reused script sources were verified.
Evidence: `docs/evidence/stage98-final.json`. No installed-game acceptance yet.
