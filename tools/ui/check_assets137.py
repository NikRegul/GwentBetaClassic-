"""Verify current translation inputs, embedded glyphs and paged leader assets."""
import hashlib
import json
import math
import re
import sqlite3
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
from localization89 import strings
from language_release137 import LOCALES, translate
from update_board_resource import validate_resource, validate_image_linkages, unpack_root
from build_leaders136 import movie_parts


def sha(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path): return json.loads(path.read_text('utf-8-sig'))

def abc_strings(data):
    offset=4 # minor + major version
    def u30():
        nonlocal offset
        value=0
        for shift in range(0,35,7):
            byte=data[offset];offset+=1;value|=(byte&127)<<shift
            if not byte&128:return value
        raise ValueError('Invalid ABC varint')
    for pool in range(2):
        count=u30()
        for _ in range(max(0,count-1)):u30()
    count=u30();offset+=max(0,count-1)*8
    strings=[]
    count=u30()
    for _ in range(max(0,count-1)):
        size=u30();strings.append(data[offset:offset+size].decode('utf8'));offset+=size
    return strings


def main():
    prepared = ROOT/'BetaGwent/build/languages137'
    leaders = read(ROOT/'docs/evidence/leaders137.json')
    texts = read(ROOT/'docs/evidence/languages137.json')['languages']
    cards = read(ROOT/'data/beta924/duel/slice.json')['cards']
    allowed = {str(c['templateId']) for c in cards if int(c['fields']['Tier']) == 1}
    assert set(leaders['bindings']) == allowed and len(allowed) == 21
    assert set(leaders['loops']) == set(leaders['bindings'].values())
    assert leaders['fps'] == 24 and leaders['fullCycles']
    assert leaders['maxOwners'] == 4 and leaders['maxPagesPerOwner'] == 2
    assert leaders['maxResidentPagesIncludingRetired']==12
    assert leaders['engineOwnedAtlasReleasedByLoader']
    for source,digest in leaders['sources'].items():assert sha(ROOT/source)==digest,('Stale leader code',source)
    assert leaders['conservativeAtlasMemoryMiB'] < 70
    canonical = set()
    for art, loop in leaders['loops'].items():
        folder = ROOT/'BetaGwent/build/leader-loops137'/art
        meta = read(folder/'complete.json')
        assert sha(folder/'complete.json') == loop['captureSha256']
        assert meta['fullCycle'] and meta['loopOnly'] and meta['introExcluded']
        assert len(list(folder.glob('*.png'))) == loop['sourceFrames'] == meta['frames']
        assert loop['frames'] == meta['frames'] - 8 and loop['seamOverlap'] == 8
        assert abs(loop['sourceFrames'] - math.ceil(loop['nativeDuration']*24)) <= 1
        assert loop['pages'] == math.ceil(loop['frames']/24)
        canonical.update(f'{art}_p{i:03}' for i in range(loop['pages']))
    assert set(leaders['resources']) == canonical
    folder = ROOT/'BetaGwent/build/leaders137/resources'
    assert {p.stem for p in folder.rglob('*.redswf')} == canonical
    for item in leaders['resources'].values():
        path = folder/item['path']
        assert sha(path) == item['sha256'] and path.stat().st_size < 1024**2
        resource, _ = validate_resource(path)
        assert len(resource.exports) == 2
        validate_image_linkages(resource)
        # Check the shipped ABC, not just the source: old crashing page bytecode
        # contained the public BitmapData.dispose multiname.
        abc=[p for code,p,raw in movie_parts(unpack_root(resource)[1])[1] if code==82]
        assert abc
        for block in abc:
            start=block.index(b'\0',4)+1
            assert 'dispose' not in abc_strings(block[start:]), ('Unsafe native atlas disposal',path)

    english = strings()
    catalog_path=ROOT/'BetaGwent/development/scripts/game/betagwent/duelCatalog.ws'
    catalog=catalog_path.read_text('utf-8-sig')
    catalog_strings=[json.loads('"'+raw+'"') for pair in re.findall(
        r'value.title = "((?:[^"\\]|\\.)*)"; value.description = "((?:[^"\\]|\\.)*)";',catalog) for raw in pair]
    assert len(catalog_strings)>=2*479
    supplement = read(ROOT/'data/beta924/design/ui-overrides137.json')
    rows = ['Ваш ближний ряд', 'Ваш дальний ряд', 'Ваш осадный ряд',
            'Вражеский ближний ряд', 'Вражеский дальний ряд', 'Вражеский осадный ряд']
    assert len(texts) == 13 and set(texts) == set(LOCALES.values())
    inputs = [ROOT/'data/beta924/design/english89.json', ROOT/'tools/localization89.py',
              ROOT/'data/beta924/design/ui-overrides137.json',catalog_path]
    native_strings = {}
    database = ROOT/'GwentB/myproject1/LocalEditorStringDataBaseW3_UTF8_mod.db'
    with sqlite3.connect(database.as_uri()+'?mode=ro', uri=True) as db:
        items = [row[0] for row in db.execute('select TEXT from STRINGS where LANG=9')]
    assert len(items) == 396
    for locale, item in texts.items():
        path = prepared/'ui'/f'{locale}.json'
        lookup = {} if locale == 'ru_ru' else dict(english) if locale == 'en_us' else read(path)
        if path.exists(): inputs.append(path)
        if locale!='ru_ru':
            assert all(text in lookup for text in catalog_strings), ('Missing current card/token/deck text',locale)
        # Native game strings use the original dictionary, independent of casing helpers.
        native_strings[locale] = [translate(raw, locale, lookup) for raw in items]
        assert all(native_strings[locale])
        if locale != 'ru_ru':
            assert not any(re.search('[А-Яа-яЁё]', text) for text in native_strings[locale]), locale
        for key, value in zip(rows, supplement.get(locale, rows)): lookup.setdefault(key, value)
        lookup.update({k.upper(): v.upper() for k, v in list(lookup.items()) if k})
        assert hashlib.sha256(json.dumps(lookup, ensure_ascii=True, sort_keys=True).encode()).hexdigest() == item['dictionarySha256'], ('User dictionary changed; rebuild text resources', locale)
        source = ROOT/'BetaGwent/build/text137'/locale/'BetaLocale137.as'
        assert sha(source) == item['sourceSha256']
        declared = json.loads(re.search(r'characters:String=(.*);', source.read_text('utf8'))[1])
        needed = {ord(c) for text in lookup.values() for c in text if ord(c) >= 32}
        assert needed <= set(map(ord, declared))
        resource_path = ROOT/'BetaGwent/build/text137/resources'/item['path']
        assert sha(resource_path) == item['sha256']
        resource, _ = validate_resource(resource_path)
        assert len(resource.exports) == 1
        validate_image_linkages(resource)
        tags = movie_parts(unpack_root(resource)[1])[1]
        fonts = [p for code, p, _ in tags if code == 75]
        assert len(fonts) == 2 and not any(code in (20,21,35,36,90,1009) for code, _, _ in tags)
        for payload in fonts:
            # DefineFont3: id, flags, language, nameLen/name, glyphCount, wide offsets.
            start = 5 + payload[4]
            count = struct.unpack_from('<H', payload, start)[0]
            offset_start = start + 2
            assert payload[2] & 4 and payload[2] & 8
            code_offset = struct.unpack_from('<I', payload, offset_start+4*count)[0]
            codes = set(struct.unpack_from('<'+str(count)+'H', payload, offset_start+code_offset))
            assert set(map(ord, declared)) <= codes, ('Missing embedded glyph', locale)
        if locale == 'zh_tw':
            assert item['fallbacks']['body'][str(ord('呐'))] == 'NotoSansSC-Medium.otf'
    sources = ['tools/ui/check_assets137.py','tools/ui/build_languages137.py',
               'tools/ui/build_leaders137.py','tools/ui/leaders060/Capture137.cs',
               'tools/ui/leaders060/BetaLeaderMovie137.as','tools/language_release137.py']
    result = dict(stage=137, leaders=21, pages=len(canonical), textLanguages=13,
                  fullCycles=True, introExcluded=True, otherAnimatedCards=0,
                  nativeItemStringsPerLanguage=396, embeddedGlyphCoverage=True,
                  currentCatalogStringsChecked=len(catalog_strings),
                  inputSources={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in inputs},
                  sources={p:sha(ROOT/p) for p in sources}, nativeGameTested=False)
    (ROOT/'docs/evidence/assets137.json').write_text(json.dumps(result, indent=2)+'\n','utf8')
    print('PASS: current 13 dictionaries and fonts, 396 native strings per language, 21 leaders/'+str(len(canonical))+' pages')


if __name__ == '__main__': main()
