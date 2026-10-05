"""Record complete pinned Monster source coverage without claiming runtime acceptance."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from duel_monsters import monster_pools

raw = (ROOT / 'data/beta924/normalized/catalog.json').read_bytes()
digest = hashlib.sha256(raw).hexdigest()
if digest != '022539802636cb45e92123a630c3788a0674c39b538fa1f69a64761a6b3ddbd3':
    raise RuntimeError('Canonical catalogue changed')
catalog = json.loads(raw)
duel = json.loads((ROOT / 'data/beta924/duel/slice.json').read_text(encoding='utf-8'))
recipes = json.loads((ROOT / 'data/beta924/duel/monsters.json').read_text(encoding='utf-8'))['cards']
implemented = {c['templateId']: c for c in duel['cards']}
collection = [t for t in catalog['templates'] if t['fields']['FactionId'] == 2
    and t['fields']['Kind'] == 1 and t['fields']['Tier'] in (1, 2, 4, 8)
    and t['attributes']['Availability'] == '1']
regular = sum(t['fields']['Tier'] != 1 for t in collection)
leaders = len(collection) - regular
if (regular, leaders) != (74, 5):
    raise RuntimeError('Monster collection eligibility changed')
missing = sorted(t['templateId'] for t in collection if t['templateId'] not in implemented)
if missing:
    raise RuntimeError(f'Missing Monster consumers: {missing}')
ids = {t['templateId'] for t in collection} | {r['templateId'] for r in recipes} | {132403, 200457, 201666, 201667}
assembly = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/Managed/Assembly-CSharp.dll'
assembly_hash = hashlib.sha256(assembly.read_bytes()).hexdigest().upper()
if assembly_hash != '0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F':
    raise RuntimeError('Original assembly changed')
report = dict(catalogSha256=digest, originalAssemblySha256=assembly_hash,
    collectibleCoverage=dict(regular=regular, leaders=leaders, missingTemplateIds=missing),
    creationPools=monster_pools(catalog),
    templates=[t for t in catalog['templates'] if t['templateId'] in ids],
    graphs=[a for a in catalog['abilities'] if a['type'] == 'CardAbility' and a['templateId'] in ids],
    recipes=recipes, runtimeVerified=False,
    scope='All original Monster collection candidates have concrete closed-duel consumers. '
          'Graph coverage, compile and source identity do not establish full runtime/scheduler/RNG parity.')
(ROOT / 'docs/evidence/monsters-current-source.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Monster source coverage: 74 regular cards, 5 leaders; all creation pools retained.')
