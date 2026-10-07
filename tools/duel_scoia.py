"""Strict 0.9.24 remaining Scoiatael consumers and full original creation pools."""
import json,re

def load_scoia(root,catalog,digest):
    doc=json.loads((root/'data/beta924/duel/scoiatael.json').read_text(encoding='utf-8'))
    if doc['catalogSha256']!=digest:raise RuntimeError('Scoiatael source changed')
    graphs={g['templateId']:g for g in catalog['abilities'] if g['type']=='CardAbility'}
    result={v['templateId']:v for v in doc['cards']}
    if len(result)!=len(doc['cards']):raise RuntimeError('Duplicate Scoiatael recipe')
    for id,v in result.items():
        if graphs[id]['recordKey']!=v['abilityRecordKey']:raise RuntimeError('Scoiatael graph changed')
    return result

def scoia_pools(c):
    g=next(g for g in c['abilities'] if g['type']=='CardAbility' and g['templateId']==201615)
    n=next(n for n in g['nodes'] if n['type']=='GetCardsDefinitionsNode')
    p={v['tag']:v for v in n['sourceTree']['children']}
    words=[int(v['attributes']['V']) for v in p['Category']['children'][0]['children']]
    pool=[t['templateId'] for t in c['templates'] if t['attributes']['Availability']=='1' and t['fields']['Kind']==1
          and t['fields']['FactionId']&int(p['Faction']['attributes']['V'])
          and t['fields']['Tier']&int(p['Tier']['attributes']['V'])
          and t['fields']['Type']&int(p['Type']['attributes']['V'])
          and any(int(t['categoryWords'][i]['decimal'])&w for i,w in enumerate(words))]
    return {142108:[113309,113308],201615:[id for id in pool if id!=142203]}

def render_scoia(c,recipes,implemented,root):
    pools=scoia_pools(c)
    for id,ids in pools.items():
        if set(ids)-set(implemented):raise RuntimeError(f'Incomplete Scoiatael pool {id}')
    expected={t['templateId'] for t in c['templates'] if t['fields']['FactionId']==16 and t['fields']['Kind']==1
              and t['attributes']['Availability']=='1' and t['fields']['Tier'] in (1,2,4,8)}
    if expected-set(implemented):raise RuntimeError('Incomplete Scoiatael collection')
    out=['','function BetaGwentScoiaPool(id : int, out ids : array<int>)','{','    ids.Clear();']
    for id,ids in pools.items():out+=[f'    if(id=={id})'+' { '+''.join(f'ids.PushBack({v});' for v in ids)+' }']
    out+=['}']
    mask=108086391057940480
    ids=[t['templateId'] for t in c['templates'] if int(t['categoryWords'][0]['decimal'])&mask]
    out+=['','function BetaGwentScoiaIthlinne(id : int) : bool','{','    return '+' || '.join('id=='+str(id) for id in ids)+';','}']
    out+=['','function BetaGwentScoiaView(id : int) : SBetaGwentDuelDefinition','{','    var d : SBetaGwentDuelDefinition;']
    for id in (201715,201716):
        loc=c['localization']['ru_ru'];desc=re.sub('<[^>]+>','',loc[str(id)+'_tooltip']).replace('\\n',' ')
        out+=[f'    if(id=={id})'+' { d.header.templateId='+str(id)+';d.title='+json.dumps(loc[str(id)+'_name'],ensure_ascii=False)+';d.description='+json.dumps(desc,ensure_ascii=False)+';return d;}']
    out+=['    return BetaGwentNilfView(id);','}'];return out
