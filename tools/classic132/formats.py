"""Bounded Classic container adapters. Inputs are never modified.

Bundle layouts: https://github.com/Systemcluster/w3edit/blob/main/src/bundle.rs
Sound cache layout: WolvenKit-7/WolvenKit.Wwise/SoundCache/Sound_Cache.cs
Only the GUI resource classes used by this mod are accepted, not arbitrary CR2W.
"""
import hashlib
from pathlib import Path
import shutil
import struct
import sys
import zlib

ROOT=Path(__file__).resolve().parents[2]


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def require(value,reason):
    if not value:raise ValueError(reason)


def snappy(raw):
    """Raw Snappy decoder for shipped vanilla GUI templates."""
    pos=0;size=0;shift=0
    while True:
        byte=raw[pos];pos+=1;size|=(byte&127)<<shift
        if byte<128:break
        shift+=7;require(shift<=28,'Snappy size')
    out=bytearray()
    while pos<len(raw):
        tag=raw[pos];pos+=1;kind=tag&3
        if kind==0:
            length=tag>>2
            if length>=60:
                width=length-59;length=int.from_bytes(raw[pos:pos+width],'little');pos+=width
            length+=1;out+=raw[pos:pos+length];pos+=length
        else:
            if kind==1:length=4+((tag>>2)&7);offset=((tag&224)<<3)|raw[pos];pos+=1
            else:
                length=1+(tag>>2);width=2 if kind==2 else 4;offset=int.from_bytes(raw[pos:pos+width],'little');pos+=width
            require(0<offset<=len(out),'Snappy copy offset')
            for _ in range(length):out.append(out[-offset])
        require(len(out)<=size,'Snappy output extent')
    require(pos==len(raw) and len(out)==size,'Snappy output size');return bytes(out)


def bundle_entries(path,include=lambda name:True):
    with Path(path).open('rb') as f:
        h=f.read(32);require(h[:8]==b'POTATO70','Bundle magic')
        version=struct.unpack_from('<H',h,20)[0];require(version in (3,5),'Bundle version')
        width=320 if version==3 else 304
        count=struct.unpack_from('<I',h,16)[0];require(count%width==0,'Bundle table')
        table=f.read(count);require(len(table)==count,'Truncated table')
        seen=set();ranges=[]
        for pos in range(0,count,width):
            row=table[pos:pos+width];name=row[:256].split(b'\0')[0].decode('ascii')
            rel=Path(name.replace('\\','/'))
            require(name and len(row[:256].split(b'\0')[0])<256 and name not in seen and not rel.is_absolute() and '..' not in rel.parts,'Unsafe/duplicate bundle name')
            seen.add(name)
            if version==5:offset,size,packed,crc,compression=struct.unpack_from('<QIIII',row,272)
            else:
                size,packed,offset=struct.unpack_from('<III',row,276)
                crc,compression=struct.unpack_from('<II',row,312)
            require(offset>=32+count and offset+packed<=Path(path).stat().st_size,'Bundle payload range')
            ranges.append((offset,offset+packed))
            if not include(name):continue
            f.seek(offset);raw=f.read(packed)
            if compression==0:data=raw
            elif compression==1:data=zlib.decompress(raw)
            elif compression==2:data=snappy(raw)
            elif compression in (4,5):
                sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
                import lz4.block
                data=lz4.block.decompress(raw,uncompressed_size=size)
            else:raise ValueError('Unsupported bundle compression '+str(compression))
            require(len(data)==size and zlib.crc32(data)==crc,'Bundle payload CRC: '+name)
            yield name,data
        previous=32+count
        for start,end in sorted(ranges):require(start>=previous,'Overlapping payload');previous=end


def cook_guid_map(path):
    """Stable depot identities from the frozen cook DB, in native TOC order."""
    import json
    result={}
    for row in json.loads(Path(path).read_text('utf-8-sig'))['files']:
        parts=row['id'].split('-')
        require(len(parts)==4 and all(len(x)==8 for x in parts),'Cook GUID layout')
        words=[int(x,16) for x in parts]
        name=row['path'].replace('\\','/')
        require(name not in result,'Duplicate cook GUID path')
        result[name]=struct.pack('<4I',words[1],words[0],words[3],words[2])
    return result


