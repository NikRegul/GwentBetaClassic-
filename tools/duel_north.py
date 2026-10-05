"""Pinned Northern consumers; source category and full creation pools."""
import json,re
def load_north(root,catalog,digest):
    doc=json.loads((root/'data/beta924/duel/northern.json').read_text(encoding='utf-8'))
    if doc['catalogSha256']!=digest:raise RuntimeError('Northern source changed')
    source={a['templateId']:a for a in catalog['abilities'] if a['type']=='CardAbility'}
    result={v['templateId']:v for v in doc['cards']}
    if len(result)!=len(doc['cards']):raise RuntimeError('Duplicate Northern recipe')
    for id,v in result.items():
        if source[id]['recordKey']!=v['abilityRecordKey']:raise RuntimeError('Northern graph changed')
    return result
def northern_pools(catalog):
    pools={122108:[113301,113311,200023],122207:[113312,113301,113401]}
    for id in (201582,201595,201621,201697):
        g=next(g for g in catalog['abilities'] if g['type']=='CardAbility' and g['templateId']==id)
        n=next(n for n in g['nodes'] if n['type']=='GetCardsDefinitionsNode');p={v['tag']:v for v in n['sourceTree']['children']}
        cats=[int(v['attributes']['V']) for v in p['Category']['children'][0]['children']]
        faction=int(p['Faction']['attributes']['V']);tier=int(p['Tier']['attributes']['V']);typ=int(p['Type']['attributes']['V'])
        pools[id]=[t['templateId'] for t in catalog['templates'] if t['attributes']['Availability']=='1' and t['fields']['Kind']==1 and (not faction or t['fields']['FactionId']&faction) and t['fields']['Tier']&tier and t['fields']['Type']&typ and (not any(cats) or any(int(t['categoryWords'][i]['decimal'])&mask for i,mask in enumerate(cats)))]
        if id==201582:pools[id]=[v for v in pools[id] if v not in (201582,122203)]
    return pools
def render_north(catalog,recipes,implemented,root):
    pools=northern_pools(catalog)
    missing={id:sorted(set(ids)-set(implemented)) for id,ids in pools.items() if set(ids)-set(implemented)}
    if missing:raise RuntimeError(f'Northern creation dependencies missing: {missing}')
    expected={t['templateId'] for t in catalog['templates'] if t['fields']['FactionId']==8 and t['attributes']['Availability']=='1' and t['fields']['Kind']==1 and t['fields']['Tier'] in (1,2,4,8)}
    if expected-set(implemented):raise RuntimeError('Incomplete Northern collection')
    categories=json.loads((root/'data/beta924/duel/northern.json').read_text(encoding='utf-8'))['categories']
    lines=['','function BetaGwentNorthernPool(id : int, out ids : array<int>)','{','    ids.Clear();']
    for id in pools:lines.append(f'    if (id == {id}) BetaGwentNorthernPool{id}(ids);')
    lines+=['}']
    for id,ids in pools.items():lines+=['',f'function BetaGwentNorthernPool{id}(out ids : array<int>)','{']+[f'    ids.PushBack({v});' for v in ids]+['}']
    lines+=['','function BetaGwentNorthernCategory(id : int, kind : int) : bool','{']
    for kind in categories:lines.append(f'    if (kind == {kind}) return BetaGwentNorthernCategory{kind}(id);')
    lines+=['    return false;','}']
    for kind,masks in categories.items():
        matching=[t['templateId'] for t in catalog['templates'] if any(int(t['categoryWords'][i]['decimal'])&mask for i,mask in enumerate(masks))]
        # Small independent switches keep the REDkit parser below its statement limit.
        groups=[matching[i:i+25] for i in range(0,len(matching),25)]
        lines+=['',f'function BetaGwentNorthernCategory{kind}(id : int) : bool','{','    return '+' || '.join(f'BetaGwentNorthernCategory{kind}_{i}(id)' for i in range(len(groups)))+';','}']
        for ordinal,group in enumerate(groups):lines+=['',f'function BetaGwentNorthernCategory{kind}_{ordinal}(id : int) : bool','{','    switch (id)','    {']+[f'    case {id}: return true;' for id in group]+['    }','    return false;','}']
    view_ids=[]
    for parent in (201621,201697):
        g=next(a for a in catalog['abilities'] if a['type']=='CardAbility' and a['templateId']==parent)
        v=next(v for group in g['sourceTree']['children'] if group['tag']=='TemporaryVariables' for v in group['children'] if v['attributes']['Name']=='CardDefList')
        view_ids += [int(v['attributes']['TemplateId']) for v in v['children'][0]['children']]
    lines+=['','function BetaGwentNorthernView(id : int) : SBetaGwentDuelDefinition','{','    var d : SBetaGwentDuelDefinition;']
    for id in view_ids:
        loc=catalog['localization']['ru_ru'];desc=re.sub('<[^>]+>','',loc.get(str(id)+'_tooltip','').replace('{Boost}','2')).replace('\\n',' ')
        lines+=[f'    if (id == {id}) {{ d.header.templateId = {id}; d.title = {json.dumps(loc[str(id)+"_name"],ensure_ascii=False)}; d.description = {json.dumps(desc,ensure_ascii=False)}; return d; }}']
    lines+=['    return BetaGwentMonsterViewDefinition(id);','}'];return lines
