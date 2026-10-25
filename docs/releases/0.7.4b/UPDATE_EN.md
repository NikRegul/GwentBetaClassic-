# Gwent Beta Classic 0.7.4b

Fix candidate for the Scaleform tracer crash in BetaGwentBoard.drawBacks at the first battle render. The user identified the method from dump parameters: method_info 756, code_length 1172, max_stack 27, max_regs 22 in Stage 198. The captured ABC body matches.

Restores the render loop from Stage 190 and isolates enemy hand lookup and status snapshots in two small helpers. Enemy hand status effects, reveal removal, inspection layering and draw animations remain enabled. Audio/intro bridge behavior is unchanged from 0.7.4a; the unbuilt bridge experiment was reverted.

Retains all 0.7.4 combat effects, NG+ keg fixes, lossless atlas compaction and the 63 MiB menu budget. RU Next-Gen only; 0.8 and Classic 1.32 remain on hold. Native gameplay confirmation is required: deck selection, Start battle, intro, mulligan, first turn, then combat and reveal effects.

Offline checks: 81 regression suites; 110 targeted checks including 102 complete rendering/cache comparisons against Stage 198. Compiled drawBacks shrinks from 1172 to 921 bytes, 22 to 17 locals and two to one hasnext2 loops. The helpers are 162 and 139 bytes. Effect data and other UI classes match 0.7.4a.
