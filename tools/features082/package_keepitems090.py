"""0.9.0: add the After-Uninstall item-definition module to both release archives.

Without the mod, a save still holds Beta items in merchant stock (betagwent_shop_*
cards, betagwent_keg kegs), the stash and containers. Missing item definitions make
the game drop the whole inventory of that merchant on load (reported on 5.01 after
uninstalling with bg_clean_confirm). This module keeps inert definitions of every
betagwent_* item (hidden everywhere: NoShow, price 0) plus the 203 legacy Redux item
definitions. It has no scripts, no loot tables and no graphics and is installed only
after removing the main mod (same idea as 0.8.2's modBetaGwentCleanerItems082).

Reads  <BG_FINAL>/package-candidate/archives-optional  (repack_optional090 output)
Writes <BG_FINAL>/package-candidate/archives-optional-keep (same archives + After-Uninstall/,
       refreshed BetaGwentDocs README/CHANGELOG/CLEANUP and manifest)
"""
from pathlib import Path
import hashlib, json, os, re, shutil, struct, sys, zipfile, zlib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / 'BetaGwent/build' / os.environ.get('BG_FINAL', 'release090-final12')
CAND = FINAL / 'package-candidate'
SRC = CAND / 'archives-optional'
OUT = CAND / 'archives-optional-keep'
WORK = FINAL / 'keepitems'
MOD = 'modBetaGwentKeepItems'
DIR = 'After-Uninstall'
sys.argv[1:] = []
sys.path[:0] = [str(ROOT / 'tools/classic132'), str(Path(__file__).parent)]
from formats import write_bundle, bundle_entries, sha
from build_resources import vlq
import package_cleaner082 as pc  # metadata() writer for both platforms

TAGS = 'NoShow,NoShowInPlayersInventory,EncumbranceOff,NoDrop'
# Documentation inside the archives is refreshed from the current texts (uninstall section).
DOCS = {'BetaGwentDocs/README_EN.md': ROOT / 'docs/releases/0.9.0/nexus/en/description.md',
        'BetaGwentDocs/README_RU.md': ROOT / 'docs/releases/0.9.0/nexus/ru/description.md',
        'BetaGwentDocs/CHANGELOG_EN.md': ROOT / 'docs/releases/0.9.0/nexus/en/changelog.md',
        'BetaGwentDocs/CHANGELOG_RU.md': ROOT / 'docs/releases/0.9.0/nexus/ru/changelog.md',
        'BetaGwentDocs/CLEANUP_EN.md': ROOT / 'docs/releases/0.9.0_CLEANUP_EN.md',
        'BetaGwentDocs/CLEANUP_RU.md': ROOT / 'docs/releases/0.9.0_CLEANUP_RU.md'}
README = {
'EN': """Gwent Beta Classic 0.9.0 — After-Uninstall item definitions

Install this ONLY after removing Gwent Beta Classic. Do not install it together with the mod.

Why: merchants, your stash and containers in a save may still hold Beta Gwent items (cards and kegs).
Without their definitions the game drops the whole inventory of such a merchant when the save loads.
This module only defines those items as hidden, worthless objects (and keeps the old Redux item
definitions). It has no scripts and changes nothing else. Keep it installed for saves made with the mod.

Uninstall:
1. In the game with the mod still installed: bg_clean_confirm('DELETE_BETA_GWENT'), save to a NEW slot, exit.
2. Remove Mods/modBetaGwent0924 (Next-Gen) or Mods/modBetaGwentClassic132 and DLC/dlcBetaGwentClassic132Assets (1.32).
3. Copy the Mods folder from this After-Uninstall folder into the game directory (Mods/modBetaGwentKeepItems).
4. Rebuild Script Merger merges if you use it, load the new slot and save again.
Reinstalling the mod: remove Mods/modBetaGwentKeepItems first.
""",
'RU': """Gwent Beta Classic 0.9.0 — определения предметов после удаления

Устанавливайте ТОЛЬКО после удаления Gwent Beta Classic. Не ставьте вместе с модом.

Зачем: у торговцев, в тайнике и в контейнерах сохранения могут оставаться предметы беты (карты и бочки).
Без их определений игра при загрузке теряет весь инвентарь такого торговца. Этот модуль только описывает
эти предметы как скрытые и бесплатные (и сохраняет определения старых предметов Redux). Скриптов в нём нет,
больше он ничего не меняет. Держите его установленным для сохранений, сделанных с модом.

Удаление:
1. В игре с ещё установленным модом: bg_clean_confirm('DELETE_BETA_GWENT'), сохраниться в НОВЫЙ слот, выйти.
2. Удалить Mods/modBetaGwent0924 (Next-Gen) или Mods/modBetaGwentClassic132 и DLC/dlcBetaGwentClassic132Assets (1.32).
3. Скопировать папку Mods из этой папки After-Uninstall в каталог игры (Mods/modBetaGwentKeepItems).
4. Пересобрать слияния Script Merger, если он используется, загрузить новый слот и сохраниться.
Повторная установка мода: сначала удалите Mods/modBetaGwentKeepItems.
"""}


