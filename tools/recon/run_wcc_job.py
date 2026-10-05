"""Run one documented Wcc operation, with bounded runtime and workspace logs."""
from pathlib import Path
import argparse,json,subprocess,time

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--timeout',type=int,default=180)
parser.add_argument('arguments',nargs=argparse.REMAINDER)
args=parser.parse_args()
root=Path(__file__).resolve().parents[2]
out=args.out.resolve()
if not out.is_relative_to(root) or not 1<=args.timeout<=600:raise SystemExit('Invalid output or timeout')
if (out/'result.json').exists():raise SystemExit('Use a fresh job directory')
out.mkdir(parents=True,exist_ok=True)
arguments=args.arguments[1:] if args.arguments[:1]==['--'] else args.arguments
tool=Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\x64_RedKit\wcc_lite.exe')
command=[str(tool),*arguments,'-agreetoterms','-wcclog='+str(out/'wcc.log')]
start=time.time();timeout=False
with (out/'stdout.txt').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
    process=subprocess.Popen(command,cwd=tool.parent,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
    print(json.dumps({'pid':process.pid,'command':command}),flush=True)
    try:process.wait(args.timeout)
    except subprocess.TimeoutExpired:timeout=True;process.kill();process.wait(10)
report=dict(command=command,exitCode=process.returncode,timedOut=timeout,seconds=round(time.time()-start,2),humanPreviouslyAcceptedWccTerms=True)
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps(report),flush=True)
raise SystemExit(1 if timeout else process.returncode)
