"""Check the observed v5 POTATO70/304-byte bundle table and packed payloads.

Unlike older 320-byte entries, this local writer stores hash16, offset64,
size32, zsize32, CRC32, compression32 and padding8 after the name256.
Compare every decompressed entry to the frozen cooked input, not only ZIP CRC.
"""
from pathlib import Path
import hashlib,struct,zlib,sys
from update_board_resource import require

def verify(bundle,input_directory,require_uncompressed_gui=False):
    data=Path(bundle).read_bytes();root=Path(input_directory)
    require(data[:8]==b'POTATO70','Unexpected bundle magic')
    table_bytes=struct.unpack_from('<I',data,16)[0]
    require(table_bytes%304==0 and table_bytes>0,'Unsupported bundle table layout')
    rows=[];names=set();ranges=[]
    for pos in range(32,32+table_bytes,304):
        raw=data[pos:pos+256];require(b'\0' in raw,'Unterminated bundle filename')
        name=raw.split(b'\0')[0].decode('ascii')
        require(name not in names,'Duplicate bundle entry');names.add(name)
        offset,size,zsize,crc,compression=struct.unpack_from('<QIIII',data,pos+272)
        require(offset>=32+table_bytes and offset+zsize<=len(data),'Truncated bundle entry')
        ranges.append((offset,offset+zsize,name))
        relative=Path(name.replace('\\','/'))
        require(not relative.is_absolute() and '..' not in relative.parts,'Unsafe bundle path')
        packed=data[offset:offset+zsize]
        if compression==0:payload=packed
        elif compression in (4,5):
            try:import lz4.block
            except ImportError:
                sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor/audio-python'));import lz4.block
            payload=lz4.block.decompress(packed,uncompressed_size=size)
        elif compression==1:payload=zlib.decompress(packed)
        else:raise ValueError('Unexpected compression '+str(compression))
        require(len(payload)==size and zlib.crc32(payload)==crc,'Packed data CRC/size mismatch: '+name)
        require(payload==(root/relative).read_bytes(),'Packed payload differs from cooked source: '+name)
        if relative.suffix in ('.redswf','.redswfx'):
            if require_uncompressed_gui:
                require(compression==0 and size==zsize and size<100*1024*1024,'Inline GUI must use raw bundle storage under 100 MiB')
            else:
                require(size<25*1024*1024 and zsize<25*1024*1024,'GUI streaming budget exceeded in bundle')
        rows.append(dict(path=name,size=size,packedSize=zsize,compression=compression,sha256=hashlib.sha256(payload).hexdigest()))
    previous=32+table_bytes
    for start,end,name in sorted(ranges):
        require(start>=previous,'Overlapping bundle entry: '+name);previous=end
    expected={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    require({n.replace('\\','/') for n in names}==expected,'Missing/unexpected bundle entries')
    return dict(bundle=str(bundle),entries=rows,packedPayloadsVerified=True,guiStoredUncompressed=require_uncompressed_gui,nativeRuntimeVerified=False)

if __name__=='__main__':
    import json
    print(json.dumps(verify(*sys.argv[1:]),indent=2))
