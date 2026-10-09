"""Import only a confirmed result against the exact source snapshot, with rollback."""
import datetime, hashlib, json, os, re, sys
from pathlib import Path
from snapshot import ROOT, inputs, fingerprint, verify
WS=ROOT/'BetaGwent/development/scripts/game/betagwent/duelAIPass.ws'
JS=ROOT/'tools/ai/jshost/runtime.js'
def main():
    file=Path(sys.argv[1]).resolve();state=json.loads(file.read_text('utf8'))
    manifest=verify(file.parent/'snapshot')
    if state.get('schema')!=2 or state.get('fingerprint')!=manifest['fingerprint']:raise ValueError('Incompatible result')
    proof=state.get('acceptedProof')
    if not proof or not proof.get('accepted'):raise ValueError('No confirmed improvement; game AI remains unchanged')
    for name in ('result','confirmation'):
        r=proof[name]
        if r['E']!=0 or r['lower']<=.5 or len(r['blocks'])<40:raise ValueError('Acceptance gate failed: '+name)
    if proof['historical']['E']!=0 or proof['historical']['mean']<.5:raise ValueError('Historical gate failed')
    if state['best']!=proof['candidate']:raise ValueError('Result and confirmed candidate disagree')
    # Same validation contract as the frozen trainer; no accepting arbitrary keys/values.
    import subprocess
    subprocess.run(['node','-e',"require(process.argv[1]).validate(JSON.parse(process.argv[2]))",str(file.parent/'snapshot/contract.js'),json.dumps(state['best'])],check=True)
    ws=WS.read_bytes();js=JS.read_bytes();source=ws.decode('utf-8-sig');runtime=js.decode('utf8')
    for k,v in state['best'].items():
        source,n=re.subn(r'(case %s: return )-?\d+(;)'%k,r'\g<1>%d\2'%v,source,count=1)
        if n!=1:raise ValueError('Missing tune '+k)
    defaults={int(k):int(v) for k,v in re.findall(r'case (\d+): return (-?\d+);',source.split('function BetaGwentAITune(',1)[1].split('// Average public value',1)[0])}
    runtime,n=re.subn(r'const __tuneDefaults = \{[^}]*\};','const __tuneDefaults = '+json.dumps(defaults)+';',runtime)
    if n!=1:raise ValueError('Missing JS defaults')
    backup=ROOT/'BetaGwent/training/backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f');backup.mkdir(parents=True)
    (backup/'duelAIPass.ws').write_bytes(ws);(backup/'runtime.js').write_bytes(js)
    targets=[(WS,(b'\xef\xbb\xbf' if ws.startswith(b'\xef\xbb\xbf') else b'')+source.encode('utf8')),(JS,runtime.encode('utf8'))]
    try:
        for p,data in targets:p.with_suffix(p.suffix+'.tmp').write_bytes(data)
        if fingerprint(inputs())!=manifest['fingerprint']:raise ValueError('Sources changed during import')
        for p,data in targets:os.replace(p.with_suffix(p.suffix+'.tmp'),p)
    except BaseException:
        WS.write_bytes(ws);JS.write_bytes(js);raise
    (backup/'import.json').write_text(json.dumps({'result':str(file),'fingerprint':manifest['fingerprint'],'tunes':state['best']},indent=2),'utf8')
    print('Imported confirmed tunes. Backup:',backup,'; rebuild required')
if __name__=='__main__':main()
