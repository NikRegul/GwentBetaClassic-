"""Build a closed DEV duel card table from the strict 0.9.24 catalogue."""
import hashlib
import json
import re
from collections import Counter
from ws_codegen import bounded_helpers, localized_plain_text
from pathlib import Path
from duel_modes import load_modes, render_modes
from duel_rows import render_rows
from duel_monsters import load_monsters, render_monsters
from duel_north import load_north, render_north
from duel_nilf import load_nilf, render_nilf
from duel_scoia import load_scoia, render_scoia
from duel_skellige import load_skellige, render_skellige
from duel_neutral import load_neutral, render_neutral

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'data/beta924/normalized/catalog.json'
raw = path.read_bytes()
if hashlib.sha256(raw).hexdigest() != '022539802636cb45e92123a630c3788a0674c39b538fa1f69a64761a6b3ddbd3':
    raise RuntimeError('Canonical catalogue changed')
c = json.loads(raw)
cards = {t['templateId']: t for t in c['templates']}
modes = load_modes(ROOT,c,hashlib.sha256(raw).hexdigest())
monsters = load_monsters(ROOT,c,hashlib.sha256(raw).hexdigest())
northern = load_north(ROOT,c,hashlib.sha256(raw).hexdigest())
nilfgaard = load_nilf(ROOT,c,hashlib.sha256(raw).hexdigest())
scoiatael = load_scoia(ROOT,c,hashlib.sha256(raw).hexdigest())
skellige = load_skellige(ROOT,c,hashlib.sha256(raw).hexdigest())

neutral = load_neutral(ROOT,c,hashlib.sha256(raw).hexdigest())

effects = {200158:24,112405:0,132310:0,132209:0,112103:0,112106:1,113301:1,113310:2,
    113311:3,153301:4,113308:5,122216:6,200055:7,113302:8,113303:9,113401:10,113402:11,113305:12,113312:13,132303:1,132402:14,132307:15,132302:0,200295:0,132107:16,132213:0,132405:0,132305:0,132306:17,132205:18,113319:19,200053:20,200307:0,132217:21,132316:0,200308:0,132313:22,132308:23,132309:25,132304:26,132206:26,132207:26,132208:26,132102:27,200073:1}
specials = json.loads((ROOT / 'data/beta924/duel/specials.json').read_text(encoding='utf-8'))
if specials['catalogSha256'] != hashlib.sha256(raw).hexdigest(): raise RuntimeError('Special source mismatch')
specials = {v['templateId']:v for v in specials['cards']}
effects.update({id:spec.get('effect',28) for id,spec in specials.items()})
effects.update({id:33 for id in modes})
effects.update({id:34 for id in monsters})
effects.update({id:34 for id in northern})
effects.update({id:34 for id in nilfgaard})
effects.update({id:34 for id in scoiatael})
effects.update({id:34 for id in skellige})
effects[152405]=0
effects[200320]=0
effects[201576]=0
effects.update({id:34 for id in neutral})
units_document=json.loads((ROOT/'data/beta924/duel/units.json').read_text(encoding='utf-8'))
if units_document['catalogSha256']!=hashlib.sha256(raw).hexdigest():raise RuntimeError('Unit source changed')
units={v['templateId']:v for v in units_document['cards']}
effects.update({id:v['effect'] for id,v in units.items()})
for id in units_document['generatedPlainUnitIds']:
    if any(a['type']=='CardAbility' and a['templateId']==id for a in c['abilities']):raise RuntimeError('Generated unit has an unimplemented ability')
    if cards[id]['fields']['Type']!=4 or cards[id]['attributes']['Availability']!='0':raise RuntimeError('Generated eligibility changed')
    effects[id]=0

def original_int_port(graph,node,field):
    ports={v['tag']:v for v in node['sourceTree']['children']}
    value=ports[field]['attributes'].get('V')
    incoming=[x for x in graph['connections'] if x['destinationPort']['nodeId']==node['nodeId'] and x['destinationPort']['field']==field]
    if incoming:
        if len(incoming)!=1:raise RuntimeError('Multiple input bindings')
        origin=next(n for n in graph['nodes'] if n['nodeId']==incoming[0]['sourcePort']['nodeId'])
        if origin['type']!='GetVarNode':raise RuntimeError('Nonconstant source binding')
        variable=next(v for group in graph['sourceTree']['children'] if group['tag'] in ('TemporaryVariables','PersistentVariables') for v in group['children'] if v['attributes']['Id']==origin['sourceTree']['attributes']['VarId'])
        value=variable['attributes']['V']
    return int(value)
presets_path = ROOT / 'data/beta924/duel/presets.json'
presets_raw = presets_path.read_bytes()
presets = json.loads(presets_raw)['presets']
if [p['id'] for p in presets] != list(range(1, len(presets) + 1)) or len({p['key'] for p in presets}) != len(presets):
    raise RuntimeError('Preset IDs/keys must be unique and contiguous')
for preset in presets:
    deck = preset['templateIds']
    if not 25 <= len(deck) <= 40: raise RuntimeError('Preset must have25..40 cards: ' + preset['key'])
    if preset['faction'] not in (2,4,8,16,32) or preset['leader'] not in effects or cards[preset['leader']]['fields']['Tier'] != 1 or cards[preset['leader']]['fields']['FactionId'] != preset['faction']: raise RuntimeError('Unsupported preset faction/leader')
    for id, count in Counter(deck).items():
        if id not in effects: raise RuntimeError('Preset ability not implemented')
        t = cards[id]; f = t['fields']
        if f['FactionId'] not in (1,preset['faction']) or f['Kind'] != 1 or f['Tier'] not in (2,4,8) or int(t['attributes']['Availability']) != 1:
            raise RuntimeError('Ineligible duel card')
        if count > (3 if f['Tier'] == 2 else 1): raise RuntimeError('Copy limit')
    preset['unitCount'] = sum(cards[id]['fields']['Type'] == 4 for id in deck)
    preset['specialCount'] = len(deck) - preset['unitCount']
    preset['goldCount'] = sum(cards[id]['fields']['Tier'] == 8 for id in deck)
    preset['silverCount'] = sum(cards[id]['fields']['Tier'] == 4 for id in deck)
    if preset['goldCount'] > 4 or preset['silverCount'] > 6: raise RuntimeError('Tier limits')
    preset['cards'] = [dict(templateId=id, copies=count) for id, count in Counter(deck).items()]
deck = presets[0]['templateIds']
def quoted(value): return json.dumps(value, ensure_ascii=False)
lines = ['// Generated strict Beta definitions. Closed DEV duel; no generic graph interpreter.',
    'struct SBetaGwentDuelDefinition', '{', '    var header : SBetaGwentTemplateHeader;',
    '    var unitTraits, targetExcludedTraits : int;', '    var pileLocation, pilePickMode, pileCandidateLimit, pileShuffle, pileTraitMask : int;', '    var specialMode, specialRequest, specialCount, specialRadius, specialToken, specialRowMask : int;', '    var title, description : string;', '    var conditionalDamage, targetExcludedFaction : int;', '    var effect, amount, addedArmor, tokens, weatherToken, targetMinimum, targetSide, playTemplateId : int;', '    var passiveBoost, passiveWeatherToken, passivePriority, deathwishDamage, deathwishIgnore : int;', '    var consumeMaximum, deathwishSpawnTemplate, deathwishSpawnCount : int;', '    var consumePassiveBoost, consumePassiveLocations, consumePassivePriority, deathwishSummonTemplate : int;', '    var consumeLocation, consumeTierMask, consumePassiveEvents : int;', '    var targetIgnore, lockTokens, lockOperation, powerMultiplier : int;', '    var targetTypes, targetTiers, transformTemplate, transformResetMode : int;', '    var deploySpawnTemplate, deploySpawnCount, deathwishSpawnMode, beforeConsumeAttackerBoost, banishedConsumeAttackerBoost : int;', '    var initialTimer, timerPeriod, timerPriority, conditionalBoost, conditionalWeatherToken, deploySummonTemplate, deploySummonOtherTemplate, deploySummonIgnore, deploySummonLinked : int;', '}',
    'function BetaGwentDuelDefinition(id : int) : SBetaGwentDuelDefinition', '{',
    '    var value : SBetaGwentDuelDefinition;', '    switch (id)', '    {']
