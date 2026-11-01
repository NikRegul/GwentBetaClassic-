"""Compile the 0.9.0 final scripts for Next-Gen with REDkit wcc_lite (Windows).

Success needs the compiler's own success line, a fresh blob and unchanged
patch sources. wcc_lite may crash during shutdown after saving the blob; that
is recorded, as in the accepted 0.9.0 integrated run.
"""
from pathlib import Path
import os
import argparse, hashlib, json, subprocess, time

ROOT = Path(__file__).resolve().parents[2]
REDKIT = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit')
SUCCESS = 'Success! Patch scripts blob saved to'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sources(folder):
    return [dict(path=p.relative_to(folder).as_posix(), sha256=sha(p)) for p in sorted(folder.rglob('*.ws'))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=ROOT / 'BetaGwent/build' / os.environ.get('BG_FINAL', 'release090-final'))
    parser.add_argument('--redkit', type=Path, default=REDKIT)
    parser.add_argument('--timeout', type=int, default=600)
    # Healthy runs log continuously; the longest gap measured in accepted runs is 20 s.
    parser.add_argument('--stall', type=int, default=120)
    args = parser.parse_args()
    # The compiler runs from its own binary folder; CLI paths belong to the
    # caller's workspace and must be absolute before changing that directory.
    args.input = args.input.resolve()
    args.redkit = args.redkit.resolve()
    scripts = args.input / 'scripts'
    out = args.input / 'compile-nextgen-final'
    assert scripts.is_dir(), scripts
    if out.exists():
        # A failed attempt stays on disk as evidence but must not block --resume;
        # an attempt that reported compiler success is never silently replaced.
        record = out / 'result.json'
        assert record.is_file(), f'{out} exists without result.json; move it away manually'
        assert json.loads(record.read_text('utf8'))['exitCode'] != 0, f'{out} holds a verified compile; use a fresh --input'
        archived = out
        index = 1
        while archived.exists():
            archived = out.with_name(f'compile-nextgen-final.failed-{index}'); index += 1
        out.rename(archived)
    (out / 'compiled').mkdir(parents=True)
    exe = args.redkit / 'bin/x64_RedKit/wcc_lite.exe'
    assert exe.is_file(), exe
    command = [str(exe), 'compilescripts', str(args.redkit / 'r4data/scripts'), '-out=' + str(out / 'compiled'),
               '-wcclog=' + str(out / 'wcc.log'), '-patch=' + str(scripts), '-agreetoterms']
    before = sources(scripts)
    started = time.monotonic(); timed_out = False; stalled = False; stopped_after_success = False; success_at = None
    stdout_path = out / 'stdout.txt'; log_path = out / 'wcc.log'
    with stdout_path.open('wb') as stdout, (out / 'stderr.txt').open('wb') as stderr:
        process = subprocess.Popen(command, cwd=exe.parent, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)
        progress = (-1, -1); last_growth = started
        while process.poll() is None:
            # wcc_lite can remain in engine shutdown after explicitly reporting
            # that the script compiler saved its fresh blob. Bound that phase
            # separately; never mistake a pre-existing artifact for success.
            elapsed=time.monotonic()-started
            current=stdout_path.read_text('utf8',errors='replace')
            artifact=out/'compiled/blob.rsblob'
            if SUCCESS in current and artifact.is_file() and artifact.stat().st_size>0:
                if success_at is None:success_at=time.monotonic()
                if time.monotonic()-success_at>=15:
                    stopped_after_success=True;process.kill();process.wait(timeout=10);break
            else:
                # wcc_lite also blocks before saving anything - engine/store
                # init can hang with the process alive and the logs frozen.
                sizes=(stdout_path.stat().st_size, log_path.stat().st_size if log_path.is_file() else 0)
                if sizes!=progress:
                    progress=sizes; last_growth=time.monotonic()
                elif time.monotonic()-last_growth>=args.stall:
                    stalled=True;process.kill();process.wait(timeout=10);break
                elif elapsed>=args.timeout:
                    timed_out=True;process.kill();process.wait(timeout=10);break
            time.sleep(.5)
    text = (out / 'stdout.txt').read_text('utf8', errors='replace')
    blob = out / 'compiled/blob.rsblob'
    completed = SUCCESS in text and blob.is_file() and blob.stat().st_size > 0
    after = sources(scripts)
    result = dict(command=command, workingDirectory=str(exe.parent),
                  exitCode=0 if completed and not timed_out and not stalled else 1, processExitCode=process.returncode,
                  completedByOutput=completed, timedOut=timed_out, stalledWithoutOutput=stalled,
                  secondsWithoutOutput=round(time.monotonic()-last_growth, 2),
                  terminatedAfterCompilerSuccess=stopped_after_success,
                  shutdownFailureAfterSuccess=completed and process.returncode != 0,
                  elapsedSeconds=round(time.monotonic() - started, 2),
                  artifacts=[dict(path=str(blob), bytes=blob.stat().st_size, sha256=sha(blob))] if blob.is_file() else [],
                  patchSourcesBefore=before, patchSourcesAfter=after,
                  patchSourcesUnchangedDuringCompile=before == after,
                  note='An artifact/exit code alone is not confirmation of runtime or save round-trip.')
    if not completed:
        # Surfaces in the caller's log: the last compiler lines say which
        # subsystem the run stopped in, which inputs cannot explain that.
        result['lastStdoutLines'] = text.splitlines()[-6:]
        result['lastLogLines'] = log_path.read_text('utf8', errors='replace').splitlines()[-6:] if log_path.is_file() else []
    (out / 'result.json').write_text(json.dumps(result, indent=2), 'utf8')
    print(json.dumps({k: result[k] for k in ('exitCode', 'processExitCode', 'completedByOutput', 'timedOut', 'stalledWithoutOutput', 'elapsedSeconds')}))
    for line in result.get('lastStdoutLines', []) + result.get('lastLogLines', []):
        print('last compiler output:', line[:220])
    raise SystemExit(result['exitCode'])


if __name__ == '__main__':
    main()
