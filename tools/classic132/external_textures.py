"""Split cooked Classic GUI resources without changing GFx or texture chunks.

The Classic CDiskBundle async reader rejects memoryBytes > 0x2000000 even
for an uncompressed bundle. External hard handles keep each request bounded.
Unlike stage96, linkage names and GFx ImageInfo filenames are never rewritten.
"""
import struct
import sys
from pathlib import Path

from formats import Resource, header_crc, require
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ui'))
from cr2w_gui_write109 import Res

LIMIT = 0x2000000


def editable(data):
    raw = bytearray(data)
    struct.pack_into('<I', raw, 4, 164)
    struct.pack_into('<I', raw, 32, header_crc(raw))
    return Res(raw)


def finish(builder):
    raw = bytearray(builder.build())
    struct.pack_into('<I', raw, 4, 163)
    struct.pack_into('<I', raw, 32, header_crc(raw))
    checked = Resource(raw)
    require(all(row[1] == 8192 for row in checked.records), 'Expected cooked exports')
    require(len(raw) <= LIMIT, 'Classic asynchronous resource limit exceeded')
    return bytes(raw)


def split(data, depot_prefix, external_indices=None):
    original = Resource(data)
    require(original.classes[0] == 'CSwfResource' and not original.imports,
            'Expected standalone inline GUI movie')
    require(original.classes[1:] == ['CSwfTexture'] * (len(original.chunks) - 1),
            'Only texture exports may be split')
    require(all(row[1] == 8192 for row in original.records), 'Input must already be cooked')
    props, end = original.properties(original.chunks[0])
    count = len(original.chunks) - 1
    require(count > 0, 'No textures to split')
    selected = set(range(count)) if external_indices is None else set(external_indices)
    require(selected and selected <= set(range(count)), 'Invalid external texture selection')
    builder = editable(data)
    references, pages = [], {}
    inline_records, inline_chunks = [], []
    for i, chunk in enumerate(original.chunks[1:]):
        if i not in selected:
            references.append(len(inline_chunks) + 2)
            inline_records.append(original.records[i + 1].copy())
            inline_chunks.append(chunk)
            continue
        path = depot_prefix + ('_%02d.redswfx' % (i + 1))
        require(len(path.encode('ascii')) < 256, 'Depot path too long')
        page = editable(data)
        page.exports = [original.records[i + 1].copy()]
        page.exports[0][2] = 0  # standalone root, not a child of the movie
        page.payloads = [chunk]
        payload = finish(page)
        checked = Resource(payload)
        require(checked.classes == ['CSwfTexture'] and checked.chunks == [chunk],
                'Standalone texture properties or pixels changed')
        pages[path] = payload
        references.append(-builder.add_import(path, 'CSwfTexture', 0))
    root = bytearray(b'\0')
    changed = 0
    for name, kind, value in props:
        if original.names[name] == 'textures':
            require(original.names[kind] == 'array:2,0,handle:CSwfTexture' and
                    value == struct.pack('<I', count) + b''.join(struct.pack('<i', i + 2) for i in range(count)),
                    'Unexpected inline texture references')
            value = struct.pack('<I', count) + b''.join(struct.pack('<i', v) for v in references)
            changed += 1
        root += struct.pack('<HHI', name, kind, len(value) + 4) + value
    require(changed == 1, 'Expected exactly one texture array')
    root += b'\0\0' + original.chunks[0][end:]
    builder.exports = [original.records[0].copy(), *inline_records]
    builder.payloads = [bytes(root), *inline_chunks]
    movie = finish(builder)
    checked = Resource(movie)
    updated, updated_end = checked.properties(checked.chunks[0])
    require(checked.chunks[0][updated_end:] == original.chunks[0][end:], 'GFx bytes changed')
    require([(n, t, v) for n, t, v in props if original.names[n] != 'textures'] ==
            [(n, t, v) for n, t, v in updated if checked.names[n] != 'textures'],
            'Non-texture movie properties changed')
    require([checked.string(r[0]) for r in checked.imports] == list(pages), 'Import order differs')
    require(checked.chunks[1:] == inline_chunks, 'Inline texture chunks changed')
    return movie, pages