records = []
for id, effect in effects.items():
    t = cards[id]; f = t['fields']; vars = {}
    graphs = [a for a in c['abilities'] if a['type'] == 'CardAbility' and a['templateId'] == id]
    for a in graphs:
        for item in a['sourceTree']['children']:
            if item['tag'] in ('TemporaryVariables','PersistentVariables'):
                for var in item['children']:
                    attrs = var['attributes']
                    if attrs.get('Type') == 'IntVar': vars[attrs['Name']] = int(attrs['V'])
    if id == 200158:
        a = graphs[0]; nodes = {n['nodeId']:n for n in a['nodes']}
        def port(nid): return {p['tag']:p['attributes'].get('V') for p in nodes[nid]['sourceTree']['children']}
        definitions = [v for g in a['sourceTree']['children'] if g['tag']=='TemporaryVariables'
            for v in g['children'] if v['attributes'].get('Name')=='CardDefList']
        choices = [int(x['attributes']['TemplateId']) for x in definitions[0]['children'][0]['children']]
        edges = {(x['sourcePort']['nodeId'],x['sourcePort']['field'],x['destinationPort']['nodeId'],x['destinationPort']['field']) for x in a['connections']}
        if choices != [113305,113312] or vars['MaxTargets'] != 1: raise RuntimeError('Dagon choices changed')
        if port(32)['MaxChoices'] != '1' or port(63)['Count'] != '1' or port(63)['SpawnType'] != '3' or port(63)['SpawnLocation'] != '0' or port(162)['Location'] != '256' or port(162)['Index'] != '0': raise RuntimeError('Dagon spawn changed')
        if not {(12,'FlowOut',32,'FlowIn'),(153,'Out',32,'ValidChoices'),(158,'Out',32,'MinChoices'),(32,'FlowOut',162,'FlowIn'),(162,'FlowOut',63,'FlowIn'),(162,'CardPosition',63,'Position'),(172,'Out',162,'PlayerId'),(32,'SelectedChoices',72,'DS'),(72,'DV',63,'Definition'),(63,'SpawnedCards',103,'CardsToPlay'),(63,'FlowOut',103,'FlowIn')} <= edges: raise RuntimeError('Dagon wiring changed')
    amount = vars.get('Damage',vars.get('Boost',0)) if effect in (1,2,3,4,8,9,10,12,13,22) else 0
    conditional_boost, conditional_weather, deploy_summon = 0, 0, 0
    conditional_damage, target_excluded_faction = 0, 0
    summon_other, summon_ignore, summon_linked = 0, 0, 0
    weather_token, target_minimum, target_side, play_template = 0, 0, 0, 0
    if id in (132102,200073):
        if len(graphs)!=1: raise RuntimeError('New control graph count changed')
        a=graphs[0]; nodes={n['nodeId']:n for n in a['nodes']}
        def port(nid): return {p['tag']:p['attributes'].get('V') for p in nodes[nid]['sourceTree']['children']}
        edges={(x['sourcePort']['nodeId'],x['sourcePort']['field'],x['destinationPort']['nodeId'],x['destinationPort']['field']) for x in a['connections']}
        amount=vars['Damage']
        if id==132102:
            conditional_damage=vars['Damage2']; conditional_weather=int(port(498)['Token'])
            target_side=2; target_minimum=int(port(16)['MinTargets'])
            if (f['Power'],f['Tier'],amount,conditional_damage,conditional_weather,target_minimum)!=(9,8,4,8,1,1): raise RuntimeError('Imlerith values changed')
            if port(47)['LocationId']!='7' or port(47)['CardTypes']!='4' or port(47)['CardTiers']!='15' or port(47)['Ignore']!='264' or port(498)['Negate']!='False': raise RuntimeError('Imlerith target query changed')
            if port(465)['Operation']!='1' or port(465)['TargetedPower']!='0' or port(465)['IgnoreArmor']!='False': raise RuntimeError('Imlerith power operation changed')
            if not {(121,'Out',47,'PlayerId'),(10,'FlowOut',16,'FlowIn'),(47,'Out',16,'ValidTargets'),(16,'FlowOut',502,'FlowIn'),(16,'SelectedTargets',502,'Cards'),(498,'Out',502,'e0'),(502,'FlowSuccess',451,'FlowIn'),(502,'FlowFail',456,'FlowIn'),(449,'Out',451,'In'),(447,'Out',456,'In'),(451,'FlowOut',465,'FlowIn'),(456,'FlowOut',465,'FlowIn'),(478,'Out',465,'Power'),(16,'SelectedTargets',465,'Targets'),(482,'Out',465,'Attacker')}<=edges: raise RuntimeError('Imlerith conditional wiring changed')
            if {nid:nodes[nid]['sourceTree']['attributes']['VarId'] for nid in (447,449,451,456,478)}!={447:'432',449:'433',451:'434',456:'434',478:'434'}: raise RuntimeError('Imlerith variable bindings changed')
        else:
            target_excluded_faction=int(port(28)['Faction']);target_minimum=int(port(53)['MinTargets'])
            if (f['Power'],f['Tier'],amount,target_excluded_faction,target_minimum)!=(6,4,8,2,1) or port(28)['Negate']!='True': raise RuntimeError('Adda values changed')
            if port(8)['PlayerId']!='3' or port(8)['LocationId']!='7' or port(8)['CardTypes']!='4' or port(8)['CardTiers']!='15' or port(8)['Ignore']!='264': raise RuntimeError('Adda target query changed')
            if port(35)['Operation']!='1' or port(35)['TargetedPower']!='0' or port(35)['IgnoreArmor']!='False': raise RuntimeError('Adda damage operation changed')
            if not {(28,'Out',15,'e0'),(8,'Out',15,'Cards'),(2,'FlowOut',15,'FlowIn'),(15,'FlowSuccess',53,'FlowIn'),(15,'FilteredCards',53,'ValidTargets'),(53,'FlowOut',35,'FlowIn'),(53,'SelectedTargets',35,'Targets'),(2,'CardPlayed',35,'Attacker'),(50,'Out',35,'Power')}<=edges: raise RuntimeError('Adda wiring changed')
    if id in (132206,132207,132208):
        if len(graphs)!=1: raise RuntimeError('Crone graph count changed')
        a=graphs[0]; nodes={n['nodeId']:n for n in a['nodes']}
        def port(nid): return {p['tag']:p['attributes'].get('V') for p in nodes[nid]['sourceTree']['children']}
        definitions=[]
        for group in a['sourceTree']['children']:
            if group['tag']!='TemporaryVariables': continue
            for var in group['children']:
                for value in var['children']:
                    if 'TemplateId' in value['attributes']: definitions.append(int(value['attributes']['TemplateId']))
                    definitions += [int(x['attributes']['TemplateId']) for x in value['children'] if 'TemplateId' in x['attributes']]
        if set(definitions)!={132206,132207,132208}-{id} or len(definitions)!=2: raise RuntimeError('Crone partners changed')
        deploy_summon,summon_other=definitions; summon_ignore=int(port(26)['Ignore']); summon_linked=1
        if f['LinkedTemplateId']!=132206 or f['LinkedTemplateOrder']!={132206:0,132207:1,132208:2}[id]: raise RuntimeError('Crone linked definitions changed')
        if port(26)['LocationId']!='16' or port(26)['CardTypes']!='4' or port(26)['CardTiers']!='14' or summon_ignore!={132206:264,132207:8,132208:264}[id]: raise RuntimeError('Crone summon query changed')
        trigger=183 if id==132206 else 180
        edges={(x['sourcePort']['nodeId'],x['sourcePort']['field'],x['destinationPort']['nodeId'],x['destinationPort']['field']) for x in a['connections']}
        common={(30,'Out',26,'PlayerId'),(26,'Out',33,'Cards'),(33,'FlowSuccess',19,'FlowIn'),(33,'FilteredCards',19,'Cards'),(42,'Out',19,'Summoner'),(trigger,'FlowOut',33,'FlowIn')}
        if not common<=edges: raise RuntimeError('Crone summon wiring changed')
        if id==132206:
            if port(170)['Negate']!='False' or not {(170,'Out',33,'e0'),(180,'Out',170,'Definitions')}<=edges: raise RuntimeError('Crone list wiring changed')
        else:
            if port(108)['Op']!='1' or port(108)['Negate']!='False' or not {(108,'Out',33,'e0'),(150,'Out',108,'e0'),(159,'Out',108,'e1'),(148,'Out',150,'Definition'),(157,'Out',159,'Definition')}<=edges: raise RuntimeError('Crone OR wiring changed')
    if id in (132304,132309):
        a=graphs[0]; nodes={n['nodeId']:n for n in a['nodes']}
        def port(nid): return {p['tag']:p['attributes'].get('V') for p in nodes[nid]['sourceTree']['children']}
        edges={(x['sourcePort']['nodeId'],x['sourcePort']['field'],x['destinationPort']['nodeId'],x['destinationPort']['field']) for x in a['connections']}
        if id == 132304:
            definitions=[v for g in a['sourceTree']['children'] if g['tag']=='TemporaryVariables' for v in g['children'] if v['attributes'].get('Name')=='CardDef']
            deploy_summon=int(definitions[0]['children'][0]['attributes']['TemplateId'])
            if deploy_summon!=132304 or f['LinkedTemplateId']!=0 or port(26)['LocationId']!='16' or port(26)['CardTypes']!='4' or port(26)['CardTiers']!='14' or port(26)['Ignore']!='0': raise RuntimeError('Arachas summon query changed')
            if not {(30,'Out',26,'PlayerId'),(26,'Out',33,'Cards'),(188,'FlowOut',33,'FlowIn'),(33,'FlowSuccess',19,'FlowIn'),(33,'FilteredCards',19,'Cards'),(42,'Out',19,'Summoner'),(148,'Out',150,'Definition'),(150,'Out',33,'e0')} <= edges: raise RuntimeError('Arachas summon wiring changed')
        else:
            amount=vars['Damage']; conditional_boost=vars['Boost']; conditional_weather=int(port(415)['TokenMask']); target_side=2; target_minimum=int(port(16)['MinTargets'])
            if (amount,conditional_boost,conditional_weather,target_minimum)!=(3,2,1,0) or vars['MaxTargets']!=1: raise RuntimeError('Warrior values changed')
            if port(47)['LocationId']!='7' or port(47)['CardTypes']!='4' or port(47)['CardTiers']!='15' or port(47)['Ignore']!='264' or port(508)['PowerType']!='0' or port(508)['Op']!='0' or port(508)['Power']!='0': raise RuntimeError('Warrior query/filter changed')
            if port(465)['Operation']!='1' or port(465)['IgnoreArmor']!='False' or port(527)['Operation']!='0': raise RuntimeError('Warrior power operation changed')
            if nodes[490]['sourceTree']['attributes']['VarId']!='432' or nodes[540]['sourceTree']['attributes']['VarId']!='433': raise RuntimeError('Warrior variable binding changed')
            if not {(121,'Out',47,'PlayerId'),(10,'FlowOut',16,'FlowIn'),(47,'Out',16,'ValidTargets'),(16,'SelectedTargets',465,'Targets'),(16,'FlowOut',465,'FlowIn'),(490,'Out',465,'Power'),(465,'FlowOut',498,'FlowIn'),(508,'Out',498,'e0'),(498,'FlowSuccess',527,'FlowIn'),(498,'FlowFail',310,'FlowIn'),(310,'Location',415,'LocationMask'),(310,'PlayerId',415,'PlayerMask'),(415,'Out',550,'List'),(550,'FlowOutTrue',527,'FlowIn'),(546,'Out',527,'Targets'),(540,'Out',527,'Power')} <= edges: raise RuntimeError('Warrior conditional wiring changed')
    if id == 132303:
        # ability/149: owner-opponent107 feeds GetCards100; RequestCardTargets45.
        target_side = 2
        requests = [n for a in graphs for n in a['nodes'] if n['type'] == 'RequestCardTargetsNode']
        if len(requests) != 1: raise RuntimeError('Wyvern request graph changed')
        ports = {x['tag']:x['attributes'].get('V') for x in requests[0]['sourceTree']['children']}
        target_minimum = int(ports['MinTargets'])
    if id == 132402:
        # ability/162: CardDefinitionVar Frost used by FilterCardList.
        frost = [v for a in graphs for group in a['sourceTree']['children']
                 if group['tag'] in ('TemporaryVariables','PersistentVariables')
                 for v in group['children'] if v['attributes'].get('Name') == 'Frost']
        if len(frost) != 1: raise RuntimeError('Hound Frost variable changed')
        play_template = int(frost[0]['children'][0]['attributes']['TemplateId'])
        if play_template != 113302: raise RuntimeError('Unexpected Hound tutor')
    if effect in (8,12,13):
        for a in graphs:
            for node in a['nodes']:
                ports = {p['tag']:p['attributes'].get('V') for p in node['sourceTree']['children']}
                if node['type'] == 'ChangeLocationTokensNode': weather_token = int(ports['Tokens'])
                if node['type'] == 'RequestLocationTargetsNode': target_minimum = int(ports['MinTargets'])
        if weather_token not in (1,2,4): raise RuntimeError('Unknown weather token')
    passive_boost, passive_token, passive_priority, death_damage, death_ignore = 0, 0, 0, 0, 0
    if id == 132302:
        passive_boost = vars['Boost']
        locations = [n for a in graphs for n in a['nodes'] if n['type'] == 'GetLocationsNode']
        triggers = [n for a in graphs for n in a['nodes'] if n['type'] == 'AfterTurnTrigger']
        if len(locations)!=1 or len(triggers)!=1: raise RuntimeError('Ancient Foglet graph changed')
        ports = {x['tag']:x['attributes'].get('V') for x in locations[0]['sourceTree']['children']}
        passive_token = int(ports['TokenMask'])
        ports = {x['tag']:x['attributes'].get('V') for x in triggers[0]['sourceTree']['children']}
        passive_priority = int(ports['Priority'])
        if passive_token!=2 or ports['OwnerLocation']!='7': raise RuntimeError('Unsupported passive filter')
    if id == 200295:
        death_damage = vars['Damage']
        filters = [n for a in graphs for n in a['nodes'] if n['type'] == 'GetCardsNode']
        if len(filters)!=1: raise RuntimeError('Rotfiend filter changed')
        ports = {x['tag']:x['attributes'].get('V') for x in filters[0]['sourceTree']['children']}
        death_ignore = int(ports['Ignore'])
        if death_ignore!=8: raise RuntimeError('Unsupported deathwish target filter')
    consume_maximum, spawn_template, spawn_count = 0, 0, 0
    if id == 132107:
        consume_maximum = vars['Power']
        requests = [n for a in graphs for n in a['nodes'] if n['type'] == 'RequestCardTargetsNode']
        if len(requests)!=1: raise RuntimeError('Kayran request changed')
        ports = {x['tag']:x['attributes'].get('V') for x in requests[0]['sourceTree']['children']}
        target_minimum = int(ports['MinTargets'])
        if consume_maximum != 7 or target_minimum != 0 or ports['MaxTargets'] != '1': raise RuntimeError('Kayran limits changed')
    if id == 132213:
        definitions = [v for a in graphs for g in a['sourceTree']['children']
            if g['tag'] in ('TemporaryVariables','PersistentVariables')
            for v in g['children'] if v['attributes'].get('Name') == 'CardDef']
        if len(definitions)!=1: raise RuntimeError('Dao spawn definition changed')
        spawn_template = int(definitions[0]['children'][0]['attributes']['TemplateId'])
        spawn_count = vars['Counter']
        if spawn_template != 132405 or spawn_count != 2: raise RuntimeError('Dao spawn changed')
    consume_boost, consume_locations, consume_priority, summon_template = 0, 0, 0, 0
    consume_location, consume_tiers, consume_events = 0, 0, 0
    if id == 132305:
        consume_boost = vars['Boost']
        triggers = [n for a in graphs for n in a['nodes'] if n['type'] in ('AfterDestroyedTrigger','AfterBanishedTrigger')]
        if len(triggers)!=2: raise RuntimeError('Nekker consume triggers changed')
        consume_events = sum(1 if node['type']=='AfterDestroyedTrigger' else 2 for node in triggers)
        for node in triggers:
            ports = {p['tag']:p['attributes'].get('V') for p in node['sourceTree']['children']}
            if ports['OwnerLocation']!='31' or ports['RemovalType']!='1' or ports['Priority']!='0' or ports['IsAmbushing']!='False': raise RuntimeError('Nekker trigger filter changed')
        consume_locations = int(ports['OwnerLocation']); consume_priority = int(ports['Priority'])
        definitions = [v for a in graphs for g in a['sourceTree']['children'] if g['tag']=='TemporaryVariables'
            for v in g['children'] if v['attributes'].get('Name')=='Nekker']
        if len(definitions)!=1: raise RuntimeError('Nekker summon changed')
        summon_template = int(definitions[0]['children'][0]['attributes']['TemplateId'])
        if summon_template != 132305 or consume_boost != 1: raise RuntimeError('Nekker values changed')
    if id == 132306:
        queries = [n for a in graphs for n in a['nodes'] if n['type']=='GetCardsNode']
        requests = [n for a in graphs for n in a['nodes'] if n['type']=='RequestCardChoiceNode']
        if len(queries)!=1 or len(requests)!=1: raise RuntimeError('Ghoul query/request changed')
        ports = {x['tag']:x['attributes'].get('V') for x in queries[0]['sourceTree']['children']}
        consume_location = int(ports['LocationId']); consume_tiers = int(ports['CardTiers'])
        if consume_location!=32 or consume_tiers!=6 or ports['CardTypes']!='4' or ports['Ignore']!='0': raise RuntimeError('Ghoul eligibility changed')
        ports = {x['tag']:x['attributes'].get('V') for x in requests[0]['sourceTree']['children']}
        target_minimum = int(ports['MinChoices']); target_side = 1
        if target_minimum!=0 or ports['MaxChoices']!='1' or vars['MaxTargets']!=1 or ports['RevealChoices']!='False': raise RuntimeError('Ghoul choice limits changed')
        # GetOwnerPlayerId40 -> GetCards32.PlayerId, not literal both-side default3.
        if not any(x.get('sourcePort',{}).get('nodeId')==40 and x.get('destinationPort',{}).get('nodeId')==32
            and x.get('destinationPort',{}).get('field')=='PlayerId' for a in graphs for x in a['connections']): raise RuntimeError('Ghoul owner filter changed')
    target_ignore, lock_tokens, lock_operation, multiplier = 264, 0, 0, 0
    if effect in (18,19):
        nodes = [n for a in graphs for n in a['nodes']]
        def only_ports(kind):
            found = [n for n in nodes if n['type']==kind]
            if len(found)!=1: raise RuntimeError('Lock graph changed: '+kind)
            return {p['tag']:p['attributes'].get('V') for p in found[0]['sourceTree']['children']}
        query = only_ports('GetCardsNode'); request = only_ports('RequestCardTargetsNode')
        token = only_ports('ChangeTokensNode'); power = only_ports('ChangePowerNode')
        target_ignore = int(query['Ignore']); target_minimum = int(request['MinTargets'])
        lock_tokens = int(token['Tokens']); lock_operation = int(token['Operation'])
        if query['PlayerId']!='3' or query['LocationId']!='7' or query['CardTypes']!='4' or query['CardTiers']!='15' or target_ignore!=256:
            raise RuntimeError('Lock target eligibility changed')
        if request['MaxTargets']!='1' or lock_tokens!=4 or lock_operation!=3 or power['TargetedPower']!='0':
            raise RuntimeError('Lock operation changed')
        if id==132205:
            multiplier = vars['Halve']
            if multiplier!=50 or target_minimum!=0 or power['Operation']!='3' or power['IgnoreArmor']!='True': raise RuntimeError('Morvudd changed')
        else:
            amount = vars['Damage']
            if amount!=4 or target_minimum!=1 or power['Operation']!='1' or power['IgnoreArmor']!='False': raise RuntimeError('Shackles changed')
    target_types, target_tiers, transform_template, transform_reset = 4, 15, 0, 0
    if effect == 20:
        nodes = [n for a in graphs for n in a['nodes']]
        def transform_ports(kind):
            found = [n for n in nodes if n['type']==kind]
            if len(found)!=1: raise RuntimeError('Transform graph changed: '+kind)
            return {p['tag']:p['attributes'].get('V') for p in found[0]['sourceTree']['children']}
        query=transform_ports('GetCardsNode'); request=transform_ports('RequestCardTargetsNode'); node=transform_ports('TransformCardsNode')
        definitions = [v for a in graphs for group in a['sourceTree']['children'] if group['tag']=='TemporaryVariables'
            for v in group['children'] if v['attributes'].get('Name')=='CardDef']
        if len(definitions)!=1: raise RuntimeError('Compression definition changed')
        transform_template=int(definitions[0]['children'][0]['attributes']['TemplateId'])
        transform_reset=int(node['ResetMode']);target_types=int(query['CardTypes']);target_tiers=int(query['CardTiers'])
        target_ignore=int(query['Ignore']);target_minimum=int(request['MinTargets'])
        if transform_template!=200307 or transform_reset!=255 or target_types!=12 or target_tiers!=6 or target_ignore!=264:
            raise RuntimeError('Compression target/reset changed')
        if query['PlayerId']!='3' or query['LocationId']!='7' or target_minimum!=1 or request['MaxTargets']!='1':
            raise RuntimeError('Compression request changed')
        figurine=cards[transform_template]
        if figurine['fields']['Power']!=2 or figurine['fields']['Tokens']!=512 or figurine['fields']['Tier']!=4:
            raise RuntimeError('Figurine template changed')
    deploy_template, deploy_count, spawn_mode, before_attacker_boost, banished_attacker_boost = 0,0,0,0,0
    if id in (132217,132316):
        nodes=[n for a in graphs for n in a['nodes']]
        def harpy_ports(kind):
            found=[n for n in nodes if n['type']==kind]
            if len(found)!=1: raise RuntimeError('Harpy graph changed: '+kind)
            return {p['tag']:p['attributes'].get('V') for p in found[0]['sourceTree']['children']}
        edges={(x['sourcePort']['nodeId'],x['sourcePort']['field'],x['destinationPort']['nodeId'],x['destinationPort']['field'])
            for a in graphs for x in a['connections']}
        spawn=next(n for n in nodes if n['type']=='SpawnCardNode')
        template_port=next(p for p in spawn['sourceTree']['children'] if p['tag']=='Definition')
        template=int(template_port['children'][0]['attributes']['TemplateId'])
        sp=harpy_ports('SpawnCardNode')
        if sp['SpawnType']!='3' or sp['SpawnLocation']!='0': raise RuntimeError('Harpy spawn mode changed')
        if id==132217:
            deploy_template,deploy_count=template,vars['Counter']
            if deploy_template!=132316 or deploy_count!=2 or not {(157,'DV',82,'Position'),(186,'Out',82,'Count'),(1,'FlowOut',82,'FlowIn')} <= edges:
                raise RuntimeError('Celeano deploy changed')
        else:
            spawn_template,spawn_count,spawn_mode=template,int(sp['Count']),1
            before_attacker_boost=banished_attacker_boost=vars['Boost']
            before=harpy_ports('BeforeDestroyedTrigger');after=harpy_ports('AfterBanishedTrigger');turn=harpy_ports('BeforeTurnEndTrigger')
            power=harpy_ports('ChangePowerNode')
            if (spawn_template,spawn_count,before_attacker_boost)!=(200308,1,4): raise RuntimeError('Harpy Egg values changed')
            if before['OwnerLocation']!='63' or after['OwnerLocation']!='512' or turn['OwnerLocation']!='7': raise RuntimeError('Egg locations changed')
            if any(t['RemovalType']!='1' or t['Priority']!='0' or t['IsAmbushing']!='False' for t in (before,after)): raise RuntimeError('Egg trigger changed')
            if power['Operation']!='0' or power['TargetedPower']!='0' or power['IgnoreArmor']!='False': raise RuntimeError('Egg boost changed')
            if not {(352,'Out',25,'Position'),(21,'FlowOut',25,'FlowIn'),(415,'FlowOutTrue',374,'FlowIn'),(374,'FlowOut',330,'FlowIn'),(493,'FlowOutTrue',330,'FlowIn'),(299,'DV',330,'Targets'),(423,'FlowOut',434,'FlowIn')} <= edges:
                raise RuntimeError('Egg source wiring changed')
    if id==132313:
        nodes=[n for a in graphs for n in a['nodes']]
        def drain_port(nid):
            n=next(n for n in nodes if n['nodeId']==nid)
            return {p['tag']:p['attributes'].get('V') for p in n['sourceTree']['children']}
        query,request,damage,boost,compare=map(drain_port,(17,40,232,327,370))
        edges={(x['sourcePort']['nodeId'],x['sourcePort']['field'],x['destinationPort']['nodeId'],x['destinationPort']['field'])
            for a in graphs for x in a['connections']}
        target_minimum=int(request['MinTargets']);target_ignore=int(query['Ignore'])
        if amount!=3 or target_minimum!=0 or request['MaxTargets']!='1': raise RuntimeError('Ekimmara amount/request changed')
        if query['PlayerId']!='3' or query['LocationId']!='7' or query['CardTypes']!='4' or query['CardTiers']!='15' or target_ignore!=264:
            raise RuntimeError('Ekimmara targets changed')
        if damage['Operation']!='1' or damage['IgnoreArmor']!='True' or damage['TargetedPower']!='0' or damage['ElementType']!='1024' or damage['AttackMethod']!='1':
            raise RuntimeError('Ekimmara damage changed')
        if boost['Operation']!='0' or boost['IgnoreArmor']!='False' or boost['TargetedPower']!='0' or compare['Op']!='3' or compare['B']!='3':
            raise RuntimeError('Ekimmara boost/cap changed')
        if not {(287,'DV',370,'A'),(376,'FlowOutTrue',383,'FlowIn'),(376,'FlowOutFalse',388,'FlowIn'),(396,'Out',383,'In'),(287,'DV',388,'In'),(402,'Out',232,'Power'),(361,'Out',327,'Power'),(232,'FlowOut',327,'FlowIn')} <= edges:
            raise RuntimeError('Ekimmara cached drain changed')
    timer_period,timer_priority=0,0
    if id==132308:
        nodes=[n for a in graphs for n in a['nodes']]
        def vran_ports(nid):
            n=next(n for n in nodes if n['nodeId']==nid)
            return {p['tag']:p['attributes'].get('V') for p in n['sourceTree']['children']}
        before,remove,reset,destroy,power=vran_ports(34),vran_ports(330),vran_ports(356),vran_ports(7),vran_ports(91)
        timer_period=vars['Counter'];timer_priority=int(before['Priority'])
        shape=next(n for n in nodes if n['nodeId']==241)
        shape=next(p for p in shape['sourceTree']['children'] if p['tag']=='Shape')['children'][0]['attributes']
        edges={(x['sourcePort']['nodeId'],x['sourcePort']['field'],x['destinationPort']['nodeId'],x['destinationPort']['field'])
            for a in graphs for x in a['connections']}
        if f['InitialTimer']!=2 or timer_period!=2 or timer_priority!=0: raise RuntimeError('Vran timer changed')
        if before['OwnerLocation']!='7' or before['IsAmbushing']!='False' or remove['Operation']!='0' or remove['Value']!='1' or reset['Operation']!='2': raise RuntimeError('Vran timer graph changed')
        if shape['Mask']!='32768' or shape['PivotX']!='4' or shape['PivotY']!='1' or shape['ApplyToBothSides']!='False': raise RuntimeError('Vran right shape changed')
        if destroy['RemovalType']!='1' or power['Operation']!='0' or power['TargetedPower']!='0' or power['IgnoreArmor']!='False': raise RuntimeError('Vran consume changed')
        if not {(1,'FlowOut',356,'FlowIn'),(343,'FlowOut',356,'FlowIn'),(356,'FlowOut',232,'FlowIn'),(34,'FlowOut',330,'FlowIn'),(42,'Out',34,'PlayerIdFilter'),(102,'DV',160,'In'),(160,'FlowOut',7,'FlowIn'),(7,'FlowOut',91,'FlowIn'),(176,'Out',91,'Power')} <= edges: raise RuntimeError('Vran wiring changed')
    if id in units:
        spec=units[id]; assert len(graphs)==1
        graph=graphs[0]; nodes=graph['nodes']
        def one(kind):
            matches=[n for n in nodes if n['type']==kind]
            if len(matches)!=1:raise RuntimeError('Unit graph shape changed')
            return matches[0]
        query=one('GetCardsNode');request=one('RequestCardTargetsNode');change=one('ChangePowerNode')
        q={p['tag']:p['attributes'].get('V') for p in query['sourceTree']['children']}
        target_types,target_tiers,target_ignore=int(q['CardTypes']),int(q['CardTiers']),int(q['Ignore'])
        assert q['LocationId']=='7'
        target_minimum=original_int_port(graph,request,'MinTargets')
        assert original_int_port(graph,request,'MaxTargets')==1
        target_side=spec['side'];amount=original_int_port(graph,change,'Power')
        p={v['tag']:v['attributes'].get('V') for v in change['sourceTree']['children']}
        assert (int(p['Operation']),int(p['TargetedPower']))=={1:(1,0),2:(0,0),31:(1,1),32:(3,0)}[effect]
        if effect==32:multiplier=amount
    categories=int(t['categoryWords'][0]['decimal'])
    unit_traits=(1 if categories & 2147483648 else 0)+(2 if categories & 549755813888 else 0)+(4 if categories & 2199023255552 else 0)+(8 if categories & 1136895090229248 else 0)+(16 if categories & 1125899906842624 else 0)+(32 if categories & 4096 else 0)+(64 if categories & 4294967296 else 0)+(128 if categories & 33554432 else 0)+(256 if categories & 65536 else 0)
    unit_traits += (512 if categories & 64 else 0)+(1024 if categories & 128 else 0)+(2048 if categories & 262144 else 0)+(4096 if categories & 1024 else 0)+(16384 if categories & 9007199254740992 else 0)+(32768 if any(n['type']=='KilledTrigger' for a in graphs for n in a['nodes']) else 0)
    pile_location,pile_pick,pile_limit,pile_shuffle,pile_traits=0,0,0,0,0
    target_excluded_traits=0
    special_mode,special_request,special_count,special_radius,special_token,special_rows=0,0,0,0,0,7
    if id in specials:
        spec=specials[id]
        special_mode,special_request=spec['mode'],spec['request']
        special_count,special_radius,special_token,special_rows=spec.get('count',0),spec.get('radius',0),spec.get('token',0),spec.get('rowMask',7)
        amount=vars.get('Damage',vars.get('Boost',0))
        target_side=spec.get('side',0)
        play_template=spec.get('playTemplateId',play_template)
        deploy_template,deploy_count=spec.get('spawnTemplate',deploy_template),spec.get('spawnCount',deploy_count)
        consume_maximum=spec.get('maxPower',consume_maximum)
        target_excluded_traits=spec.get('excludedTraits',0)
        nodes=[n for a in graphs for n in a['nodes']]
        queries=[n for n in nodes if n['type']=='GetCardsNode']
        if queries:
            q={x['tag']:x['attributes'].get('V') for x in queries[0]['sourceTree']['children']}
            target_types,target_tiers,target_ignore=int(q['CardTypes']),int(q['CardTiers']),int(q['Ignore'])
        else: target_types,target_tiers,target_ignore=4,15,8
        if id==200225:target_types,target_tiers,target_ignore=4,6,264
        if id==201753:deploy_count=vars['Counter']; assert deploy_count==3
        if effect==29:
            if len(queries)!=1:raise RuntimeError('Pile query graph changed')
            pile_location=int(q['LocationId']); assert pile_location==spec['pileLocation'] and q['PlayerId']=='3'
            pile_pick,pile_limit,pile_shuffle,pile_traits=spec['pilePickMode'],spec['pileCandidateLimit'],spec['pileShuffle'],spec['pileTraitMask']
            choices=[n for n in nodes if n['type']=='RequestCardChoiceNode']
            if choices:
                choice={x['tag']:x['attributes'].get('V') for x in choices[0]['sourceTree']['children']}
                target_minimum=original_int_port(graphs[0],choices[0],'MinChoices'); assert original_int_port(graphs[0],choices[0],'MaxChoices')==1
            else:target_minimum=1
            amount=vars.get('Boost',0)
        requests=[n for n in nodes if n['type'] in ('RequestCardTargetsNode','RequestLocationTargetsNode')]
        if requests:
            q={x['tag']:x['attributes'].get('V') for x in requests[0]['sourceTree']['children']}
            target_minimum=original_int_port(graphs[0],requests[0],'MinTargets')
        if special_request==1 and not requests:raise RuntimeError('Target special missing source request')
        if special_request==2 and not requests:raise RuntimeError('Row special missing source request')
        if id==113315: amount=vars['Power']; assert amount==10
        if id==200224: target_types,target_tiers,target_ignore=4,15,8
        if special_mode==9: multiplier=vars['Halve']; assert multiplier==50
        if id==113207: assert amount==3 and vars['Counter']==5
        if id==113306: assert amount==13
        if id==201749: assert amount==1 and vars['MaxTargets']==2
    armor = vars.get('Armor',0) if effect == 3 else 0
    title = c['localization']['ru_ru'][f'{id}_name']
    desc = c['localization']['ru_ru'].get(f'{id}_tooltip','')
    for name, number in vars.items(): desc = desc.replace('{' + name + '}', str(number))
    desc = localized_plain_text(desc)
    lines += [f'    case {id}:', f'        value.header.templateId = {id};',
        f'        value.header.typeMask = {f["Type"]}; value.header.tierMask = {f["Tier"]}; value.header.factionMask = {f["FactionId"]};',
        f'        value.header.power = {f["Power"]}; value.header.armor = {f["Armor"]};',
        f'        value.title = {quoted(title)}; value.description = {quoted(desc)};',
        f'        value.pileLocation = {pile_location}; value.pilePickMode = {pile_pick}; value.pileCandidateLimit = {pile_limit}; value.pileShuffle = {pile_shuffle}; value.pileTraitMask = {pile_traits};',
        f'        value.unitTraits = {unit_traits}; value.targetExcludedTraits = {target_excluded_traits};',
        f'        value.specialMode = {special_mode}; value.specialRequest = {special_request}; value.specialCount = {special_count}; value.specialRadius = {special_radius}; value.specialToken = {special_token}; value.specialRowMask = {special_rows};',
        f'        value.effect = {effect}; value.amount = {amount}; value.addedArmor = {armor}; value.tokens = {f["Tokens"]};',
        f'        value.conditionalDamage = {conditional_damage}; value.targetExcludedFaction = {target_excluded_faction};',
        f'        value.weatherToken = {weather_token}; value.targetMinimum = {target_minimum}; value.targetSide = {target_side}; value.playTemplateId = {play_template};',
        f'        value.passiveBoost = {passive_boost}; value.passiveWeatherToken = {passive_token}; value.passivePriority = {passive_priority};',
        f'        value.deathwishDamage = {death_damage}; value.deathwishIgnore = {death_ignore};', f'        value.consumeMaximum = {consume_maximum}; value.deathwishSpawnTemplate = {spawn_template}; value.deathwishSpawnCount = {spawn_count};', f'        value.consumePassiveBoost = {consume_boost}; value.consumePassiveLocations = {consume_locations}; value.consumePassivePriority = {consume_priority}; value.deathwishSummonTemplate = {summon_template};', f'        value.consumeLocation = {consume_location}; value.consumeTierMask = {consume_tiers}; value.consumePassiveEvents = {consume_events};', f'        value.targetIgnore = {target_ignore}; value.lockTokens = {lock_tokens}; value.lockOperation = {lock_operation}; value.powerMultiplier = {multiplier};', f'        value.targetTypes = {target_types}; value.targetTiers = {target_tiers}; value.transformTemplate = {transform_template}; value.transformResetMode = {transform_reset};', f'        value.deploySpawnTemplate = {deploy_template}; value.deploySpawnCount = {deploy_count}; value.deathwishSpawnMode = {spawn_mode}; value.beforeConsumeAttackerBoost = {before_attacker_boost}; value.banishedConsumeAttackerBoost = {banished_attacker_boost};', f'        value.initialTimer = {f["InitialTimer"]}; value.timerPeriod = {timer_period}; value.timerPriority = {timer_priority}; value.conditionalBoost = {conditional_boost}; value.conditionalWeatherToken = {conditional_weather}; value.deploySummonTemplate = {deploy_summon}; value.deploySummonOtherTemplate = {summon_other}; value.deploySummonIgnore = {summon_ignore}; value.deploySummonLinked = {summon_linked};', '        break;']
    records.append(dict(templateId=id, fields=f, placement=t['placement'], title=title, description=desc,
        pileLocation=pile_location,pilePickMode=pile_pick,pileCandidateLimit=pile_limit,pileShuffle=pile_shuffle,pileTraitMask=pile_traits,unitTraits=unit_traits,targetExcludedTraits=target_excluded_traits, specialMode=special_mode,specialRequest=special_request,specialCount=special_count,specialRadius=special_radius,specialToken=special_token,specialRowMask=special_rows, effect=effect, amount=amount, addedArmor=armor, conditionalDamage=conditional_damage, targetExcludedFaction=target_excluded_faction, weatherToken=weather_token, targetMinimum=target_minimum, targetSide=target_side, playTemplateId=play_template, passiveBoost=passive_boost, passiveWeatherToken=passive_token, passivePriority=passive_priority, deathwishDamage=death_damage, deathwishIgnore=death_ignore, consumeMaximum=consume_maximum, deathwishSpawnTemplate=spawn_template, deathwishSpawnCount=spawn_count, consumePassiveBoost=consume_boost, consumePassiveLocations=consume_locations, consumePassivePriority=consume_priority, deathwishSummonTemplate=summon_template, consumeLocation=consume_location, consumeTierMask=consume_tiers, consumePassiveEvents=consume_events, targetIgnore=target_ignore, lockTokens=lock_tokens, lockOperation=lock_operation, powerMultiplier=multiplier, targetTypes=target_types, targetTiers=target_tiers, transformTemplate=transform_template, transformResetMode=transform_reset, deploySpawnTemplate=deploy_template, deploySpawnCount=deploy_count, deathwishSpawnMode=spawn_mode, beforeConsumeAttackerBoost=before_attacker_boost, banishedConsumeAttackerBoost=banished_attacker_boost, initialTimer=f["InitialTimer"],timerPeriod=timer_period,timerPriority=timer_priority,conditionalBoost=conditional_boost,conditionalWeatherToken=conditional_weather,deploySummonTemplate=deploy_summon, deploySummonOtherTemplate=summon_other, deploySummonIgnore=summon_ignore, deploySummonLinked=summon_linked, originalVariables=vars,
        abilityRecordKeys=[a['recordKey'] for a in graphs]))
    if id in monsters or id in northern or id in nilfgaard or id in scoiatael or id in skellige or id in neutral:
        recipe=(neutral if id in neutral else skellige if id in skellige else scoiatael if id in scoiatael else nilfgaard if id in nilfgaard else monsters if id in monsters else northern)[id]
        overlay={k:(vars[v] if isinstance(v,str) else v) for k,v in recipe['fields'].items()}
        lines[-1:-1]=[f'        value.{k} = {v};' for k,v in overlay.items()]
        records[-1].update(overlay)
