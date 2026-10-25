# Gwent Beta Classic 0.7.4a

Loading fix candidate for the reported stall immediately after requesting an NPC Gwent match, before deck selection. The 0.7.4 menu reached 64.507 MiB; the previous 63.377 MiB menu loaded. A boundary near 64 MiB is a hypothesis pending gameplay verification.

The VFX atlas now packs individual cells instead of entire family pages: 2048x3968 to 2048x3136, saving 1.625 MiB. All 1112 cells retain identical dimensions and pixels; all 43 particle recipes are unchanged. No resolution reduction or effects disabled. New builds enforce a 63 MiB menu budget. An early MENU_CONFIG_BEGIN diagnostic was added.

All 0.7.4 changes are retained. The accepted editor, keg opening, lightning, weather layers and card dissolve remain unchanged. Verify NPC deck selection first, then starting a duel and the leader introduction. The earlier introduction crash remains a separate gameplay check.
