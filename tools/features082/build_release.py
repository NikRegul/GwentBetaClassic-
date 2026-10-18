"""Package both 0.8.2 RC platforms, preserving accepted art/audio payloads."""
from pathlib import Path
import hashlib, json, shutil, struct, sys, zipfile, zlib
ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'BetaGwent/build/release082-rc1'
VERSION='0.8.2-rc1'
CLASSIC_COMPILE=ROOT/'BetaGwent/build/universal081/classic-runtime/runs/release082-rc1-clean-cache/result.json'
sys.path[:0]=[str(ROOT/'tools/classic132'),str(ROOT/'tools/ui'),str(ROOT/'tools/universal')]
from formats import bundle_entries, sha, fnv64, require
from build_resources import read_vlq, vlq, strip_menu_authoring

def redux():
    return {p.relative_to(BUILD/'redux').as_posix():p for p in (BUILD/'redux/gameplay').rglob('*.xml')}

def extra_resources(platform):
    folder=BUILD/platform/'extra-resources'
    return {p.relative_to(folder).as_posix():p for p in folder.rglob('*') if p.is_file()} if folder.exists() else {}

def nextgen_metadata(source,bundle,positions,files,toc_size):
    require(source[:8]==b'\x03VTM\x07\0\0\0','Next-Gen metadata version')
    count,pos=read_vlq(source,16);strings=bytearray(source[pos:pos+count]);pos+=count;arrays=[]
    for width in (32,24,24,4,8,12,16):
        count,pos=read_vlq(source,pos);arrays.append([bytearray(source[p:p+width]) for p in range(pos,pos+count*width,width)]);pos+=count*width
    require(pos==len(source) and not arrays[3],'Unsupported metadata layout')
    rows,entries,bundles,_,dirs,init,hashes=arrays
    def text(off):return strings[off:strings.index(0,off)].decode('ascii')
    def append(value):
        off=len(strings);strings.extend(value.encode('ascii')+b'\0');return off
    names={text(struct.unpack_from('<I',r)[0]):i for i,r in enumerate(rows) if i}
    def dirname(i):
        parts=[]
        while i:
            off,i=struct.unpack('<2i',dirs[i]);parts.append(text(off))
        return '\\'.join(reversed(parts))
    directory_ids={dirname(i):i for i in range(len(dirs))}
    def directory_id(name):
        if name not in directory_ids:
            parent,_,leaf=name.rpartition('\\');parent_id=directory_id(parent)
            directory_ids[name]=len(dirs);dirs.append(bytearray(struct.pack('<2i',append(leaf),parent_id)))
        return directory_ids[name]
    for name in sorted(n.replace('/','\\') for n in redux()):
        require(name not in names,'Duplicate legacy item path')
        fid=len(rows);names[name]=fid
        rows.append(bytearray(struct.pack('<8I',append(name),0,0,0,fid,0,0,0)))
        entries.append(bytearray(24));parent,_,leaf=name.rpartition('\\')
        init.append(bytearray(struct.pack('<3i',fid,directory_id(parent),append(leaf))))
        hashes.append(bytearray(struct.pack('<QIi',fnv64(name.encode('ascii')),fid,-1)))
    require(set(n.replace('\\','/') for n in names)==set(files),'Metadata paths differ from bundle')
    maximum=0
    for name,fid in names.items():
        key=name.replace('\\','/');size=files[key].stat().st_size;maximum=max(maximum,size)
        struct.pack_into('<II',rows[fid],8,size,size);struct.pack_into('<I',rows[fid],20,0)
        entries[fid]=bytearray(struct.pack('<QIIII',positions[key],size,0,fid,1))
    require(len(bundles)==2,'Single bundle required')
    old=struct.unpack('<Q4I',bundles[1]);start=32+toc_size
    bundles[1]=bytearray(struct.pack('<Q4I',bundle.stat().st_size-start,start,old[2],1,len(names)))
    hashes.sort(key=lambda r:struct.unpack_from('<Q',r)[0])
    require({struct.unpack_from('<I',h,8)[0] for h in hashes}==set(range(1,len(rows))),'Metadata hash coverage')
    output=bytearray(source[:8]+struct.pack('<II',maximum,maximum)+vlq(len(strings))+strings)
    for array in arrays:output+=vlq(len(array))+b''.join(array)
    return output