# REDkit's parser exhausts its statement stack on a large generated switch.
# Keep complete definitions in small functions; the public lookup stays unchanged.
function_index = lines.index('function BetaGwentDuelDefinition(id : int) : SBetaGwentDuelDefinition')
case_lines = lines[function_index + 5:]
case_starts = [i for i, line in enumerate(case_lines) if line.startswith('    case ')]
blocks = [case_lines[start:end] for start, end in zip(case_starts, case_starts[1:] + [len(case_lines)])]
groups = [blocks[i:i + 4] for i in range(0, len(blocks), 4)]
lines = lines[:function_index] + [
    'function BetaGwentDuelDefinition(id : int) : SBetaGwentDuelDefinition', '{',
    '    var value : SBetaGwentDuelDefinition;']
group_for_id = {int(re.search(r'case (\d+):', block[0])[1]): ordinal
                for ordinal, group in enumerate(groups) for block in group}
lookup_ids = sorted(group_for_id)
lookup_groups = [lookup_ids[i:i + 64] for i in range(0, len(lookup_ids), 64)]
for ordinal, ids in enumerate(lookup_groups):
    lines.append(f'    if (id >= {ids[0]} && id <= {ids[-1]}) return BetaGwentDuelDefinitionLookup{ordinal}(id);')
