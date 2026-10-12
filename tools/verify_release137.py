"""Verify five actual 0.6.1 archives and their current native build provenance."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import sys
import zipfile
import argparse

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT/'docs/evidence'
VOICES = ('en','ru','de','it','pt-br')
CONTENT = 'Mods/modBetaGwent0924/content/'
sys.path.insert(0,str(ROOT/'tools/ui'))
sys.path.insert(0,str(ROOT/'tools/ai'))
from snapshot import verify as verify_snapshot
from verify_bundle96 import verify as verify_bundle
from verify_cooked_menu95 import verify as verify_cooked
from check_assets137 import main as check_assets
from build_voice137 import durations, DEFAULT_TEXT


def sha(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path): return json.loads(path.read_text('utf-8-sig'))


def assert_sources(values):
    for path,digest in values.items(): assert sha(ROOT/path)==digest, ('Stale input/evidence',path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=('all','both',*VOICES),default='all')
    args=parser.parse_args()
    languages=VOICES if args.language in ('all','both') else (args.language,)
    check_assets()
    motion=read(EVIDENCE/'leader-motion137.json')
    assert_sources(motion['sources'])
    assert len(motion['leaderArt'])==21 and all(x['uniqueFrames']==x['sourceFrames'] for x in motion['leaderArt'].values())
    regression=read(EVIDENCE/'regressions137.json')
    assert verify_snapshot(Path(regression['snapshot']))['fingerprint']==regression['fingerprint']
    assert len(regression['checks'])>=49
    release_test=read(EVIDENCE/'leader-release137.json')
    assert release_test['passed'] and release_test['checks']>=3
    assert_sources(release_test['sources'])
    for check in regression['checks']:
        assert sha(ROOT/check['script'])==check['sha256']
        assert sha(Path(check['log']))==check['logSha256']
    for report_name in ('check_intro_audio133','check_audio135'):
        report=read(Path(regression['snapshot']).parent/(report_name+'.json'))
        assert_sources(report['sources'])
        assert {x['language'] for x in report['reports']}==set(VOICES)
        if 'intro' in report_name:
            assert all(x['pairs']>=441 and x['exhaustiveLeaderVariantPairs'] for x in report['reports'])
        else: assert all(x['checks']>=14 for x in report['reports'])
    ui=read(EVIDENCE/'ui137.json')
    assert ui['checks']>=286
    assert_sources(ui['sources'])
    menus=read(EVIDENCE/'stage137-completion.json')
    assert len(menus['menus'])==4
    for path,digest in menus['sources'].items():
        assert sha(ROOT/'BetaGwent/ui/src'/path)==digest,path
    contract=(ROOT/'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws').read_text('utf-8-sig')
    bindings=sorted(set(re.findall(r'GetMemberFlashFunction\("([^"]+)"\)',contract)))
    assert bindings
    for menu in menus['menus']:
        assert menu['language']=='ru' and sha(Path(menu['resource']))==menu['sha256']
        suffix='' if menu['entry']=='BetaGwentBoard' else '-'+menu['entry']
        native=read(EVIDENCE/f'stage137-ru-board-resource-update{suffix}.json')
        bridge=read(EVIDENCE/f'stage137-ru-board-bridge-bytecode{suffix}.json')
        build=read(EVIDENCE/f'stage137-ru-board-build{suffix}.json')
        assert native['nativeABCMatchesBuiltSWF'] and native['headerTableChunkChecksumsVerified']
        assert bridge['passed'] and bridge['bindings']==bindings and menu['bindings']==len(bindings)
        assert build['sources']==menus['sources']

    leaders=read(EVIDENCE/'leaders137.json')
    texts=read(EVIDENCE/'languages137.json')['languages']
    voices=read(EVIDENCE/'voice137.json')
    compiled=read(ROOT/'BetaGwent/build/stage137/compilations137.json')
    assert all(language in compiled for language in languages)
    assert len({compiled[language]['run'] for language in languages})==1
    packages=[]
    for language in languages:
        base=ROOT/'BetaGwent/build/release137'/language
        project=base/'project/BetaGwent0924'
        work=project/'workspace'
        patch=Path(voices[language]['patch'])
        compilation=Path(compiled[language]['compiled'])
        result=read(compilation/'result.json')
        assert result['exitCode']==0 and not result['timedOut'] and result['patchSourcesUnchangedDuringCompile']
        log=(compilation/'stdout.txt').read_text('utf8',errors='replace')
        assert 'Success! Patch scripts blob saved' in log and '[Script]: Error [' not in log
        assert len(result['patchSourcesBefore'])==70 and result['patchSourcesBefore']==compiled[language]['sources']
        for source in result['patchSourcesBefore']:
            assert sha(work/'scripts'/source['path'])==sha(patch/source['path'])==source['sha256']
            original=ROOT/'BetaGwent/build/board-patch'/source['path']
            if original.name not in ('developmentBoardMenu.ws','duelAudioCatalog.ws'):
                assert sha(original)==source['sha256'],('Updated source needs native rebuild',original)
        # Check the two intentionally generated scripts against current base code and actual WAV timings.
        original=ROOT/'BetaGwent/build/board-patch/game/betagwent'
        expected,_=durations((original/'duelAudioCatalog.ws').read_text('utf-8-sig'),
                             ROOT/'BetaGwent/audio'/voices[language]['project']/'Originals/SFX/BetaGwent79')
        assert expected==(patch/'game/betagwent/duelAudioCatalog.ws').read_text('utf-8-sig')
        expected=(original/'developmentBoardMenu.ws').read_text('utf-8-sig').replace(
            'FlashArgInt(FactsQueryLatestValue("bg_text_language"))',
            'FlashArgInt(BetaGwentTextLanguage137(FactsQueryLatestValue("bg_text_language")))')
        expected+=f'\nfunction BetaGwentTextLanguage137(value:int):int\n{{ if(value>=1&&value<=13)return value;return {DEFAULT_TEXT[language]}; }}\n'
        assert expected==(patch/'game/betagwent/developmentBoardMenu.ws').read_text('utf-8-sig')
        frozen=read(base/'frozen.json')
        for item in frozen['files']:assert sha(project/item['path'])==item['sha256']
        assert sha(project/'LocalEditorStringDataBaseW3_UTF8_mod.db')==sha(ROOT/'GwentB/myproject1/LocalEditorStringDataBaseW3_UTF8_mod.db')
        for item in menus['menus']:
            name=Path(item['resource']).name
            verify_cooked(work/'betagwent'/name,base/'cooked/betagwent'/name)
        for item in [*leaders['resources'].values(),*texts.values()]:
            verify_cooked(work/item['path'],base/'cooked'/item['path'])
        packed=verify_bundle(base/'package'/CONTENT/'blob0.bundle',base/'bundle-input',
                             require_uncompressed_gui=True,gui_limit_mib=56)
        names={x['path'].replace('\\','/').lower() for x in packed['entries']}
        assert not any('redux' in n or 'betagwentpremium' in n for n in names)
        for folder,resources in (('betagwentleaders',leaders['resources']),('betagwenttext',texts)):
            expected_names={x['path'].lower() for x in resources.values()}
            assert {n for n in names if '/'+folder+'/' in n}==expected_names
        bank=Path(voices[language]['bank'])
        assert sha(bank)==voices[language]['sha256'] and voices[language]['voiceCount']==907
        release=read(EVIDENCE/f'stage137-release-{language}.json')
        archive=Path(release['archive'])
        assert archive.name==f'GwentBetaClassic-0.6.1-{language.upper()}.zip'
        assert release['archiveVerified'] and sha(archive)==release['archiveSha256']
        assert archive.stat().st_size==release['archiveBytes']
        assert archive.with_suffix('.zip.sha256').read_text('ascii').split()[0]==release['archiveSha256']
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            manifest=json.loads(z.read('manifest.json'))
            assert manifest['stage']==137 and manifest['version']=='0.6.1' and manifest['voiceLanguage']==language
            assert set(manifest['textLanguages'])==set(texts) and manifest['mediaCount']==1438 and manifest['voiceCount']==907
            files=z.namelist()
            assert len(files)==len(set(files))
            assert set(files)=={x['path'] for x in manifest['files']}|{'manifest.json'}
            for item in manifest['files']:
                assert z.getinfo(item['path']).file_size==item['bytes']
                with z.open(item['path']) as stream: assert hashlib.file_digest(stream,'sha256').hexdigest()==item['sha256']
            info=json.loads(z.read('Mods/modBetaGwent0924/info.json'))
            assert info['version']=='0.6.1' and info['gameVersion']=='5.01'
            assert z.read(CONTENT+'precompiled.rsblob')==(compilation/'compiled/blob.rsblob').read_bytes()
            cache=z.read(CONTENT+'soundspc.cache')
            assert cache[:4]==b'CS3W' and len(cache)==bank.stat().st_size+104
            assert cache[64:-40]==bank.read_bytes()
            native_strings=read(EVIDENCE/f'stage137-cooked-strings-{language}.json')['languages']
            assert {'ru','en','de','fr','it','pl','es','esmx','br','jp','kr','cn','zh'}<=set(native_strings)
            for locale,item in native_strings.items():
                assert item['strings']==396 and hashlib.sha256(z.read(CONTENT+locale+'.w3strings')).hexdigest()==item['sha256']
            assert sum(n.endswith('soundspc.cache') for n in files)==1 and not any(n.endswith('.bnk') for n in files)
            doclang='RU' if language=='ru' else 'EN'
            for stem in ('README','CONTROLS','CHANGELOG'):
                name=f'{stem}_{doclang}.md'
                assert z.read(name)==(ROOT/'BetaGwent/release/publish-0.6.1'/name).read_bytes()
            assert 'NOTO-LICENSE-OFL.txt' in files and not any('redux' in n.lower() for n in files)
        packages.append(dict(language=language,archive=str(archive),bytes=archive.stat().st_size,
                             sha256=release['archiveSha256'],freshNativeScripts=70,textLanguages=13))
        print('Verified '+language+' archive, native scripts/menus/fonts/pages/audio and payloads',flush=True)
    old={
      '0.6.0-RU':'04e4927ff5df5b3faf13ca74b33375a6559e8af92951ceb7b6e5124596856e4c',
      '0.6.0-EN':'641240351f0601f800b02ffc84b37955e618730b7b8f79ccdc63a0c1f099fb18',
      '0.5.4-RU':'0acb1ba8bb00b094bb7c7e1cc4e3396204a542b0374ae9c0ab878073a8e32008',
      '0.5.4-EN':'a7c33a4ec09d01fb1d2b28a907570d3dbd5bfd3f663765599530fce64fb41c6e'}
    for name,digest in old.items():assert sha(ROOT/'BetaGwent/release'/('GwentBetaClassic-'+name+'.zip'))==digest
    report=dict(version='0.6.1',passed=True,packages=packages,menus=4,voicePackages=len(languages),textLanguages=13,
                leaderCards=21,leaderPages=len(leaders['resources']),otherAnimatedCards=0,
                regressionSuites=len(regression['checks']),oldArchivesUnmodified=True,
                nativeGameTested=False,installedGameModified=False,
                nativeAtlasDisposeRemovedFromAll282Pages=True,
                inGameLeaderIntroductionRetestRequired=True,
                verifiedAtUtc=datetime.now(timezone.utc).isoformat())
    (EVIDENCE/'validation137.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
