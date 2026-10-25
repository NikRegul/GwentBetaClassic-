"""Fixed paired development/holdout comparison on92 unique compositions."""
from pathlib import Path
import argparse, collections, hashlib, json, math, shutil, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'))
from comparison_inputs import validate_snapshot
sys.path.insert(0,str(ROOT/'tools/features091'))
from parallel_tests091 import aggregate, atomic


def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--cycles',type=int,required=True)
    p.add_argument('--workers',type=int,default=4);p.add_argument('--kind',choices=['development','holdout'],required=True)
    a=p.parse_args();assert 1<=a.workers<=4 and 1<=a.cycles<=16
    out=a.out.resolve();assert out.is_relative_to(ROOT/'BetaGwent/build') and not out.exists()
    candidate=a.candidate.resolve();baseline=a.baseline.resolve();manifest=validate_snapshot(candidate)
    roster=ROOT/'BetaGwent/build/classic093-knockout-20261024-01/entrants.json'
    entrants=[e for e in json.loads(roster.read_text('utf8')) if e['group']=='hard'];pool=sorted(e['presetId'] for e in entrants)
    assert len(pool)==len(set(pool))==92
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    plan=dict(schema=1,kind=a.kind,candidateFingerprint=manifest['fingerprint'],baselineProofSha256=sha(baseline/'comparison.json'),
              rosterSha256=sha(roster),pool=pool,cycles=a.cycles,seed=a.seed,workers=a.workers,plannedGames=92*4*a.cycles,
              strength=4,simDamp=40,format='Same raw deals; independent mulligans; both policies on both compositions and mirrored initiative.',
              acceptance='Complete with0errors; positive point difference;99% lower bound above50% both by paired blocks and by composition clusters. Technical and regression gates separately required.',
              tools={n:sha(ROOT/'tools/ai'/n) for n in ['compare_all093c.js','comparison_bridge119.js','replay119.js','run_comparison093c.py']})
    out.mkdir();atomic(out/'plan.json',plan);jobs=[];started=time.monotonic()
    profiles=dict(profiles=[dict(presetId=e['presetId'],id=e['key'],title=e['title']) for e in entrants])
    for i in range(a.workers):
        folder=out/f'part-{i:02}';folder.mkdir();start=i*92//a.workers;count=(i+1)*92//a.workers-start
        shutil.copytree(candidate,folder/'candidate');shutil.copytree(baseline,folder/'baseline')
        for name in ['compare_all093c.js','comparison_bridge119.js','replay119.js']:shutil.copy2(ROOT/'tools/ai'/name,folder/name)
        atomic(folder/'profiles.json',profiles)
        atomic(folder/'run.json',dict(pool=pool,cycles=a.cycles,seed=a.seed,candidateLabel='0.9.3c candidate',baselineLabel='0.9.3b',
                                    randomMatchups=True,candidateStrength=4,baselineStrength=4,blockStart=start,blockCount=count,
                                    maximumKnowsStartingList=True,traceEvery=4,fastHost=True,simDamp=40))
        jobs.append(dict(folder=folder,blockStart=start,blockCount=count))
    for job in jobs:
        job['log']=(job['folder']/'worker.log').open('w',encoding='utf8')
        job['process']=subprocess.Popen(['node',str(job['folder']/'compare_all093c.js'),str(job['folder'])],cwd=ROOT,
                                       stdout=job['log'],stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    last=-1
    while True:
        reports=[]
        for job in jobs:
            try:reports.append(json.loads((job['folder']/'report.json').read_text('utf8')))
            except (OSError,json.JSONDecodeError):pass
        summary=aggregate(reports,plan['plannedGames']);summary.update(candidateFingerprint=manifest['fingerprint'],kind=a.kind,
                planSha256=sha(out/'plan.json'),wallSeconds=round(time.monotonic()-started,2),poolSize=92)
        clusters=collections.defaultdict(list)
        for job in jobs:
            try:r=json.loads((job['folder']/'report.json').read_text('utf8'))
            except (OSError,json.JSONDecodeError):continue
            blocks=collections.defaultdict(list)
            for g in r['games']:blocks[g['block']].append(g)
            for block,games in blocks.items():
                if len(games)!=4 or any(g.get('error') for g in games):continue
                anchor=pool[job['blockStart']+block%job['blockCount']]
                clusters[anchor].append(sum(.5 if g['winner']==3 else int(g['winner']==g['newSeat']+1) for g in games)/4)
        means=[sum(v)/len(v) for v in clusters.values()];n=len(means);mean=sum(means)/n if n else None
        se=math.sqrt(sum((x-mean)**2 for x in means)/(n-1)/n) if n>1 else None
        summary['compositionClusters']=n;summary['clusterLower99']=max(0,mean-2.576*se) if se is not None else None
        summary['clusterUpper99']=min(1,mean+2.576*se) if se is not None else None
        summary['acceptancePassed']=bool(summary['complete'] and summary['errors']==0 and summary['confirmedBetter'] and n==92 and summary['clusterLower99']>.5)
        atomic(out/'summary.json',summary)
        if last!=summary['completedGames']:
            print(json.dumps({k:summary[k] for k in ['completedGames','wins','losses','draws','errors','wallSeconds']}),flush=True);last=summary['completedGames']
        if all(job['process'].poll() is not None for job in jobs):break
        time.sleep(5)
    for job in jobs:job['log'].close()
    assert summary['complete'] and summary['errors']==0 and all(j['process'].returncode==0 for j in jobs),'Incomplete/errorful comparison'
    assert all(sha(ROOT/'tools/ai'/n)==h for n,h in plan['tools'].items()),'Runner tools changed during fixed comparison'
    print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
