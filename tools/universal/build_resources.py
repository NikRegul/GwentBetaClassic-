from pathlib import Path
import hashlib,json,struct,sys,zlib,shutil
ROOT=Path('D:/w3mod');BASE=ROOT/'BetaGwent/build/universal081'
sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import bundle_entries,sha,require
from build_resources import strip_menu_authoring,read_vlq,vlq
def build():
 source=ROOT/'BetaGwent/build/release202/ru/package/Mods/modBetaGwent0924/content'
 menus=json.loads((BASE/'menus/menus.json').read_text());replacements={Path(x['path']).name:Path(x['path']) for x in menus['menus']}
 out=BASE/'resources-nextgen';resources=out/'resources';resources.mkdir(parents=True,exist_ok=True);files={}
 for name,raw in bundle_entries(source/'blob0.bundle'):
  name=name.replace('\\','/');p=resources/name;p.parent.mkdir(parents=True,exist_ok=True)
  if Path(name).name in replacements:raw=replacements[Path(name).name].read_bytes()
  if name.endswith('.redswf'):
   raw=strip_menu_authoring(raw);require(len(raw)<63*1024**2,'Menu over budget '+name)
  p.write_bytes(raw);files[name]=p
 with (source/'blob0.bundle').open('rb') as f:
  header=bytearray(f.read(32));table=bytearray(f.read(struct.unpack_from('<I',header,16)[0]))
 require(struct.unpack_from('<H',header,20)[0]==5,'Expected Next-Gen bundle')
 offset=(32+len(table)+4095)&~4095;positions=[]
 for i in range(0,len(table),304):
  name=bytes(table[i:i+256]).split(b'\0')[0].decode().replace('\\','/');raw=files[name].read_bytes();positions.append((offset,files[name]))
  struct.pack_into('<QIIII',table,i+272,offset,len(raw),len(raw),zlib.crc32(raw),0);offset=(offset+len(raw)+4095)&~4095
 total=positions[-1][0]+positions[-1][1].stat().st_size;struct.pack_into('<I',header,8,total)
 bundle=out/'blob0.bundle'
 with bundle.open('wb') as f:
  f.write(header);f.write(table)
  for offset,p in positions:
   f.write(bytes(offset-f.tell()))
   with p.open('rb') as src:shutil.copyfileobj(src,f)
 entries={n.replace('\\','/'):d for n,d in bundle_entries(bundle)}
 require(set(entries)==set(files),'Bundle file set')
 for n,d in entries.items():require(hashlib.sha256(d).hexdigest()==sha(files[n]),'Bundle payload '+n)
 data=(source/'metadata.store').read_bytes();require(struct.unpack_from('<I',data,4)[0]==7,'Expected Next-Gen metadata')
 size,pos=read_vlq(data,16);strings=data[pos:pos+size];pos+=size;arrays=[]
 for width in (32,24,24,4,8,12,16):
  count,pos=read_vlq(data,pos);arrays.append([bytearray(data[p:p+width]) for p in range(pos,pos+count*width,width)]);pos+=count*width
 require(pos==len(data) and not arrays[3],'Unsupported metadata layout')
 offsets={p.relative_to(resources).as_posix():offset for offset,p in positions};file_names={};maximum=0
 for i,record in enumerate(arrays[0]):
  if not i:continue
  off=struct.unpack_from('<I',record)[0];name=strings[off:strings.index(0,off)].decode().replace('\\','/')
  size=files[name].stat().st_size;struct.pack_into('<II',record,8,size,size);struct.pack_into('<I',record,20,0);file_names[i]=name;maximum=max(maximum,size)
 for i,record in enumerate(arrays[1]):
  if not i:continue
  old,packed,nxt,fid,bid=struct.unpack('<QIIII',record);require(bid==1 and nxt==0,'Multiple bundles not supported')
  name=file_names[fid];struct.pack_into('<QIIII',record,0,offsets[name],files[name].stat().st_size,nxt,fid,bid)
 require(len(arrays[2])==2,'Single bundle expected')
 total,off,name,first,count=struct.unpack('<Q4I',arrays[2][1]);start=32+len(table)
 arrays[2][1]=bytearray(struct.pack('<Q4I',name and bundle.stat().st_size-start or bundle.stat().st_size-start,start,name,first,count))
 output=bytearray(b'\x03VTM'+struct.pack('<III',7,maximum,maximum)+vlq(len(strings))+strings)
 for records in arrays:output+=vlq(len(records))+b''.join(records)
 (out/'metadata.store').write_bytes(output)
 report=dict(entries=[dict(path=n,bytes=p.stat().st_size,sha256=sha(p)) for n,p in files.items()],bundleSha256=sha(bundle),metadataSha256=sha(out/'metadata.store'),guiLimitMiB=63)
 (out/'resources.json').write_text(json.dumps(report,indent=2));print('Next-Gen resources verified',len(files),'max main menu MiB',max(p.stat().st_size for n,p in files.items() if n.startswith('betagwent/') and n.endswith('.redswf'))/1024**2)
if __name__=='__main__':build()
