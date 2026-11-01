"""Read-only DXBC disassembly of the exact editor materials using Windows D3DCompiler."""
from pathlib import Path
import argparse, ctypes, gzip, hashlib, json, struct, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
from UnityPy.export.ShaderConverter import ShaderProgram
from UnityPy.streams import EndianBinaryReader
from UnityPy.helpers import CompressionHelper

def disassemble(code):
    start=code.index(b'DXBC');size=struct.unpack_from('<I',code,start+24)[0];dxbc=code[start:start+size]
    assert len(dxbc)==size
    dll=ctypes.WinDLL('d3dcompiler_47.dll')
    dll.D3DDisassemble.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_uint,ctypes.c_char_p,ctypes.POINTER(ctypes.c_void_p)]
    dll.D3DDisassemble.restype=ctypes.c_long
    data=ctypes.create_string_buffer(dxbc);blob=ctypes.c_void_p()
    result=dll.D3DDisassemble(data,len(dxbc),0,None,ctypes.byref(blob));assert result==0,hex(result)
    table=ctypes.cast(blob,ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    pointer=ctypes.WINFUNCTYPE(ctypes.c_void_p,ctypes.c_void_p)(table[3])(blob)
    length=ctypes.WINFUNCTYPE(ctypes.c_size_t,ctypes.c_void_p)(table[4])(blob)
    try:return dxbc,ctypes.string_at(pointer,length).decode('utf8').rstrip('\0')
    finally:ctypes.WINFUNCTYPE(ctypes.c_ulong,ctypes.c_void_p)(table[2])(blob)

def main():
    p=argparse.ArgumentParser();p.add_argument('--audit',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    out=a.out.resolve();assert out.is_relative_to(ROOT/'BetaGwent/build') and not out.exists()
    audit=json.loads((a.audit/'audit.json').read_text('utf8'));source=ROOT/audit['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==audit['sourceSha256']
    env=UnityPy.load(str(source));objects={str(o.path_id):o for o in env.objects};out.mkdir();results={}
    for sid,shader in audit['shaders'].items():
        obj=objects[sid];data=obj.read();dest=out/sid;dest.mkdir()
        (dest/'serialized.json.gz').write_bytes(gzip.compress(json.dumps(obj.read_typetree()).encode()))
        unique={};programs=[]
        for platform,offset,compressed,decompressed in zip(data.platforms,data.offsets,data.compressedLengths,data.decompressedLengths):
            if isinstance(offset,list):offset,compressed,decompressed=offset[0],compressed[0],decompressed[0]
            raw=CompressionHelper.decompress_lz4(bytes(data.compressedBlob)[offset:offset+compressed],decompressed)
            parsed=ShaderProgram(EndianBinaryReader(raw,endian='<'),obj.version)
            for i,sub in enumerate(parsed.m_SubPrograms):
                if not sub.m_ProgramCode or b'DXBC' not in sub.m_ProgramCode:continue
                code,assembly=disassemble(sub.m_ProgramCode);key=hashlib.sha256(code).hexdigest()
                if key not in unique:
                    file=dest/(str(len(unique))+'.asm');file.write_text(assembly,'utf8');file.with_suffix('.dxbc').write_bytes(code);unique[key]=file.name
                programs.append(dict(index=i,platform=int(platform),type=int(sub.m_ProgramType),keywords=sub.m_Keywords,sha256=key,file=unique[key]))
        results[sid]=dict(name=shader['name'],programs=programs,uniquePrograms=len(unique))
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    (out/'report.json').write_text(json.dumps(dict(sourceSha256=digest,shaders=results),indent=2),'utf8')
    print(json.dumps({v['name']:v['uniquePrograms'] for v in results.values()}))

if __name__=='__main__':main()
