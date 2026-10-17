"""Verify the Classic Scaleform DLC container without starting the game."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib

from audit_installed_pipeline import metadata
from dependencies import read_dependency_cache
from formats import Resource, bundle_entries, fnv64, header_crc, sha
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ui'))
from cr2w_gui_write109 import Res


def audit(content, report_path):
    expected = json.loads(report_path.read_text('utf8'))
    bundle = content / 'bundles/blob0.bundle'
    payloads = dict(bundle_entries(bundle))
    with bundle.open('rb') as stream:
        head = stream.read(32); toc = stream.read(struct.unpack_from('<I', head, 16)[0])
    rows = {toc[i:i+256].split(b'\0')[0].decode(): toc[i:i+320] for i in range(0, len(toc), 320)}
    assert len(rows) == len(payloads) == 336
    sizes, arrays, text = metadata(content / 'metadata.store')
    files, entries, bundles, buffers, dirs, init, hashes = arrays
    assert not buffers and len(files) == len(entries) == 337 and len(bundles) == 2
    names = {}
    for fid, row in enumerate(files[1:], 1):
        name_offset, _, packed, size, first, compression, buffer_id, has_buffer = struct.unpack('<8I', row)
        path = text(name_offset); names[fid] = path; physical = rows[path]
        assert (size, packed) == struct.unpack_from('<II', physical, 276)
        assert size == packed and not compression and not buffer_id and not has_buffer
        assert struct.unpack('<5I', entries[first]) == (fid, 1, struct.unpack_from('<I', physical, 284)[0], packed, 0)
        assert physical[256:272].hex() == expected['nativeGuids'][path.replace('\\', '/')]
    bundle_row = struct.unpack('<6I', bundles[1])
    assert text(bundle_row[0]) == r'bundles\blob0.bundle' and bundle_row[1:3] == (1, 336)
    assert bundle_row[3] + bundle_row[4] == bundle.stat().st_size
    assert bundle_row[4] == 32 + len(toc) and bundle_row[5] == 0
    def directory(i):
        parts, seen = [], set()
        while i:
            assert i not in seen; seen.add(i)
            off, i = struct.unpack('<II', dirs[i]); parts.append(text(off))
        return '\\'.join(reversed(parts))
    assert len(init) == len(hashes) == 336
    for row in init:
        fid, di, leaf = struct.unpack('<3I', row)
        parent = directory(di)
        assert (parent + '\\' if parent else '') + text(leaf) == names[fid]
    values = [struct.unpack('<Qq', row) for row in hashes]
    assert values == sorted(values) and {fid for _, fid in values} == set(names)
    assert all(h == fnv64(names[fid].encode('ascii')) for h, fid in values)
    cache = read_dependency_cache((content / 'dep.cache').read_bytes())
    assert not any(cache['first'] + cache['second']) and cache['pool'] == [0]
    assert set(cache['guids']) == {bytes(16)} | {bytes.fromhex(g) for g in expected['nativeGuids'].values()}
    assert sizes == (max(map(len, payloads.values())),) * 2 and sizes[0] <= 0x2000000
    for record in expected['auxiliary']:
        data = payloads[record['path']]
        assert hashlib.sha256(data).hexdigest() == record['sha256']
        resource = Resource(data)
        assert resource.classes[0] == 'CSwfResource'
        assert all(row[1] == 8192 for row in resource.records)
    data = payloads[expected['definitionPath']]
    assert struct.unpack_from('<I', data, 4)[0] == 163 and header_crc(data) == struct.unpack_from('<I', data, 32)[0]
    for i, width in enumerate((1, 8, 8, 16, 24)):
        off, count, crc = struct.unpack_from('<III', data, 40 + i * 12)
        assert not count or zlib.crc32(data[off:off + count * width]) == crc
    edit = bytearray(data); struct.pack_into('<I', edit, 4, 164); struct.pack_into('<I', edit, 32, header_crc(edit))
    definition = Res(edit); types = definition.name_list()
    assert [types[row[0]] for row in definition.exports] == ['CDLCDefinition', 'CR4ScaleformContentDLCMounter']
    assert [(row[1], row[2]) for row in definition.exports] == [(8192, 0), (8200, 1)]
    helper = Resource.__new__(Resource); helper.names = types
    root, end = helper.properties(definition.payloads[0]); assert end == len(definition.payloads[0])
    props = {types[n]: (types[t], v) for n, t, v in root}
    assert props['mounters'] == ('array:2,0,ptr:IGameplayDLCMounter', struct.pack('<II', 1, 2))
    assert props['visibleInDLCMenu'] == ('Bool', b'\0')
    child, end = helper.properties(definition.payloads[1]); assert end == len(definition.payloads[1]) and len(child) == 1
    n, t, value = child[0]
    assert types[n] == 'scaleformDirectoryPath' and types[t] == 'String'
    assert value[1:].decode() == expected['scaleformDirectoryPath'] and value[0] == len(value[1:]) | 128
    for row, payload in zip(definition.exports, definition.payloads):
        assert row[6] == zlib.crc32(payload)
    return dict(passed=True, bundleFiles=336, auxiliaryMovies=335, definitions=1,
                maximumResourceBytes=sizes[0], allMoviePayloadsPreserved=True,
                nativeMounterSchemaVerified=True, bundleSha256=sha(bundle), nativeGameplayVerified=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--content', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.content, args.report)
    args.out.write_text(json.dumps(result, indent=2), 'utf8')
    print(json.dumps(result, indent=2))
