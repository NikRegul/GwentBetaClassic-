"""Prepare/run mirrored matches: 0.9.1 vs 0.9.0, or maximum vs easy."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=['versions','difficulty']);p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--old',type=Path,default=ROOT/'BetaGwent/build/ai091/baseline')
    p.add_argument('--out',type=Path,required=True);p.add_argument('--resume',action='store_true')
    p.add_argument('--seed',type=int,default=91020621);p.add_argument('--cycles',type=int,default=1)
    a=p.parse_args();out=a.out.resolve()
    sys.path.insert(0,str(ROOT/'tools/ai'));from comparison_inputs import validate_snapshot
    validate_snapshot(a.candidate)
    if not a.resume:
        assert not out.exists(),'Use a fresh directory or --resume';out.mkdir(parents=True)
        shutil.copytree(a.candidate,out/'candidate')
        if a.mode=='versions':
            subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/ai/prepare_comparison115.py'),str(a.candidate.resolve()),str(a.old.resolve()),str(out/'baseline')],check=True,cwd=ROOT)
        else:
            shutil.copytree(a.candidate,out/'baseline')
            sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
            proof=dict(schema=1,baselineRules=sha(out/'baseline/rules.js'),sharedBattleMechanics=True,
                       sameDeckCatalogue=sha(out/'candidate/sources/BetaGwent/development/scripts/game/betagwent/duelCatalog.ws'),sessionPolicyMethods=['OpponentStep'],samePolicyDifferentDifficulty=True)
            (out/'baseline/comparison.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
        for n in ['compare_ai.js','comparison_bridge119.js','replay119.js']:shutil.copy2(ROOT/'tools/ai'/n,out/n)
        shutil.copy2(ROOT/'data/beta924/ai/rules.json',out/'profiles.json')
        config=dict(cycles=a.cycles,seed=a.seed,candidateLabel='0.9.1 maximum',candidateStrength=4,
                    baselineLabel='0.9.0 maximum' if a.mode=='versions' else '0.9.1 easy',baselineStrength=4 if a.mode=='versions' else 2,
                    mode=a.mode,maximumKnowsStartingList=True)
        (out/'run.json').write_text(json.dumps(config,indent=2),encoding='utf8')
    command=['node',str(out/'compare_ai.js'),str(out)]
    if a.resume:command.append('--resume')
    raise SystemExit(subprocess.run(command,cwd=ROOT).returncode)
if __name__=='__main__':main()
