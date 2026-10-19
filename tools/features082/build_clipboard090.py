"""Build the clipboard-only native module, optional loader and isolated tests."""
from pathlib import Path
import os,subprocess,json,hashlib,sys,argparse
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'BetaGwent/native/clipboard'
OUT=ROOT/'BetaGwent/build/clipboard090'

def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=OUT)
    OUT=parser.parse_args().out.resolve()
    assert OUT.is_relative_to(ROOT/'BetaGwent/build')
    assert not OUT.exists(),'Keep prior native candidates immutable'
    OUT.mkdir(parents=True)
    msvc=Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.34.31933')
    sdk=Path('C:/Program Files (x86)/Windows Kits/10');ver='10.0.22000.0'
    env=dict(os.environ)
    env['PATH']=str(msvc/'bin/Hostx64/x64')+';'+env['PATH']
    env['INCLUDE']=';'.join(str(p) for p in [msvc/'include',*[sdk/'Include'/ver/k for k in ['shared','um','ucrt']]])
    env['LIB']=';'.join(str(p) for p in [msvc/'lib/x64',sdk/'Lib'/ver/'um/x64',sdk/'Lib'/ver/'ucrt/x64'])
    cl=str(msvc/'bin/Hostx64/x64/cl.exe')
    flags=['/nologo','/std:c++17','/O2','/W4','/WX','/wd4191','/MT','/EHsc','/guard:cf','/DUNICODE','/D_UNICODE','/Fo'+str(OUT)+'\\']
    builds=[('module',['bridge.cpp','module.cpp'],'GwentBetaClipboard.asi',True),
            ('loader',['loader.cpp'],'dinput8.dll',True),('test',['bridge.cpp','test.cpp'],'clipboard_bridge_test.exe',False)]
    for label,files,name,dll in builds:
        cmd=[cl,*flags,*(['/LD'] if dll else []),*[str(SRC/f) for f in files],'/Fe'+str(OUT/name),'/link','/WX','/DYNAMICBASE','/NXCOMPAT','user32.lib',*(['/DEF:'+str(SRC/'loader.def')] if label=='loader' else [])]
        result=subprocess.run(cmd,cwd=OUT,env=env,capture_output=True,text=True,errors='replace')
        (OUT/(label+'-build.log')).write_text(result.stdout+result.stderr,'utf8')
        print(label,result.returncode,flush=True)
        if result.returncode:print(result.stdout+result.stderr);raise SystemExit(1)
    files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in OUT.iterdir() if p.suffix in ['.asi','.dll','.exe']}
    (OUT/'build.json').write_text(json.dumps(dict(compiler=cl,flags=flags,files=files,inGameVerified=False),indent=2),'utf8')
    print(json.dumps(files),flush=True)

if __name__=='__main__':main()
