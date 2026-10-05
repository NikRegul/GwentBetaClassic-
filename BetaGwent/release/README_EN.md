# Gwent Beta Classic 0.2.0

**You must back up your saves before installing the mod and before every update. Bugs can still occur; use a separate test save for your first matches.**

Replaces The Witcher 3's Gwent with rules and cards from Gwent Beta 0.9.24.
This package has English text and English battle voices. The separate RU
package has Russian text and voices. Install one variant at a time.

479 collectible cards, including 21 leaders; five factions; all special cards,
units and leaders are implemented. The deck builder supports eight saved deck
slots, renaming, filters, ownership limits and 25–40 card decks. Five starter
decks are supplied. The full catalog also shows unowned cards and their sources.

Native NPC Gwent opens the new pre-match deck menu. Quest players have fixed
decks and assigned gold rewards; an already-owned gold reward gives 300 crowns.
Ordinary players draw random decks from a 55-deck pool each match and award one
random eligible bronze/silver card for each of your first four wins against
that character. Old saves keep their existing first reward; three remain.
Bronze ownership is capped at three; silver, gold and leaders at one.

The Crow's Perch quartermaster sells 150-crown kegs. Buy several, then open
them one at a time from inventory or the deck menu. A keg contains up to four
remaining bronze copies plus one rare choice from three cards. Silver versus
gold/leader is 50/50 while both pools have cards. Excess copies are excluded.
The final kegs may contain fewer bronze cards for the same price. Vanilla
merchant cards are replaced with comparable Beta cards. Collect 'Em All
requires one copy of every collectible card and leader.

Battle supports mulligans, automatic round transitions, precise unit insertion,
direct special-card targeting, Ambush concealment, weather, animated actions,
original Beta artwork, sound effects and weighted battle voice variants.
You can inspect either graveyard and your own deck. Deck viewing groups cards
by color and randomizes display order; the enemy deck and hand stay hidden.
The AI has 40 adapted archetype profiles and common card-economy/pass logic.

## Installation

1. Close the game and back up your save.
2. Extract `Mods` to The Witcher 3 installation directory. The result should be
   `Mods/modBetaGwent0924/content`.
3. Replace the previous mod folder. Do not keep RU and EN in separate mod folders.
4. Open the game's Gwent deck menu to edit decks, or talk to an NPC to play.

Players do not need REDkit, Wwise or the compiler. The package contains cooked
menus, localization, sound cache and compiled scripts. Supported build target:
PC game/REDkit 5.0. Older 4.04 compatibility has not been established.
Other mods that replace Gwent menus, rewards or card trade can conflict.
Custom deck names remain as you named them when switching language packages.
Collection, deck slots and NPC reward history are part of your game save.

See `CONTROLS_EN.md` and `CHANGELOG_EN.md`. This revision compiles and its
archive contents are verified; the new English build and four-win rewards
still need a short installed-game check. Previous Russian battle build was
accepted by the project owner. This is an early public version.

## What comes next

Board layout and animations closer to the original Beta; more accurate weather
presentation; archetype AI tuning based on actual matches; remaining complex
card forecasts; music and optional announcer cosmetics. Broader tournament,
quest, old-save/NG+, mod-compatibility and controller-layout coverage is still
needed. Implemented does not mean every possible card combination has been
exhaustively verified.
