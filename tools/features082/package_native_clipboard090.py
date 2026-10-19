"""Bundle reversible UI/native clipboard probes for Classic and Next-Gen."""
from pathlib import Path
import sys,json,struct,hashlib,shutil,zipfile,zlib
ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'BetaGwent/build/release090-native-clipboard';NATIVE=ROOT/'BetaGwent/build/clipboard090-r4'
sys.path[:0]=[str(ROOT/'tools/classic132'),str(ROOT/'tools/ui'),str(ROOT/'tools/universal'),str(Path(__file__).parent)]
from formats import bundle_entries,sha
from build_resources import strip_menu_authoring
from package_cleaner082 import metadata

def main():
    package=BUILD/'package';assert not package.exists();package.mkdir()
    shutil.copytree(BUILD/'probe/package/Mods',package/'Classic132/Mods')
    info=package/'Classic132/Mods/mod000BetaGwentClassic132LocaleFix090/info.json'
    data=json.loads(info.read_text());data.update(name='Classic native Windows clipboard UI',nativeClipboardRequired=True);info.write_text(json.dumps(data,indent=2),'utf8')
    mod=package/'NextGen/Mods/mod000BetaGwentNativeClipboard090';content=mod/'content';content.mkdir(parents=True)
    source=ROOT/'BetaGwent/build/release082-polish2/nextgen/package/Mods/modBetaGwent0924/content'
    report=json.loads((BUILD/'nextgen/menus/menus.json').read_text('utf8'))
    menus={Path(m['path']).name:Path(m['path']) for m in report['menus']};files={}
    with (source/'blob0.bundle').open('rb') as f:
        header=bytearray(f.read(32));toc=f.read(struct.unpack_from('<I',header,16)[0])
    old={row[:256].split(b'\0')[0].decode('ascii').replace('\\','/'):row for row in [toc[i:i+304] for i in range(0,len(toc),304)]}
    for name in old:
        if Path(name).name not in menus:continue
        raw=strip_menu_authoring(menus[Path(name).name].read_bytes());assert len(raw)<63*1024**2
        p=BUILD/'nextgen/probe-resources'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);files[name]=p
    assert len(files)==4
    table=bytearray();positions={};offset=(32+304*len(files)+4095)&~4095
    for name,p in files.items():
        row=bytearray(old[name]);size=p.stat().st_size;struct.pack_into('<QIIII',row,272,offset,size,size,zlib.crc32(p.read_bytes()),0)
        table+=row;positions[name]=offset;offset=(offset+size+4095)&~4095
    struct.pack_into('<I',header,8,max(positions[n]+p.stat().st_size for n,p in files.items()));struct.pack_into('<I',header,16,len(table))
    bundle=content/'blob0.bundle'
    with bundle.open('wb') as f:
        f.write(header);f.write(table)
        for name,p in files.items():
            f.write(bytes(positions[name]-f.tell()))
            with p.open('rb') as stream:shutil.copyfileobj(stream,f)
    assert {n.replace('\\','/'):hashlib.sha256(raw).hexdigest() for n,raw in bundle_entries(bundle)}=={n:sha(p) for n,p in files.items()}
    (content/'metadata.store').write_bytes(metadata(files,bundle,False));shutil.copy2(source/'dep.cache',content/'dep.cache')
    (mod/'info.json').write_text(json.dumps(dict(version='0.9.0',candidate=True,name='Next-Gen native Windows clipboard UI',nativeClipboardRequired=True,mainModRequired=True,gameplayVerified=False),indent=2),'utf8')
    for path in ['Classic132/bin/x64','NextGen/bin/x64','NextGen/bin/x64_dx12']:
        binfolder=package/path;(binfolder/'plugins').mkdir(parents=True)
        shutil.copy2(NATIVE/'dinput8.dll',binfolder/'dinput8.dll');shutil.copy2(NATIVE/'GwentBetaClipboard.asi',binfolder/'plugins/GwentBetaClipboard.asi')
    for lang,text in {
      'RU':'''# Проверка нативного копирования 0.9.0

Выбрать папку Classic132 для 1.32 или NextGen для 5.01 и скопировать её
содержимое в каталог соответствующей игры. Основной мод оставить установленным.
Все файлы bin обязательны для кнопки копирования; -debugscripts и помощники
не нужны. Для Classic обновляется прежняя проверочная накладка с именем LocaleFix.

Если уже есть dinput8.dll от другого мода, НЕ заменять его: использовать его
совместимый ASI-загрузчик для plugins/GwentBetaClipboard.asi. Поставляемый
dinput8.dll только передаёт DirectInput штатной DLL Windows и загружает этот
единственный модуль. Другие плагины он не загружает.

Модуль распознаёт структуру GFx в EXE, связывает текстовый callback с Windows
и возвращает реальный успех/отказ setData. Обрабатываются только валидные BG1
на 25–40 карт. Прочий текст и ввод остаются в прежнем обработчике. Нет слежения
за буфером, фоновых программ, логов с кодами, изменений EXE на диске или сейвов.

Проверить отдельно в 1.32 и 5.01: открыть экспорт, нажать Копировать,
переключиться в текстовое приложение и вставить Ctrl+V. Совпадение картинки
и кода проверить полностью. Закрыть/открыть редактор и проверить NPC-партию.
49 нативных и 38 проверок интерфейса прошли. Проверка внутри игр ещё требуется.

Для отката удалить только установленные этой проверкой диагностические Mods,
plugins/GwentBetaClipboard.asi и поставленный с ней dinput8.dll; чужой загрузчик
не удалять. Перезапуск обязателен: callback закреплён до завершения процесса.
''',
      'EN':'''# Native clipboard test 0.9.0

Use Classic132 for 1.32 or NextGen for 5.01. Copy that folder's contents into
the matching game directory, keeping the main mod installed. The bin files
are required for the Copy button. No helper or -debugscripts is needed.

Do not overwrite another mod's dinput8.dll. Use its compatible ASI loader for
plugins/GwentBetaClipboard.asi instead. Our optional bootstrap forwards the
Windows DirectInput functions and loads this single plugin.

The module recognizes the GFx clipboard structure, connects its text callback
to Windows and returns the actual setData result. Only valid BG1 codes with
25–40 cards are copied. It does not poll the clipboard, launch background
programs, log deck codes, modify saves or patch the executable on disk.

Test separately in 1.32 and 5.01: Export, Copy, switch to a text application,
Ctrl+V, compare the entire code. Reopen the editor and test an NPC match.
49 native and 38 UI checks passed; actual in-game copying still needs testing.

To revert, remove this test's diagnostic mod folder, the ASI plugin and only
the dinput8.dll supplied here. Preserve other loaders. Restart the game.
'''
    }.items():(package/f'README_{lang}.md').write_text(text,'utf8')
    files=[dict(path=p.relative_to(package).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(package.rglob('*')) if p.is_file()]
    manifest=dict(version='0.9.0',candidate=True,requiredGameVersions=['1.32','5.01'],nativeChecks=49,uiChecks=38,gameCopyVerified=False,files=files)
    (package/'manifest.json').write_text(json.dumps(manifest,indent=2),'utf8')
    archive=ROOT/'BetaGwent/release/GwentBetaClassic-0.9.0-NativeClipboard-Test.zip';assert not archive.exists()
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(package.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(package).as_posix())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    archive.with_suffix('.zip.sha256').write_text(sha(archive)+'  '+archive.name+'\n','ascii')
    (BUILD/'package-verification.json').write_text(json.dumps(dict(archive=str(archive),bytes=archive.stat().st_size,sha256=sha(archive),**manifest),indent=2),'utf8')
    print(json.dumps(dict(archive=str(archive),bytes=archive.stat().st_size)))

if __name__=='__main__':main()
