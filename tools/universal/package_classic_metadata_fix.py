"""Repair Classic metadata file IDs and package fix5; no game launch/install."""
from pathlib import Path
import hashlib
import json
import struct
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import classic_metadata_hash_rows,fnv64,sha
from build_resources import read_vlq

BASE=ROOT/'BetaGwent/build/classic081-metadata-fix5'
MOD='Mods/modBetaGwentClassic132/'
SOURCE=ROOT/'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix4-AllLanguages.zip'
VERSION='0.8.1-classic-metadata-fix5'


def repair(data):
    assert data[:4]==b'\x03VTM' and struct.unpack_from('<I',data,4)[0]==6
    size,pos=read_vlq(data,16);strings=data[pos:pos+size];pos+=size;arrays=[]
    for width in (32,20,24,4,8,12,16):
        count,pos=read_vlq(data,pos)
        arrays.append([data[p:p+width] for p in range(pos,pos+count*width,width)])
        if width==16:hash_start=pos
        pos+=count*width
    assert pos==len(data)
    hashes=classic_metadata_hash_rows(arrays[6],len(arrays[0]))
    output=data[:hash_start]+b''.join(hashes)
    fixed=sum(a!=b for a,b in zip(arrays[6],hashes))
    assert len(output)==len(data) and output[:hash_start]==data[:hash_start]
    ids=set()
    for old,row in zip(arrays[6],hashes):
        h,fid=struct.unpack('<Qq',row);ids.add(fid)
        off=struct.unpack_from('<I',arrays[0][fid])[0]
        path=strings[off:strings.index(0,off)]
        assert h==fnv64(path) and row[:12]==old[:12]
        assert 0<fid<len(arrays[0])
    assert len(ids)==len(hashes)==len(arrays[0])-1
    return output,dict(hashRecords=len(hashes),fixedNegativeFileIds=fixed,
                       pathHashesPreserved=True,recordOrderPreserved=True,
                       positiveInt64FileIds=True,bundleOffsetsUnchanged=True)


def main():
    assert not BASE.exists(),'Keep prior candidates immutable'
    BASE.mkdir(parents=True)
    patch=ROOT/'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix5-MetadataPatch.zip'
    full=ROOT/'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix5-AllLanguages.zip'
    assert not patch.exists() and not full.exists()
    readme='''Gwent Beta Classic 0.8.1 — Classic 1.32, fix5

Исправлена таблица metadata.store: индексы ресурсов записаны положительными
64-битными числами, как в штатной metadata Classic. В fix4 у 351 из 352
ресурсов верхние 32 бита индекса равнялись FFFFFFFF, что давало отрицательный
int64. Среди них меню DeckBuilder и betagwent_decks.redswf.

Малый архив MetadataPatch применяется поверх установленного fix4:
1. Закройте игру.
2. Удалите диагностическую папку Mods/mod000BetaGwentClassic132Probe.
3. Скопируйте Mods из малого архива в корень игры с заменой двух файлов
   в modBetaGwentClassic132: info.json и content/metadata.store.
   Основную папку modBetaGwentClassic132 при установке малого патча НЕ удаляйте.

Полный архив AllLanguages устанавливается самостоятельно: удалите прежний
modBetaGwentClassic132 и диагностическую папку, затем скопируйте Mods из
полного архива в корень игры 1.32.

Проверка: загрузить сохранение → открыть колоды → редактор → выход и возврат
управления. Код меню, скрипты, карты, текстуры и аудио побайтово сохранены
из fix4. Работоспособность в игре пока не подтверждена пользователем.
'''
    with zipfile.ZipFile(SOURCE) as source:
        metadata,report=repair(source.read(MOD+'content/metadata.store'))
        assert report['fixedNegativeFileIds']==351
        info=json.loads(source.read(MOD+'info.json'));info['version']=VERSION
        replacements={MOD+'content/metadata.store':metadata,
                      MOD+'info.json':json.dumps(info,indent=2).encode('utf8')}
        (BASE/'metadata.store').write_bytes(metadata)
        (BASE/'README_RU.txt').write_text(readme,'utf-8-sig')
        with zipfile.ZipFile(patch,'x',zipfile.ZIP_DEFLATED) as target:
            for path,data in replacements.items():target.writestr(path,data)
            target.writestr('README_RU.txt',readme.encode('utf-8-sig'))
        expected={}
        with zipfile.ZipFile(full,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as target:
            for entry in source.infolist():
                assert not entry.is_dir()
                data=replacements.get(entry.filename)
                if data is None:data=source.read(entry)
                if entry.filename=='README_RU.md':data=readme.encode('utf-8-sig')
                if entry.filename=='BetaGwentDocs/BuildInfo.json':
                    build=json.loads(data);build.update(version=VERSION,classicHashFileIdsValidated=True,nativeGameplayVerified=False)
                    data=json.dumps(build,indent=2).encode('utf8')
                target.writestr(entry.filename,data)
                expected[entry.filename]=hashlib.sha256(data).hexdigest()
            target.writestr('BetaGwentDocs/ClassicMetadataFix.json',json.dumps(report,indent=2))
    for archive in (patch,full):
        with zipfile.ZipFile(archive) as packaged:
            assert packaged.testzip() is None
            if archive==full:
                for path,digest in expected.items():
                    with packaged.open(path) as stream:
                        assert hashlib.file_digest(stream,'sha256').hexdigest()==digest
            assert packaged.read(MOD+'content/metadata.store')==metadata
        archive.with_suffix('.zip.sha256').write_text(sha(archive)+'  '+archive.name+'\n','ascii')
    report.update(version=VERSION,sourceArchiveSha256=sha(SOURCE),
                  patch=dict(path=str(patch),bytes=patch.stat().st_size,sha256=sha(patch)),
                  full=dict(path=str(full),bytes=full.stat().st_size,sha256=sha(full)),
                  bundleScriptsAudioUnchanged=True,gameplayVerified=False)
    (BASE/'verification.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
