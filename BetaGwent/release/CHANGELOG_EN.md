# Gwent Beta Classic 0.4.1 — changes since 0.3.4

Back up saves before installation and every update. The cumulative changes below include 0.4.1 and the intermediate versions after 0.3.4.

## New in 0.4.1

- Rebaked all ten original Beta board halves with correct nearest-surface depth selection, restoring gold ornaments, metal fittings and trim previously covered by rear faces.
- Preserved one horizontal reflection: score rails left, row symbols right. Each player's half retains its faction board.
- Added original hand/leader separators from level8.
- Larger visible row/total digits based on Gwent Numbers glyph metrics, dark outlines, and a yellow leading total.
- Separate weather-impact audio, distinct from placement and generic physical hits, using original ice, magic, physical, lightning and fire events in existing RU/EN banks. The causing weather wins over overlapping row tokens.
- Hits play all four original impact-sheet cells in sequence instead of a template-selected still. Frost impacts include an original ice texture.
- Graveyard/previews show Lock. Added death/round-cleanup preservation checks; rules already retained the status. Snapshot armour, resilience and timers are shown too.
- Atlas dimensions, card resolution and texture memory have not increased.
- Added editable Build-0.4.1.ps1 for RU/EN packages.

Compilation, menu bindings, resource limits and archive integrity are checked during the build. Installed-game audio, visuals and controls still need verification. Exact Unity effect parity and perfect AI play are not claimed.

# Gwent Beta Classic 0.4.0

- Linked AI explanations: candidate evaluations, leader/card selection, rows, targets and explicit pass reasons. Lookahead simulations do not flood the gameplay log.
- Synergy checks across all 46 archetypes: safe rows, booster adjacency, unreachable catch-up and complete play resolution; summons, discard setup and engine preservation where applicable.
- Reproducible old/new AI comparisons with shared rosters, raw deal and RNG. Per-archetype statistics, saved games/failures and a replay tool.
- Fixed the comparison host to use exported training weights by default. Gameplay already used these weights.
- Persistent animation pace and reduced-effects preferences. Reduced effects retain source/target cues and value changes.
- Public target/area/weather previews before selection, plus remaining selections. Hidden and random results are not revealed.
- Editable PowerShell build/comparison scripts, instructions in UPDATE.md and separate Russian/English packages.
- Includes the single-screen mulligan, own-deck and ability-choice views, created-spy trigger fix and editor alignment from 0.3.5-preview.5.

The host verifies rules; preview positioning and input still need in-game verification. Back up your saves before updating.

# Gwent Beta Classic 0.3.5-preview.1

- Eredin's FrostWraiths opponent uses the complete approved Wild Hunt starter, including its leader and copy counts.
- Deck and graveyard viewers use a unified grid without tabs, collection styling, strength banners and a detailed right-side preview.

Test build: armour digits, correct reactive ship source, combined power/armour impacts, Dimun placement and early Bran setup. Cerys keeps her discard priority. See PREVIEW.md for details and in-game checks. Back up saves before installation.

# Gwent Beta Classic 0.3.4

**Back up your saves before updating.**

- Native game AI evaluates plausible replies using public leaders, faction and visible cards across 40 archetypes. Hidden player hands and exact deck selections do not determine the reply model. Risk affects move ordering, never the actual catch-up score.
- Full card inspection redesigned around the Beta preview layout: large framed card with base strength on the right, name, tags and complete description on the left.
- Right-side previews centred within their panel. Quest sources explicitly say the card can be obtained from the named NPC.
- Target instructions moved between board halves, outside all six rows.
- Original higher-resolution faction emblems on keg card backs, without increasing atlas dimensions.
- Weather remains animated during fade-out; animated score/power numbers retain their centre.
- Editable PowerShell full/partial build scripts and updated AI training instructions.

80 self-play matches covering all 40 decks completed without errors. This checks functionality; it does not prove improved win rate or replace in-game verification.