def utf16(raw):
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')): return raw
    text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    if text.startswith('<?xml'):
        end = text.index('?>'); decl = re.sub(r"encoding\s*=\s*(['\"])[^'\"]*\1", 'encoding="UTF-16"', text[:end])
        text = decl + text[end:]
    return text.replace('\n', '\r\n').encode('utf-16')


def read_xml(p):
    raw = p.read_bytes()
    return ET.fromstring(raw.decode('utf16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig'))


def item_names():
    names = set()
    for mode in ['items', 'items_plus']:
        root = read_xml(CAND / 'classic/resources/gameplay' / mode / 'betagwent_shop.xml')
        names |= {x.attrib['name'] for x in root.findall('./definitions/items/item')}
    assert names and all(n.startswith('betagwent_') for n in names) and 'betagwent_keg' in names, len(names)
    return sorted(names)


def build(content, classic, names):
    resource = WORK / ('resources-classic' if classic else 'resources-nextgen'); files = {}
    for mode in ['items', 'items_plus']:
        root = ET.Element('redxml'); items = ET.SubElement(ET.SubElement(root, 'definitions'), 'items')
        for name in names:
            item = ET.SubElement(items, 'item', dict(name=name, hold_slot='', equip_slot='', template='', stackable='999',
                ability_slots='0', category='misc', price='0', icon_path='icons/inventory/gwint/ico_gwent_weather_neutral.png',
                localisation_key_name='gwint_name_dummy', localisation_key_description='gwint_desc_gwint_card'))
            ET.SubElement(item, 'tags').text = TAGS
        redux = CAND / 'redux/gameplay' / mode / 'betagwent_redux_inventory.xml'
        assert redux.is_file(), redux
        for name, raw in [('betagwent_keep_items.xml', ET.tostring(root, encoding='utf8', xml_declaration=True)), ('betagwent_redux_inventory.xml', redux.read_bytes())]:
            if classic: raw = utf16(raw)  # 1.32 XML definitions are UTF-16 LE
            p = resource / 'gameplay' / mode / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
            files[p.relative_to(resource).as_posix()] = p
    content.mkdir(parents=True); bundle = content / 'blob0.bundle'
    if classic:
        write_bundle(files, bundle)
    else:
        # Next-Gen bundle layout as in package_cleaner082 (304-byte TOC rows, header from the main mod).
        rows = bytearray(); offset = (32 + 304 * len(files) + 4095) & ~4095; positions = {}
        for name, p in sorted(files.items()):
            row = bytearray(304); encoded = name.replace('/', '\\').encode('ascii'); row[:len(encoded)] = encoded
            struct.pack_into('<QIIII', row, 272, offset, p.stat().st_size, p.stat().st_size, zlib.crc32(p.read_bytes()), 0)
            positions[name] = offset; rows += row; offset = (offset + p.stat().st_size + 4095) & ~4095
        header = bytearray((CAND / 'nextgen/package/Mods/modBetaGwent0924/content/blob0.bundle').read_bytes()[:32])
        struct.pack_into('<II', header, 8, max(positions[n] + p.stat().st_size for n, p in files.items()), 0)
        struct.pack_into('<I', header, 16, len(rows))
        with bundle.open('wb') as stream:
            stream.write(header); stream.write(rows)
            for name, p in sorted(files.items()):
                stream.write(bytes(positions[name] - stream.tell())); stream.write(p.read_bytes())
    got = {n.replace('\\', '/'): hashlib.sha256(raw).hexdigest() for n, raw in bundle_entries(bundle)}
    assert got == {n: sha(p) for n, p in files.items()}, 'bundle round trip'
    (content / 'metadata.store').write_bytes(pc.metadata(files, bundle, classic))
    # XML-only package: sentinel dependency cache, no external resources.
    (content / 'dep.cache').write_bytes(b'SPED' + struct.pack('<I', 2) + vlq(1) + bytes(16) + b''.join(vlq(1) + bytes(4) for _ in range(3)))
    return files


