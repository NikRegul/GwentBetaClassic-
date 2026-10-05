"""Read-only source audit; writes evidence under docs/evidence, never game data."""
from pathlib import Path
import collections
import csv
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs' / 'evidence'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/data_definitions'
DIY = ROOT / 'LegacyGwent-diy(1)/LegacyGwent-diy/src/Cynthia.Card/src/Cynthia.Card.Common'

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

with zipfile.ZipFile(SOURCE) as archive:
    templates = ET.fromstring(archive.read('Templates.xml'))
    abilities = ET.fromstring(archive.read('Abilities.xml'))
    locales = {}
    for name in archive.namelist():
        if name.startswith('Localization/') and name.endswith('.csv'):
            # csv module handles quoted semicolons and multiline fields.
            rows = list(csv.DictReader(io.StringIO(archive.read(name).decode('utf-8-sig'), newline=''), delimiter=';'))
            locales[name] = {r['Key']: r.get(Path(name).stem, '') for r in rows if r.get('Key')}
    save('beta-archive.json', {
        'path': str(SOURCE), 'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'info': archive.read('Info').decode().strip(),
        'entries': [{'name': n, 'bytes': archive.getinfo(n).file_size, 'sha256': hashlib.sha256(archive.read(n)).hexdigest()} for n in archive.namelist()],
    })

ids = {t.get('Id') for t in templates}
ability_ids = {a.get('Template') for a in abilities if a.get('Type') == 'CardAbility'}
nodes = collections.Counter(n.get('Type') for a in abilities for n in a.findall('Nodes/*'))
name_missing = {name: [t.get('Id') for t in templates if t.get('Id') + '_name' not in rows] for name, rows in locales.items()}
stats = {
    'template_records': len(templates), 'unique_template_ids': len(ids),
    'duplicate_ids': [k for k,v in collections.Counter(t.get('Id') for t in templates).items() if v > 1],
    'template_attribute_counts': {key: dict(collections.Counter(t.get(key) for t in templates)) for key in ['Type','Availability']},
    'template_field_counts': {key: dict(collections.Counter(t.findtext(key) for t in templates)) for key in ['FactionId','Tier','Type','Kind','Rarity']},
    'ability_records': len(abilities), 'ability_types': dict(collections.Counter(a.get('Type') for a in abilities)),
    'card_ability_references_not_in_templates': sorted(ability_ids - ids),
    'node_type_count': len(nodes), 'node_counts': dict(nodes.most_common()),
    'locales': {name: {'keys': len(rows), 'template_name_missing_ids': name_missing[name]} for name,rows in locales.items()},
    'note': 'Raw counts, not a count of unique collectible cards. Missing abilities/names can be legitimate service or vanilla cards.',
}
save('beta-data-summary.json', stats)
with (OUT / 'beta-template-manifest.csv').open('w', encoding='utf-8-sig', newline='') as f:
    fields = ['Id','DebugName','Availability','FactionId','Tier','Type','Kind','Rarity','Power','Armor','InitialTimer','Tokens','LinkedTemplateId','ArtId','has_card_ability','en_name','ru_name']
    writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
    for t in templates:
        row = {key: t.get(key) if key in ['Id','DebugName','Availability'] else t.findtext(key) for key in fields[:13]}
        art = t.find('ArtDefinition')
        row.update(ArtId=art.get('ArtId') if art is not None else None, has_card_ability=t.get('Id') in ability_ids,
                   en_name=locales['Localization/en_us.csv'].get(t.get('Id')+'_name'), ru_name=locales['Localization/ru_ru.csv'].get(t.get('Id')+'_name'))
        writer.writerow(row)

text = (DIY / 'GwentGame/GwentMap.cs').read_text(encoding='utf-8-sig')
# Static recognisable initializers only. Flag count rather than claiming execution equivalence.
entries = []
for m in re.finditer(r'new GwentCard\s*\(\)\s*\{(.*?)\n\s*\}\s*\n\s*\}', text, re.S):
    body = m.group(1)
    values = {k: re.search(r'\b'+k+r'\s*=\s*"([^"]+)"', body) for k in ['CardId','CardArtsId']}
    if not values['CardId']: continue
    power = re.search(r'\bStrength\s*=\s*(-?\d+)', body)
    entries.append({'id': values['CardId'].group(1), 'art': values['CardArtsId'].group(1) if values['CardArtsId'] else None, 'strength': int(power.group(1)) if power else None})
templates_by_id = {t.get('Id'): t for t in templates}
candidates = []; differences = []
for e in entries:
    # Art IDs often resemble TemplateId*100, but this is an audit candidate, never canonical mapping.
    if not e['art'] or not e['art'].isdigit(): continue
    candidate = str(int(e['art'])//100)
    t = templates_by_id.get(candidate)
    if t is None: continue
    row = dict(e, beta_candidate=candidate, beta_name=t.get('DebugName'), beta_power=int(t.findtext('Power')), status='art-derived candidate; needs identity/effect confirmation')
    candidates.append(row)
    if row['strength'] is not None and row['strength'] != row['beta_power']: differences.append(row)
save('diy-audit.json', {'cardmap_version': re.search(r'new Version\(([^)]+)\)',text).group(1), 'parsed_entries':len(entries), 'distinct_parsed_ids':len({e['id'] for e in entries}), 'new_gwentcard_occurrences':text.count('new GwentCard'), 'effect_cs_files':len(list((DIY/'CardEffects').rglob('*.cs'))), 'art_mapping_candidates':len(candidates), 'power_differences_on_candidates':differences, 'note':'Regex reconnaissance. Art-derived joins are candidates, not confirmed semantic mappings.'})
save('diy-to-beta-candidates.json', candidates)
print(json.dumps({'templates':len(templates),'abilities':len(abilities),'node_types':len(nodes),'locales':len(locales),'parsed_diy_entries':len(entries),'power_difference_candidates':len(differences)},ensure_ascii=True))
