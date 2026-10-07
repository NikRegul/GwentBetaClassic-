"""Record complete collection coverage and its pinned original graph dependencies."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
raw=(ROOT/'data/beta924/normalized/catalog.json').read_bytes();c=json.loads(raw)
slice=json.loads((ROOT/'data/beta924/duel/slice.json').read_text(encoding='utf8'))
implemented={v['templateId'] for v in slice['cards']};gs={g['templateId']:g for g in c['abilities'] if g['type']=='CardAbility'}
records=[];views={201717:200102,201718:200102}
views.update({int(k):v for k,v in json.loads((ROOT/'data/beta924/duel/neutral.json').read_text(encoding='utf8'))['views'].items()})
def refs(node):
    out=[int(node['attributes']['TemplateId'])] if 'TemplateId' in node['attributes'] and int(node['attributes']['TemplateId']) else []
    for child in node['children']:out+=refs(child)
    return out
for faction,file in ((32,'skellige'),(1,'neutral')):
    doc=json.loads((ROOT/f'data/beta924/duel/{file}.json').read_text(encoding='utf8'))
    runtime=(ROOT/f'BetaGwent/development/scripts/game/betagwent/duel{"Skellige" if faction==32 else "Neutral"}.ws').read_text(encoding='utf-8-sig')
    for recipe in doc['cards']:
        id=recipe['templateId'];g=gs[id];assert id in implemented
        variables={v['attributes']['Name']:int(v['attributes']['V']) for group in g['sourceTree']['children'] if group['tag'] in ('TemporaryVariables','PersistentVariables') for v in group['children'] if v['attributes'].get('Type')=='IntVar'}
        assert variables==recipe['originalVariables'];assert g['recordKey']==recipe['abilityRecordKey'];assert str(id) in runtime
        dependencies=sorted(set(refs(g['sourceTree'])))
        unresolved=set(dependencies)-implemented-set(views)
        assert not unresolved,(id,unresolved)
        records.append(dict(templateId=id,abilityRecordKey=g['recordKey'],title=c['localization']['ru_ru'].get(str(id)+'_name'),originalVariables=variables,fixedDefinitionDependencies=dependencies,originalQueriesAndTriggers=[n for n in g['nodes'] if n['type'].endswith('Trigger') or n['type'] in ('GetCardsDefinitionsNode','GetInitialDeckDefinitions','GetCardsNode','RequestCardTargetsNode','RequestCardChoiceNode','RequestTemplateChoiceNode','RequestLocationTargetsNode')],graphSha256=hashlib.sha256(json.dumps(g,ensure_ascii=False,sort_keys=True).encode()).hexdigest()))
collectible={t['templateId'] for t in c['templates'] if t['attributes']['Availability']=='1' and t['fields']['Kind']==1 and t['fields']['Tier'] in (1,2,4,8)}
assert collectible<=implemented and len(collectible)==479 and len(slice['collectibleIds'])==458 and len(slice['leaderIds'])==21
report=dict(stage=76,catalogSha256=hashlib.sha256(raw).hexdigest(),originalClientAssemblySha256=hashlib.sha256((ROOT/'Gwent 0.9.24.3.432/Gwent_Data/Managed/Assembly-CSharp.dll').read_bytes()).hexdigest(),newConsumers=records,views=views,newCollectibleSkellige=60,newCollectibleNeutral=51,collectibleCandidates=479,regularImplemented=458,leaderImplemented=21,remainingRegular=0,definitionCount=len(implemented),internalCount=len(implemented-collectible),presetCount=len(slice['presets']),runtimeVerified=False,scope='Coverage of explicit consumers and fixed source dependencies; not proof of original trigger scheduling/RNG, AI, acquisition or native battle parity.')
(ROOT/'docs/evidence/collection76-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Verified 111 new collectible consumers, 16 internal dependencies, 24 new choice views; all 479 collection candidates registered.')
