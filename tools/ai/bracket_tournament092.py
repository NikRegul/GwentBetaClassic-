"""Prepare or resume a frozen, balanced knockout tournament (46 decks)."""
from pathlib import Path
from contextlib import contextmanager
import argparse, datetime, hashlib, json, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

@contextmanager
def lock(out):
    import msvcrt
    with (out/'controller.lock').open('a+b') as f:
        if f.seek(0,2)==0:f.write(b'0');f.flush()
        f.seek(0)
        try:msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:raise SystemExit('Controller already running; refusing duplicate')
        try:yield
        finally:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--prepare',action='store_true')
    p.add_argument('--snapshot',type=Path);p.add_argument('--cycles',type=int,default=1)
    p.add_argument('--original-snapshot',type=Path);p.add_argument('--old-policy',type=Path)
    p.add_argument('--seed',type=int,default=923101600);p.add_argument('--workers',type=int,default=16)
    p.add_argument('--max-seed-pairs',type=int,default=6);p.add_argument('--sim-damp',type=int,default=40)
    p.add_argument('--deadline',default='2026-10-23T20:00:00+03:00');p.add_argument('--benchmark',action='store_true')
    a=p.parse_args();out=a.out.resolve();assert out.is_relative_to(ROOT/'BetaGwent/build') and out!=ROOT/'BetaGwent/build'
    if a.prepare:
        assert a.snapshot and not out.exists();assert 1<=a.cycles<=50 and 1<=a.workers<=18 and 2<=a.max_seed_pairs<=12 and 0<=a.sim_damp<=70
        from comparison_inputs import validate_snapshot
        snapshot=a.snapshot.resolve();m=validate_snapshot(snapshot);assert len(m['presets'])==46
        out.mkdir(parents=True);runner=out/'runner';runner.mkdir()
        for n in ['bracket_tournament092.js','bracket_schedule092.js','variant_decks092.js','report_bracket092.py','versioned_match092.js','comparison_bridge119.js']:
            shutil.copy2(ROOT/'tools/ai'/n,runner/n)
        assert bool(a.original_snapshot)==bool(a.old_policy)
        versioned=a.original_snapshot is not None
        if versioned:
            original=a.original_snapshot.resolve();old_policy=a.old_policy.resolve();old_manifest=validate_snapshot(original)
            proof=json.loads((old_policy/'comparison.json').read_text('utf8'))
            assert proof.get('original091') and Path(proof['candidate'])==snapshot and Path(proof['oldSnapshot'])==original
            assert proof['baselineRules']==sha(old_policy/'rules.js') and proof['sharedBattleMechanics']
            for n in ('runtime.js','harness.js'):assert sha(old_policy/n)==sha(snapshot/n)
            subprocess.run(['node',str(runner/'bracket_tournament092.js'),'--version-metadata',str(snapshot),str(original),str(out/'deck-metadata.json')],cwd=ROOT,check=True)
        else:subprocess.run(['node',str(runner/'bracket_tournament092.js'),'--metadata',str(snapshot),str(out/'deck-metadata.json')],cwd=ROOT,check=True)
        config=dict(snapshot=str(snapshot),out=str(out),cycles=a.cycles,seed=a.seed,workers=a.workers,maxSeedPairs=a.max_seed_pairs,simDamp=a.sim_damp,
                    strength=4,benchmark=a.benchmark,deadline=a.deadline,metadataSha256=sha(out/'deck-metadata.json'),controllerSha256=sha(Path(__file__)))
        config['versioned']=versioned
        if versioned:config.update(originalSnapshot=str(original),originalFingerprint=old_manifest['fingerprint'],oldPolicy=str(old_policy),oldPolicyFiles={n:sha(old_policy/n) for n in ('rules.js','runtime.js','harness.js','tunes.json','comparison.json')})
        datetime.datetime.fromisoformat(config['deadline'])
        (out/'config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n','utf8')
        (out/'runner-sha256.json').write_text(json.dumps({f.name:sha(f) for f in runner.iterdir()},indent=2)+'\n','utf8')
        print('PREPARED',out,flush=True);return
    assert not (out/'STOP').exists() and not (out/'cancelled.json').exists(),'Explicitly stopped/cancelled run cannot resume silently'
    config=json.loads((out/'config.json').read_text('utf8'));assert config['controllerSha256']==sha(Path(__file__)),'Controller changed'
    hashes=json.loads((out/'runner-sha256.json').read_text('utf8'))
    def verify():
        assert sha(out/'deck-metadata.json')==config['metadataSha256'],'Metadata changed'
        for n,h in hashes.items():assert sha(out/'runner'/n)==h,'Frozen runner changed: '+n
    with lock(out):
        verify();subprocess.run(['node',str(out/'runner/bracket_tournament092.js'),str(out/'config.json')],cwd=ROOT,check=True)
        verify();subprocess.run([sys.executable,'-X','utf8',str(out/'runner/report_bracket092.py'),str(out)],cwd=ROOT,check=True)
    print('COMPLETE',out,flush=True)

if __name__=='__main__':main()
