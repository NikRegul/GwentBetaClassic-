"""Concrete original Beta template-choice branches; display-only templates stay separate."""
import json, re
from pathlib import Path

def load_modes(root, catalog, digest):
    document=json.loads((root/'data/beta924/duel/modes.json').read_text(encoding='utf-8'))
    if document['catalogSha256']!=digest:raise RuntimeError('Mode catalogue changed')
    templates={t['templateId']:t for t in catalog['templates']}
    modes={item['templateId']:item for item in document['cards']}
    # These are full parent graphs with native template choices, not PlayCards of the view IDs.
    for id, item in modes.items():
        graphs=[a for a in catalog['abilities'] if a['type']=='CardAbility' and a['templateId']==id]
        if len(graphs)!=1:raise RuntimeError('Mode graph count changed')
        graph=graphs[0];nodes={n['nodeId']:n for n in graph['nodes']}
        requests=[n for n in nodes.values() if n['type']=='RequestTemplateChoiceNode']
        if len(requests)!=1:raise RuntimeError('Template request changed')
        request=requests[0]
        ports={p['tag']:p for p in request['sourceTree']['children']}
        if ports['MinChoices']['attributes']['V']!='1' or ports['MaxChoices']['attributes']['V']!='1':raise RuntimeError('Mode limits changed')
        edge=next(x for x in graph['connections'] if x['destinationPort']['nodeId']==request['nodeId'] and x['destinationPort']['field']=='ValidChoices')
        producer=nodes[edge['sourcePort']['nodeId']]
        if producer['type']!='GetVarNode':raise RuntimeError('Mode choices are not original variable')
        var=next(v for group in graph['sourceTree']['children'] if group['tag']=='TemporaryVariables' for v in group['children'] if v['attributes']['Id']==producer['sourceTree']['attributes']['VarId'])
        ids=[int(v['attributes']['TemplateId']) for v in var['children'][0]['children']]
        if ids!=[v['templateId'] for v in item['choices']]:raise RuntimeError('Original mode choice order changed')
        if any(templates[v]['attributes']['Availability']!='0' for v in ids):raise RuntimeError('Choice views unexpectedly collectible')
    return modes

def render_modes(catalog,modes):
    templates={t['templateId']:t for t in catalog['templates']}
    views={v['templateId'] for item in modes.values() for v in item['choices']}
    q=lambda x:json.dumps(x,ensure_ascii=False)
    lines=['', '// Mode display definitions are never separately played.',
        'function BetaGwentDuelModeChoices(id : int, out ids : array<int>)', '{', '    ids.Clear();', '    switch (id)', '    {']
    for id,item in modes.items():
        lines += [f'    case {id}:']+[f'        ids.PushBack({v["templateId"]});' for v in item['choices']]+['        break;']
    lines += ['    }','}', '', 'function BetaGwentDuelModeDefinition(base : SBetaGwentDuelDefinition, choice : int) : SBetaGwentDuelDefinition', '{', '    switch (base.header.templateId)', '    {']
    for id,item in modes.items():
        lines += [f'    case {id}:','        switch (choice)','        {']
        for v in item['choices']:
            route=v['route']; mode={'reset_base':31,'heal_base':32,'parity':36,'destroy':35,'damage_banish':34,'row_token':37}.get(route,0)
            effect=29 if route in ('pile','pile_random') else 28
            request=0 if route in ('parity','pile','pile_random') else 1
            if route=='row_token':request=2
            lines += [f'        case {v["templateId"]}:', f'            base.effect = {effect}; base.specialMode = {mode}; base.specialRequest = {request};',
                f'            base.amount = {v.get("amount",0)}; base.targetMinimum = {v["minimum"]}; base.targetSide = {v["side"]};',
                f'            base.targetTypes = 4; base.targetTiers = {v["tiers"]}; base.targetIgnore = {v["ignore"]};',
                f'            base.pileTraitMask = {v.get("traits",0)}; base.pileLocation = {v.get("location",0)};',
                f'            base.pilePickMode = {3 if route=="pile_random" else 0}; base.specialToken = {v.get("token",v.get("parity",0))}; base.specialRowMask = 7;',
                f'            base.powerMultiplier = {1 if v.get("healReset") else 0};',
                '            return base;']
        lines += ['        }', '        break;']
    lines += ['    }', '    return base;', '}', '', 'function BetaGwentDuelViewDefinition(id : int) : SBetaGwentDuelDefinition','{','    var value : SBetaGwentDuelDefinition;', '    switch (id)','    {']
    for id in sorted(views):
        t=templates[id];f=t['fields'];variables={}
        for a in catalog['abilities']:
            if a['type']!='CardAbility' or a['templateId']!=id:continue
            for group in a['sourceTree']['children']:
                if group['tag'] not in ('TemporaryVariables','PersistentVariables'):continue
                variables.update({v['attributes']['Name']:v['attributes']['V'] for v in group['children'] if v['attributes'].get('Type')=='IntVar'})
        desc=catalog['localization']['ru_ru'].get(f'{id}_tooltip','')
        for name,v in variables.items():desc=desc.replace('{'+name+'}',str(v))
        desc=re.sub('<[^>]+>','',desc).replace('\\n','\n')
        if '{' in desc:raise RuntimeError('Unresolved mode description: '+str(id))
        lines += [f'    case {id}:', f'        value.header.templateId = {id}; value.header.typeMask = {f["Type"]}; value.header.tierMask = {f["Tier"]}; value.header.factionMask = {f["FactionId"]};',
            f'        value.title = {q(catalog["localization"]["ru_ru"][f"{id}_name"])}; value.description = {q(desc)};', '        return value;']
    lines += ['    }', '    return BetaGwentNeutralView(id);', '}']
    return lines
