"""Install variable-size native DDS pages using actual GFx image IDs.

All CRC, metadata, handle, linkage, symbol and ABC checks remain mandatory.
Identical exporter aliases share one texture; no dimension-based guessing.
"""
from pathlib import Path
import argparse,hashlib,io,json,os,struct,zlib
from PIL import Image
from update_board_resource import validate_resource,validate_image_linkages,unpack_root,movie_parts,header_crc,require,TARGET,SOURCE,ROOT

def sha(data):return hashlib.sha256(data).hexdigest()
def tag(code,payload):return struct.pack('<HI',(code<<6)|63,len(payload))+payload
def string(value):
 data=value.encode('ascii');require(len(data)<128,'Native property string too long')
 return bytes([len(data)|128])+data
def properties(r,props):
 out=bytearray(b'\0')
 for name,(kind,data) in props.items():
  out+=struct.pack('<HHI',r.names.index(name),r.names.index(kind),len(data)+4)+data
 return bytes(out)+b'\0\0'
def symbols(tags):
 out={}
 for code,p,_ in tags:
  if code!=76:continue
  count=struct.unpack_from('<H',p)[0];pos=2
  for _ in range(count):
   cid=struct.unpack_from('<H',p,pos)[0];pos+=2;end=p.index(0,pos);out[cid]=p[pos:end];pos=end+1
 return out

