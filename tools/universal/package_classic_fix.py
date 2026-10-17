"""Package a Classic-only resource fix without changing scripts or audio."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import Resource, bundle_entries, sha, require

MOD='Mods/modBetaGwentClassic132/'


def verify_textures(previous, current):
    before=dict(bundle_entries(previous))
    checked=changed=0
    for name,data in bundle_entries(current):
        old=before.pop(name)
        if not name.endswith('.redswf'):
            continue
        original,result=Resource(old),Resource(data)
        require(original.classes==result.classes,'GUI chunk identities changed')
        # Native movie/ABC, properties, fonts and symbol bindings are identical.
        require(original.chunks[0]==result.chunks[0],'Native movie changed')
        for cls,record,old_chunk,new_chunk in zip(original.classes,original.records,original.chunks,result.chunks):
            if cls!='CSwfTexture':continue
            _,old_pos=original.properties(old_chunk)
            _,new_pos=result.properties(new_chunk)
            require(old_chunk[:old_pos]==new_chunk[:new_pos],'Texture properties changed')
            a,b=old_chunk[old_pos:],new_chunk[new_pos:]
            if record[1]==0:
                require(a[:24]==b[:24] and b[24:28]==struct.pack('<HH',16,0),'Cooked texture header')
                require(a[24:-4]==b[28:],'Texture pixels changed')
                changed+=1
            else:require(a==b,'Existing cooked texture changed')
            checked+=1
        require(all(r[1]==8192 for r in result.records),'Uncooked GUI export remains')
    require(not before,'Bundle resource set changed')
    return dict(textureChunksChecked=checked,textureChunksCooked=changed,pixelBytesPreserved=True,
                nativeMoviesUnchanged=True,gameplayVerified=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-archive',type=Path,required=True)
    parser.add_argument('--previous-resources',type=Path,required=True)
    parser.add_argument('--resources',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    require(not args.out.exists(),'Keep previous packages immutable')
    verification=verify_textures(args.previous_resources/'blob0.bundle',args.resources/'blob0.bundle')
    require(verification['textureChunksCooked']>0,'No authoring GUI textures were converted')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    version='0.8.1-classic-fix3'
    readme='''# Gwent Beta Classic 0.8.1 — Classic 1.32, fix3

Исправление подготовки ресурсов меню для старого движка. Авторские текстуры
REDkit преобразованы в формат cooked, используемый штатными меню 1.32.
Пиксели, размеры, код меню, правила, скрипты и озвучка сохранены из menu-fix2.
В пакете все 13 языков текста и пять озвучек; выбор — двумя кнопками в моде.

Установка: закройте игру, удалите старую папку modBetaGwentClassic132 из Mods,
затем скопируйте папку Mods из этого архива в корень The Witcher 3 1.32.
Не смешивайте файлы старой и новой сборки. Оставьте только одну версию мода.
При других скриптовых модах обновите объединение в Script Merger.

Это кандидат для проверки исправления; открытие меню в игре ещё не подтверждено.
Первый тест: загрузить сохранение → открыть колоды → открыть редактор → выйти
и проверить возврат управления. Затем проверить NPC → колоды → партия → выход.
Перед проверкой сохраните копию своих сохранений.
Для лога используйте -debugscripts; после проверки сохраните scriptslog.txt
из Documents/The Witcher 3 до следующего запуска игры.
'''
    expected={}
    with zipfile.ZipFile(args.source_archive) as source,zipfile.ZipFile(args.out,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as target:
        for entry in source.infolist():
            require(not entry.is_dir(),'Unexpected directory entry')
            path=entry.filename
            if path in (MOD+'content/blob0.bundle',MOD+'content/metadata.store'):
                replacement=args.resources/Path(path).name
                target.write(replacement,path);expected[path]=sha(replacement)
                continue
            data=source.read(entry)
            if path==MOD+'info.json':
                info=json.loads(data);info['version']=version;data=json.dumps(info,indent=2).encode('utf8')
            elif path=='BetaGwentDocs/BuildInfo.json':
                info=json.loads(data);info.update(version=version,cookedGuiTextures=True,nativeGameplayVerified=False)
                data=json.dumps(info,indent=2).encode('utf8')
            elif path=='README_RU.md':data=readme.encode('utf-8-sig')
            target.writestr(path,data);expected[path]=hashlib.sha256(data).hexdigest()
        target.writestr('BetaGwentDocs/ClassicTextureFix.json',json.dumps(verification,indent=2))
    with zipfile.ZipFile(args.out) as archive:
        for path,digest in expected.items():
            with archive.open(path) as stream:
                require(hashlib.file_digest(stream,'sha256').hexdigest()==digest,'Archive file changed: '+path)
        require(archive.testzip() is None,'ZIP CRC verification failed')
    verification.update(archive=str(args.out.resolve()),sha256=sha(args.out),bytes=args.out.stat().st_size,
                        verifiedFiles=len(expected),scriptsAndAudioUnchanged=True)
    args.out.with_suffix('.zip.sha256').write_text(verification['sha256']+'  '+args.out.name+'\n','ascii')
    args.out.with_suffix('.verification.json').write_text(json.dumps(verification,indent=2)+'\n','utf8')
    print(json.dumps(verification,indent=2),flush=True)


if __name__=='__main__':main()
