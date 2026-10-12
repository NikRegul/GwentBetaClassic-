"""Regression for the fresh REDkit cache header versus immutable audio payload."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from verify_release136 import compare_audio_cache

original=b'CS3W'+bytes(range(100))
fresh=bytearray(original);fresh[12:16]=b'new!'
assert not compare_audio_cache(original,bytes(fresh))['cacheByteIdentical']
assert compare_audio_cache(original,original)['cacheByteIdentical']
checks=2
for offset in (0,8,16,64,103):
    corrupt=bytearray(fresh);corrupt[offset]^=1
    try:compare_audio_cache(original,bytes(corrupt))
    except AssertionError:checks+=1
    else:raise AssertionError('Changed cache byte accepted: '+str(offset))
try:compare_audio_cache(original,bytes(fresh[:-1]))
except AssertionError:checks+=1
else:raise AssertionError('Truncated cache accepted')
sources=['tools/verify_release136.py','tools/recon/check_audio_cache136.py']
report=dict(checks=checks,actualVerifier=True,sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})
(ROOT/'docs/evidence/audio-cache136.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps(report))
