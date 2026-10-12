# Leader portrait pipeline — 0.6.1 / Stage 137

The active implementation is `BetaLeaderMovie137.as`, built by `tools/ui/build_leaders137.py` and loaded by `BetaGwent/ui/src/BetaGwentLeaderPreview.as`. The earlier `BetaLeaderMovie.as` and Stage 136 generator remain historical references.

Only the 21 leaders are permitted. Full 24 fps captures are paged into 282 native resources, driven by the owning menu clock so hover/reparenting does not restart the cycle. Portraits can appear on the battlefield, in hand when applicable and in the right preview. Ordinary premium cards and large character entrance animations are excluded.

Imported textures are engine-owned CSwfTexture images: never call `BitmapData.dispose()` on them. Clear ActionScript references and let the Loader own release. Loading callbacks record state; render and deferred unload happen separately. Active, loading and retired pages share a global cap of 12. This is a resource count limit, not a measurement of total game memory.

Reduced effects, failed loads and exhausted capacity use static fallback. Validate all 282 compiled page resources for the absence of unsafe disposal, then retest leader pairs and repeated transitions in the native game.

- [Build](../../../docs/BUILD_0.6.1_RU.md)
- [Manual checklist](../../../docs/TESTING_0.6.1_RU.md)
- [Crash diagnosis](../../../docs/reviews/2026-10-12-crash061-hotfix.md)

Original captures, atlases and native resource templates are local binary dependencies and are excluded from the source repository.
