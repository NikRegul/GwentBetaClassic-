# Gwent Beta Classic 0.2.1-preview.2 — Beta deck builder

Separate preview after the first release. Includes preview.1 faction boards
and effects, plus a redesigned deck editing screen.

The layout follows the original 0.9.24 `CreateDeck`: deck and leader on the
left, collection in the centre, large card preview on the right. Original
forest background, wooden shelves, rarity frames, faction/rarity icons and
faction description panels are adapted to TW3's menu safe area.

The collection displays 12 cards per page. The deck displays 12 distinct
cards per page with copy counts and artwork strips. The permanent preview
shows the original ability, tags, keyword explanations and flavour text.
Hovering only rebuilds the preview when the selected card changes.
Saved slots, renaming, filters and deck legality remain available.

## Controls

- Confirm adds a copy from the collection or removes one from the deck.
- LT/RT remove/add a copy of the focused card.
- View switches between deck and collection; LB/RB change the active page.
- Start saves a legal deck; B/Esc cancels the editor.
- X/right click/I opens full inspection. Right stick or wheel over the
  description scrolls long text. Wheel over the collection changes pages.
- Use Rename for the existing on-screen keyboard. Leader arrows are on
  the left, faction buttons above the collection.

## Installation and acceptance

Close the game and **back up your saves before installing or updating**.
Install only one language ZIP, replacing `Mods/modBetaGwent0924`. The build
does not modify the installed game. Russian native resources are also
updated in the REDkit development project.

Check the three-column layout; add/remove cards in both panels; switch
factions/leaders; use search, filters, paging and long-text scrolling.
Rename/save/reopen a deck. Repeat View, LT/RT, LB/RB, X and Start with a
controller, then launch one NPC match with the saved deck. Preview.1 board
and effects still need the same combined in-game acceptance.

Native menu bindings, ABC, DDS and CRC are validated during building.
Runtime appearance/control acceptance is pending. Saved-deck selection and
the full catalog retain their previous layouts. Full Unity shaders,
premium animations and deck-editor transition animations are not yet ported.
