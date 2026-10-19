"""Check the two final 0.9.0 archives before manual in-game testing."""
from pathlib import Path
import os
import hashlib, json, sys, zipfile

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'BetaGwent/build' / os.environ.get('BG_FINAL', 'release090-final') / 'package-candidate'
LATEST = max(BASE.glob('archives-optional*'), key=lambda p: p.stat().st_mtime, default=BASE / 'archives')
ARCHIVES = BASE / sys.argv[1] if len(sys.argv) > 1 else LATEST
OPT = '' if ARCHIVES.name == 'archives' else 'Optional-CopyButton/'
EXPECT = {
    '1.32': ('modBetaGwentClassic132', ['bin/x64']),
    '5.0+': ('modBetaGwent0924', ['bin/x64', 'bin/x64_dx12']),
}
MARK = 'cleanup is INCOMPLETE'
checks = 0


def check(ok, message):
    global checks
    if not ok:
        raise SystemExit('FAIL: ' + message)
    checks += 1


report = {}
for platform, (mod, bins) in EXPECT.items():
    path = ARCHIVES / f'GwentBetaClassic-0.9.0-{platform}-AllLanguages.zip'
    check(path.is_file(), f'archive missing: {path}')
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        check(z.testzip() is None, platform + ' zip integrity')
        for folder in bins:
            check(f'{OPT}{folder}/dinput8.dll' in names, f'{platform} {OPT}{folder}/dinput8.dll')
            check(f'{OPT}{folder}/plugins/GwentBetaClipboard.asi' in names, f'{platform} {OPT}{folder} ASI plugin')
        if OPT:
            check(not any(n.startswith('bin/') for n in names), platform + ' no bin in archive root')
            check(OPT + 'README_RU.txt' in names and OPT + 'README_EN.txt' in names, platform + ' optional README')
        info = json.loads(z.read(f'Mods/{mod}/info.json'))
        check(info['version'] == '0.9.0', platform + ' info version')
        check(not any('Copy-Deck-Code' in n for n in names), platform + ' no Copy-Deck-Code helper')
        check(not any('Copy-Deck-Code' in z.read(n).decode('utf-8', 'ignore') for n in names if n.startswith('BetaGwentDocs/') and n.endswith('.md') and not n.startswith('BetaGwentDocs/CLEANUP')), platform + ' docs without Copy-Deck-Code fallback')
        build = json.loads(z.read('BetaGwentDocs/BuildInfo.json'))
        check(build.get('nativeClipboard') and build.get('cleanerSingleResultMessage'), platform + ' build info')
        if platform == '1.32':
            # Classic lowers the @addMethod cleaner body into game/player/playerWitcher.ws.
            hits = [n for n in names if n.endswith('.ws') and MARK in z.read(n).decode('utf-16')]
            check(len(hits) == 1, 'classic cleaner fix present once: ' + ', '.join(hits))
            text = z.read(hits[0]).decode('utf-16')
            check(text.index(MARK) < text.index('profile and known mirrors cleared'), 'classic cleaner failure branch precedes success')
            check('DLC/dlcBetaGwentClassic132Assets' in ''.join(sorted(names)), 'classic DLC folder')
        else:
            blob = z.read(f'Mods/{mod}/content/precompiled.rsblob')
            compiled = json.loads((ROOT / 'BetaGwent/build' / os.environ.get('BG_FINAL', 'release090-final') / 'compile-nextgen-final/result.json').read_text('utf8'))
            check(hashlib.sha256(blob).hexdigest() == compiled['artifacts'][0]['sha256'], 'next-gen blob is the final compile')
            fixed = (ROOT / 'BetaGwent/build' / os.environ.get('BG_FINAL', 'release090-final') / 'scripts/game/betagwent/profileCleanup090.ws').read_text('utf-8-sig')
            check(MARK in fixed, 'next-gen compiled from fixed cleaner source')
        report[platform] = dict(archive=str(path), bytes=path.stat().st_size, files=len(names))
print(json.dumps(dict(checks=checks, archives=report, inGameVerified=False), indent=2))
