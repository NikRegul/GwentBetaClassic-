"""Profile WS must avoid operators that retail 1.32 compiles incorrectly.

0.9.3: "%" on large values broke the RNG on 1.32. 0.9.4: "?:" broke the
profile store section check and "%" broke 15-bit fact banks on 1.32, while the
JS checks (ws2js) evaluated both correctly. Use BetaGwentProfileMod / if-blocks.
"""
from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT/'BetaGwent/development/scripts/game/betagwent'
# collectionProfile.ws is not listed: its Park-Miller reward RNG keeps "%" on
# Next-Gen, and prepare091.py replaces that block with engine RandRange on 1.32.
NAMES = ['aaProfileStore.ws', 'deckProfile.ws', 'profileBackup.ws',
         'scrapsProfile.ws', 'kegProfile.ws', 'profileCleanup090.ws']

def code(line):
    line = re.sub(r'"(\\.|[^"\\])*"', '""', line)
    return line.split('//')[0]

def main():
    problems = []
    for name in NAMES:
        path = DIR/name
        if not path.exists():
            continue
        for number, line in enumerate(path.read_text('utf-8-sig').splitlines(), 1):
            c = code(line)
            if '%' in c:
                problems.append(f'{name}:{number}: "%" (use BetaGwentProfileMod)')
            if re.search(r'\?[^?]*:', c):
                problems.append(f'{name}:{number}: "?:" (use if)')
    helper = (DIR/'aaProfileStore.ws').read_text('utf-8-sig')
    if 'function BetaGwentProfileMod(value : int, maximum : int) : int' not in helper:
        problems.append('aaProfileStore.ws: BetaGwentProfileMod missing')
    def helper_mod(v, m):
        q = abs(v) // abs(m)
        q = q if (v >= 0) == (m > 0) else -q
        return v - q * m
    def cpp_mod(v, m):
        r = abs(v) % abs(m)
        return r if v >= 0 else -r
    for v in [0, 1, -1, 32767, 32768, 112103, -18969, 2147483647, -2147483647, 65520, 65521, 999999, 1000000]:
        for m in [32768, 65521, 1000000, 127773, 7]:
            if helper_mod(v, m) != cpp_mod(v, m):
                problems.append(f'helper mismatch {v} % {m}')
    print('CLASSIC132_OPS094', json.dumps(dict(complete=not problems, problems=problems)))
    return 1 if problems else 0

if __name__ == '__main__':
    sys.exit(main())
