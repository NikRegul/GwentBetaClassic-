"""Run isolated regressions against the frozen 0.8.2 release sources."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import argparse

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'BetaGwent/build/release082-final'
OUT = ROOT / 'BetaGwent/build/audit082-20261018'


def main():
    global SOURCE, OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,default=SOURCE)
    parser.add_argument('--output',type=Path,default=OUT)
    parser.add_argument('--prepare-only',action='store_true')
    args=parser.parse_args();SOURCE=args.source.resolve();OUT=args.output.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    snapshot = OUT / 'rules'
    snapshot.mkdir(exist_ok=True)
    scripts = SOURCE / 'scripts/game/betagwent'
    import build_js
    core = OUT / 'core-inputs'
    core.mkdir(exist_ok=True)
    for original in (ROOT / 'BetaGwent/scripts/game/betagwent').glob('*.ws'):
        shutil.copy2(scripts / original.name, core / original.name)
    build_js.CORE = core
    build_js.DEV = scripts
    build_js.main(snapshot / 'rules.js')
    for name in ['runtime.js', 'harness.js']:
        shutil.copy2(ROOT / 'tools/ai/jshost' / name, snapshot / name)
    tuning = (scripts / 'duelAIPass.ws').read_text('utf-8-sig')
    tuning = tuning.split('function BetaGwentAITune(', 1)[1].split('// Average public value', 1)[0]
    defaults = {k: int(v) for k, v in re.findall(r'case (\d+): return (-?\d+);', tuning)}
    runtime = snapshot / 'runtime.js'
    text, count = re.subn(r'const __tuneDefaults = \{[^}]*\};', 'const __tuneDefaults = ' + json.dumps(defaults) + ';', runtime.read_text('utf8'))
    assert count == 1
    runtime.write_text(text, 'utf8')
    catalogue = (scripts / 'duelAICatalog.ws').read_text('utf-8-sig')
    mapping = catalogue.split('function BetaGwentAIPresetProfile(', 1)[1].split('\n}', 1)[0]
    pool = sorted(int(x) for x in re.findall(r'case (\d+): return \d+;', mapping))
    assert len(set(pool)) == 46
    inputs = {p.relative_to(SOURCE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (SOURCE / 'scripts').rglob('*.ws')}
    fingerprint = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    (snapshot / 'manifest.json').write_text(json.dumps(dict(presets=pool, fingerprint=fingerprint, source=str(SOURCE), files=inputs), indent=2), 'utf8')
    if args.prepare_only:
        print('Prepared',snapshot,flush=True)
        return
    for platform in ['nextgen', 'classic']:
        for directory in ['src', 'src-BetaGwentBoard', 'src-GwintGame', 'src-DeckBuilder', 'src-BetaGwentKeg']:
            target = OUT / platform / 'ui' / directory
            target.mkdir(parents=True, exist_ok=True)
            for p in (SOURCE / platform / 'ui' / directory).glob('*.as'):
                shutil.copy2(p, target / p.name)
    logs = OUT / 'logs'
    logs.mkdir(exist_ok=True)
    names = ['check_consume_self', 'check_no_targets127', 'check_deck_combos128',
             'check_policy133', 'check_hidden_information133', 'check_armor_restore165',
             'check_miruna_aglais_scorch180', 'check_emissary_mulligan181', 'check_playtest188',
             'check_playtest_rules150', 'check_lock_choice144', 'check_chase139',
             'check_spy138', 'check_cooperative156', 'check_ciri_return062',
             'check_decisive127', 'check_concede127', 'check_tutor127', 'check_preventive127',
             'check_ships127', 'check_draug127', 'check_losing131', 'check_cavalry131',
             'check_ciri131', 'check_combo127']
    jobs = [(name, ['node', str(ROOT / 'tools/ai' / (name + '.js')), str(snapshot), str(OUT / (name + '.json'))]) for name in names]
    for name in ['check_ui_layout', 'check_editor_navigation', 'check_intro_portraits', 'check_exchange_open']:
        jobs.append((name, ['node', str(ROOT / 'tools/features082' / (name + '.js')), str(OUT)]))
    def run(job):
        name, cmd = job
        start = time.monotonic()
        try:
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf8', errors='replace', timeout=180)
            code, output = proc.returncode, proc.stdout + proc.stderr
        except subprocess.TimeoutExpired as exc:
            code, output = -1, str(exc)
        (logs / (name + '.log')).write_text(output, 'utf8')
        result = dict(name=name, exitCode=code, seconds=round(time.monotonic()-start, 2), passLines=sum(line.startswith('PASS') for line in output.splitlines()))
        if code:
            result['failureTail'] = output[-2500:]
        print(json.dumps(result, ensure_ascii=False), flush=True)
        return result
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for result in executor.map(run, jobs):
            results.append(result)
            (OUT / 'checks-summary.json').write_text(json.dumps(results, indent=2), 'utf8')
    drift = [p for p, digest in inputs.items() if hashlib.sha256((SOURCE / p).read_bytes()).hexdigest() != digest]
    assert not drift, drift
    print('TOTAL', len(results), 'FAILED', sum(r['exitCode'] != 0 for r in results), 'sourceDrift', len(drift), flush=True)


if __name__ == '__main__':
    main()
