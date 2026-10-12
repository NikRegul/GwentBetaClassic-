"""Additional candidates where the first forty-game proposal did not improve."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
patch=json.loads((ROOT/'data/beta924/ai/deck_patch128.json').read_text('utf-8'))
second = len(sys.argv)>1 and sys.argv[1] in ('second','preserve-medic')
swaps={74:(112215,112210),87:(162107,112105)} if second else {74:(112215,132210),87:(162107,162102),94:(113102,113209)}
out={}
for d in patch['decks']:
    if d['presetId'] not in swaps:continue
    cards=list(d['expectedTemplateIds'])
    for c in d['remove']:cards.remove(c)
    cards+=d['add']
    old,new=swaps[d['presetId']]
    if d['presetId']==74 and old not in cards:
        old=next(c for c in [112210,132210] if c in cards)
    cards[cards.index(old)]=new
    out[d['presetId']]=cards
if second:
    d=next(d for d in patch['decks'] if d['presetId']==83)
    cards=list(d['expectedTemplateIds']);cards[cards.index(200132)]=201622
    out[83]=cards
if len(sys.argv)>1 and sys.argv[1]=='preserve-medic':
    d=next(d for d in patch['decks'] if d['presetId']==87)
    cards=list(d['expectedTemplateIds']);cards[cards.index(201617)]=162107
    out={87:cards}
    name='decks128-preserve-medic.json'
else:name='decks128-alternatives-second.json' if second else 'decks128-alternatives.json'
path=ROOT/'BetaGwent/build'/name
path.write_text(json.dumps(out,indent=2)+'\n','utf-8')
print(path)