# Gwent Beta Classic 0.3.3

**Back up your saves before updating. Install one language only. Start with a separate test save.**

- Removed visible escaped line breaks in headings. Opponent profiles show the leader and deck name; the NPC name remains on the setup screen.
- Row and total scores are centred using the original Beta numeral bounds. Long button labels fit inside their frames with padding.
- Hold the coin, P or Y / triangle to pass. A quick click no longer passes; the progress animation remains.
- Search and renaming share a text dialog with Unicode input and a selectable RU/EN keyboard. An empty search clears the filter.
- Deck saving reports the specific reason for rejection; long initial names are limited to 48 characters. Existing save schemas are unchanged.
- AI placement checks safe rows after archetype and neighbour preferences. Full rows are excluded; tactical exceptions and summon rules are preserved.
- Added AI row-placement details and deck-validation reasons to the log.

Compilation and packaging are checked automatically. Visuals, input and save persistence still need verification in the installed game. The experimental opponent-response model and new trained weights are not included in this release.

# Gwent Beta Classic 0.3.2

**Back up saves before updating. Install only one language. Test this build on a separate save first.**

- Five starter decks can be edited and saved directly, independently of the eight custom slots. Existing custom decks are preserved.
- Explicit clickable Pass and Inspect controls; controller focus and action hints refined.
- All four menu timelines now target 60 Hz instead of 30 Hz. Actual in-game FPS still needs measurement.
- Weather moves continuously, transitions in and out smoothly, and remains visible with reduced motion.
- Revised card landing timings, a centred coin flip, and layered deck/graveyard piles.
- NPC names and archetypes shown on two lines.
- Keg receipts show collection additions or the actual scraps granted for excess copies.
- English vendor item fallback prepared for other game text languages; RU and EN remain the complete mod translations.
- AI checks actual chase results, including leaders and the changed hand after the first action. Future strategic value is kept separate from the current score.
- AI preserves its last medic or other card in an optional round when playing it cannot catch up. This check does not concede a decisive round.
- All incoming units consider adjacency to an active Redanian Knight; Assassin evaluates its victim and insertion slot; independent Vran engines are preserved.
- Plain created units prefer an available safe row. Card-specific summon and random spawn rules are preserved.
- Shared positive boost and armor presentation is combined into one effect per target across abilities, rather than only Alzur's Thunder.
- Beta-style catalog: original strength flags/font, aligned buttons and unified preview. Removed implementation/queue labels, generic keg labels under every card, and manual milling UI.
- Specific quest rewards show their source and also explain keg/crafting availability.
- Original armor/resilience elements, aligned description panel and a removed redundant board instruction.
- Keg opening uses 48 frames at 24 fps from the original recording, with separate static scenery and moving crop.
- AI training freezes sources, includes all 40 decks, swaps seats and deck assignments, supports stop/resume and validates imports with backups.
- RU/EN build script and game metadata 5.01. The 0.3.1 economy is unchanged.

Exact visual parity and stronger AI across every archetype are not claimed. UI, controller and save behavior still require a combined test in the installed game.

# Gwent Beta Classic 0.3.1

**Back up your saves before updating. Delete the old modBetaGwent0924 folder before installing.**