def nextgen():
    part=BUILD/'nextgen';package=part/'package';require(not package.exists(),'Fresh package required')
    shutil.copytree(ROOT/'BetaGwent/build/universal081/package-nextgen',package)
    content=package/'Mods/modBetaGwent0924/content'
    source=ROOT/'BetaGwent/build/universal081-menu-fix2/resources-nextgen'
    menus=json.loads((part/'menus/menus.json').read_text('utf8'))
    replacements={Path(m['path']).name:Path(m['path']) for m in menus['menus']}
    files={};resources=part/'resources';preserved=0;changed=[];extra=extra_resources('nextgen')
    for name,raw in bundle_entries(source/'blob0.bundle'):
        key=name.replace('\\','/');p=resources/key;p.parent.mkdir(parents=True,exist_ok=True)
        before=hashlib.sha256(raw).hexdigest()
        if Path(key).name in replacements:
            raw=strip_menu_authoring(replacements[Path(key).name].read_bytes());require(len(raw)<63*1024**2,'NG menu budget')
            changed.append(key)
        elif key in extra:raw=extra[key].read_bytes()
        else:preserved+=1
        p.write_bytes(raw);files[key]=p
        if key not in changed and key not in extra:require(sha(p)==before,'Auxiliary payload changed')
    files.update(redux());require(len(changed)==4,'Four menus required')
    with (source/'blob0.bundle').open('rb') as f:
        header=bytearray(f.read(32));table=f.read(struct.unpack_from('<I',header,16)[0])
    require(struct.unpack_from('<H',header,20)[0]==5,'Next-Gen bundle v5 required')
    old_rows={r[:256].split(b'\0')[0].decode('ascii').replace('\\','/'):bytearray(r) for r in [table[i:i+304] for i in range(0,len(table),304)]}
    table=bytearray();positions={};offset=(32+304*len(files)+4095)&~4095
    for name,p in files.items():
        row=old_rows.get(name,bytearray(304));encoded=name.replace('/','\\').encode('ascii');row[:len(encoded)]=encoded
        struct.pack_into('<QIIII',row,272,offset,p.stat().st_size,p.stat().st_size,zlib.crc32(p.read_bytes()),0)
        positions[name]=offset;table+=row;offset=(offset+p.stat().st_size+4095)&~4095
    total=max(positions[n]+p.stat().st_size for n,p in files.items());struct.pack_into('<I',header,8,total);struct.pack_into('<I',header,16,len(table))
    bundle=content/'blob0.bundle'
    with bundle.open('wb') as f:
        f.write(header);f.write(table)
        for name,p in files.items():
            f.write(bytes(positions[name]-f.tell()))
            with p.open('rb') as stream:shutil.copyfileobj(stream,f)
    checked={n.replace('\\','/'):hashlib.sha256(raw).hexdigest() for n,raw in bundle_entries(bundle)}
    require(checked=={n:sha(p) for n,p in files.items()},'Next-Gen bundle roundtrip')
    (content/'metadata.store').write_bytes(nextgen_metadata((source/'metadata.store').read_bytes(),bundle,positions,files,len(table)))
    result=json.loads((BUILD/'compile-nextgen/result.json').read_text('utf8'))
    require(result['exitCode']==0 and result['patchSourcesUnchangedDuringCompile'],'NG script compile failed')
    shutil.copy2(BUILD/'compile-nextgen/compiled/blob.rsblob',content/'precompiled.rsblob')
    report=dict(platform='5.0+',nativeCompilationPassed=True,changedMenus=changed,unchangedAuxiliaryPayloads=preserved,updatedLanguageResources=list(extra),reduxDefinitions=2,entries=len(files),maximumResourceBytes=max(p.stat().st_size for p in files.values()))
    finish(part,'modBetaGwent0924',report)

