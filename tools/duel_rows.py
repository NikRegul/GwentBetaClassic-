"""Read concrete row amounts and verify the strict original event graphs."""
def render_rows(catalog):
    lines=['', 'function BetaGwentDuelRowAmount(token : int) : int', '{', '    switch (token)', '    {']
    for token, name, expected, required in [
        (256,'Boost',2,{'BeforeTurnTrigger'}),
        (512,'Change',3,{'AfterChangedLocationTokenTrigger','AfterMovedTrigger','AfterSpawnedTrigger','AfterTransformedTrigger','AfterChangedCardTokenTrigger'}),
        (1024,'Damage',4,{'BeforeTurnTrigger','AfterPlayedTrigger'}),
        (2048,'Change',2,{'AfterChangedLocationTokenTrigger','AfterMovedTrigger','AfterSpawnedTrigger','AfterTransformedTrigger','AfterChangedCardTokenTrigger'}),
    ]:
        graphs=[a for a in catalog['abilities'] if a['type']=='LocationTokenAbility' and int(a['sourceTree']['attributes']['LocationToken'])==token]
        if len(graphs)!=1:raise RuntimeError('Row ability missing')
        graph=graphs[0]
        variables={v['attributes']['Name']:v['attributes'].get('V') for g in graph['sourceTree']['children'] if g['tag']=='TemporaryVariables' for v in g['children']}
        amount=int(variables[name])
        if amount!=expected or not required.issubset({n['type'] for n in graph['nodes']}):raise RuntimeError('Row graph changed')
        lines.append(f'    case {token}: return {amount};')
    return lines+['    }','    return 0;','}']
