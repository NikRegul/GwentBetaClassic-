"""Prepare missing legacy item definitions before save deserialization (no save edits)."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / 'data/beta924/compatibility/redux_inventory.json'
FILENAME = 'betagwent_redux_inventory.xml'


def definitions(catalog, mode):
    required = catalog['requiredItemNames']
    native = catalog['nativeItemNames'][mode]
    if len(required) != len(set(required)) or len(native) != len(set(native)):
        raise ValueError('Duplicate item names')
    if not set(native) <= set(required):
        raise ValueError('Native coverage must be a subset of the legacy catalog')
    if any(not re.fullmatch(r'gwint_card_[a-z0-9_]+', name) for name in required):
        raise ValueError('Only audited gwint card names may be retained')
    root = ET.Element('redxml')
    items = ET.SubElement(ET.SubElement(root, 'definitions'), 'items')
    for name in sorted(set(required) - set(native)):
        item = ET.SubElement(items, 'item', {
            'name': name, 'hold_slot': '', 'equip_slot': '', 'template': '',
            'stackable': '999', 'ability_slots': '0', 'category': 'misc', 'price': '0',
            'icon_path': 'icons/inventory/gwint/ico_gwent_weather_neutral.png',
            'localisation_key_name': 'gwint_name_dummy',
            'localisation_key_description': 'gwint_desc_gwint_card',
        })
        ET.SubElement(item, 'tags').text = 'NoShowInPlayersInventory,EncumbranceOff,BetaGwentLegacyRedux'
    ET.indent(root, space='  ')
    return ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'


def verify(raw, catalog, mode):
    root = ET.fromstring(raw)
    items = root.findall('./definitions/items/item')
    names = [item.attrib['name'] for item in items]
    native = set(catalog['nativeItemNames'][mode])
    required = set(catalog['requiredItemNames'])
    assert len(names) == len(set(names))
    assert not set(names) & native, 'Must not replace vanilla items'
    assert set(names) | native == required, 'Missing legacy definition'
    for item in items:
        assert item.attrib['category'] == 'misc'
        assert item.attrib['template'] == item.attrib['hold_slot'] == item.attrib['equip_slot'] == ''
        assert item.attrib['price'] == '0'
        assert set(item.findtext('tags').split(',')) == {
            'NoShowInPlayersInventory', 'EncumbranceOff', 'BetaGwentLegacyRedux'}
        assert list(item) == item.findall('tags'), 'Legacy definitions must not execute actions'
    return dict(required=len(required), native=len(native), retained=len(names),
                sha256=hashlib.sha256(raw).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'BetaGwent/build/features082/redux-inventory')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to((ROOT / 'BetaGwent/build').resolve()) or out == (ROOT / 'BetaGwent/build').resolve():
        parser.error('Output must be a build subdirectory')
    if out.exists() and not args.verify:
        parser.error('Use a fresh directory; previous candidates are retained')
    catalog = json.loads(CATALOG.read_text('utf8'))
    assert catalog['schema'] == 1
    report = dict(source=str(CATALOG.relative_to(ROOT)), sourceSha256=hashlib.sha256(CATALOG.read_bytes()).hexdigest(),
                  modes={}, gameInstalled=False, saveFilesModified=False, gameplayVerified=False,
                  nativeBundleBuilt=False)
    for mode in ('items', 'items_plus'):
        path = out / 'gameplay' / mode / FILENAME
        raw = definitions(catalog, mode)
        if args.verify:
            assert path.read_bytes() == raw, 'Candidate differs from audited source names'
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        report['modes'][mode] = verify(raw, catalog, mode)
    if not args.verify:
        (out / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', 'utf8')
    else:
        assert json.loads((out / 'verification.json').read_text('utf8')) == report
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