def classic():
    import build_classic_subimages as fragments
    base=fragments.base;part=BUILD/'classic';source=ROOT/'BetaGwent/build/classic081-effect-routes-fix18'
    base.BUILD=part;fragments.BUILD=part;base.SOURCE=source;base.VERSION=VERSION;base.edit_movie=fragments.add_fragments;base.archive=lambda:None
    extra=extra_resources('classic')
    base.edit_other_resource=lambda name,raw:extra[name.replace('\\','/')].read_bytes() if name.replace('\\','/') in extra else raw
    original_write=base.write_bundle;original_metadata=base.base.metadata
    def write(files,out,guids):return original_write(dict(files,**redux()),out,guids)
    base.write_bundle=write
    base.base.metadata=lambda raw,bundle,additions:original_metadata(raw,bundle,{n.replace('/','\\'):True for n in redux()})
    result=json.loads(CLASSIC_COMPILE.read_text('utf8'))
    require(result['compilePassed'] and not result['errors'],'Classic script compilation failed')
    require(not (part/'release-verification.json').exists(),'Completed release is immutable')
    if not (part/'verification.json').exists():base.main()
    target=part/'package/Mods/modBetaGwentClassic132/content/scripts'
    # Remove only the copied, owned source tree; never touch the accepted snapshot.
    require(target.resolve().is_relative_to(part.resolve()) and not target.is_symlink(),'Owned scripts required')
    if target.exists():shutil.rmtree(target)
    shutil.copytree(BUILD/'classic-prepared/Mods/modBetaGwentClassic132/content/scripts',target)
    for path in (part/'package/DLC').rglob('*'):
        if path.is_file():require(sha(path)==sha(source/'package'/path.relative_to(part/'package')),'Accepted DLC changed')
    require(sha(part/'package/Mods/modBetaGwentClassic132/content/soundspc.cache')==sha(source/'package/Mods/modBetaGwentClassic132/content/soundspc.cache'),'Accepted audio changed')
    report=json.loads((part/'verification.json').read_text('utf8'))
    report.update(platform='1.32',nativeCompilationPassed=True,reduxDefinitions=2)
    finish(part,'modBetaGwentClassic132',report)

