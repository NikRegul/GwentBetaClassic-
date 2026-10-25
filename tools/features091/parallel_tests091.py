"""18-process paired experiments with distinct deals AND archetype matchups."""
from pathlib import Path
import argparse, ctypes, hashlib, json, math, os, shutil, subprocess, time, sys
ROOT=Path(__file__).resolve().parents[2]

def read(p):
    # Node publishes reports with atomic rename. Antivirus/indexers can briefly
    # hold either name on Windows; a missing sample is not a failed experiment.
    for attempt in range(12):
        try:return json.loads(p.read_text('utf8'))
        except (PermissionError,FileNotFoundError,json.JSONDecodeError):time.sleep(.025*(attempt+1))
    return None
def atomic(p,data):
    temp=p.with_suffix('.tmp');temp.write_text(json.dumps(data,indent=2),encoding='utf8')
    for attempt in range(30):
        try:temp.replace(p);return
        except PermissionError:time.sleep(.025*(attempt+1))
    raise OSError('Cannot publish '+str(p))
def aggregate(reports,planned):
    blocks=[b for r in reports for b in r.get('blocks',[])]
    wins=sum(r.get('wins',0) for r in reports);losses=sum(r.get('losses',0) for r in reports);draws=sum(r.get('draws',0) for r in reports)
    errors=sum(r.get('errors',0) for r in reports);n=len(blocks);mean=sum(blocks)/n if n else None
    se=math.sqrt(sum((b-mean)**2 for b in blocks)/(n-1)/n) if n>1 else None
    low=max(0,mean-2.576*se) if se is not None else None;high=min(1,mean+2.576*se) if se is not None else None
    complete=sum(r.get('completedGames',0) for r in reports)==planned
    games=[g for r in reports for g in r.get('games',[])];pairs={tuple(sorted((g['left'],g['right']))) for g in games}
    metrics={}
    for version in ['candidate','baseline']:
        entries=[g.get('policyMetrics',{}).get(version,{}) for g in games];decisions=sum(e.get('decisions',0) for e in entries)
        events={}
        for e in entries:
            for name,count in e.get('events',{}).items():events[name]=events.get(name,0)+count
        metrics[version]=dict(decisions=decisions,meanMilliseconds=sum(e.get('milliseconds',0) for e in entries)/decisions if decisions else None,
                              peakMilliseconds=max([e.get('peakMilliseconds',0) for e in entries] or [0]),events=events)
    return dict(plannedGames=planned,completedGames=sum(r.get('completedGames',0) for r in reports),wins=wins,losses=losses,draws=draws,errors=errors,
                matchupPairs=len(pairs),distinctDeals=len({(*sorted((g['left'],g['right'])),g['seed']) for g in games}),policyMetrics=metrics,
                scoreRate=(wins+.5*draws)/(wins+losses+draws) if wins+losses+draws else None,
                pairedBlocks=n,lower99=low,upper99=high,complete=complete,confirmedBetter=bool(complete and not errors and low is not None and low>.5))

def prepare_shard(candidate,baseline,out,mode,index):
    out.mkdir(parents=True)
    assert out.resolve().is_relative_to((ROOT/'BetaGwent/build').resolve())
    shutil.copytree(candidate,out/'candidate');shutil.copytree(baseline if mode=='versions' else candidate,out/'baseline')
    if mode=='difficulty':
        sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        atomic(out/'baseline/comparison.json',dict(schema=1,baselineRules=sha(out/'baseline/rules.js'),sharedBattleMechanics=True,
            sameDeckCatalogue=sha(out/'candidate/sources/BetaGwent/development/scripts/game/betagwent/duelCatalog.ws'),sessionPolicyMethods=['OpponentStep'],samePolicyDifferentDifficulty=True))
    for n in ['compare_ai.js','comparison_bridge119.js','replay119.js']:shutil.copy2(ROOT/'tools/ai'/n,out/n)
    shutil.copy2(ROOT/'data/beta924/ai/rules.json',out/'profiles.json')
    atomic(out/'run.json',dict(cycles=1,seed=(91020620+(index+1)*2654435761+(mode=='difficulty'))&0xffffffff,
        candidateLabel='0.9.1 maximum',baselineLabel='0.9.0 maximum' if mode=='versions' else '0.9.1 easy',
        candidateStrength=4,baselineStrength=4 if mode=='versions' else 2,matchupOffset=index,traceEvery=46,
        maximumKnowsStartingList=True,mode=mode))

