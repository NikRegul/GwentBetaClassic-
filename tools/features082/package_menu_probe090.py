"""Create a reversible four-menu override, preserving native textures and GUIDs."""
from pathlib import Path
import json,struct,sys,hashlib,shutil,zipfile,argparse
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'BetaGwent/build/release090-decrement-fix'
ARCHIVE=ROOT/'BetaGwent/release/GwentBetaClassic-0.9.0-1.32-MenuFix-Test.zip'
sys.path[:0]=[str(ROOT/'tools/classic132'),str(ROOT/'tools/ui'),str(ROOT/'tools/universal'),str(Path(__file__).parent)]
from formats import Resource,bundle_entries,write_bundle,sha
from update_board_resource import movie_parts
from package_cleaner082 import metadata
import build_classic_subimages as fragments
from build_classic_bitmap_fix import MAIN,native,image_names


def main():
    part=OUT/'classic';probe=OUT/'probe';assert not probe.exists()
    probe.mkdir()
    report=json.loads((part/'menus/menus.json').read_text('utf8'))
    compiled={Path(r['path']).stem:Path(r['path']) for r in report['menus']}
    for stem in compiled:
        text=(part/'menus'/(stem+'-abc.txt')).read_text('utf8')
        import re
        assert not re.search(r'\bdeclocal\s+\d',text),'Number declocal still emitted'
    fragments.BUILD=part
    base=ROOT/'BetaGwent/build/release082-polish2/classic/package/Mods/modBetaGwentClassic132/content'
    with (base/'blob0.bundle').open('rb') as f:
        head=f.read(32);table=f.read(struct.unpack_from('<I',head,16)[0])
    guids={row[:256].split(b'\0')[0].decode('ascii').replace('\\','/'):row[256:272]
           for row in [table[i:i+320] for i in range(0,len(table),320)]}
    files={};changed=[]
    for name,raw in bundle_entries(base/'blob0.bundle'):
        if name not in MAIN:continue
        old=Resource(raw);fresh=Resource(compiled[MAIN[name]].read_bytes())
        pos,old_movie=native(old);_,new_movie=native(fresh)
        new_movie=fragments.add_fragments(new_movie)
        assert image_names(new_movie)==image_names(old_movie)
        before=[(c,p) for c,p,_ in movie_parts(old_movie)[1] if c==1008]
        original_ids={struct.unpack_from('<H',p)[0] for c,p in before}
        after=[(c,p) for c,p,_ in movie_parts(new_movie)[1] if c==1008 and struct.unpack_from('<H',p)[0] in original_ids]
        assert before==after
        root=old.chunks[0][:pos]+struct.pack('<I',len(new_movie))+new_movie+bytes(4)
        raw=old.replace_chunks([root,*old.chunks[1:]])
        checked=Resource(raw)
        assert checked.chunks[1:]==old.chunks[1:] and checked.imports==old.imports
        assert len(raw)<=32*1024**2
        key=name.replace('\\','/');path=probe/'resources'/key;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        files[key]=path;changed.append(dict(path=key,bytes=len(raw),texturePixelsUnchanged=True,importsAndBindingsUnchanged=True,numberDeclocalAbsent=True))
    assert len(changed)==4
    for p in (ROOT/'BetaGwent/build/release090-integrated/classic/extra-resources').rglob('*.redswf'):
        key=p.relative_to(ROOT/'BetaGwent/build/release090-integrated/classic/extra-resources').as_posix()
        assert key.startswith('gameplay/gui_new/swf/betagwenttext/')
        files[key]=p
    assert len(files)==17
    package=probe/'package';mod=package/'Mods/mod000BetaGwentClassic132LocaleFix090';content=mod/'content';content.mkdir(parents=True)
    bundle=content/'blob0.bundle';write_bundle(files,bundle,guids)
    assert {n.replace('\\','/'):hashlib.sha256(raw).hexdigest() for n,raw in bundle_entries(bundle)}=={n:sha(p) for n,p in files.items()}
    (content/'metadata.store').write_bytes(metadata(files,bundle,True))
    # Dependencies use global resource GUIDs, preserved from the main package;
    # the unchanged main mod supplies the external pages they refer to.
    shutil.copy2(base/'dep.cache',content/'dep.cache')
    info=dict(version='0.9.0',candidate=True,name='Classic numeric local decrement diagnostic',
              mainModRequired=True,menus=4,locales=13,numberDeclocalAbsent=True,gameplayVerified=False)
    (mod/'info.json').write_text(json.dumps(info,indent=2),'utf8')
    (package/'README_RU.txt').write_text('Проверочная накладка Classic 1.32. Обновляет ранее установленную mod000BetaGwentClassic132LocaleFix090: теперь проверяет числовой декремент в подгонке кнопок. Основной мод и DLC обязательны. Байты текстур, привязки и GUID сохранены; скрипты игры не меняются. После проверки накладку нужно удалить при включении исправления в полный пакет. Результат в игре пока не подтверждён.\n','utf8')
    (probe/'verification.json').write_text(json.dumps(dict(**info,menusVerified=changed,dependencyCacheUnchanged=True),indent=2),'utf8')
    archive=ARCHIVE;assert not archive.exists()
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(package.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(package).as_posix())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    archive.with_suffix('.zip.sha256').write_text(sha(archive)+'  '+archive.name+'\n','ascii')
    print(json.dumps(dict(archive=str(archive),bytes=archive.stat().st_size,menus=4,numberDeclocalAbsent=True)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--build',type=Path,default=OUT);parser.add_argument('--archive',type=Path,default=ARCHIVE)
    args=parser.parse_args();OUT=args.build.resolve();ARCHIVE=args.archive.resolve()
    assert OUT.is_relative_to(ROOT/'BetaGwent/build') and ARCHIVE.is_relative_to(ROOT/'BetaGwent')
    main()
