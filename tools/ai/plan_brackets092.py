"""Choose whole balanced cycles from an uncontended final-snapshot speed check."""
from pathlib import Path
import argparse,datetime,json,math,sys

def choose(speed,available_seconds,reserve_seconds=1800,max_pairs=6,entrants=46):
    assert speed['workers']>=1 and speed['gamesPerSecond']>0 and speed['p95GameSeconds']>0
    # Both observed parallel throughput and a conservative per-worker tail
    # bound must fit. Also reserve a full longest bracket path plus reporting.
    safe_rate=min(speed['gamesPerSecond']*.60,speed['workers']/(speed['p95GameSeconds']*1.5))
    assert entrants in (46,92)
    critical_path=(6 if entrants==46 else 7)*max_pairs*2*speed['p95GameSeconds']
    budget=max(0,available_seconds-reserve_seconds-critical_path)
    maximum_per_cycle=23*(entrants-1)*max_pairs*2
    cycles=math.floor(budget*safe_rate/maximum_per_cycle)
    return dict(cycles=cycles,brackets=cycles*23,entrants=entrants,maximumGames=cycles*maximum_per_cycle,minimumGames=cycles*23*(entrants-1)*4,
                safeGamesPerSecond=safe_rate,criticalPathReserveSeconds=critical_path,reportReserveSeconds=reserve_seconds,
                conservativeRunSeconds=cycles*maximum_per_cycle/safe_rate+critical_path if cycles else 0,
                maximumSeedPairs=max_pairs)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--benchmark',type=Path,required=True);p.add_argument('--snapshot',type=Path,required=True)
    p.add_argument('--start',default='2026-10-23T16:00:00+03:00');p.add_argument('--deadline',default='2026-10-23T20:00:00+03:00')
    p.add_argument('--workers',type=int,default=16);p.add_argument('--max-seed-pairs',type=int,default=6);p.add_argument('--out',type=Path)
    a=p.parse_args();from comparison_inputs import validate_snapshot
    m=validate_snapshot(a.snapshot.resolve());benchmark=json.loads((a.benchmark/'benchmark.json').read_text('utf8'))
    assert benchmark['complete'] and benchmark['identity']['fingerprint']==m['fingerprint'],'Benchmark must use the exact final rules'
    assert benchmark['speed']['workers']==a.workers,'Measure the chosen worker count; do not extrapolate parallel speed'
    start=datetime.datetime.fromisoformat(a.start);deadline=datetime.datetime.fromisoformat(a.deadline);assert start.tzinfo and deadline.tzinfo
    config=json.loads((a.benchmark/'config.json').read_text('utf8'));entrants=92 if config.get('versioned') else 46
    if config.get('versioned'):
        import hashlib
        for n,h in config['oldPolicyFiles'].items():assert hashlib.sha256((Path(config['oldPolicy'])/n).read_bytes()).hexdigest()==h
        assert benchmark['identity']['versionComparison']['oldPolicyFiles']==config['oldPolicyFiles']
    start=max(start,datetime.datetime.now(datetime.timezone.utc));result=choose(benchmark['speed'],(deadline-start).total_seconds(),max_pairs=a.max_seed_pairs,entrants=entrants)
    assert result['cycles']>=1,'Not enough measured capacity for a balanced cycle: reduce tie-break limit BEFORE starting or free the machine and remeasure'
    result.update(fingerprint=m['fingerprint'],benchmark=str(a.benchmark.resolve()),start=start.isoformat(),deadline=deadline.isoformat(),workers=a.workers)
    if a.out:a.out.write_text(json.dumps(result,indent=2)+'\n','utf8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