def main():
    p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=18);p.add_argument('--shards',type=int,default=18)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--old',type=Path,default=ROOT/'BetaGwent/build/ai091/baseline')
    p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    assert 1<=a.workers<=18 and 1<=a.shards<=23
    out=a.out.resolve();assert out.is_relative_to((ROOT/'BetaGwent/build').resolve());out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(ROOT/'tools/ai'))
    from comparison_inputs import validate_snapshot
    manifest=validate_snapshot(a.candidate)
    identity=dict(candidate=manifest['fingerprint'],old=validate_snapshot(a.old)['fingerprint'],shards=a.shards)
    if (out/'identity.json').exists():assert read(out/'identity.json')==identity,'Resume inputs differ'
    else:atomic(out/'identity.json',identity)
    baseline=out/'old-policy'
    if not baseline.exists():subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/ai/prepare_comparison115.py'),str(a.candidate.resolve()),str(a.old.resolve()),str(baseline)],cwd=ROOT,check=True)
    jobs=[]
    for index in range(a.shards):
        for mode in ['versions','difficulty']:
            target=out/f'{mode}-{index:02}'
            if not target.exists():prepare_shard(a.candidate.resolve(),baseline,target,mode,index)
            jobs.append(dict(mode=mode,index=index,path=target))
    prior=read(out/'summary.json') if (out/'summary.json').exists() else {}
    prior=prior or {};elapsed=prior.get('seconds',0);peak=prior.get('peakActiveWorkers',prior.get('activeWorkers',0))
    running={};failed=[];started=time.monotonic();last=-1;cache={}
    allowed_mask=None
    if os.name=='nt':
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.GetCurrentProcess.restype=ctypes.c_void_p
        process_mask=ctypes.c_size_t();system_mask=ctypes.c_size_t()
        kernel.GetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
        kernel.GetProcessAffinityMask(kernel.GetCurrentProcess(),ctypes.byref(process_mask),ctypes.byref(system_mask))
        cpus=[i for i in range(64) if process_mask.value&(1<<i)]
        assert len(cpus)>=a.workers,'Insufficient allowed CPU processors'
        allowed_mask=sum(1<<i for i in cpus[:a.workers])
        kernel.SetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
    while True:
        reports={};pending=[]
        cancelled=(out/'STOP').exists()
        if cancelled:
            for process,log in running.values():
                if process.poll() is None:process.terminate()
            for process,log in running.values():process.wait(timeout=30);log.close()
            running.clear()
        for j in jobs:
            name=str(j['path']);report=j['path']/'report.json'
            if report.exists():
                fresh=read(report)
                if fresh is not None:cache[name]=fresh
            if name in cache:reports[name]=cache[name]
            if reports.get(name,{}).get('complete'):continue
            if name in failed:continue
            if name not in running:pending.append(j)
        for name,(process,log) in list(running.items()):
            status=process.poll()
            if status is not None:
                log.close();del running[name]
                if status:failed.append(name)
        slots=0 if cancelled else max(0,a.workers-len(running))
        for j in pending[:slots]:
            name=str(j['path']);log=(j['path']/'worker.log').open('a',encoding='utf8')
            command=['node',str(j['path']/'compare_ai.js'),name]
            if (j['path']/'report.json').exists():command.append('--resume')
            process=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            if allowed_mask is not None:
                if not kernel.SetProcessAffinityMask(int(process._handle),allowed_mask):raise OSError(ctypes.get_last_error(),'Cannot set worker CPU affinity')
            running[name]=(process,log)
        peak=max(peak,len(running))
        summary=dict(workers=a.workers,activeWorkers=len(running),peakActiveWorkers=peak,managerPid=os.getpid(),workerPids=[p.pid for p,l in running.values()],cancelled=cancelled,identity=identity,cpuAffinityMask=allowed_mask,logicalProcessors=os.cpu_count(),
                     seconds=round(elapsed+time.monotonic()-started,2),failed=failed,experiments={})
        for mode in ['versions','difficulty']:
            group=[reports[str(j['path'])] for j in jobs if j['mode']==mode and str(j['path']) in reports]
            summary['experiments'][mode]=aggregate(group,a.shards*184)
        atomic(out/'summary.json',summary)
        completed=sum(r['completedGames'] for r in summary['experiments'].values())
        if completed!=last:
            print(json.dumps(dict(completed=completed,total=a.shards*368,active=summary['activeWorkers'],failed=len(failed))),flush=True);last=completed
        if cancelled or all(r['complete'] for r in summary['experiments'].values()) and not running:break
        if failed and not running:break
        time.sleep(3)
    if cancelled or failed or any(r['errors'] or not r['complete'] for r in summary['experiments'].values()):raise SystemExit(1)

if __name__=='__main__':main()
