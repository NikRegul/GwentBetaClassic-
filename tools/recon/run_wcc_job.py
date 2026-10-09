"""Run one documented Wcc operation, with bounded runtime and workspace logs.

Stage 105 hardening: on this machine wcc_lite sometimes never exits although its
work is done, or stalls during start-up. The runner therefore
  * finishes the job when the expected output (--expect) is written and stable,
    then closes the lingering process (reported as completedByOutput);
  * restarts a stalled attempt (no log growth and no output for --stall seconds)
    up to --retries times, keeping every attempt's log;
  * still fails on the overall --timeout.
"""
from pathlib import Path
import argparse,json,subprocess,time

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--timeout',type=int,default=180)
parser.add_argument('--expect',type=Path,action='append',default=[],help='Output file(s) whose appearance means the job is done')
parser.add_argument('--stall',type=int,default=240)
parser.add_argument('--retries',type=int,default=2)
parser.add_argument('arguments',nargs=argparse.REMAINDER)
args=parser.parse_args()
root=Path(__file__).resolve().parents[2]
out=args.out.resolve()
if not out.is_relative_to(root) or not 1<=args.timeout<=3600:raise SystemExit('Invalid output or timeout')
if (out/'result.json').exists():raise SystemExit('Use a fresh job directory')
out.mkdir(parents=True,exist_ok=True)
arguments=args.arguments[1:] if args.arguments[:1]==['--'] else args.arguments
tool=Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\x64_RedKit\wcc_lite.exe')
log=out/'wcc.log'
command=[str(tool),*arguments,'-agreetoterms','-wcclog='+str(log)]
expect=[p.resolve() for p in args.expect]

def size(p):
    try:return p.stat().st_size
    except OSError:return -1
def outputs_ready(started,stable):
    if not expect:return False
    ready=True
    for p in expect:
        try:st=p.stat()
        except OSError:ready=False;continue
        if st.st_mtime<started-2 or st.st_size<=0:ready=False;continue
        if stable.get(p)!=st.st_size:
            stable[p]=st.st_size;stable[str(p)+'@']=time.time();ready=False
        elif time.time()-stable[str(p)+'@']<8:ready=False
    return ready

start=time.time();attempts=[];result=None
for attempt in range(args.retries+1):
    if log.exists():log.replace(out/f'wcc-attempt{attempt}.log')
    began=time.time();stable={};last_size=-1;last_change=began;state='running'
    with (out/'stdout.txt').open('ab') as stdout,(out/'stderr.txt').open('ab') as stderr:
        # Own minimised console: without a console wcc_lite could hang (07.10.2026).
        info=subprocess.STARTUPINFO();info.dwFlags|=subprocess.STARTF_USESHOWWINDOW;info.wShowWindow=7
        process=subprocess.Popen(command,cwd=tool.parent,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NEW_CONSOLE,startupinfo=info)
        print(json.dumps({'pid':process.pid,'attempt':attempt,'command':command}),flush=True)
        while True:
            code=process.poll()
            if code is not None:state='exited';break
            now=time.time()
            if now-start>args.timeout:state='timeout';break
            current=size(log)
            if current!=last_size:last_size=current;last_change=now
            if outputs_ready(began,stable):
                # Output finished; give the process a short grace period to exit by itself.
                try:process.wait(15);state='exited'
                except subprocess.TimeoutExpired:state='completedByOutput'
                break
            if now-last_change>args.stall and not any(size(p)>0 and p.stat().st_mtime>=began-2 for p in expect):state='stalled';break
            time.sleep(1)
        if state in ('timeout','stalled','completedByOutput'):
            process.kill()
            try:process.wait(15)
            except subprocess.TimeoutExpired:pass
    attempts.append(dict(attempt=attempt,state=state,exitCode=process.returncode,seconds=round(time.time()-began,2)))
    print(json.dumps(attempts[-1]),flush=True)
    if state=='stalled' and attempt<args.retries:continue
    result=state;break

ok=result=='completedByOutput' or (result=='exited' and process.returncode==0)
report=dict(command=command,exitCode=0 if result=='completedByOutput' else process.returncode,timedOut=result in ('timeout','stalled'),
            completedByOutput=result=='completedByOutput',attempts=attempts,seconds=round(time.time()-start,2),humanPreviouslyAcceptedWccTerms=True)
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps(report),flush=True)
raise SystemExit(0 if ok else (process.returncode or 1))
