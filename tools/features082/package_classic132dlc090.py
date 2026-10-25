"""0.9.0 build 14: Classic 1.32 item definitions, texts and keg icon as a DLC.

1.32 reads new item definition files only through a DLC definition (.reddlc with
CR4DefinitionsDLCMounter / CR4DefinitionsNGPlusDLCMounter, as dlc\\dlc1\\dlc1.reddlc);
XML files added to a Mods bundle are ignored. Item names come from w3strings and the
inventory icon from texture.cache, both loaded from the DLC content folder (as DLC1).
Confirmed in game: the items from such a DLC exist and innkeepers stock kegs.

Adds to the 1.32 archive:
  DLC/dlcBetaGwentClassic132Items/content/{bundles/blob0.bundle, metadata.store, dep.cache,
      *.w3strings (v162), texture.cache (v6)}
Replaces the 1.32 After-Uninstall module (a Mods stub is not loaded by 1.32) with
  After-Uninstall/DLC/dlcBetaGwentClassic132KeepItems (inert definitions, same as 5.0+).
Both archives get the refreshed BetaGwentDocs. Main mod files, scripts and Flash are copied unchanged.

Reads  <BG_SOURCE>/package-candidate/archives-optional-keep (build 13)
Writes <BG_FINAL>/package-candidate/archives-optional-keep (+ classic132-dlc work folder)
"""
from pathlib import Path
import hashlib, json, os, re, struct, sys, zipfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / 'tools/classic132'), str(HERE)]
import classic_items_dlc090 as dlc
import classic132_assets090 as assets
from formats import bundle_entries, sha

SOURCE = ROOT / 'BetaGwent/build' / os.environ.get('BG_SOURCE', 'release090-final13')
FINAL = ROOT / 'BetaGwent/build' / os.environ.get('BG_FINAL', 'release090-final14')
CAND = SOURCE / 'package-candidate'
SRC = CAND / 'archives-optional-keep'
OUT = FINAL / 'package-candidate/archives-optional-keep'
WORK = FINAL / 'classic132-dlc'
ITEMS = 'dlcBetaGwentClassic132Items'
KEEP = 'dlcBetaGwentClassic132KeepItems'
DIR = 'After-Uninstall'
TAGS = 'NoShow,NoShowInPlayersInventory,EncumbranceOff,NoDrop'
KEYS = ('bg_keg_name', 'bg_keg_desc')
NG_CONTENT = CAND / 'nextgen/package/Mods/modBetaGwent0924/content'
DOCS = {'BetaGwentDocs/README_EN.md': ROOT / 'docs/releases/0.9.0/nexus/en/description.md',
        'BetaGwentDocs/README_RU.md': ROOT / 'docs/releases/0.9.0/nexus/ru/description.md',
        'BetaGwentDocs/CHANGELOG_EN.md': ROOT / 'docs/releases/0.9.0/nexus/en/changelog.md',
        'BetaGwentDocs/CHANGELOG_RU.md': ROOT / 'docs/releases/0.9.0/nexus/ru/changelog.md',
        'BetaGwentDocs/CLEANUP_EN.md': ROOT / 'docs/releases/0.9.0_CLEANUP_EN.md',
        'BetaGwentDocs/CLEANUP_RU.md': ROOT / 'docs/releases/0.9.0_CLEANUP_RU.md'}
README = {
'EN': f"""Gwent Beta Classic 0.9.0 (1.32) — After-Uninstall item definitions

Install this ONLY after removing Gwent Beta Classic. Do not install it together with the mod.

Why: merchants, your stash and containers in a save may still hold Beta Gwent items (cards and kegs).
Without their definitions the game drops the whole inventory of such a merchant when the save loads.
This module only defines those items as hidden, worthless objects (and keeps the old Redux item
definitions). It has no scripts and changes nothing else. Keep it installed for saves made with the mod.
On 1.32 new item definitions load only from a DLC, so this module is a DLC folder.

Uninstall:
1. In the game with the mod still installed: bg_clean_confirm('DELETE_BETA_GWENT'), save to a NEW slot, exit.
2. Remove Mods/modBetaGwentClassic132, DLC/dlcBetaGwentClassic132Assets and DLC/{ITEMS}.
3. Copy the DLC folder from this After-Uninstall folder into the game directory (DLC/{KEEP}).
4. Rebuild Script Merger merges if you use it, load the new slot and save again.
Reinstalling the mod: remove DLC/{KEEP} first.
""",
'RU': f"""Gwent Beta Classic 0.9.0 (1.32) — определения предметов после удаления

Устанавливайте ТОЛЬКО после удаления Gwent Beta Classic. Не ставьте вместе с модом.

Зачем: у торговцев, в тайнике и в контейнерах сохранения могут оставаться предметы беты (карты и бочки).
Без их определений игра при загрузке теряет весь инвентарь такого торговца. Этот модуль только описывает
эти предметы как скрытые и бесплатные (и сохраняет определения старых предметов Redux). Скриптов в нём нет,
больше он ничего не меняет. Держите его установленным для сохранений, сделанных с модом.
В 1.32 новые определения предметов загружаются только из DLC, поэтому модуль — папка DLC.

Удаление:
1. В игре с ещё установленным модом: bg_clean_confirm('DELETE_BETA_GWENT'), сохраниться в НОВЫЙ слот, выйти.
2. Удалить Mods/modBetaGwentClassic132, DLC/dlcBetaGwentClassic132Assets и DLC/{ITEMS}.
3. Скопировать папку DLC из этой папки After-Uninstall в каталог игры (DLC/{KEEP}).
4. Пересобрать слияния Script Merger, если он используется, загрузить новый слот и сохраниться.
Повторная установка мода: сначала удалите DLC/{KEEP}.
"""}


