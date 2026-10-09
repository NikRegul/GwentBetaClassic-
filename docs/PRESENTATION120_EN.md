# Gwent Beta Classic 0.4.1

Back up your saves before updating. Remove the old `Mods/modBetaGwent0924`
folder and install Mods from one language package. Collection and saved-deck
formats are unchanged. Game target: 5.01.

## Changes since 0.4.0

- Rebaked all ten board halves from original Beta meshes and textures. Fixed
  depth selection: the camera looks from negative Z, so the nearest, lowest-Z
  surface must win. Rear faces previously covered gold ornaments, metal fittings
  and sections of the trim.
- Preserved one runtime horizontal reflection: score rails left, row symbols
  right. Each player's half retains its faction board.
- Restored original hand and leader separators from the level8 scene.
- Increased visible row/total digits using Gwent Numbers glyph metrics, added
  dark outlines and a yellow highlight for the leading total.
- Weather impacts have separate audio from weather placement and generic hits.
  Uses original ice, magic, physical, lightning and fire events already present
  in both banks. The causing weather's identity wins over overlapping row tokens.
- Regular hits play all four original impact-sheet cells in order instead of
  one template-selected still. Frost hits include an original ice-texture burst.
- Graveyard cards and previews show Lock. The rules already preserved it on
  death; added regression coverage. Snapshot armour, resilience and timer marks
  are also shown in these views.

Atlas dimensions, card resolution and texture memory are unchanged. Reference
videos and the original Beta client are not included.

## Build

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-0.4.1.ps1 -Language both -CheckAI
```

Use `-Language ru` or `en` for one package. Individual stages:
`-Step prepare`, `scripts`, `menus`, `package`. Board bake:
`python D:\w3mod\tools\ui\build_board120.py`.

CHANGELOG_EN.md lists accumulated changes since 0.3.4. The 0.4.0 documentation
still describes AI editing, training and version comparisons.

## In-game verification

Compilation, menu bindings, resource limits and archive integrity are checked
during the build. Installed-game rendering/audio still needs verification:
different faction halves, one/two/three-digit scores, armour hits, weather ticks,
locked graveyard cards and animation speeds. The GFx adaptation does not run
Unity shaders/particles directly; this is not a claim of pixel-perfect parity.
