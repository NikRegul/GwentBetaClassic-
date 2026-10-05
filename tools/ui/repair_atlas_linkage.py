"""Repair atlas39 DDS names to use the owning native movie's linkage prefix.

Keep raw SWF/ABC, atlas pixel data, board chunks and root properties unchanged.
Only the two atlas ImageInfo filenames and CSwfTexture linkage strings change.
"""
import argparse
import json
import os
import struct
import zlib
from pathlib import Path
from update_board_resource import (
    ROOT, TARGET, validate_resource, unpack_root, movie_parts, require, sha,
    header_crc, validate_image_linkages,
)


def encode_string(value):
    require(len(value) < 128, 'Unsupported linkage string length')
    return bytes([len(value) | 128]) + value


def encode_properties(resource, props):
    out = bytearray(b'\0')
    for name, (kind, value) in props.items():
        out += struct.pack('<HHI', resource.names.index(name), resource.names.index(kind), len(value) + 4) + value
    return bytes(out) + b'\0\0'


def main(apply):
    resource, records = validate_resource(TARGET)
    require(len(resource.exports) == 7, 'Expected atlas39 resource with six textures')
    metadata, gfx, swf = unpack_root(resource)
    root_props, _ = resource.properties_at(resource.exports[0]['data'])
    movie_name = root_props['linkageName'][1][1:]
    require(movie_name.endswith(b'.gfx'), 'Movie linkage must end in .gfx')
    old_name = b'betagwent-card-atlas-v1.dds'
    new_name = movie_name[:-4] + b'_i6.dds'
    prefix, tags, tail = movie_parts(gfx)
    new_tags, changed_infos = [], 0
    for code, payload, raw in tags:
        if code == 1009:
            filename_offset = 11 + payload[10]
            name = payload[filename_offset + 1:]
            require(len(name) == payload[filename_offset], 'Unexpected ImageInfo filename')
            if name == old_name:
                payload = payload[:filename_offset] + bytes([len(new_name)]) + new_name
                raw = struct.pack('<HI', (code << 6) | 63, len(payload)) + payload
                changed_infos += 1
        new_tags.append(raw)
    require(changed_infos == 2, 'Expected exactly two atlas39 image bindings')
    body = prefix + b''.join(new_tags)
    new_gfx = gfx[:4] + struct.pack('<I', len(body) + 8) + zlib.compress(body + tail, 9)
    chunks = [metadata + struct.pack('<I', len(new_gfx)) + new_gfx + struct.pack('<I', len(swf)) + swf]
    changed_textures = []
    for ordinal, texture in enumerate(resource.exports[1:]):
        props, end = resource.properties_at(texture['data'])
        if props['linkageName'][1][1:] == old_name:
            props['linkageName'] = ('String', encode_string(new_name))
            chunks.append(encode_properties(resource, props) + texture['data'][end:])
            changed_textures.append(ordinal)
        else:
            chunks.append(texture['data'])
    require(changed_textures == [2, 5], 'Unexpected atlas texture positions')
    table_offset, count, _ = resource.tables[4]
    out = bytearray(resource.data[:table_offset]) + bytearray(count * 24)
    cursor = table_offset + count * 24
    for index, chunk in enumerate(chunks):
        record = list(records[index])
        record[3], record[4], record[6] = len(chunk), cursor, zlib.crc32(chunk)
        struct.pack_into('<HHIIIII', out, table_offset + index * 24, *record)
        out += chunk
        cursor += len(chunk)
    struct.pack_into('<II', out, 24, len(out), len(out))
    struct.pack_into('<I', out, 40 + 4 * 12 + 8, zlib.crc32(out[table_offset:table_offset + count * 24]))
    struct.pack_into('<I', out, 32, header_crc(out))
    build = ROOT / 'BetaGwent/build/atlas-linkage40'
    build.mkdir(parents=True, exist_ok=True)
    candidate = build / 'betagwent_board.redswf'
    candidate.write_bytes(out)
    checked, _ = validate_resource(candidate)
    validate_image_linkages(checked)
    check_meta, check_gfx, check_swf = unpack_root(checked)
    require(check_meta == metadata and check_swf == swf, 'Root properties/raw SWF changed')
    before = [(c, p) for c, p, _ in tags if c != 1009]
    after = [(c, p) for c, p, _ in movie_parts(check_gfx)[1] if c != 1009]
    require(before == after, 'Non-image native tags/ABC changed')
    for index, (old, new) in enumerate(zip(resource.exports[1:], checked.exports[1:])):
        if index not in changed_textures:
            require(old['data'] == new['data'], 'Board texture changed')
        else:
            _, old_end = resource.properties_at(old['data'])
            _, new_end = checked.properties_at(new['data'])
            require(old['data'][old_end:] == new['data'][new_end:], 'Atlas pixel data changed')
    backup = None
    if apply:
        backups = ROOT / 'BetaGwent/build/resource-backups'
        backups.mkdir(exist_ok=True)
        backup = backups / (sha(resource.data) + '.redswf')
        if not backup.exists():
            backup.write_bytes(resource.data)
        require(backup.read_bytes() == resource.data, 'Backup mismatch')
        require(TARGET.read_bytes() == resource.data, 'Active resource changed during repair')
        pending = TARGET.with_suffix('.redswf.updating')
        with pending.open('xb') as output:
            output.write(out)
            output.flush()
            os.fsync(output.fileno())
        os.replace(pending, TARGET)
        require(TARGET.read_bytes() == out, 'Installed repair mismatch')
    report = dict(target=str(TARGET), source=str(ROOT / 'BetaGwent/ui/build/betagwent_board.swf'),
        sourceSha256=sha(swf), originalSha256=sha(resource.data), updatedSha256=sha(out),
        updatedBytes=len(out), candidate=str(candidate), backup=str(backup) if backup else None,
        applied=apply, movieLinkage=movie_name.decode(), atlasLinkage=new_name.decode(),
        headerTableChunkChecksumsVerified=True, rootPropertiesPreserved=True,
        nativeImageTagsPreserved=False, nativeABCMatchesBuiltSWF=True,
        textureChunksPreserved=4, totalTextureChunks=6, atlasPixelsPreserved=True,
        nativeImageLinkagePrefixVerified=True, nativeRuntimeVerified=False,
        note='Resource-only fix40: atlas DDS filename must carry owning .gfx linkage prefix; scripts remain compile39. Runtime pending.')
    for filename in ('board-resource-update.json', 'board-atlas-linkage40.json'):
        (ROOT / 'docs/evidence' / filename).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    main(parser.parse_args().apply)
