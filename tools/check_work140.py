"""Audit current AI/UI against frozen WS; keep reports apart from accepted 0.6.2."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'BetaGwent/build/audit140/regressions'
SNAPSHOT=ROOT/'BetaGwent/build/audit140/candidate-v3'

def main():
    BASE.mkdir(parents=True,exist_ok=True)
    preload=BASE/'redirect.js'
    preload.write_text("const fs=require('fs'),path=require('path'),write=fs.writeFileSync;"
        "fs.writeFileSync=function(file,...args){if(typeof file==='string'){const p=path.resolve(file),prefix=path.resolve('docs/evidence')+path.sep;"
        "if(p.startsWith(prefix)){file=path.join(__dirname,'legacy-evidence',path.relative(prefix,p));fs.mkdirSync(path.dirname(file),{recursive:true});}}return write.call(fs,file,...args);};",'utf8')
    commands=[]
    for name in ('check_consume_self','scenarios123','scenarios124','scenarios125',
        'check_followups126','check_engines126','check_weather_visual126',
        'check_decisive127','check_ships127','check_concede127','check_tutor127',
        'check_preventive127','check_clearrisk127','check_draug127','check_combo127',
        'check_no_targets127','check_losing131','check_cavalry131','check_ciri131',
        'check_policy133','check_hidden_information133','check_spy138','check_chase139','check_strategy140','check_deck_combos128'):
        commands.append(['node',f'tools/ai/{name}.js',str(SNAPSHOT),str(BASE/(name+'.json'))])
    commands.append(['node','tools/ai/check_before_after140.js'])
    for name in ('check_controller123','check_catalog123','check_optional124',
        'check_halfcast126','check_controller126','check_timing126',
        'check_card_presentation126','check_followups127','check_presentation133',
        'check_ux135','check_release137','check_leader_release137','check_fixes061',
        'check_polish138','check_motion139','check_effects140'):
        commands.append(['node','-r',str(preload),f'tools/ui/{name}.js',
            *(['--source-only','--stage138'] if name=='check_fixes061' else [str(BASE/(name+'.json'))])])
    commands.append([sys.executable,'-X','utf8','tools/ai/check_locals133.py'])
    records=[]
    for command in commands:
        script=next(a for a in command if a.startswith('tools/'))
        log=BASE/(Path(script).stem+'.log')
        with log.open('wb') as output:
            result=subprocess.run(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT)
        records.append(dict(script=script,exitCode=result.returncode,sha256=hashlib.sha256((ROOT/script).read_bytes()).hexdigest(),log=str(log)))
        print(('PASS ' if result.returncode==0 else 'FAIL ')+script,flush=True)
        if result.returncode:print(log.read_text('utf8',errors='replace')[-4500:],flush=True)
    report=dict(stage=140,checks=records,passed=all(c['exitCode']==0 for c in records),nativeGameTested=False,
        fingerprint=json.loads((SNAPSHOT/'manifest.json').read_text('utf8'))['fingerprint'])
    (ROOT/'docs/evidence/regressions140.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    if not report['passed']:sys.exit(1)

if __name__=='__main__':main()
