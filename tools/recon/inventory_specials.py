"""Freeze original special-card graphs and an honest implementation queue."""
import hashlib,json,re
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
raw=(ROOT/'data/beta924/normalized/catalog.json').read_bytes()
if hashlib.sha256(raw).hexdigest()!='022539802636cb45e92123a630c3788a0674c39b538fa1f69a64761a6b3ddbd3':raise RuntimeError('Canonical catalogue changed')
c=json.loads(raw)
done={x['templateId'] for x in json.loads((ROOT/'data/beta924/duel/slice.json').read_text(encoding='utf-8'))['cards']}
specials=[]
for t in c['templates']:
    f=t['fields'];ident=t['templateId']
    if f['Type']!=2 or f['Tier'] not in (2,4,8) or f['Kind']!=1 or t['attributes']['Availability']!='1':continue
    graphs=[g for g in c['abilities'] if g['type']=='CardAbility' and g['templateId']==ident]
    variables={}
    for g in graphs:
        for group in g['sourceTree']['children']:
            if group['tag'] in ('TemporaryVariables','PersistentVariables'):
                for v in group['children']:
                    if v['attributes'].get('Type')=='IntVar':variables[v['attributes']['Name']]=int(v['attributes']['V'])
    desc=c['localization']['ru_ru'].get(f'{ident}_tooltip','')
    for name,value in variables.items():desc=desc.replace('{'+name+'}',str(value))
    specials.append(dict(templateId=ident,title=c['localization']['ru_ru'].get(f'{ident}_name',''),
        description=re.sub('<[^>]+>','',desc).replace('\\n','\n'),fields=f,variables=variables,
        implemented=ident in done,graphs=graphs))
specials.sort(key=lambda t:(-t['fields']['Tier'],t['templateId']))
summary=dict(catalogSha256=hashlib.sha256(raw).hexdigest(),count=len(specials),
    countsByTier=dict(Counter(s['fields']['Tier'] for s in specials)),implemented=sum(s['implemented'] for s in specials),
    remaining=[s['templateId'] for s in specials if not s['implemented']],runtimeVerified=False,
    scope='Original Availability1/Kind1/special Type2/Tier2,4,8 candidates, including Doomed; current concrete definitions only count as implemented.')
(ROOT/'docs/evidence/specials-source.json').write_text(json.dumps(dict(summary=summary,specials=specials),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data/beta924/planning/specials_queue.json').write_text(json.dumps(dict(summary=summary,specials=[{k:v for k,v in s.items() if k!='graphs'} for s in specials]),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Specials:',len(specials),'implemented:',summary['implemented'],'remaining:',len(summary['remaining']))
