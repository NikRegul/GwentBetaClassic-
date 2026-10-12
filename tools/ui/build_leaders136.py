"""Build exactly 21 lazy native leader movies from the reviewed 0.6.0 input set.

One small AS movie is compiled once; each card receives its own native BC1 atlas,
unique GFx image linkage and resource CRC. Main-menu texture budgets are unchanged.
No release archive is built here. Input sources and their hashes are recorded.
"""
import argparse, hashlib, io, json, shutil, struct, subprocess, zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image, ImageChops, ImageStat, ImageFile
from update_board_resource import validate_resource, validate_image_linkages, unpack_root, movie_parts, header_crc
from install_native_hd93 import properties, string, tag
from externalize_gui96 import rebuild

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'BetaGwent/build/leaders136'
DEPOT = 'gameplay/gui_new/swf/betagwentleaders'
TARGET = WORK / 'resources' / DEPOT
sha = lambda data: hashlib.sha256(data).hexdigest()
# Pillow's BC encoder writes the whole atlas in one call. Its default 64 KiB
# output buffer crashes on this atlas; provision the complete uncompressed size.
ImageFile.MAXBLOCK = max(ImageFile.MAXBLOCK, 2048*1560*4)


def compile_template(atlas, movie_source=None):
    WORK.mkdir(parents=True, exist_ok=True)
    atlas.save(WORK / 'atlas.png')
    shutil.copyfile(movie_source or Path(__file__).parent / 'leaders060/BetaLeaderMovie.as', WORK / 'BetaLeaderMovie.as')
    java = Path(r'C:\Program Files\Microsoft\jdk-11.0.12.7-hotspot\bin\java.exe')
    swf = WORK / 'premium.swf'
    command = [str(java), '-Xmx1g', '-jar', str(ROOT/'tools/vendor/apache-royale-0.9.12/royale-asjs/lib/mxmlc.jar'),
               '-load-config='+str(ROOT/'BetaGwent/ui/board-config.xml'), '-source-path='+str(WORK),
               '-source-path+='+str(ROOT/'BetaGwent/ui/src'),
               '-output='+str(swf), str(WORK/'BetaLeaderMovie.as')]
    with (WORK/'compile.log').open('wb') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    exporter = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\tools\GFx4\gfxexport_mult4fix.exe')
    with (WORK/'export.log').open('wb') as log:
        subprocess.run([str(exporter), '-i', 'DDS', '-quick', '-d1', '-o', str(WORK), '-d', str(WORK), str(swf)],
                       stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    gfx = (WORK/'premium.gfx').read_bytes()
    if gfx[:3] == b'GFX': gfx = b'FWS'+gfx[3:]
    prefix, tags, tail = movie_parts(gfx)
    images = [payload for code,payload,_ in tags if code == 1009]
    width,height=atlas.size
    if not images or any(struct.unpack('<HH',p[6:10]) != (width,height) for p in images):
        raise ValueError('Unexpected template image dimensions')
    # The exporter emits duplicate aliases for an embedded BitmapAsset. Bind
    # every original character ID to one shared native texture, as board menus do.
    info = struct.pack('<5H',0,9,14,width,height)+images[-1][10:]
    body = prefix+tag(1009,info)
    for code,payload,raw in tags:
        if code == 1009:
            cid = struct.unpack_from('<H',payload)[0]
            raw = tag(1008,struct.pack('<6H',cid,0,0,0,width,height))
        body += raw
    return b'FWS'+gfx[3:4]+struct.pack('<I',len(body)+8)+body+tail


def native_movie(art, atlas, template, resource, root_props, texture_props, import_tag, dds=None, portrait=(256,312)):
    dds = dds or (ROOT/'BetaGwent/build/release060-preparation/leaders'/(art+'.dds')).read_bytes()
    width,height=atlas.size
    if len(dds) != 128+width*height//2 or dds[84:88] != b'DXT1': raise ValueError('BC1 atlas layout differs')
    prefix, tags, tail = movie_parts(template)
    linkage = 'leader_'+art+'_i1.dds'
    chunks = [import_tag]
    for code, payload, raw in tags:
        if code == 1000: continue
        if code == 1009:
            end = 11+payload[10]
            payload = payload[:end]+bytes([len(linkage)])+linkage.encode('ascii')
            raw = tag(code, payload)
        chunks.append(raw)
    body = prefix+b''.join(chunks)
    gfx = b'CFX'+template[3:4]+struct.pack('<I',len(body)+8)+zlib.compress(body+tail,9)
    props = dict(root_props)
    props['importFile'] = ('String',string('generated/leaders/'+art+'.swf'))
    props['importFileTimeStamp'] = ('CDateTime',bytes(8))
    header,_ = resource.properties_at(props['header'][1])
    for key,value in (('frameWidth',portrait[0]),('width',portrait[0]),('frameHeight',portrait[1]),('height',portrait[1]),('frameRate',30)):
        header[key] = ('Float',struct.pack('<f',value))
    props['header'] = ('SSwfHeaderInfo',properties(resource,header))
    props['imageImportOptions'] = ('String',string('DDS -d1c -quick'))
    props['linkageName'] = ('String', string('leader_'+art+'.gfx'))
    props['textures'] = ('array:2,0,handle:CSwfTexture', struct.pack('<II',1,2))
    root = properties(resource,props)+struct.pack('<I',len(gfx))+gfx+struct.pack('<I',0)
    props = dict(texture_props)
    props['linkageName'] = ('String', string(linkage))
    props['width'] = ('Uint32',struct.pack('<I',width)); props['height'] = ('Uint32',struct.pack('<I',height))
    props['compression'] = ('ETextureCompression',struct.pack('<H',resource.names.index('TCM_DXTNoAlpha')))
    props['textureGroup'] = ('CName',struct.pack('<H',resource.names.index('GUIWithoutAlpha')))
    pixels = struct.pack('<6I',0,1,width,height,width*2,len(dds)-128)+dds[128:]+struct.pack('<I',0)
    result = bytearray(rebuild(resource,[('CSwfResource',root),('CSwfTexture',properties(resource,props)+pixels)]))
    table=struct.unpack_from('<I',result,88)[0]
    struct.pack_into('<I',result,table+24+4,1) # inline texture belongs to root export
    struct.pack_into('<I',result,96,zlib.crc32(result[table:table+48]))
    struct.pack_into('<I',result,32,header_crc(result))
    path = TARGET / (art+'.redswf');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(result)
    checked,_ = validate_resource(path);validate_image_linkages(checked)
    if unpack_root(checked)[1] != gfx: raise ValueError('Native movie roundtrip differs')
    return dict(path=DEPOT+'/'+path.name,bytes=len(result),sha256=sha(result),pixelSha256=sha(dds[128:]))



def main():
    preparation=ROOT/'BetaGwent/build/release060-preparation/leaders'
    manifest=json.loads((preparation/'manifest.json').read_text('utf8'))
    bindings=json.loads((preparation/'BetaGwentLeaderCatalog.json').read_text('utf8'))
    cards=json.loads((ROOT/'data/beta924/duel/slice.json').read_text('utf8'))['cards']
    expected={str(c['templateId']) for c in cards if int(c['fields']['Tier'])==1}
    assert len(bindings)==21 and set(bindings)==expected
    arts=sorted(set(bindings.values()))
    first=Image.open(preparation/(arts[0]+'.dds')).convert('RGB')
    template=compile_template(first)
    resource,_=validate_resource(ROOT/'GwentB/myproject1/workspace/betagwent/betagwent_board.redswf')
    root_props,_=resource.properties_at(resource.exports[0]['data'])
    texture_props,_=resource.properties_at(resource.exports[1]['data'])
    import_tag=next(raw for code,p,raw in movie_parts(unpack_root(resource)[1])[1] if code==1000)
    results={}
    for art in arts:
        atlas=Image.open(preparation/(art+'.dds')).convert('RGB')
        assert atlas.size==(2048,1560)
        results[art]=native_movie(art,atlas,template,resource,root_props,texture_props,import_tag)
    assert {p.stem for p in TARGET.glob('*.redswf')}==set(arts),'stale non-leader resources'
    rows=','.join(json.dumps(k)+':'+json.dumps(v) for k,v in sorted(bindings.items()))
    source='package { public class BetaGwentLeaderCatalog { private static const ARTS:Object={'+rows+'}; public static function path(id:int):String { var art:String=ARTS[String(id)];return art?"swf/betagwentleaders/"+art+".swf":null; } } }\n'
    (ROOT/'BetaGwent/ui/src/BetaGwentLeaderCatalog.as').write_text(source,'utf8')
    report=dict(stage=136,bindings=bindings,resources=results,preparationSha256=sha((preparation/'manifest.json').read_bytes()),frames=40,fps=12,maxActivePreviews=1,maxBoardMovies=3,maxActiveMovies=4,nativeRuntimeVerified=False)
    report['sources']={p:sha((ROOT/p).read_bytes()) for p in ['tools/ui/build_leaders136.py','tools/ui/leaders060/BetaLeaderMovie.as','BetaGwent/ui/src/BetaGwentLeaderCatalog.as']}
    (ROOT/'docs/evidence/leaders136.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print('PASS: 21 native leader portraits; bytes:',sum(v['bytes'] for v in results.values()),flush=True)

if __name__=='__main__':main()
