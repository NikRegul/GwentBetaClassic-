"""Prepare a paired 0.6.2 / stage139 experiment on identical mechanics/deals."""
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'BetaGwent/build/audit139'
out=BASE/'compare'
assert not (out/'run.json').exists(), 'Experiment already prepared'
shutil.copytree(BASE/'candidate',out/'candidate')
for name in ('compare_ai.js','comparison_bridge119.js','replay119.js'):
    shutil.copy2(ROOT/'tools/ai'/name,out/name)
shutil.copy2(ROOT/'data/beta924/ai/rules.json',out/'profiles.json')
(out/'run.json').write_text(json.dumps(dict(cycles=1,seed=139062,
    candidateLabel='stage139',baselineLabel='0.6.2'),indent=2)+'\n','utf8')
print(out)
