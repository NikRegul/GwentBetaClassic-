"""Complete strict Beta neutral consumers and creation choices."""
import json,re

def load_neutral(root,catalog,digest):
    doc=json.loads((root/'data/beta924/duel/neutral.json').read_text(encoding='utf8'))
    if doc['catalogSha256']!=digest:raise RuntimeError('Neutral catalogue changed')
    gs={g['templateId']:g for g in catalog['abilities'] if g['type']=='CardAbility'}
    result={v['templateId']:v for v in doc['cards']}
    for id,v in result.items():
        if v['abilityRecordKey']!=gs[id]['recordKey']:raise RuntimeError('Neutral graph changed')
    return result

def neutral_pools(c):
    pools={112108:[112401,112402],112109:[112403,112404],113208:[113302,113305,113301],201627:[201725,201731,201737]}
    for id in (200056,200058,200087,132215,201631):
        g=next(g for g in c['abilities'] if g['type']=='CardAbility' and g['templateId']==id)
        n=next(n for n in g['nodes'] if n['type']=='GetCardsDefinitionsNode');p={v['tag']:v for v in n['sourceTree']['children']}
        cat=[int(v['attributes']['V']) for v in p['Category']['children'][0]['children']]
        tier=int(p['Tier']['attributes']['V']);types=int(p['Type']['attributes']['V'])
        pools[id]=[t['templateId'] for t in c['templates'] if t['attributes']['Availability']=='1' and t['fields']['Kind']==1 and (not tier or t['fields']['Tier']&tier) and (not types or t['fields']['Type']&types) and (not any(cat) or any(int(t['categoryWords'][i]['decimal'])&v for i,v in enumerate(cat)))]
    return pools

def render_neutral(c,recipes,implemented,root):
    pools=neutral_pools(c)
    for id,ids in pools.items():
        if set(ids)-set(implemented):raise RuntimeError(f'Incomplete neutral creation {id}')
    expected={t['templateId'] for t in c['templates'] if t['attributes']['Availability']=='1' and t['fields']['Kind']==1 and t['fields']['Tier'] in (1,2,4,8)}
    if expected-set(implemented):raise RuntimeError('Incomplete full Beta collection')
    out=['','function BetaGwentNeutralPool(id : int, out ids : array<int>)','{','    ids.Clear();']
    for id in pools:out += [f'    if(id=={id})BetaGwentNeutralPool{id}(ids);']
    out+=['}']
    for id,ids in pools.items():out += ['',f'function BetaGwentNeutralPool{id}(out ids : array<int>)','{']+[f'    ids.PushBack({v});' for v in ids]+['}']
    doc=json.loads((root/'data/beta924/duel/neutral.json').read_text(encoding='utf8'))
    out+=['','function BetaGwentNeutralView(id : int) : SBetaGwentDuelDefinition','{','    var d : SBetaGwentDuelDefinition;']
    for id,parent in doc['views'].items():
        loc=c['localization']['ru_ru'];desc=re.sub('<[^>]+>','',loc.get(id+'_tooltip',''))
        g=next((g for g in c['abilities'] if g['type']=='CardAbility' and g['templateId']==int(id)),next(g for g in c['abilities'] if g['type']=='CardAbility' and g['templateId']==parent))
        for group in g['sourceTree']['children']:
            if group['tag'] in ('TemporaryVariables','PersistentVariables'):
                for v in group['children']:
                    if v['attributes'].get('Type')=='IntVar':desc=desc.replace('{'+v['attributes']['Name']+'}',v['attributes']['V'])
        if '{' in desc:raise RuntimeError('Unresolved neutral choice '+id)
        out += [f'    if(id=={id})'+' {d.header.templateId='+id+';d.title='+json.dumps(loc[id+'_name'],ensure_ascii=False)+';d.description='+json.dumps(desc,ensure_ascii=False)+';return d;}']
    out+=['    return BetaGwentSkelligeView(id);','}']
    out+=['','function BetaGwentNeutralDraconid(id : int) : bool','{','    switch(id)','    {']+[f'    case {t["templateId"]}: return true;' for t in c['templates'] if int(t['categoryWords'][0]['decimal'])&281474976710656]+['    }','    return false;','}']
    g=next(g for g in c['abilities'] if g['type']=='CardAbility' and g['templateId']==201774)
    def refs(node):
        result=[int(node['attributes']['TemplateId'])] if 'TemplateId' in node['attributes'] else []
        for ch in node['children']:result+=refs(ch)
        return result
    family=sorted(set(refs(g['sourceTree'])))
    out+=['','function BetaGwentNeutralDandelionFamily(id : int) : bool','{','    switch(id)','    {']+[f'    case {id}: return true;' for id in family]+['    }','    return false;','}']
    return out
