"""Build a Classic voice target from a verified, frozen Next-Gen release stage.

The shared core/UI is selected by hashes; all platform edits are generated.
Completed phases may be reused only with matching input and output hashes.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

from formats import ROOT,require,sha,sound_index,write_sound_cache,bundle_entries
from dependencies import copy_dependency_cache
sys.path.insert(0,str(ROOT/'tools'))
from freeze_platform_inputs import freeze


def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')


def run(script,*arguments):
    print(Path(script).name,flush=True)
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/script),*map(str,arguments)],cwd=ROOT,check=True)


def init_probe(game,probe):
    require(probe.is_relative_to(ROOT/'BetaGwent/build') and not probe.exists(),'Fresh compiler runtime required')
    probe.mkdir(parents=True);shutil.copytree(game/'bin',probe/'bin')
    content=probe/'content';content.mkdir();shutil.copytree(game/'content/content0/scripts',content/'content0/scripts')
    def junction(source,destination):
        command="New-Item -ItemType Junction -Path '"+str(destination).replace("'","''")+"' -Target '"+str(source).replace("'","''")+"' | Out-Null"
        subprocess.run(['powershell','-NoProfile','-Command',command],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    for path in (game/'content').iterdir():
        if path.is_dir() and path.name!='content0':junction(path,content/path.name)
        elif path.is_file():shutil.copy2(path,content/path.name)
    for path in (game/'content/content0').iterdir():
        if path.name=='scripts':continue
        if path.is_dir():junction(path,content/'content0'/path.name)
        else:shutil.copy2(path,content/'content0'/path.name)
    if (game/'DLC').exists():junction(game/'DLC',probe/'DLC')


def compilation(prepared,probe,result_path):
    prep=read(prepared/'preparation.json')
    if result_path is None:
        result_path=probe/'runs/classic-port/result.json'
        if not result_path.exists():
            audit=read(prep['audit'])
            if not probe.exists():init_probe(Path(audit['game']),probe)
            run('tools/classic132/native_compile.py','--probe-root',probe,'--prepared',prepared,'--label','classic-port','--compiler-feedback')
    result=read(result_path)
    require(result['compilePassed'] and not result['errors'] and not result['timedOut'],'Classic compiler did not pass')
    require(result['preparationManifestSha256']==sha(prepared/'preparation.json'),'Compiler used different sources')
    cache=next(x for x in result['freshArtifacts'] if Path(x['path']).name=='x64.final.redscripts')
    candidates=[Path(result_path).parent/'compiled/x64.final.redscripts',Path(cache['path'])]
    require(any(p.is_file() and sha(p)==cache['sha256'] for p in candidates),'Compiled cache evidence unavailable or changed')
    return result_path,result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-stage',type=int,required=True);p.add_argument('--version',required=True)
    p.add_argument('--test-revision',type=int,default=1)
    p.add_argument('--language',choices=('ru','en','de','it','pt-br'),default='ru')
    p.add_argument('--release',action='store_true',help='Use final version/name without a test suffix; gameplay acceptance remains separate')
    p.add_argument('--gui-limit-mib',type=int,help='Defaults to the selected Next-Gen stage budget')
    p.add_argument('--game',type=Path,default=Path(r'D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt'))
    p.add_argument('--out',type=Path,required=True);p.add_argument('--audit',type=Path)
    p.add_argument('--probe-root',type=Path);p.add_argument('--compile-result',type=Path);p.add_argument('--resources',type=Path)
    p.add_argument('--menus',type=Path,help='Verified shared Classic menus from this source stage')
    p.add_argument('--previous',type=Path,help='Previous Classic package manifest for a source change report')
    a=p.parse_args();out=a.out.resolve();require(out.is_relative_to(ROOT/'BetaGwent/build') and out!=ROOT/'BetaGwent/build','Output must be a build subdirectory')
    require(re.fullmatch(r'[A-Za-z0-9_.+-]+',a.version) and a.test_revision>0,'Invalid version or test revision')
    source=ROOT/f'BetaGwent/build/release{a.source_stage}/{a.language}/package';release=read(source/'manifest.json')
    require(release['version']==a.version and release['stage']==a.source_stage and release['language']==a.language,'Source version/stage/language mismatch')
    require(release['voiceLanguage']==a.language and len(release['textLanguages'])==13,'Source voice/text languages mismatch')
    budget=a.gui_limit_mib if a.gui_limit_mib is not None else read(ROOT/f'BetaGwent/build/stage{a.source_stage}/gui-budget.json')['guiLimitMiB']
    require(1<=budget<=65,'GUI budget must be 1..65 MiB')
    out.mkdir(parents=True,exist_ok=True)
    generators={path.relative_to(ROOT).as_posix():sha(path) for path in sorted((ROOT/'tools/classic132').glob('*')) if path.suffix in ('.py','.inc')}
    inputs=dict(sourceStage=a.source_stage,sourceVersion=a.version,testRevision=a.test_revision,language=a.language,release=a.release,guiLimitMiB=budget,game=str(a.game.resolve()),sourceManifestSha256=sha(source/'manifest.json'),generators=generators)
    stamp=out/'build-inputs.json'
    if stamp.exists():require(read(stamp)==inputs,'Build inputs changed; choose a fresh output directory')
    else:save(stamp,inputs)
    ui=freeze(a.source_stage)
    audit=a.audit.resolve() if a.audit else out/'audit'
    if not (audit/'audit.json').exists():run('tools/recon/audit_classic132.py','--game',a.game,'--source-stage',a.source_stage,'--language',a.language,'--out',audit)
    require(read(audit/'audit.json')['sourceStage']==a.source_stage and read(audit/'audit.json').get('sourceLanguage','ru')==a.language,'Audit source stage/language mismatch')
    prepared=out/'scripts-prepared'
    if not (prepared/'preparation.json').exists():run('tools/classic132/prepare_scripts.py','--audit',audit,'--out',prepared)
    require(read(prepared/'preparation.json')['sourceStage']==a.source_stage and read(prepared/'preparation.json').get('sourceLanguage','ru')==a.language,'Prepared source stage/language mismatch')
    run('tools/classic132/verify_scripts.py',prepared)
    native_path,native=compilation(prepared,a.probe_root.resolve() if a.probe_root else out/'runtime',a.compile_result)
    menus=a.menus.resolve() if a.menus else out/'menus'
    if a.menus:require((menus/'menus.json').is_file(),'Shared menus must already be built')
    if not (menus/'menus.json').exists():run('tools/classic132/build_menus.py','--stage',a.source_stage,'--prepared',prepared,'--source-ui',ui,'--out',menus,*(['--resume'] if menus.exists() else []))
    menu_report=read(menus/'menus.json');require(menu_report['sourceStage']==a.source_stage and menu_report['frozenSources']==read(ROOT/f'docs/evidence/stage{a.source_stage}-completion.json')['sources'],'UI source mismatch')
    script=(prepared/'Mods/modBetaGwentClassic132/content/scripts/game/betagwent/developmentBoardMenu.ws').read_text('utf16')
    bindings=sorted(set(re.findall(r'GetMemberFlashFunction\("([^"]+)"\)',script)))
    if a.menus:require(menu_report.get('scriptBindings')==bindings,'Shared menu bindings differ from this voice target')
    for menu in menu_report['menus']:require(sha(menu['path'])==menu['sha256'],'Menu changed')
    resources=a.resources.resolve() if a.resources else out/'resources-classic'
    if a.resources:require((resources/'resources.json').is_file(),'Shared resources must already be built')
    if not (resources/'resources.json').exists():run('tools/classic132/build_resources.py','--stage',a.source_stage,'--menus',menus,'--game',a.game,'--out',resources,'--gui-limit-mib',budget)
    resource_report=read(resources/'resources.json');require(resource_report['sourceStage']==a.source_stage and resource_report['guiLimitMiB']==budget,'Resource stage/budget mismatch')
    replacements={Path(row['path']).name:row['sha256'] for row in menu_report['menus']}
    # Converted CR2W resources have different container hashes; check their recorded
    # authoring menu inputs rather than comparing converted bytes to source bytes.
    if a.resources:require(read(resources/'menu-inputs.json')==replacements,'Shared resources were built with different Classic menus')
    else:save(resources/'menu-inputs.json',replacements)
    for row in resource_report['entries']:require(sha(resources/'resources'/row['path'])==row['sha256'],'Resource changed')
    expected_resources={x['path']:x['sha256'] for x in resource_report['entries']}
    require({n.replace('\\','/'):hashlib.sha256(d).hexdigest() for n,d in bundle_entries(resources/'blob0.bundle')}==expected_resources,'Bundle differs from verified resources')
    require(sha(resources/'metadata.store')==resource_report['metadata']['sha256'],'Metadata changed')
    # Extract the exact frozen language bank, not an actively edited authoring bank.
    cache=source/'Mods/modBetaGwent0924/content/soundspc.cache'
    expected=next(x['sha256'] for x in release['files'] if x['path'].endswith('/soundspc.cache'));require(sha(cache)==expected,'Frozen audio cache changed')
    _,index=sound_index(cache);require(len(index)==1,'Source cache must contain a single embedded bank')
    off,size=next(iter(index.values()))
    with cache.open('rb') as f:f.seek(off);bank_bytes=f.read(size)
    bank=out/(a.language+'-nextgen.bnk')
    if bank.exists():require(bank.read_bytes()==bank_bytes,'Source bank changed')
    else:bank.write_bytes(bank_bytes)
    xml=out/'new-bank.xml'
    if not xml.exists():run('tools/vendor/audio/wwiser.pyz','-d','xml','-dn',xml.with_suffix(''),bank)
    audio=out/'audio'
    if not (audio/'audio.json').exists():run('tools/classic132/build_audio.py','--bank',bank,'--xml',xml,'--out',audio)
    audio_report=read(audio/'audio.json');require(audio_report['sourceBankSha256']==sha(bank) and audio_report['bankVersion']==88,'Audio source mismatch')
    require(sha(audio/'BetaGwent79.bnk')==audio_report['sha256'],'Classic bank changed')
    if not (audio/'legacy-verified.xml').exists():run('tools/vendor/audio/wwiser.pyz','-d','xml','-dn',audio/'legacy-verified',audio/'BetaGwent79.bnk')
    import xml.etree.ElementTree as ET
    parsed=ET.parse(audio/'legacy-verified.xml').getroot();require(not parsed.findall('.//error') and not parsed.findall('.//skip'),'Wwise structure was not fully parsed')
    sound=out/'soundspc.cache'
    sound_report=write_sound_cache(audio/'banks/Windows',sound)
    require(sound_report['mediaCount']==audio_report['mediaCount'],'Missing streamed media')
    save(out/'sound-cache.json',sound_report)
    package=out/'package';content=package/'Mods/modBetaGwentClassic132/content'
    require(not package.exists(),'Package is immutable; use a fresh build output for another archive')
    content.mkdir(parents=True);shutil.copytree(prepared/'Mods/modBetaGwentClassic132/content/scripts',content/'scripts')
    for name in ('blob0.bundle','metadata.store'):shutil.copy2(resources/name,content/name)
    dependency=source/'Mods/modBetaGwent0924/content/dep.cache'
    dependency_record=next(x for x in release['files'] if x['path'].endswith('/dep.cache'))
    require(sha(dependency)==dependency_record['sha256'],'Frozen dependency cache changed')
    copy_dependency_cache(dependency,content/'dep.cache')
    shutil.copy2(sound,content/'soundspc.cache')
    # Other voice packs are excluded. Keep the frozen text files because the
    # shared menu supports language selection and native names use these IDs.
    for path in (source/'Mods/modBetaGwent0924/content').glob('*.w3strings'):
        record=next(x for x in release['files'] if x['path'].endswith('/'+path.name));require(sha(path)==record['sha256'],'Text source changed');shutil.copy2(path,content/path.name)
    version=a.version if a.release else a.version+'-classic132-test'+str(a.test_revision)
    save(content.parent/'info.json',dict(name='Gwent Beta Classic',modName='modBetaGwentClassic132',version=version,gameVersion='1.32',voiceLanguage=a.language,textLanguages=release['textLanguages']))
    for name in ('LICENSE','ATTRIBUTIONS.md','NOTO-LICENSE-OFL.txt','SOURCE.txt','UPDATE.md','CONTROLS_RU.md','CONTROLS_EN.md','CHANGELOG_RU.md','CHANGELOG_EN.md'):
        if (source/name).is_file():shutil.copy2(source/name,package/name)
    readme=f'''# Gwent Beta Classic {a.version} — версия 1.32 ({a.language.upper()})

Основа: проверенный снимок Next-Gen Stage {a.source_stage}, озвучка {a.language.upper()}, 13 языков текста.
Скрипты успешно проверены нативным компилятором игры 1.32: ошибок нет.
Обычные предупреждения EnableDebugOverlayFilter, EnableDebugPostProcess и
DebugSetEShowFlag встречаются и на чистой игре.

Установка: закройте игру, сохраните резервную копию сохранений, отключите старую
папку modBetaGwent0924 и старые тестовые сборки. Скопируйте папку Mods из архива
в корень игры. Одновременно должна быть включена только одна версия мода.
При наличии других скриптовых модов проверьте конфликты в Script Merger.
REDkit, Wwise и патчер аннотаций для игры не нужны.

Загрузка окон, ввод русского имени колоды,
сохранение/загрузка коллекции, завершение квестовой партии, эффекты и озвучка
нуждаются в игровом тесте. Форматы/CRC и компиляция проверены; прохождение партии
и воспроизведение звука пока не подтверждены.

Перенос следующих обновлений: docs/CLASSIC132_PORT_RU.md в исходном проекте.
'''
    (package/'README_RU.md').write_text(readme,'utf8')
    (package/'README_EN.md').write_text(f'''# Gwent Beta Classic {a.version} — Classic 1.32 ({a.language.upper()})

Voice: {a.language.upper()}. All 13 selectable text languages are included.
Built from the shared Stage {a.source_stage}; the native 1.32 script compiler passed.
Close the game, back up saves, disable modBetaGwent0924 and older Classic copies,
then copy Mods into the game directory. Install only one voice package at a time.
Check script conflicts with Script Merger when using other script mods.
Gameplay, audio playback and save compatibility require an in-game test.
''','utf8')
    prep=read(prepared/'preparation.json')
    report=dict(schema=1,version=version,sourceVersion=a.version,sourceStage=a.source_stage,gameVersion='1.32',language=a.language,voiceLanguage=a.language,textLanguages=release['textLanguages'],
        sharedScripts=prep['sourceScripts'],sharedUi=menu_report['frozenSources'],generators=generators,sourceManifestSha256=sha(source/'manifest.json'),
        nativeCompilationPassed=True,compilerResult=str(native_path),compilerResultSha256=sha(native_path),compilerWarnings=native['compilerFeedback']['warnings'],
        scripts=len(prep['outputScripts']),resources=len(resource_report['entries']),bundleVersion=3,metadataVersion=6,resourceVersion=163,
        soundCacheVersion=1,wwiseVersion=88,audioCodec=audio_report.get('audioCodec','pcm'),streamedMedia=sound_report['mediaCount'],guiLimitMiB=budget,
        nativeGameplayVerified=False,nativeAudioPlaybackVerified=False,installedGameModified=False)
    changes=dict(sharedScriptCount=len(prep['sourceScripts']),sharedUiCount=len(menu_report['frozenSources']))
    if a.previous:
        previous=read(a.previous)
        for name,key in [('scripts','sharedScripts'),('ui','sharedUi'),('adapters','generators')]:
            before=previous[key];after=report[key]
            changes[name]=dict(changed=[n for n in before.keys()&after.keys() if before[n]!=after[n]],added=sorted(after.keys()-before.keys()),removed=sorted(before.keys()-after.keys()))
    save(out/'source-changes.json',changes)
    report['files']=[dict(path=p.relative_to(package).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(package.rglob('*')) if p.is_file()]
    save(package/'manifest.json',report)
    suffix='' if a.release else '-test'+str(a.test_revision)
    archive=ROOT/'BetaGwent/release'/f'GwentBetaClassic-{a.version}-1.32-{a.language.upper()}{suffix}.zip'
    require(not archive.exists(),'Archive already exists; never overwrite a release')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in sorted(package.rglob('*')):
            if path.is_file():z.write(path,path.relative_to(package).as_posix())
    with zipfile.ZipFile(archive) as z:
        require(z.testzip() is None,'ZIP CRC failed')
        for item in report['files']:require(hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256'],'ZIP payload mismatch')
    result=dict(report,archive=str(archive),archiveBytes=archive.stat().st_size,archiveSha256=sha(archive),archiveVerified=True,createdUtc=datetime.now(timezone.utc).isoformat())
    archive.with_suffix('.zip.sha256').write_text(result['archiveSha256']+'  '+archive.name+'\n','ascii')
    save(out/'result.json',result);save(ROOT/f'docs/evidence/classic132-stage{a.source_stage}-{a.language}.json',result)
    print('Verified Classic '+a.language.upper()+' archive:',archive,flush=True)


if __name__=='__main__':main()
