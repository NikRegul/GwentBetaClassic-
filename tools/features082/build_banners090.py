"""0.9.0 resource candidate: Beta big-card faction banners as lazy native GFx pages.

Same ImageInfo/SubImage layout as tools/ui/build_leaders136.py: one tiny AS
movie compiled by mxmlc, with its bitmap aliases bound directly to one native
CR2W CSwfTexture. Banners need alpha: TCM_DXTAlpha / GUIWithAlpha, DXT5 pixels
from extract_banners090.py (original Beta meshes and texture atlas).
Classic: Resource.classic() cooks each texture (flags 8192, resident mip, v163).
The four menus and their frozen textures are not touched.

Output: BetaGwent/build/banners090/{nextgen,classic}/resources/<DEPOT>/*.redswf
"""
from pathlib import Path
import argparse, hashlib, json, shutil, struct, subprocess, sys, zlib
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'tools/ui'), str(ROOT / 'tools/classic132')]
from PIL import Image
from update_board_resource import validate_resource, validate_image_linkages, unpack_root, movie_parts, header_crc
from install_native_hd93 import properties, string, tag
from externalize_gui96 import rebuild
import formats

INPUT = ROOT / 'BetaGwent/build/banners090-seamfix-input'
WORK = ROOT / 'BetaGwent/build/banners090-native'
DEPOT = 'gameplay/gui_new/swf/betagwentbanners'
TEMPLATE = ROOT / 'GwentB/myproject1/workspace/betagwent/betagwent_board.redswf'
CLASSIC_LIMIT = 0x2000000
MOVIE = '''package
{
    import flash.display.Sprite;
    // Lazy banner page: shows its one native image at (0,0); no bitmap access.
    [SWF(width="%d",height="%d",frameRate="30",backgroundColor="#000000")]
    public class BetaLeaderMovie extends Sprite
    {
        [Embed(source="atlas.png",compression="true",quality="90")]
        private static var Atlas:Class;
        public function BetaLeaderMovie(){mouseEnabled=false;mouseChildren=false;addChild(new Atlas());}
    }
}
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def compile_page(size):
    """Compile a JPEG placeholder understood by the real GFx 4 exporter."""
    folder = WORK / 'template'; folder.mkdir(parents=True)
    Image.new('RGB', size, (127,127,127)).save(folder/'atlas.png')
    (folder/'BetaLeaderMovie.as').write_text(MOVIE % size, 'utf8')
    java = Path(r'C:\Program Files\Microsoft\jdk-11.0.12.7-hotspot\bin\java.exe')
    swf = folder/'premium.swf'
    command = [str(java), '-Xmx1g', '-jar', str(ROOT/'tools/vendor/apache-royale-0.9.12/royale-asjs/lib/mxmlc.jar'),
               '-load-config='+str(ROOT/'BetaGwent/ui/board-config.xml'), '-source-path='+str(folder),
               '-source-path+='+str(ROOT/'BetaGwent/ui/src'), '-output='+str(swf), str(folder/'BetaLeaderMovie.as')]
    with (folder/'compile.log').open('wb') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    return swf


def export_page(swf, key, size):
    # The SDK cannot decode PNG-in-DefineBitsJPEG2 from the old template.
    # Its JPEG placeholder is replaced by the original BC3 pixels below.
    # Export every filename so each movie has its own real ExporterInfo.
    folder = WORK / 'sdk' / key; folder.mkdir(parents=True)
    source = folder / (key + '.swf'); shutil.copy2(swf, source)
    exporter = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\tools\GFx4\gfxexport_mult4fix.exe')
    command = [str(exporter), '-i', 'DDS', '-quick', '-d5', '-lwr', '-o', str(folder), '-d', str(folder), str(source)]
    with (folder/'export.log').open('wb') as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
    assert result.returncode == 0, (key, result.returncode)
    data = (folder/(key.lower()+'.gfx')).read_bytes()
    if data[:3] == b'GFX':data = b'FWS'+data[3:]
    prefix, tags, tail = movie_parts(data)
    images = [p for c,p,r in tags if c == 1009]
    assert images and images[-1][10], 'SDK bound bitmap export name required'
    info_tag = next(p for c,p,r in tags if c == 1000)
    assert key.lower().encode('ascii') in info_tag.lower() and b'betagwent-board' not in info_tag
    assert not any(c == 65 for c,p,r in tags), 'SDK must strip ScriptLimits'
    width,height = size
    assert all(struct.unpack_from('<2H',p,6) == size for p in images)
    info = struct.pack('<5H',0,9,14,width,height)+images[-1][10:]
    # Same order as every working page (menus, leader and language pages):
    # ExporterInfo (1000) first, then the external ImageInfo (1009).
    assert tags[0][0] == 1000, 'SDK movie must start with ExporterInfo'
    body = prefix
    for code,payload,raw in tags:
        if code == 1009:
            raw = tag(1008, struct.pack('<6H',struct.unpack_from('<H',payload)[0],0,0,0,width,height))
        body += raw
        if code == 1000:
            body += tag(1009,info)
    return b'FWS'+data[3:4]+struct.pack('<I',len(body)+8)+body+tail


def pad_dds(dds, source, target):
    # Pad BC3 block rows without recompressing any of the original pixels.
    sw, sh = source; width, height = target
    assert sw % 4 == sh % 4 == 0 and width >= sw and height >= sh
    assert dds[84:88] == b'DXT5' and len(dds) == 128 + sw * sh
    header = bytearray(dds[:128])
    struct.pack_into('<III', header, 12, height, width, width * height)
    pixels = bytearray(width * height)
    for row in range(sh // 4):
        pixels[row * width * 4:row * width * 4 + sw * 4] = dds[128 + row * sw * 4:128 + (row + 1) * sw * 4]
    return bytes(header + pixels)


def native_banner(key, size, template, resource, root_props, texture_props, import_tag, dds):
    width, height = size
    if len(dds) != 128 + width * height or dds[84:88] != b'DXT5':
        raise ValueError('BC3 (DXT5) banner layout differs: ' + key)
    prefix, tags, tail = movie_parts(template)
    linkage = 'banner_' + key.lower() + '_i1.dds'
    chunks = []
    for code, payload, raw in tags:
        if code == 1009:
            end = 11 + payload[10]
            payload = payload[:end] + bytes([len(linkage)]) + linkage.encode('ascii')
            raw = tag(code, payload)
        chunks.append(raw)
    body = prefix + b''.join(chunks)
    gfx = b'CFX' + template[3:4] + struct.pack('<I', len(body) + 8) + zlib.compress(body + tail, 9)
    props = dict(root_props)
    props['importFile'] = ('String', string('generated/banners/' + key + '.swf'))
    props['importFileTimeStamp'] = ('CDateTime', bytes(8))
    header, _ = resource.properties_at(props['header'][1])
    for name, value in (('frameWidth', width), ('width', width), ('frameHeight', height), ('height', height), ('frameRate', 30)):
        header[name] = ('Float', struct.pack('<f', value))
    props['header'] = ('SSwfHeaderInfo', properties(resource, header))
    props['imageImportOptions'] = ('String', string('DDS -d5 -quick'))
    props['linkageName'] = ('String', string('banner_' + key.lower() + '.gfx'))
    props['textures'] = ('array:2,0,handle:CSwfTexture', struct.pack('<II', 1, 2))
    root = properties(resource, props) + struct.pack('<I', len(gfx)) + gfx + struct.pack('<I', 0)
    props = dict(texture_props)
    props['linkageName'] = ('String', string(linkage))
    props['width'] = ('Uint32', struct.pack('<I', width)); props['height'] = ('Uint32', struct.pack('<I', height))
    props['compression'] = ('ETextureCompression', struct.pack('<H', resource.names.index('TCM_DXTAlpha')))
    props['textureGroup'] = ('CName', struct.pack('<H', resource.names.index('GUIWithAlpha')))
    # SMipData: dims, BC3 pitch (16 bytes per 4x4 block = width*4 per block row), size.
    pixels = struct.pack('<6I', 0, 1, width, height, width * 4, len(dds) - 128) + dds[128:] + struct.pack('<I', 0)
    result = bytearray(rebuild(resource, [('CSwfResource', root), ('CSwfTexture', properties(resource, props) + pixels)]))
    table = struct.unpack_from('<I', result, 88)[0]
    struct.pack_into('<I', result, table + 24 + 4, 1)  # inline texture belongs to the root export
    struct.pack_into('<I', result, 96, zlib.crc32(result[table:table + 48]))
    struct.pack_into('<I', result, 32, header_crc(result))
    return bytes(result), gfx


def main():
    global WORK, INPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=WORK)
    parser.add_argument('--input', type=Path, default=INPUT)
    args = parser.parse_args(); WORK = args.out.resolve()
    INPUT = args.input.resolve()
    assert WORK.is_relative_to((ROOT / 'BetaGwent/build').resolve())
    assert not WORK.exists(), 'Fresh output folder required: ' + str(WORK)
    meta = json.loads((INPUT / 'banners.json').read_text('utf8'))
    source_size = tuple(meta['canvas']); keys = sorted(meta['banners'])
    size = tuple(1 << (n - 1).bit_length() for n in source_size)
    source = Image.open(INPUT / (keys[0] + '.png')).convert('RGBA')
    assert source.size == source_size
    compiled = compile_page(size)
    resource, _ = validate_resource(TEMPLATE)
    root_props, _ = resource.properties_at(resource.exports[0]['data'])
    texture_props, _ = resource.properties_at(resource.exports[1]['data'])
    assert 'TCM_DXTAlpha' in resource.names and 'GUIWithAlpha' in resource.names
    import_tag = next(raw for code, p, raw in movie_parts(unpack_root(resource)[1])[1] if code == 1000)
    report = dict(stage='0.9.0-banners', canvas=size, sourceCanvas=source_size, depot=DEPOT, banners={}, nativeRuntimeVerified=False)
    for key in keys:
        template = export_page(compiled, key, size)
        png = (INPUT / (key + '.png')).read_bytes()
        assert sha(png) == meta['banners'][key]['sha256'], key
        original_dds = (INPUT / (key + '.dds')).read_bytes()
        dds = pad_dds(original_dds, source_size, size)
        ng, gfx = native_banner(key, size, template, resource, root_props, texture_props, import_tag, dds)
        filename = key.lower() + '.redswf'
        path = WORK / 'nextgen/resources' / DEPOT / filename; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(ng)
        checked, _ = validate_resource(path); validate_image_linkages(checked)
        if unpack_root(checked)[1] != gfx:
            raise ValueError('Native movie roundtrip differs: ' + key)
        classic = formats.Resource(ng).classic()
        assert len(classic) <= CLASSIC_LIMIT and len(ng) <= CLASSIC_LIMIT
        cpath = WORK / 'classic/resources' / DEPOT / filename; cpath.parent.mkdir(parents=True, exist_ok=True)
        cpath.write_bytes(classic)
        formats.Resource(classic)  # structural re-read (CRC, cooked flags)
        report['banners'][key] = dict(file=filename,nextgen=dict(bytes=len(ng), sha256=sha(ng)), classic=dict(bytes=len(classic), sha256=sha(classic)),
                                      pixelsSha256=sha(dds[128:]), placement={k: meta['banners'][key][k] for k in ('x', 'y', 'w', 'h', 'px')})
        print(key, len(ng), len(classic), flush=True)
    (WORK / 'banners-report.json').write_text(json.dumps(report, indent=2), 'utf8')
    print('PASS: %d native banner pages per platform (in-game unverified)' % len(keys))


if __name__ == '__main__':
    main()
