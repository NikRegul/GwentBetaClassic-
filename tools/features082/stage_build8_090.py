"""Stage build 8: build 7 scripts and both compiles reused (SHA-checked), ui8 menus."""
from pathlib import Path
import hashlib, json, os, shutil, sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
import prepare_final090 as final
B = ROOT / 'BetaGwent/build'
SOURCE = B / os.environ.get('BG_SOURCE', 'release090-final7')
OUT = B / os.environ.get('BG_FINAL', 'release090-final8')
UI = B / os.environ.get('BG_UI', 'release090-ui8')
# Bridge r7 (Import without ~1300 original setData calls) when built, else r6b.
NATIVE = B / ('clipboard090-r7' if (B / 'clipboard090-r7/GwentBetaClipboard.asi').is_file() else 'clipboard090-r6b')
BANNERS = B / os.environ.get('BG_BANNERS', 'banners090-sdk-fix5')
CLASSIC = B / 'universal081/classic-runtime/runs' / os.environ.get('BG_CLASSIC_LABEL', 'release090-final7') / 'result.json'


def hashes(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*.ws')}


def main():
    expected = hashes(SOURCE / 'scripts')
    compiled = json.loads((SOURCE / 'compile-nextgen-final/result.json').read_text('utf8'))
    assert compiled['exitCode'] == 0 and compiled['patchSourcesUnchangedDuringCompile']
    assert {r['path']: r['sha256'] for r in compiled['patchSourcesBefore']} == expected
    result = json.loads(CLASSIC.read_text('utf8'))
    assert result['compilePassed'] and not result['errors']
    assert result['preparationManifestSha256'] == final.sha(SOURCE / 'classic-prepared-final/preparation.json')
    assert not OUT.exists(), 'Fresh candidate required'
    OUT.mkdir()
    for name in ['scripts', 'classic-prepared-final', 'compile-nextgen-final']:
        shutil.copytree(SOURCE / name, OUT / name)
    for name in ['scripts-changed.json', 'classic-prepared-diff.json']:
        shutil.copy2(SOURCE / name, OUT / name)
    final.stage_phase(OUT, UI, NATIVE, json.loads((OUT / 'scripts-changed.json').read_text()), BANNERS)
    (OUT / 'compile-reuse.json').write_text(json.dumps(dict(source=str(SOURCE), classicResult=str(CLASSIC),
        gameplaySourcesIdentical=True, preparedManifestIdentical=True, inGameVerified=False), indent=2), 'utf8')


if __name__ == '__main__':
    main()
