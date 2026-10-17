"""Restore the omitted compatible dependency index to Classic fix5."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/classic132'))
from dependencies import read_dependency_cache,verify_cache_paths,copy_dependency_cache
from formats import bundle_entries,sha

BASE=ROOT/'BetaGwent/build/classic081-dependencies-fix6'
SOURCE=ROOT/'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix5-AllLanguages.zip'
FROZEN=ROOT/'BetaGwent/build/release202/ru/package'
CACHE=FROZEN/'Mods/modBetaGwent0924/content/dep.cache'
MOD='Mods/modBetaGwentClassic132/'
VERSION='0.8.1-classic-dependencies-fix6'


def main():
    assert not BASE.exists()
    BASE.mkdir()
    manifest=json.loads((FROZEN/'manifest.json').read_text('utf-8-sig'))
    record=next(x for x in manifest['files'] if x['path'].endswith('/dep.cache'))
    assert sha(CACHE)==record['sha256']
    parsed=read_dependency_cache(CACHE.read_bytes())
    native=read_dependency_cache(Path('D:/GOG Galaxy/Games/The Witcher 3 Wild Hunt/content/content0/dep.cache').read_bytes())
    assert parsed['guids'][0]==native['guids'][0]
    resources=[n for n,d in bundle_entries(ROOT/'BetaGwent/build/classic081-boot-fix4/resources-classic/blob0.bundle')
               if d[:4]==b'CR2W']
    report=verify_cache_paths(CACHE.read_bytes(),FROZEN.parent/'cooked/cook.db',resources)
    assert report['verifiedResourcePaths']==345
    report.update(copy_dependency_cache(CACHE,BASE/'dep.cache'))
    patch=ROOT/'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix6-DependencyPatch.zip'
    full=ROOT/'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix6-AllLanguages.zip'
    assert not patch.exists() and not full.exists()
    readme='''Gwent Beta Classic 0.8.1 — Classic 1.32, fix6

Восстановлен пропущенный файл content/dep.cache: индекс GUID всех 345
CR2W-ресурсов мода. Этот кэш присутствовал в рабочем пакете Next-Gen,
но упаковщики Classic копировали только bundle/metadata и пропускали его.
Проверен формат SPED v2, совпадающий с установленной 1.32, и наличие всех
345 ресурсов, включая четыре Flash-меню, их .menu и guiconfig.

Малый DependencyPatch устанавливается поверх fix5:
1. Закройте игру.
2. Удалите диагностическую папку Mods/mod000BetaGwentClassic132Probe.
3. Скопируйте Mods из малого архива в корень игры с заменой info.json.
   Появится content/dep.cache. Основной modBetaGwentClassic132 НЕ удаляйте.

Полный AllLanguages устанавливается самостоятельно: удалите прежний
modBetaGwentClassic132 и диагностическую папку, затем скопируйте Mods
из полного архива в корень игры 1.32.

Проверка: открытие колод → редактор → выход с возвратом управления;
затем разговор с NPC → гвинт → экран выбора колоды → партия.
При зависании сообщите, на каком этапе оно произошло, и закройте игру:
scriptslog.txt будет прочитан локально. Исправление ещё требует проверки
пользователем. Bundle, metadata fix5, код меню, скрипты и аудио не менялись.
'''
    with zipfile.ZipFile(SOURCE) as source:
        assert MOD+'content/dep.cache' not in source.namelist()
        info=json.loads(source.read(MOD+'info.json'));info['version']=VERSION
        info['dependencyCacheIncluded']=True
        replacement={MOD+'info.json':json.dumps(info,indent=2).encode('utf8'),
                     MOD+'content/dep.cache':CACHE.read_bytes()}
        with zipfile.ZipFile(patch,'x',zipfile.ZIP_DEFLATED) as target:
            for name,data in replacement.items():target.writestr(name,data)
            target.writestr('README_RU.txt',readme.encode('utf-8-sig'))
        expected={}
        with zipfile.ZipFile(full,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as target:
            for entry in source.infolist():
                data=replacement.get(entry.filename)
                if data is None:data=source.read(entry)
                if entry.filename=='README_RU.md':data=readme.encode('utf-8-sig')
                if entry.filename=='BetaGwentDocs/BuildInfo.json':
                    build=json.loads(data);build.update(version=VERSION,dependencyCacheIncluded=True,nativeGameplayVerified=False)
                    data=json.dumps(build,indent=2).encode('utf8')
                target.writestr(entry.filename,data);expected[entry.filename]=hashlib.sha256(data).hexdigest()
            target.writestr(MOD+'content/dep.cache',CACHE.read_bytes())
            target.writestr('BetaGwentDocs/ClassicDependenciesFix.json',json.dumps(report,indent=2))
    for archive in (patch,full):
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            assert z.read(MOD+'content/dep.cache')==CACHE.read_bytes()
            if archive==full:
                for path,digest in expected.items():
                    with z.open(path) as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==digest
        archive.with_suffix('.zip.sha256').write_text(sha(archive)+'  '+archive.name+'\n','ascii')
    report.update(version=VERSION,sourceArchiveSha256=sha(SOURCE),
                  classicNativeCacheGuids=len(native['guids']),
                  patch=dict(path=str(patch),bytes=patch.stat().st_size,sha256=sha(patch)),
                  full=dict(path=str(full),bytes=full.stat().st_size,sha256=sha(full)),
                  bundleMetadataScriptsAudioUnchanged=True,gameplayVerified=False)
    (BASE/'verification.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
