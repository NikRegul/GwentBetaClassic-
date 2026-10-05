"""Verify observed REDkit cooked GUI serialization against its frozen input.

Cooking renumbers CNames, marks exports cooked and inserts the native texture
format before pixels. It must preserve GFx and every compressed color block.
"""
from pathlib import Path
import hashlib,json,struct,zlib
from read_gui_resource import GuiResource
from update_board_resource import require,header_crc,unpack_root,validate_resource,validate_image_linkages

def verify(source,path):
    original,_=validate_resource(source)
    validate_image_linkages(original)
    cooked=GuiResource(path);data=cooked.data
    require(struct.unpack_from('<II',data,24)==(len(data),len(data)),'Cooked extent mismatch')
    require(header_crc(data)==struct.unpack_from('<I',data,32)[0],'Cooked header CRC mismatch')
    require(all(cooked.tables[i]==(0,0,0) for i in (2,5,6,7,8,9)),'Unexpected cooked auxiliary tables')
    for i,width in ((0,1),(1,8),(3,16),(4,24)):
        offset,count,crc=cooked.tables[i]
        require(zlib.crc32(cooked.slice(offset,count*width))==crc,'Cooked table CRC '+str(i))
    offset,count,_=cooked.tables[4];cursor=offset+count*24
    require(count==len(original.exports),'Cooked chunk count differs')
    for i in range(count):
        _,flags,parent,size,pos,template,crc=struct.unpack_from('<HHIIIII',data,offset+i*24)
        require(flags==8192 and template==0 and parent==(0 if i==0 else 1) and pos==cursor,
                'Unexpected cooked export layout '+str(i))
        require(zlib.crc32(cooked.slice(pos,size))==crc,'Cooked chunk CRC '+str(i))
        require(cooked.exports[i]['class']==original.exports[i]['class'],'Cooked chunk type differs')
        cursor+=size
    require(cursor==len(data),'Trailing cooked bytes')
    _,gfx,raw=unpack_root(cooked)
    require(gfx==unpack_root(original)[1] and raw==b'','Cooked native movie changed')
    validate_image_linkages(cooked)
    rows=[]
    for i,(a,b) in enumerate(zip(original.exports[1:],cooked.exports[1:])):
        pa,ea=original.properties_at(a['data']);pb,eb=cooked.properties_at(b['data'])
        require(set(pa)==set(pb),'Cooked texture properties differ')
        for key in pa:
            ka,va=pa[key];kb,vb=pb[key]
            require(ka==kb,'Cooked property type differs')
            if ka in ('CName','ETextureCompression'):
                va=original.name(struct.unpack('<H',va)[0]);vb=cooked.name(struct.unpack('<H',vb)[0])
            require(va==vb,'Cooked texture property differs: '+key)
        sa=a['data'][ea:];sb=b['data'][eb:]
        header=struct.unpack_from('<6I',sa)
        require(header==struct.unpack_from('<6I',sb),'Cooked texture dimensions/pitch differ')
        require(sa[-4:]==b'\0'*4 and struct.unpack_from('<I',sb,24)[0]==16,'Unknown texture buffer format')
        require(len(sa[24:-4])==header[5] and sa[24:-4]==sb[28:],'Cooked pixel blocks differ')
        rows.append(dict(width=header[2],height=header[3],pixelBytes=header[5],identical=True))
    return dict(source=str(source),cooked=str(path),bytes=len(data),
                sha256=hashlib.sha256(data).hexdigest(),checksumsVerified=True,
                nativeMovieIdentical=True,textures=rows,nativeRuntimeVerified=False)

if __name__=='__main__':
    import sys
    print(json.dumps(verify(Path(sys.argv[1]),Path(sys.argv[2])),indent=2))
