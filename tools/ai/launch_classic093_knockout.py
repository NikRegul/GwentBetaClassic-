"""Wait for the verified final build, benchmark, freeze and run knockout grids."""
import argparse,datetime,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def replace(source,dest):
    for attempt in range(101):
        try:source.replace(dest);return
        except PermissionError:
            if attempt==100:raise
            time.sleep(.02)
def main():
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--grids',type=int,default=16);p.add_argument('--workers',type=int,default=4);p.add_argument('--resume',action='store_true');a=p.parse_args()
    a.build=a.build.resolve();a.out=a.out.resolve();assert 1<=a.grids<=64 and 1<=a.workers<=4
    assert a.out.is_relative_to(ROOT/'BetaGwent/build') and a.out!=ROOT/'BetaGwent/build'
    a.out.mkdir(parents=True,exist_ok=True);lock=a.out/'launcher.lock'
    with lock.open('x',encoding='utf8') as f:f.write(json.dumps(dict(pid=os.getpid(),started=now())))
    status=dict(status='waiting-for-verified-build',pid=os.getpid(),started=now(),build=str(a.build),out=str(a.out),grids=a.grids,workers=a.workers)
    def save():
        status['lastActivity']=now();tmp=a.out/'launch.json.tmp';tmp.write_text(json.dumps(status,indent=2)+'\n','utf8');replace(tmp,a.out/'launch.json')
    def run(name,args):
        status['step']=name;save()
        with (a.out/(name+'.log')).open('a' if a.resume else 'w',encoding='utf8') as log:subprocess.run([str(x) for x in args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    try:
        if not a.resume:assert not (a.out/'plan.json').exists(),'Tournament already prepared; do not duplicate'
        if not (a.out/'plan.json').exists():
            while not (a.build/'release.json').exists():
                if (a.build/'cancelled.json').exists() or (a.build/'build-failed.json').exists():raise RuntimeError('Build failed/superseded; tournament will not start')
                timestamps=[f.stat().st_mtime for f in (a.build/'logs').glob('*') if f.is_file()]
                if timestamps and time.time()-max(timestamps)>1800:raise RuntimeError('Build output stale for30min; inspect before retry')
                save();time.sleep(15)
            status['status']='verifying-final-build';save()
            if not (a.build/'archive-verification.json').exists():run('independent-build-verification',[sys.executable,'-X','utf8','tools/features093/verify093.py',a.build])
            if not (a.out/'preflight-config.json').exists():run('prepare-inputs',['node','tools/ai/prepare_classic093_knockout.cjs',a.build,a.out,a.grids,a.workers])
            runner=a.out/'frozen/tools/ai/run_classic093_knockout.cjs'
            status['status']='benchmarking-before-plan-freeze';save()
            if not (a.out/'benchmark.json').exists():run('benchmark',['node',runner,a.out,'--benchmark'])
            run('freeze-plan',['node','tools/ai/prepare_classic093_knockout.cjs',a.build,a.out,a.grids,a.workers,'--finalize-plan'])
        plan=json.loads((a.out/'plan.json').read_text('utf8'));status.update(minimumGames=plan['minimumGames'],maximumGames=plan['maximumGames'],estimatedHours=plan['estimatedHours'],status='tournament-running')
        assert plan['grids']==a.grids and plan['workers']==a.workers,'Resume settings must match the frozen plan'
        runner=a.out/'frozen/tools/ai/run_classic093_knockout.cjs';command=['node',str(runner),str(a.out)]
        if a.resume:command+=['--resume']
        with (a.out/'tournament.log').open('a' if a.resume else 'w',encoding='utf8') as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);status['runnerPid']=child.pid;save()
            while child.poll() is None:
                progress=a.out/'progress.json'
                if progress.exists():
                    snapshot=json.loads(progress.read_text('utf8'));status['progress']=snapshot
                    stamp=datetime.datetime.fromisoformat(snapshot['lastActivity'].replace('Z','+00:00'))
                    if (datetime.datetime.now(datetime.timezone.utc)-stamp).total_seconds()>1800:raise RuntimeError('Tournament progress stale for30min')
                    if snapshot.get('lastGameActivity'):
                        stamp=datetime.datetime.fromisoformat(snapshot['lastGameActivity'].replace('Z','+00:00'))
                        if (datetime.datetime.now(datetime.timezone.utc)-stamp).total_seconds()>1800:raise RuntimeError('No completed tournament game for30min')
                save();time.sleep(15)
            assert child.returncode==0,'Tournament failed; preserve results/logs and inspect before explicit resume'
        report=json.loads((a.out/'report.json').read_text('utf8'));assert report['complete'] and report['errors']==0
        status['status']='complete';status['completedGames']=report['games'];save()
    except BaseException as e:
        status['status']='failed';status['error']=repr(e)
        child=locals().get('child')
        if child is not None and child.poll() is None:child.terminate();child.wait(timeout=20)
        save();raise
    finally:lock.unlink(missing_ok=True)
if __name__=='__main__':main()
