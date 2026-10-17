import struct
import unittest

from build_resources import vlq
from dependencies import read_dependency_cache


def fixture(first=(0,1),second=(0,0),pool=(0,1,1)):
    arrays=[([bytes(16),bytes([1])*16],16),
            ([struct.pack('<I',x) for x in first],4),
            ([struct.pack('<I',x) for x in second],4),
            ([struct.pack('<I',x) for x in pool],4)]
    return b'SPED'+struct.pack('<I',2)+b''.join(vlq(len(rows))+b''.join(rows) for rows,_ in arrays)


class Dependencies(unittest.TestCase):
    def test_reads_guid_table_and_both_reference_tables(self):
        parsed=read_dependency_cache(fixture())
        self.assertEqual(len(parsed['guids']),2)
        self.assertEqual(parsed['first'],[0,1])
        self.assertEqual(parsed['second'],[0,0])
        self.assertEqual(parsed['pool'],[0,1,1])

    def test_rejects_unknown_versions_truncation_and_extra_bytes(self):
        good=fixture()
        for bad in (good[:4]+struct.pack('<I',3)+good[8:],good[:-1],good+b'\0',good[:8]):
            with self.subTest(data=bad),self.assertRaises(ValueError):read_dependency_cache(bad)

    def test_rejects_mismatched_parallel_table_and_out_of_range_reference(self):
        for bad in (fixture(first=(0,)),fixture(first=(0,10)),fixture(pool=())):
            with self.subTest(data=bad),self.assertRaises(ValueError):read_dependency_cache(bad)


if __name__=='__main__':unittest.main()
