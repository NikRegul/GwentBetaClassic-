"""0.9.0 build 15: Classic 1.32 keg reward menu through a stock menu name and stock paths.

Evidence (classic132-full-feedback/20261019-200900-310090 and scriptslog):
* RequestMenu('BetaGwentKeg') on 1.32 creates no menu at all: no BOARD_CLOSED of a
  keg instance, no load of betagwent\\betagwent_kegop.menu or its movie. The name exists
  only in the mod's guiconfig, which 1.32 does not use for new names.
* RequestMenu('TestMenu') (a name from the stock guiconfig) did create the mod's menu
  class (BOARD_CLOSED revision=0) in a separate test mod.
* DeckBuilder / GwintGame work on 1.32 the same way: stock menu name, stock .menu path,
  stock movie path with native GUIDs (fix8/fix9).

So on Classic the keg menu becomes TestMenu, exactly like the two working menus:
  betagwent\\betagwent_kegop.menu    -> gameplay\\gui_new\\guirsrc\\r4test.menu   (native GUID)
  betagwent\\betagwent_kegop.redswf  -> gameplay\\gui_new\\swf\\test\\panel_test.redswf (native GUID)
Menu definitions, movie, its 9 texture pages and every dependency index are preserved;
only the menu import, paths, GUIDs and the Classic RequestMenu name change.

Reads  <BG_SOURCE>/package-candidate/archives-optional-keep (build 14)
Writes <BG_FINAL>/package-candidate/archives-optional-keep
"""
from pathlib import Path
import hashlib, json, os, shutil, struct, sys, zipfile, zlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / 'tools/classic132'), str(ROOT / 'tools/ui'), str(ROOT / 'tools/universal')]
from formats import Resource, bundle_entries, sha
from build_resources import read_vlq
from dependencies import read_dependency_cache
from remap_depot import remap_metadata
from build_classic_stock_paths import menu_import

SOURCE = ROOT / 'BetaGwent/build' / os.environ.get('BG_SOURCE', 'release090-final14')
FINAL = ROOT / 'BetaGwent/build' / os.environ.get('BG_FINAL', 'release090-final15')
SRC = SOURCE / 'package-candidate/archives-optional-keep'
OUT = FINAL / 'package-candidate/archives-optional-keep'
WORK = FINAL / 'classic132-keg'
GAME = Path(os.environ.get('BG_GAME132', 'D:/GOG Galaxy/Games/The Witcher 3 Wild Hunt'))
ZIP = 'GwentBetaClassic-0.9.0-1.32-AllLanguages.zip'
MOD = 'Mods/modBetaGwentClassic132/content/'
SCRIPT = MOD + 'scripts/game/betagwent/developmentBoardMenu.ws'
OLD_MENU, NEW_MENU = r'betagwent\betagwent_kegop.menu', r'gameplay\gui_new\guirsrc\r4test.menu'
OLD_SWF, NEW_SWF = r'betagwent\betagwent_kegop.redswf', r'gameplay\gui_new\swf\test\panel_test.redswf'
PATHS = {OLD_MENU: NEW_MENU, OLD_SWF: NEW_SWF}
NATIVE_BUNDLES = {NEW_MENU: 'content/content0/bundles/blob.bundle', NEW_SWF: 'content/content0/bundles/r4gui.bundle'}
EXPECTED_GUIDS = {NEW_MENU: 'b0502be8e04cfeeddf0d328e40460304', NEW_SWF: '414463b5b6b760c45f673f9d145de1c7'}
CALL_OLD = "theGame.RequestMenu('BetaGwentKeg',kegMenuInit);"
CALL_NEW = "theGame.RequestMenu('TestMenu',kegMenuInit);"
# Classic 1.32: the Park-Miller step of BetaGwentProgressionPick returned the same value
# on every call (build 16: all four keg cards identical, the same three offers in every
# keg). The engine RNG (RandRange, also used for the keg voice lines, which do vary on
# 1.32) replaces it on Classic. Next-Gen keeps its generator.
PLAYER = MOD + 'scripts/game/player/playerWitcher.ws'
RNG_OLD = ("    next=16807*(betaGwentProgressionSeed%127773)-2836*(betaGwentProgressionSeed/127773);\r\n"
           "    if(next<=0)next+=2147483647;betaGwentProgressionSeed=next;\r\n"
           "    if(maximum<=0)return 0;return next%maximum;")
