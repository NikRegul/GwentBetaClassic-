"""Pinned Beta Skellige collection and complete creation pools."""
import json
import re


def load_skellige(root, catalog, digest):
    doc = json.loads((root / 'data/beta924/duel/skellige.json').read_text(encoding='utf-8'))
    if doc['catalogSha256'] != digest:
        raise RuntimeError('Skellige catalogue changed')
    graphs = {g['templateId']: g for g in catalog['abilities'] if g['type'] == 'CardAbility'}
    recipes = {v['templateId']: v for v in doc['cards']}
    if len(recipes) != len(doc['cards']):
        raise RuntimeError('Duplicate Skellige recipe')
    for id, v in recipes.items():
        if v['abilityRecordKey'] != graphs.get(id, {}).get('recordKey'):
            raise RuntimeError('Skellige graph identity changed')
    return recipes


def skellige_pools(c):
    pools = {152206: [113312, 113401, 200021]}
    for id in (201581, 201642):
        g = next(g for g in c['abilities'] if g['type'] == 'CardAbility' and g['templateId'] == id)
        n = next(n for n in g['nodes'] if n['type'] == 'GetCardsDefinitionsNode')
        p = {v['tag']: v for v in n['sourceTree']['children']}
        masks = [int(v['attributes']['V']) for v in p['Category']['children'][0]['children']]
        pools[id] = [t['templateId'] for t in c['templates'] if t['attributes']['Availability'] == '1'
                     and t['fields']['Kind'] == 1 and t['fields']['FactionId'] & int(p['Faction']['attributes']['V'])
                     and t['fields']['Tier'] & int(p['Tier']['attributes']['V'])
                     and t['fields']['Type'] & int(p['Type']['attributes']['V'])
                     and (not any(masks) or any(int(t['categoryWords'][i]['decimal']) & m for i, m in enumerate(masks)))]
        if id == 201581:
            pools[id] = [v for v in pools[id] if v not in (201581, 152214)]
    return pools


def render_skellige(c, recipes, implemented, root):
    pools = skellige_pools(c)
    for id, ids in pools.items():
        if set(ids) - set(implemented):
            raise RuntimeError(f'Incomplete Skellige creation pool {id}')
    expected = {t['templateId'] for t in c['templates'] if t['attributes']['Availability'] == '1'
                and t['fields']['Kind'] == 1 and t['fields']['FactionId'] == 32 and t['fields']['Tier'] in (1, 2, 4, 8)}
    if expected - set(implemented):
        raise RuntimeError('Incomplete Skellige collection')
    out = ['', 'function BetaGwentSkelligePool(id : int, out ids : array<int>)', '{', '    ids.Clear();']
    for id, ids in pools.items():
        out += [f'    if(id=={id})' + ' { ' + ''.join(f'ids.PushBack({v});' for v in ids) + ' }']
    out += ['}']
    masks={1:17628164784392,2:1073741824,3:33554432,4:67108864,5:2199023255552,6:45035996273704960,7:536870912,8:4096,9:18014398509481984}
    out += ['', 'function BetaGwentSkelligeCategory(id : int, kind : int) : bool', '{']
    for kind in masks:out += [f'    if(kind=={kind})return BetaGwentSkelligeCategory{kind}(id);']
    out += ['    return false;', '}']
    for kind,mask in masks.items():
        ids=[t['templateId'] for t in c['templates'] if int(t['categoryWords'][0]['decimal'])&mask]
        out += ['',f'function BetaGwentSkelligeCategory{kind}(id : int) : bool','{','    switch(id)','    {']+[f'    case {v}: return true;' for v in ids]+['    }','    return false;','}']
    out += ['', 'function BetaGwentSkelligeClan(id : int) : int','{','    switch(id)','    {']
    for t in c['templates']:
        clan=sum(1<<i for i,mask in enumerate((17592186044416,1073741824,8388608,536870912,256,34359738368,8)) if int(t['categoryWords'][0]['decimal'])&mask)
        if clan:out += [f'    case {t["templateId"]}: return {clan};']
    out += ['    }','    return 0;','}','function BetaGwentSkelligeSameClan(a : int, b : int) : bool {return (BetaGwentSkelligeClan(a)&BetaGwentSkelligeClan(b))!=0;}']
    out += ['', 'function BetaGwentSkelligeView(id : int) : SBetaGwentDuelDefinition', '{', '    var d : SBetaGwentDuelDefinition;']
    for id in (201717, 201718):
        loc = c['localization']['ru_ru']
        desc = re.sub('<[^>]+>', '', loc[str(id) + '_tooltip'])
        out += [f'    if(id=={id})' + ' { d.header.templateId=' + str(id) + ';d.title=' + json.dumps(loc[str(id) + '_name'], ensure_ascii=False) + ';d.description=' + json.dumps(desc, ensure_ascii=False) + ';return d;}']
    out += ['    return BetaGwentScoiaView(id);', '}']
    return out
