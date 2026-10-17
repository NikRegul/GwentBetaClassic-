"""Read-only structural audit of the actually installed Classic package."""
from collections import Counter
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib

from build_resources import read_vlq
from dependencies import read_dependency_cache, verify_cache_paths
from formats import Resource, bundle_entries, cook_guid_map, fnv64, sha

ROOT = Path(__file__).resolve().parents[2]
GAME = Path('D:/GOG Galaxy/Games/The Witcher 3 Wild Hunt')
OUT = ROOT / 'BetaGwent/build/classic081-complete-audit'
sys.path.insert(0, str(ROOT / 'tools/ui'))
from update_board_resource import movie_parts


def metadata(path):
    data = path.read_bytes()
    assert data[:8] == b'\x03VTM\x06\0\0\0'
    size, pos = read_vlq(data, 16)
    strings = data[pos:pos + size]
    pos += size
    arrays = []
    for width in (32, 20, 24, 4, 8, 12, 16):
        count, pos = read_vlq(data, pos)
        assert count >= 0 and pos + count * width <= len(data)
        arrays.append([data[i:i + width] for i in range(pos, pos + count * width, width)])
        pos += count * width
    assert pos == len(data)
    def string(offset):
        assert 0 <= offset < len(strings)
        return strings[offset:strings.index(0, offset)].decode('ascii')
    return struct.unpack_from('<2I', data, 8), arrays, string


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mod-root', type=Path, default=GAME / 'Mods/modBetaGwentClassic132')
    parser.add_argument('--script-root', type=Path)
    parser.add_argument('--expected-version', default='0.8.1-classic-bundle-guids-fix7')
    parser.add_argument('--guid-overrides', type=Path)
    parser.add_argument('--out', type=Path, default=OUT / 'installed-audit.json')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    content = args.mod_root / 'content'
    checks, issues = [], []
    def check(label, condition, detail=None):
        record = dict(check=label, passed=bool(condition))
        if detail is not None:
            record['detail'] = detail
        checks.append(record)
        if not condition:
            issues.append(record)
    installed = []
    for path in sorted(content.parent.rglob('*')):
        if path.is_file():
            installed.append(dict(path=path.relative_to(content.parent).as_posix(),
                                  bytes=path.stat().st_size, sha256=sha(path)))
    check('Package version', json.loads((content.parent / 'info.json').read_text('utf-8-sig'))['version'] ==
          args.expected_version)
    check('No other active mod directories', [p.name for p in sorted((GAME / 'Mods').iterdir()) if p.is_dir()] ==
          ['modBetaGwentClassic132'])
    settings = Path.home() / 'Documents/The Witcher 3/mods.settings'
    check('No overriding mods.settings', not settings.exists() or not settings.read_text('utf-8-sig').strip())
    expected = ROOT / 'BetaGwent/build/universal081/classic-prepared/Mods/modBetaGwentClassic132/content/scripts'
    script_root = args.script_root or content / 'scripts'
    actual_scripts = {p.relative_to(script_root).as_posix(): sha(p)
                      for p in script_root.rglob('*.ws')}
    expected_scripts = {p.relative_to(expected).as_posix(): sha(p) for p in expected.rglob('*.ws')}
    check('Every installed script matches prepared inputs', actual_scripts == expected_scripts,
          dict(installed=len(actual_scripts), expected=len(expected_scripts)))
    with (content / 'blob0.bundle').open('rb') as f:
        header = f.read(32)
        toc = f.read(struct.unpack_from('<I', header, 16)[0])
    check('Bundle v3 and declared file size', header[:8] == b'POTATO70' and
          struct.unpack_from('<H', header, 20)[0] == 3 and
          struct.unpack_from('<I', header, 8)[0] == (content / 'blob0.bundle').stat().st_size)
    rows = {}
    for i in range(0, len(toc), 320):
        row = toc[i:i + 320]
        name = row[:256].split(b'\0')[0].decode('ascii')
        assert name not in rows
        rows[name] = row
    sizes, arrays, string = metadata(content / 'metadata.store')
    files, entries, bundles, buffers, dirs, init, hashes = arrays
    check('Metadata dummy records and absence of external buffers',
          files[0] == bytes(32) and entries[0] == bytes(20) and bundles[0] == bytes(24) and not buffers)
    file_paths = {}
    for i, raw in enumerate(files[1:], 1):
        name_off, path_hash, packed, size, first, compression, buffer_id, has_buffer = struct.unpack('<8I', raw)
        name = string(name_off)
        file_paths[i] = name
        assert name in rows
        row = rows[name]
        assert (size, packed) == struct.unpack_from('<II', row, 276)
        assert compression == struct.unpack_from('<I', row, 316)[0]
        assert not buffer_id and not has_buffer
        assert struct.unpack('<5I', entries[first]) == (i, 1, struct.unpack_from('<I', row, 284)[0], packed, 0)
    check('Every metadata file/entry matches bundle size, compression, offset', set(file_paths.values()) == set(rows))
    b = struct.unpack('<6I', bundles[1])
    check('Bundle metadata name, range and group', string(b[0]) == 'blob0.bundle' and b[1:3] == (1, len(rows)) and
          b[3] + b[4] == (content / 'blob0.bundle').stat().st_size and b[4] == 32 + len(toc) and b[5] == 0)
    hash_rows = [struct.unpack('<Qq', h) for h in hashes]
    check('Path hashes are positive IDs, complete, unique and sorted',
          len(hash_rows) == len(rows) and {i for h, i in hash_rows} == set(file_paths) and
          hash_rows == sorted(hash_rows) and
          all(h == fnv64(file_paths[i].encode('ascii')) for h, i in hash_rows))
    def directory(i):
        visited, parts = set(), []
        while i:
            assert i not in visited and 0 < i < len(dirs)
            visited.add(i)
            off, i = struct.unpack('<2i', dirs[i])
            parts.append(string(off))
        return '\\'.join(reversed(parts))
    for raw in init:
        fid, di, no = struct.unpack('<3i', raw)
        prefix = directory(di)
        assert (prefix + '\\' if prefix else '') + string(no) == file_paths[fid]
    check('Directory tree reconstructs every depot path', len(init) == len(rows))
    guids = cook_guid_map(ROOT / 'BetaGwent/build/release202/ru/cooked/cook.db')
    if args.guid_overrides:
        overrides = json.loads(args.guid_overrides.read_text('utf8'))['nativeGuids']
        guids.update({name.replace('\\', '/'): bytes.fromhex(value) for name, value in overrides.items()})
    resource_paths, menus, movies, classes, linkage_issues = [], [], [], Counter(), []
    textures = 0
    payloads = dict(bundle_entries(content / 'blob0.bundle'))
    external_dependencies = {}
    for name, raw in payloads.items():
        # bundle_entries verifies all CRCs, extents and payload overlaps.
        if not raw.startswith(b'CR2W'):
            assert name.endswith(('.xml', '.csv'))
            continue
        resource_paths.append(name)
        resource = Resource(raw)
        assert struct.unpack_from('<I', raw, 4)[0] == 163
        assert all(row[1] == 8192 for row in resource.records)
        assert rows[name][256:272] == guids[name.replace('\\', '/')]
        classes.update(resource.classes)
        for cls, chunk in zip(resource.classes, resource.chunks):
            if cls != 'CSwfTexture':
                continue
            _, texture_end = resource.properties(chunk)
            tail_tex = chunk[texture_end:]
            unknown, mips, width, height, pitch, size = struct.unpack_from('<6I', tail_tex)
            assert unknown == 0 and mips == 1 and width and height and pitch
            assert len(tail_tex) == size + 28 and tail_tex[24:28] == b'\x10\0\0\0'
            textures += 1
        if resource.classes[0] == 'CMenuResource':
            props, end = resource.properties(resource.chunks[0])
            menus.append(dict(path=name, properties={resource.names[n]: value.hex() for n, t, value in props},
                              imports=[resource.string(x[0]) for x in resource.imports]))
            assert all(resource.string(x[0]) in rows for x in resource.imports)
        if resource.classes[0] != 'CSwfResource':
            continue
        props, end = resource.properties(resource.chunks[0])
        properties = {resource.names[n]: value for n, t, value in props}
        length = struct.unpack_from('<I', resource.chunks[0], end)[0]
        movie = resource.chunks[0][end + 4:end + 4 + length]
        assert resource.chunks[0][end + 4 + length:] == bytes(4)
        prefix, tags, tail = movie_parts(movie)
        attrs = next(p for c, p, r in tags if c == 69)
        assert struct.unpack('<I', attrs)[0] & 8  # AS3, not AS2
        texture_names = []
        texture_array = properties.get('textures', bytes(4))
        count = struct.unpack_from('<I', texture_array)[0]
        handles = struct.unpack_from('<' + 'i' * count, texture_array, 4)
        assert len(texture_array) == 4 + 4 * count
        external_dependencies[name] = []
        for handle in handles:
            if handle > 0:
                assert resource.classes[handle - 1] == 'CSwfTexture'
                texture_resource, chunk = resource, resource.chunks[handle - 1]
            else:
                assert handle < 0
                imported = resource.imports[-handle - 1]
                assert resource.names[imported[1]] == 'CSwfTexture' and imported[2] == 0
                path = resource.string(imported[0])
                texture_resource = Resource(payloads[path])
                assert texture_resource.classes == ['CSwfTexture']
                assert texture_resource.records[0][2] == 0
                chunk = texture_resource.chunks[0]
                external_dependencies[name].append(path)
            props, end = texture_resource.properties(chunk)
            properties_tex = {texture_resource.names[n]: v for n, t, v in props}
            texture_names.append(properties_tex['linkageName'][1:])
        image_names = []
        for kind, payload, encoded in tags:
            if kind == 1009:
                p = 11 + payload[10]
                assert len(payload[p + 1:]) == payload[p]
                image_names.append(payload[p + 1:])
        if image_names != texture_names:
            linkage_issues.append(name)
        movies.append(dict(path=name, bytes=len(raw), movieBytes=len(movie), movieVersion=movie[3],
                           fileAttributes=attrs.hex(), textures=len(texture_names),
                           linkageName=properties['linkageName'][1:].decode('ascii'),
                           tags=dict(Counter(str(c) for c, p, r in tags))))
    check('All resource CRCs, versions, cooked chunks, GUIDs and movie extents', True,
          dict(resources=len(resource_paths), textures=textures, classes=dict(classes)))
    check('Every GFx image resolves to corresponding inline or external texture', not linkage_issues, linkage_issues)
    parsed_cache = read_dependency_cache((content / 'dep.cache').read_bytes())
    registered = set(parsed_cache['guids'])
    assert all(guids[path.replace('\\', '/')] in registered for path in resource_paths)
    cache = dict(version=2, guidCount=len(registered), verifiedResourcePaths=len(resource_paths),
                 dependencyPoolEntries=len(parsed_cache['pool']))
    check('Dependency cache covers all shipped CR2W GUIDs', True, cache)
    guid_indices = {value: i for i, value in enumerate(parsed_cache['guids'])}
    for movie_path, paths in external_dependencies.items():
        if not paths:
            continue
        index = guid_indices[guids[movie_path.replace('\\', '/')]]
        offset = parsed_cache['first'][index]
        assert offset > 0
        expected_indices = [guid_indices[guids[p.replace('\\', '/')]] for p in paths]
        assert parsed_cache['pool'][offset:offset + len(paths) + 1] == expected_indices + [0]
    check('External texture hard-dependency lists cover every imported texture', True,
          dict(movies=sum(bool(p) for p in external_dependencies.values()),
               textures=sum(map(len, external_dependencies.values()))))
    max_size = max(struct.unpack_from('<I', r, 276)[0] for r in rows.values())
    check('Metadata allocation maxima cover every bundle entry', sizes == (max_size, max_size), sizes)
    check('Every resource fits Classic CDiskBundle async 32 MiB limit', max_size <= 0x2000000, max_size)
    report = dict(createdUtc=datetime.now(timezone.utc).isoformat(), game=str(GAME),
                  auditedMod=str(content.parent), scriptRoot=str(script_root),
                  executableSha256=sha(GAME / 'bin/x64/witcher3.exe'), installed=installed,
                  checks=checks, structuralIssues=issues, menus=menus, movies=movies,
                  runtimeVerified=False, gameStarted=False, gameModified=False,
                  unresolved=['Actual GFx file-open paths and result', 'Suppressed native Scaleform errors',
                              'Classic async-loader behavior for 62.9 MiB GUI',
                              'Real document-class construction and bridge binding',
                              'Editor exit and NPC match after successful UI registration'])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
    print(json.dumps(dict(checks=len(checks), failed=len(issues), bundleFiles=len(rows),
                         resourceCount=len(resource_paths), movies=len(movies), textures=textures,
                         largestResourceMiB=max_size / 1024**2, output=str(args.out)), indent=2))
    if issues:
        raise RuntimeError('Structural audit failed: ' + ', '.join(x['check'] for x in issues))


if __name__ == '__main__':
    main()
