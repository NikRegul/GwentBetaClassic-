"""Update the existing public Git checkout with audited source-only 0.4.1 files."""
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'BetaGwent/build/github-0.3.0'
SUFFIXES = {'.py', '.ws', '.as', '.js', '.json', '.xml', '.md', '.cs', '.csproj', '.ps1', '.txt'}
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
    for source in (ROOT / 'BetaGwent/release/publish-0.4.1').glob('*.md'):
        copy(source)
    for source in (ROOT / 'docs/evidence').glob('*120*.json'):
        if source.name != 'github120-preparation.json':
            copy(source)
    for name in ('stage119-final-archetypes.json', 'stage119-final-release.json'):
        copy(ROOT / 'docs/evidence' / name)
    for name in ('BetaGwent/README.md', 'BetaGwent/ui/README.md'):
        copy(ROOT / name)
    for name in ('deck_rules.txt', 'deck_rules_researched_114.md'):
        copy(ROOT / name)
    previous = (OUT / 'README.md').read_text('utf8')
    tail = previous[previous.index('## Contributing'):] if '## Contributing' in previous else ''
    (OUT / 'README.md').write_text('''# Gwent Beta Classic 0.4.1

Gwent Beta 0.9.24 inside The Witcher 3: 479 collectible cards, 21 leaders,
five factions, editable saved decks, NPC matches, card collecting and controller support.

**Back up saves before installation and every update. Bugs can still occur.**

0.4.1 restores gold ornaments and fittings by baking the camera-facing surfaces
of all ten original faction board halves. It retains the single horizontal
reflection, adds original hand/leader separators, improves score typography,
animates the original hit sheet and routes weather impacts to dedicated sounds.
Locked cards retain and display their lock in the graveyard. Atlas dimensions
and card resolution are unchanged. Packages target PC game version 5.01.

Changes since 0.3.4 also include researched deck rosters and AI strategies,
46-archetype checks, decision logging, reproducible AI comparison, action previews,
animation settings and unified card/deck/graveyard selection screens.

- [Cumulative changelog / English](BetaGwent/release/publish-0.4.1/CHANGELOG_0.3.4_to_0.4.1_EN.md)
- [Cumulative changelog / Russian](BetaGwent/release/publish-0.4.1/CHANGELOG_0.3.4_to_0.4.1_RU.md)
- [0.4.1 build and acceptance notes / English](docs/PRESENTATION120_EN.md)
- [0.4.1 build and acceptance notes / Russian](docs/PRESENTATION120_RU.md)
- [0.4.0 AI tools and configuration](docs/PRESENTATION119_EN.md)
- [PowerShell build script](tools/Build-0.4.1.ps1)
- [Build guide / Russian](docs/BUILD_RU.md) / [English](docs/BUILD_EN.md)
- [AI architecture / Russian](docs/ARCHITECTURE_AI_RU.md) / [English](docs/ARCHITECTURE_AI_EN.md)

Native menus, script compilation and archive checks are verified during the
build. Visual, audio and controller acceptance still require installed-game
testing. A literal recreation of Unity shaders/particles is not claimed.

This repository contains source code and documentation. Original clients,
textures, fonts, audio, native templates, tool SDKs and Wwise license keys are
excluded. The local build needs those inputs; a fresh clone is not a complete
standalone build environment. Original code is GPL-3.0-only.

''' + tail, 'utf8')
    report = {'version': '0.4.1', 'checkout': str(OUT), 'sourceOnly': True,
              'filesCopied': len(copied), 'files': copied, 'assetsExcluded': True,
              'licenseKeysExcluded': True, 'pushed': False}
    (ROOT / 'docs/evidence/github120-preparation.json').write_text(json.dumps(report, indent=2) + '\n', 'utf8')
    print(json.dumps({key: value for key, value in report.items() if key != 'files'}, indent=2))


if __name__ == '__main__':
    main()
