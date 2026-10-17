"""Regression checks for the retail Classic GUI texture payload layout."""
import struct
import unittest

from formats import classic_texture_tail


class TextureCookingTests(unittest.TestCase):
    def test_moves_pixels_to_resident_mip_without_changing_them(self):
        pixels=bytes(range(256))*2
        header=struct.pack('<6I',0,1,32,16,128,len(pixels))
        cooked=classic_texture_tail(header+pixels+b'\0'*4)
        self.assertEqual(cooked[:24],header)
        self.assertEqual(struct.unpack_from('<HH',cooked,24),(16,0))
        self.assertEqual(cooked[28:],pixels)

    def test_rejects_unknown_layouts_and_truncated_pixels(self):
        valid=struct.pack('<6I',0,1,4,4,16,16)+bytes(range(16))+b'\0'*4
        for tail in (valid[:-1],valid+b'\0',valid[:-4]+b'\1\0\0\0',
                     valid[:4]+struct.pack('<I',2)+valid[8:]):
            with self.subTest(tail=tail):
                with self.assertRaises(ValueError):classic_texture_tail(tail)


if __name__=='__main__':unittest.main()
