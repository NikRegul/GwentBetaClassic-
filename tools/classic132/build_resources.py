"""Convert frozen release GUI resources and build a verified Classic bundle."""
import argparse
import json
from pathlib import Path
import struct
import sys

from formats import ROOT,Resource,bundle_entries,header_crc,require,sha,write_bundle,classic_metadata_hash_rows,cook_guid_map

sys.path.insert(0,str(ROOT/'tools/ui'))
from cr2w_gui_write109 import Res,prop


def strip_menu_authoring(data):
    """Drop the editor SWF; preserve native GFx, properties and every texture."""
    resource=Resource(data)
    require(resource.classes[0]=='CSwfResource','Expected SWF resource')
    root=resource.chunks[0]
    _,pos=resource.properties(root)
    require(pos+4<=len(root),'Missing native movie length')
    native_size=struct.unpack_from('<I',root,pos)[0]
    native_end=pos+4+native_size
    require(native_end+4<=len(root),'Truncated native movie')
    editor_size=struct.unpack_from('<I',root,native_end)[0]
    require(native_end+4+editor_size==len(root),'Invalid editor movie extent')
    if not editor_size:return data
    chunks=[root[:native_end]+struct.pack('<I',0),*resource.chunks[1:]]
    output=resource.replace_chunks(chunks)
    checked=Resource(output)
    require(checked.chunks==chunks,'Shipping movie or textures changed')
    return output


def classic_config(data):
    original=Resource(data)
    require(original.classes==['CGuiConfigResource'],'Expected Classic config')
    d=bytearray(data);struct.pack_into('<I',d,4,164);struct.pack_into('<I',d,32,header_crc(d))
    result=Res(d);props,end=original.properties(original.chunks[0]);require(end==len(original.chunks[0]),'Config tail')
    menu_additions=bytearray()
    for name,path in [('BetaGwentBoard',r'betagwent\betagwent_board.menu'),('BetaGwentKeg',r'betagwent\betagwent_kegop.menu')]:
        require(name not in original.names,'Already patched config')
        name_index=result.add_name(name);import_index=result.add_import(path,'CMenuResource',4)
        menu_additions+=b'\0'+prop(result,'menuName','CName',struct.pack('<H',name_index))+prop(result,'menuResource','soft:CMenuResource',struct.pack('<H',import_index))+b'\0\0'
    chunk=bytearray(b'\0')
    old_menus=None
    for name,kind,value in props:
        if original.names[name]=='menus':
            old_menus=value;count=struct.unpack_from('<I',value)[0]
            value=struct.pack('<I',count+2)+value[4:]+menu_additions
        chunk+=prop(result,original.names[name],original.names[kind],value)
    require(old_menus is not None,'No menus property')
    chunk+=b'\0\0';result.payloads=[bytes(chunk)]
    out=Resource(result.build()).classic();checked=Resource(out)
    changed,_=checked.properties(checked.chunks[0]);new=next(v for n,t,v in changed if checked.names[n]=='menus')
    require(new[4:4+len(old_menus)-4]==old_menus[4:],'Vanilla menus changed')
    return out


def read_vlq(data,pos):
    byte=data[pos];pos+=1;value=byte&63;negative=byte&128;more=byte&64;shift=6
    while more:
        byte=data[pos];pos+=1;value|=(byte&127)<<shift;shift+=7;more=byte&128
        require(shift<=34,'Invalid VLQ')
    return -value if negative else value,pos


def vlq(value):
    require(value>=0,'Negative count');out=bytearray([value&63]);value>>=6
    if value:out[0]|=64
    elif not out[0]:out[0]=128
    while value:
        byte=value&127;value>>=7;out.append(byte|(128 if value else 0))
    return bytes(out)


