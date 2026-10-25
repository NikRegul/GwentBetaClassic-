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
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args()
    # The compiler runs from its own binary folder; CLI paths belong to the
    # caller's workspace and must be absolute before changing that directory.
    args.input = args.input.resolve()
    args.redkit = args.redkit.resolve()
    scripts = args.input / 'scripts'
    out = args.input / 'compile-nextgen-final'
    assert scripts.is_dir() and not out.exists(), 'Fresh output folder required'
    (out / 'compiled').mkdir(parents=True)
    exe = args.redkit / 'bin/x64_RedKit/wcc_lite.exe'
    assert exe.is_file(), exe
    command = [str(exe), 'compilescripts', str(args.redkit / 'r4data/scripts'), '-out=' + str(out / 'compiled'),
               '-wcclog=' + str(out / 'wcc.log'), '-patch=' + str(scripts), '-agreetoterms']
    before = sources(scripts)
    started = time.monotonic(); timed_out = False; stopped_after_success = False; success_at = None
    with (out / 'stdout.txt').open('wb') as stdout, (out / 'stderr.txt').open('wb') as stderr:
        process = subprocess.Popen(command, cwd=exe.parent, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)
        while process.poll() is None:
            # wcc_lite can remain in engine shutdown after explicitly reporting
            # that the script compiler saved its fresh blob. Bound that phase
            # separately; never mistake a pre-existing artifact for success.
            elapsed=time.monotonic()-started
            current=(out/'stdout.txt').read_text('utf8',errors='replace')
            artifact=out/'compiled/blob.rsblob'
            if SUCCESS in current and artifact.is_file() and artifact.stat().st_size>0:
                if success_at is None:success_at=time.monotonic()
                if time.monotonic()-success_at>=15:
                    stopped_after_success=True;process.kill();process.wait(timeout=10);break
            elif elapsed>=args.timeout:
                timed_out=True;process.kill();process.wait(timeout=10);break
            time.sleep(.5)
    text = (out / 'stdout.txt').read_text('utf8', errors='replace')
    blob = out / 'compiled/blob.rsblob'
    completed = SUCCESS in text and blob.is_file() and blob.stat().st_size > 0
    after = sources(scripts)
    result = dict(command=command, workingDirectory=str(exe.parent),
                  exitCode=0 if completed and not timed_out else 1, processExitCode=process.returncode,
                  completedByOutput=completed, timedOut=timed_out,
                  terminatedAfterCompilerSuccess=stopped_after_success,
                  shutdownFailureAfterSuccess=completed and process.returncode != 0,
                  elapsedSeconds=round(time.monotonic() - started, 2),
                  artifacts=[dict(path=str(blob), bytes=blob.stat().st_size, sha256=sha(blob))] if blob.is_file() else [],
                  patchSourcesBefore=before, patchSourcesAfter=after,
                  patchSourcesUnchangedDuringCompile=before == after,
                  note='An artifact/exit code alone is not confirmation of runtime or save round-trip.')
    (out / 'result.json').write_text(json.dumps(result, indent=2), 'utf8')
    print(json.dumps({k: result[k] for k in ('exitCode', 'processExitCode', 'completedByOutput', 'timedOut', 'elapsedSeconds')}))
    raise SystemExit(result['exitCode'])


if __name__ == '__main__':
    main()