lines += ['    return value;', '}', '']
for ordinal, ids in enumerate(lookup_groups):
    lines += [f'function BetaGwentDuelDefinitionLookup{ordinal}(id : int) : SBetaGwentDuelDefinition', '{',
              '    var value : SBetaGwentDuelDefinition;', '    switch (id)', '    {']
    lines += [f'    case {id}: return BetaGwentDuelDefinitionGroup{group_for_id[id]}(id);' for id in ids]
    lines += ['    }', '    return value;', '}', '']
for ordinal, group in enumerate(groups):
    lines += [f'function BetaGwentDuelDefinitionGroup{ordinal}(id : int) : SBetaGwentDuelDefinition', '{',
        '    var value : SBetaGwentDuelDefinition;', '    switch (id)', '    {']
    for block in group: lines += block
    lines += ['    }', '    return value;', '}', '']
lines += ['// Legacy fixture retains preset1; live menu selects both sides explicitly.',
    'function BetaGwentDuelDeck(out ids : array<int>)', '{', '    BetaGwentDuelPresetDeck(1, ids);', '}', '',
    'struct SBetaGwentDuelPreset', '{', '    var id, leaderTemplateId, unitCount, specialCount, goldCount, silverCount : int;',
    '    var title, description : string;', '}',
    f'function BetaGwentDuelPresetCount() : int {{ return {len(presets)}; }}', '',
    'function BetaGwentDuelPreset(id : int) : SBetaGwentDuelPreset', '{', '    var value : SBetaGwentDuelPreset;']
