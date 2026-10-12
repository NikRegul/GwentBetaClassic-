"""Validate live generated decks, authored overrides and protected player rosters."""
import copy,json,sys
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ai_deck_patch128 import apply_patch
read=lambda name:json.loads((ROOT/name).read_text('utf-8-sig'))
rules=read('data/beta924/ai/rules.json')
presets=read('data/beta924/duel/presets.json')['presets']
research=read('data/beta924/ai/researched115.json')['profiles']
full={c['templateId']:c for c in read('data/beta924/planning/full_catalog.json')['cards']}
patch=read('data/beta924/ai/deck_patch128.json')
variety=read('data/beta924/ai/deck_variety128.json')
by_id={p['id']:p for p in presets};active=[p for p in rules['profiles'] if p['active']]
assert len(active)==46 and set(by_id)==set(range(1,100))
for p in active:
    assert by_id[p['presetId']]['templateIds']==p['templateIds']
    assert by_id[p['presetId']]['leader']==p['leader']
    counts=Counter(p['templateIds']);tiers=Counter(full[i]['tier'] for i in p['templateIds'])
    assert len(p['templateIds'])==(40 if p['presetId']==83 else 25)
    assert tiers[8]<=4 and tiers[4]<=6 and full[p['leader']]['leader']
    assert all(not full[i]['leader'] and full[i]['faction'] in (1,p['faction']) and n<=(3 if full[i]['tier']==2 else 1) for i,n in counts.items())
    assert not any(c.isascii() and c.isalpha() for c in p['title']),p['title']
for ident,cards in patch['retainedCards'].items():assert set(cards)<=set(by_id[int(ident)]['templateIds'])
original80=next(p for p in research if p['presetId']==80)
assert Counter(by_id[80]['templateIds'])==Counter(original80['templateIds']) and by_id[80]['leader']==original80['leader']
leaders={p['leader'] for p in active}
assert {200158,200169,201580,201589}<=leaders
for change in variety['decks']:
    counts=Counter(by_id[change['presetId']]['templateIds'])
    overlap=max(sum((counts&Counter(p['templateIds'])).values()) for p in active if p['presetId']!=change['presetId'])
    assert overlap<=18,(change['presetId'],overlap)
for change in patch['decks']:
    if change.get('enabled',True) is False and change['presetId'] not in {v['presetId'] for v in variety['decks'] if v.get('enabled',True)}:
        assert Counter(by_id[change['presetId']]['templateIds'])==Counter(change['expectedTemplateIds']),('disabled revision must keep the original roster',change['presetId'])
for ident in (74,85):
    tiers=Counter(full[i]['tier'] for i in by_id[ident]['templateIds'])
    assert tiers[8]==4 and tiers[4]==6,(ident,tiers)
assert 123201 not in by_id[94]['templateIds'] and 200019 in by_id[94]['templateIds']
assert Counter(by_id[83]['templateIds'])[201622]==2 and 122313 in by_id[83]['templateIds']
# Apply to a fresh author roster; verify safety guards reject changed author input.
source_presets=copy.deepcopy(presets[:53])
profiles=copy.deepcopy(research)
for p in profiles:
    p.update(notes=[],changes=[])
    source_presets.append(dict(id=p['presetId'],title=p['title'],leader=p['leader'],faction=p['faction'],templateIds=list(p['templateIds'])))
protected=copy.deepcopy(source_presets[:53])
apply_patch(ROOT,profiles,source_presets,full,rules['families'])
assert source_presets[:53]==protected
wrong_profiles=copy.deepcopy(research)
wrong_presets=copy.deepcopy(source_presets)
try:apply_patch(ROOT,wrong_profiles,wrong_presets,full,rules['families'])
except AssertionError:pass
else:raise AssertionError('Changed input must require explicit review')
report=dict(activeProfiles=46,legalPresets=99,protectedPlayerPresets=53,eredin80Preserved=True,retainedFringillaDraigSabrina=True,newLeaders=4,sourceGuardVerified=True,nativeGameTested=False)
(ROOT/'docs/evidence/rosters128.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
print(json.dumps(report))
