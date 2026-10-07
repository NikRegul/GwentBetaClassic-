"""Freeze strict Beta Northern collection, consumers and full creation dependencies."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from duel_north import northern_pools
raw=(ROOT/'data/beta924/normalized/catalog.json').read_bytes();digest=hashlib.sha256(raw).hexdigest()
if digest!='022539802636cb45e92123a630c3788a0674c39b538fa1f69a64761a6b3ddbd3':raise RuntimeError('Canonical catalogue changed')
c=json.loads(raw);duel=json.loads((ROOT/'data/beta924/duel/slice.json').read_text(encoding='utf-8'))
implemented={v['templateId'] for v in duel['cards']};recipes=json.loads((ROOT/'data/beta924/duel/northern.json').read_text(encoding='utf-8'))
collection=[t for t in c['templates'] if t['fields']['FactionId']==8 and t['fields']['Kind']==1 and t['fields']['Tier'] in (1,2,4,8) and t['attributes']['Availability']=='1']
assert len(collection)==71 and all(t['templateId'] in implemented for t in collection)
pools=northern_pools(c)
assert all(set(ids)<=implemented for ids in pools.values())
graphs=[g for g in c['abilities'] if g['type']=='CardAbility' and g['templateId'] in ({t['templateId'] for t in collection}|{v['templateId'] for v in recipes['cards']}|{200037,132204})]
views={}
for parent in (201621,201697):
 g=next(g for g in graphs if g['templateId']==parent)
 v=next(v for group in g['sourceTree']['children'] if group['tag']=='TemporaryVariables' for v in group['children'] if v['attributes']['Name']=='CardDefList')
 views[parent]=[int(v['attributes']['TemplateId']) for v in v['children'][0]['children']]
assert views=={201621:[201719,201720],201697:[201721,201722]}
spies=[dict(templateId=t['templateId'],placement=t['placement'],tokens=t['fields']['Tokens']) for t in c['templates'] if t['templateId'] in implemented and t['fields']['Type']==4 and int(t['placement']['OpponentSide']) and not int(t['placement']['PlayerSide'])]
report=dict(stage=74,catalogSha256=digest,regularCount=67,leaderCount=4,collection=collection,recipes=recipes['cards'],categories=recipes['categories'],fullCreationPools=pools,displayOnlyChoices=views,spyMetadata=spies,graphs=graphs,
    recentFightEvidence='docs/evidence/battle70-user-full.txt',runtimeVerified=False,
    note='Collection coverage is concrete consumer coverage, not full original scheduler/RNG parity or human runtime acceptance.')
(ROOT/'docs/evidence/northern-current-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Northern source:67 regular +4 leaders; pools', {id:len(ids) for id,ids in pools.items()},'spy templates',[s['templateId'] for s in spies])
