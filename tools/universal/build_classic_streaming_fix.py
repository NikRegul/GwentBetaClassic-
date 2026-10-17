"""Build fix9 from installed fix8: every GUI request <= Classic's 32 MiB cap."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/classic132'))
from formats import Resource, bundle_entries, fnv64, require, sha, write_bundle
from build_resources import read_vlq, vlq
from dependencies import read_dependency_cache
from external_textures import LIMIT, split

GAME = Path('D:/GOG Galaxy/Games/The Witcher 3 Wild Hunt')
SOURCE = GAME / 'Mods/modBetaGwentClassic132'
INSTALLED = SOURCE
BASE = ROOT / 'BetaGwent/build/classic081-streaming-fix9'
VERSION = '0.8.1-classic-streaming-fix9'
ARCHIVE_NAME = 'GwentBetaClassic-0.8.1-1.32-fix9-StreamingPatch.zip'


def metadata(source, bundle, additions):
    require(source[:8] == b'\x03VTM\x06\0\0\0', 'Expected Classic metadata')
    size, pos = read_vlq(source, 16)
    strings = bytearray(source[pos:pos + size]); pos += size
    arrays = []
    for width in (32, 20, 24, 4, 8, 12, 16):
        count, pos = read_vlq(source, pos)
        require(count >= 0 and pos + count * width <= len(source), 'Metadata extent')
        arrays.append([bytearray(source[i:i + width]) for i in range(pos, pos + count * width, width)])
        pos += count * width
    require(pos == len(source) and not arrays[3], 'Unsupported metadata buffers/tail')
    files, entries, bundles, buffers, dirs, init, hashes = arrays
    def text(offset):
        return strings[offset:strings.index(0, offset)].decode('ascii')
    def append(value):
        offset = len(strings); strings.extend(value.encode('ascii') + b'\0'); return offset
    names = {text(struct.unpack_from('<I', row)[0]): fid for fid, row in enumerate(files) if fid}
    def directory_name(i):
        parts = []
        while i:
            off, i = struct.unpack('<2i', dirs[i]); parts.append(text(off))
        return '\\'.join(reversed(parts))
    directory_ids = {directory_name(i): i for i in range(len(dirs))}
    def directory_id(name):
        if name not in directory_ids:
            parent, _, leaf = name.rpartition('\\')
            parent_id = directory_id(parent)
            directory_ids[name] = len(dirs)
            dirs.append(bytearray(struct.pack('<2i', append(leaf), parent_id)))
        return directory_ids[name]
    for name in sorted(additions):
        require(name not in names, 'New path collides with existing resource')
        fid = len(files); names[name] = fid
        files.append(bytearray(struct.pack('<8I', append(name), 0, 0, 0, fid, 0, 0, 0)))
        entries.append(bytearray(20))
        parent, _, leaf = name.rpartition('\\')
        init.append(bytearray(struct.pack('<3i', fid, directory_id(parent), append(leaf))))
        hashes.append(bytearray(struct.pack('<Qq', fnv64(name.encode('ascii')), fid)))
    with bundle.open('rb') as stream:
        header = stream.read(32); toc = stream.read(struct.unpack_from('<I', header, 16)[0])
    maximum = 0
    seen = set()
    for i in range(0, len(toc), 320):
        row = toc[i:i + 320]; name = row[:256].split(b'\0')[0].decode('ascii')
        fid = names[name]; size, packed, offset = struct.unpack_from('<3I', row, 276)
        require(size == packed and struct.unpack_from('<I', row, 316)[0] == 0, 'Uncompressed entries required')
        struct.pack_into('<6I', files[fid], 8, packed, size, fid, 0, 0, 0)
        entries[fid] = bytearray(struct.pack('<5I', fid, 1, offset, packed, 0))
        maximum = max(maximum, size); seen.add(name)
    require(seen == set(names) and len(entries) == len(files), 'Metadata file set differs')
    require(maximum <= LIMIT, 'Resource exceeds native async cap')
    require(len(bundles) == 2, 'Expected one bundle')
    name_offset = struct.unpack_from('<I', bundles[1])[0]
    start = 32 + len(toc)
    bundles[1] = bytearray(struct.pack('<6I', name_offset, 1, len(names), bundle.stat().st_size - start, start, 0))
    hashes.sort(key=lambda r: struct.unpack_from('<Q', r)[0])
    result = bytearray(source[:8] + struct.pack('<2I', maximum, maximum) + vlq(len(strings)) + strings)
    for array in arrays:
        result += vlq(len(array)) + b''.join(array)
    return bytes(result)


def dependency_cache(source, guids, dependencies):
    parsed = read_dependency_cache(source)
    require(not any(parsed['first'] + parsed['second']) and parsed['pool'] == [0],
            'Expected the verified fix8 cache without external dependencies')
    ids = {guid: i for i, guid in enumerate(parsed['guids'])}
    for name in sorted(dependencies['pages']):
        guid = guids[name.replace('\\', '/')]
        require(guid not in ids, 'GUID collision')
        ids[guid] = len(parsed['guids']); parsed['guids'].append(guid)
        parsed['first'].append(0); parsed['second'].append(0)
    for name, pages in dependencies['movies'].items():
        index = ids[guids[name.replace('\\', '/')]]
        parsed['first'][index] = len(parsed['pool'])
        parsed['pool'].extend(ids[guids[p.replace('\\', '/')]] for p in pages)
        parsed['pool'].append(0)  # native zero-terminated GUID-index list
    result = bytearray(b'SPED' + struct.pack('<I', 2))
    for field in ('guids', 'first', 'second', 'pool'):
        values = parsed[field]
        result += vlq(len(values))
        result += b''.join(values) if field == 'guids' else struct.pack('<' + 'I' * len(values), *values)
    require(read_dependency_cache(bytes(result)) == parsed, 'Dependency cache roundtrip')
    return bytes(result)


def main():
    require(not BASE.exists(), 'Keep build artifacts immutable')
    require(json.loads((SOURCE / 'info.json').read_text('utf8'))['version'] == '0.8.1-classic-stock-paths-fix8', 'Expected installed fix8')
    require(sha(SOURCE / 'content/blob0.bundle') == '4d3eb67dbb205b6c91ef5aafe48bd63d4383373d0633aad597539270d4cb5fd4', 'Source bundle differs')
    content = BASE / 'package/Mods/modBetaGwentClassic132/content'
    content.mkdir(parents=True)
    resources = BASE / 'resources'; resources.mkdir()
    with (SOURCE / 'content/blob0.bundle').open('rb') as stream:
        header = stream.read(32); toc = stream.read(struct.unpack_from('<I', header, 16)[0])
    guids = {}
    for i in range(0, len(toc), 320):
        row = toc[i:i + 320]; name = row[:256].split(b'\0')[0].decode('ascii')
        if row[256:272] != bytes(16): guids[name.replace('\\', '/')] = row[256:272]
    files, changes, old_hashes = {}, [], {}
    deps = dict(pages={}, movies={})
    for name, raw in bundle_entries(SOURCE / 'content/blob0.bundle'):
        old_hashes[name] = hashlib.sha256(raw).hexdigest()
        if len(raw) > LIMIT:
            require(name.endswith('.redswf'), 'Unexpected oversized resource')
            prefix = 'betagwent\\classic132textures\\' + name.rsplit('\\', 1)[-1].removesuffix('.redswf')
            movie, pages = split(raw, prefix)
            deps['movies'][name] = list(pages)
            before = Resource(raw)
            changes.append(dict(path=name, beforeBytes=len(raw), afterBytes=len(movie), textures=len(pages),
                                nativeMovieUnchanged=True, textureChunksUnchanged=True,
                                textureChunkHashes=[hashlib.sha256(c).hexdigest() for c in before.chunks[1:]]))
            for path, data in pages.items():
                target = resources / path.replace('\\', '/'); target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
                files[path.replace('\\', '/')] = target; deps['pages'][path] = True
                guids[path.replace('\\', '/')] = hashlib.sha256(b'BetaGwentClassic132:texture:' + path.encode('ascii')).digest()[:16]
            raw = movie
        target = resources / name.replace('\\', '/'); target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
        files[name.replace('\\', '/')] = target
    require(len(changes) == 4 and len(set(guids.values())) == len(guids), 'Unexpected split count or GUID collision')
    entries = write_bundle(files, content / 'blob0.bundle', guids)
    (content / 'metadata.store').write_bytes(metadata((SOURCE / 'content/metadata.store').read_bytes(), content / 'blob0.bundle', deps['pages']))
    (content / 'dep.cache').write_bytes(dependency_cache((SOURCE / 'content/dep.cache').read_bytes(), guids, deps))
    info = json.loads((SOURCE / 'info.json').read_text('utf8'))
    info.update(version=VERSION, classicAsyncLimitBytes=LIMIT, externalTextureResources=True, nativeGameplayVerified=False)
    (content.parent / 'info.json').write_text(json.dumps(info, indent=2), 'utf8')
    changed_names = {r['path'] for r in changes}
    unchanged = 0
    for name, raw in bundle_entries(content / 'blob0.bundle'):
        if name in old_hashes and name not in changed_names:
            require(hashlib.sha256(raw).hexdigest() == old_hashes[name], 'Unrelated payload changed'); unchanged += 1
    require(unchanged == len(old_hashes) - 4, 'Unchanged payload coverage differs')
    report = dict(version=VERSION, sourceBundleSha256=sha(SOURCE / 'content/blob0.bundle'),
                  nativeLimitBytes=LIMIT, maximumResourceBytes=max(r['bytes'] for r in entries),
                  menus=changes, externalTextures=len(deps['pages']), unchangedPayloads=unchanged,
                  nativeGuids={n: v.hex() for n, v in guids.items()}, entries=entries,
                  nativeGameplayVerified=False, gameStarted=False, gameModified=False)
    (BASE / 'verification.json').write_text(json.dumps(report, indent=2), 'utf8')
    install_files = ('content/blob0.bundle', 'content/metadata.store', 'content/dep.cache', 'info.json')
    install_manifest = dict(version=VERSION, sourceVersion=json.loads((INSTALLED / 'info.json').read_text('utf8'))['version'],
                            installedBefore={p: sha(INSTALLED / p) for p in install_files},
                            installFiles={p: sha(content.parent / p) for p in install_files})
    (BASE / 'install-manifest.json').write_text(json.dumps(install_manifest, indent=2), 'utf8')
    archive = ROOT / 'BetaGwent/release' / ARCHIVE_NAME
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as target:
        for file in sorted((BASE / 'package').rglob('*')):
            if file.is_file(): target.write(file, file.relative_to(BASE / 'package').as_posix())
    with zipfile.ZipFile(archive) as target: require(target.testzip() is None, 'ZIP CRC failure')
    (BASE / 'archive.json').write_text(json.dumps(dict(path=str(archive), bytes=archive.stat().st_size, sha256=sha(archive)), indent=2), 'utf8')
    print(json.dumps({k: report[k] for k in ('version', 'maximumResourceBytes', 'externalTextures', 'unchangedPayloads')}, indent=2))


if __name__ == '__main__':
    main()
