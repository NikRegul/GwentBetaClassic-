"""Validate cooked GUI movies and every external native texture dependency."""
from pathlib import Path
import hashlib,json,struct,zlib
from read_gui_resource import GuiResource
from update_board_resource import require,header_crc,unpack_root,movie_parts

def read_checked(path,cooked=False):
    r=GuiResource(path);data=r.data
    require(len(data)<25*1024*1024,'GUI resource exceeds conservative streaming limit')
    require(struct.unpack_from('<II',data,24)==(len(data),len(data)),'Invalid file extent')
    require(header_crc(data)==struct.unpack_from('<I',data,32)[0],'Invalid header CRC')
    require(all(r.tables[i]==(0,0,0) for i in (5,6,7,8,9)),'Unexpected auxiliary GUI tables')
    for i,width in ((0,1),(1,8),(2,8),(3,16),(4,24)):
        offset,count,crc=r.tables[i]
        if count:require(zlib.crc32(r.slice(offset,count*width))==crc,'Table CRC mismatch '+str(i))
    offset,count,_=r.tables[4];cursor=offset+count*24
    require(count==1,'External GUI resource should have exactly one root chunk')
    for i in range(count):
        _,flags,parent,size,pos,template,crc=struct.unpack_from('<HHIIIII',data,offset+i*24)
        require(flags==(8192 if cooked else 0) and parent==0 and template==0 and pos==cursor,'Unsupported export layout')
        require(zlib.crc32(r.slice(pos,size))==crc,'Chunk CRC mismatch');cursor+=size
    require(cursor==len(data),'Trailing resource bytes')
    return r

def props(r):
    result,end=r.properties_at(r.exports[0]['data']);decoded={}
    for key,(kind,value) in result.items():
        if kind in ('CName','ETextureCompression'):value=r.name(struct.unpack('<H',value)[0])
        decoded[key]=(kind,value)
    return decoded,end

def verify(source,path,source_workspace,cooked_workspace):
    a=read_checked(source);b=read_checked(path,True)
    require(a.exports[0]['class']==b.exports[0]['class']=='CSwfResource','Unexpected GUI class')
    pa=props(a)[0];pb=props(b)[0]
    require(set(pb)=={'linkageName','textures'},'Unexpected cooked GUI properties')
    require({k:pa[k] for k in pb}==pb,'Runtime root properties changed')
    require(set(pa)-set(pb)=={'importFile','importFileTimeStamp','header','imageImportOptions'},'Unknown stripped editor metadata')
    require(a.imports==b.imports and len(a.imports)==15,'Texture dependency table changed')
    p,_=a.properties_at(a.exports[0]['data']);n=len(a.imports)
    require(p['textures']==('array:2,0,handle:CSwfTexture',struct.pack('<I',n)+b''.join(struct.pack('<i',-i-1) for i in range(n))),
            'Invalid external texture handle array')
    _,gfx,raw=unpack_root(a);require(raw==b'' and unpack_root(b)[1:]==(gfx,b''),'Cooked native GFx changed')
    filenames=[]
    for code,payload,_ in movie_parts(gfx)[1]:
        if code==1009:
            pos=11+payload[10];require(len(payload[pos+1:])==payload[pos],'Invalid native filename')
            filenames.append(payload[pos+1:])
    require(len(filenames)==n,'Image/texture count mismatch')
    textures=[]
    for i,imported in enumerate(a.imports):
        require(imported['class']=='CSwfTexture' and imported['flags']==0,'Unexpected texture reference type')
        relative=Path(imported['path'].replace('\\','/'))
        require(not relative.is_absolute() and '..' not in relative.parts,'Invalid texture path')
        sa=read_checked(Path(source_workspace)/relative);sb=read_checked(Path(cooked_workspace)/relative,True)
        require(sa.exports[0]['class']==sb.exports[0]['class']=='CSwfTexture','Wrong external class')
        pa,ea=props(sa);pb,eb=props(sb)
        require(set(pb)-set(pa)=={'textureCacheKey'} and pb['textureCacheKey'][0]=='Uint32' and len(pb['textureCacheKey'][1])==4,
                'Unexpected standalone texture metadata')
        require({k:pb[k] for k in pa}==pa,'Runtime texture properties changed')
        require(pa['linkageName'][1][1:]==filenames[i],'Native image filename does not identify its texture')
        x=sa.exports[0]['data'][ea:];y=sb.exports[0]['data'][eb:]
        header=struct.unpack_from('<6I',x)
        require(header==struct.unpack_from('<6I',y),'Texture extent/pitch changed')
        require(x[-4:]==b'\0'*4 and struct.unpack_from('<I',y,24)[0]==16,'Unknown texture serialization')
        require(len(x[24:-4])==header[5] and x[24:-4]==y[28:],'Texture pixels changed')
        textures.append(dict(path=imported['path'],bytes=len(sb.data),width=header[2],height=header[3],
                             pixelSha256=hashlib.sha256(x[24:-4]).hexdigest(),pixelsIdentical=True))
    return dict(source=str(source),cooked=str(path),bytes=len(b.data),sha256=hashlib.sha256(b.data).hexdigest(),
                externalHandlesVerified=True,checksumsVerified=True,nativeMovieIdentical=True,
                textures=textures,nativeRuntimeVerified=False)

if __name__=='__main__':
    import sys
    print(json.dumps(verify(*sys.argv[1:]),indent=2))
