"""Current public release entry point; every ordinary run uses a fresh folder."""
from pathlib import Path
import argparse, datetime, json, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if args.resume and args.out is None:
        parser.error('--resume requires the explicit unfinished --out folder')
    out = (args.out or ROOT/'BetaGwent/build'/datetime.datetime.now().strftime('release093-%Y%m%d-%H%M%S')).resolve()
    if not out.is_relative_to(ROOT/'BetaGwent/build') or out == ROOT/'BetaGwent/build':
        parser.error('--out must be a child of BetaGwent/build')
    subprocess.run([sys.executable, '-X', 'utf8', 'tools/recon/check_project_layout.py'], cwd=ROOT, check=True)
    command = [sys.executable, '-X', 'utf8', 'tools/features093/build093_public.py', '--out', str(out)]
    if args.resume:
        command.append('--resume')
    subprocess.run(command, cwd=ROOT, check=True)
    sys.path.insert(0, str(ROOT/'tools/features093'))
    from collect_release093 import main as collect
    dest = collect([str(out)])
    manifest = json.loads((out/'rules/manifest.json').read_text('utf8'))
    (ROOT/'BetaGwent/build/release093-public-latest.json').write_text(json.dumps(dict(path=str(out), version='0.9.3', status='ready', fingerprint=manifest['fingerprint'], releaseFolder=str(dest)), indent=2)+'\n', 'utf8')
    print('READY:', out, flush=True)

if __name__ == '__main__':
    main()
