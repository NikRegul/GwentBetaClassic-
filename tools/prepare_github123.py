"""Update the existing public Git checkout with audited source-only 0.4.3 files."""
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'BetaGwent/build/github-0.3.0'
SUFFIXES = {'.py', '.ws', '.as', '.js', '.json', '.xml', '.md', '.cs', '.csproj', '.ps1', '.txt', '.csv'}
EXCLUDE = {'vendor', '__pycache__', 'bin', 'obj', 'node_modules', '.git', 'assets', 'audio', 'build'}
PRIVATE_HELPERS = {'github_auth_probe89.py', 'download_github_cli93.py', 'github_upload_batches89.py'}


def main():
    assert (OUT / '.git').is_dir(), 'Existing public checkout required'
    copied = []

    def copy(source):
        relative = source.relative_to(ROOT)
        if any(part in EXCLUDE for part in relative.parts) or source.name in PRIVATE_HELPERS:
            return
        if source.suffix not in SUFFIXES:
            return
        raw = source.read_bytes()
        content = raw.decode('utf-8-sig')
        assert not re.search(r'<Property[^>]+Name="LicenseKey"[^>]+Value="[^"\s]+"', content), relative
        assert not re.search(r'(?m)^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', content), relative
        assert not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})', content), relative
        target = OUT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied.append({'path': relative.as_posix(), 'sha256': hashlib.sha256(raw).hexdigest()})

    for folder in ('BetaGwent/scripts', 'BetaGwent/development/scripts', 'BetaGwent/ui/src',
                   'tools', 'data/beta924/duel', 'data/beta924/design', 'data/beta924/ai'):
        for source in sorted((ROOT / folder).rglob('*')):
            if source.is_file():
                copy(source)
    for source in (ROOT / 'docs').glob('*.md'):
        copy(source)
    for source in (ROOT / 'BetaGwent/release').glob('*.md'):
        copy(source)
    for source in (ROOT / 'BetaGwent/release/publish-0.4.3').glob('*.md'):
        copy(source)
    for source in (ROOT / 'BetaGwent/release/publish-0.4.2').glob('*.md'):
        copy(source)
    for source in (ROOT / 'BetaGwent/release/publish-0.4.3').glob('*.txt'):
        copy(source)
    for source in (ROOT / 'docs/evidence').glob('*123*.json'):
        if source.name != 'github123-preparation.json':
            copy(source)
    for name in ('stage119-final-archetypes.json', 'stage119-final-release.json'):
        copy(ROOT / 'docs/evidence' / name)
    for name in ('BetaGwent/README.md', 'BetaGwent/ui/README.md'):
        copy(ROOT / name)
    for name in ('deck_rules.txt', 'deck_rules_researched_114.md'):
        copy(ROOT / name)
    for name in ('REPORT_RU.md', 'report.json', 'archetypes.csv'):
        copy(ROOT / 'BetaGwent/training/compare-041-042' / name)
    previous = (OUT / 'README.md').read_text('utf8')
    tail = previous[previous.index('## Contributing'):] if '## Contributing' in previous else ''
    (OUT / 'README.md').write_text('''# Gwent Beta Classic 0.4.3

Gwent Beta 0.9.24 inside The Witcher 3: 479 collectible cards, 21 leaders,
five factions, editable saved decks, NPC matches, card collecting and controller support.
Targets PC game version 5.01. Install one language package at a time.

0.4.3 prevents self-consumption and fixes Morkvarg returning with zero strength.
Shuffling a weakened card preserves its strength. AI target selection, Vran food
chains, spy placement, empty Ointment choices and weather replacement are corrected.
The 46-deck opponent rotation persists with saves, and Cursed Adda has two tactics.

Ability choices use the mulligan-style grid with board inspection during a pending
choice. Craft buttons appear directly on cards and work before NPC matches;
controller focus and row
navigation are corrected, and frost/rain presentation and timer alignment improved.
The local changelog also records the preceding 0.4.2 fixes.

- [0.4.3 changelog / English](BetaGwent/release/publish-0.4.3/CHANGELOG_EN.md)
- [0.4.3 changelog / Russian](BetaGwent/release/publish-0.4.3/CHANGELOG_RU.md)
- [0.4.3 validation / English](docs/PRESENTATION123_EN.md)
- [0.4.3 validation / Russian](docs/PRESENTATION123_RU.md)
- [PowerShell build script](tools/Build-0.4.3.ps1)
- [AI comparison script](tools/Compare-AI.ps1)
- [Completed 0.4.1 vs 0.4.2 comparison](docs/AI_COMPARISON_041_042_REVIEW_RU.md)
- [Build guide / Russian](docs/BUILD_RU.md) / [English](docs/BUILD_EN.md)

The completed 0.4.2 versus 0.4.1 comparison scored 50.35% over 1,840 games;
this does not establish overall superiority. 0.4.3 regression checks validate
corrected situations, not an overall playing-strength improvement.

Native script/menu compilation and archive checks are verified during the build.
Installed-game visuals, controller operation and native save round trips still
require acceptance testing. Back up saves before installation and updates.

This repository contains source code and documentation. Original clients,
textures, fonts, audio, native templates, tool SDKs and Wwise license keys are
excluded. A fresh clone needs those local build inputs. Original code is GPL-3.0-only.

''' + tail, 'utf8')
    report = {'version': '0.4.3', 'checkout': str(OUT), 'sourceOnly': True,
              'filesCopied': len(copied), 'files': copied, 'assetsExcluded': True,
              'licenseKeysExcluded': True, 'pushed': False}
    (ROOT / 'docs/evidence/github123-preparation.json').write_text(json.dumps(report, indent=2) + '\n', 'utf8')
    print(json.dumps({key: value for key, value in report.items() if key != 'files'}, indent=2))


if __name__ == '__main__':
    main()
