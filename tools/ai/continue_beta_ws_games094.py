"""Continue one explicitly selected unfinished frozen parity matrix, per match.

Original inputs/results are read-only. The derived validator changes only the
outer schedule loop; assertions, game seeds, clock, JS/WS and profiles stay intact.
Per-match processes bound memory lifetime and make future interruptions resumable.
"""
from pathlib import Path
import argparse, ctypes, datetime, hashlib, json, os, shutil, subprocess, time

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text('utf8'))

def save(path, data):
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data, indent=2)+'\n', 'utf8')
    temporary.replace(path)

def alive(pid):
    # os.kill(pid, 0) is unsafe on Windows: use a read-only process query.
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x1000, False, int(pid))
    if not handle:
        error = ctypes.get_last_error()
        if error in (87, 1168):
            return False
        raise OSError(error, 'Cannot establish process ownership; refusing duplicate')
    try:
        code = ctypes.c_ulong()
        if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
            raise ctypes.WinError(ctypes.get_last_error())
        return code.value == 259
    finally:
        kernel.CloseHandle(handle)

def derive(source):
    old = ' for(let i=0;i<schedules.length;i++){'
    assert source.count(old) == 1, 'Unknown frozen validator schedule'
    new = " const selectedIndex=Number(process.argv[process.argv.indexOf('--case-index')+1]);\n"
    new += " assert(process.argv.includes('--case-index')&&Number.isInteger(selectedIndex)&&selectedIndex>=0&&selectedIndex<schedules.length);\n"
    new += ' for(let i=selectedIndex;i<=selectedIndex;i++){'
    return source.replace(old, new), dict(before=old, after=new)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--resume', action='store_true')
    p.add_argument('--timeout', type=int, default=180)
    a = p.parse_args()
    run, out = a.run.resolve(), a.out.resolve()
    assert run.is_relative_to(ROOT/'BetaGwent/build') and out.is_relative_to(run) and out != run
    original = read(run/'whole-js-ws.json')
    assert not original['complete'], 'Do not restart a completed matrix'
    count = len(original['records'])
    assert [r['index'] for r in original['records']] == list(range(count))
    assert count < original['total'] == 92 and not original.get('error')
    status = read(run/'whole-parity-status.json')
    for pid in [status.get('pid'), status.get('childPid')]:
        assert not pid or not alive(pid), 'Original owner is active; do not duplicate'
    for name, digest in original['inputDigests'].items():
        assert sha(Path(name)) == digest, 'Frozen original input changed: '+name
    assert out.exists() == a.resume, 'Use fresh output or explicitly resume unfinished output'
    if not a.resume:
        out.mkdir()
        shutil.copytree(run/'research', out/'research')
        source_path = run/'research/tools/ai/check_beta_ws_games092.cjs'
        source = source_path.read_text('utf8')
        derived, change = derive(source)
        validator = out/'research/tools/ai/check_beta_ws_games094.cjs'
        validator.write_text(derived, 'utf8')
        save(out/'original-report.json', original)
        shutil.copy2(Path(__file__),out/'driver-source.py')
        frozen = {str(q.relative_to(out)):sha(q) for q in (out/'research').rglob('*') if q.is_file()}
        save(out/'plan.json', dict(originalRun=str(run), originalReportSha256=sha(run/'whole-js-ws.json'),
                                  originalCompletedGames=count, originalValidatorSha256=sha(source_path),
                                  derivedValidatorSha256=sha(validator), driverSha256=sha(Path(__file__)),
                                  scheduleOnlyChange=change, inputs=frozen, timeout=a.timeout,
                                  strengthComparison=False, originalResultsNeverOverwritten=True))
    plan = read(out/'plan.json')
    assert plan['originalRun'] == str(run) and plan['originalReportSha256'] == sha(run/'whole-js-ws.json')
    assert plan['timeout'] == a.timeout and plan['driverSha256'] == sha(Path(__file__))
    assert not (out/'report.json').exists() or not read(out/'report.json')['complete']
    for name,digest in plan['inputs'].items():
        assert sha(out/name) == digest, name
    lock = out/'owner.json'
    if (out/'status.json').exists():
        prior_status=read(out/'status.json')
        if prior_status.get('phase')=='running' and prior_status.get('childPid'):
            assert not alive(prior_status['childPid']), 'Orphaned case is still active; do not duplicate'
    if lock.exists():
        assert not alive(read(lock)['pid']), 'Continuation owner is active'
        lock.rename(out/('owner-stale-'+str(time.time_ns())+'.json'))
    with lock.open('x', encoding='utf8') as f:
        json.dump(dict(pid=os.getpid(), startedAt=datetime.datetime.now(datetime.timezone.utc).isoformat()), f)
    report = {k:v for k,v in original.items() if k not in ['current','lastChosen','lastActivity','records']}
    report.update(records=original['records'][:], complete=False,
                  continuationPlanSha256=sha(out/'plan.json'),
                  continuation='Same frozen seeds/profiles/assertions; fresh process per remaining match. Unfinished match restarts from its own initial seed.')
    report_path = out/'report.json'
    try:
        for index in range(count, original['total']):
            case = out/('case-%03d'%index)
            case.mkdir(exist_ok=True)
            successes = []
            for q in case.glob('attempt-*.json'):
                data = read(q)
                if data.get('complete') and len(data.get('records', [])) == 1:
                    successes.append((q,data))
            assert len(successes) <= 1, 'Duplicate completed case'
            if successes:
                file,data = successes[0]
            else:
                attempt = len(list(case.glob('attempt-*.log'))) + 1
                file = case/('attempt-%02d.json'%attempt)
                command = ['node', str(out/'research/tools/ai/check_beta_ws_games094.cjs'), str(run),
                           str(run/'rules'), str(file), '92', '--mapping',
                           str(out/'research/data/beta924/design/beta_ai_profiles093.json'),
                           '--case-index', str(index)]
                with (case/('attempt-%02d.log'%attempt)).open('w', encoding='utf8') as log:
                    child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                    start = time.monotonic()
                    while child.poll() is None:
                        save(out/'status.json', dict(phase='running',pid=os.getpid(),childPid=child.pid,
                             currentIndex=index,completedGames=len(report['records']),total=92,
                             elapsedSeconds=round(time.monotonic()-start,2),command=command,
                             updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat()))
                        if time.monotonic()-start > a.timeout:
                            child.kill();child.wait()
                            raise TimeoutError('Unfinished case %d timed out; inspect preserved attempt, do not count as loss'%index)
                        time.sleep(2)
                    assert child.returncode == 0, 'Inspect case log: '+str(case)
                data = read(file)
            assert data['complete'] and not data.get('error') and len(data['records']) == 1
            record = data['records'][0]
            assert record['index'] == index and record['status'] == 'complete'
            assert data['fingerprint'] == original['fingerprint'] and data['sourceSha256'] == original['sourceSha256']
            assert data['bindingChecks'] == 109 and data['peakActionsPerCallback'] <= 1
            for name,digest in data['inputDigests'].items():
                assert sha(Path(name)) == digest, name
            report['records'].append(record)
            report['checks'] += data['checks']
            report['peakCallbackMs'] = max(report['peakCallbackMs'],data['peakCallbackMs'])
            report['lastActivity'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            save(report_path, report)
            print(json.dumps(dict(index=index,completedGames=len(report['records']),total=92)),flush=True)
        assert [r['index'] for r in report['records']] == list(range(92))
        for name,digest in original['inputDigests'].items():
            assert sha(Path(name)) == digest, name
        report['complete'] = True
        save(report_path, report)
        save(out/'status.json', dict(phase='complete',completedGames=92,pid=os.getpid()))
    except BaseException as error:
        if 'child' in locals() and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=5)
            except subprocess.TimeoutExpired:child.kill();child.wait()
        save(out/'status.json', dict(phase='failed',pid=os.getpid(),error=repr(error),
                                   completedGames=len(report['records']),testLossesAssigned=0))
        raise
    finally:
        lock.rename(out/('owner-ended-'+str(time.time_ns())+'.json'))

if __name__ == '__main__':
    main()
