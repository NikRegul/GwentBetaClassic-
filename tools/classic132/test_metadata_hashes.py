import struct
import unittest

from formats import classic_metadata_hash_rows


class MetadataHashes(unittest.TestCase):
    def test_negative_source_id_becomes_positive_classic_int64(self):
        source=struct.pack('<QII',0x3143a16874f215f4,232,0xFFFFFFFF)
        self.assertLess(struct.unpack('<Qq',source)[1],0)
        result=classic_metadata_hash_rows([source],353)
        self.assertEqual(struct.unpack('<Qq',result[0]),(0x3143a16874f215f4,232))

    def test_native_positive_rows_are_byte_identical_and_order_preserved(self):
        rows=[struct.pack('<Qq',9,2),struct.pack('<Qq',3,1)]
        self.assertEqual(classic_metadata_hash_rows(rows,3),rows)

    def test_invalid_cross_indices_and_unknown_encoding_rejected(self):
        for file_id,upper in [(0,0),(3,0),(1,1)]:
            with self.subTest(file_id=file_id,upper=upper),self.assertRaises(ValueError):
                classic_metadata_hash_rows([struct.pack('<QII',9,file_id,upper)],3)


if __name__=='__main__':unittest.main()
