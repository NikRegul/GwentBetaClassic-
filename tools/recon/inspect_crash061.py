"""Read narrowly scoped crash instructions, registers and PE RTTI (no game changes)."""
import hashlib,json, mmap, struct, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EXE=Path(r'F:\Steam\steamapps\common\The Witcher 3\bin\x64_dx12\witcher3.exe')
data=EXE.read_bytes()
pe=struct.unpack_from('<I',data,60)[0]
count=struct.unpack_from('<H',data,pe+6)[0]
opt=pe+24
base=struct.unpack_from('<Q',data,opt+24)[0]
section=opt+struct.unpack_from('<H',data,pe+20)[0]
sections=[struct.unpack_from('<8sIIII',data,section+i*40) for i in range(count)]
def read(rva,n):
    for name,virtual,size,rawsize,raw in sections:
        if size<=rva and rva+n<=size+rawsize:return data[raw+rva-size:raw+rva-size+n]
    raise ValueError(hex(rva))
def q(rva):return struct.unpack('<Q',read(rva,8))[0]
result={'executable':str(EXE),'sha256':hashlib.sha256(data).hexdigest(),
        'peTimestamp':struct.unpack_from('<I',data,pe+8)[0],'rtti':{},'dumps':[]}
for vtable in (0x3a72c08,0x3a72c58,0x3a6fd38):
    try:
        locator=q(vtable-8)-base
        sig,offset,cd,typ,cls,selfrva=struct.unpack('<6I',read(locator,24))
        result['rtti'][hex(vtable)]={'signature':sig,'name':read(typ+16,240).split(b'\0')[0].decode('ascii')}
    except Exception as error:result['rtti'][hex(vtable)]={'error':str(error)}
for pid in (22760,34804):
    path=Path(fr'C:\Users\NikR\AppData\Local\CrashDumps\witcher3.exe.{pid}.dmp')
    with path.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as dump:
        count,directory=struct.unpack_from('<II',dump,8)
        streams={}
        for i in range(count):
            kind,size,rva=struct.unpack_from('<III',dump,directory+12*i);streams[kind]=(size,rva)
        size,rva=streams[6];cs,cr=struct.unpack_from('<II',dump,rva+160)
        names=['rax','rcx','rdx','rbx','rsp','rbp','rsi','rdi','r8','r9','r10','r11','r12','r13','r14','r15','rip']
        regs=dict(zip(names,[hex(v) for v in struct.unpack_from('<17Q',dump,cr+120)]))
        result['dumps'].append({'pid':pid,'registers':regs})
tool=Path(r'C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.34.31933\bin\Hostx64\x64\dumpbin.exe')
for lo,hi in ((0xd29470,0xd295a0),(0xd380b0,0xd38140),(0xdf4380,0xdf4450)):
    text=subprocess.check_output([str(tool),'/disasm',f'/range:0x{base+lo:x},0x{base+hi:x}',str(EXE)],text=True)
    (ROOT/f'docs/evidence/crash061-disasm-{lo:x}.txt').write_text(text,'utf8')
(ROOT/'docs/evidence/crash061-analysis.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
print(json.dumps(result,indent=2))
