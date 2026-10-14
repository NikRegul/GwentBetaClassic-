# Gwent Beta Classic 0.7.3

Preparation for in-game testing. Every voice package includes 13 text languages.

- Placement: original particles for the regular landing, gold cards, frost, fog and rain. The weather variant is chosen by row; leaders get no extra effect when played.
- Summon and spawn: SpawnBlink and the landing match the card's arrival. Moving to another row ends with the matching landing.
- Ambush: original dust and leaves instead of the generic gold flash and caption. Flipping keeps the card centred.
- Transform: the art is replaced in place under the original particles; the effect is taken from the transform operation registry. Effect duration is accounted for during match playback.
- In the Beta interface the collection, catalog and deck list scroll without pages, and only visible rows are created. Mouse wheel, scroll bar and LB/RB; the D-pad continues the list past the visible area.
- Drag cards from the collection to the deck and back. Invalid or outdated drops are cancelled; releasing after a drag does not add a second copy by click. A short flight confirms each addition or removal.
- A new deck is created by choosing a faction and leader. Leader availability and quest-faction limits are also checked in the game scripts. Cancelling does not take a save slot.
- Newly obtained cards are marked "NEW", with a "New cards" filter. Viewing a card with the mouse or controller clears the mark. Old collections migrate without marking every previously owned card. Marks are saved separately and included in the verified profile backup.
- `bg_allcards` grants all missing collectible cards and leaders up to the allowed number of copies. Running it again does not duplicate cards or re-mark viewed ones. Money, kegs, rewards and decks are untouched.
- `bgboard_effects` shows the current battle effect handlers by default. Added scenes for weather landings, transforms and leader plays. Back/Repeat/Next stay available while viewing.
- Checked Trial of the Grasses (200078): the current special-card handler issues a mandatory request with minimum=1 and maximum=1. MonsterRequest mode 18 belongs to Jotunn and is not used for this card; no rule change was needed.

AI fixes:

- Elven Swordmaster and Braenn evaluate damage by their current power. Target choice accounts for Miruna's pending charm without double-counting an already resolved timer.
- Aglais without a suitable special card is kept for later rounds. In a non-mandatory round the AI may keep its hand by passing if every move is non-positive and passing after timers keeps the lead. Mandatory rounds and confirmed catch-up are preserved.
- Created and nested special cards are scored with the same calculation as a direct play. An Execution that destroys the AI's own strongest units scores negatively; Last Wish picks the more useful alternative.

The accepted lightning, weather layers, destruction and banish are preserved. Light uses additive blending per the source material; smoke and leaves keep normal alpha. Unity shader refraction and the HeroOverlay geometry overlay do not run in Scaleform; particles and art swaps are used instead. The final look and save migration still need an in-game check.

Additions after in-game testing of the editor:

- Faction selection shows the five original Beta emblems over the banners; no new textures were added.
- A short mouse press on a collection card adds it, and on a deck row removes it. Releasing outside the original card cancels the click; dragging, RMB and the craft button remain separate actions. A repeated CLICK does not duplicate the change.
- Editor card spacing reduced from 318 to 240 vertically and from 186 to 176 horizontally.
- `bgboard_effects` lists distinct battle operations and representatives of different bindings first, then the remaining cards. Parasite shows +12 and damage separately; Raven's Eye shows three rows; Igni shows three targets in one row. Mass destruction is no longer limited to one sample.
- The AI mulligans Emissary when the remaining chain "Emissary → Recruit with no follow-up" has an expected result of −1. Useful chains are kept; a set of 39 checks was added.