- Beta-style keg opening: a separate screen where the troll merchant smashes the keg (animation from the Beta), with his voice lines in English and Russian.
- Face-down cards show their own faction back and glow in their rarity colour on hover; reveal them one by one, pick your fifth card, then see "Your new cards!".
- Kegs are opened from the deck builder (Kegs button).
- New keg: four cards with a chance of higher rarity plus a choice of three cards of one rarity (rare, epic or legendary). Price 200 crowns.
- Every Gwent card merchant sells kegs, 5 at a time; stock refills over time.
- Bought kegs are stored in the save instead of the inventory; kegs from older versions are moved automatically. Removing the mod can no longer wipe Geralt's inventory.
- Card scraps, as in Beta 0.9.24: craft cards in the deck builder and the All cards catalog. Prices by rarity (craft/mill): common 30/10, rare 80/20, epic 200/50, legendary 800/200.
- Duplicates can now drop from kegs and NPC rewards; a copy above the deck limit turns into scraps automatically.
- A full set (3 bronze, 1 silver, 1 gold or leader) is never milled; only spare copies turn into scraps.
- The deck builder shows your scraps; clicking a missing card offers to craft it.
- Scraps for matches: +20 for each win against an ordinary NPC after the four card rewards, +50 for a repeat win against a quest or tournament opponent, +5 for a defeat. A duplicate quest gold card gives 200 scraps.
- AI values cards that play or summon other cards from the deck (synergy and a thinner deck).
- AI can play weather early: the more turns left in the round, the more it is worth, discounted by the chance that the opponent passes. This also covers cards that play weather from the deck (Wild Hunt Hound).
- AI keeps growing finishers (Dol Blathanna Sentry, Bloody Baron) for the deciding round and plays the Sentry after its special cards.
- Voice lines: a newly played card cuts off the previous line; lines no longer pile up.

# Gwent Beta Classic 0.3.0

**Back up your saves before updating. Delete the old modBetaGwent0924 folder before installing.**

- New AI: before every move it plays out its candidate cards and leader on a copy of the board and picks the best result.
- AI mulligans by card value learned from thousands of simulated matches.
- AI no longer places units into harmful weather and prefers rows with useful effects.
- AI places units for adjacency synergies (e.g. cards that boost both neighbours go between units).
- AI chooses targets by simulation (e.g. Coral no longer turns its own unit into a figurine).
- AI saves its leader: it no longer spends it to win a round that one hand card can win.
- Named NPCs (Zoltan, innkeepers, tournaments) now draw a random archetype of their faction; all 40 archetypes appear much more often.
- The opponent's deck archetype is shown instead of the NPC name.
- Beta fonts, card frames, HUD, counters and faction card backs.
- Leader intro with voice lines before the match.
- Beta-style mulligan screen.
- Original Beta row weather, drawn under the cards.
- Multi-target effects play on all targets at once.
- The acting card is highlighted, its name is shown and an arrow points from it to the target (useful for end-of-turn triggers).
- Beta spying (eye) and revealed-card (magnifying glass) tokens.
- Leader shows its power in the corner; the hand counter includes the leader.
- Hand cards sit in an even, flat row.
- Widescreen support: side panels instead of black bars.
- Deck selection shows HD leader covers.
- Deck builder: new "Owned" filter; deck size limit text updated (25–40).
- All labels now fit their buttons and panels.
- Removed the "Rematch" button.
- Fixed: Beta target abilities are mandatory when a legal target exists (some cards could skip their target).
- Fixed: Cow Carcass timer stalled when the side it lies on had passed.
- Fixed: Dimun Light Longship boosted itself with no unit on its right.
- Fixed: Dwarven Agitator now picks from your starting deck, not what is left in it.
- Fixed: Zoltan's parrot and other created units are placed between units instead of at the row edge.
- Fixed: pressing Space during the leader intro could freeze the screen.
- Interface errors no longer freeze the match; they are written to scriptslog.txt.

# Gwent Beta Classic 0.2.9

**Back up your saves before updating.**

- Fixed: the game was not paused during a match — key presses made Geralt drink potions and guards attack. Gwent menus now fully pause the game like vanilla Gwent.
- Beta board laid out from the original Beta scene: pass coin, two-half crown, score ribbons, rows, leader, hand, deck and graveyard.
- Rows and board halves at the original scale (were 81%).

# Gwent Beta Classic 0.2.6

**Back up saves before updating.**

- Selected units use battlefield card dimensions for their borders.
- Controller focus excludes text/effect extents and follows hand-card rotation.
- Fixed button, row and choice-card body bounds.
- Half-texel atlas sampling and a conservative native Bitmap fallback.
- Compact resolution and the 55 MiB GUI limit retained. RU/EN share gameplay.

