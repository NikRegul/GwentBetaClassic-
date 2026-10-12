# 0.5.2

### Tutorial
- The tutorial was reworked into seven pages: cards and rounds, tutors, weather, summons and resurrection, spies, leaders and ambushes (Leaders and Ambushes are now separate pages).
- Every page has a "Try it" button that plays a short recorded example on a mini-board. For example, Impenetrable Fog hits the strongest unit and summons a Foglet from the deck, Fringilla passes a weak strength to a machine, Morenn triggers from ambush.
- The tutorial opens by itself before the first game and can be skipped with "Skip tutorial". The Tutorial button is always available on the deck selection screen and in the battle menu.

### Fixes
- Deleting a saved player deck did not work: the request took the starter deck branch, was rejected and the deck returned to the list. Fixed.
- The AI plays False Ciri while the opponent has not passed: when the opponent passes she returns to the AI's side. After the opponent has passed, the AI no longer plays her.

### AI decks
Based on 2,100 AI-vs-AI games (every deck against every other, no errors or hangs) and paired trials:
- Slave Infantry: Vicovaro Novices (which found no alchemy cards) replaced with Alba Armored Cavalry. Win rate 26% instead of 5%.
- Arethusa: Thunder replaced with Redanian Knights - 26% instead of 17%.
- Dryads: Sages replaced with Mahakam Guards - 31% instead of 25%.
