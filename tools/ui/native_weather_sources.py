"""Read-only extraction of TW3 Gwent's own weather texture sprites.

They share spare cells in the existing board atlas, so no new native texture
schema, game asset patch, or world particle emitter is needed.
"""
from pathlib import Path
import hashlib
import io
import json
import struct
from PIL import Image
from read_gui_resource import GuiResource

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\r4data\gameplay\gui_new\swf\gwint\gwint_game.redswf')

def extract():
    resource = GuiResource(SOURCE)
    textures = {}
    # Coordinates refer to the native packed images, not a screenshot.
    regions = [
        (-1, 6, (0, 0, 480, 260), 'fog-soft'),
        (-2, 3, (0, 0, 128, 128), 'fog-cloud'),
        (-3, 5, (70, 380, 380, 488), 'frost-left'),
        (-4, 5, (380, 380, 690, 488), 'frost-middle'),
        (-5, 5, (690, 380, 1000, 488), 'frost-right'),
        (-6, 8, (0, 0, 256, 180), 'rain-left'),
        (-7, 8, (256, 0, 512, 180), 'rain-right'),
        (-8, 6, (0, 535, 240, 735), 'frost-crystals'),
    ]
    output = ROOT / 'BetaGwent/ui/assets/weather'
    output.mkdir(parents=True, exist_ok=True)
    entries = []
    for ident, index, bounds, name in regions:
        chunk = resource.exports[index]['data']
        if index not in textures:
            props, end = resource.properties_at(chunk)
            width = struct.unpack('<I', props['width'][1])[0]
            height = struct.unpack('<I', props['height'][1])[0]
            marker, levels, w, h, stride, size = struct.unpack_from('<6I', chunk, end)
            if (marker, levels, w, h, stride, size) != (0, 1, width, height, width * 4, width * height):
                raise ValueError('Unexpected native DXT5 texture layout')
            header = bytearray(128)
            header[:4] = b'DDS '
            struct.pack_into('<7I', header, 4, 124, 0x81007, height, width, size, 0, 1)
            struct.pack_into('<II4s', header, 76, 32, 4, b'DXT5')
            struct.pack_into('<I', header, 108, 0x1000)
            textures[index] = Image.open(io.BytesIO(bytes(header) + chunk[end + 24:end + 24 + size])).convert('RGBA')
        image = textures[index].crop(bounds).resize((128, 180), Image.Resampling.LANCZOS)
        target = output / (name + '.png')
        image.save(target)
        entries.append(dict(atlasId=ident, name=name, textureIndex=index, crop=list(bounds),
                            textureSha256=hashlib.sha256(chunk).hexdigest(), thumbnail=str(target),
                            thumbnailSha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    report = dict(source=str(SOURCE), sourceSha256=hashlib.sha256(resource.data).hexdigest(),
                  sprites=entries, sourceUnchanged=SOURCE.read_bytes() == resource.data,
                  policy='Native TW3 Gwent texture sprites; local UI animation, not world w2p emitters.')
    (ROOT / 'docs/evidence/native-weather79e.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    return entries
