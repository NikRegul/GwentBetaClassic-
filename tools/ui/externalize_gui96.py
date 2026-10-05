"""Split a shipping GUI movie into small native .redswfx texture resources.

CSwfTexture is a registered resource in both REDkit and the retail executable.
Its external CHandle encoding follows WolvenKit's CR2W implementation. All
dimensions, compression, image IDs and pixel blocks remain unchanged; only
image filenames and texture handle locations change. No AS recompilation.
"""
from pathlib import Path
import hashlib,json,struct,zlib
from read_gui_resource import GuiResource
from update_board_resource import require,header_crc,unpack_root,movie_parts,validate_resource
from install_native_hd93 import properties,string,tag

ROOT=Path(__file__).resolve().parents[2]

def rebuild(r,chunks,imports=()):
    """Rebuild observed v164 tables, preserving CName hashes and property rows."""
    strings=bytearray(r.strings);import_bytes=bytearray()
    for path,classname,flags in imports:
        import_bytes+=struct.pack('<IHH',len(strings),r.names.index(classname),flags)
        strings+=path.encode('ascii')+b'\0'
    out=bytearray(r.data[:160])
    for i in range(10):struct.pack_into('<III',out,40+i*12,0,0,0)
    for i,payload,count in ((0,strings,len(strings)),
        (1,r.slice(r.tables[1][0],r.tables[1][1]*8),r.tables[1][1]),
        (2,import_bytes,len(imports)),
        (3,r.slice(r.tables[3][0],r.tables[3][1]*16),r.tables[3][1])):
        if count:struct.pack_into('<III',out,40+i*12,len(out),count,zlib.crc32(payload));out+=payload
    offset=len(out);out+=bytes(len(chunks)*24)
    for i,(classname,payload) in enumerate(chunks):
        struct.pack_into('<HHIIIII',out,offset+i*24,r.names.index(classname),0,0,len(payload),len(out),0,zlib.crc32(payload))
        out+=payload
    struct.pack_into('<III',out,88,offset,len(chunks),zlib.crc32(out[offset:offset+len(chunks)*24]))
    struct.pack_into('<II',out,24,len(out),len(out));struct.pack_into('<I',out,32,header_crc(out))
    return bytes(out)

def externalize(source,target,workspace):
    source=Path(source);target=Path(target);workspace=Path(workspace)
    require(target.resolve().is_relative_to((ROOT/'BetaGwent/build').resolve()),'Shipping build copies only')
    r,_=validate_resource(source);metadata,gfx,raw=unpack_root(r)
    names=[];imports=[];pages=[]
    for i,e in enumerate(r.exports[1:]):
        props,end=r.properties_at(e['data']);pixels=e['data'][end:]
        digest=hashlib.sha256(pixels).hexdigest()
        name='betagwent96_'+digest[:24]+'.dds';depot='betagwent\\textures96\\page_'+digest[:24]+'.redswfx'
        props=dict(props);props['linkageName']=('String',string(name))
        payload=properties(r,props)+pixels
        page=workspace/Path(depot.replace('\\','/'));page.parent.mkdir(parents=True,exist_ok=True)
        data=rebuild(r,[('CSwfTexture',payload)])
        if page.exists():
            existing=GuiResource(page);other,after=existing.properties_at(existing.exports[0]['data'])
            require(existing.exports[0]['data'][after:]==pixels,'Shared texture hash collision')
            require(other['linkageName']==props['linkageName'],'Shared texture identity differs')
        else:page.write_bytes(data)
        names.append(name.encode());imports.append((depot,'CSwfTexture',0))
        pages.append(dict(path=depot,bytes=page.stat().st_size,width=struct.unpack('<I',props['width'][1])[0],
                          height=struct.unpack('<I',props['height'][1])[0],pixelSha256=digest))
    prefix,tags,tail=movie_parts(gfx);parts=[];ordinal=0
    for code,payload,encoded in tags:
        if code==1009:
            pos=11+payload[10]
            payload=payload[:pos]+bytes([len(names[ordinal])])+names[ordinal];ordinal+=1
            encoded=tag(code,payload)
        parts.append(encoded)
    require(ordinal==len(imports),'Texture/native image count differs')
    body=prefix+b''.join(parts);movie=gfx[:4]+struct.pack('<I',len(body)+8)+zlib.compress(body+tail,9)
    props,_=r.properties_at(r.exports[0]['data']);props=dict(props)
    props['textures']=('array:2,0,handle:CSwfTexture',struct.pack('<I',len(imports))+b''.join(struct.pack('<i',-i-1) for i in range(len(imports))))
    root=properties(r,props)+struct.pack('<I',len(movie))+movie+struct.pack('<I',0)
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(rebuild(r,[('CSwfResource',root)],imports))
    after=GuiResource(target);after_props,_=after.properties_at(after.exports[0]['data'])
    require(after_props['textures']==props['textures'] and len(after.imports)==len(imports),'External handle roundtrip failed')
    require(next(p for c,p,_ in movie_parts(unpack_root(after)[1])[1] if c==82)==next(p for c,p,_ in tags if c==82),'Native ABC changed')
    return dict(source=str(source),target=str(target),before=len(r.data),after=target.stat().st_size,
                authoringRemoved=True,pixelsUnchanged=True,nativeABCUnchanged=True,textures=pages,nativeRuntimeVerified=False)

if __name__=='__main__':
    import sys
    result=externalize(sys.argv[1],sys.argv[2],sys.argv[3]);print(json.dumps(result,indent=2))
