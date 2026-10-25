"""Isolated native compiler probe, never a release/package or installation."""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import BASE_SCRIPTS

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    assert not a.out.exists(),'Fresh technical probe required'
    a.out.mkdir(parents=True);shutil.copytree(BASE_SCRIPTS/'scripts',a.out/'scripts')
    target=a.out/'scripts/game/betagwent'
    for folder in [ROOT/'BetaGwent/scripts/game/betagwent',ROOT/'BetaGwent/development/scripts/game/betagwent',a.stage]:
        for file in folder.glob('*.ws'):shutil.copy2(file,target/file.name)
    (a.out/'compiler-probe.json').write_text(json.dumps(dict(scope='Native compiler/type checking of staged direct Beta WS modules. No release, archives, installation or enabled difficulty.',
        stage=str(a.stage),scripts={p.relative_to(a.out/'scripts').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((a.out/'scripts').rglob('*.ws'))}),indent=2)+'\n',encoding='utf8')
    print(a.out)

if __name__=='__main__':main()
