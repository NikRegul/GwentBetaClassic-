import struct
import unittest

from build_resources import read_vlq, vlq
from formats import fnv64
from remap_depot import remap_metadata


def fixture():
    strings = bytearray(b'\0blob0.bundle\0old\0old\\a.redswf\0old\\b.redswf\0a.redswf\0b.redswf\0')
    def off(value):
        return strings.index(value.encode() + b'\0')
    paths = [r'old\a.redswf', r'old\b.redswf']
    arrays = [[bytes(32)], [bytes(20)], [bytes(24)], [],
              [bytes(8), struct.pack('<2i', off('old'), 0)], [], []]
    arrays[2].append(struct.pack('<6I', off('blob0.bundle'), 1, 2, 9000, 672, 0))
    for i, name in enumerate(paths, 1):
        arrays[0].append(struct.pack('<8I', off(name), 0, i, i, i, 0, 0, 0))
        arrays[1].append(struct.pack('<5I', i, 1, i * 4096, i, 0))
        arrays[5].append(struct.pack('<3i', i, 1, off(name.split('\\')[-1])))
        arrays[6].append(struct.pack('<Qq', fnv64(name.encode()), i))
    arrays[6].sort(key=lambda row: struct.unpack_from('<Q', row)[0])
    result = b'\x03VTM' + struct.pack('<3I', 6, 2, 2) + vlq(len(strings)) + strings
    return result + b''.join(vlq(len(a)) + b''.join(a) for a in arrays)


def parse(data):
    size, pos = read_vlq(data, 16)
    strings = data[pos:pos + size]
    pos += size
    arrays = []
    for width in (32, 20, 24, 4, 8, 12, 16):
        count, pos = read_vlq(data, pos)
        arrays.append([data[i:i + width] for i in range(pos, pos + count * width, width)])
        pos += count * width
    assert pos == len(data)
    return strings, arrays


class RemapDepot(unittest.TestCase):
    def test_noop_is_byte_identical(self):
        data = fixture()
        self.assertEqual(remap_metadata(data, {}, {}), data)

    def test_new_nested_path_keeps_file_id_offset_and_unrelated_entry(self):
        data = fixture()
        target = r'gameplay\gui_new\swf\gwint\deck_builder.redswf'
        result = remap_metadata(data, {r'old\a.redswf': target}, {r'old\a.redswf': 23})
        strings, arrays = parse(result)
        old_s, old_a = parse(data)
        self.assertEqual(arrays[0][2], old_a[0][2])
        self.assertEqual(arrays[1][2], old_a[1][2])
        self.assertEqual(arrays[2], old_a[2])
        self.assertEqual(struct.unpack('<5I', arrays[1][1]), (1, 1, 4096, 23, 0))
        self.assertEqual(struct.unpack_from('<2I', result, 8), (23, 23))
        paths = {}
        for raw in arrays[5]:
            fid, di, no = struct.unpack('<3i', raw)
            parts = [strings[no:strings.index(0, no)].decode()]
            while di:
                no, di = struct.unpack('<2i', arrays[4][di])
                parts.append(strings[no:strings.index(0, no)].decode())
            paths[fid] = '\\'.join(reversed(parts))
        self.assertEqual(paths, {1: target, 2: r'old\b.redswf'})
        hashes = [struct.unpack('<Qq', r) for r in arrays[6]]
        self.assertEqual(hashes, sorted(hashes))
        self.assertIn((fnv64(target.encode()), 1), hashes)

    def test_collisions_and_missing_sources_fail_before_output(self):
        for mapping in ({r'old\a.redswf': r'old\b.redswf'}, {r'absent\a.redswf': r'new\a.redswf'}):
            with self.assertRaises(ValueError):
                remap_metadata(fixture(), mapping, {})


if __name__ == '__main__':
    unittest.main()
