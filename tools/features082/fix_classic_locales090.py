"""Export Classic font movies with the real SDK instead of cloning board metadata."""
from pathlib import Path
import sys,struct,zlib,hashlib,json,subprocess,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'BetaGwent/build/release090-integrated'
sys.path[:0]=[str(ROOT/'tools/ui'),str(ROOT/'tools/classic132'),str(Path(__file__).parent)]
from update_board_resource import movie_parts
from formats import Resource,write_bundle,sha
from package_cleaner082 import metadata
EXE=Path('D:/GOG Galaxy/Games/The Witcher 3 REDkit/bin/tools/GFx4/gfxexport_mult4fix.exe')
DEPOT='gameplay/gui_new/swf/betagwenttext'

def native_movie(resource):
    chunk=resource.chunks[0];_,pos=resource.properties(chunk)
    size=struct.unpack_from('<I',chunk,pos)[0]
    return pos,chunk[pos+4:pos+4+size]

def main():
    out=BUILD/'classic-languages-fixed';assert not out.exists();out.mkdir()
    reports=[];files={}
    for original in sorted((ROOT/'BetaGwent/build/release082-polish2/classic/resources'/DEPOT).glob('*.redswf')):
        name=original.stem;rel=DEPOT+'/'+original.name
        override=BUILD/'classic/extra-resources'/rel
        source=override if override.exists() else original
        resource=Resource(source.read_bytes());pos,movie=native_movie(resource)
        prefix,tags,tail=movie_parts(movie)
        assert len(resource.chunks)==1 and resource.classes==['CSwfResource']
        folder=out/name;folder.mkdir();swf=folder/(name+'.swf')
        body=prefix+b''.join(raw for code,data,raw in tags if code!=1000)+tail
        swf.write_bytes(b'FWS'+movie[3:4]+struct.pack('<I',len(body)+8)+body)
        command=[str(EXE),'-i','DDS','-lwr','-o',str(folder),'-d',str(folder),str(swf)]
        result=subprocess.run(command,capture_output=True,text=True,errors='replace',timeout=90)
        (folder/'export.log').write_text(result.stdout+result.stderr,'utf8')
        assert result.returncode==0,(name,result.stderr)
        exported=(folder/(name+'.gfx')).read_bytes()
        assert exported[:3]==b'GFX'
        _,new_tags,new_tail=movie_parts(b'FWS'+exported[3:])
        assert [d for c,d,_ in tags if c in [75,82,76]]==[d for c,d,_ in new_tags if c in [75,82,76]],'Font/ABC/linkage changed: '+name
        info=next(d for c,d,_ in new_tags if c==1000)
        assert name.encode('ascii') in info and b'betagwent_board' not in info
        assert not any(c==65 for c,_,_ in new_tags),'Exporter did not strip ScriptLimits'
        native=b'CFX'+exported[3:8]+zlib.compress(exported[8:],9)
        root=resource.chunks[0][:pos]+struct.pack('<I',len(native))+native+bytes(4)
        fixed=resource.replace_chunks([root]);checked=Resource(fixed)
        assert struct.unpack_from('<I',fixed,4)[0]==163 and all(r[1]==8192 for r in checked.records)
        override.parent.mkdir(parents=True,exist_ok=True);override.write_bytes(fixed);files[rel]=override
        reports.append(dict(locale=name,source=str(source),sourceSha256=hashlib.sha256(resource.data).hexdigest(),sha256=sha(override),bytes=len(fixed),fontAndAbcBytesPreserved=True,oldExporterInfo=next(d.hex() for c,d,_ in tags if c==1000),newExporterInfo=info.hex()))
    assert len(files)==13
    # A small, removable override lets the actual Classic loader validate this
    # independently of unfinished release packaging or AI changes.
    package=out/'package';mod=package/'Mods/mod000BetaGwentClassic132LocaleFix090';content=mod/'content';content.mkdir(parents=True)
    base=ROOT/'BetaGwent/build/release082-polish2/classic/package/Mods/modBetaGwentClassic132/content/blob0.bundle'
    with base.open('rb') as stream:
        header=stream.read(32);toc=stream.read(struct.unpack_from('<I',header,16)[0])
    guids={row[:256].split(b'\0')[0].decode('ascii').replace('\\','/'):row[256:272] for row in [toc[i:i+320] for i in range(0,len(toc),320)]}
    bundle=content/'blob0.bundle';write_bundle(files,bundle,guids)
    (content/'metadata.store').write_bytes(metadata(files,bundle,True))
    (content/'dep.cache').write_bytes(b'SPED'+struct.pack('<I',2)+b'\1'+bytes(16)+(b'\1'+bytes(4))*3)
    info=dict(name='Gwent Beta Classic 1.32 locale loading diagnostic',version='0.9.0',candidate=True,onlyLocaleResources=True,fontsAndAbcPreserved=True,gameplayVerified=False)
    (mod/'info.json').write_text(json.dumps(info,indent=2),'utf8')
    (package/'README_RU.txt').write_text('Проверочная накладка для основной 0.9.0 Classic 1.32. Скопировать Mods в папку игры, основную сборку и её DLC оставить. Меняются только 13 языковых ресурсов: используется настоящий GFxExport 4.3.27 вместо скопированного ExporterInfo основного меню. Байткод, словари и шрифтовые глифы побайтно сохранены. Проверить открытие колод и смену языков. После включения исправления в полную сборку удалить mod000BetaGwentClassic132LocaleFix090. Это кандидат, игровой результат ещё не подтверждён.\n','utf8')
    records=[dict(path=p.relative_to(package).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(package.rglob('*')) if p.is_file()]
    (package/'manifest.json').write_text(json.dumps(dict(**info,files=records),indent=2),'utf8')
    archive=ROOT/'BetaGwent/release/GwentBetaClassic-0.9.0-1.32-LocaleFix-Test.zip';assert not archive.exists()
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(package.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(package).as_posix())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    archive.with_suffix('.zip.sha256').write_text(sha(archive)+'  '+archive.name+'\n','ascii')
    (out/'verification.json').write_text(json.dumps(dict(exporter=str(EXE),locales=reports,archive=str(archive),gameplayVerified=False),indent=2),'utf8')
    print(json.dumps(dict(locales=13,abcAndGlyphsUnchanged=True,archive=str(archive),bytes=archive.stat().st_size)))

if __name__=='__main__':main()
