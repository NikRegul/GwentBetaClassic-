"""Compile isolated vanilla/merged Classic sources with the available REDkit Wcc.

This is a diagnostic with the recorded compiler, not Classic runtime acceptance.
The installed game is only read; compiler input and output stay in the workspace.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
TOOL = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\x64_RedKit\wcc_lite.exe')


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def manifest(directory):
    return {p.relative_to(directory).as_posix(): sha(p) for p in sorted(directory.rglob('*.ws'))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--baseline-only', action='store_true')
    parser.add_argument('--timeout', type=int, default=180)
    args = parser.parse_args()
    out = args.out.resolve()
    build = (ROOT / 'BetaGwent/build').resolve()
    if not out.is_relative_to(build) or out == build or out.exists():
        parser.error('Use a fresh subdirectory of BetaGwent/build')
    if not 1 <= args.timeout <= 300:
        parser.error('Timeout must be 1..300')
    prepared = args.prepared.resolve()
    preparation = json.loads((prepared / 'preparation.json').read_text('utf8'))
    audit_path = Path(preparation['audit'])
    if sha(audit_path) != preparation['auditSha256']:
        parser.error('Audit changed')
    audit = json.loads(audit_path.read_text('utf8'))
    game = Path(audit['game'])
    base = game / 'content/content0/scripts'
    if manifest(base) != audit['vanillaScripts']:
        parser.error('Classic base scripts changed since audit')
    patch = prepared / 'Mods/modBetaGwentClassic132/content/scripts'
    if manifest(patch) != preparation['outputScripts']:
        parser.error('Prepared scripts changed')
    acceptance = json.loads((ROOT / f"BetaGwent/build/stage{preparation['sourceStage']}/compile/result.json").read_text('utf8'))
    if not acceptance.get('humanReportedPriorLicenseAcceptance') or acceptance['command'][0] != str(TOOL):
        parser.error('Prior human acceptance for this Wcc tool is required')
    source = out / 'sources'
    shutil.copytree(base, source)
    if not args.baseline_only:
        shutil.copytree(patch, source, dirs_exist_ok=True)
    before = manifest(source)
    compiled = out / 'compiled'
    compiled.mkdir()
    command = [str(TOOL), 'compilescripts', str(source), '-out=' + str(compiled),
               '-wcclog=' + str(out / 'wcc.log'), '-agreetoterms']
    started = time.monotonic()
    timed_out = False
    with (out / 'stdout.txt').open('wb') as stdout, (out / 'stderr.txt').open('wb') as stderr:
        process = subprocess.Popen(command, cwd=TOOL.parent, stdin=subprocess.DEVNULL,
                                   stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        print(json.dumps(dict(pid=process.pid, command=command, baselineOnly=args.baseline_only)), flush=True)
        try:
            process.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            process.wait(timeout=10)
    transcript = '\n'.join(p.read_text('utf8', errors='replace') for p in
                           [out / 'stdout.txt', out / 'stderr.txt', out / 'wcc.log'] if p.exists())
    errors = sorted(set(line.strip() for line in transcript.splitlines() if '[Script]: Error [' in line or '[Script]: Fatal' in line))
    artifacts = [dict(path=p.relative_to(out).as_posix(), bytes=p.stat().st_size, sha256=sha(p))
                 for p in sorted(compiled.rglob('*')) if p.is_file()]
    unchanged = before == manifest(source)
    passed = (process.returncode == 0 and not timed_out and not errors and unchanged
              and bool(artifacts) and 'Success!' in transcript)
    report = dict(command=command, compiler=str(TOOL), compilerSha256=sha(TOOL),
                  compilerFamily='REDkit (Next-Gen); diagnostic against Classic source inputs',
                  baselineOnly=args.baseline_only, gameVersion='1.32', sourceStage=preparation['sourceStage'],
                  exitCode=process.returncode, timedOut=timed_out, elapsedSeconds=round(time.monotonic()-started, 2),
                  errors=errors, artifacts=artifacts, sourceCount=len(before), sources=before,
                  sourcesUnchanged=unchanged, diagnosticPassed=passed,
                  classicRuntimeVerified=False, installedGameModified=False)
    (out / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(transcript[-12000:], flush=True)
    print(json.dumps({k: report[k] for k in ('exitCode','timedOut','elapsedSeconds','sourceCount','diagnosticPassed','errors','artifacts')}, ensure_ascii=False, indent=2), flush=True)
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
