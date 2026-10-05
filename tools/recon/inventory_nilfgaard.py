"""Freeze strict 0.9.24 Nilfgaard collection and complete creation dependencies.

Checks source coverage; does not claim human runtime or original scheduler parity.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from duel_nilf import load_nilf, nilf_pools


def main():
    raw = (ROOT / 'data/beta924/normalized/catalog.json').read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != '022539802636cb45e92123a630c3788a0674c39b538fa1f69a64761a6b3ddbd3':
        raise RuntimeError('Canonical catalogue changed')
    catalog = json.loads(raw)
    duel = json.loads((ROOT / 'data/beta924/duel/slice.json').read_text(encoding='utf-8'))
    recipes = load_nilf(ROOT, catalog, digest)
    implemented = {v['templateId']: v for v in duel['cards']}
    collection = [t for t in catalog['templates'] if t['fields']['FactionId'] == 4
                  and t['fields']['Kind'] == 1 and t['fields']['Tier'] in (1, 2, 4, 8)
                  and t['attributes']['Availability'] == '1']
    regular = [t for t in collection if t['fields']['Tier'] != 1]
    leaders = [t for t in collection if t['fields']['Tier'] == 1]
    assert len(regular) == 71 and len(leaders) == 4
    assert all(t['templateId'] in implemented for t in collection)
    pools = nilf_pools(catalog)
    assert all(set(ids) <= set(implemented) for ids in pools.values())
    assert len(pools[201580]) == 20 and 201580 not in pools[201580]
    assert set(duel['leaderIds']) == {t['templateId'] for t in catalog['templates']
        if t['fields']['Kind'] == 1 and t['fields']['Tier'] == 1
        and t['attributes']['Availability'] == '1'}
    for id, recipe in recipes.items():
        assert implemented[id]['effect'] == 34
        assert implemented[id]['specialMode'] == recipe['fields']['specialMode']
    views = {201603: [201694, 201695], 201662: [201713, 201714],
             201653: [201672, 201673]}
    graphs = [g for g in catalog['abilities'] if g['type'] == 'CardAbility'
              and g['templateId'] in ({t['templateId'] for t in collection} | set(recipes))]
    for parent, expected in views.items():
        graph = next(g for g in graphs if g['templateId'] == parent)
        variable = next(v for group in graph['sourceTree']['children']
                        if group['tag'] == 'TemporaryVariables' for v in group['children']
                        if v['attributes']['Type'] == 'CardDefinitionListVar'
                        and [int(x['attributes']['TemplateId']) for x in v['children'][0]['children']] == expected)
        actual = [int(v['attributes']['TemplateId']) for v in variable['children'][0]['children']]
        assert actual == expected, (parent, actual, expected)
    root_ids = {t['templateId'] for t in collection}
    dependencies = sorted(set(recipes) - root_ids)
    report = dict(stage=74, catalogSha256=digest, regularCount=71, leaderCount=4,
        collection=collection, recipes=list(recipes.values()), dependencyIds=dependencies,
        fullCreationPools=pools, displayOnlyChoices=views, graphs=graphs,
        spyMetadata=[dict(templateId=t['templateId'], placement=t['placement'],
                          tokens=t['fields']['Tokens']) for t in collection
                     if t['fields']['Type'] == 4 and int(t['placement']['OpponentSide'])
                     and not int(t['placement']['PlayerSide'])],
        consumers={name: hashlib.sha256((ROOT / 'BetaGwent/development/scripts/game/betagwent' / name).read_bytes()).hexdigest()
                   for name in ('duelNilf.ws', 'duelNilfDependencies.ws', 'duelSession.ws', 'duelLiveCard.ws')},
        runtimeVerified=False,
        note='Concrete consumer and full creation-pool coverage; full original scheduler/RNG parity and human runtime acceptance pending.')
    out = ROOT / 'docs/evidence/nilfgaard-current-source.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Nilfgaard:71 regular +4 leaders; full pools', {id: len(ids) for id, ids in pools.items()})


if __name__ == '__main__':
    main()
