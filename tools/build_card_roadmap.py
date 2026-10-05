"""Inventory original collection candidates and missing ability consumers, not runtime parity."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
raw = (ROOT / 'data/beta924/normalized/catalog.json').read_bytes()
digest = hashlib.sha256(raw).hexdigest()
if digest != '022539802636cb45e92123a630c3788a0674c39b538fa1f69a64761a6b3ddbd3':
    raise RuntimeError('Canonical catalogue changed')
catalog = json.loads(raw)
duel = json.loads((ROOT / 'data/beta924/duel/slice.json').read_text(encoding='utf-8'))
implemented = {c['templateId'] for c in duel['cards']}
# Original GwentGameplay.EFactionId, read from Assembly-CSharp.dll via Mono.Cecil.
factions = {1:'Neutral',2:'Monsters',4:'Nilfgaard',8:'NorthernRealms',16:'Scoiatael',32:'Skellige'}
records = []
for card in catalog['templates']:
    f = card['fields']; ident = card['templateId']
    if int(card['attributes']['Availability']) != 1 or f['Kind'] != 1 or f['Tier'] not in (1,2,4,8):
        continue
    graphs = [g for g in catalog['abilities'] if g['type'] == 'CardAbility' and g['templateId'] == ident]
    records.append(dict(templateId=ident, title=catalog['localization']['ru_ru'].get(f'{ident}_name',''),
        faction=factions.get(f['FactionId'],str(f['FactionId'])), factionMask=f['FactionId'], tier=f['Tier'],
        power=f['Power'], typeMask=f['Type'], leader=f['Tier']==1,
        implementedInClosedDuel=ident in implemented,
        abilityRecordKeys=[g['recordKey'] for g in graphs],
        abilityGraphNodeCount=sum(len(g['nodes']) for g in graphs)))
records.sort(key=lambda c:(c['factionMask'], c['leader'], -c['tier'], c['templateId']))
summary = []
for mask, title in factions.items():
    entries = [r for r in records if r['factionMask']==mask]
    cards = [r for r in entries if not r['leader']]; leaders = [r for r in entries if r['leader']]
    summary.append(dict(faction=title,factionMask=mask,collectionCandidates=len(cards),
        implementedCollection=sum(r['implementedInClosedDuel'] for r in cards),
        remainingCollection=sum(not r['implementedInClosedDuel'] for r in cards),
        leaderCandidates=len(leaders),implementedLeaders=sum(r['implementedInClosedDuel'] for r in leaders)))
result = dict(catalogSha256=digest,source='Original client0.9.24.3.432 catalogue; faction enum from managed assembly',
    scope='Availability1/Kind1/Tier1,2,4,8 candidates, including Doomed. Additional leader/game-mode restrictions must be checked before enabling each candidate. Token/internal templates and arbitrary graph parity are separate work.',
    candidateCount=len(records), collectionCandidateCount=sum(not r['leader'] for r in records),
    leaderCandidateCount=sum(r['leader'] for r in records), byFaction=summary, cards=records,
    implementedMeans='Concrete closed-duel definition/consumer exists; not a claim of full original runtime parity.',
    runtimeVerified=False)
target=ROOT/'data/beta924/planning/card_implementation_queue.json'
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
