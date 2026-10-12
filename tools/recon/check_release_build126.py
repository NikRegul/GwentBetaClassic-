"""Regression checks for an expanded UI contract and interrupted audio cook."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('presentation',ROOT/'tools/build_presentation94.py')
presentation=importlib.util.module_from_spec(spec);spec.loader.exec_module(presentation)
script=(ROOT/'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws').read_text('utf-8-sig')
bindings=sorted(set(presentation.re.findall(r'GetMemberFlashFunction\("([^"]+)"\)',script)))
checks=0
def check(value,name):
    global checks
    assert value,name
    checks+=1

presentation.validate_bindings(dict(passed=True,bindings=bindings),script)
check('markDeckEdited' in bindings,'new starter reset binding is part of the contract')
for report in [dict(passed=False,bindings=bindings),dict(passed=True,bindings=bindings[:-1]),dict(passed=True,bindings=bindings+['obsolete'])]:
    try:presentation.validate_bindings(report,script)
    except RuntimeError:checks+=1
    else:raise AssertionError('invalid bridge accepted')

with tempfile.TemporaryDirectory(dir=ROOT/'BetaGwent/build',prefix='audio-retry126-') as directory:
    base=Path(directory);split=base/'split.list';split.write_text('previous interrupted cook','utf8')
    exits=iter([0xC0000008,0]);started=[]
    class Process:
        def __init__(self,*args,**kwargs):
            check(not split.exists(),'each audio attempt receives a fresh split list')
            self.returncode=next(exits);self.pid=1
            split.write_text('attempt '+str(len(started)),'utf8');started.append(self.returncode)
        def poll(self):return self.returncode
    arguments=['runner','--out',str(base/'job'),'--timeout','10','--','cooksounds','-outsplitfile='+str(split)]
    with patch.object(sys,'argv',arguments),patch('subprocess.Popen',Process),contextlib.redirect_stdout(io.StringIO()):
        try:runpy.run_path(str(ROOT/'tools/recon/run_wcc_job.py'),run_name='__main__')
        except SystemExit as result:check(result.code==0,'retry succeeds')
    check((base/'job/audio-split-before-attempt0.list').read_text('utf8')=='previous interrupted cook','previous diagnostic is retained')
    check((base/'job/audio-split-before-attempt1.list').read_text('utf8')=='attempt 0','crashed attempt diagnostic is retained')
    check(split.read_text('utf8')=='attempt 1','successful final split list is retained')
report=dict(checks=checks,bindings=len(bindings),nativeWccMocked=True)
(ROOT/'docs/evidence/release-build126.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps(report))
