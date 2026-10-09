"""Minimal CR2W v164 rewriter for GUI resources (stage 109).

Appends strings/names/imports and replaces the single export payload, recomputing
table offsets, table CRCs, export checksum, file sizes and the header CRC
(0xDEADBEEF fill, as tools/ui/update_board_resource.header_crc). Existing string
offsets, name and import indices are never changed. A no-op rebuild must be
byte-identical to the input (checked by selftest).
"""
import struct,zlib,sys
from pathlib import Path

def fnv0(name):
    h=0x811c9dc5
    for x in name.encode()+b'\0':h^=x;h=(h*0x01000193)&0xffffffff
    return h

def header_crc(data):
    h=bytearray(data[:160]);struct.pack_into('<I',h,32,0xDEADBEEF);return zlib.crc32(h)

class Res:
    def __init__(self,data):
        self.d=bytes(data);t=[struct.unpack_from('<III',self.d,40+i*12) for i in range(10)]
        assert self.d[:4]==b'CR2W' and struct.unpack_from('<I',self.d,4)[0]==164
        assert all(x==(0,0,0) for x in t[5:]),'unsupported tables'
        o,n,_=t[0];self.strings=bytearray(self.d[o:o+n])
        o,n,_=t[1];self.names=[list(struct.unpack_from('<II',self.d,o+i*8)) for i in range(n)]
        o,n,_=t[2];self.imports=[list(struct.unpack_from('<IHH',self.d,o+i*8)) for i in range(n)]
        o,n,_=t[3];self.t3=self.d[o:o+n*16];self.t3n=n
        o,n,_=t[4];self.exports=[list(struct.unpack_from('<HHIIIII',self.d,o+i*24)) for i in range(n)]
        self.payloads=[self.d[e[4]:e[4]+e[3]] for e in self.exports]
        end=max(e[4]+e[3] for e in self.exports);assert end==len(self.d),'trailing data'
        assert [e[4] for e in self.exports]==sorted(e[4] for e in self.exports)
    def name_list(self):return [self.strings[o:self.strings.index(0,o)].decode() for o,_ in self.names]
    def add_string(self,s):
        off=len(self.strings);self.strings+=s.encode()+b'\0';return off
    def add_name(self,s):
        names=self.name_list()
        if s in names:return names.index(s)
        self.names.append([self.add_string(s),fnv0(s)]);return len(self.names)-1
    def add_import(self,path,cls,flags):
        ci=self.add_name(cls);self.imports.append([self.add_string(path),ci,flags]);return len(self.imports)
    def build(self):
        head=bytearray(self.d[:160]);body=bytearray()
        pos=160
        def table(i,blob,count):
            nonlocal pos
            struct.pack_into('<III',head,40+i*12,pos if count else 0,count,zlib.crc32(blob) if count else 0)
            body.extend(blob);pos+=len(blob)
        table(0,bytes(self.strings),len(self.strings))
        table(1,b''.join(struct.pack('<II',*n) for n in self.names),len(self.names))
        table(2,b''.join(struct.pack('<IHH',*n) for n in self.imports),len(self.imports))
        table(3,self.t3,self.t3n)
        exports_at=pos;table(4,b'\0'*24*len(self.exports),len(self.exports))
        out=head+body;data_pos=len(out);ex=bytearray()
        for e,p in zip(self.exports,self.payloads):
            e[3]=len(p);e[4]=data_pos+len(ex);e[6]=zlib.crc32(p);ex+=p
        etab=b''.join(struct.pack('<HHIIIII',*e) for e in self.exports)
        out[exports_at:exports_at+len(etab)]=etab
        struct.pack_into('<III',out,40+4*12,exports_at,len(self.exports),zlib.crc32(etab))
        out+=ex;struct.pack_into('<II',out,24,len(out),len(out));struct.pack_into('<I',out,32,header_crc(out))
        return bytes(out)

def prop(r,name,kind,value):
    return struct.pack('<HHI',r.add_name(name),r.add_name(kind),len(value)+4)+value

def selftest(path):
    d=Path(path).read_bytes();assert Res(d).build()==d,'no-op rebuild differs: '+str(path)

if __name__=='__main__':
    for p in sys.argv[1:]:selftest(p);print('identical',p)
