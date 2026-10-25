"""Run a frozen targeted experiment under an exclusive controller lock."""
from pathlib import Path
import argparse,json,subprocess,sys
from bracket_tournament092 import lock
from comparison_inputs import validate_snapshot

ROOT=Path(__file__).resolve().parents[2]

def main():
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args()
    config=a.config.resolve();c=json.loads(config.read_text('utf8'));out=Path(c['out']).resolve()
    assert out.is_relative_to(ROOT/'BetaGwent/build') and not (out/'STOP').exists() and not (out/'cancelled.json').exists()
    for directory in set(c['versions'].values())|{c['baseline']}:validate_snapshot(directory)
    out.mkdir(parents=True,exist_ok=True)
    with lock(out):
        subprocess.run(['node',str(config.parent/'weak_variants092.js'),str(config)],cwd=ROOT,check=True)
        r=json.loads((out/'report.json').read_text('utf8'));assert r['complete'] and r['errors']==0
    print('COMPLETE',out,flush=True)

if __name__=='__main__':main()
