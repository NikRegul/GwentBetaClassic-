"""Supervised Wcc compile probe. Writes only an explicit workspace build directory."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--patch', type=Path)
parser.add_argument('--timeout', type=int, default=120)
parser.add_argument('--terms-already-accepted', action='store_true',
                    help='Only use after the human has personally accepted the Wcc license.')
args = parser.parse_args()
workspace = Path(r'D:\w3mod').resolve()
out = args.out.resolve()
if not out.is_relative_to(workspace):
    raise SystemExit('Output must be within D:\\w3mod')
if args.timeout < 1 or args.timeout > 300:
    raise SystemExit('Timeout must be 1..300 seconds')
out.mkdir(parents=True, exist_ok=True)
(out / 'compiled').mkdir(exist_ok=True)
if any(path.suffix.lower() in ('.redscripts', '.rsblob') for path in (out / 'compiled').rglob('*') if path.is_file()):
    raise SystemExit('Use a fresh output directory: previous compiled artifacts are present')


def patch_snapshot():
    if not args.patch:
        return []
    patch_root = args.patch.resolve()
    if not patch_root.is_dir():
        raise SystemExit('Patch directory does not exist')
    return [{'path': path.relative_to(patch_root).as_posix(),
             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(patch_root.rglob('*.ws'))]


patch_before = patch_snapshot()
tool = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\x64_RedKit\wcc_lite.exe')
source = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\r4data\scripts')
command = [str(tool), 'compilescripts', str(source), '-out=' + str(out / 'compiled'),
           '-wcclog=' + str(out / 'wcc.log')]
if args.patch:
    command.append('-patch=' + str(args.patch.resolve()))
if args.terms_already_accepted:
    command.append('-agreetoterms')
started = time.time()
timed_out = False
with (out / 'stdout.txt').open('wb') as stdout, (out / 'stderr.txt').open('wb') as stderr:
    process = subprocess.Popen(command, cwd=tool.parent, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                               creationflags=subprocess.CREATE_NO_WINDOW)
    print(json.dumps({'pid': process.pid, 'command': command}), flush=True)
    try:
        process.wait(timeout=args.timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait(timeout=10)
patch_after = patch_snapshot()
artifacts = []
for path in out.rglob('*'):
    if path.is_file() and path.suffix.lower() in ('.redscripts', '.rsblob'):
        artifacts.append({'path': str(path), 'bytes': path.stat().st_size,
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest().upper()})
report = {'command': command, 'workingDirectory': str(tool.parent), 'exitCode': process.returncode, 'timedOut': timed_out,
          'humanReportedPriorLicenseAcceptance': args.terms_already_accepted,
          'elapsedSeconds': round(time.time() - started, 2), 'artifacts': artifacts,
          'patchSourcesBefore': patch_before, 'patchSourcesAfter': patch_after,
          'patchSourcesUnchangedDuringCompile': patch_before == patch_after,
          'note': 'An artifact/exit code alone is not confirmation of runtime or save round-trip.'}
(out / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, ensure_ascii=False), flush=True)
