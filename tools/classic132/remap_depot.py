"""Bounded v6 depot-path remapping, preserving file IDs and bundle offsets."""
import struct

from build_resources import read_vlq, vlq
from formats import fnv64, require


def remap_metadata(data, paths, changed_sizes):
    require(data[:8] == b'\x03VTM\x06\0\0\0', 'Classic metadata v6 required')
    size, pos = read_vlq(data, 16)
    strings = bytearray(data[pos:pos + size])
    pos += size
    arrays = []
    for width in (32, 20, 24, 4, 8, 12, 16):
        count, pos = read_vlq(data, pos)
        require(count >= 0 and pos + count * width <= len(data), 'Metadata extent')
        arrays.append([bytearray(data[i:i + width]) for i in range(pos, pos + count * width, width)])
        pos += count * width
    require(pos == len(data) and not arrays[3], 'Metadata buffers/tail')
    files, entries, bundles, buffers, dirs, init, hashes = arrays
    def text(offset):
        return strings[offset:strings.index(0, offset)].decode('ascii')
    def append(value):
        encoded = value.encode('ascii') + b'\0'
        offset = len(strings)
        strings.extend(encoded)
        return offset
    names = {i: text(struct.unpack_from('<I', row)[0]) for i, row in enumerate(files) if i}
    require(set(paths) <= set(names.values()), 'Missing source depot path')
    destinations = [paths.get(n, n) for n in names.values()]
    require(len(set(destinations)) == len(destinations), 'Colliding destination depot path')
    directory_ids = {}
    def directory_name(i):
        parts, seen = [], set()
        while i:
            require(i not in seen and 0 < i < len(dirs), 'Directory cycle/range')
            seen.add(i)
            off, i = struct.unpack('<2i', dirs[i])
            parts.append(text(off))
        return '\\'.join(reversed(parts))
    for i in range(len(dirs)):
        directory_ids[directory_name(i)] = i
    def directory_id(name):
        if name in directory_ids:
            return directory_ids[name]
        parent, _, leaf = name.rpartition('\\')
        parent_id = directory_id(parent)
        i = len(dirs)
        dirs.append(bytearray(struct.pack('<2i', append(leaf), parent_id)))
        directory_ids[name] = i
        return i
    changed_ids = {}
    for fid, old in names.items():
        if old in paths:
            new = paths[old]
            require('/' not in new and new and not new.startswith('\\'), 'Expected relative backslash path')
            struct.pack_into('<I', files[fid], 0, append(new))
            changed_ids[fid] = new
        if old in changed_sizes:
            size = changed_sizes[old]
            require(size > 0 and struct.unpack_from('<I', files[fid], 20)[0] == 0, 'Uncompressed file required')
            struct.pack_into('<2I', files[fid], 8, size, size)
            eid = struct.unpack_from('<I', files[fid], 16)[0]
            require(struct.unpack_from('<I', entries[eid])[0] == fid and
                    struct.unpack_from('<I', entries[eid], 16)[0] == 0, 'Single entry required')
            struct.pack_into('<I', entries[eid], 12, size)
    for row in init:
        fid = struct.unpack_from('<i', row)[0]
        if fid in changed_ids:
            directory, _, leaf = changed_ids[fid].rpartition('\\')
            struct.pack_into('<3i', row, 0, fid, directory_id(directory), append(leaf))
    for row in hashes:
        h, fid = struct.unpack('<Qq', row)
        if fid in changed_ids:
            struct.pack_into('<Q', row, 0, fnv64(changed_ids[fid].encode('ascii')))
    hashes.sort(key=lambda row: struct.unpack_from('<Q', row)[0])
    max_packed = max(struct.unpack_from('<I', row, 8)[0] for row in files)
    max_memory = max(struct.unpack_from('<I', row, 12)[0] for row in files)
    result = bytearray(data[:8] + struct.pack('<2I', max_packed, max_memory) + vlq(len(strings)) + strings)
    for array in arrays:
        result += vlq(len(array)) + b''.join(array)
    return bytes(result)
