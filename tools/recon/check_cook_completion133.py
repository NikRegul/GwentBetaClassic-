"""Exercise actual cooker completion and retry logic without running REDkit."""
import ast,contextlib,io,json,runpy,sys,tempfile,time
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
runner=ROOT/'tools/recon/run_wcc_job.py'
tree=ast.parse(runner.read_text('utf8'))
functions=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('size','outputs_ready')],type_ignores=[])
checks=0
def check(value,name):
    global checks
    assert value,name
    checks+=1

with tempfile.TemporaryDirectory(dir=ROOT/'BetaGwent/build',prefix='cook-completion133-') as directory:
    base=Path(directory);out=base/'probe';out.mkdir()
    old=b'Cooking finished in 1s\n';stdout=out/'stdout.txt';stdout.write_bytes(old+b'Start cooking\n')
    database=base/'cook.db';menu=base/'menu.redswf'
    database.write_bytes(b'database');menu.write_bytes(b'partial resource')
    now=time.time();clock=[now]
    class Clock:
        @staticmethod
        def time():return clock[0]
    scope=dict(expect=[database,menu],arguments=['cook'],out=out,cook_stdout_offset=len(old),time=Clock)
    exec(compile(functions,str(runner),'exec'),scope)
    ready=scope['outputs_ready'];stable={}
    check(not ready(now,stable),'old completion and new cook.db cannot authorize shutdown')
    stdout.write_bytes(old+b'Cooking finished in 1s\n')
    check(not ready(now,stable),'completed resources must first become stable')
    clock[0]+=9
    check(ready(now,stable),'current completion and stable resources authorize shutdown')
    menu.write_bytes(b'')
    check(not ready(now,stable),'empty menu prevents shutdown completion')
    menu.write_bytes(b'complete resource')

    cooked=base/'cooked';cooked.mkdir();(cooked/'partial').write_text('old','utf8')
    job=base/'jobs/cook';exits=iter([0xC0000008,0]);attempts=[]
    class Process:
        def __init__(self,*args,**kwargs):
            check(not cooked.exists(),'each retry starts without partial cooked resources')
            cooked.mkdir();(cooked/'partial').write_text('attempt '+str(len(attempts)),'utf8')
            self.returncode=next(exits);self.pid=1;attempts.append(self.returncode)
        def poll(self):return self.returncode
    argv=['runner','--out',str(job),'--fresh-cook-output',str(cooked),'--timeout','10','--','cook']
    with patch.object(sys,'argv',argv),patch('subprocess.Popen',Process),contextlib.redirect_stdout(io.StringIO()):
        try:runpy.run_path(str(runner),run_name='__main__')
        except SystemExit as result:check(result.code==0,'clean retry succeeds')
    check((job/'cooked-before-attempt0/partial').read_text('utf8')=='old','old partial diagnostic preserved')
    check((job/'cooked-before-attempt1/partial').read_text('utf8')=='attempt 0','crashed attempt diagnostic preserved')
    check((cooked/'partial').read_text('utf8')=='attempt 1','successful output retained')

report=dict(stage=133,checks=checks,actualRunnerFunctions=True,nativeWccMocked=True)
(ROOT/'docs/evidence/cook-completion133.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps(report))
