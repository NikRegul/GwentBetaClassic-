"""Concrete Monster consumers. Never register a card without its full recipe."""
import json
def load_monsters(root,catalog,digest):
    doc=json.loads((root/'data/beta924/duel/monsters.json').read_text(encoding='utf-8'))
    if doc['catalogSha256']!=digest:raise RuntimeError('Monster source changed')
    recipes={v['templateId']:v for v in doc['cards']}
    if len(recipes)!=len(doc['cards']):raise RuntimeError('Duplicate Monster recipe')
    source={a['templateId']:a for a in catalog['abilities'] if a['type']=='CardAbility'}
    for id,v in recipes.items():
        if v.get('abilityRecordKey')!=source[id]['recordKey']:raise RuntimeError('Monster graph identity changed')
    return recipes
def monster_pools(catalog):
    pools={132203:[113401,200023,113312],133302:[132304,132201,201701,132301,132302,132306,132314,200295],132220:[200067]}
    for id in (131101,201584,201587):
        a=next(g for g in catalog['abilities'] if g['type']=='CardAbility' and g['templateId']==id)
        n=next(n for n in a['nodes'] if n['type']=='GetCardsDefinitionsNode')
        p={v['tag']:v for v in n['sourceTree']['children']}
        faction=int(p['Faction']['attributes']['V']);tier=int(p['Tier']['attributes']['V']);typ=int(p['Type']['attributes']['V'])
        availability=int(p['Availability']['children'][0]['children'][0]['attributes']['V']);assert availability==2
        category=int(p['Category']['children'][0]['children'][0]['attributes']['V'])
        # EnumMask<EAvailability>: bit 1<<BaseSet (1), not Tutorial=2.
        pools[id]=[t['templateId'] for t in catalog['templates'] if t['fields']['Kind']==1 and (not faction or t['fields']['FactionId']&faction) and t['fields']['Tier']&tier and t['fields']['Type']&typ and availability&(1<<int(t['attributes']['Availability'])) and (not category or int(t['categoryWords'][0]['decimal'])&category)]
        if id==201584:pools[id]=[v for v in pools[id] if v not in (201584,132204)]
    return pools
def render_monsters(catalog,recipes,implemented):
    pools=monster_pools(catalog)
    missing={id:sorted(set(ids)-set(implemented)) for id,ids in pools.items() if set(ids)-set(implemented)}
    if missing:raise RuntimeError(f'Monster creation pool contains unimplemented cards: {missing}')
    expected={t['templateId'] for t in catalog['templates'] if t['fields']['FactionId']==2 and t['fields']['Kind']==1 and t['fields']['Tier'] in (1,2,4,8) and t['attributes']['Availability']=='1'}
    if expected-set(implemented):raise RuntimeError(f'Incomplete Monster faction: {sorted(expected-set(implemented))}')
    lines=['','function BetaGwentMonsterTemplates(id : int, out ids : array<int>)','{','    ids.Clear();']
    for id in pools:lines.append(f'    if (id == {id}) BetaGwentMonsterPool{id}(ids);')
    lines+=['}']
    for id,ids in pools.items():
        lines += ['',f'function BetaGwentMonsterPool{id}(out ids : array<int>)','{']+[f'    ids.PushBack({v});' for v in ids]+['}']
    lines+=['','function BetaGwentMonsterSpawnAllowed(parentId : int, childId : int) : bool','{','    var ids : array<int>; BetaGwentMonsterTemplates(parentId, ids); if (ids.Contains(childId)) return true; BetaGwentNorthernPool(parentId, ids); if (ids.Contains(childId)) return true; BetaGwentNilfPool(parentId, ids); if (ids.Contains(childId)) return true; BetaGwentScoiaPool(parentId, ids); if(ids.Contains(childId))return true; BetaGwentSkelligePool(parentId, ids); if(ids.Contains(childId))return true;BetaGwentNeutralPool(parentId,ids);return ids.Contains(childId);','}']
    lines+=['','function BetaGwentMonsterViewDefinition(id : int) : SBetaGwentDuelDefinition','{','    var value : SBetaGwentDuelDefinition;']
    for id,desc in ((201666,'Укрепите все другие ваши реликты в руке, колоде и на поле на 2 ед.'),(201667,'Сыграйте бронзовый или серебряный реликт из своей колоды и укрепите его на 2 ед.')):
        lines += [f'    if (id == {id})', '    {', f'        value.header.templateId = {id}; value.title = {json.dumps(catalog["localization"]["ru_ru"][str(id)+"_name"],ensure_ascii=False)};', f'        value.description = {json.dumps(desc,ensure_ascii=False)}; return value;', '    }']
    lines+=['    return BetaGwentDuelDefinition(id);','}']
    return lines
