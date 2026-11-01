"""Sync reviewed source paths into the existing public checkout; never push.

The working repository also contains local game resources. Do not push its
unfiltered history into the source-only public repository.
"""
from pathlib import Path
import argparse, gzip, hashlib, json, re, shutil, subprocess

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT/'BetaGwent/publication'
SUFFIXES = {'.py','.js','.cjs','.as','.ws','.json','.md','.txt','.csv','.xml','.ps1','.cmd','.cs','.csproj','.cpp','.h','.gz'}
PREFIXES = ('BetaGwent/scripts/', 'BetaGwent/development/scripts/', 'BetaGwent/ui/src/', 'BetaGwent/compat/', 'BetaGwent/native/', 'tools/')
DATA_PREFIXES = ('data/beta924/ai/', 'data/beta924/design/', 'data/beta924/duel/', 'data/beta924/localization')
SKIP_PARTS = {'__pycache__','node_modules','vendor','bin','obj','build','assets','wwise-base'}
PRIVATE_TOOLS = {'github_auth_probe89.py','download_github_cli93.py','github_upload_batches89.py',
                 'capture_capability_result.py','inspect_crash061.py','inline_showcase090.py',
                 'build_installers.py','test_installer.ps1','package_language_layout.py'}
PRIVATE_PREFIXES = ('docs/agent-evaluation/', 'docs/prompts/')
SECRETS = [r'(?m)^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})', r'\bsk-(?:proj-)?[A-Za-z0-9_-]{40,}', r'<Property[^>]+Name="LicenseKey"[^>]+Value="[^"\s]+"']

