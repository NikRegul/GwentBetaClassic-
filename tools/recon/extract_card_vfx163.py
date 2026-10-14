"""Extend the original Beta VFX registry inventory to every template.

No game rules or artwork are inferred from a card name. Graph fields and the
decoded original registry determine the effect; an absent registration stays
explicitly absent. The original 85-special inventory remains immutable.
"""
from pathlib import Path
import collections
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[2]
ELEMENTS = {1:'Physical',16:'Fire',32:'Ice',64:'Lightning',128:'Earth',256:'Air',
            512:'LightMagic',1024:'DarkMagic',2048:'Nature',4096:'Water',
            8192:'Poison',16384:'Blood',32768:'Bubbles'}
FIELDS = ('ElementType','AttackMethod','RemovalType','MovementType','Operation',
          'LocationToken','Tokens','SpawnType')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def build():
    catalog_path = ROOT/'data/beta924/normalized/catalog.json'
    original_path = ROOT/'docs/evidence/special-vfx142.json'
    catalog = json.loads(catalog_path.read_text('utf8'))
    original = json.loads(original_path.read_text('utf8'))
    registry = original['registry']
    assert digest(ROOT/original['source']) == original['sourceSha256']
    abilities = {a['templateId']:a for a in catalog['abilities'] if a['type']=='CardAbility'}
    sound_path = ROOT/'docs/evidence/beta-audio86-vfx-map.json'
    sounds = json.loads(sound_path.read_text('utf8'))
    sounds_by_prefab = collections.defaultdict(list)
    for sound in sounds:
        sounds_by_prefab[sound['object']].append(sound)

    def resolve(table, method, element, template):
        if element <= 0 or element & (element-1):
            return None
        row = next((r for r in registry.get(table,{}).get('rows',[]) if r['method']==method), None)
        if row is None:
            return None
        bit = str(element.bit_length()-1)
        # Overrides have the original template ID as key. Preserve the binding
        # including its component/pathId, rather than guessing a generic name.
        return row['overrides'].get(bit,{}).get(str(template)) or row['effects'].get(bit)

    cards = []
    unresolved = []
    prefabs = set()
    for template in catalog['templates']:
        tid = template['templateId']
        definition = template['fields']
        collectible = (template['attributes'].get('Availability')=='1' and
                       definition['Kind']==1 and definition['Tier'] in (1,2,4,8))
        ability = abilities.get(tid,{})
        effects = []
        for node in ability.get('nodes',[]):
            fields = {child['tag']:child['attributes'].get('V') for child in node['sourceTree']['children']}
            visual = {key:int(fields[key]) for key in FIELDS if fields.get(key) is not None}
            if not visual:
                continue
            element = visual.get('ElementType',1)
            method = visual.get('AttackMethod',0)
            attack = resolve('AttackApplyMethodData',method,element,tid)
            impact = resolve('CardPowerAttackVFXHandlerData',0,element,tid) if node['type']=='ChangePowerNode' else None
            token = registry.get('LocationTokenVFXHandlerData',{}).get('tokenEffects',{}).get(
                str(visual.get('Tokens',visual.get('LocationToken',0)))) if node['type']=='ChangeLocationTokensNode' else None
            bindings = [b for b in (attack,impact,token) if b]
            for binding in bindings:
                prefabs.add(binding['prefab'])
            effect = dict(nodeId=node['nodeId'],node=node['type'],fields=visual,
                          elementName=ELEMENTS.get(element),attack=attack,impact=impact,rowEffect=token,
                          sounds={b['prefab']:sounds_by_prefab[b['prefab']] for b in bindings})
            if node['type']=='ChangePowerNode' and element and not attack and not impact:
                # E.g. direct Ice or side Air: the generic original registry has
                # no such slot. Do not manufacture a similarly named prefab.
                unresolved.append(dict(templateId=tid,nodeId=node['nodeId'],element=element,
                                       method=method,operation=visual.get('Operation')))
            effects.append(effect)
        cards.append(dict(templateId=tid,name=template['attributes']['DebugName'],
                          title=catalog['localization']['ru_ru'].get(str(tid)+'_name'),
                          collectible=collectible,leader=collectible and definition['Tier']==1,
                          special=definition['Type']==2,hasAbility=bool(ability),effects=effects))
    assert len({c['templateId'] for c in cards}) == len(catalog['templates'])
    assert sum(c['collectible'] for c in cards)==479 and sum(c['leader'] for c in cards)==21
    report = dict(stage=163,scope='Every template, including units, leaders and internal definitions',
                  source=original['source'],sourceSha256=original['sourceSha256'],
                  catalogSha256=digest(catalog_path),registrySha256=digest(original_path),
                  soundMapSha256=digest(sound_path),templateCount=len(cards),
                  collectibleCount=479,leaderCount=21,
                  cardsWithPowerEffects=sum(any(e['node']=='ChangePowerNode' for e in c['effects']) for c in cards),
                  cards=cards,prefabs=sorted(prefabs),unregisteredPowerCombinations=unresolved,
                  nativeRuntimeVerified=False,uniquePrefabRenderingComplete=False)
    target = ROOT/'docs/evidence/card-vfx163.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps({key:report[key] for key in ('templateCount','collectibleCount','leaderCount',
                    'cardsWithPowerEffects','uniquePrefabRenderingComplete')},ensure_ascii=False))


if __name__=='__main__':
    build()
