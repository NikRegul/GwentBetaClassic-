"""Write trained tunes (best.json from tools/ai/jshost/train.js) into BetaGwentAITune defaults.
python tools/ai/apply_tunes.py BetaGwent/training/js-YYYY-MM-DD/best.json
"""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
WS = ROOT / 'BetaGwent/development/scripts/game/betagwent/duelAIPass.ws'
JS = ROOT / 'tools/ai/jshost/runtime.js'
best = json.loads(Path(sys.argv[1]).read_text('utf8'))['best']
src = open(WS, encoding='utf-8-sig', newline='').read()
for k, v in best.items():
    src, n = re.subn(r'(case %s: return )-?\d+(;)' % k, r'\g<1>%d\2' % int(v), src, count=1)
    if n != 1: raise SystemExit('tune %s not found in duelAIPass.ws' % k)
open(WS, 'w', encoding='utf-8-sig', newline='').write(src)
js = JS.read_text('utf8')
m = re.search(r'const __tuneDefaults = \{([^}]*)\};', js)
d = {int(a): int(b) for a, b in re.findall(r'(\d+):\s*(-?\d+)', m[1])}
d.update({int(k): int(v) for k, v in best.items()})
js = js[:m.start()] + 'const __tuneDefaults = { ' + ', '.join('%d: %d' % kv for kv in sorted(d.items())) + ' };' + js[m.end():]
JS.write_text(js, 'utf8')
print('applied', best)
