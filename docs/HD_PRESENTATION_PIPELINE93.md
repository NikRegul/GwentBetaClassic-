# HD presentation pipeline — stage93

`tools/ui/build_hd_art93.py` consumes the preserved extraction manifests
for boards/editor and original DIY card sources. Sources remain unchanged.
It bakes boards with bilinear UV sampling into common bounds:
X=-124..160; own Y=-95..3; opponent Y=-3..95. Both halves are2048×708.
Runtime draws each half at1160×400, x312, y154/554. Six row targets use
x437, width754, height96, y218/584 plus104 per row. Source border ornaments
are outside the playable area and remain visible.

Seven HD pages: four256×360 illustration pages, one board page, two UI
pages. The2048×720 small atlas retains only57 weather/particle bindings.
HD aliases/crops share rectangles; whole backgrounds/board halves do not
need separate bitmap copies for every tile.

`BetaGwentHDArt.as` is generated from pixel rectangles; each page retains
one immutable BitmapData when the native runtime provides it. The fallback
retains the existing native Bitmap path. There are no bitmap pixel writes.
`BetaGwentCardArt.as` routes HD IDs before particle IDs. UI corners/edges
use nine-slice crops through `betaNine`; geometry is centralized in
`rowGeometry`/`rowLayout`. Hover updates only the corresponding side pane.

`tools/ui/install_native_hd93.py` follows actual GFx ImageInfo IDs and
optional SubImage tags, rather than assigning DDS by dimensions. Every
source JPEG/alpha binding resolves to its exported DDS. Identical DDS
aliases share one ImageInfo/CSwfTexture; all original character IDs remain
as SubImage bindings, and SymbolClass/ABC remain unchanged. 20 image
bindings use10 texture chunks. Root texture handles, property identities,
chunk/table/header CRCs, DDS format/extent, movie frames, symbols and
ABC are verified before an atomic backed-up install.

The resource validator accepts1..32 inline textures of the same observed
CSwfTexture schema; checks on auxiliary tables, metadata and CRCs remain.
The original .gfx import identity is retained. Each menu owns a distinct
movie linkage to avoid cache collisions. Native runtime acceptance of the
HD adaptation remains pending.

```powershell
python -X utf8 tools/ui/build_card_art.py
python -X utf8 tools/build_presentation93.py
python -X utf8 tools/package_presentation93.py
python -X utf8 tools/finalize_presentation93.py
```

The full artwork builder regenerates HD pages after initial extraction.
For existing manifests alone, `tools/ui/build_hd_art93.py` is sufficient.
Run sequentially; do not edit source/assets during six-menu compilation.
EN is built first, RU last. Native resources are captured under
`BetaGwent/build/stage93/{ru,en}/resources`; RU updates only the REDkit
workspace. Package outputs use isolated `release93` and preview.3 names.
Compiled stage90 WS is reused only after matching every source hash.
No game install, publication, Git operation or UI automation is performed.

Evidence: `docs/evidence/hd-art93.json`, `stage93-completion.json` and
per-menu/per-language bridge/native reports. Offline composites generated
by `preview_layout93.py` inspect asset proportions; they are not runtime
screenshots and do not validate interaction.