def utf16(raw):
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')): return raw
    text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    if text.startswith('<?xml'):
        end = text.index('?>')
        text = re.sub(r"encoding\s*=\s*(['\"])[^'\"]*\1", 'encoding="UTF-16"', text[:end]) + text[end:]
    return text.replace('\n', '\r\n').encode('utf-16')


def read_xml(raw):
    return ET.fromstring(raw.decode('utf16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig'))


def item_xml():
    xml, names = {}, set()
    for mode in ['items', 'items_plus']:
        shop = (CAND / 'classic/resources/gameplay' / mode / 'betagwent_shop.xml').read_bytes()
        redux = (CAND / 'redux/gameplay' / mode / 'betagwent_redux_inventory.xml').read_bytes()
        items = read_xml(shop).findall('./definitions/items/item')
        names |= {x.attrib['name'] for x in items}
        keg = [x for x in items if x.attrib['name'] == 'betagwent_keg']
        assert len(keg) == 1 and keg[0].attrib['localisation_key_name'] == KEYS[0], mode
        assert keg[0].attrib['icon_path'] == 'icons/inventory/betagwent/ico_betagwent_keg.png', mode
        xml[f'{mode}/betagwent_shop.xml'] = utf16(shop)
        xml[f'{mode}/betagwent_redux_inventory.xml'] = utf16(redux)
    assert names and all(n.startswith('betagwent_') for n in names)
    return xml, sorted(names)


def keep_xml(names):
    xml = {}
    for mode in ['items', 'items_plus']:
        root = ET.Element('redxml'); items = ET.SubElement(ET.SubElement(root, 'definitions'), 'items')
        for name in names:
            item = ET.SubElement(items, 'item', dict(name=name, hold_slot='', equip_slot='', template='', stackable='999',
                ability_slots='0', category='misc', price='0', icon_path='icons/inventory/gwint/ico_gwent_weather_neutral.png',
                localisation_key_name='gwint_name_dummy', localisation_key_description='gwint_desc_gwint_card'))
            ET.SubElement(item, 'tags').text = TAGS
        xml[f'{mode}/betagwent_keep_items.xml'] = utf16(ET.tostring(root, encoding='utf8', xml_declaration=True))
        xml[f'{mode}/betagwent_redux_inventory.xml'] = utf16((CAND / 'redux/gameplay' / mode / 'betagwent_redux_inventory.xml').read_bytes())
    return xml