def files(directory, *args):
    return set(subprocess.check_output(['git','ls-files','-z',*args], cwd=directory).decode('utf8').split('\0'))-{''}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--ui-snapshot', type=Path, help='Reviewed Board and Classic overlay directory; preserve unfinished local UI work')
    args = parser.parse_args()
    assert (PUBLIC/'.git').is_dir(), 'Existing separate public checkout required'
    remote = subprocess.check_output(['git','remote','get-url','origin'], cwd=PUBLIC, text=True).strip()
    assert remote == 'https://github.com/NikRegul/GwentBetaClassic-.git', 'Unexpected public remote'
    old = files(PUBLIC)
    candidates = files(ROOT, '--cached', '--others', '--exclude-standard')
    roots = {'README.md','LICENSE','ATTRIBUTIONS.md','Build-0.9.3.cmd','Build-0.9.4.cmd','Build-0.9.4a.cmd','Build-0.9.5.cmd','.gitattributes'}
    # Required by the release freeze and localization compiler; JSON metadata,
    # not artwork/audio. Keep its historical game-data attribution.
    catalog = 'data/beta924/normalized/catalog.json'
    selected = {}
    overrides = {}
    if args.ui_snapshot:
        directory = args.ui_snapshot.resolve()
        assert directory.is_relative_to(ROOT.resolve()), 'UI snapshot must be inside the workspace'
        for folder in ('src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'):
            overrides['BetaGwent/ui/'+folder+'/BetaGwentBoard.as'] = directory/'BetaGwentBoard.as'
        overrides['tools/features091/BetaGwentBoard_classic093.as'] = directory/'BetaGwentBoard_classic093.as'
        assert all(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(directory) for p in overrides.values()), 'Missing or unsafe reviewed UI snapshot'
    for name in sorted(candidates):
        if name.startswith(PRIVATE_PREFIXES) or (name.startswith('docs/reviews/') and any(word in Path(name).name for word in ('cleanup', 'space-audit'))):
            continue
        p = overrides.get(name, ROOT/name)
        if name.startswith('tools/saveprobe094/') and p.suffix == '.txt':
            continue
        if not p.is_file() or p.is_symlink() or any(x in SKIP_PARTS for x in Path(name).parts) or p.name in PRIVATE_TOOLS:
            continue
        allowed = name in roots or name == catalog or name.startswith(PREFIXES) or name.startswith(DATA_PREFIXES)
        if name.startswith('docs/'):
            allowed = p.suffix == '.md' or name in old and p.suffix in {'.json','.csv','.txt'}
        if name.startswith('data/') and name in old:
            allowed = True
        if name.startswith('BetaGwent/ui/src-') and p.name == 'BetaGwentBoard.as':
            allowed = True
        if not allowed or p.suffix not in SUFFIXES and name not in roots:
            continue
        raw = p.read_bytes()
        assert len(raw) < (50 if name == catalog else 10)*1024**2, 'Review oversized public source: '+name
        payload = raw
        if p.suffix == '.gz':
            assert name.startswith('tools/ai/fixtures/') and name.endswith('.json.gz'), 'Review compressed public source: '+name
            with gzip.open(p, 'rb') as compressed:
                payload = compressed.read(10*1024**2)
            assert len(payload) < 10*1024**2, 'Review oversized compressed fixture: '+name
            json.loads(payload)
        text = payload.decode('utf-16' if payload[:2] in (b'\xff\xfe',b'\xfe\xff') else 'utf-8-sig')
        assert not any(re.search(pattern, text) for pattern in SECRETS), 'Potential secret: '+name
        selected[name] = (p, raw)
    assert roots <= selected.keys(), 'Required public sources missing or ignored: '+', '.join(sorted(roots-selected.keys()))
    boards = [selected['BetaGwent/ui/'+folder+'/BetaGwentBoard.as'][1]
              for folder in ('src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg')]
    assert all(raw == boards[0] and raw.startswith(b'\xef\xbb\xbf') and b'\n' not in raw.replace(b'\r\n', b'') for raw in boards), 'Review five Board copies and BOM/CRLF before exporting'
    gate = selected['tools/features091/prepare_ui091.py'][1].decode('utf-8-sig')
    for name in ('BetaGwent/ui/src/BetaGwentBoard.as','tools/features091/BetaGwentBoard_classic093.as'):
        assert hashlib.sha256(selected[name][1]).hexdigest() in gate, 'Review UI source SHA gate before exporting: '+name
    unexpected = files(PUBLIC, '--others', '--exclude-standard')-selected.keys()-{'.gitignore'}
    assert not unexpected, 'Review unexpected public checkout files before staging: '+', '.join(sorted(unexpected))
    removed = old-selected.keys()-{'.gitignore'}
    changed = sum(not (PUBLIC/n).is_file() or (PUBLIC/n).read_bytes()!=raw for n,(_,raw) in selected.items())
    if args.apply:
        for name in sorted(removed):
            p = PUBLIC/name
            assert p.resolve().is_relative_to(PUBLIC.resolve()) and not p.is_symlink(), name
            p.unlink(missing_ok=True)
        for name,(p,raw) in selected.items():
            dest = PUBLIC/name
            assert dest.resolve().is_relative_to(PUBLIC.resolve()), name
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.is_file() or dest.read_bytes()!=raw:
                shutil.copyfile(p,dest)
            assert dest.read_bytes() == raw, name
        (PUBLIC/'.gitignore').write_text('/BetaGwent/build/\n/BetaGwent/build-inputs/\n/BetaGwent/toolchains/\n/BetaGwent/publication/\n/BetaGwent/drafts/\n/BetaGwent/reports/\n/BetaGwent/release/\n/BetaGwent/training/\n/tools/vendor/\n/release/\n/tmp/\n/worktrees/\n**/__pycache__/\n**/node_modules/\n**/bin/\n**/obj/\n*.pyc\n*.log\n*.zip\n*.exe\n*.dll\n*.jar\n*.tmp\n*.bak\n', 'utf8')
        with (PUBLIC/'.gitignore').open('a', encoding='utf8') as ignore:
            ignore.write('/tools/saveprobe094/*.txt\n')
        # Empty source directories are harmless and are not tracked by Git.
    print(json.dumps(dict(sourceOnly=True,files=len(selected),changed=changed,removedObsolete= len(removed),reviewedUiSnapshot=bool(overrides),applied=args.apply,pushed=False)))

if __name__ == '__main__':
    main()
