"""Verify the Russian compact candidate; installed-game acceptance stays pending."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    evidence=ROOT/'docs/evidence'
    art=json.loads((evidence/'compact-art98.json').read_text('utf8'))
    assert art['logicalSlotsUnchanged'] and art['cardPhysicalSize']==[288,405]
    assert art['boardHalfPhysicalSize']==[1536,531]
    for item in art['records']:
        assert sha(Path(item['source']))==item['sourceSha256']
        assert sha(Path(item['output']))==item['sha256']
    movies=json.loads((evidence/'stage98-completion.json').read_text('utf8'))
    assert len(movies['menus'])==3 and all(m['language']=='ru' for m in movies['menus'])
    for item in movies['menus']:assert sha(Path(item['resource']))==item['sha256']
    base=ROOT/'BetaGwent/build/release98/ru'
    packed=json.loads((base/'packed-resources-verified.json').read_text('utf8'))
    assert packed['packedPayloadsVerified'] and packed['guiStoredUncompressed'] and packed['guiLimitMiB']==55
    menus=[i for i in packed['entries'] if i['path'].endswith('.redswf')]
    assert len(menus)==3 and not any(i['path'].endswith('.redswfx') for i in packed['entries'])
    for item in menus:assert item['compression']==0 and item['size']==item['packedSize'] and item['size']<55*1024**2
    compiled=ROOT/'BetaGwent/build/board-compile97ru-final'
    result=json.loads((compiled/'result.json').read_text('utf8'))
    assert result['exitCode']==0 and not result['timedOut'] and result['patchSourcesUnchangedDuringCompile']
    assert len(result['patchSourcesBefore'])==61
    for item in result['patchSourcesBefore']:
        assert sha(base/'project/BetaGwent0924/workspace/scripts'/item['path'])==item['sha256']
    release=json.loads((evidence/'stage98-release-ru.json').read_text('utf8'))
    archive=Path(release['archive'])
    assert release['archiveVerified'] and release['version']=='0.2.5' and sha(archive)==release['archiveSha256']
    with zipfile.ZipFile(archive) as contents:
        assert contents.testzip() is None
        for item in release['files']:
            assert hashlib.sha256(contents.read(item['path'])).hexdigest()==item['sha256']
        assert hashlib.sha256(contents.read('Mods/modBetaGwent0924/content/precompiled.rsblob')).hexdigest()==sha(compiled/'compiled/blob.rsblob')
    report=dict(version='0.2.5',language='ru',archive=str(archive),archiveBytes=release['archiveBytes'],archiveSha256=release['archiveSha256'],
                menus=menus,cardPhysicalSize=art['cardPhysicalSize'],boardHalfPhysicalSize=art['boardHalfPhysicalSize'],
                originalHDImagesUnchanged=True,verifiedScriptSourcesReused=61,packageIntegrityVerified=True,
                nativeRuntimeVerified=False,installedGameModified=False,englishBuildDeferred=True,publicationDeferred=True)
    (evidence/'stage98-final.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
