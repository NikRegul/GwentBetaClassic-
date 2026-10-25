"""Copy and hash-check permanent build inputs before retiring old build trees.

This command never deletes its donors. Run only in the original local checkout.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from build_inputs import INPUTS


HASHES = {}

def sha(path):
    info=path.stat()
    key=(str(path.resolve()),info.st_size,info.st_mtime_ns,info.st_ctime_ns)
    if key in HASHES:return HASHES[key]
    with path.open('rb') as stream:
        result=hashlib.file_digest(stream, 'sha256').hexdigest()
    after=path.stat()
    assert (info.st_size,info.st_mtime_ns,info.st_ctime_ns)==(after.st_size,after.st_mtime_ns,after.st_ctime_ns),path
    HASHES[key]=result
    return result


def save(path, data):
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--resume', action='store_true', help='Finish an interrupted migration; verify existing payloads before reuse')
    args = parser.parse_args()
    manifest = INPUTS / 'manifest.json'
    if args.verify:
        data = json.loads(manifest.read_text('utf8'))
        for item in data['files']:
            path = INPUTS / item['path']
            assert path.is_file() and not path.is_symlink() and sha(path) == item['sha256'], path
        print('Verified permanent inputs:', len(data['files']), 'files', flush=True)
        return
    assert not INPUTS.exists() or args.resume, 'Existing inputs require --verify or --resume'
    INPUTS.mkdir(parents=True, exist_ok=args.resume)
    copied = {}

    def copy(source, relative):
        source = Path(source)
        assert source.is_file() and not source.is_symlink(), source
        target = INPUTS / relative
        assert target.resolve().is_relative_to(INPUTS.resolve())
        if target.exists():
            original=sha(source)
            if sha(target)==original:
                copied[target.relative_to(INPUTS).as_posix()]=dict(origin=source.relative_to(ROOT).as_posix(),originalSha256=original)
                return target
            # These two metadata files have already had their absolute references
            # rebased on a previous attempt. Recreate them from the same donor;
            # their payload hashes are independently checked again below.
            rebased = relative.as_posix().endswith('/ui-inputs.json') or relative.as_posix()=='accepted-assets/menu-music-caches/manifest.json'
            assert args.resume and rebased, 'Existing payload differs: '+str(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        before = sha(source)
        shutil.copy2(source, target)
        assert sha(target) == before == sha(source), source
        copied[target.relative_to(INPUTS).as_posix()] = dict(origin=source.relative_to(ROOT).as_posix(), originalSha256=before)
        return target

    def tree(source, relative):
        source = Path(source)
        assert source.is_dir() and not source.is_junction() and not source.is_symlink(), source
        for path in sorted(source.iterdir()):
            assert not path.is_symlink() and not path.is_junction(), path
            if path.name == '__pycache__':
                continue
            if path.is_dir():
                tree(path, Path(relative) / path.name)
            else:
                copy(path, Path(relative) / path.name)

    old = ROOT / 'BetaGwent/build'
    for name in ['scripts', 'classic-audit']:
        tree(old / 'release090-final12' / name, Path('script-baseline') / name)
    for platform in ['1.32', '5.0+']:
        name = f'GwentBetaClassic-0.9.0-{platform}-AllLanguages.zip'
        copy(old / 'release090-final17-release/package-candidate/archives-optional-keep' / name, Path('package-baseline') / name)
    for source, dest in [('release091-ui4', 'ui'), ('release090-ui12', 'ui-baseline')]:
        for platform in ['classic', 'nextgen']:
            folder = old / source / platform
            tree(folder / 'ui', Path(dest) / platform / 'ui')
            for name in ['ui-inputs.json', 'subimages.json']:
                if (folder / name).exists():
                    copy(folder / name, Path(dest) / platform / name)
            # Exact original templates are needed when compiling a changed UI.
            menus = json.loads((folder / 'menus/menus.json').read_text('utf8'))
            for item in menus['menus']:
                template = copy(Path(item['path']), Path(dest) / platform / 'menus' / Path(item['path']).name)
                assert sha(template) == item['sha256']
                item['path'] = str(template)
                swf = Path(copied[template.relative_to(INPUTS).as_posix()]['origin']).with_suffix('.swf')
                if (ROOT / swf).exists():
                    copy(ROOT / swf, Path(dest) / platform / 'menus' / swf.name)
            menu_manifest = INPUTS / dest / platform / 'menus/menus.json'
            save(menu_manifest, menus)
            pinned = INPUTS / dest / platform / 'ui-inputs.json'
            data = json.loads(pinned.read_text('utf8'))
            for item in data['menus']:
                resource = copy(Path(item['resource']), Path(dest) / platform / 'input-templates' / Path(item['resource']).name)
                assert sha(resource) == item['sha256']
                item['resource'] = str(resource)
            save(pinned, data)
        if (old / source / 'gamepad-source.json').exists():
            copy(old / source / 'gamepad-source.json', Path(dest) / 'gamepad-source.json')
        print('Copied and verified', dest, flush=True)
    assets = old / 'release091h-final2'
    # Preserve only manifest-authoritative payloads, not extracted duplicates.
    ui = json.loads((assets / 'ui-patch/manifest.json').read_text('utf8'))
    for platform in ui['platforms'].values():
        for item in platform['files'].values():
            source = Path(item['path'])
            target = copy(source, Path('accepted-assets/ui-patch') / source.relative_to(assets / 'ui-patch'))
            assert sha(target) == item['sha256']
            item['path'] = str(target)
    save(INPUTS / 'accepted-assets/ui-patch/manifest.json', ui)
    tree(assets / 'menu-music-caches', 'accepted-assets/menu-music-caches')
    copy(assets / 'menu-music/music.json', 'accepted-assets/menu-music/music.json')
    music_path = INPUTS / 'accepted-assets/menu-music-caches/manifest.json'
    music = json.loads(music_path.read_text('utf8'))
    for platform in music['platforms'].values():
        for key in ['cache', 'bank']:
            source = Path(platform[key])
            # Accepted h assets may retain an origin path from the identical g
            # cache. Match the payload subtree and verify its authoritative hash.
            parts=source.parts
            assert parts.count('menu-music-caches')==1,source
            target = INPUTS / 'accepted-assets/menu-music-caches' / Path(*parts[parts.index('menu-music-caches')+1:])
            assert sha(target) == platform[key + 'Sha256']
            platform[key] = str(target)
    save(music_path, music)
    tree(old / 'classic-audio091-split1', 'classic-audio')
    # Retain authoring materials so later font/audio/VFX work does not depend
    # on discarded release snapshots. They remain local and are never published.
    authoring = ['languages137', 'text138', 'special-vfx142', 'element-vfx163', 'elements164',
                 'leader-intros142', 'leader-intro-resources142', 'leaders137', 'leader-loops137',
                 'audio109', 'audio135', 'audio137', 'audio141', 'universal081/audio-classic',
                 'universal081/audio-merged', 'universal081/audio-nextgen',
                 'classic081-geometry-effects-fix14/audio']
    for name in authoring:
        if (old / name).is_dir():
            tree(old / name, Path('authoring') / name)
            print('Preserved authoring:', name, flush=True)
    files = []
    for path in sorted(INPUTS.rglob('*')):
        if path.is_file():
            rel = path.relative_to(INPUTS).as_posix()
            files.append(dict(path=rel, bytes=path.stat().st_size, sha256=sha(path), **copied.get(rel, {})))
    save(manifest, dict(schema=1, files=files, note='Local licensed inputs; historical origin paths are provenance only. Donors were not deleted.'))
    print('Permanent input manifest:', len(files), 'files;', sum(x['bytes'] for x in files), 'bytes', flush=True)


if __name__ == '__main__':
    main()