preset_groups=[presets[i:i+12] for i in range(0,len(presets),12)]
for index,group in enumerate(preset_groups):
    lines += [f'    if(id >= {group[0]["id"]} && id <= {group[-1]["id"]})return BetaGwentDuelPresetDetails{index}(id);']
lines += ['    return value;','}','']
for index,group in enumerate(preset_groups):
    lines += [f'function BetaGwentDuelPresetDetails{index}(id : int) : SBetaGwentDuelPreset','{','    var value : SBetaGwentDuelPreset;','    switch(id) {']
    for preset in group:
        lines += [f'    case {preset["id"]}:', f'        value.id = {preset["id"]}; value.leaderTemplateId = {preset["leader"]};',
            f'        value.title = {quoted(preset["title"])}; value.description = {quoted(preset["description"])};',
            f'        value.unitCount = {preset["unitCount"]}; value.specialCount = {preset["specialCount"]};',
            f'        value.goldCount = {preset["goldCount"]}; value.silverCount = {preset["silverCount"]};', '        break;']
    lines += ['    }','    return value;','}','']
lines += [
    'function BetaGwentDuelPresetDeck(id : int, out ids : array<int>) : bool', '{', '    ids.Clear();']
for preset in presets:
    lines += [f'    if(id == {preset["id"]}) {{ BetaGwentDuelPresetCards{preset["id"]}(ids); return true; }}']
