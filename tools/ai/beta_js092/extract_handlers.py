"""Read original handler sheets / request hints as data; never run native code."""
from pathlib import Path
import xml.etree.ElementTree as E
import hashlib,json,zipfile,collections

root=Path(__file__).resolve().parents[3]
out=Path(__file__).resolve().parent/'data'
with zipfile.ZipFile(root/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/data_definitions') as z:
    raw_s=z.read('Summations.xml');raw_a=z.read('Abilities.xml')

def scalar(v):
    if v in ['True','False']:return v=='True'
    try:return int(v)
    except (ValueError,TypeError):pass
    try:return float(v)
    except (ValueError,TypeError):return v

sheets={};ordered_sheets=[];duplicates=[]
for sheet in E.fromstring(raw_s):
    entries=[]
    for a in sheet:
        entries.append({'handler':a.get('Handler'),'weight':float(a.get('Weighting','0')),
            'rounds':a.get('ValidRounds','All'),'scoring':a.get('ResultScoring','Linear'),
            'propagate':float(a.get('ScoreToPropagate','0')),
            'settings':{s.get('Type'):scalar(s.text) for s in a.findall('Settings/Setting')}})
    key=sheet.get('UniqueId');entry={'id':key,'name':sheet.get('Name'),'entries':entries}
    ordered_sheets.append(entry)
    # Original LoadUpChildHandlers scans the list and stops at FIRST matching id.
    if key not in sheets:sheets[key]=entry
    else:duplicates.append({'id':key,'selected':sheets[key]['name'],'shadowed':entry['name']})

requests={};template_info={}
for ability in E.fromstring(raw_a):
    template=ability.get('Template')
    if template is None:continue
    node_list=ability.findall('Nodes/*')
    info=template_info.setdefault(template,{'abilities':[],'hasPlayCardsNode':False})
    info['abilities'].append(int(ability.get('NId','0')))
    info['hasPlayCardsNode'] |= any(n.get('Type')=='PlayCardsNode' for n in node_list)
    variables={int(v.get('Id')):(n,v) for n in node_list for v in n if v.get('Id')}
    incoming={int(e.get('DstId')):int(e.get('SrcId')) for e in ability.findall('Connections/*')}
    def input_expression(node,name,default):
        v=node.find(name)
        if v is None:return {'literal':default}
        destination=int(v.get('Id','0'))
        if destination not in incoming:return {'literal':int(v.get('V',str(default)))}
        source=incoming[destination];pair=variables.get(source)
        if pair is not None:
            parent,var=pair
            symbol={'GetOwnerPlayerIdNode':'owner','GetOwnerOpponentPlayerIdNode':'opponentOfOwner',
                'GetCurrentPlayerIdNode':'currentPlayer'}.get(parent.get('Type'))
            if symbol:return {'symbol':symbol,'sourceNode':int(parent.get('Id'))}
        return {'unmappedSourceVariable':source}
    for node in node_list:
        kind=node.get('Type','')
        if kind not in ['RequestCardTargetsNode','RequestCardChoiceNode','RequestTemplateChoiceNode','RequestLocationTargetsNode']:continue
        hint_bits=[]
        for i,bits in enumerate(node.findall('AIHint/V/*')):
            value=int(bits.get('V','0'))
            hint_bits.extend(i*64+bit for bit in range(64) if value&(1<<bit))
        hint=hint_bits[0] if hint_bits and hint_bits[0]>0 else 1
        family={'RequestCardTargetsNode':'targets','RequestCardChoiceNode':'choices',
            'RequestTemplateChoiceNode':'templates','RequestLocationTargetsNode':'locations'}[kind]
        minimum=node.find('MinTargets' if family in ['targets','locations'] else 'MinChoices')
        maximum=node.find('MaxTargets' if family in ['targets','locations'] else 'MaxChoices')
        entry={'ability':int(ability.get('NId','0')),'node':int(node.get('Id','0')),
            'kind':family,'hint':hint,'min':int(minimum.get('V','1')) if minimum is not None else 1,
            'max':int(maximum.get('V','1')) if maximum is not None else 1}
        if family=='locations':
            entry['players']=input_expression(node,'ValidPlayers',3)
            entry['rows']=input_expression(node,'ValidTargets',7)
        requests.setdefault(template,[]).append(entry)

for name,data in [('summations',sheets),('summations-ordered',ordered_sheets),('request-hints',requests),('request-template-info',template_info)]:
    (out/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest={'sheets':len(ordered_sheets),'uniqueSheetIds':len(sheets),'duplicateIds':duplicates,
    'associations':sum(len(x['entries']) for x in ordered_sheets),
    'requestTemplates':len(requests),'requestNodes':sum(map(len,requests.values())),
    'sourceSha256':{'Summations.xml':hashlib.sha256(raw_s).hexdigest(),'Abilities.xml':hashlib.sha256(raw_a).hexdigest()},
    'note':'Request-node hints only; multiple same-kind stages require explicit shared-engine phase mapping. This is data, not completed policy integration.'}
(out/'handler-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest))
