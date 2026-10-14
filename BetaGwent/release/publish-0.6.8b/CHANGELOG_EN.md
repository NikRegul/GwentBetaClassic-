# Gwent Beta Classic 0.6.8b

- Scorch burns cards in place using original fire/frame textures and a GFx dissolve.
- Special-card portraits appear once on play, then clear before subsequent effects.
- Alzur uses original lightning trail/sparks and validated, deduplicated travel/impact audio.
- Mourntart consumes all victims together while preserving complete action history.
- Saved animated/static leader option, independent of shortened battle effects.
- Four battle-menu tabs, stable controller focus, reachable disabled entries with reasons, and modal-safe A/B handling.
- Controller battle hints move to the right sidebar; card descriptions remain scrollable.
- Mouse acceleration requires holding RMB, then restores tempo on release or focus loss. A short click has no speed/skip action.

Includes 0.6.6. Fifty-one regression suites, 70 native scripts, four menus and package checks; in-game acceptance remains pending.

Low-memory variant: three effect atlases use half resolution in each dimension. Cards, leaders, text, timings, rules and AI are preserved. GUI loading target: 56 MiB.