def resource_prefix(r):
 # Copy the engine's existing CName hash rather than guessing its algorithm.
 # Adding a name keeps all existing property/class indices stable.
 from read_gui_resource import GuiResource
 exemplar=GuiResource(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\r4data\gameplay\gui_new\swf\glossary\panel_glossary_bestiary.redswf')
 strings=bytearray(r.strings)
 no,count,_=r.tables[1];names=bytearray(r.data[no:no+count*8])
 for name in ('TCM_DXTNoAlpha','GUIWithoutAlpha'):
  if name not in r.names:
   index=exemplar.names.index(name)
   name_hash=exemplar.unpack('<II',exemplar.tables[1][0]+index*8)[1]
   names+=struct.pack('<II',len(strings),name_hash)
   strings+=name.encode()+b'\0';r.names.append(name)
 po,pc,_=r.tables[3];props=r.data[po:po+pc*16]
 out=bytearray(r.data[:160])
 for i,data,entries in [(0,strings,len(strings)),(1,names,len(r.names)),(3,props,pc)]:
  struct.pack_into('<III',out,40+i*12,len(out),entries,zlib.crc32(data));out+=data
 return out

def card_dds(export_name, exported_dds):
 import re
 import numpy as np
 match=re.match(rb'cards-(\d+)_png',export_name)
 if not match and not export_name.startswith((b'board_classic_png',b'board_wide_png',b'cardslots104_png',b'covers107_png',b'keg109')):return None
 digest=sha(exported_dds+b'bc3-to-bc1-v1');cache=ROOT/'BetaGwent/build/card-bc1';cache.mkdir(exist_ok=True)
 target=cache/(digest+'.dds')
 if not target.exists():
  # Every visible card rectangle is opaque. Unused cells are never sampled.
  # BC1 retains the full 384x540 illustration and halves GPU/storage bytes.
  # BC3 uses the same four-colour blocks as BC1. Discard only the opaque
  # alpha blocks; reverse endpoint/index order where BC1 would use transparency.
  require(exported_dds[84:88]==b'DXT5','Expected original BC3 card page')
  blocks=np.frombuffer(exported_dds[128:],dtype='<u4').reshape(-1,4)[:,2:].copy()
  endpoints=blocks[:,0];first=endpoints&65535;second=endpoints>>16
  swap=first<second;equal=first==second
  blocks[swap,0]=(first[swap]<<16)|second[swap]
  blocks[swap,1]^=np.uint32(0x55555555);blocks[equal,1]=0
  header=bytearray(exported_dds[:128]);header[84:88]=b'DXT1'
  struct.pack_into('<I',header,20,blocks.nbytes)
  target.write_bytes(header+blocks.tobytes())
 return target.read_bytes()

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--apply',action='store_true')
 parser.add_argument('--entry',choices=['BetaGwentBoard','DeckBuilder','GwintGame','BetaGwentKeg'],default='BetaGwentBoard')
 a=parser.parse_args();stem={'BetaGwentBoard':'betagwent_board','DeckBuilder':'betagwent_decks','GwintGame':'betagwent_npc00','BetaGwentKeg':'betagwent_kegop'}[a.entry]
 target=TARGET.with_name(stem+'.redswf');source=SOURCE.with_name(stem+'.swf')
 r,records=validate_resource(target);validate_image_linkages(r)
 _,old_gfx,old_swf=unpack_root(r)
 old_prefix,old_tags,_=movie_parts(old_swf);native_prefix,native_tags,native_tail=movie_parts(old_gfx)
 swf=source.read_bytes();prefix,tags,tail=movie_parts(swf)
 # Preserve stage dimensions and frame count. Only 30 -> 60 Hz is allowed;
 # the engine movie and authoring copy receive the same new frame header.
 require(not tail and len(prefix)==len(old_prefix)==len(native_prefix),'Movie frame header size changed')
 require(prefix[:-4]==old_prefix[:-4]==native_prefix[:-4] and prefix[-2:]==old_prefix[-2:]==native_prefix[-2:],'Movie stage extent/frame count changed')
 require(struct.unpack_from('<H',prefix,len(prefix)-4)[0] in (30*256,60*256),'Unsupported movie frame rate')
 names=symbols(tags);old_import=next(raw for c,p,raw in native_tags if c==1000)
 dds_dir=ROOT/('BetaGwent/ui/build/native-atlas'+('' if a.entry=='BetaGwentBoard' else '-'+a.entry))
 exported=(dds_dir/(stem+'.gfx')).read_bytes()
 if exported[:3]==b'GFX':exported=b'FWS'+exported[3:]
 _,export_tags,_=movie_parts(exported)
 exported_images={};subimages={}
 for c,p,_ in export_tags:
  if c==1009:
   image_id=struct.unpack_from('<H',p)[0];pos=11+p[10]
   require(pos<len(p) and len(p[pos+1:])==p[pos],'Malformed exporter image filename')
   exported_images[image_id]=p[pos+1:].decode('ascii')
  if c==1008:
   cid,image_id,x,y,w,h=struct.unpack('<6H',p)
   require(x==y==0,'Unexpected packed exporter subimage')
   subimages[cid]=image_id
 root_props,_=r.properties_at(r.exports[0]['data']);old_name=root_props['linkageName'][1][1:]
 movie_name=stem.replace('_','-',1).encode()+old_name[15:]
 require(len(movie_name)==len(old_name) and movie_name.endswith(b'.gfx'),'Movie identity changed length')
 template,_=r.properties_at(r.exports[1]['data']);metadata=resource_prefix(r)
 card_pages={}
 for c,p,_ in tags:
  if c!=35:continue
  cid=struct.unpack_from('<H',p)[0];export_name=names.get(cid,b'')
  if export_name.startswith((b'cards-',b'board_classic_png',b'board_wide_png',b'cardslots104_png',b'covers107_png',b'keg109')):
   filename=exported_images[subimages.get(cid,cid)]
   card_pages[sha((dds_dir/filename).read_bytes())]=export_name
 unique={};textures=[];infos=[];replacements={};bindings=[]
 for c,p,_ in tags:
  if c!=35:continue
  cid,jpeg_size=struct.unpack_from('<HI',p)
  with Image.open(io.BytesIO(p[6:6+jpeg_size])) as image:width,height=image.size
  filename=exported_images.get(subimages.get(cid,cid));require(filename is not None,'Exporter image ID missing')
  require(Path(filename).name==filename,'Unexpected DDS path')
  path=dds_dir/filename;original_dds=path.read_bytes();dds=card_dds(card_pages.get(sha(original_dds),b''),original_dds) or original_dds;dims=((width+3)//4*4,(height+3)//4*4)
  require(dds[:4]==b'DDS ' and struct.unpack_from('<II',dds,12)==(dims[1],dims[0]),'DDS extent mismatch')
  opaque=dds[84:88]==b'DXT1'
  require(dds[84:88] in (b'DXT1',b'DXT5') and len(dds)==128+dims[0]*dims[1]//(2 if opaque else 1),'Unsupported DDS format/payload')
  digest=sha(dds)
  if digest not in unique:
   image_id=len(textures);unique[digest]=image_id
   linkage=movie_name[:-4]+('_i'+str(image_id+1)+'.dds').encode()
   props=dict(template);props['width']=('Uint32',struct.pack('<I',dims[0]));props['height']=('Uint32',struct.pack('<I',dims[1]))
   props['compression']=('ETextureCompression',struct.pack('<H',r.names.index('TCM_DXTNoAlpha' if opaque else 'TCM_DXTAlpha')))
   props['textureGroup']=('CName',struct.pack('<H',r.names.index('GUIWithoutAlpha' if opaque else 'GUIWithAlpha')))
   props['linkageName']=('String',string(linkage.decode()))
   chunk=properties(r,props)+struct.pack('<6I',0,1,dims[0],dims[1],dims[0]*(2 if opaque else 4),len(dds)-128)+dds[128:]+struct.pack('<I',0)
   textures.append(chunk)
   export=names.get(cid,b'');require(len(export)<256 and len(linkage)<256,'DDS ImageInfo string overflow')
   infos.append(tag(1009,struct.pack('<5H',image_id,9,14,*dims)+bytes([len(export)])+export+bytes([len(linkage)])+linkage))
  image_id=unique[digest]
  replacements[cid]=tag(1008,struct.pack('<6H',cid,image_id,0,0,width,height))
  bindings.append(dict(cid=cid,imageId=image_id,source=str(path),sha256=digest,size=list(dims),format=dds[84:88].decode()))
 require(1<=len(textures)<=32 and len(replacements)==len(exported_images),'Unexpected native image coverage')
 body=prefix+old_import+b''.join(infos)
 for c,p,raw in tags:
  if c==65:continue
  body+=replacements[struct.unpack_from('<H',p)[0]] if c==35 else raw
 gfx=old_gfx[:4]+struct.pack('<I',len(body)+8)+zlib.compress(body+native_tail,9)
 props=dict(root_props);count=len(textures)
 props['textures']=('array:2,0,handle:CSwfTexture',struct.pack('<I',count)+b''.join(struct.pack('<I',i+2) for i in range(count)))
 props['linkageName']=('String',string(movie_name.decode()))
 require(all(props[k]==root_props[k] for k in props if k not in ('textures','linkageName')),'Root property changed')
 # Wcc's intermediate writer also serializes the authoring SWF before stripping
 # it. Store standard CWS, keeping its bytecode/pixels, below that buffer limit.
 stored_swf=b'CWS'+swf[3:8]+zlib.compress(swf[8:],6)
 root=properties(r,props)+struct.pack('<I',len(gfx))+gfx+struct.pack('<I',len(stored_swf))+stored_swf
 chunks=[root]+textures;offset=len(metadata);out=metadata+bytearray(len(chunks)*24);cursor=len(out)
 for i,chunk in enumerate(chunks):
  record=list(records[0] if i==0 else records[1]);record[3]=len(chunk);record[4]=cursor;record[6]=zlib.crc32(chunk)
  struct.pack_into('<HHIIIII',out,offset+i*24,*record);out+=chunk;cursor+=len(chunk)
 struct.pack_into('<II',out,24,len(out),len(out))
 struct.pack_into('<III',out,88,offset,len(chunks),zlib.crc32(out[offset:offset+len(chunks)*24]))
 struct.pack_into('<I',out,32,header_crc(out))
 build=ROOT/'BetaGwent/build/native-hd93-resource';build.mkdir(parents=True,exist_ok=True)
 candidate=build/(stem+'.redswf');candidate.write_bytes(out)
 checked,_=validate_resource(candidate);validate_image_linkages(checked)
 _,check_gfx,check_swf=unpack_root(checked)
 require(check_swf==stored_swf and check_gfx==gfx,'Native movie round trip failed')
 require(b'FWS'+check_swf[3:8]+zlib.decompress(check_swf[8:])==swf,'Compressed authoring SWF differs')
 require(symbols(movie_parts(gfx)[1])==names,'Native image/root symbols differ')
 raw_abc=next(p for c,p,_ in tags if c==82)
 require(next(p for c,p,_ in movie_parts(gfx)[1] if c==82)==raw_abc,'Native/source ABC mismatch')
 native_subimages={struct.unpack_from('<H',p)[0]:struct.unpack('<6H',p) for c,p,_ in movie_parts(gfx)[1] if c==1008}
 require(set(native_subimages)==set(replacements),'Native image coverage differs')
 backup=None
 if a.apply:
  backups=ROOT/'BetaGwent/build/resource-backups';backups.mkdir(exist_ok=True)
  backup=backups/(sha(r.data)+'.redswf')
  if not backup.exists():backup.write_bytes(r.data)
  # Stage 105: every build adds a ~150 MB backup (232 files / 33 GB by 07.10.2026).
  # Keep only the newest 12 originals; the current one is always among them.
  old=sorted(backups.glob('*.redswf'),key=lambda p:p.stat().st_mtime,reverse=True)[12:]
  for stale in old:
   if stale!=backup:
    try:stale.unlink()
    except OSError:pass
  require(backup.read_bytes()==r.data and target.read_bytes()==r.data,'Original/backup resource changed')
  pending=target.with_suffix('.redswf.pending')
  with pending.open('xb') as f:f.write(out);f.flush();os.fsync(f.fileno())
  os.replace(pending,target);require(target.read_bytes()==out,'Native install mismatch')
 report=dict(entry=a.entry,source=str(source),sourceSha256=sha(swf),target=str(target),updatedSha256=sha(out),
             updatedBytes=len(out),originalSha256=sha(r.data),candidate=str(candidate),backup=str(backup),applied=a.apply,
             nativeABCMatchesBuiltSWF=True,nativeSymbolsMatchBuiltSWF=True,headerTableChunkChecksumsVerified=True,
             nativeImageLinkagePrefixVerified=True,totalTextureChunks=len(textures),exportedBindings=len(bindings),
             aliasTexturesDeduplicated=len(bindings)-len(textures),bindings=bindings,nativeRuntimeVerified=False)
 suffix='' if a.entry=='BetaGwentBoard' else '-'+a.entry
 (ROOT/('docs/evidence/board-resource-update'+suffix+'.json')).write_text(json.dumps(report,indent=2)+'\n','utf8')
 print('Installed native HD',a.entry,'textures',len(textures),'aliases',len(bindings),'bytes',len(out),flush=True)
if __name__=='__main__':main()
