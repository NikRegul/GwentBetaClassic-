"""Adopt existing profile screens, then run their separate holdout. No build/install."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[2]
STATE=ROOT/'BetaGwent/drafts/day-iteration-20261023/state.json'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def main():
    p=argparse.ArgumentParser();p.add_argument('screen',type=Path);p.add_argument('gaps',type=Path);p.add_argument('out',type=Path);p.add_argument('confirmation',type=Path);p.add_argument('mapping',type=Path)
    p.add_argument('--resume-confirmation',action='store_true');p.add_argument('--workers',type=int,default=1);a=p.parse_args()
    assert 1<=a.workers<=12
    assert a.out.exists() if a.resume_confirmation else not a.out.exists(),'Use a fresh directory, or explicitly resume a stopped confirmation'
    a.out.mkdir(parents=True,exist_ok=a.resume_confirmation);lock=a.out/'exclusive.lock'
    with lock.open('x',encoding='utf8') as f:f.write(json.dumps(dict(pid=os.getpid(),started=now())))
    status=dict(status='waiting-for-existing-screens',pid=os.getpid(),started=now(),screen=str(a.screen),gaps=str(a.gaps),confirmation=str(a.confirmation),mapping=str(a.mapping),buildForbidden=True)
    def save():
        status['lastActivity']=now();(a.out/'workflow.json').write_text(json.dumps(status,indent=2)+'\n','utf8')
        d=json.loads(STATE.read_text('utf8'));x=d['userRequestedNextRelease']['profileMapping']
        if x.get('cancelRequested'):raise RuntimeError('Profile workflow cancellation requested in saved state')
        x['workflow']=dict(out=str(a.out),**status);d['lastBackgroundActivity']=now()
        tmp=STATE.with_suffix('.profile-workflow.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8');tmp.replace(STATE)
    def run(name,args):
        status['step']=name;save()
        with (a.out/(name+'.log')).open('w',encoding='utf8') as f:subprocess.run([str(v) for v in args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
    try:
        while True:
            snapshots=[]
            for folder in [a.screen,a.gaps]:
                d=json.loads((folder/'progress.json').read_text('utf8'));assert d['errors']==0 and d['status'] in ['running','complete'],d
                stamp=datetime.datetime.fromisoformat(d['lastActivity'].replace('Z','+00:00'))
                if d['status']=='running' and (datetime.datetime.now(datetime.timezone.utc)-stamp).total_seconds()>1800:raise RuntimeError('Screen progress stale for30min: '+str(folder))
                snapshots.append(dict(out=str(folder),completed=d['completed'],total=d['total'],status=d['status'],lastActivity=d['lastActivity']))
            status['screens']=snapshots;save()
            if all(d['status']=='complete' for d in snapshots):break
            time.sleep(60)
        if not a.resume_confirmation:
            status['status']='preparing-independent-confirmation';save()
            for i,folder in enumerate([a.screen,a.gaps]):run('screen-analysis-'+str(i),[sys.executable,'-X','utf8','tools/ai/analyze_beta_profile_trials093.py',folder])
            run('prepare-confirmation',[sys.executable,'-X','utf8','tools/ai/prepare_beta_profile_confirmation093.py',a.screen,a.gaps,a.confirmation])
        else:
            # An operator must first prove old processes stopped and audit the
            # saved prefix. The runner repeats the frozen source/prefix audit.
            run('resume-prefix-audit',[sys.executable,'-X','utf8','tools/ai/analyze_beta_profile_trials093.py',a.confirmation,'--audit-only'])
        status['status']='varied-opponent-confirmation-running';save()
        # One owner, optional worker threads; immutable jobs and sources remain
        # unchanged. It never launches compilers or package commands.
        log=(a.out/'confirmation.log').open('a' if a.resume_confirmation else 'w',encoding='utf8')
        runner='tools/ai/run_beta_profile_parallel093.cjs' if a.workers>1 else 'tools/ai/run_beta_profile_trials093.cjs'
        command=['node',runner,str(a.confirmation)]
        if a.workers>1:command+=['--workers',str(a.workers)]
        if a.resume_confirmation:command+=['--resume']
        child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        status['workers']=a.workers
        status['confirmationPid']=child.pid;save()
        while child.poll() is None:
            progress=a.confirmation/'progress.json'
            if progress.exists():
                progress_state=json.loads(progress.read_text('utf8'));status['confirmationProgress']=progress_state
                stamp=datetime.datetime.fromisoformat(progress_state['lastActivity'].replace('Z','+00:00'))
                if (datetime.datetime.now(datetime.timezone.utc)-stamp).total_seconds()>1800:raise RuntimeError('Confirmation progress stale for30min')
            save();time.sleep(60)
        log.close();assert child.returncode==0,'Confirmation runner failed; preserve logs and completed prefix'
        run('equivalence',['node','tools/ai/beta_profile_equivalence093.cjs',a.screen,a.out/'equivalence.json'])
        run('finalize-mapping',[sys.executable,'-X','utf8','tools/ai/finalize_beta_profile_mapping093.py',a.confirmation,a.out/'equivalence.json',a.mapping])
        status['status']='js-mapping-ready-ws-verification-required';status['mappingSha256']=hashlib.sha256(a.mapping.read_bytes()).hexdigest();save()
    except BaseException as e:
        status['status']='failed';status['error']=repr(e)
        # Stop only the confirmation process owned by this coordinator; never
        # create/restart adopted runs or label an error a game loss.
        child=locals().get('child')
        if child is not None and child.poll() is None:child.terminate();child.wait(timeout=20)
        (a.out/'workflow.json').write_text(json.dumps(status,indent=2)+'\n','utf8')
        raise
    finally:lock.unlink(missing_ok=True)

if __name__=='__main__':main()