def main():
    assert SRC.is_dir() and not OUT.exists(), (SRC, OUT)
    assert not WORK.exists(), 'Fresh keepitems work folder required'
    names = item_names(); OUT.mkdir()
    report = dict(items=len(names), tags=TAGS, archives={})
    for platform, classic in [('1.32', True), ('5.0+', False)]:
        stub = WORK / platform / DIR; content = stub / 'Mods' / MOD / 'content'
        build(content, classic, names)
        (stub / 'Mods' / MOD / 'info.json').write_text(json.dumps(dict(version='0.9.0', platform=platform, purpose='inert Beta item definitions after uninstalling', items=len(names), scripts=False), indent=2), 'utf8')
        for lang, text in README.items(): (stub / f'README_{lang}.txt').write_text(text.replace('\n', '\r\n'), 'utf-8-sig')
        name = f'GwentBetaClassic-0.9.0-{platform}-AllLanguages.zip'
        with zipfile.ZipFile(SRC / name) as src, zipfile.ZipFile(OUT / name, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as dst:
            manifest = None; replaced = set()
            for info in src.infolist():
                assert not info.filename.startswith(DIR + '/')
                if info.filename == 'manifest-0.9.0.json': manifest = json.loads(src.read(info.filename)); continue
                if info.filename in DOCS:
                    assert 'After-Uninstall'.encode() in DOCS[info.filename].read_bytes(), 'run update_nexus_keep090/refresh_showcase090 first: ' + info.filename
                    dst.writestr(info, DOCS[info.filename].read_bytes()); replaced.add(info.filename); continue
                dst.writestr(info, src.read(info.filename))
            assert manifest and replaced == set(DOCS), (replaced, set(DOCS))
            added = []
            for p in sorted(stub.rglob('*')):
                if p.is_file():
                    arc = DIR + '/' + p.relative_to(stub).as_posix(); dst.write(p, arc)
                    added.append(dict(path=arc, bytes=p.stat().st_size, sha256=sha(p)))
            for row in manifest['files']:
                if row['path'] in DOCS:
                    data = DOCS[row['path']].read_bytes(); row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            manifest['files'] = sorted(manifest['files'] + added, key=lambda f: f['path'])
            manifest['afterUninstall'] = dict(folder=DIR, mod=MOD, items=len(names), installWithMod=False)
            dst.writestr('manifest-0.9.0.json', json.dumps(manifest, indent=2), zipfile.ZIP_DEFLATED, 6)
        with zipfile.ZipFile(OUT / name) as z:
            assert z.testzip() is None
            entries = z.namelist()
            assert f'{DIR}/Mods/{MOD}/content/blob0.bundle' in entries and f'{DIR}/README_EN.txt' in entries
            assert not any(e.startswith(f'Mods/{MOD}/') for e in entries), 'keep module must not be installed with the mod'
        digest = sha(OUT / name)
        (OUT / (name + '.sha256')).write_text(digest + '  ' + name + '\n', 'ascii')
        report['archives'][name] = dict(sha256=digest, bytes=(OUT / name).stat().st_size)
        print(name, (OUT / name).stat().st_size // (1024 * 1024), 'MB', 'keep items:', len(names))
    (OUT / 'keepitems.json').write_text(json.dumps(report, indent=2), 'utf8')


if __name__ == '__main__':
    main()
