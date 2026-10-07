"""Strict 0.9.24 Nilfgaard graphs and complete creation dependencies."""
import json,re

def load_nilf(root,catalog,digest):
    doc=json.loads((root/'data/beta924/duel/nilfgaard.json').read_text(encoding='utf-8'))
    if doc['catalogSha256']!=digest:raise RuntimeError('Nilfgaard source changed')
    graphs={a['templateId']:a for a in catalog['abilities'] if a['type']=='CardAbility'}
    result={v['templateId']:v for v in doc['cards']}
    if len(result)!=len(doc['cards']):raise RuntimeError('Duplicate Nilfgaard recipe')
    for id,v in result.items():
        if graphs.get(id,{}).get('recordKey')!=v['abilityRecordKey']:raise RuntimeError('Nilfgaard graph changed')
    return result

def nilf_pools(c):
    pools={142202:[113312,113401,113301],162207:[113305,113401,200023],162213:[162315,200115,162314],201597:[152304,152312,152313,152315,200144]}
    for id in (200050,201580,201583,201589,201585,201653):
        g=next(g for g in c['abilities'] if g['type']=='CardAbility' and g['templateId']==id)
        n=next(n for n in g['nodes'] if n['type']=='GetCardsDefinitionsNode');p={v['tag']:v for v in n['sourceTree']['children']}
        cats=[int(v['attributes']['V']) for v in p['Category']['children'][0]['children']]
        faction=int(p['Faction']['attributes']['V']);tier=int(p['Tier']['attributes']['V']);typ=int(p['Type']['attributes']['V'])
        pools[id]=[t['templateId'] for t in c['templates'] if t['attributes']['Availability']=='1' and t['fields']['Kind']==1 and (not faction or t['fields']['FactionId']&faction) and t['fields']['Tier']&tier and (not typ or t['fields']['Type']&typ) and (not any(cats) or any(int(t['categoryWords'][i]['decimal'])&mask for i,mask in enumerate(cats)))]
        if id==201580:pools[id]=[v for v in pools[id] if v!=id]
        if id==201583:pools[id]=[v for v in pools[id] if v not in (id,162210)]
        if id==201585:pools[id]=[v for v in pools[id] if v not in (id,142203)]
    return pools

def render_nilf(c,recipes,implemented,root):
    doc=json.loads((root/'data/beta924/duel/nilfgaard.json').read_text(encoding='utf-8'))
    pools=nilf_pools(c)
    missing={id:sorted(set(ids)-set(implemented)) for id,ids in pools.items() if set(ids)-set(implemented)}
    if missing:raise RuntimeError(f'Nilfgaard dependencies missing: {missing}')
    expected={t['templateId'] for t in c['templates'] if t['fields']['FactionId']==4 and t['attributes']['Availability']=='1' and t['fields']['Kind']==1 and t['fields']['Tier'] in (1,2,4,8)}
    if expected-set(implemented):raise RuntimeError('Incomplete Nilfgaard collection')
    lines=['','function BetaGwentNilfPool(id : int, out ids : array<int>)','{','    ids.Clear();']
    for id in pools:lines.append(f'    if (id == {id}) BetaGwentNilfPool{id}(ids);')
    lines+=['}']
    for id,ids in pools.items():lines+=['',f'function BetaGwentNilfPool{id}(out ids : array<int>)','{']+[f'    ids.PushBack({v});' for v in ids]+['}']
    lines+=['','function BetaGwentNilfSharedCategory(a : int, b : int) : bool','{']
    # Compare original words in Python; emitted switches avoid unsupported 64-bit bitsets.
    templates={t['templateId']:t for t in c['templates']}
    groups={}
    for a in implemented:
        masks=[int(x['decimal']) for x in templates[a]['categoryWords']]
        match=tuple(b for b in implemented if any(a&int(b['decimal']) for a,b in zip(masks,templates[b]['categoryWords'])))
        if match:groups.setdefault(match,[]).append(a)
    for ordinal,(matching,ids) in enumerate(groups.items()):
        lines.append('    if ('+' || '.join('a == '+str(i) for i in ids)+f') return BetaGwentNilfShared{ordinal}(b);')
    lines+=['    return false;','}']
    for ordinal,(matching,ids) in enumerate(groups.items()):
        lines+=['',f'function BetaGwentNilfShared{ordinal}(id : int) : bool','{','    switch (id)','    {']+[f'    case {id}: return true;' for id in matching]+['    }','    return false;','}']
    for name,mask in [('Dwarf',[140737488355328,0,0]),('Spell',[1048576,0,0]),('Agent',[0,2048,0]),('Elf',[549755813888,0,0]),('Dryad',[137438953472,0,0]),('Support',[8796093022208,0,0])]:
        ids=[t['templateId'] for t in c['templates'] if any(int(t['categoryWords'][i]['decimal'])&v for i,v in enumerate(mask))]
        lines+=['',f'function BetaGwentNilf{name}(id : int) : bool','{','    return '+' || '.join(f'id == {id}' for id in ids)+';','}']
    graphs={g['templateId']:g for g in c['abilities'] if g['type']=='CardAbility'}
    minimums={}
    for id,v in recipes.items():
        g=graphs.get(id);minimum=[]
        for n in g['nodes'] if g else []:
            if n['type'] not in ('RequestCardTargetsNode','RequestCardChoiceNode'):continue
            field='MinTargets' if n['type']=='RequestCardTargetsNode' else 'MinChoices'
            p=next(v for v in n['sourceTree']['children'] if v['tag']==field)
            value=int(p['attributes'].get('V','0'))
            incoming=[x for x in g['connections'] if x['destinationPort']['nodeId']==n['nodeId'] and x['destinationPort']['field']==field]
            if incoming:
                origin=next(z for z in g['nodes'] if z['nodeId']==incoming[0]['sourcePort']['nodeId'])
                if origin['type']=='GetVarNode':
                    var=next(z for group in g['sourceTree']['children'] if group['tag'] in ('TemporaryVariables','PersistentVariables') for z in group['children'] if z['attributes']['Id']==origin['sourceTree']['attributes']['VarId'])
                    value=int(var['attributes']['V'])
            minimum.append(value)
        if minimum and min(minimum)>0:minimums[id]=1
    lines+=['','function BetaGwentNilfMinimum(id : int) : int','{','    switch(id)','    {']+[f'    case {id}: return 1;' for id in minimums]+['    }','    return 0;','}']
    lines+=['','function BetaGwentNilfText(reveal : bool) : string','{','    if(reveal)return "Карта вскрыта";return "Карта скрыта";','}']
    lines+=['','function BetaGwentNilfView(id : int) : SBetaGwentDuelDefinition','{','    var d : SBetaGwentDuelDefinition;']
    for id,parent in doc['views'].items():
        loc=c['localization']['ru_ru'];desc=re.sub('<[^>]+>','',loc.get(id+'_tooltip','')).replace('\\n',' ')
        for k,v in parent.get('variables',{}).items():desc=desc.replace('{'+k+'}',str(v))
        lines+=[f'    if (id == {id}) {{ d.header.templateId = {id}; d.title = {json.dumps(loc[id+"_name"],ensure_ascii=False)}; d.description = {json.dumps(desc,ensure_ascii=False)}; return d; }}']
    lines+=['    return BetaGwentNorthernView(id);','}'];return lines
