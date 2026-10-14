"""Prepare a paired 0.6.3 / stage140 experiment on identical mechanics/deals."""
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'BetaGwent/build/audit140'
out=BASE/'compare-v3'
assert not (out/'run.json').exists(), 'Experiment already prepared'
shutil.copytree(BASE/'candidate-v3',out/'candidate')
for name in ('compare_ai.js','comparison_bridge119.js','replay119.js'):
    shutil.copy2(ROOT/'tools/ai'/name,out/name)
shutil.copy2(ROOT/'data/beta924/ai/rules.json',out/'profiles.json')
(out/'run.json').write_text(json.dumps(dict(cycles=1,seed=140062,
    candidateLabel='stage140',baselineLabel='0.6.3'),indent=2)+'\n','utf8')
print(out)