def convert_metadata(source,bundle,out):
    """Preserve path hashes/tree; convert Classic lookup IDs, sizes and offsets."""
    data=Path(source).read_bytes();require(data[:4]==b'\x03VTM','Metadata magic')
    version=struct.unpack_from('<I',data,4)[0];require(version in (6,7),'Metadata version')
    size,pos=read_vlq(data,16);strings=data[pos:pos+size];pos+=size
    arrays=[]
    for width in (32,24 if version==7 else 20,24,4,8,12,16):
        count,pos=read_vlq(data,pos);require(count>=0,'Metadata count');arrays.append([bytearray(data[p:p+width]) for p in range(pos,pos+count*width,width)]);pos+=count*width
    require(pos==len(data) and not arrays[3],'Metadata buffers/layout')
    with Path(bundle).open('rb') as f:h=f.read(32);table=f.read(struct.unpack_from('<I',h,16)[0])
    entries={}
    for p in range(0,len(table),320):
        row=table[p:p+320];name=row[:256].split(b'\0')[0].decode();size,packed,offset=struct.unpack_from('<III',row,276);entries[name]=(size,packed,offset)
    file_names={};maximum=0
    for i,record in enumerate(arrays[0]):
        if i==0:continue
        off=struct.unpack_from('<I',record)[0];name=strings[off:strings.index(0,off)].decode('ascii')
        require(name in entries,'Missing metadata resource '+name);size,packed,offset=entries[name]
        struct.pack_into('<II',record,8,packed,size);struct.pack_into('<I',record,20,0);file_names[i]=name;maximum=max(maximum,size)
    require(set(file_names.values())==set(entries),'Metadata file set')
    converted=[]
    for i,record in enumerate(arrays[1]):
        if not i:converted.append(bytearray(20));continue
        if version==7:offset,packed,nxt,fid,bid=struct.unpack('<QIIII',record)
        else:fid,bid,offset,packed,nxt=struct.unpack('<5I',record)
        require(bid==1 and nxt==0,'Multiple metadata bundles/entries unsupported')
        size,packed,offset=entries[file_names[fid]];converted.append(bytearray(struct.pack('<5I',fid,bid,offset,packed,nxt)))
    arrays[1]=converted;require(len(arrays[2])==2,'Single bundle expected')
    arrays[6]=classic_metadata_hash_rows(arrays[6],len(arrays[0]))
    record=arrays[2][1]
    if version==7:total,off,name,first,count=struct.unpack('<Q4I',record)
    else:name,first,count,total,off,burst=struct.unpack('<6I',record)
    offset=32+len(table);arrays[2][1]=bytearray(struct.pack('<6I',name,first,count,Path(bundle).stat().st_size-offset,offset,0))
    result=bytearray(b'\x03VTM'+struct.pack('<III',6,maximum,maximum)+vlq(len(strings))+strings)
    for records in arrays:result+=vlq(len(records))+b''.join(records)
    Path(out).write_bytes(result)
    return dict(version=6,files=len(entries),pathHashesPreserved=True,
                classicHashFileIdsValidated=True,offsetsRegenerated=True,sha256=sha(out))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=int,required=True);p.add_argument('--menus',type=Path,required=True)
    p.add_argument('--game',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--gui-limit-mib',type=int,default=65)
    a=p.parse_args();out=a.out.resolve();require(not out.exists() and out.is_relative_to(ROOT/'BetaGwent/build'),'Fresh build output required')
    require(1<=a.gui_limit_mib<=65,'GUI budget must be 1..65 MiB')
    package=ROOT/f'BetaGwent/build/release{a.stage}/ru/package';source=package/'Mods/modBetaGwent0924/content'
    manifest=json.loads((package/'manifest.json').read_text('utf8'))
    for name in ('blob0.bundle','metadata.store'):
        record=next(x for x in manifest['files'] if x['path'].endswith('/'+name));require(sha(source/name)==record['sha256'],'Frozen release changed: '+name)
    menus=json.loads((a.menus/'menus.json').read_text('utf8'));require(menus['sourceStage']==a.stage,'Menu stage mismatch')
    replacements={Path(x['path']).name:Path(x['path']) for x in menus['menus']}
    for row in menus['menus']:require(sha(row['path'])==row['sha256'],'Menu changed')
    templates=dict(bundle_entries(a.game/'content/content0/bundles/startup.bundle',lambda n:n.endswith('r4default.guiconfig')))
    require(len(templates)==1,'Classic config not found');template=next(iter(templates.values()));config=classic_config(template)
    inputs=out/'resources';inputs.mkdir(parents=True);files={};conversions=[]
    for name,raw in bundle_entries(source/'blob0.bundle'):
        name=name.replace('\\','/');path=inputs/name;path.parent.mkdir(parents=True,exist_ok=True)
        if Path(name).name in replacements:raw=replacements[Path(name).name].read_bytes()
        if name.endswith('.redswf'):raw=strip_menu_authoring(raw)
        if name.endswith('.guiconfig'):raw=config
        elif raw[:4]==b'CR2W':raw=Resource(raw).classic()
        elif Path(name).suffix not in ('.xml','.csv'):raise ValueError('Unsupported resource '+name)
        if name.endswith('.redswf'):require(len(raw)<a.gui_limit_mib*1024*1024,'Menu exceeds GUI budget: '+name)
        path.write_bytes(raw);files[name]=path
        conversions.append(dict(path=name,bytes=len(raw),sha256=sha(path),classicVersion=163 if raw[:4]==b'CR2W' else None))
    guids=cook_guid_map(package.parent/'cooked/cook.db')
    entries=write_bundle(files,out/'blob0.bundle',guids=guids);metadata=convert_metadata(source/'metadata.store',out/'blob0.bundle',out/'metadata.store')
    report=dict(sourceStage=a.stage,sourceBundleSha256=sha(source/'blob0.bundle'),sourceConfigSha256=__import__('hashlib').sha256(template).hexdigest(),
                bundleVersion=3,resourceVersion=163,metadata=metadata,entries=entries,guiLimitMiB=a.gui_limit_mib,
                vanillaGuiConfigPreserved=True,customMenusAdded=2,cookedGuiTextures=True,
                nativeResourceGuidsPreserved=True,nativeResourcePlaybackVerified=False)
    (out/'resources.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print('Classic resources verified:',len(entries),flush=True)


if __name__=='__main__':main()