lines += ['    return false;', '}', '']
for preset in presets:
    lines += [f'function BetaGwentDuelPresetCards{preset["id"]}(out ids : array<int>)', '{']
    lines += [f'    ids.PushBack({id});' for id in preset['templateIds']]+['}', '']
leader_ids=sorted(id for id in effects if cards[id]['fields']['Tier']==1 and cards[id]['attributes']['Availability']=='1')
lines += [
    'function BetaGwentDuelIsLeader(id : int) : bool { return '+ ' || '.join(f'id == {id}' for id in leader_ids)+'; }',
    'function BetaGwentDuelLeaders(out ids : array<int>) { ids.Clear(); '+ ' '.join(f'ids.PushBack({id});' for id in leader_ids)+' }']
collectible_ids = sorted(id for id in effects if cards[id]['fields']['Kind'] == 1
    and cards[id]['fields']['Tier'] in (2,4,8) and int(cards[id]['attributes']['Availability']) == 1)
lines += ['', 'function BetaGwentCollectionTotal(faction : int) : int', '{', '    switch(faction) {',f'    case 0: return {len(collectible_ids)+len(leader_ids)};']
for faction in (1,2,4,8,16,32):
    lines.append(f'    case {faction}: return {sum(cards[i]["fields"]["FactionId"]==faction for i in collectible_ids+leader_ids)};')
