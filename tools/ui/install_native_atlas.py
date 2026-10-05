"""Add or replace the card atlas using the observed native DDS/SubImage schema.

Only workspace resource is changed, with backup. Existing four board texture
chunks and import/header metadata are preserved. Does not run REDkit UI.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import os
import struct
import zlib
from PIL import Image
from update_board_resource import validate_resource, validate_image_linkages, unpack_root, movie_parts, header_crc, require, TARGET, SOURCE, ROOT

BUILD = ROOT / 'BetaGwent/build/native-atlas-resource'

def sha(data): return hashlib.sha256(data).hexdigest()
def tag(code,payload):return struct.pack('<HI',(code<<6)|63,len(payload))+payload
def string(value):
    encoded=value.encode('ascii');require(len(encoded)<128,'Unsupported ASCII string length')
    return bytes([len(encoded)|128])+encoded
def properties(resource,props):
    result=bytearray(b'\0')
    for name,(kind,value) in props.items():
        result+=struct.pack('<HHI',resource.names.index(name),resource.names.index(kind),len(value)+4)+value
    return bytes(result)+b'\0\0'
def symbols(tags):
    result={}
    for code,p,_ in tags:
        if code!=76:continue
        count=struct.unpack_from('<H',p)[0];pos=2
        for _ in range(count):
            character=struct.unpack_from('<H',p,pos)[0];pos+=2;end=p.index(0,pos)
            result[character]=p[pos:end];pos=end+1
    return result

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true')
parser.add_argument('--entry',choices=['BetaGwentBoard','DeckBuilder','GwintGame'],default='BetaGwentBoard');args=parser.parse_args()
entry_stem={'BetaGwentBoard':'betagwent_board','DeckBuilder':'betagwent_decks','GwintGame':'betagwent_npc00'}[args.entry]
base_target=TARGET
TARGET=TARGET.with_name(entry_stem+'.redswf');SOURCE=SOURCE.with_name(entry_stem+'.swf')
if args.entry!='BetaGwentBoard' and not TARGET.exists():
    require(args.apply,'Create dedicated resource with --apply')
    TARGET.write_bytes(base_target.read_bytes())
BUILD.mkdir(parents=True,exist_ok=True)
r,records=validate_resource(TARGET)
require(len(r.exports) in (5,7),'Expected four boards with optional two atlas bindings')
updating_atlas=len(r.exports)==7
if updating_atlas: validate_image_linkages(r)
art_manifest=json.loads((ROOT/'docs/evidence/card-art-build.json').read_text(encoding='utf-8'))
atlas_width,atlas_height=art_manifest.get('atlasSize',[768,360])
require(128 <= atlas_width <= 4096 and atlas_width % 128 == 0 and 360 <= atlas_height <= 4096 and atlas_height % 180 == 0,'Unsupported atlas extent')
board_indices=(1,2,4,5) if updating_atlas else (1,2,3,4)
metadata,old_gfx,old_swf=unpack_root(r)
old_prefix,old_tags,_=movie_parts(old_swf)
native_prefix,native_tags,native_tail=movie_parts(old_gfx)
new_swf=SOURCE.read_bytes();new_prefix,new_tags,new_tail=movie_parts(new_swf)
require(new_prefix==old_prefix==native_prefix and not new_tail,'Frame header changed')
old_images={sha(p[2:]):p for code,p,_ in old_tags if code==35}
board_dims={}
for texture in [r.exports[i] for i in board_indices]:
    props,end=r.properties_at(texture['data'])
    width=struct.unpack('<I',props['width'][1])[0];height=struct.unpack('<I',props['height'][1])[0]
    filename=props['linkageName'][1][1:]
    board_dims[(width,height)]=(filename,texture['data'])
require(set(board_dims)=={(4096,1820),(3804,1820)},'Unexpected board dimensions')
old_import=next(raw for code,p,raw in native_tags if code==1000)
image_header=next(p[2:6] for code,p,_ in native_tags if code==1009)
require(image_header==struct.pack('<HH',9,14),'Unexpected DDS image header')
names=symbols(new_tags);infos=[];replacements={};atlas_ids=[]
root_props,_=r.properties_at(r.exports[0]['data'])
movie_name=root_props['linkageName'][1][1:]
require(movie_name.endswith(b'.gfx'),'Native movie linkage missing')
old_stem=movie_name[:-4]
if args.entry!='BetaGwentBoard':
    # Distinct movie identity avoids native movie-cache collisions between the
    # practice, library, and NPC roots. Embedded DDS pixel data stays identical.
    movie_name=entry_stem.replace('_','-',1).encode()+old_stem[15:]+b'.gfx'
    require(len(movie_name)==len(old_stem)+4,'Unexpected native identity length')
    board_dims={dims:(name.replace(old_stem,movie_name[:-4],1),chunk) for dims,(name,chunk) in board_dims.items()}
atlas_name=movie_name[:-4]+b'_i6.dds'
for code,p,raw in new_tags:
    if code!=35:continue
    cid,jpeg_length=struct.unpack_from('<HI',p)
    with Image.open(io.BytesIO(p[6:6+jpeg_length])) as im: width,height=im.size
    physical=((width+3)//4*4,(height+3)//4*4)
    if physical==(atlas_width,atlas_height):filename=atlas_name;atlas_ids.append(cid)
    else:
        require(sha(p[2:]) in old_images,'Board image changed')
        require(physical in board_dims,'Unknown native image');filename=board_dims[physical][0]
    export=names.get(cid,b'');require(len(export)<256 and len(filename)<256,'GFx string too long')
    image_id=len(infos)
    payload=struct.pack('<H',image_id)+image_header+struct.pack('<HH',*physical)+bytes([len(export)])+export+bytes([len(filename)])+filename
    infos.append(tag(1009,payload))
    replacements[cid]=tag(1008,struct.pack('<6H',cid,image_id,0,0,width,height))
require(len(infos)==6 and len(atlas_ids)==2,'Expected four board images and two atlas bindings')
native_body=native_prefix+old_import+b''.join(infos)
for code,p,raw in new_tags:
    if code==65:continue  # exporter removes ScriptLimits in the observed native movie
    native_body+=replacements[struct.unpack_from('<H',p)[0]] if code==35 else raw
new_gfx=old_gfx[:4]+struct.pack('<I',len(native_body)+8)+zlib.compress(native_body+native_tail,9)
props,_=r.properties_at(r.exports[0]['data'])
props['textures']=('array:2,0,handle:CSwfTexture',struct.pack('<7I',6,2,3,4,5,6,7))
props['linkageName']=('String',string(movie_name.decode()))
new_metadata=properties(r,props)
for key in props:
    if key not in ('textures','linkageName'): require(props[key]==r.properties_at(r.exports[0]['data'])[0][key],'Root metadata changed')
root_chunk=new_metadata+struct.pack('<I',len(new_gfx))+new_gfx+struct.pack('<I',len(new_swf))+new_swf
dds_files=list((ROOT/('BetaGwent/ui/build/native-atlas'+('' if args.entry=='BetaGwentBoard' else '-'+args.entry))).glob('*.dds'))
atlas_files=[]
for path in dds_files:
    data=path.read_bytes()
    if data[:4]==b'DDS ' and struct.unpack_from('<II',data,12)==(atlas_height,atlas_width): atlas_files.append((path,data))
require(len(atlas_files)==2,'Expected exactly two freshly exported atlas DDS aliases')
require(atlas_files[0][1]==atlas_files[1][1],'DDS atlas aliases differ')
dds_path,dds=atlas_files[0]
require(dds[84:88]==b'DXT5' and len(dds)==128+atlas_width*atlas_height,'Unexpected atlas DDS payload')
texture_props,_=r.properties_at(r.exports[1]['data'])
texture_props['width']=('Uint32',struct.pack('<I',atlas_width));texture_props['height']=('Uint32',struct.pack('<I',atlas_height))
texture_props['linkageName']=('String',string(atlas_name.decode()))
atlas_chunk=properties(r,texture_props)+struct.pack('<6I',0,1,atlas_width,atlas_height,atlas_width*4,len(dds)-128)+dds[128:]+struct.pack('<I',0)
# Match ImageInfo order, including the duplicate embed bindings. Original board
# chunks remain byte-identical and in their original relative order.
original_boards=[r.exports[i]['data'] for i in board_indices]
boards=[chunk.replace(old_stem,movie_name[:-4],1) for chunk in original_boards]
chunks=[root_chunk,boards[0],boards[1],atlas_chunk,boards[2],boards[3],atlas_chunk]
table_offset=r.tables[4][0];count=len(chunks);data_offset=table_offset+count*24
out=bytearray(r.data[:table_offset])+bytearray(count*24)
for i,chunk in enumerate(chunks):
    record=list(records[0] if i==0 else records[min(i,4)])
    record[3]=len(chunk);record[4]=data_offset;record[6]=zlib.crc32(chunk)
    struct.pack_into('<HHIIIII',out,table_offset+i*24,*record)
    out+=chunk;data_offset+=len(chunk)
struct.pack_into('<II',out,24,len(out),len(out))
struct.pack_into('<III',out,40+4*12,table_offset,count,zlib.crc32(out[table_offset:table_offset+count*24]))
struct.pack_into('<I',out,32,header_crc(out))
candidate=BUILD/(entry_stem+'.redswf');candidate.write_bytes(out)
checked,_=validate_resource(candidate);check_meta,check_gfx,check_swf=unpack_root(checked)
validate_image_linkages(checked)
require(check_swf==new_swf and check_gfx==new_gfx,'Movie round trip failed')
require([checked.exports[i]['data'] for i in (1,2,4,5)]==boards,'Original board texture data changed')
require(symbols(movie_parts(check_gfx)[1])==names,'Native/source symbols differ')
backup=None
if args.apply:
    backups=ROOT/'BetaGwent/build/resource-backups';backups.mkdir(exist_ok=True)
    backup=backups/(sha(r.data)+'.redswf')
    if not backup.exists():backup.write_bytes(r.data)
    require(backup.read_bytes()==r.data,'Backup mismatch')
    require(TARGET.read_bytes()==r.data,'Project resource changed while preparing atlas')
    pending=TARGET.with_suffix('.redswf.pending')
    with pending.open('xb') as output:
        output.write(out);output.flush();os.fsync(output.fileno())
    os.replace(pending,TARGET)
    require(TARGET.read_bytes()==out,'Installed atlas resource mismatch')
report=dict(entry=args.entry,movieLinkage=movie_name.decode(),boardPixelPayloadsUnchanged=True,target=str(TARGET),source=str(SOURCE),sourceSha256=sha(new_swf),originalSha256=sha(r.data),updatedSha256=sha(out),
    updatedBytes=len(out),candidate=str(candidate),backup=str(backup) if backup else None,applied=args.apply,
    headerTableChunkChecksumsVerified=True,rootPropertiesPreserved=old_stem==movie_name[:-4],nativeImageTagsPreserved=False,
    textureChunksPreserved=4 if old_stem==movie_name[:-4] else 0,textureChunksAdded=0 if updating_atlas else 2,textureChunksReplaced=2 if updating_atlas else 0,totalTextureChunks=6,nativeABCMatchesBuiltSWF=True,
    nativeSymbolsMatchBuiltSWF=True,sourceBoardImagePayloadsUnchanged=True,
    atlasDDS=str(dds_path),atlasDDSSha256=sha(dds),atlasImageIds=atlas_ids,atlasSize=[atlas_width,atlas_height],atlasLinkage=atlas_name.decode(),nativeImageLinkagePrefixVerified=True,nativeRuntimeVerified=False,
    note='Native atlas install/update; owning .gfx linkage prefix verified. Original board chunks preserved. Restart REDkit to load current artwork and ABC. No UI automation.')
(ROOT/('docs/evidence/board-resource-update'+('' if args.entry=='BetaGwentBoard' else '-'+args.entry)+'.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
