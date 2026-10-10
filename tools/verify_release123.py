"""Verify the delivered 0.4.3 archives against their native build inputs."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/evidence'


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    menus = read(EVIDENCE / 'stage123-completion.json')
    assert len(menus['menus']) == 8
    for name, digest in menus['sources'].items():
        assert sha(ROOT / 'BetaGwent/ui/src' / name) == digest, name
    for menu in menus['menus']:
        assert menu['bindings'] == 46 and sha(Path(menu['resource'])) == menu['sha256']
        suffix = '' if menu['entry'] == 'BetaGwentBoard' else '-' + menu['entry']
        native = read(EVIDENCE / f"stage123-{menu['language']}-board-resource-update{suffix}.json")
        assert native['nativeABCMatchesBuiltSWF'] and native['headerTableChunkChecksumsVerified']
        assert native['updatedSha256'] == menu['sha256']
    states = ROOT / 'BetaGwent/build/stage123/powershell'
    packages = []
    for language in ('ru', 'en'):
        state = read(states / f'{language}-compile.json')
        build = Path(state['compiled'])
        compiled = read(build / 'result.json')
        assert compiled['exitCode'] == 0 and not compiled['timedOut']
        assert compiled['patchSourcesUnchangedDuringCompile']
        assert 'Success! Patch scripts blob saved' in (build / 'stdout.txt').read_text('utf8', errors='replace')
        project = ROOT / f'BetaGwent/build/release123/{language}/project/BetaGwent0924/workspace/scripts'
        assert len(compiled['patchSourcesBefore']) == 69
        assert any(x['path'].endswith('opponentRotation.ws') for x in compiled['patchSourcesBefore'])
        for source in compiled['patchSourcesBefore']:
            assert sha(project / source['path']) == source['sha256'], source['path']
        limits = read(ROOT / f'BetaGwent/build/release123/{language}/menu-input.json')
        assert len(limits) == 4 and all(item['after'] < 55 * 1024 * 1024 for item in limits.values())
        release = read(EVIDENCE / f'stage123-release-{language}.json')
        archive = Path(release['archive'])
        assert release['version'] == '0.4.3' and release['archiveVerified']
        assert sha(archive) == release['archiveSha256']
        with zipfile.ZipFile(archive) as zipped:
            assert zipped.testzip() is None
            for item in release['files']:
                assert hashlib.sha256(zipped.read(item['path'])).hexdigest() == item['sha256'], item['path']
            info = json.loads(zipped.read('Mods/modBetaGwent0924/info.json'))
            assert info['version'] == '0.4.3' and info['gameVersion'] == '5.01'
            assert language.upper() in info['description']
            assert hashlib.sha256(zipped.read('Mods/modBetaGwent0924/content/precompiled.rsblob')).hexdigest() == sha(build / 'compiled/blob.rsblob')
            notes = zipped.read(f'CHANGELOG_{language.upper()}.md')
            # Packaging reads/writes text with universal newline conversion on Windows.
            # The manifest above still verifies exact archived bytes; compare source text here.
            source_notes = (ROOT / f'BetaGwent/release/publish-0.4.3/CHANGELOG_{language.upper()}.md').read_text('utf8')
            assert notes.decode('utf8').splitlines() == source_notes.splitlines()
            for name in ('LICENSE', 'SOURCE.txt'):
                assert name in zipped.namelist()
        packages.append(dict(language=language, archive=str(archive), bytes=archive.stat().st_size,
                             sha256=release['archiveSha256'], crcAndManifestVerified=True,
                             freshNativeSources=len(compiled['patchSourcesBefore']), menusUnder55MiB=True))
    checks = {name: read(EVIDENCE / (name + '.json')) for name in ('ai123', 'rotation123', 'controller123', 'catalog123', 'crafting123', 'wcc-retry123')}
    previous = read(EVIDENCE / 'previous-release123.json')
    assert len(previous) == 2
    for path, digest in previous.items():
        assert sha(ROOT / path) == digest, path
    result = dict(stage=123, version='0.4.3', nativeMenus=8, bindingsPerMenu=46,
                  packages=packages, regressions=checks, retailGameTested=False,
                  nativeSaveRoundtripTested=False, nativeControllerTested=False,
                  previousReleaseUnmodified=True)
    (EVIDENCE / 'release123-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
