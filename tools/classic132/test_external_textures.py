import struct
import unittest

from build_resources import strip_menu_authoring
from external_textures import editable, finish, split
from formats import Resource
from cr2w_gui_write109 import prop
from test_shipping import fixture


def movie():
    cooked = Resource(strip_menu_authoring(fixture())).classic()
    before = Resource(cooked)
    builder = editable(cooked)
    _, end = before.properties(before.chunks[0])
    builder.payloads[0] = b'\0' + prop(builder, 'textures', 'array:2,0,handle:CSwfTexture',
                                     struct.pack('<II', 1, 2)) + b'\0\0' + before.chunks[0][end:]
    builder.exports[1][2] = 1
    return finish(builder)


class ExternalTexturesTests(unittest.TestCase):
    def test_movie_and_texture_survive_external_reference_roundtrip(self):
        source = Resource(movie())
        data, pages = split(source.data, r'betagwent\classic132textures\test')
        after = Resource(data)
        self.assertEqual(after.classes, ['CSwfResource'])
        properties, end = after.properties(after.chunks[0])
        _, old_end = source.properties(source.chunks[0])
        self.assertEqual(after.chunks[0][end:], source.chunks[0][old_end:])
        self.assertEqual(properties[0][2], struct.pack('<Ii', 1, -1))
        path = next(iter(pages))
        self.assertEqual(after.string(after.imports[0][0]), path)
        self.assertEqual(after.names[after.imports[0][1]], 'CSwfTexture')
        self.assertEqual(after.imports[0][2], 0)
        texture = Resource(pages[path])
        self.assertEqual(texture.classes, ['CSwfTexture'])
        self.assertEqual(texture.records[0][2], 0)
        self.assertEqual(texture.chunks, source.chunks[1:])
        self.assertTrue(all(r[1] == 8192 for r in texture.records + after.records))

    def test_invalid_inline_texture_reference_is_rejected(self):
        builder = editable(movie())
        builder.payloads[0] = builder.payloads[0].replace(struct.pack('<II', 1, 2), struct.pack('<II', 1, 99), 1)
        with self.assertRaisesRegex(ValueError, 'Unexpected inline texture references'):
            split(finish(builder), r'betagwent\classic132textures\test')

    def test_already_externalized_movie_is_rejected(self):
        data, _ = split(movie(), r'betagwent\classic132textures\test')
        with self.assertRaisesRegex(ValueError, 'standalone inline'):
            split(data, r'betagwent\classic132textures\test')

    def test_mixed_inline_external_handles_preserve_both_textures(self):
        builder = editable(movie())
        original = Resource(movie())
        _, end = original.properties(original.chunks[0])
        builder.payloads[0] = b'\0' + prop(builder, 'textures', 'array:2,0,handle:CSwfTexture',
                                         struct.pack('<III', 2, 2, 3)) + b'\0\0' + original.chunks[0][end:]
        builder.exports.append(builder.exports[1].copy())
        builder.payloads.append(builder.payloads[1])
        before = Resource(finish(builder))
        movie_data, pages = split(before.data, r'betagwent\classic132textures\mixed', {0})
        after = Resource(movie_data)
        self.assertEqual(after.classes, ['CSwfResource', 'CSwfTexture'])
        props, _ = after.properties(after.chunks[0])
        self.assertEqual(props[0][2], struct.pack('<Iii', 2, -1, 2))
        self.assertEqual(after.chunks[1:], before.chunks[2:])
        self.assertEqual(Resource(next(iter(pages.values()))).chunks, before.chunks[1:2])


if __name__ == '__main__':
    unittest.main()