def write_bundle(files,out,guids=None):
    """Uncompressed GUI, 4096-byte payload alignment, Classic v3/320-byte TOC."""
    items=sorted(files.items());toc=bytearray();cursor=(32+320*len(items)+4095)&~4095
    positions=[]
    for name,path in items:
        raw=name.replace('/','\\').encode('ascii');require(len(raw)<256,'Bundle name too long')
        size=path.stat().st_size;crc=0
        with path.open('rb') as f:
            is_resource=f.read(4)==b'CR2W';f.seek(0)
            while block:=f.read(1024*1024):crc=zlib.crc32(block,crc)
        row=bytearray(320);row[:len(raw)]=raw
        if is_resource:
            identity=(guids or {}).get(name.replace('\\','/'))
            require(identity is not None and len(identity)==16 and identity!=bytes(16),
                    'Missing native resource GUID: '+name)
            row[256:272]=identity
        struct.pack_into('<III',row,276,size,size,cursor);struct.pack_into('<II',row,312,crc,0)
        toc+=row;positions.append(cursor);cursor=(cursor+size+4095)&~4095
    total=positions[-1]+items[-1][1].stat().st_size if items else 32
    require(total<2**32,'Classic bundle size limit')
    h=b'POTATO70'+struct.pack('<III',total,0,len(toc))+bytes.fromhex('030001000013131313131313')
    with Path(out).open('wb') as f:
        f.write(h);f.write(toc)
        for (_,path),position in zip(items,positions):
            f.write(b'\0'*(position-f.tell()))
            with path.open('rb') as src:shutil.copyfileobj(src,f)
    verified=[]
    for name,data in bundle_entries(out):
        rel=name.replace('\\','/');require(hashlib.sha256(data).hexdigest()==sha(files[rel]),'Packed payload mismatch')
        verified.append(dict(path=rel,bytes=len(data),sha256=sha(files[rel])))
    require(len(verified)==len(items),'Bundle file count');return verified


def header_crc(data):
    h=bytearray(data[:160]);struct.pack_into('<I',h,32,0xDEADBEEF);return zlib.crc32(h)


def classic_texture_tail(tail):
    """Cook the observed single-mip GUI texture without changing BC pixels.

    The layout is pinned against the installed 1.32 gwint menu textures.
    Other mip layouts need a separate adapter, never a guessed conversion.
    """
    require(len(tail)>=28,'Truncated authoring GUI texture')
    unknown,mips,width,height,pitch,size=struct.unpack_from('<6I',tail)
    require(unknown==0 and mips==1 and width>0 and height>0 and pitch>0,
            'Unsupported authoring GUI texture layout')
    require(len(tail)==28+size and tail[-4:]==b'\0'*4,
            'Expected single authoring mip and empty resident mip')
    pixels=tail[24:24+size]
    cooked=tail[:24]+struct.pack('<HH',16,0)+pixels
    require(cooked[28:]==pixels and len(cooked)==len(tail),'GUI texture pixels changed')
    return cooked


class Resource:
    """The same bounded table/property schema is used by v163 and v164 GUI."""
    def __init__(self,data):
        self.data=bytes(data);d=self.data
        require(len(d)>=160 and d[:4]==b'CR2W' and struct.unpack_from('<I',d,4)[0] in (163,164),'GUI resource version')
        require(header_crc(d)==struct.unpack_from('<I',d,32)[0],'Resource header CRC')
        require(struct.unpack_from('<II',d,24)==(len(d),len(d)),'Resource buffers not supported')
        self.tables=[struct.unpack_from('<III',d,40+i*12) for i in range(10)]
        require(all(x==(0,0,0) for x in self.tables[5:]),'Resource auxiliary tables')
        for i,width in enumerate((1,8,8,16,24)):
            off,count,crc=self.tables[i]
            require(off+count*width<=len(d) and (not count or zlib.crc32(d[off:off+count*width])==crc),'Resource table CRC '+str(i))
        off,count,_=self.tables[0];self.strings=d[off:off+count]
        off,count,_=self.tables[1];self.names=[self.string(struct.unpack_from('<I',d,off+i*8)[0]) for i in range(count)]
        off,count,_=self.tables[2];self.imports=[struct.unpack_from('<IHH',d,off+i*8) for i in range(count)]
        off,count,_=self.tables[4];self.records=[list(struct.unpack_from('<HHIIIII',d,off+i*24)) for i in range(count)]
        self.chunks=[];cursor=off+count*24
        for cls,flags,parent,size,pos,template,crc in self.records:
            require(pos==cursor and pos+size<=len(d) and flags in (0,8192) and template==0,'Unsupported GUI chunk')
            raw=d[pos:pos+size];require(zlib.crc32(raw)==crc,'Chunk CRC');cursor+=size;self.chunks.append(raw)
        require(cursor==len(d),'Resource trailing bytes')
        self.classes=[self.names[r[0]] for r in self.records]
        allowed={'CSwfResource','CSwfTexture','CGuiConfigResource','CMenuResource','CMenuDef','CMenuPauseParam','CMenuInheritBackgroundVideoParam','CMenuRenderBackgroundParam'}
        require(self.classes and not set(self.classes)-allowed,'Unsupported GUI class')

    def string(self,off):return self.strings[off:self.strings.index(0,off)].decode('utf8')

    def properties(self,raw):
        require(raw[0]==0,'Object marker');pos=1;props=[]
        while raw[pos:pos+2]!=b'\0\0':
            n,t,size=struct.unpack_from('<HHI',raw,pos);end=pos+4+size
            require(size>=4 and end<=len(raw),'Property range')
            props.append((n,t,raw[pos+8:end]));pos=end
        return props,pos+2

    def classic(self):
        # REDkit authoring textures store pixels in SMipData, followed by an
        # empty resident mip. Retail Classic reads cooked textures: SMipData
        # contains dimensions/pitch only; pixels follow ResidentMipSize and
        # the two uint16 resident-mip fields. Changing v164 to v163 alone
        # leaves the authoring flags and the wrong texture payload layout.
        chunks=[]
        for record,cls,chunk in zip(self.records,self.classes,self.chunks):
            if cls=='CSwfTexture' and record[1]==0:
                _,pos=self.properties(chunk)
                chunk=chunk[:pos]+classic_texture_tail(chunk[pos:])
            chunks.append(chunk)
        out=bytearray(self.replace_chunks(chunks))
        table,count,_=self.tables[4]
        for i in range(count):struct.pack_into('<H',out,table+i*24+2,8192)
        struct.pack_into('<I',out,96,zlib.crc32(out[table:table+count*24]))
        struct.pack_into('<I',out,4,163);struct.pack_into('<I',out,32,header_crc(out))
        checked=Resource(out)
        require(all(r[1]==8192 for r in checked.records),'Classic exports must be cooked')
        return bytes(out)

    def replace_chunks(self,chunks):
        require(len(chunks)==len(self.records),'Chunk count changed')
        table,count,_=self.tables[4];out=bytearray(self.data[:table])+bytearray(count*24)
        for i,(record,chunk) in enumerate(zip(self.records,chunks)):
            record=record.copy();record[3]=len(chunk);record[4]=len(out);record[6]=zlib.crc32(chunk)
            struct.pack_into('<HHIIIII',out,table+i*24,*record);out+=chunk
        struct.pack_into('<III',out,88,table,count,zlib.crc32(out[table:table+count*24]))
        struct.pack_into('<II',out,24,len(out),len(out));struct.pack_into('<I',out,32,header_crc(out))
        Resource(out);return bytes(out)


