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
completed_by_output = False
with (out / 'stdout.txt').open('wb') as stdout, (out / 'stderr.txt').open('wb') as stderr:
    process = subprocess.Popen(command, cwd=tool.parent, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                               creationflags=subprocess.CREATE_NO_WINDOW)
    print(json.dumps({'pid': process.pid, 'command': command}), flush=True)
    stable_at = None
    previous_blob = None
    while process.poll() is None:
        blob = out / 'compiled/blob.rsblob'
        size = blob.stat().st_size if blob.exists() else 0
        blob_signature = (size, hashlib.sha256(blob.read_bytes()).hexdigest()) if size else None
        transcript = (out / 'stdout.txt').read_text('utf8', errors='replace')
        success = 'Success! Patch scripts blob saved' in transcript and '[Script]: Error [' not in transcript
        if size > 0 and success:
            if blob_signature != previous_blob or stable_at is None:
                stable_at = time.time()
            elif stable_at is not None and time.time() - stable_at >= 2:
                # Updated Wcc may linger in Wwise shutdown after compilation.
                # Only close our child after its successful, stable blob is written.
                completed_by_output = True
                process.kill()
                process.wait(timeout=10)
                break
        else:
            stable_at = None
        previous_blob = blob_signature
        if time.time() - started >= args.timeout:
            timed_out = True
            process.kill()
            process.wait(timeout=10)
            break
        time.sleep(1)
patch_after = patch_snapshot()
artifacts = []
for path in out.rglob('*'):
    if path.is_file() and path.suffix.lower() in ('.redscripts', '.rsblob'):
        artifacts.append({'path': str(path), 'bytes': path.stat().st_size,
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest().upper()})
report = {'command': command, 'workingDirectory': str(tool.parent), 'exitCode': 0 if completed_by_output else process.returncode,
          'processExitCode': process.returncode, 'completedByOutput': completed_by_output, 'timedOut': timed_out,
          'humanReportedPriorLicenseAcceptance': args.terms_already_accepted,
          'elapsedSeconds': round(time.time() - started, 2), 'artifacts': artifacts,
          'patchSourcesBefore': patch_before, 'patchSourcesAfter': patch_after,
          'patchSourcesUnchangedDuringCompile': patch_before == patch_after,
          'note': 'An artifact/exit code alone is not confirmation of runtime or save round-trip.'}
(out / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, ensure_ascii=False), flush=True)
raise SystemExit(0 if report['exitCode'] == 0 and not timed_out and patch_before == patch_after else 1)
