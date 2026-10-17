"""Control test: original 1.32 SWF, custom WS class; no compiled AS replacement."""
from pathlib import Path
import hashlib
import json
import struct
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/classic132'),str(ROOT/'tools/ui')]
from formats import Resource,bundle_entries,header_crc,write_bundle,sha,cook_guid_map
from cr2w_gui_write109 import Res,prop
from build_classic_probe import minimal_metadata
from package_classic_metadata_fix import repair

BASE=ROOT/'BetaGwent/build/classic081-native-control'
GAME=Path('D:/GOG Galaxy/Games/The Witcher 3 Wild Hunt')
MENU='gameplay/gui_new/guirsrc/r4deck_builder.menu'
STOCK_MOVIE=r'gameplay\gui_new\swf\gwint\deck_builder.redswf'


def main():
    assert not BASE.exists()
    BASE.mkdir()
    originals=dict(bundle_entries(GAME/'content/content0/bundles/blob.bundle',
                                  lambda n:n.replace('\\','/')==MENU))
    assert len(originals)==1
    source=next(iter(originals.values()))
    (BASE/'native-original.menu').write_bytes(source)
    parseable=bytearray(source)
    struct.pack_into('<I',parseable,4,163)
    struct.pack_into('<I',parseable,32,header_crc(parseable))
    original=Resource(parseable)
    assert original.string(original.imports[0][0])==STOCK_MOVIE
    raw=bytearray(parseable)
    struct.pack_into('<I',raw,4,164);struct.pack_into('<I',raw,32,header_crc(raw))
    result=Res(raw)
    menu_class=result.add_name('CR4BetaGwentBoardMenu')
    old_props,end=original.properties(original.chunks[0])
    assert end==len(original.chunks[0])
    root=bytearray(b'\0')
    for name,kind,value in old_props:
        if original.names[name]=='menuClass':value=struct.pack('<H',menu_class)
        root+=prop(result,original.names[name],original.names[kind],value)
    root+=b'\0\0'
    result.payloads[0]=bytes(root)
    output=Resource(result.build()).classic()
    checked=Resource(output)
    assert checked.imports==original.imports
    assert checked.chunks[1:]==original.chunks[1:]
    expected_props=[(original.names[n],original.names[t],v)
                    for n,t,v in old_props if original.names[n]!='menuClass']
    new_props,_=checked.properties(checked.chunks[0])
    assert [(checked.names[n],checked.names[t],v) for n,t,v in new_props
            if checked.names[n]!='menuClass']==expected_props
    assert checked.string(checked.imports[0][0])==STOCK_MOVIE
    movie=bundle_entries(GAME/'content/content0/bundles/r4gui.bundle',lambda n:n==STOCK_MOVIE)
    movie_data=next(movie)[1]
    stock_movie_sha=hashlib.sha256(movie_data).hexdigest()
    assert next(movie,None) is None
    menu=BASE/'r4deck_builder.menu';menu.write_bytes(output)
    package=BASE/'package'
    content=package/'Mods/mod000BetaGwentClassic132Probe/content'
    content.mkdir(parents=True)
    write_bundle({MENU:menu},content/'blob0.bundle',guids=cook_guid_map(ROOT/'BetaGwent/build/release202/ru/cooked/cook.db'))
    minimal_metadata(ROOT/'BetaGwent/build/classic081-metadata-fix5/metadata.store',
                     content/'blob0.bundle',content/'metadata.store')
    metadata,report=repair((content/'metadata.store').read_bytes())
    assert report['fixedNegativeFileIds']==0 and report['hashRecords']==1
    assert metadata==(content/'metadata.store').read_bytes()
    (content.parent/'info.json').write_text(json.dumps(dict(
        name='Classic 1.32 original SWF control',version='native-control1',gameVersion='1.32'),indent=2),'utf8')
    readme='''Контроль загрузки родного Flash-меню 1.32; не исправление и не игровой пакет.

Закройте игру. Основной modBetaGwentClassic132 (fix5) оставьте на месте.
Скопируйте Mods из архива в корень игры с заменой файлов существующей
mod000BetaGwentClassic132Probe. Здесь подменяется только .menu: Flash берётся
неизменённым из установленной 1.32. Нашего ActionScript в этом архиве нет.

Загрузите сохранение и один раз откройте обычные колоды. Ожидается краткий
показ родного меню, затем его закрытие: наш WS-мост намеренно проверяет
функции, которых в родном Flash нет. В логе ожидаются MENU_CONFIG_BEGIN,
BOARD_MISSING_FLASH_FUNCTION и BOARD_CLOSED. Этот тест нужен, даже если окно
не успеет отрисоваться: логи подтверждают запуск родного movie.

Не начинайте партию. После проверки закройте игру и сообщите результат;
scriptslog.txt будет прочитан локально. Затем удалите только диагностическую
папку mod000BetaGwentClassic132Probe. Основной мод оставьте.
'''
    (package/'README_RU.txt').write_text(readme,'utf-8-sig')
    archive=ROOT/'BetaGwent/release/GwentBetaClassic-1.32-NativeMenu-Control.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for path in package.rglob('*'):
            if path.is_file():z.write(path,path.relative_to(package).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert sorted(p for p in z.namelist() if p.endswith('.bundle'))==[
            'Mods/mod000BetaGwentClassic132Probe/content/blob0.bundle']
    report.update(archive=str(archive),bytes=archive.stat().st_size,sha256=sha(archive),
                  stockMoviePath=STOCK_MOVIE,stockMovieSha256=stock_movie_sha,
                  stockMovieUnchanged=True,customActionScriptIncluded=False,
                  menuDefinitionPropertiesPreserved=True,gameplayVerified=False)
    (BASE/'verification.json').write_text(json.dumps(report,indent=2),'utf8')
    archive.with_suffix('.zip.sha256').write_text(sha(archive)+'  '+archive.name+'\n','ascii')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
