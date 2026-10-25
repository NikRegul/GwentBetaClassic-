"""Start a new 0.9.1 candidate from a finished one without redoing tests and native compiles.

Copies the frozen sources, test results, checkpoints and both compile results of the
source candidate into a fresh output folder (archives are NOT copied), together with
the Classic compile record keyed by the folder name. build091.py --resume then re-checks
every frozen hash and cached test fingerprint and packages new archives, now with the
Classic 1.32 sound bank list fix. Scripts and AI stay byte-identical to the source.
"""
from pathlib import Path
import argparse, json, shutil, sys

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'BetaGwent/build'
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import CLASSIC_RUNTIME
RUNS=CLASSIC_RUNTIME/'runs'
SKIP={'archives','release.json'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--from',dest='source',default='release091-candidate5')
    p.add_argument('--to',dest='target',default='release091-candidate6')
    a=p.parse_args()
    source=BUILD/a.source;target=BUILD/a.target
    assert (source/'source-freeze.json').is_file(),'Source candidate missing: '+str(source)
    assert (source/'compile-nextgen-final/result.json').is_file(),'Next-Gen compile missing in source'
    assert (RUNS/a.source/'result.json').is_file(),'Classic compile record missing: '+str(RUNS/a.source)
    assert not target.exists(),'Target exists, choose a new --to: '+str(target)
    assert not (RUNS/a.target).exists(),'Classic run record exists for target: '+str(RUNS/a.target)
    target.mkdir()
    for item in source.iterdir():
        if item.name in SKIP:continue
        if item.is_dir():shutil.copytree(item,target/item.name)
        else:shutil.copy2(item,target/item.name)
    shutil.copytree(RUNS/a.source,RUNS/a.target)
    # Cached test proofs record the output folder in their command; point them at the new
    # folder so build091 reuses them. Fingerprints and tool hashes are still re-checked.
    for proof in (target/'checkpoints').glob('*.json'):
        record=json.loads(proof.read_text('utf8'))
        record['command']=[x.replace(str(source),str(target)) for x in record['command']]
        proof.write_text(json.dumps(record,indent=2),encoding='utf8')
    (target/'cloned-from.json').write_text(json.dumps(dict(source=a.source,reason='Classic 1.32 sound bank list fix (Seven Cats q601 hang)',
        scriptsUnchanged=True,copied=sorted(i.name for i in source.iterdir() if i.name not in SKIP)),indent=2),encoding='utf8')
    print('CLONED',source,'->',target,flush=True)

if __name__=='__main__':main()
