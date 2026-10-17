"""Restore native depot GUIDs in the Classic v3 bundle TOC, payload unchanged."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import cook_guid_map,sha
from dependencies import read_dependency_cache

BASE=ROOT/'BetaGwent/build/classic081-guid-fix7'
SOURCE=ROOT/'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix6-AllLanguages.zip'
OLD_BUNDLE=ROOT/'BetaGwent/build/classic081-boot-fix4/resources-classic/blob0.bundle'
MOD='Mods/modBetaGwentClassic132/'
VERSION='0.8.1-classic-bundle-guids-fix7'


def tail_sha(path,offset):
    with path.open('rb') as f:
        f.seek(offset)
        return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    assert not BASE.exists()
    resources=BASE/'resources-classic';resources.mkdir(parents=True)
    guids=cook_guid_map(ROOT/'BetaGwent/build/release202/ru/cooked/cook.db')
    cache=ROOT/'BetaGwent/build/classic081-dependencies-fix6/dep.cache'
    registered=set(read_dependency_cache(cache.read_bytes())['guids'])
    with OLD_BUNDLE.open('rb') as f:
        header=f.read(32);size=struct.unpack_from('<I',header,16)[0];before=f.read(size)
    assert header[:8]==b'POTATO70' and struct.unpack_from('<H',header,20)[0]==3
    assert size%320==0
    after=bytearray(before);changed=[]
    for pos in range(0,size,320):
        name=before[pos:pos+256].split(b'\0')[0].decode('ascii').replace('\\','/')
        if name not in guids:continue
        assert before[pos+256:pos+272]==bytes(16) and guids[name] in registered
        after[pos+256:pos+272]=guids[name];changed.append(name)
    assert len(changed)==len(guids)==345
    for pos in range(0,size,320):
        assert after[pos:pos+256]==before[pos:pos+256]
        assert after[pos+272:pos+320]==before[pos+272:pos+320]
    candidate=resources/'blob0.bundle';shutil.copy2(OLD_BUNDLE,candidate)
    with candidate.open('r+b') as f:f.seek(32);f.write(after)
    assert candidate.stat().st_size==OLD_BUNDLE.stat().st_size
    assert tail_sha(candidate,32+size)==tail_sha(OLD_BUNDLE,32+size)
    report=dict(bundleVersion=3,resourceGuidsRestored=345,resourcePayloadsUnchanged=True,
                payloadSha256=tail_sha(candidate,32+size),tocOffsetsSizesCrcUnchanged=True,
                dependencyCacheGuidsMatched=True,bundleSha256=sha(candidate))
    readme='''Gwent Beta Classic 0.8.1 — Classic 1.32, fix7

Восстановлены GUID всех 345 CR2W-ресурсов в таблице Classic-bundle.
Предыдущий упаковщик записывал в эти 16-байтовые поля нули. Идентификаторы
взяты из зафиксированного cook.db и сверены с dep.cache fix6. GUID штатных
DeckBuilder и GwintGame совпадают с родными bundle установленной 1.32.
Содержимое ресурсов и смещения, размеры, CRC не менялись.

BundleGuidPatch ставится поверх установленного fix6: закройте игру,
удалите mod000BetaGwentClassic132Probe, если она осталась, и скопируйте Mods
из патча в корень игры с заменой файлов. Основной modBetaGwentClassic132
при установке патча НЕ удаляйте. Полный AllLanguages устанавливается отдельно:
прежнюю папку мода заменяют папкой Mods из полного архива.

Проверьте колоды → редактор → выход и возврат управления. Затем отдельно
NPC → выбор колоды → партия: при прошлой сборке из загрузки партии выхода
не было, в отличие от состояния с камерой при открытии редактора.
Работа fix7 в игре ещё не подтверждена. Скрипты, Flash-код, текстуры,
metadata fix5, dep.cache fix6, тексты и озвучка сохранены.
'''
    patch=ROOT/'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix7-BundleGuidPatch.zip'
    full=ROOT/'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix7-AllLanguages.zip'
    assert not patch.exists() and not full.exists()
    with zipfile.ZipFile(SOURCE) as source:
        info=json.loads(source.read(MOD+'info.json'));info.update(version=VERSION,nativeBundleGuidsIncluded=True)
        info_bytes=json.dumps(info,indent=2).encode('utf8')
        (BASE/'info.json').write_bytes(info_bytes)
        for name in ('metadata.store','dep.cache'):(resources/name).write_bytes(source.read(MOD+'content/'+name))
        assert (resources/'dep.cache').read_bytes()==cache.read_bytes()
        assert source.getinfo(MOD+'content/blob0.bundle').file_size==OLD_BUNDLE.stat().st_size
        with source.open(MOD+'content/blob0.bundle') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==sha(OLD_BUNDLE)
        with zipfile.ZipFile(patch,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as target:
            for name in ('blob0.bundle','metadata.store','dep.cache'):target.write(resources/name,MOD+'content/'+name)
            target.writestr(MOD+'info.json',info_bytes)
            target.writestr('README_RU.txt',readme.encode('utf-8-sig'))
        expected={}
        with zipfile.ZipFile(full,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as target:
            for entry in source.infolist():
                if entry.filename==MOD+'content/blob0.bundle':
                    target.write(candidate,entry.filename);expected[entry.filename]=sha(candidate);continue
                data=source.read(entry)
                if entry.filename==MOD+'info.json':data=info_bytes
                elif entry.filename=='README_RU.md':data=readme.encode('utf-8-sig')
                elif entry.filename=='BetaGwentDocs/BuildInfo.json':
                    build=json.loads(data);build.update(version=VERSION,nativeBundleGuidsIncluded=True,nativeGameplayVerified=False)
                    data=json.dumps(build,indent=2).encode('utf8')
                target.writestr(entry.filename,data);expected[entry.filename]=hashlib.sha256(data).hexdigest()
            target.writestr('BetaGwentDocs/ClassicBundleGuidFix.json',json.dumps(report,indent=2))
    for archive in (patch,full):
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            if archive==full:
                for path,digest in expected.items():
                    with z.open(path) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==digest
            with z.open(MOD+'content/blob0.bundle') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==sha(candidate)
        archive.with_suffix('.zip.sha256').write_text(sha(archive)+'  '+archive.name+'\n','ascii')
    report.update(version=VERSION,sourceArchiveSha256=sha(SOURCE),
                  patch=dict(path=str(patch),bytes=patch.stat().st_size,sha256=sha(patch)),
                  full=dict(path=str(full),bytes=full.stat().st_size,sha256=sha(full)),
                  metadataDependenciesScriptsAudioUnchanged=True,gameplayVerified=False)
    (BASE/'verification.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
