"""Load the exact known-good native movie through the mod's custom path."""
from pathlib import Path
import json
import struct
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/classic132'),str(ROOT/'tools/ui')]
from formats import Resource,bundle_entries,header_crc,write_bundle,sha,cook_guid_map
from cr2w_gui_write109 import Res
from build_classic_probe import minimal_metadata
from package_classic_metadata_fix import repair

BASE=ROOT/'BetaGwent/build/classic081-native-alias-control'
CONTROL=ROOT/'BetaGwent/build/classic081-native-control'
GAME=Path('D:/GOG Galaxy/Games/The Witcher 3 Wild Hunt')
MENU='gameplay/gui_new/guirsrc/r4deck_builder.menu'
CUSTOM='betagwent/betagwent_decks.redswf'
STOCK=r'gameplay\gui_new\swf\gwint\deck_builder.redswf'


def main():
    assert not BASE.exists()
    BASE.mkdir()
    good=Resource((CONTROL/'r4deck_builder.menu').read_bytes())
    raw=bytearray(good.data)
    struct.pack_into('<I',raw,4,164);struct.pack_into('<I',raw,32,header_crc(raw))
    edited=Res(raw)
    assert len(edited.imports)==1 and good.string(good.imports[0][0])==STOCK
    edited.imports[0][0]=edited.add_string(CUSTOM.replace('/','\\'))
    result=Resource(edited.build()).classic()
    checked=Resource(result)
    assert checked.chunks==good.chunks and checked.classes==good.classes
    assert checked.string(checked.imports[0][0])==CUSTOM.replace('/','\\')
    assert checked.imports[0][1:]==good.imports[0][1:]
    native=dict(bundle_entries(GAME/'content/content0/bundles/r4gui.bundle',lambda n:n==STOCK))
    assert len(native)==1
    movie=BASE/'betagwent_decks.redswf';movie.write_bytes(next(iter(native.values())))
    assert sha(movie)==json.loads((CONTROL/'verification.json').read_text('utf8'))['stockMovieSha256']
    menu=BASE/'r4deck_builder.menu';menu.write_bytes(result)
    package=BASE/'package';content=package/'Mods/mod000BetaGwentClassic132Probe/content'
    content.mkdir(parents=True)
    write_bundle({MENU:menu,CUSTOM:movie},content/'blob0.bundle',guids=cook_guid_map(ROOT/'BetaGwent/build/release202/ru/cooked/cook.db'))
    minimal_metadata(ROOT/'BetaGwent/build/classic081-metadata-fix5/metadata.store',
                     content/'blob0.bundle',content/'metadata.store')
    data,report=repair((content/'metadata.store').read_bytes())
    assert report['fixedNegativeFileIds']==0 and report['hashRecords']==2
    assert data==(content/'metadata.store').read_bytes()
    (content.parent/'info.json').write_text(json.dumps(dict(
        name='Classic native movie through custom depot path',
        version='native-custom-path-control1',gameVersion='1.32'),indent=2),'utf8')
    (package/'README_RU.txt').write_text('''Контроль пути загрузки, не исправление.

Закройте игру. Скопируйте Mods поверх существующей диагностической папки
mod000BetaGwentClassic132Probe с заменой файлов. Основной fix5 оставьте.
Откройте обычные колоды. Родной Flash полностью совпадает с предыдущим
успешным контролем; изменён только путь ресурса на путь нашего мода.
Ожидаются короткое открытие штатного меню и автоматическое закрытие,
MENU_CONFIG_BEGIN / BOARD_MISSING_FLASH_FUNCTION / BOARD_CLOSED в логе.
Закройте игру и сообщите результат. После проверки удалите только накладку.
''','utf-8-sig')
    archive=ROOT/'BetaGwent/release/GwentBetaClassic-1.32-NativeMenu-CustomPath-Control.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in package.rglob('*'):
            if p.is_file():z.write(p,p.relative_to(package).as_posix())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    report.update(archive=str(archive),bytes=archive.stat().st_size,sha256=sha(archive),
                  nativeMovieSha256=sha(movie),nativeMovieByteIdentical=True,
                  nativeMenuDefinitionChunksIdentical=True,onlyMenuImportPathChanged=True,
                  customActionScriptIncluded=False,gameplayVerified=False)
    (BASE/'verification.json').write_text(json.dumps(report,indent=2),'utf8')
    archive.with_suffix('.zip.sha256').write_text(sha(archive)+'  '+archive.name+'\n','ascii')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