def finish(part,mod,report):
    package=part/'package';info_path=package/'Mods'/mod/'info.json';info=json.loads(info_path.read_text('utf8'))
    info.update(version=VERSION,nativeGameplayVerified=False,deckExchange=True,consoleCommands=True,reduxInventoryCompatibility=True)
    info_path.write_text(json.dumps(info,ensure_ascii=False,indent=2),'utf8')
    docs=package/'BetaGwentDocs';docs.mkdir(exist_ok=True)
    for stale in ['README_PREVIEW_RU.md','BuildInfo.json']:
        p=docs/stale
        if p.exists():p.unlink()
    readme='''Gwent Beta Classic 0.8.2-rc1 — кандидат для игровой проверки.

Установка: полностью заменить прежнюю папку Mods/MOD и, если есть в архиве, DLC/dlcBetaGwentClassic132Assets. Остальные моды и DLC сохраняются. Сделайте резервную копию прежней версии. В архиве 1.32 уже включены принятые эффекты fix18. Скрипты устанавливаются без готового кэша: Script Merger может потребовать повторного объединения с другими модами. Для Next-Gen используется precompiled.rsblob.

В редакторе: «Экспорт» копирует BG1-строку; «Импорт» принимает строку из буфера. При недостающих картах показывается список и стоимость; создание требует отдельного нажатия. Неверная строка не меняет колоду. После импорта сохраните колоду обычной кнопкой. Если движок не даёт доступ к буферу, используйте Ctrl+C/Ctrl+V в выделяемом поле.

Консоль: bg_help(), bg_status(), bg_kegs(10), bg_scraps(1000), bg_card(id,1), bg_find("имя"), bg_faction("monsters"), bg_leaders(), bg_allcards(), bg_shopcheck(), bg_shoprefill(5). Изменение коллекции закрыто во время партии и меню; пополнение магазина требует открытого магазина. Команды меняют профиль, затем нужно штатно сохранить игру.

Обычные погибшие карты летят в фактический сброс своей стороны; особые карты — после разрешения способности. Изгнание и растворение сохраняют принятые эффекты.

Совместимость Redux: добавлены определения 203 отсутствующих карт для загрузки старого сохранения. Проверять на копии сохранения ДО исчезновения тела/инвентаря; уже утраченные данные этот мод не восстанавливает. Файлы сохранений не редактируются.

Перед stable проверить: обмен колодами, неверный код, создание недостающих карт, сохранение/загрузка; смерть отряда, сыгранная особая карта, изгнание; загрузку старого Redux-сохранения; NPC-партию и возврат управления. Новые сообщения обмена пока на русском; прежние 13 языков текста и 5 озвучек сохранены. Это RC, игровая приёмка ещё не завершена.
'''.replace('Mods/MOD','Mods/'+mod).replace('0.8.2-rc1',VERSION)
    if VERSION=='0.8.2-rc2':readme+='\nRC2: исправлено открытие импорта и экспорта непосредственно в редакторе колоды. Скрипты и прочие функции совпадают с RC1.\n'
    if VERSION=='0.8.2-rc3':
        readme=readme.replace('Новые сообщения обмена пока на русском; прежние 13 языков текста и 5 озвучек сохранены.','Сообщения обмена переведены на 13 языков; пять озвучек сохранены.')
        readme+='\nRC3: переводы обмена, отступы окон, нижняя панель действий, место под состояние колоды, переход с видимого края карточной полки к сохранению с геймпада и обратно. VS переходит от входа к движущемуся портрету; анимация королевы синхронизируется с реальным запуском её звука.\n'
    if VERSION=='0.8.2':
        for stale in ['README_0.8.2_RC_RU.txt','README_RU.md']:
            p=docs/stale
            if p.exists():p.unlink()
        public=ROOT/'docs/releases/0.8.2/nexus'
        for lang in ['ru','en']:
            shutil.copy2(public/lang/'description.md',docs/('README_'+lang.upper()+'.md'))
            shutil.copy2(public/lang/'changelog.md',docs/('CHANGELOG_'+lang.upper()+'.md'))
    else:
        (docs/'README_0.8.2_RC_RU.txt').write_text(readme,'utf8')
    report.update(version=VERSION,gameplayVerified=False,saveFilesModified=False)
    (part/'release-verification.json').write_text(json.dumps(report,indent=2),'utf8')
    (docs/'BuildInfo.json').write_text(json.dumps(report,indent=2),'utf8')
    files=[dict(path=p.relative_to(package).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(package.rglob('*')) if p.is_file()]
    manifest=dict(version=VERSION,platform=report['platform'],files=files,nativeGameplayVerified=False)
    (package/('manifest-'+VERSION+'.json')).write_text(json.dumps(manifest,indent=2),'utf8')
    name='GwentBetaClassic-'+VERSION+'-'+('1.32' if mod.endswith('132') else '5.0+')+'-AllLanguages.zip'
    archive=ROOT/'BetaGwent/release'/name
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(package.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(package).as_posix())
    with zipfile.ZipFile(archive) as z:require(z.testzip() is None,'ZIP CRC')
    digest=sha(archive);archive.with_suffix('.zip.sha256').write_text(digest+'  '+name+'\n','ascii')
    (part/'archive.json').write_text(json.dumps(dict(path=str(archive),bytes=archive.stat().st_size,sha256=digest),indent=2),'utf8')
    print(name,archive.stat().st_size,flush=True)

if __name__=='__main__':
    {'classic':classic,'nextgen':nextgen}[sys.argv[1]]()
