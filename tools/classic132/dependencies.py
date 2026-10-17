"""Bounded reader for the observed shared Classic/Next-Gen SPED v2 cache."""
from pathlib import Path
import json
import struct

from build_resources import read_vlq
from formats import require,sha


def read_dependency_cache(data):
    require(data[:8]==b'SPED'+struct.pack('<I',2),'Expected SPED dependency cache version 2')
    pos=8;arrays=[]
    try:
        for width in (16,4,4,4):
            count,pos=read_vlq(data,pos)
            require(0<=count<=len(data)//width and pos+count*width<=len(data),
                    'Dependency cache array extent')
            arrays.append(data[pos:pos+count*width]);pos+=count*width
    except (IndexError,struct.error) as error:
        raise ValueError('Truncated dependency cache') from error
    require(pos==len(data),'Dependency cache trailing bytes')
    guids=[arrays[0][i:i+16] for i in range(0,len(arrays[0]),16)]
    require(len(guids)>0 and len(set(guids))==len(guids),'Dependency cache GUID identities')
    indices=[list(struct.unpack('<'+'I'*(len(a)//4),a)) for a in arrays[1:]]
    first,second,pool=indices
    require(len(first)==len(second)==len(guids) and pool and pool[0]==0,
            'Dependency cache parallel arrays')
    require(all(i<len(pool) for i in first+second),'Dependency cache reference range')
    return dict(guids=guids,first=first,second=second,pool=pool)


def verify_cache_paths(data,cook_db,paths):
    parsed=read_dependency_cache(data)
    files=json.loads(Path(cook_db).read_text('utf-8-sig'))['files']
    by_path={x['path'].replace('\\','/'):x for x in files}
    required={x.replace('\\','/') for x in paths}
    require(required<=set(by_path),'Cook database missing shipped GUI resources')
    guids=set(parsed['guids'])
    for path in required:
        words=[int(x,16) for x in by_path[path]['id'].split('-')]
        require(len(words)==4,'Cook database GUID layout')
        guid=struct.pack('<4I',words[1],words[0],words[3],words[2])
        require(guid in guids,'Dependency cache missing shipped GUI resource: '+path)
    return dict(version=2,guidCount=len(parsed['guids']),verifiedResourcePaths=len(required),
                dependencyPoolEntries=len(parsed['pool']))


def copy_dependency_cache(source,destination):
    source,destination=Path(source),Path(destination)
    data=source.read_bytes();parsed=read_dependency_cache(data)
    destination.write_bytes(data)
    require(destination.read_bytes()==data,'Dependency cache copy mismatch')
    return dict(version=2,bytes=len(data),guidCount=len(parsed['guids']),
                sha256=sha(destination),sourceBytesPreserved=True)