lines += ['    default: return 0;','    }','}']
lines += ['', 'function BetaGwentDuelCollection(out ids : array<int>)', '{', '    ids.Clear();']
lines += [f'    ids.PushBack({id});' for id in collectible_ids]
lines += ['}', '', 'function BetaGwentDuelCollectible(id : int) : bool', '{', '    switch(id)', '    {']
lines += [f'    case {id}: return true;' for id in collectible_ids]
lines += ['    }','    return false;','}']
lines += ['', 'function BetaGwentDuelResetInInactive(id : int) : bool', '{', '    switch (id)', '    {']
lines += [f'    case {id}: return true;' for id in effects if cards[id]['resetInInactive']]
lines += ['    }', '    return false;', '}']
source = ROOT / 'BetaGwent/development/scripts/game/betagwent/duelCatalog.ws'
killed_ability_ids = sorted({g['templateId'] for g in c['abilities'] if g['type']=='CardAbility' and any(n['type']=='KilledTrigger' for n in g['nodes'])})
lines += ['', 'function BetaGwentDuelHasKilledAbility(id : int) : bool', '{', '    return ' + ' || '.join(f'id=={id}' for id in killed_ability_ids) + ';', '}']
lines += render_modes(c,modes)
lines += render_rows(c)
lines += render_monsters(c,monsters,effects)
lines += render_north(c,northern,effects,ROOT)
lines += render_nilf(c,nilfgaard,effects,ROOT)
lines += render_scoia(c,scoiatael,effects,ROOT)
lines += render_skellige(c,skellige,effects,ROOT)
lines += render_neutral(c,neutral,effects,ROOT)
spy_ids=[id for id in effects if cards[id]['fields']['Type']==4 and int(cards[id]['placement'].get('OpponentSide',0))!=0 and int(cards[id]['placement'].get('PlayerSide',0))==0]
lines += ['', 'function BetaGwentDuelSpying(id : int) : bool { return '+' || '.join(f'id == {id}' for id in spy_ids)+'; }']
play_choice_ids=sorted({g['templateId'] for g in c['abilities'] if g['type']=='CardAbility'
    and any(n['type']=='PlayCardsNode' for n in g['nodes'])
    and any(n['type']=='RequestCardChoiceNode' for n in g['nodes'])})
