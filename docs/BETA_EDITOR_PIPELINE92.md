# Deck builder asset and build pipeline — stage92

Source: local read-only `Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles`.
`tools/ui/beta_editor_sources.py` extracts sprites from their owning bundles:
`gui/spriteatlases/uber/{deckbuilder,deckpicker,filterbuttons,factioniconsmedium,sidepreview}`.
It also exports RectTransforms from `gui/prefabs/deckbuilder_base` to
`BetaGwent/ui/assets/beta-editor/layout.json`. The original has DeckPicker
at x=-605, Collection width855, SidePreview at x=605 in a1565×715 CreateDeck.
The AS layout adapts these three regions to1920×1080.

Source hashes and sprite path IDs/crops: `docs/evidence/beta-editor92.json`.
Full-size extracted PNGs and128×180 atlas tiles:
`BetaGwent/ui/assets/beta-editor`. Contact sheet: `BetaGwent/ui/build/beta-editor92.png`.
35 additional bindings, IDs-1200..-1270, share the existing immutable atlas.
No new embedded texture or native texture schema is introduced.

Runtime: `BetaGwent/ui/src/BetaGwentBoard.as`, functions `drawDeckEditor`,
`redrawEditorCollection`, `showEditorCard`, `editorBetaButton`.
Only the selected preview is rebuilt on hover/focus. Search remains debounced;
no full catalog/card-grid reconstruction is performed for each mouse move.
`BetaGwentController.focusPane` takes an optional boundary and card-only mode;
the editor uses x440, keeping the battle/default pane logic unchanged.

```powershell
python -X utf8 tools/ui/build_card_art.py
python -X utf8 tools/build_presentation92.py
python -X utf8 tools/package_presentation92.py
python -X utf8 tools/finalize_presentation92.py
```

Run sequentially. The six RU/EN native movies are captured under
`BetaGwent/build/stage92/{ru,en}/resources`; RU finishes last and updates
the REDkit project. Existing preview.1/0.2.0 archives remain immutable.
English source generation uses `data/beta924/design/english89.json` and
rejects untranslated literals. The packager checks every WitcherScript
source against stage90 native compilation before reusing that blob; audio
and strings are reused only after verifying frozen hashes and string DB rows.
Version:0.2.1-preview.2, isolated `release92/{ru,en}` outputs.

Original CD Projekt textures remain outside the GPL license of the mod code.
No installed-game update, GitHub upload or runtime UI automation is performed.
