"""Resume the frozen night tournament and create its report only after completion.

Preparation is separate: the final snapshot, rosters and fixed schedule must be
reviewed before starting. This command never resumes the cancelled old tournament.
"""
from pathlib import Path
from contextlib import contextmanager
import argparse,datetime,hashlib,json,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
LATEST=ROOT/'BetaGwent/build/tournament-night092-latest.json'

@contextmanager
def controller_lock(out):
    import msvcrt
    with (out/'controller.lock').open('a+b') as handle:
        if handle.seek(0,2)==0:handle.write(b'0');handle.flush()
        handle.seek(0)
        try:msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:raise SystemExit('Tournament controller already running; no second run started')
        try:yield
        finally:handle.seek(0);msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path)
    p.add_argument('--snapshot',type=Path)
    p.add_argument('--prepare',action='store_true')
    p.add_argument('--workers',type=int,default=16)
    a=p.parse_args()
    if a.out:out=a.out.resolve()
    elif LATEST.exists() and not a.prepare:out=Path(json.loads(LATEST.read_text('utf8'))['path'])
    else:p.error('Provide --out for a new tournament')
    assert out.is_relative_to(ROOT/'BetaGwent/build') and out.name!='tournament092-ai3'
    config_path=out/'config.json'
    if a.prepare:
        assert a.snapshot and not out.exists(),'Fresh output and explicit frozen snapshot required'
        assert 1<=a.workers<=18
        sys.path.insert(0,str(ROOT/'tools/ai'))
        from comparison_inputs import validate_snapshot
        snapshot=a.snapshot.resolve();validate_snapshot(snapshot)
        subprocess.run(['node','tools/ai/prepare_night092.js',str(snapshot),str(out)],cwd=ROOT,check=True)
        config=json.loads((out/'config-proposal.json').read_text('utf8'))
        config.update(workers=a.workers,seed=923022307,blocksByStrength={'2':1,'3':1,'4':2},
            deadline='2026-10-23T07:30:00+03:00',
            protocolNote='49 entrants, all pairs at each difficulty, mirrored seats; 9408 games. Volume fixed before the first result, reduced before starting to retain deadline reserve.')
        config_path.write_text(json.dumps(config,ensure_ascii=False,indent=2),'utf8')
        runner=out/'runner';runner.mkdir()
        for name in ['tournament_night092.js','variant_decks092.js','report_tournament_night092.py']:
            shutil.copy2(ROOT/'tools/ai'/name,runner/name)
        frozen={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in runner.iterdir()}
        (out/'runner-sha256.json').write_text(json.dumps(frozen,indent=2),'utf8')
        print('PREPARED:',out,flush=True)
        return
    assert config_path.is_file() and not (out/'STOP').exists(),'Missing configuration or explicitly stopped tournament'
    for name,digest in json.loads((out/'runner-sha256.json').read_text('utf8')).items():
        assert hashlib.sha256((out/'runner'/name).read_bytes()).hexdigest()==digest,'Frozen tournament tool changed'
    LATEST.write_text(json.dumps(dict(path=str(out)),indent=2),'utf8')
    with controller_lock(out):
        subprocess.run(['node',str(out/'runner/tournament_night092.js'),str(config_path)],cwd=ROOT,check=True)
        subprocess.run([sys.executable,'-X','utf8',str(out/'runner/report_tournament_night092.py'),str(out)],cwd=ROOT,check=True)
    print('COMPLETE:',out,flush=True)

if __name__=='__main__':main()