RNG_NEW = ("    // Classic 1.32: engine RNG (the Park-Miller step repeated one value on 1.32).\r\n"
           "    next=RandRange(1000000)+1;betaGwentProgressionSeed=next;\r\n"
           "    if(maximum<=0)return 0;return RandRange(maximum);")


def toc_rows(path):
    with Path(path).open('rb') as stream:
        head = stream.read(32)
        return bytearray(stream.read(struct.unpack_from('<I', head, 16)[0]))


def native_guids():
    """GUIDs of the stock resources, read from the installed 1.32 bundles (or the frozen values)."""
    result = {}
    for name, bundle in NATIVE_BUNDLES.items():
        guid = bytes.fromhex(EXPECTED_GUIDS[name])
        if (GAME / bundle).is_file():
            toc = toc_rows(GAME / bundle)
            rows = [toc[i:i + 320] for i in range(0, len(toc), 320)]
            hit = [bytes(r[256:272]) for r in rows if r[:256].split(b'\0')[0].decode('ascii', 'replace') == name]
            assert hit == [guid], (name, [h.hex() for h in hit])
        result[name] = guid
    return result


def patch_bundle(bundle, native, menu_raw):
    toc = toc_rows(bundle); old_guids = {}; changed = {}
    offsets = sorted(struct.unpack_from('<I', toc, i + 284)[0] for i in range(0, len(toc), 320))
    names = [toc[i:i + 256].split(b'\0')[0].decode('ascii') for i in range(0, len(toc), 320)]
    assert NEW_MENU not in names and NEW_SWF not in names and OLD_MENU in names and OLD_SWF in names
    with bundle.open('r+b') as stream:
        for i in range(0, len(toc), 320):
            row = toc[i:i + 320]; name = names[i // 320]
            if name not in PATHS: continue
            old_guids[name] = bytes(row[256:272])
            new = PATHS[name].encode('ascii'); row[:256] = new + bytes(256 - len(new))
            row[256:272] = native[PATHS[name]]
            if name == OLD_MENU:
                size, packed, offset = struct.unpack_from('<III', row, 276)
                assert size == packed and struct.unpack_from('<I', row, 316)[0] == 0
                following = min(v for v in offsets if v > offset)
                assert offset + len(menu_raw) <= following, 'menu does not fit its slot'
                stream.seek(offset); stream.write(menu_raw + bytes(max(0, size - len(menu_raw))))
                struct.pack_into('<II', row, 276, len(menu_raw), len(menu_raw))
                struct.pack_into('<I', row, 312, zlib.crc32(menu_raw)); changed[name] = len(menu_raw)
            toc[i:i + 320] = row
        stream.seek(32); stream.write(toc)
    return old_guids, changed


def main():
    assert (SRC / ZIP).is_file() and not OUT.exists() and not WORK.exists(), (SRC, OUT, WORK)
    native = native_guids()
    content = WORK / 'content'; content.mkdir(parents=True)
    with zipfile.ZipFile(SRC / ZIP) as z:
        for name in ['blob0.bundle', 'metadata.store', 'dep.cache']:
            with z.open(MOD + name) as src, (content / name).open('wb') as dst: shutil.copyfileobj(src, dst)
        script = z.read(SCRIPT); player = z.read(PLAYER)
    before = {n.replace('\\', '/'): hashlib.sha256(raw).hexdigest() for n, raw in bundle_entries(content / 'blob0.bundle')}
    menu_old = dict(bundle_entries(content / 'blob0.bundle', lambda n: n == OLD_MENU))[OLD_MENU]
    menu_new = menu_import(menu_old, OLD_SWF, NEW_SWF)
    old_guids, changed = patch_bundle(content / 'blob0.bundle', native, menu_new)
    meta = remap_metadata((content / 'metadata.store').read_bytes(), PATHS, changed)
    (content / 'metadata.store').write_bytes(meta)
    cache = bytearray((content / 'dep.cache').read_bytes()); parsed = read_dependency_cache(bytes(cache))
    count, pos = read_vlq(cache, 8)
    for old, new in PATHS.items():
        i = parsed['guids'].index(old_guids[old]); cache[pos + i * 16:pos + (i + 1) * 16] = native[new]
    after = read_dependency_cache(bytes(cache))
    assert all(after[k] == parsed[k] for k in ('first', 'second', 'pool')), 'dependency indices changed'
    swf_index = after['guids'].index(native[NEW_SWF]); k = after['first'][swf_index]; deps = []
    while after['pool'][k]: deps.append(after['pool'][k]); k += 1
    assert len(deps) == 9, deps  # the movie's nine texture pages stay hard dependencies
    (content / 'dep.cache').write_bytes(cache)
    # Bundle check: every payload unchanged except the edited menu, two entries renamed.
    got = {n.replace('\\', '/'): hashlib.sha256(raw).hexdigest() for n, raw in bundle_entries(content / 'blob0.bundle')}
    rename = {o.replace('\\', '/'): n.replace('\\', '/') for o, n in PATHS.items()}
    expect = {rename.get(n, n): h for n, h in before.items()}
    expect[NEW_MENU.replace('\\', '/')] = hashlib.sha256(menu_new).hexdigest()
    assert got == expect, 'bundle payload check'
    checked = Resource(dict(bundle_entries(content / 'blob0.bundle', lambda n: n == NEW_MENU))[NEW_MENU])
    assert checked.string(checked.imports[0][0]) == NEW_SWF
    text = script.decode('utf-16')
    assert text.count(CALL_OLD) == 1 and CALL_NEW not in text, 'keg RequestMenu call'
    script_new = text.replace(CALL_OLD, CALL_NEW).encode('utf-16')
    assert script_new[:2] == script[:2] == b'\xff\xfe'
    (WORK / 'developmentBoardMenu.ws').write_bytes(script_new)
    text = player.decode('utf-16')
    assert text.count(RNG_OLD) == 1 and player[:2] == b'\xff\xfe', 'BetaGwentProgressionPick body'
    (WORK / 'playerWitcher.ws').write_bytes(text.replace(RNG_OLD, RNG_NEW).encode('utf-16'))
    replace = {MOD + 'blob0.bundle': content / 'blob0.bundle', MOD + 'metadata.store': content / 'metadata.store',
               MOD + 'dep.cache': content / 'dep.cache', SCRIPT: WORK / 'developmentBoardMenu.ws',
               PLAYER: WORK / 'playerWitcher.ws'}
    OUT.mkdir(parents=True); report = dict(paths=PATHS, nativeGuids={k: v.hex() for k, v in native.items()},
                                           textureDependencies=len(deps), archives={})
    for name in [ZIP, 'GwentBetaClassic-0.9.0-5.0+-AllLanguages.zip']:
        if name != ZIP:
            shutil.copy2(SRC / name, OUT / name)
        else:
            with zipfile.ZipFile(SRC / name) as src, zipfile.ZipFile(OUT / name, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as dst:
                manifest = json.loads(src.read('manifest-0.9.0.json'))
                for info in src.infolist():
                    if info.filename == 'manifest-0.9.0.json': continue
                    if info.filename in replace:
                        dst.write(replace[info.filename], info.filename); continue
                    with src.open(info) as a, dst.open(info, 'w') as b: shutil.copyfileobj(a, b, 1 << 20)
                for row in manifest['files']:
                    if row['path'] in replace:
                        p = replace[row['path']]; row.update(bytes=p.stat().st_size, sha256=sha(p))
                manifest['classicKegMenu'] = dict(menuName='TestMenu', menu=NEW_MENU, movie=NEW_SWF)
                dst.writestr('manifest-0.9.0.json', json.dumps(manifest, indent=2), zipfile.ZIP_DEFLATED, 6)
            with zipfile.ZipFile(OUT / name) as z:
                assert z.testzip() is None
                rows = {f['path']: f['sha256'] for f in json.loads(z.read('manifest-0.9.0.json'))['files']}
                for arc, p in replace.items():
                    assert rows[arc] == sha(p) and hashlib.sha256(z.read(arc)).hexdigest() == rows[arc], arc
        digest = sha(OUT / name)
        (OUT / (name + '.sha256')).write_text(digest + '  ' + name + '\n', 'ascii')
        report['archives'][name] = dict(sha256=digest, bytes=(OUT / name).stat().st_size)
        print(name, (OUT / name).stat().st_size // (1024 * 1024), 'MB')
    report['installFiles'] = {arc: sha(p) for arc, p in replace.items()}
    (WORK / 'classic132-keg.json').write_text(json.dumps(report, indent=2), 'utf8')
    print('keg menu: TestMenu ->', NEW_MENU, '->', NEW_SWF, '| texture deps', len(deps))


if __name__ == '__main__':
    main()