Update 0.2.6 fixes card borders and controller focus bounds and changes atlas sampling to reduce flicker. Compact resolution remains: cards 288×405, board halves 1536×531. Russian 0.2.5 startup was confirmed in the installed game; new visual changes and English startup still need testing. Back up saves and replace the whole Mods/modBetaGwent0924 folder.

# Gwent Beta Classic 0.2.4

**Back up saves before every update.**

- Fixed Roar creating its Bear; audited neighboring nested-play transitions.
- Refreshed stale deck/graveyard choices; excluded active play ancestors.
- Free-row fallback and spy-side handling for nested units.
- Row validation agrees with allied/enemy/any-side highlighting.
- Balanced cursor ownership and input-context restoration.
- Restored inline HD textures; native bundle is stored uncompressed.
- Matching RU/EN code, fresh script blobs and build/AI documentation.

Installed-game rendering and input acceptance of this revision remain pending.
0.2.3 opened menus but did not render external textures. Replace the whole
Mods/modBetaGwent0924 folder; do not mix package versions. See UPDATE.md.

## 0.2.2

Improve shipping-GFx startup compatibility: remove the early MouseEvent.RIGHT_CLICK lookup and detect native RMB without an additional SDK class. Installed-game acceptance of the blank-editor/NPC-loading fix is pending.

# Gwent Beta Classic 0.2.1

**Back up your saves before installation and every update. Bugs can still occur.
Use a separate test save for your first matches.**

## Changes

- HD target highlights preserve transparency instead of covering card artwork with black rectangles.
- Full right-click inspection handles native Scaleform button events without playing a card or confirming a target; I and Shift + click remain available. Before placement, RMB cancels the selected leader or hand card.
- Aglais transfers the opponent graveyard special before adding Doomed: replay resolves, then the special is banished and the turn continues.

- Separate ordinary death, fire destruction and consume sounds. Consumed units
  no longer play a second death animation. Banish no longer flies into a consumer.
- White Frost shows one application on each of the two adjacent rows.
- AI estimates Seltkirk's first-strike duel using power and armor, preserves
  reactive cards without worthwhile targets, and reserves leader abilities.
- A low card-ordering score no longer causes a needless pass. Early passes are
  more conservative; deliberate card-economy passes and round-two dry passes remain.
- Card illustrations: 384×540, replacing old 128×180 thumbnails. Ten original
  Beta board halves: 2048×708 with shared scale and correct faction proportions.
- Original Beta backgrounds, wooden panels, buttons, frames and deck-builder
  shelves. Proportional portraits, a right reading pane and match settings under Start.
- 49 original Beta hit/weather images and flipbook frames at source resolution,
  retaining extracted intro timings and the fog frame curve.
- Controller: ←→ hand, ↑ nearest field unit; ←→ insertion, ↑↓ / LB/RB row,
  A confirm, B back. Card/target navigation stays separate from panel buttons.
  Start opens match actions; existing inspection, deck/grave and hold-to-pass remain.


# 0.2.0

- Full English package: original English card texts, translated UI/gameplay
  messages/item strings, original English battle recordings; 1418 audio media.
- Separate Russian package with the same mechanics and Russian recordings.
- Card-choice modal isolates focus and mouse input from board rows, fixing
  Dandelion: Poet choice interference. Existing mandatory choices remain required.
- Ordinary NPC decks are randomized each match; quest opponents retain fixed decks.
- Four rewarded victories per ordinary NPC, one eligible bronze/silver per win.
  Earlier first-win rewards count as one; no save schema reset. Quest rewards unchanged.
- Shared 40-profile archetype AI and pass/card-economy layer from 0.1.1.
- Source distribution and developer build/AI guides prepared for community work.

Compilation, bridge and archive checks pass. The latest fixes and English
presentation still require installed-game acceptance. Board/animation fidelity,
AI strategy refinement and broader compatibility are the next stages.
