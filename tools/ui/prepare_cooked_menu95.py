"""Remove editor-only authoring SWF from a shipping copy before Wcc serialization.

The native GFx, all image chunks, properties, symbols and ABC remain unchanged.
Never run this against the REDkit working resources; only a release/probe copy.
"""
from pathlib import Path
import struct,zlib,sys
from update_board_resource import validate_resource,unpack_root,header_crc

def strip_authoring(path):
    path=Path(path).resolve()
    build=Path(__file__).resolve().parents[2]/'BetaGwent/build'
    if not path.is_relative_to(build.resolve()):raise ValueError('Only build copies may be stripped')
    r,records=validate_resource(path)
    metadata,gfx,swf=unpack_root(r)
    root=metadata+struct.pack('<I',len(gfx))+gfx+struct.pack('<I',0)
    chunks=[root]+[e['data'] for e in r.exports[1:]]
    table=r.tables[4][0];out=bytearray(r.data[:table])+bytearray(len(chunks)*24)
    for i,chunk in enumerate(chunks):
        record=list(records[i]);record[3]=len(chunk);record[4]=len(out);record[6]=zlib.crc32(chunk)
        struct.pack_into('<HHIIIII',out,table+i*24,*record);out+=chunk
    struct.pack_into('<II',out,24,len(out),len(out))
    struct.pack_into('<III',out,88,table,len(chunks),zlib.crc32(out[table:table+len(chunks)*24]))
    struct.pack_into('<I',out,32,header_crc(out));path.write_bytes(out)
    checked,_=validate_resource(path);meta,after,raw=unpack_root(checked)
    assert metadata==meta and gfx==after and raw==b''
    assert [e['data'] for e in checked.exports[1:]]==chunks[1:]
    return dict(before=len(r.data),after=len(out),editorBytesRemoved=len(swf),nativeUnchanged=True)

if __name__=='__main__':
    print(strip_authoring(sys.argv[1]))
