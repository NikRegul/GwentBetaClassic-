"""Route the two failed entry movies through existing native Classic paths.

Candidate only. Source movies, Flash code and all texture payloads are unchanged.
Builds in workspace; installation is a separate guarded step, no game launch.
"""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'tools/classic132'), str(ROOT / 'tools/ui')]
from formats import Resource, bundle_entries, header_crc, sha
from build_resources import read_vlq
from dependencies import read_dependency_cache
from remap_depot import remap_metadata
from cr2w_gui_write109 import Res

GAME = Path('D:/GOG Galaxy/Games/The Witcher 3 Wild Hunt')
SOURCE = GAME / 'Mods/modBetaGwentClassic132'
BASE = ROOT / 'BetaGwent/build/classic081-stock-paths-fix8'
VERSION = '0.8.1-classic-stock-paths-fix8'
PATHS = {
    r'betagwent\betagwent_decks.redswf': r'gameplay\gui_new\swf\gwint\deck_builder.redswf',
    r'betagwent\betagwent_npc00.redswf': r'gameplay\gui_new\swf\gwint\gwint_game.redswf',
}
MENUS = {r'gameplay\gui_new\guirsrc\r4deck_builder.menu': r'betagwent\betagwent_decks.redswf',
         r'gameplay\gui_new\guirsrc\r4gwint_game.menu': r'betagwent\betagwent_npc00.redswf'}


def menu_import(data, old, new):
    source = Resource(data)
    assert len(source.imports) == 1 and source.string(source.imports[0][0]) == old
    raw = bytearray(data)
    struct.pack_into('<I', raw, 4, 164)
    struct.pack_into('<I', raw, 32, header_crc(raw))
    edited = Res(raw)
    edited.imports[0][0] = edited.add_string(new)
    result = Resource(edited.build()).classic()
    checked = Resource(result)
    assert checked.chunks == source.chunks and checked.classes == source.classes
    assert checked.string(checked.imports[0][0]) == new
    assert checked.imports[0][1:] == source.imports[0][1:]
    return result


