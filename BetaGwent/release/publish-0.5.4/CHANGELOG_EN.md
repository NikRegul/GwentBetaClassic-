# Gwent Beta Classic 0.5.4 — changes

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
