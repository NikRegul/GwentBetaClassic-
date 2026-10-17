"""Combine inline UI fix with a native Classic Scaleform DLC registration."""
import json
from pathlib import Path
import shutil
import struct
import sys
import zipfile

import build_classic_streaming_fix as base
from build_resources import vlq
from dependencies import read_dependency_cache
from formats import Resource, bundle_entries, fnv64, header_crc, require, sha, write_bundle
from cr2w_gui_write109 import Res, prop
from install_native_hd93 import string

ROOT = base.ROOT
BUILD = ROOT / 'BetaGwent/build/classic081-native-resources-fix10'
INLINE = ROOT / 'BetaGwent/build/classic081-inline-ui-fix10'
VERSION = '0.8.1-classic-native-resources-fix10'
DLC = 'dlcBetaGwentClassic132Assets'
DLC_PATH = r'dlc\dlcbetagwentclassic132assets\betagwent_gui.reddlc'


def make_definition(template):
    data = bytearray(template)
    struct.pack_into('<I', data, 4, 164); struct.pack_into('<I', data, 32, header_crc(data))
    builder = Res(data)
    require(builder.name_list()[builder.exports[0][0]] == 'CDLCDefinition', 'Expected native DLC definition')
    candidates = [i for i, row in enumerate(builder.exports)
                  if builder.name_list()[row[0]] == 'CR4ScaleformContentDLCMounter']
    require(len(candidates) == 1 and not builder.imports, 'Unexpected native DLC mounter schema')
    name = builder.add_name('betagwent_classic132_gui')
    root = (b'\0' + prop(builder, 'id', 'CName', struct.pack('<H', name)) +
            prop(builder, 'localizedNameKey', 'String', string('Gwent Beta Classic')) +
            prop(builder, 'localizedDescriptionKey', 'String', string('')) +
            prop(builder, 'mounters', 'array:2,0,ptr:IGameplayDLCMounter', struct.pack('<II', 1, 2)) +
            prop(builder, 'visibleInDLCMenu', 'Bool', b'\0') + b'\0\0')
    mounter = b'\0' + prop(builder, 'scaleformDirectoryPath', 'String', string('gameplay\\gui_new\\')) + b'\0\0'
    builder.exports = [builder.exports[0].copy(), builder.exports[candidates[0]].copy()]
    builder.exports[1][2] = 1
    require([r[1] for r in builder.exports] == [8192, 8200], 'Native DLC cooked flags differ')
    builder.payloads = [root, mounter]
    result = bytearray(builder.build())
    struct.pack_into('<I', result, 4, 163); struct.pack_into('<I', result, 32, header_crc(result))
    # Validate exact native table/chunk checksums without widening GUI schemas.
    editable = bytearray(result)
    struct.pack_into('<I', editable, 4, 164); struct.pack_into('<I', editable, 32, header_crc(editable))
    checked = Res(editable)
    require(checked.payloads == [root, mounter] and checked.exports[1][2] == 1, 'DLC payload roundtrip')
    for i, width in enumerate((1, 8, 8, 16, 24)):
        import zlib
        off, count, crc = struct.unpack_from('<III', result, 40 + i * 12)
        require(not count or zlib.crc32(result[off:off + count * width]) == crc, 'DLC table CRC')
    return bytes(result)


def make_metadata(bundle, relative_name):
    with bundle.open('rb') as stream:
        head = stream.read(32); toc = stream.read(struct.unpack_from('<I', head, 16)[0])
    strings = bytearray(b'\0')
    def add(value):
        pos = len(strings); strings.extend(value.encode('ascii') + b'\0'); return pos
    files, entries, dirs, init, hashes = [bytes(32)], [bytes(20)], [bytes(8)], [], []
    dir_ids = {'': 0}
    def directory(path):
        if path not in dir_ids:
            parent, _, leaf = path.rpartition('\\')
            parent_id = directory(parent); dir_ids[path] = len(dirs)
            dirs.append(struct.pack('<2I', add(leaf), parent_id))
        return dir_ids[path]
    maximum = 0
    for pos in range(0, len(toc), 320):
        row = toc[pos:pos + 320]; path = row[:256].split(b'\0')[0].decode('ascii')
        size, packed, offset = struct.unpack_from('<3I', row, 276); fid = len(files)
        require(size == packed and struct.unpack_from('<I', row, 316)[0] == 0, 'Uncompressed DLC expected')
        files.append(struct.pack('<8I', add(path), 0, packed, size, fid, 0, 0, 0))
        entries.append(struct.pack('<5I', fid, 1, offset, packed, 0))
        parent, _, leaf = path.rpartition('\\')
        init.append(struct.pack('<3I', fid, directory(parent), add(leaf)))
        hashes.append(struct.pack('<Qq', fnv64(path.encode('ascii')), fid)); maximum = max(maximum, size)
    require(maximum <= 0x2000000, 'DLC exceeds Classic async cap')
    start = 32 + len(toc)
    bundles = [bytes(24), struct.pack('<6I', add(relative_name), 1, len(files) - 1, bundle.stat().st_size - start, start, 0)]
    hashes.sort(key=lambda r: struct.unpack_from('<Q', r)[0])
    result = bytearray(b'\x03VTM' + struct.pack('<3I', 6, maximum, maximum) + vlq(len(strings)) + strings)
    for array in (files, entries, bundles, [], dirs, init, hashes): result += vlq(len(array)) + b''.join(array)
    return bytes(result)