def main():
    assert not BASE.exists(), 'Keep build artifacts immutable'
    assert json.loads((SOURCE / 'info.json').read_text('utf8'))['version'] == '0.8.1-classic-bundle-guids-fix7'
    assert sha(SOURCE / 'content/blob0.bundle') == 'e30126aaa88e827d80e6c285174093a45b0b982ee50e41def124894fa86236d1'
    content = BASE / 'package/Mods/modBetaGwentClassic132/content'
    content.mkdir(parents=True)
    with (SOURCE / 'content/blob0.bundle').open('rb') as stream:
        header = stream.read(32)
        toc = bytearray(stream.read(struct.unpack_from('<I', header, 16)[0]))
    native = {}
    with (GAME / 'content/content0/bundles/r4gui.bundle').open('rb') as stream:
        h = stream.read(32)
        table = stream.read(struct.unpack_from('<I', h, 16)[0])
    for i in range(0, len(table), 320):
        row = table[i:i + 320]
        name = row[:256].split(b'\0')[0].decode('ascii')
        if name in PATHS.values():
            native[name] = row[256:272]
    assert set(native) == set(PATHS.values()) and all(native.values())
    menu_data = dict(bundle_entries(SOURCE / 'content/blob0.bundle', lambda n: n in MENUS))
    replacements = {n: menu_import(raw, MENUS[n], PATHS[MENUS[n]]) for n, raw in menu_data.items()}
    assert set(replacements) == set(MENUS)
    bundle = content / 'blob0.bundle'
    shutil.copy2(SOURCE / 'content/blob0.bundle', bundle)
    changed_sizes, old_guids, changed_toc = {}, {}, []
    offsets = sorted(struct.unpack_from('<I', toc, i + 284)[0] for i in range(0, len(toc), 320))
    with bundle.open('r+b') as stream:
        for i in range(0, len(toc), 320):
            row = toc[i:i + 320]
            name = row[:256].split(b'\0')[0].decode('ascii')
            if name in PATHS:
                new = PATHS[name].encode('ascii')
                old_guids[name] = bytes(row[256:272])
                row[:256] = new + bytes(256 - len(new))
                row[256:272] = native[PATHS[name]]
            if name in replacements:
                raw = replacements[name]
                size, packed, offset = struct.unpack_from('<III', row, 276)
                assert size == packed and struct.unpack_from('<I', row, 316)[0] == 0
                following = min((v for v in offsets if v > offset), default=bundle.stat().st_size)
                assert offset + len(raw) <= following
                stream.seek(offset)
                old = stream.read(size)
                assert old == menu_data[name]
                stream.seek(offset)
                stream.write(raw)
                if len(raw) < size:
                    stream.write(bytes(size - len(raw)))
                struct.pack_into('<II', row, 276, len(raw), len(raw))
                struct.pack_into('<I', row, 312, zlib.crc32(raw))
                changed_sizes[name] = len(raw)
            if row != toc[i:i + 320]:
                changed_toc.append(name)
                toc[i:i + 320] = row
        stream.seek(32)
        stream.write(toc)
    assert set(changed_toc) == set(PATHS) | set(MENUS)
    metadata = remap_metadata((SOURCE / 'content/metadata.store').read_bytes(), PATHS, changed_sizes)
    (content / 'metadata.store').write_bytes(metadata)
    # These GUIDs now identify the existing native resource paths. Preserve
    # every dependency index, pool and unrelated identity byte-for-byte.
    cache = bytearray((SOURCE / 'content/dep.cache').read_bytes())
    count, pos = read_vlq(cache, 8)
    before_cache = read_dependency_cache(bytes(cache))
    for old in PATHS:
        i = before_cache['guids'].index(old_guids[old])
        cache[pos + i * 16:pos + (i + 1) * 16] = native[PATHS[old]]
    after_cache = read_dependency_cache(bytes(cache))
    assert all(after_cache[key] == before_cache[key] for key in ('first', 'second', 'pool'))
    (content / 'dep.cache').write_bytes(cache)
    info = json.loads((SOURCE / 'info.json').read_text('utf8'))
    info.update(version=VERSION, classicStockEntryPaths=True, nativeGameplayVerified=False)
    (content.parent / 'info.json').write_text(json.dumps(info, indent=2), 'utf8')
    old_payloads = {n: hashlib.sha256(raw).hexdigest() for n, raw in bundle_entries(SOURCE / 'content/blob0.bundle')}
    verified = []
    for name, raw in bundle_entries(bundle):
        old = next((o for o, new in PATHS.items() if new == name), name)
        digest = hashlib.sha256(raw).hexdigest()
        if old in replacements:
            assert raw == replacements[old]
        else:
            assert digest == old_payloads[old]
        verified.append(dict(path=name, bytes=len(raw), sha256=digest))
    assert len(verified) == 352
    report = dict(version=VERSION, sourceVersion='0.8.1-classic-bundle-guids-fix7',
                  remappedPaths=PATHS, nativeGuids={p: g.hex() for p, g in native.items()},
                  unchangedPayloads=350, menuDefinitionsPreserved=True,
                  flashCodeTexturesScriptsAudioUnchanged=True, dependencyPoolPreserved=True,
                  gameStarted=False, gameplayVerified=False, files=verified)
    report['installedBefore'] = {n: sha(SOURCE / n) for n in
                                ('content/blob0.bundle', 'content/metadata.store', 'content/dep.cache', 'info.json')}
    report['installFiles'] = {n: sha(content.parent / n) for n in report['installedBefore']}
    archive = ROOT / 'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix8-StockPathsPatch.zip'
    assert not archive.exists()
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted((BASE / 'package').rglob('*')):
            if path.is_file():
                z.write(path, path.relative_to(BASE / 'package').as_posix())
        z.writestr('README_RU.txt', 'Кандидат fix8 для установленного fix7.\n'
                   'Два входных меню направлены на штатные пути Classic.\n'
                   'Содержимое Flash и текстуры сохранены. Игровая проверка ещё необходима.\n'.encode('utf-8-sig'))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name, expected in report['installFiles'].items():
            with z.open('Mods/modBetaGwentClassic132/' + name) as f:
                assert hashlib.file_digest(f, 'sha256').hexdigest() == expected
    report['archive'] = dict(path=str(archive), bytes=archive.stat().st_size, sha256=sha(archive))
    (BASE / 'verification.json').write_text(json.dumps(report, indent=2), 'utf8')
    archive.with_suffix('.zip.sha256').write_text(sha(archive) + '  ' + archive.name + '\n', 'ascii')
    print(json.dumps({k: v for k, v in report.items() if k != 'files'}, indent=2))


if __name__ == '__main__':
    main()
