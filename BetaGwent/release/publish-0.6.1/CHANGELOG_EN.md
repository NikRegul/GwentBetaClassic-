# Gwent Beta Classic 0.6.1

- Fixed a crash at the beginning of the leader introduction, including Eredin paired with Radovid or the Arachas Queen: portrait frame changes no longer manually dispose an engine-owned texture.
- Portrait page unloading is deferred outside loader callbacks. Added regression checks for repeated hovering, unfinished loads, missing resources and the total page limit, including pages awaiting unloading.
- All five packages include 13 text languages: EN, RU, DE, FR, IT, PL, ES, ES-MX, PT-BR, JP, KR, ZH-CN and ZH-TW. Text selection is independent of voices and persists with your game save.
- Five complete installation variants, each with one voice language: EN, RU, DE, IT or PT-BR. The keg troll uses Russian lines in DE/IT. Install only one package.
- Added fonts for the new languages, including Japanese, Korean and Chinese. A missing TC character uses an SC glyph. Only the selected dictionary and fonts are loaded.
- Card translations are based on official Beta localization; new interface translations need community feedback and proofreading. ES-MX and ZH-TW adapt ES and SC interface text while using official card names.
- Friendly and enemy row labels are translated as complete phrases, correcting French and Spanish word order. Native card item strings support all 13 languages; these labels outside the mod interface follow the game's language.
- The 21 leader card portraits use full motion cycles at 24 fps, with a blended loop seam. Board portraits survive interface redraws and hovering hand cards.
- Portrait frames stream in pages: at most two active pages per portrait and four portraits at once. A global limit of 12 pages includes pages awaiting unloading. This bounds animation resources, not total game memory.
- Ordinary premium card animations and large leader entrance animations are not included.
- Voice timings now match each package's actual recordings, including dialogue queues and music ducking.

Translation preview for PC 5.01. The 1.32 build is not included yet. Compilation, resource and archive checks do not replace in-game testing of motion, fonts and saves.

# Gwent Beta Classic 0.6.0

- Only the 21 leaders are animated: on the board, in hand and in the right-side hover portrait. Other cards retain static artwork.
- Portraits use calm Loop clips. Large Intro entrance animations are excluded; the short loop boundary uses an overlapping frame blend.
- Loading is delayed; up to three small portraits and one hover portrait are allowed. Switching cards and redrawing release the old movie. Static artwork remains on loading failure. Reduced effects disables animated portraits.
- Added independent RU/EN text selection: the “Text RU / EN” button at the upper left of deck/collection menus and the text option in the battle settings menu. The preference is stored with the game save.
- Each archive includes one voice language: RU or EN. Changing text does not change voices. After in-game validation of 0.6.0, a translation preview is planned for 0.6.1 to gather feedback.
- Card search supports both languages. Custom deck names and search input remain unchanged.
- Added regressions for text switching, user input, resource cleanup, portrait limits, Intro exclusion and the exact leader allowlist. UI, speech and AI fixes from 0.5.4 are retained.
- The profile mirror now uses two alternating banks with checksums. Validation precedes application; a damaged current bank falls back to the previous bank. Pending paid keg choices, settings and reward ledgers are included. A real game-save restoration test is still required.
- RU/EN switching applies to mod screens and card descriptions. Inventory item names and notifications outside those screens still follow the package and game language.

Requires The Witcher 3 Next-Gen 5.01. Version 1.32 will receive a separate build.
In-game acceptance is still required to assess smoothness and native memory use.

## 0.5.4 — changes

- Aligned the Tutorial button inside the right deck-selection panel. Tutorial pages share consistent margins, a layout grid and a button baseline; Try it is centred below its example.
- Card details retain and blur the tutorial behind them. Returning restores the same page and example.
- Added a dedicated tutorial controller mode: visible focus above the window, card and action selection, LB/RB page navigation and return from card details.
- Added Cantarella and an explanation of her draw ability to the Spies page. Removed advice to always save the leader for the final round.
- Music is temporarily ducked during dialogue and restored to the user volume when speech ends or is cancelled. Game settings are never overwritten. RU/EN dialogue bank gain increased by 6 dB.
- Playing another card no longer cuts off the current line. The queue is bounded and stale summon chatter expires. The AI waits for speech to finish after replaying a move.
- Device changes, focus updates and pointer movement no longer skip leader introductions. Deliberate skipping remains available.
- Controller focus returns to the board after a completed play and its mandatory choices.
- Added no-target effect diagnostics for future match analysis. In the reviewed log, the AI detected an Elven Mercenary with no targets and replaced it during mulligan; this case does not confirm a tutor bug.
- Added tutorial, controller, speech queue, music duck and opponent wait regressions. Base packaging excludes premium portraits, including stale staged assets.

Requires The Witcher 3 / REDkit 5.01. Redux compatibility and animated premium portraits are not included.
Source tests and native compilation do not replace listening and controller acceptance in game.

## Retained 0.5.3 changes

- The introduction waits for both leader voice lines to finish. A long first line no longer removes the second from the queue. Skipping the introduction stops its voices.
- Speeding up an active replay keeps card movement, number changes and sound synchronized while preserving animation progress. The hint switches to Skip without redrawing the board.
- Grouped area hits preserve separate reveal and status-change frames.
- Epidemic excludes concealed ambush cards when finding and destroying the weakest units. Immunity and armor do not prevent this area destruction. AI evaluation follows the same rules and does not depend on concealed ambush power.
- AI accounts for hand-size differences and the value of preserving cards and the leader for the next round. This additional reserve is disabled in deciding rounds.
- Public reply estimates adapt to already seen cards and include the possibility of a pass. A rare worst-case reply is no longer treated as the inevitable continuation.
- Bounded lookahead covers different action roles: engines, control, draw and combos, without increasing the simulation budget.
- Added reproducible decision checks with acceptable alternatives and independent seeds, plus regressions for the reported bugs.
- Preserved the current tutorial and Tutorial button, translations, False Ciri and deck deletion fixes.
- Included the final 0.5.2 deck changes: Slave Infantry replaces Vicovaro Novices with Alba Armored Cavalry; Arethusa replaces Thunder with Redanian Knights; Dryads replaces Sages with Mahakam Guards. These changes were selected in the second agent's paired trials.

Requires The Witcher 3 / REDkit 5.01. The obsolete Redux compatibility layer is excluded.
Automated source checks do not replace in-game animation and audio verification.