def main():
    assert SRC.is_dir() and not OUT.exists() and not WORK.exists(), (SRC, OUT, WORK)
    for target in DOCS.values():
        text = target.read_text('utf-8-sig')
        assert 'After-Uninstall' in text or 'CHANGELOG' in str(target).upper(), target
    for doc, word in [('README_EN.md', ITEMS), ('README_RU.md', ITEMS), ('CLEANUP_EN.md', KEEP), ('CLEANUP_RU.md', KEEP)]:
        target = DOCS['BetaGwentDocs/' + doc]
        assert word in target.read_text('utf-8-sig'), 'run update_nexus14_090 and refresh_showcase090 first: ' + str(target)
    xml, names = item_xml()
    stage = WORK / '1.32'
    report = dict(items=len(names), dlc=dlc.build_dlc(stage / 'DLC', ITEMS, xml, 'Gwent Beta Classic items', WORK / 'work-items'))
    content = stage / 'DLC' / ITEMS / 'content'
    report['strings'] = {}
    sources = sorted(NG_CONTENT.glob('*.w3strings'))
    assert {p.stem for p in sources} >= {'en', 'ru', 'de', 'fr', 'it', 'pl', 'es', 'esmx', 'br', 'jp', 'kr', 'zh', 'cn'}, sources
    for p in sources:
        raw, info = assets.classic_strings(p.read_bytes(), KEYS)
        (content / p.name).write_bytes(raw); report['strings'][p.name] = info
    cache, report['textureCache'] = assets.classic_texture_cache((NG_CONTENT / 'texture.cache').read_bytes())
    (content / 'texture.cache').write_bytes(cache)
    keep_stage = WORK / 'keep-1.32' / DIR
    report['keep'] = dlc.build_dlc(keep_stage / 'DLC', KEEP, keep_xml(names), 'Gwent Beta Classic kept items', WORK / 'work-keep')
    for lang, text in README.items(): (keep_stage / f'README_{lang}.txt').write_text(text.replace('\n', '\r\n'), 'utf-8-sig')
    OUT.mkdir(parents=True); report['archives'] = {}
    for platform in ['1.32', '5.0+']:
        name = f'GwentBetaClassic-0.9.0-{platform}-AllLanguages.zip'; classic = platform == '1.32'
        added = []
        with zipfile.ZipFile(SRC / name) as src, zipfile.ZipFile(OUT / name, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as dst:
            manifest = json.loads(src.read('manifest-0.9.0.json')); replaced = set()
            for info in src.infolist():
                n = info.filename
                if n == 'manifest-0.9.0.json' or (classic and n.startswith(DIR + '/')): continue
                assert not n.startswith('DLC/' + ITEMS), n
                if n in DOCS:
                    dst.writestr(info, DOCS[n].read_bytes()); replaced.add(n); continue
                dst.writestr(info, src.read(n))
            assert replaced == set(DOCS), replaced
            if classic:
                for base, prefix in [(stage, ''), (keep_stage, DIR + '/')]:
                    for p in sorted(base.rglob('*')):
                        if p.is_file():
                            arc = prefix + p.relative_to(base).as_posix(); dst.write(p, arc)
                            added.append(dict(path=arc, bytes=p.stat().st_size, sha256=sha(p)))
                manifest['files'] = [f for f in manifest['files'] if not f['path'].startswith(DIR + '/')]
                manifest['afterUninstall'] = dict(folder=DIR, dlc=KEEP, items=len(names), installWithMod=False)
                manifest['classicItemsDlc'] = ITEMS
            for row in manifest['files']:
                if row['path'] in DOCS:
                    data = DOCS[row['path']].read_bytes(); row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            manifest['files'] = sorted(manifest['files'] + added, key=lambda f: f['path'])
            dst.writestr('manifest-0.9.0.json', json.dumps(manifest, indent=2), zipfile.ZIP_DEFLATED, 6)
        with zipfile.ZipFile(OUT / name) as z:
            assert z.testzip() is None
            entries = set(z.namelist())
            if classic:
                for need in [f'DLC/{ITEMS}/content/bundles/blob0.bundle', f'DLC/{ITEMS}/content/ru.w3strings',
                             f'DLC/{ITEMS}/content/texture.cache', f'DLC/dlcBetaGwentClassic132Assets/content/metadata.store',
                             f'{DIR}/DLC/{KEEP}/content/bundles/blob0.bundle', f'{DIR}/README_EN.txt']:
                    assert need in entries, need
                assert not any(e.startswith(f'{DIR}/Mods/') for e in entries)
                got = {n.replace('\\', '/') for n, _ in bundle_entries(content / 'bundles/blob0.bundle')}
                assert f'dlc/{ITEMS.lower()}/data/gameplay/items/betagwent_shop.xml' in got, got
            manifest = json.loads(z.read('manifest-0.9.0.json'))
            assert {f['path'] for f in manifest['files']} == entries - {'manifest-0.9.0.json'}, 'manifest/archive mismatch'
        digest = sha(OUT / name)
        (OUT / (name + '.sha256')).write_text(digest + '  ' + name + '\n', 'ascii')
        report['archives'][name] = dict(sha256=digest, bytes=(OUT / name).stat().st_size)
        print(name, (OUT / name).stat().st_size // (1024 * 1024), 'MB')
    (WORK / 'classic132-dlc.json').write_text(json.dumps(report, indent=2), 'utf8')
    print('items', len(names), 'strings', len(report['strings']), 'icon', report['textureCache']['textures'])


if __name__ == '__main__':
    main()
