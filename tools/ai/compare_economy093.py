"""Run all 46 four-game paired blocks in disjoint worker slices, with common deals."""
from pathlib import Path
import argparse, json, shutil, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'))
from comparison_inputs import validate_snapshot
sys.path.insert(0,str(ROOT/'tools/features091'))
from parallel_tests091 import aggregate, atomic

def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--workers',type=int,default=8);p.add_argument('--seed',type=int,default=2026102101)
    p.add_argument('--matchup-offset',type=int,default=0)
    p.add_argument('--cycles',type=int,default=1);p.add_argument('--random-matchups',action='store_true')
    p.add_argument('--strength',type=int,choices=[2,3,4],default=4);p.add_argument('--fast-host',action='store_true')
    p.add_argument('--sim-damp',type=int,choices=range(71),help='Fixed common search reduction in both arms (default 40)')
    p.add_argument('--resume',action='store_true',help='Resume saved shards only after the previous controller has stopped')
    a=p.parse_args();assert 0<=a.matchup_offset<45 and 1<=a.cycles<=30
    out=a.out.resolve();assert out.is_relative_to(ROOT/'BetaGwent/build') and out.exists()==a.resume;assert 1<=a.workers<=16
    candidate=a.candidate.resolve();baseline=a.baseline.resolve();identity=validate_snapshot(candidate)['fingerprint']
    out.mkdir(parents=True,exist_ok=a.resume);running=[];ranges=[];folders=[];start=time.monotonic()
    for i in range(a.workers):
        begin=i*46//a.workers;count=(i+1)*46//a.workers-begin;folder=out/f'part-{i:02}'
        config=dict(cycles=a.cycles,seed=a.seed,candidateLabel='candidate',baselineLabel='previous version',randomMatchups=a.random_matchups,
            candidateStrength=a.strength,baselineStrength=a.strength,blockStart=begin,blockCount=count,matchupOffset=a.matchup_offset,maximumKnowsStartingList=a.strength==4,traceEvery=4,fastHost=a.fast_host)
        if a.sim_damp is not None:config['simDamp']=a.sim_damp
        if a.resume:
            assert json.loads((folder/'run.json').read_text('utf8'))==config,'Changed experiment configuration'
            assert validate_snapshot(folder/'candidate')['fingerprint']==identity,'Changed candidate snapshot'
            assert (folder/'baseline/rules.js').read_bytes()==(baseline/'rules.js').read_bytes(),'Changed baseline rules'
        else:
            folder.mkdir();shutil.copytree(candidate,folder/'candidate');shutil.copytree(baseline,folder/'baseline')
            for n in ['compare_ai.js','comparison_bridge119.js','replay119.js']:shutil.copy2(ROOT/'tools/ai'/n,folder/n)
            shutil.copy2(ROOT/'data/beta924/ai/rules.json',folder/'profiles.json')
            (folder/'run.json').write_text(json.dumps(config),encoding='utf8')
        folders.append(folder);ranges.extend(range(begin,begin+count))
    assert sorted(ranges)==list(range(46)) and len(set(ranges))==46
    for folder in folders:
        if a.resume and json.loads((folder/'report.json').read_text('utf8'))['complete']:
            running.append((None,None,folder));continue
        log=(folder/'worker.log').open('a' if a.resume else 'w',encoding='utf8')
        command=['node',str(folder/'compare_ai.js'),str(folder)]+(['--resume'] if a.resume else [])
        process=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        running.append((process,log,folder))
    last=-1
    while True:
        reports=[]
        for process,log,folder in running:
            report=folder/'report.json'
            if report.exists():
                try:reports.append(json.loads(report.read_text('utf8')))
                except (OSError,json.JSONDecodeError):pass
        summary=aggregate(reports,184*a.cycles);summary.update(fingerprint=identity,seed=a.seed,matchupOffset=a.matchup_offset,randomMatchups=a.random_matchups,cycles=a.cycles,strength=a.strength,fastHost=a.fast_host,workers=a.workers,wallSeconds=round(time.monotonic()-start,2))
        atomic(out/'summary.json',summary)
        if last!=summary['completedGames']:
            print(json.dumps({k:summary[k] for k in ['completedGames','wins','losses','draws','errors','wallSeconds']}),flush=True);last=summary['completedGames']
        if all(process is None or process.poll() is not None for process,_,_ in running):break
        time.sleep(2)
    for process,log,_ in running:
        if log:log.close()
    assert summary['complete'] and summary['errors']==0 and all(process is None or process.returncode==0 for process,_,_ in running),'Incomplete/errorful benchmark'
    print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
