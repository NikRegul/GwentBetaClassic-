"""Fix10: preserve native inline UI textures, externalize only card atlases."""
import struct

import build_classic_streaming_fix as build
from external_textures import split
from formats import Resource, require
from update_board_resource import movie_parts
from install_native_hd93 import symbols


def split_cards(raw, prefix):
    resource = Resource(raw)
    _, end = resource.properties(resource.chunks[0])
    size = struct.unpack_from('<I', resource.chunks[0], end)[0]
    tags = movie_parts(resource.chunks[0][end + 4:end + 4 + size])[1]
    bindings = symbols(tags)
    selected = set()
    for code, payload, _ in tags:
        if code == 1008:
            character, image, x, y, width, height = struct.unpack('<6H', payload)
            if bindings.get(character, b'').startswith(b'cards-'):
                selected.add(image)
    require(len(selected) == 9, 'Expected nine complete card atlas pages')
    return split(raw, prefix, selected)


def main():
    build.SOURCE = build.ROOT / 'BetaGwent/build/classic081-streaming-fix9/installed-before'
    build.BASE = build.ROOT / 'BetaGwent/build/classic081-inline-ui-fix10'
    build.VERSION = '0.8.1-classic-inline-ui-fix10'
    build.ARCHIVE_NAME = 'GwentBetaClassic-0.8.1-1.32-fix10-InlineUIPatch.zip'
    build.split = split_cards
    build.main()


if __name__ == '__main__':
    main()
