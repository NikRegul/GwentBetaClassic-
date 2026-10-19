"""0.9.0 build 7 scripts: build 5 scripts + two card fixes checked against Beta 0.9.24 graphs.

* Myrgtabrakke (112205): Beta deals 2 damage, then repeats while Counter (2) > 0
  with a decrement -> 3 hits in total (the mod did 2).
* Harald the Cripple (200161): Beta IntForeach Start 0, Num = Counter (9) + 1;
  IntForeachNode.IsFinished is index >= Start + Num -> 10 hits (the mod did 9).
Output: BetaGwent/build/release090-scripts7/scripts (input for prepare_final090 --scripts-from).
"""
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'BetaGwent/build/release090-final5/scripts'
OUT = ROOT / 'BetaGwent/build/release090-scripts7'
PATCHES = [
    ('game/betagwent/duelNeutral.ws', 'source.monsterRemaining=BetaGwentNorthPick(id==112111,3,2);', 'source.monsterRemaining=3;'),
    ('game/betagwent/duelNilf.ws', 'RandomDamage(source,enemy,s.locationMask,1,9);', 'RandomDamage(source,enemy,s.locationMask,1,10);'),
]


def main():
    assert not OUT.exists(), 'Fresh output folder required'
    shutil.copytree(SOURCE, OUT / 'scripts')
    for name, old, new in PATCHES:
        p = OUT / 'scripts' / name
        raw = p.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf')
        s = raw.decode('utf-8-sig')
        assert s.count(old) == 1, (name, old)
        p.write_bytes((b'\xef\xbb\xbf' if bom else b'') + s.replace(old, new).encode('utf8'))
    print('Prepared build 7 scripts: Myrgtabrakke 3 hits, Harald 10 hits.')


if __name__ == '__main__':
    main()