lines+=['', 'function BetaGwentDuelPlayChoice(id : int) : bool', '{', '    switch (id)', '    {']
lines+=[f'    case {id}: return true;' for id in play_choice_ids]
lines+=['    }', '    return false;', '}']
lines=bounded_helpers(lines)
source.write_text('\n'.join(lines) + '\n',encoding='utf-8-sig')
out = ROOT / 'data/beta924/duel'; out.mkdir(exist_ok=True)
(out / 'slice.json').write_text(json.dumps(dict(catalogSha256=hashlib.sha256(raw).hexdigest(), cards=records,
    decks=[dict(player=side, faction=2, leader=200055, templateIds=deck) for side in (1,2)],
    presets=presets, presetsSourceSha256=hashlib.sha256(presets_raw).hexdigest(),
    selectablePresetCount=len(presets), leaderIds=leader_ids, collectibleIds=collectible_ids,
    deckBuilderRules=dict(minimum=25,maximum=40,goldMaximum=4,silverMaximum=6,bronzeCopies=3,otherCopies=1,savedSlots=8),
    legacyFixturePreset=1, presetListsAreHistoricalDecks=False,
    deckSizeAndCopyLimitsChecked=True, runtimeVerified=False,
    scope=f'Closed DEV duel with{len(records)} definitions; concrete special-card routing from specials.json. Remaining specials are inventoried separately, never counted as implemented. ' +'Imlerith Frost-conditioned damage4/8 and Adda damage8 against non-Monsters, three Crones with paired deck summon, original ignore masks and linked-card reverse candidate order; Wild Hunt Warrior damage3/boost2 after killed or Frost target, Arachas Drone summon own deck copies beside source without Played or extra RNG, seeded shuffle/mulligan, weather and First Light choices, nested Rally/Hound play, concrete Ancient Foglet AfterTurn, Rotfiend and Dao Killed consumers, Kayran Consume and Lesser Dao spawn/Void cleanup, Nekker active/hand/deck AfterDestroyed/AfterBanished consume boosts and Killed summon from deck without deploy; Ghoul optional own Bronze/Silver grave choice, Consume banish and cached-current-power boost; Morvudd and Shackles queued lock toggle, enemy-only multiply50/damage4, native lock badge; Compression transforms Bronze/Silver active targets into same-ID Jade Figurine2/Doomed with All reset and no Killed. Clear Skies/Rally are choice-only templates. Concrete local managed-action coordinator with nested passive FIFOs. Celeano deploys two Eggs on its left; Egg boosts the Consume attacker before destruction, and after Consume banish, and Killed spawns a Hatchling in a random available own row. Ekimmara optional active-unit Drain caches min(current,3), ignores armor, then boosts owner by the same amount; does not emit Consume. Vran timer2 resets on Played and TimerTriggered, removes1 before own turn, and consumes the immediate right ally with cached power. Full controller, arbitrary graphs, original RNG parity and runtime verification of additions pending.'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Duel table:{len(records)} canonical definitions,{len(presets)} legal25..40-card faction presets,{len(leader_ids)} selectable leaders; runtime pending.')