def main():
    require(not BUILD.exists(), 'Fresh immutable build required')
    source = INLINE / 'package/Mods/modBetaGwentClassic132'
    package = BUILD / 'package'; mod = package / 'Mods/modBetaGwentClassic132'
    shutil.copytree(source, mod)
    info = json.loads((mod / 'info.json').read_text('utf8'))
    info.update(version=VERSION, classicTextureLayout='card-atlases-external-ui-inline', scaleformDLC=DLC)
    (mod / 'info.json').write_text(json.dumps(info, indent=2), 'utf8')
    verification = json.loads((INLINE / 'verification.json').read_text('utf8'))
    verification['version'] = VERSION
    (BUILD / 'verification.json').write_text(json.dumps(verification, indent=2), 'utf8')
    # Keep auxiliary payloads in Mods too. DLC registers native file identities;
    # byte-identical copies avoid altering any existing soft or hard reference.
    dlc_content = package / 'DLC' / DLC / 'content'
    dlc_content.mkdir(parents=True)
    resources = BUILD / 'dlc-resources'; resources.mkdir()
    files, guids, auxiliary = {}, {}, []
    for name, data in bundle_entries(mod / 'content/blob0.bundle'):
        if not name.startswith((r'gameplay\gui_new\swf\betagwentleaders',
                                r'gameplay\gui_new\swf\betagwentleaderintros',
                                r'gameplay\gui_new\swf\betagwenttext')):
            continue
        checked = Resource(data)
        require(checked.classes[0] == 'CSwfResource', 'Expected auxiliary movie')
        path = resources / name.replace('\\', '/'); path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
        normalized = name.replace('\\', '/'); files[normalized] = path
        guids[normalized] = bytes.fromhex(verification['nativeGuids'][normalized])
        auxiliary.append(dict(path=name, sha256=sha(path), bytes=len(data)))
    require(len(auxiliary) == 335, 'Unexpected leader/intro/text movie count')
    template = ROOT / 'BetaGwent/build/classic081-complete-audit/dlc-template.reddlc'
    path = resources / DLC_PATH.replace('\\', '/'); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(make_definition(template.read_bytes()))
    files[DLC_PATH.replace('\\', '/')] = path
    guids[DLC_PATH.replace('\\', '/')] = __import__('hashlib').sha256(DLC_PATH.encode('ascii')).digest()[:16]
    bundle = dlc_content / 'bundles/blob0.bundle'; bundle.parent.mkdir()
    entries = write_bundle(files, bundle, guids)
    (dlc_content / 'metadata.store').write_bytes(make_metadata(bundle, r'bundles\blob0.bundle'))
    identities = [bytes(16)] + [guids[name] for name in sorted(guids)]
    cache = b'SPED' + struct.pack('<I', 2) + vlq(len(identities)) + b''.join(identities)
    cache += vlq(len(identities)) + bytes(4 * len(identities))
    cache += vlq(len(identities)) + bytes(4 * len(identities)) + vlq(1) + bytes(4)
    require(len(read_dependency_cache(cache)['guids']) == len(identities), 'DLC cache mismatch')
    (dlc_content / 'dep.cache').write_bytes(cache)
    report = dict(version=VERSION, dlc=DLC, definitionPath=DLC_PATH,
                  definitionTemplateSha256=sha(template), scaleformDirectoryPath='gameplay\\gui_new\\',
                  assetsIdenticalToMod=True, auxiliary=auxiliary, entries=entries,
                  nativeGuids={n: g.hex() for n, g in guids.items()}, nativeGameplayVerified=False)
    (BUILD / 'dlc-verification.json').write_text(json.dumps(report, indent=2), 'utf8')
    installed = base.GAME / 'Mods/modBetaGwentClassic132'
    names = ['content/blob0.bundle', 'content/metadata.store', 'content/dep.cache', 'info.json']
    manifest = dict(version=VERSION, sourceVersion='0.8.1-classic-streaming-fix9',
                    installedBefore={n: sha(installed / n) for n in names},
                    installFiles={n: sha(mod / n) for n in names},
                    dlc=DLC, dlcFiles={p.relative_to(package / 'DLC' / DLC).as_posix(): sha(p)
                                      for p in (package / 'DLC' / DLC).rglob('*') if p.is_file()})
    (BUILD / 'install-manifest.json').write_text(json.dumps(manifest, indent=2), 'utf8')
    archive = ROOT / 'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix10-NativeResourcesPatch.zip'
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as target:
        for path in sorted(package.rglob('*')):
            if path.is_file(): target.write(path, path.relative_to(package).as_posix())
    with zipfile.ZipFile(archive) as target: require(target.testzip() is None, 'Archive CRC failure')
    (BUILD / 'archive.json').write_text(json.dumps(dict(path=str(archive), sha256=sha(archive), bytes=archive.stat().st_size), indent=2), 'utf8')
    print(json.dumps(dict(version=VERSION, auxiliaryMovies=len(auxiliary), dlcFiles=len(entries), maximumModBytes=verification['maximumResourceBytes']), indent=2))


if __name__ == '__main__':
    main()