def fnv64(data):
    value=0xcbf29ce484222325
    for byte in data:value=((value^byte)*0x100000001b3)&0xffffffffffffffff
    return value


def classic_metadata_hash_rows(rows, file_count):
    """Write Classic hash lookup as (uint64 hash, int64 positive file ID).

    Frozen v7 inputs contain a low file-ID word followed by 0xFFFFFFFF.
    Preserving those 16 bytes makes the Classic int64 ID negative. Accept
    only the observed legacy/source encodings and validate the cross-index.
    The path hash and record order remain unchanged.
    """
    result=[]
    for row in rows:
        require(len(row)==16,'Metadata hash record width')
        path_hash,file_id,upper=struct.unpack('<QII',row)
        require(0<file_id<file_count,'Metadata hash file ID range')
        require(upper in (0,0xFFFFFFFF),'Unsupported metadata file ID encoding')
        result.append(struct.pack('<Qq',path_hash,file_id))
    return result


def sound_index(path):
    with Path(path).open('rb') as f:
        h=f.read(64);require(h[:4]==b'CS3W','Sound cache magic');version=struct.unpack_from('<I',h,4)[0]
        require(version in (1,2),'Sound cache version')
        if version==1:info,count,names,size=struct.unpack_from('<4I',h,16);checksum=struct.unpack_from('<Q',h,40)[0];width=12;fmt='<III'
        else:info,count,names,size=struct.unpack_from('<QQQI',h,16);checksum=struct.unpack_from('<Q',h,56)[0];width=24;fmt='<QQQ'
        f.seek(names);strings=f.read(size);f.seek(info);table=f.read(count*width)
        require(len(strings)==size and len(table)==count*width and fnv64(strings+table)==checksum,'Sound index checksum')
        output={}
        for no,off,length in struct.iter_unpack(fmt,table):
            name=strings[no:strings.index(0,no)].decode('utf8');require(name not in output and off+length<=names,'Sound entry range')
            output[name]=(off,length)
        return version,output


def write_sound_cache(bankdir,out):
    files=sorted(Path(bankdir).glob('*.bnk'))+sorted(Path(bankdir).glob('*.wem'))
    names=bytearray();table=bytearray();cursor=48
    for path in files:
        name=path.name.lower().encode('ascii');size=path.stat().st_size
        table+=struct.pack('<III',len(names),cursor,size);names+=name+b'\0';cursor+=size
    require(cursor+len(names)+len(table)<2**32,'Classic sound cache 32-bit limit')
    buffersize=(max(p.stat().st_size for p in files)+4095)&~4095
    header=b'CS3W'+struct.pack('<7IQQ',1,0,0,cursor+len(names),len(files),cursor,len(names),buffersize,fnv64(names+table))
    require(len(header)==48,'Sound header width')
    with Path(out).open('wb') as f:
        f.write(header)
        for path in files:
            with path.open('rb') as src:shutil.copyfileobj(src,f)
        f.write(names);f.write(table)
    version,index=sound_index(out);require(version==1 and len(index)==len(files),'Sound count')
    with Path(out).open('rb') as f:
        for path in files:
            off,size=index[path.name.lower()];f.seek(off)
            require(hashlib.sha256(f.read(size)).hexdigest()==sha(path),'Cached sound mismatch')
    return dict(version=version,fileCount=len(files),bankCount=sum(p.suffix=='.bnk' for p in files),mediaCount=sum(p.suffix=='.wem' for p in files),payloadsVerified=True,sha256=sha(out))
