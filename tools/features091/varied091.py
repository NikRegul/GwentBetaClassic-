"""Independent seeded tactical positions at four search budgets."""
from pathlib import Path
import concurrent.futures, hashlib, json, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[2]

def main():
    snapshot=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(ROOT/'tools/ai'));from comparison_inputs import validate_snapshot
    manifest=validate_snapshot(snapshot);started=time.monotonic()
    def run(damp):
        result=out/f'damp-{damp}.json'
        command=['node',str(ROOT/'tools/ai/check_varied_tactics091.js'),str(snapshot),str(result),'128',str(91029001+damp*1009),str(damp)]
        r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=1800)
        (out/f'damp-{damp}.log').write_text(r.stdout+r.stderr,encoding='utf8')
        if r.returncode:raise RuntimeError((r.stdout+r.stderr)[-2000:])
        data=json.loads(result.read_text('utf8'));assert data['fingerprint']==manifest['fingerprint'] and not data['failed']
        return data
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:reports=list(pool.map(run,[0,40,70,100]))
    validate_snapshot(snapshot)
    families={}
    for r in reports:
        for case in r['results']:families[case['family']]=families.get(case['family'],0)+1
    summary=dict(fingerprint=manifest['fingerprint'],cases=sum(len(r['results']) for r in reports),failed=0,
                 seeds=[r['seed'] for r in reports],damping=[r['damp'] for r in reports],families=families,
                 seconds=round(time.monotonic()-started,2),actualWitcherScript=True,nativeGameTested=False)
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary))
if __name__=='__main__':main()
