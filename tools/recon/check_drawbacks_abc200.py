"""Inspect compiled enemy-hand methods, excluding bitmap tags from the ABC dump."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import struct
import subprocess
import zlib

ROOT=Path(__file__).resolve().parents[2]

def inspect(path,output):
    raw=path.read_bytes()
    if raw[:3]==b'CWS':data=b'FWS'+raw[3:8]+zlib.decompress(raw[8:])
    elif raw[:3]==b'FWS':data=raw
    else:raise ValueError('Unsupported SWF')
    tags=8+(5+4*(data[8]>>3)+7)//8+4
    kept=[];at=tags
    while at<len(data):
        begin=at;head=struct.unpack_from('<H',data,at)[0];at+=2;kind=head>>6;size=head&63
        if size==63:size=struct.unpack_from('<I',data,at)[0];at+=4
        end=at+size
        if end>len(data):raise ValueError('Invalid SWF tag')
        if kind in (69,82):kept.append(data[begin:end])
        at=end
        if kind==0:break
    body=data[8:tags]+b''.join(kept)+b'\0\0'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(b'FWS'+data[3:4]+struct.pack('<I',len(body)+8)+body)
    java=Path(r'C:\Program Files\Microsoft\jdk-11.0.12.7-hotspot\bin\java.exe')
    jar=ROOT/'tools/vendor/apache-royale-0.9.12/royale-asjs/lib/compiler-swfdump.jar'
    result=subprocess.run([str(java),'-jar',str(jar),'-abc',str(output)],capture_output=True,check=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
    dump=result.stdout.decode('utf8',errors='replace').replace('\r\n','\n');methods={}
    for name in ('drawBacks','enemyHandView191','drawEnemyHandStatuses191'):
        match=re.search(r'^  private function '+name+r'\([^\n]+\n  \{\n.*?^  \}',dump,re.M|re.S)
        if not match:continue
        text=match.group();metrics={key:int(re.search(r'//\s+'+key+r'\s+(\d+)',text)[1]) for key in ('method_info','max_stack','max_regs','code_length')}
        metrics['iteratorLoops']=len(re.findall(r'\bhasnext2\b',text));methods[name]=metrics
        output.with_name(output.stem+'-'+name+'.txt').write_text(text+'\n',encoding='utf8')
    return {'swf':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'methods':methods}

def main():
    p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    before=inspect(a.before,ROOT/'tmp/drawbacks200/before-abc.swf');after=inspect(a.after,ROOT/'tmp/drawbacks200/after-abc.swf')
    old=before['methods']['drawBacks'];new=after['methods']['drawBacks']
    checks={'oldCrashFingerprintMatches':old['code_length']==1172 and old['max_stack']==27 and old['max_regs']==22,
            'smallerRenderMethod':new['code_length']<old['code_length'],
            'fewerRenderLocals':new['max_regs']<old['max_regs'],
            'onlyOriginalIteratorInRender':new['iteratorLoops']==1,
            'helpersCompiled':all(n in after['methods'] for n in ('enemyHandView191','drawEnemyHandStatuses191'))}
    report={'before':before,'after':after,'checks':checks,'passed':all(checks.values()),'nativeGameTested':False}
    a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2));return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
