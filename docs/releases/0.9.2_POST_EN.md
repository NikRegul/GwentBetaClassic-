# 0.9.2 — a closer look at AI decisions

This update focuses on how the opponent spends its hand. When should it concede an expensive round? Which card should take an empty round after a pass? Can it save a finisher without losing the match now?

The AI now chooses separate continuations after different enemy replies and can solve small supported public endgames. Exact checks of promising cards also run on easy and medium. Several decisions involving Miruna, Frightener, Nekkers, Slyzard and reserved finishers have been corrected.

There are usability changes too: Panther uses a board targeting arrow, Henry var Attre can finish optional selection, and related cards and created spells are shown more accurately. The original Gwent Beta main menu theme plays in the deck builder; match music stays the same.

Maximum difficulty knows your original deck list, but not your real hidden hand or future draw order. No starting five-point bonus has been added.

Tests help fix specific mistakes, but the short control matches do not yet establish an overall win-rate increase. Reports from actual play are especially useful: a wasted card, a bad pass or a missed combo. Please include the difficulty, cards and score; a log from `-debugscripts` helps too.

Choose the archive for Classic 1.32 or Next-Gen 5.0+. Install the main mod; `modBetaGwentMenuMusic` is optional and adds the Beta theme to the deck builder. Without it, the game's normal music continues. Classic also needs the included DLC. The full changelog and installation instructions are in the package.
