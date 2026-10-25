"""Quick source/data layout check; --hash-inputs verifies the licensed input store."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hash-inputs', action='store_true')
    parser.add_argument('--sources-only', action='store_true', help='Check public source checkout without licensed local dependencies')
    args = parser.parse_args()
    data = ROOT/'data/beta924'
    assert (data/'normalized/catalog.json').is_file(), 'Required card/localization metadata missing'
    mapping = json.loads((data/'design/beta_ai_profiles093.json').read_text('utf8'))
    plan = data/'ai/validation093/profile-confirmation-plan.json'
    assert hashlib.sha256(plan.read_bytes()).hexdigest() == mapping['confirmation']['planSha256']
    assert len(mapping['assignments']) == 109 and len({x['composition'] for x in mapping['assignments']}) == 92
    for name, key, count in [('final092-rosters.json', 'decks', 46), ('beta-rosters-audit.json', 'eligible', 45)]:
        assert len(json.loads((data/'ai/validation093'/name).read_text('utf8'))[key]) == count
    boards = [(ROOT/'BetaGwent/ui'/p/'BetaGwentBoard.as').read_bytes() for p in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']]
    assert all(b == boards[0] and b.startswith(b'\xef\xbb\xbf') and b'\n' not in b.replace(b'\r\n', b'') for b in boards)
    ui_preparer = (ROOT/'tools/features091/prepare_ui091.py').read_text('utf8')
    for board in [ROOT/'BetaGwent/ui/src/BetaGwentBoard.as', ROOT/'tools/features091/BetaGwentBoard_classic093.as']:
        assert hashlib.sha256(board.read_bytes()).hexdigest() in ui_preparer, 'Review and update UI source SHA gate: '+str(board)
    if not args.sources_only:
        assert (ROOT/'BetaGwent/build-inputs/manifest.json').is_file(), 'Prepare documented local build inputs first'
    assert not (args.sources_only and args.hash_inputs), 'Choose sources-only or licensed input verification'
    if args.hash_inputs:
        subprocess.run([sys.executable, '-X', 'utf8', 'tools/recon/migrate_build_inputs.py', '--verify'], cwd=ROOT, check=True)
    print('PASS: permanent parity data, 109 preset bindings / 92 compositions, five BOM/CRLF boards' + ('' if args.sources_only else ', input manifest'))

if __name__ == '__main__':
    main()
