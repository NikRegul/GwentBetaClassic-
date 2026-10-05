"""Validate the installed board update and reject damaged CR2W candidates."""
from pathlib import Path
import struct
import tempfile
import unittest

from update_board_resource import (TARGET, SOURCE, ROOT, header_crc, movie_parts,
                                   unpack_root, validate_resource, ResourceError)


class ResourceUpdateChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resource, cls.records = validate_resource(TARGET)
        cls.original, _ = validate_resource(ROOT / 'BetaGwent/build/resource-backups/715dd11924b17af9af615f835683bed1e27a6f28c50f10b868950786c92f1c62.redswf')

    def damaged(self, mutate):
        data = bytearray(self.resource.data)
        mutate(data)
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as directory:
            path = Path(directory) / 'damaged.redswf'
            path.write_bytes(data)
            with self.assertRaises(ResourceError):
                validate_resource(path)

    def test_installed_code_matches_source_and_preserves_native_images(self):
        props, movie, raw = unpack_root(self.resource)
        old_props, old_movie, _ = unpack_root(self.original)
        self.assertEqual(SOURCE.read_bytes(), raw)
        self.assertEqual(old_props, props)
        _, native, tail = movie_parts(movie)
        _, old_native, old_tail = movie_parts(old_movie)
        _, source, _ = movie_parts(raw)
        abc = lambda tags: next(payload for code, payload, _ in tags if code == 82)
        self.assertEqual(abc(native), abc(source))
        self.assertNotEqual(abc(old_native), abc(native))
        self.assertEqual([tag for tag in native if tag[0] != 82],
                         [tag for tag in old_native if tag[0] != 82])
        self.assertEqual(old_tail, tail)
        self.assertEqual([chunk['data'] for chunk in self.original.exports[1:]],
                         [chunk['data'] for chunk in self.resource.exports[1:]])

    def test_header_corruption_is_rejected(self):
        self.damaged(lambda data: data.__setitem__(12, data[12] ^ 1))

    def test_texture_corruption_is_rejected(self):
        position = self.records[1][4] + self.records[1][3] - 1
        self.damaged(lambda data: data.__setitem__(position, data[position] ^ 1))

    def test_root_corruption_is_rejected(self):
        position = self.records[0][4] + self.records[0][3] - 1
        self.damaged(lambda data: data.__setitem__(position, data[position] ^ 1))

    def test_table_corruption_is_rejected_even_with_valid_header(self):
        def mutate(data):
            position = self.resource.tables[4][0] + 20
            data[position] ^= 1
            struct.pack_into('<I', data, 32, header_crc(data))
        self.damaged(mutate)


if __name__ == '__main__':
    unittest.main()
