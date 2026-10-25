"""Read-only replay of a development block with diagnostic decision states."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('old', type=Path); p.add_argument('new', type=Path)
    p.add_argument('out', type=Path); p.add_argument('--block', type=int, required=True)
    a = p.parse_args(); out = a.out.resolve()
    assert not out.exists() and out.is_relative_to(ROOT / 'BetaGwent/build')
    originals = [a.old.resolve(), a.new.resolve()]
    reports = [json.loads((d / 'report.json').read_text('utf8')) for d in originals]
    configs = [json.loads((d / 'run.json').read_text('utf8')) for d in originals]
    assert all(c['cycles'] == 1 for c in configs)
    assert all(c['blockStart'] <= a.block < c['blockStart'] + c['blockCount'] for c in configs)
    assert configs[0]['seed'] == configs[1]['seed']
    out.mkdir()
    evidence = []
    for label, source, config, original in zip(('prior', 'expanded'), originals, configs, reports):
        dest = out / label; dest.mkdir()
        for name in ('candidate', 'baseline'):
            shutil.copytree(source / name, dest / name)
        for name in ('comparison_bridge119.js', 'replay119.js', 'profiles.json'):
            shutil.copy2(source / name, dest / name)
        runner = (source / 'compare_ai.js').read_text('utf8')
        needle = 'decisions.push({step:steps,version:'
        assert runner.count(needle) == 1
        runner = runner.replace(needle, 'decisions.push({beforeState:lastState,step:steps,version:')
        (dest / 'compare_ai.js').write_text(runner, encoding='utf8')
        config.update(blockStart=a.block, blockCount=1, traceEvery=1)
        (dest / 'run.json').write_text(json.dumps(config), encoding='utf8')
        with (dest / 'worker.log').open('w', encoding='utf8') as log:
            subprocess.run(['node', str(dest / 'compare_ai.js'), str(dest)], cwd=ROOT,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        fresh = json.loads((dest / 'report.json').read_text('utf8'))
        expected = [g for g in original['games'] if g['block'] == a.block-original['blockStart']]
        assert len(expected) == len(fresh['games']) == 4
        for x, y in zip(expected, fresh['games']):
            assert all(x[k] == y[k] for k in ('left', 'right', 'newSeat', 'mirror', 'seed', 'winner', 'steps'))
        evidence.append(dict(label=label, original=str(source), originalReportSha256=hashlib.sha256((source/'report.json').read_bytes()).hexdigest(),
                             exactOutcomeReplay=True, games=4, errors=fresh['errors']))
        print(label, 'exact replay', flush=True)
    (out / 'proof.json').write_text(json.dumps(dict(kind='development-diagnostic-not-holdout', records=evidence), indent=2)+'\n', encoding='utf8')


if __name__ == '__main__':
    main()
