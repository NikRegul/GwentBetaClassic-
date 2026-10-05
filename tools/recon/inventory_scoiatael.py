"""Freeze strict Beta Scoiatael consumers and their complete creation pools.

Source coverage is distinct from human gameplay acceptance and scheduler parity.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from duel_scoia import load_scoia, scoia_pools
from duel_nilf import nilf_pools


def main():
    raw = (ROOT / 'data/beta924/normalized/catalog.json').read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != '022539802636cb45e92123a630c3788a0674c39b538fa1f69a64761a6b3ddbd3':
        raise RuntimeError('Canonical catalogue changed')
    catalog = json.loads(raw)
    duel = json.loads((ROOT / 'data/beta924/duel/slice.json').read_text(encoding='utf-8'))
    recipes = load_scoia(ROOT, catalog, digest)
    implemented = {v['templateId']: v for v in duel['cards']}
    collection = [t for t in catalog['templates'] if t['fields']['FactionId'] == 16
                  and t['fields']['Kind'] == 1 and t['fields']['Tier'] in (1, 2, 4, 8)
                  and t['attributes']['Availability'] == '1']
    regular = [t for t in collection if t['fields']['Tier'] != 1]
    leaders = [t for t in collection if t['fields']['Tier'] == 1]
    assert len(regular) == 66 and len(leaders) == 4
    assert all(t['templateId'] in implemented for t in collection)
    collection_ids = {t['templateId'] for t in collection}
    pools = {id: ids for id, ids in nilf_pools(catalog).items() if id in collection_ids}
    pools.update(scoia_pools(catalog))
    assert all(set(ids) <= set(implemented) for ids in pools.values())
    assert 142203 not in pools[201615]
    assert len(recipes) == 14 and set(recipes) <= collection_ids
    for id, recipe in recipes.items():
        assert implemented[id]['effect'] == 34
        assert implemented[id]['specialMode'] == recipe['fields']['specialMode']
    graphs = [g for g in catalog['abilities'] if g['type'] == 'CardAbility'
              and g['templateId'] in collection_ids]
    graph = next(g for g in graphs if g['templateId'] == 201615)
    expected = [201715, 201716]
    assert any([int(x['attributes']['TemplateId']) for x in v['children'][0]['children']] == expected
               for group in graph['sourceTree']['children'] if group['tag'] == 'TemporaryVariables'
               for v in group['children'] if v['attributes']['Type'] == 'CardDefinitionListVar')
    presets = json.loads((ROOT / 'data/beta924/duel/presets.json').read_text(encoding='utf-8'))['presets']
    scoia_presets = [p for p in presets if p['faction'] == 16]
    assert len(scoia_presets) == 3
    report = dict(stage=74, catalogSha256=digest, regularCount=66, leaderCount=4,
        collection=collection, addedRecipes=list(recipes.values()), previouslyImplementedRegularCount=52,
        fullCreationPools=pools, displayOnlyChoices={201615: expected}, graphs=graphs,
        presets=scoia_presets, presetsAreHistorical=False,
        consumers={name: hashlib.sha256((ROOT / 'BetaGwent/development/scripts/game/betagwent' / name).read_bytes()).hexdigest()
                   for name in ('duelScoia.ws', 'duelNilfDependencies.ws', 'duelSession.ws', 'duelMonsters.ws', 'duelMonsterDuel.ws')},
        originalPlayAndDrawIL='docs/evidence/scoia73-play-il.txt',
        runtimeVerified=False, factionInitiativeImplemented=False,
        note='Concrete consumers and full creation pools; human runtime, faction initiative, general original scheduler/priority/RNG parity pending.')
    out = ROOT / 'docs/evidence/scoiatael-current-source.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Scoiatael:66 regular +4 leaders; complete pools', {id: len(ids) for id, ids in pools.items()})


if __name__ == '__main__':
    main()
