"""Persistent, reviewed deck additions. Original Beta lists are never repaired."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'data/beta924/design'


def imported_presets():
    path = DESIGN / 'beta_deck_import092.json'
    if not path.exists():
        return []
    data = json.loads(path.read_text('utf8'))
    assert data['approvedDistinct'] == 30 and len(data['decks']) == 30
    assert len(data['heldAssets']) == 15
    return [dict(id=100+i, key='beta-original-'+d['asset'], title=d['asset'],
                 description='Подлинный состав Beta 0.9.24.3.432. Исходное имя: '+d['asset']+'.',
                 faction=d['faction'], leader=d['leader'], templateIds=list(d['templateIds']),
                 originalBetaAsset=d['asset'], originalBetaSourcePreset=d['presetId'])
            for i, d in enumerate(data['decks'])]


def apply_npc_decks(document, cards, records):
    path = DESIGN / 'npc_decks092.json'
    if not path.exists():
        return
    config = json.loads(path.read_text('utf8'))
    by_id = {p['id']: p for p in document['presets']}
    by_key = {r['deckName']: r for r in records}
    assert {x['deckName'] for x in config['assignments']} == set(by_key)
    signatures = set()
    for spec in config['assignments']:
        record = by_key[spec['deckName']]
        target, base = by_id[record['preset']], by_id[spec['basePreset']]
        ids = list(base['templateIds'])
        for old, new in spec.get('replacements', []):
            assert old in ids and new not in ids, (spec['deckName'], old, new)
            ids[ids.index(old)] = new
        counts = Counter(ids)
        assert 25 <= len(ids) <= 40
        assert all(cards[i]['fields']['FactionId'] in (1, base['faction']) for i in ids)
        assert all(n <= (3 if cards[i]['fields']['Tier'] == 2 else 1) for i, n in counts.items())
        assert all(cards[i]['attributes']['Availability'] == '1' for i in ids)
        assert sum(cards[i]['fields']['Tier'] == 8 for i in ids) <= 4
        assert sum(cards[i]['fields']['Tier'] == 4 for i in ids) <= 6
        identity = tuple(sorted(ids)), base['leader']
        assert identity not in signatures, 'Named NPC lists must remain distinct: '+spec['deckName']
        signatures.add(identity)
        target.update(leader=base['leader'], faction=base['faction'], templateIds=ids,
                      npcDeck=spec['deckName'], basePreset=base['id'],
                      npcRulesProfile=base['aiRulesProfile'],
                      description=spec['theme'], npcTheme=spec['theme'])
        record.update(basePreset=base['id'], aiRulesProfile=base['aiRulesProfile'],
                      theme=spec['theme'], replacements=spec.get('replacements', []))


def render_helpers(presets):
    lines = ['function BetaGwentOriginalBetaDeckName(id : int) : string {', '    switch(id) {']
    lines += [f'    case {p["id"]}: return {json.dumps(p["originalBetaAsset"], ensure_ascii=False)};'
              for p in presets if p.get('originalBetaAsset')]
    lines += ['    default: return "";', '    }', '}',
              'function BetaGwentAINpcProfile(id : int) : int {', '    switch(id) {']
    lines += [f'    case {p["id"]}: return {p["npcRulesProfile"]};' for p in presets if p.get('npcRulesProfile')]
    lines += ['    default: return 0;', '    }', '}']
    return lines
