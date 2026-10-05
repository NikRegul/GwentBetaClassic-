"""Replace only the ABC in the already-imported development board resource.

Limited to the observed CR2W v164 layout: one CSwfResource and a bounded
array of inline CSwfTexture chunks, no imports/buffers/embedded resources. The native GFx
image tags, texture chunks, properties and source import identity are kept.
The new raw SWF must differ from the stored raw SWF only in its single ABC.
Default: build and verify a candidate. --apply: backup and atomically install.

CR2W CRC/header layout reference:
https://github.com/WolvenKit/WolvenKit-7/blob/main/WolvenKit.CR2W/CR2W/CR2WFile.cs
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import zlib

from read_gui_resource import GuiResource, ResourceError

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / 'GwentB/myproject1/workspace/betagwent/betagwent_board.redswf'
SOURCE = ROOT / 'BetaGwent/ui/build/betagwent_board.swf'
BUILD = ROOT / 'BetaGwent/build/resource-update'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, reason):
    if not condition:
        raise ResourceError(reason)


def header_crc(data):
    header = bytearray(data[:160])
    struct.pack_into('<I', header, 32, 0xDEADBEEF)
    return zlib.crc32(header)


def validate_resource(path):
    resource = GuiResource(path)
    data = resource.data
    require(struct.unpack_from('<II', data, 24) == (len(data), len(data)), 'Unexpected file/buffer extent')
    require(header_crc(data) == struct.unpack_from('<I', data, 32)[0], 'Invalid header CRC')
    texture_count = len(resource.exports) - 1
    require(1 <= texture_count <= 32 and [item['class'] for item in resource.exports] == ['CSwfResource'] + ['CSwfTexture'] * texture_count,
            'Unexpected resource chunks')
    root_props, _ = resource.properties_at(resource.exports[0]['data'])
    require(root_props['textures'] == ('array:2,0,handle:CSwfTexture',
        struct.pack('<I', texture_count) + b''.join(struct.pack('<I', i + 2) for i in range(texture_count))),
        'Unexpected texture handles')
    require(all(resource.tables[i] == (0, 0, 0) for i in (2, 5, 6, 7, 8, 9)), 'Unsupported auxiliary tables')
    for i, width in ((0, 1), (1, 8), (3, 16), (4, 24)):
        offset, count, checksum = resource.tables[i]
        require(zlib.crc32(data[offset:offset + count * width]) == checksum, 'Invalid table CRC ' + str(i))
    offset, count, _ = resource.tables[4]
    records = [struct.unpack_from('<HHIIIII', data, offset + i * 24) for i in range(count)]
    cursor = offset + count * 24
    for record in records:
        _, flags, _, size, position, template, checksum = record
        require(flags == 0 and template == 0 and position == cursor, 'Non-contiguous or unsupported chunk')
        require(zlib.crc32(data[position:position + size]) == checksum, 'Invalid chunk CRC')
        cursor += size
    require(cursor == len(data), 'Unsupported data after last chunk')
    return resource, records


def movie_parts(movie):
    require(movie[:3] in (b'FWS', b'CWS', b'CFX'), 'Expected SWF or native CFX')
    body = zlib.decompress(movie[8:]) if movie[:3] in (b'CWS',b'CFX') else movie[8:]
    declared = struct.unpack_from('<I', movie, 4)[0]
    require(8 <= declared <= len(body) + 8, 'Invalid movie extent')
    prefix_size = (5 + 4 * (body[0] >> 3) + 7) // 8 + 4
    cursor, tags = prefix_size, []
    while cursor < declared - 8:
        start = cursor
        header = struct.unpack_from('<H', body, cursor)[0]
        cursor += 2
        code, size = header >> 6, header & 63
        if size == 63:
            size = struct.unpack_from('<I', body, cursor)[0]
            cursor += 4
        require(cursor + size <= declared - 8, 'Truncated movie tag')
        payload = body[cursor:cursor + size]
        cursor += size
        tags.append((code, payload, body[start:cursor]))
        if code == 0:
            break
    require(tags and tags[-1][0] == 0 and cursor == declared - 8, 'Unexpected declared movie ending')
    require(sum(code == 82 for code, _, _ in tags) == 1, 'Expected exactly one DoABC')
    return body[:prefix_size], tags, body[cursor:]


def unpack_root(resource):
    chunk = resource.exports[0]['data']
    _, end = resource.properties_at(chunk)
    gfx_size = struct.unpack_from('<I', chunk, end)[0]
    gfx = chunk[end + 4:end + 4 + gfx_size]
    swf_offset = end + 4 + gfx_size
    swf_size = struct.unpack_from('<I', chunk, swf_offset)[0]
    raw = chunk[swf_offset + 4:]
    require(len(gfx) == gfx_size and len(raw) == swf_size, 'Unexpected root buffer layout')
    return chunk[:end], gfx, raw


def validate_image_linkages(resource):
    """Check DDS names resolve through the same owning movie as working boards."""
    root_props, _ = resource.properties_at(resource.exports[0]['data'])
    movie_name = root_props['linkageName'][1][1:]
    require(movie_name.endswith(b'.gfx'), 'Missing native .gfx linkage')
    stem = movie_name[:-4]
    names = []
    for texture in resource.exports[1:]:
        props, _ = resource.properties_at(texture['data'])
        name = props['linkageName'][1][1:]
        require(name.startswith(stem + b'_i') and name.endswith(b'.dds'),
                'DDS linkage does not identify owning .gfx: ' + name.decode())
        require(name[len(stem) + 2:-4].isdigit(), 'Invalid native DDS ordinal')
        names.append(name)
    _, gfx, _ = unpack_root(resource)
    image_names = []
    for code, payload, _ in movie_parts(gfx)[1]:
        if code != 1009:
            continue
        pos = 11 + payload[10]
        require(pos < len(payload) and len(payload[pos + 1:]) == payload[pos], 'Invalid ImageInfo filename')
        image_names.append(payload[pos + 1:])
    require(image_names == names, 'Native image/texture linkage order differs')


def main(apply):
    BUILD.mkdir(parents=True, exist_ok=True)
    resource, records = validate_resource(TARGET)
    validate_image_linkages(resource)
    original = resource.data
    metadata, gfx, stored_swf = unpack_root(resource)
    new_swf = SOURCE.read_bytes()
    raw_prefix, old_tags, old_tail = movie_parts(stored_swf)
    new_prefix, new_tags, new_tail = movie_parts(new_swf)
    native_prefix, native_tags, native_tail = movie_parts(gfx)
    require(stored_swf[:4] == new_swf[:4] and raw_prefix == new_prefix and old_tail == new_tail,
            'Movie version/frame header changed')
    without_abc = lambda tags: [tag for tag in tags if tag[0] != 82]
    require(without_abc(old_tags) == without_abc(new_tags), 'Update changes images or non-ABC tags; use native importer')
    old_abc = next(tag[1] for tag in old_tags if tag[0] == 82)
    new_abc_tag = next(tag for tag in new_tags if tag[0] == 82)
    require(next(tag[1] for tag in native_tags if tag[0] == 82) == old_abc, 'Native/source ABC mismatch')
    native_body = native_prefix + b''.join(new_abc_tag[2] if tag[0] == 82 else tag[2] for tag in native_tags)
    # The native exporter includes an unused allocation tail after End. Preserve
    # those bytes too; the declared movie extent excludes that tail.
    new_gfx = gfx[:4] + struct.pack('<I', len(native_body) + 8) + zlib.compress(native_body + native_tail, 9)
    new_chunk = metadata + struct.pack('<I', len(new_gfx)) + new_gfx + struct.pack('<I', len(new_swf)) + new_swf
    root_record = records[0]
    delta = len(new_chunk) - root_record[3]
    candidate = bytearray(original[:root_record[4]] + new_chunk + original[root_record[4] + root_record[3]:])
    table_offset, table_count, _ = resource.tables[4]
    for i, record in enumerate(records):
        fields = list(record)
        if i == 0:
            fields[3] = len(new_chunk)
            fields[6] = zlib.crc32(new_chunk)
        else:
            fields[4] += delta
        struct.pack_into('<HHIIIII', candidate, table_offset + i * 24, *fields)
    struct.pack_into('<II', candidate, 24, len(candidate), len(candidate))
    struct.pack_into('<I', candidate, 40 + 4 * 12 + 8,
                     zlib.crc32(candidate[table_offset:table_offset + table_count * 24]))
    struct.pack_into('<I', candidate, 32, header_crc(candidate))
    candidate_path = BUILD / 'betagwent_board.redswf'
    candidate_path.write_bytes(candidate)
    checked, _ = validate_resource(candidate_path)
    check_metadata, check_gfx, check_swf = unpack_root(checked)
    _, check_tags, check_tail = movie_parts(check_gfx)
    require(check_metadata == metadata and check_swf == new_swf, 'Root metadata/source not preserved')
    require(without_abc(check_tags) == without_abc(native_tags) and check_tail == native_tail,
            'Native GFx image tags or tail changed')
    require(next(tag[1] for tag in check_tags if tag[0] == 82) == new_abc_tag[1], 'New native ABC mismatch')
    require(all(a['data'] == b['data'] for a, b in zip(resource.exports[1:], checked.exports[1:])),
            'Texture chunks changed')
    native_movie_path = BUILD / 'installed-board.gfx'
    native_movie_path.write_bytes(b'GFX' + check_gfx[3:8] + zlib.decompress(check_gfx[8:])[:struct.unpack_from('<I', check_gfx, 4)[0] - 8])
    backup_path = ROOT / 'BetaGwent/build/resource-backups' / (sha(original) + '.redswf')
    if apply and bytes(candidate) != original:
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        if backup_path.exists():
            require(backup_path.read_bytes() == original, 'Backup collision')
        else:
            with backup_path.open('xb') as backup:
                backup.write(original)
        require(TARGET.read_bytes() == original, 'Project resource changed while preparing update')
        temporary = TARGET.with_suffix('.redswf.updating')
        with temporary.open('xb') as output:
            output.write(candidate)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, TARGET)
        require(TARGET.read_bytes() == candidate, 'Installed resource mismatch')
    report = dict(target=str(TARGET), source=str(SOURCE), sourceSha256=sha(new_swf),
                  originalSha256=sha(original), updatedSha256=sha(candidate), updatedBytes=len(candidate),
                  candidate=str(candidate_path), nativeMovie=str(native_movie_path),
                  backup=str(backup_path) if apply and candidate != original else None,
                  applied=apply, headerTableChunkChecksumsVerified=True,
                  rootPropertiesPreserved=True, nativeImageTagsPreserved=True,
                  textureChunksPreserved=len(resource.exports) - 1, nativeABCMatchesBuiltSWF=True,
                  nativeRuntimeVerified=False,
                  note='File update only. Restart REDkit to discard the cached previous movie; then test bgboard_open().')
    (ROOT / 'docs/evidence/board-resource-update.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    main(args.apply)
