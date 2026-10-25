"""Read-only inspection of the audited 1.32 sound-bank table and memory budget."""
from pathlib import Path
import csv,ctypes as C,hashlib,io,json,struct,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import AUDIO
GAME=Path(r'D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt\bin\x64\witcher3.exe')

def main():
    rows=list(csv.reader(io.StringIO(subprocess.check_output(['tasklist','/FI','IMAGENAME eq witcher3.exe','/FO','CSV','/NH'],text=True))))
    ids=[int(r[1]) for r in rows if r and r[0].lower()=='witcher3.exe']
    k=C.WinDLL('kernel32',use_last_error=True);p=C.WinDLL('psapi',use_last_error=True)
    k.OpenProcess.argtypes=[C.c_uint32,C.c_int,C.c_uint32];k.OpenProcess.restype=C.c_void_p
    k.CloseHandle.argtypes=[C.c_void_p]
    k.QueryFullProcessImageNameW.argtypes=[C.c_void_p,C.c_uint32,C.c_wchar_p,C.POINTER(C.c_uint32)]
    k.ReadProcessMemory.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_size_t,C.POINTER(C.c_size_t)]
    p.EnumProcessModulesEx.argtypes=[C.c_void_p,C.POINTER(C.c_void_p),C.c_uint32,C.POINTER(C.c_uint32),C.c_uint32]
    results=[]
    for pid in ids:
        handle=k.OpenProcess(0x410,False,pid)
        if not handle:continue
        try:
            path=C.create_unicode_buffer(32768);length=C.c_uint32(len(path))
            assert k.QueryFullProcessImageNameW(handle,0,path,C.byref(length))
            if Path(path.value).resolve()!=GAME.resolve():continue
            modules=(C.c_void_p*1024)();needed=C.c_uint32()
            assert p.EnumProcessModulesEx(handle,modules,C.sizeof(modules),C.byref(needed),3)
            base=modules[0]
            def read(rva,size):
                buf=C.create_string_buffer(size);got=C.c_size_t()
                assert k.ReadProcessMemory(handle,base+rva,buf,size,C.byref(got)) and got.value==size
                return buf.raw
            # Pinned native SoundLoadBank implementation; refuse a different executable.
            assert read(0x264750,6)==b'\x40\x53\x48\x81\xec\x50'
            table,count,current=struct.unpack('<QII',read(0x2bd9f58,16))
            maximum=struct.unpack('<I',read(0x291020c,4))[0];assert maximum==400*1024**2 and count<10000
            banks=[]
            for i in range(count):
                raw=read(table-base+i*24,24)
                refs,bankid,size,flags,name,status=struct.unpack('<6I',raw)
                banks.append(dict(index=i,references=refs,bankId=bankid,bytes=size,flags=flags,nameId=name,status=status))
            candidates=[r for r in banks if r['bytes']==261121906]
            split=AUDIO/'manifest.json'
            sizes={r['bytes']:r['name'] for r in json.loads(split.read_text('utf8'))['banks']} if split.exists() else {}
            results.append(dict(pid=pid,executable=str(GAME),executableSha256=hashlib.sha256(GAME.read_bytes()).hexdigest(),bankCount=count,
                loadedBankBytes=current,budgetBytes=maximum,remainingBytes=maximum-current,
                universalBetaBank=candidates,languageBetaBanks=[dict(r,name=sizes[r['bytes']]) for r in banks if r['bytes'] in sizes],
                largestBanks=sorted(banks,key=lambda r:-r['bytes'])[:12],readOnly=True))
        finally:k.CloseHandle(handle)
    print(json.dumps(results,indent=2))
    if results:
        out=ROOT/'BetaGwent/build/classic-audio091-sync1/native-bank-inspection.json'
        out.write_text(json.dumps(results,indent=2),'utf8')

if __name__=='__main__':main()
