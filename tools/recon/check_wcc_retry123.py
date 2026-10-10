"""Exercise the actual Wcc runner with deterministic process exit sequences."""
import contextlib
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
runner = ROOT / 'tools/recon/run_wcc_job.py'
checks = 0


def check(value, name):
    global checks
    if not value:
        raise AssertionError(name)
    checks += 1


with tempfile.TemporaryDirectory(dir=ROOT / 'BetaGwent/build', prefix='wcc-retry123-') as directory:
    for label, exits, expected_code, attempts in (
        ('shutdown-then-success', [0xC0000008, 0], 0, 2),
        ('real-failure', [2], 2, 1),
        ('repeated-shutdown', [0xC0000008] * 3, 0xC0000008, 3),
    ):
        job = Path(directory) / label
        remaining = iter(exits)

        class Process:
            def __init__(self, *args, **kwargs):
                self.pid = 1
                self.returncode = next(remaining)

            def poll(self):
                return self.returncode

        arguments = [str(runner), '--out', str(job), '--timeout', '10', '--', 'cookstrings']
        with patch.object(sys, 'argv', arguments), patch('subprocess.Popen', Process), contextlib.redirect_stdout(io.StringIO()):
            try:
                runpy.run_path(str(runner), run_name='__main__')
            except SystemExit as result:
                check(result.code == expected_code, label + ': exit status')
        report = json.loads((job / 'result.json').read_text('utf8'))
        check(len(report['attempts']) == attempts, label + ': bounded attempts')
        check(report['exitCode'] == expected_code, label + ': recorded result')
        check(not report['completedByOutput'], label + ': crash not accepted as completed output')

report = dict(stage=123, checks=checks, actualWccRunner=True, mockedProcessExits=True)
(ROOT / 'docs/evidence/wcc-retry123.json').write_text(json.dumps(report, indent=2) + '\n', 'utf8')
print(json.dumps(report))
