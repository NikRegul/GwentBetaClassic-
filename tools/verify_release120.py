"""Verify 0.4.1 native artifacts and the files actually delivered in both ZIPs."""
import hashlib
import json
import zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/evidence'


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    menus = read(EVIDENCE / 'stage120-completion.json')
    assert len(menus['menus']) == 8
    assert all(m['bindings'] == 46 and sha(Path(m['resource'])) == m['sha256'] for m in menus['menus'])
    for menu in menus['menus']:
        suffix = '' if menu['entry'] == 'BetaGwentBoard' else '-' + menu['entry']
        native = read(EVIDENCE / f"stage120-{menu['language']}-board-resource-update{suffix}.json")
        assert native['nativeABCMatchesBuiltSWF'] and native['headerTableChunkChecksumsVerified']
        assert native['updatedSha256'] == menu['sha256']
    for name, digest in menus['sources'].items():
        assert sha(ROOT / 'BetaGwent/ui/src' / name) == digest, name
    boards = read(EVIDENCE / 'board120.json')
    assert len(boards['boards']) == 10 and len(boards['dividers']) == 6
    assert boards['dimensionsUnchanged'] and boards['originalsUnchanged'] and boards['runtimeMirrorRequired']
    for path, digest in boards['sourceHashes'].items():
        assert sha(Path(path)) == digest, path
    atlas = ROOT / 'BetaGwent/ui/assets/compact98/boards.png'
    hud = ROOT / 'BetaGwent/ui/assets/battle120/hud120.png'
    assert sha(atlas) == boards['boardAtlasSha256']
    assert sha(hud) == boards['hudAtlasSha256']
    assert Image.open(atlas).size == (3072, 2655)
    assert Image.open(hud).size == (1024, 1988)
    assert 'half.scaleX=-1' in (ROOT / 'BetaGwent/ui/src/BetaGwentBoard.as').read_text('utf8').replace(' ', '')
    states = ROOT / 'BetaGwent/build/stage120/powershell'
    run = read(states / 'ru-compile.json')['run']
    checks = read(states / f'{run}-ai/snapshot/checks119.json')
    assert checks['profiles'] == 46 and checks['checks'] >= 534
    lock_checks = read(states / f'{run}-ai/snapshot/checks120.json')
    assert lock_checks['graveyardLockPassed'] and lock_checks['checks'] == 11
    result = {'stage': 120, 'version': '0.4.1', 'nativeMenus': 8, 'bindingsPerMenu': 46,
              'archetypes': 46, 'archetypeChecks': checks['checks'], 'graveyardLockRegressionPassed': True,
              'originalBoardsUnmodified': True, 'atlasDimensionsUnchanged': True,
              'gameRuntimeVerified': False, 'retailInstallationModified': False, 'packages': []}
    for language in ('ru', 'en'):
        state = read(states / f'{language}-compile.json')
        assert state['run'] == run
        build = Path(state['compiled'])
        compiled = read(build / 'result.json')
        assert compiled['exitCode'] == 0 and not compiled['timedOut']
        assert compiled['patchSourcesUnchangedDuringCompile']
        assert 'Success! Patch scripts blob saved' in (build / 'stdout.txt').read_text('utf8', errors='replace')
        for item in compiled['artifacts']:
            assert sha(Path(item['path'])).upper() == item['sha256']
        project = ROOT / f'BetaGwent/build/release120/{language}/project/BetaGwent0924/workspace/scripts'
        native_sizes = read(ROOT / f'BetaGwent/build/release120/{language}/menu-input.json')
        assert len(native_sizes) == 4 and all(item['after'] < 55 * 1024 * 1024 for item in native_sizes.values())
        assert len(compiled['patchSourcesBefore']) == 67
        for source in compiled['patchSourcesBefore']:
            assert sha(project / source['path']) == source['sha256'], source['path']
        release = read(EVIDENCE / f'stage120-release-{language}.json')
        archive = Path(release['archive'])
        assert release['version'] == '0.4.1' and release['archiveVerified']
        assert sha(archive) == release['archiveSha256']
        with zipfile.ZipFile(archive) as zipped:
            assert zipped.testzip() is None
            for item in release['files']:
                assert hashlib.sha256(zipped.read(item['path'])).hexdigest() == item['sha256'], item['path']
            assert all(name in zipped.namelist() for name in ('UPDATE.md', 'LICENSE', 'SOURCE.txt'))
            info = json.loads(zipped.read('Mods/modBetaGwent0924/info.json'))
            assert info['version'] == '0.4.1' and info['gameVersion'] == '5.01'
            assert language.upper() in info['description']
            blob = zipped.read('Mods/modBetaGwent0924/content/precompiled.rsblob')
            assert hashlib.sha256(blob).hexdigest() == sha(build / 'compiled/blob.rsblob')
            changelog = zipped.read(f'CHANGELOG_{language.upper()}.md').decode('utf8')
            assert '0.4.1' in changelog and '0.4.0' in changelog and '0.3.4' in changelog
            if language == 'ru':
                assert '\u0412\u0441\u0435 \u0434\u0435\u0441\u044f\u0442\u044c' in changelog
            cumulative = ROOT / f'BetaGwent/release/publish-0.4.1/CHANGELOG_0.3.4_to_0.4.1_{language.upper()}.md'
            text = cumulative.read_text('utf8')
            assert '0.3.5-preview.1' in text and '0.4.0' in text and '0.4.1' in text
            assert '???' not in text
        result['packages'].append({'language': language, 'archive': str(archive), 'bytes': archive.stat().st_size,
                                   'sha256': release['archiveSha256'], 'freshCompiledSources': 67,
                                   'crcAndManifestVerified': True})
    for language, digest in (
        ('RU', 'd939f807e30db0c71a6138f91c01bed7b892ab551a19a94571deae748cd318f9'),
        ('EN', '4e033c60529d6006f62e3551e79123c63aaa99555db1e76570a6b13ce6ed3009'),
    ):
        assert sha(ROOT / f'BetaGwent/release/GwentBetaClassic-0.4.0-{language}.zip') == digest
    result['previousReleaseUnmodified'] = True
    (EVIDENCE / 'stage120-final-release.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
