"""Reproduce long output inventories using the actual Wcc runner with a fake process."""
import contextlib
import inspect
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]


def main():
    with tempfile.TemporaryDirectory(prefix='expected137-',dir=ROOT/'BetaGwent/build') as directory:
        base=Path(directory)
        paths=[base/('resource-'+str(i).zfill(4)+'.redswf') for i in range(400)]
        listing=base/'outputs.json'
        listing.write_text(json.dumps(list(map(str,paths))),'utf8')
        calls=[]
        class Process:
            def __init__(self,*args,**kwargs):
                scope=inspect.currentframe().f_back.f_globals
                assert scope['expect']==paths
                assert '--expect-list' not in args[0], 'Runner flags leaked to native Wcc'
                self.returncode=0;self.pid=1;calls.append(1)
            def poll(self):return 0
        argv=['runner','--out',str(base/'job'),'--expect-list',str(listing),'--','cookstrings']
        with patch.object(sys,'argv',argv),patch.object(subprocess,'Popen',Process),contextlib.redirect_stdout(io.StringIO()):
            try:runpy.run_path(str(ROOT/'tools/recon/run_wcc_job.py'),run_name='__main__')
            except SystemExit as result:assert result.code==0
        assert calls==[1]
        listing.write_text('[17]','utf8')
        argv[2]=str(base/'invalid')
        with patch.object(sys,'argv',argv),patch.object(subprocess,'Popen',Process):
            try:runpy.run_path(str(ROOT/'tools/recon/run_wcc_job.py'),run_name='__main__')
            except SystemExit as result:assert 'JSON array of strings' in str(result.code)
            else:raise AssertionError('Invalid list accepted')
        assert calls==[1]
    print('PASS: actual runner loads 400 expected paths without long argv and rejects invalid list')


if __name__=='__main__':main()
