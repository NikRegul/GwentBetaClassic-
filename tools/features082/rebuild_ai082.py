"""Build an isolated 0.8.2 revision, retaining accepted assets and original archives."""
from pathlib import Path
import hashlib,json,shutil,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'BetaGwent/build/release082-ai1'
BASE=ROOT/'BetaGwent/build/release082-final'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def prepare():
    sys.path.insert(0,str(ROOT/'tools/classic132'))
    from prepare_scripts import prepare as lower
    adir=BUILD/'classic-audit'
    audit=json.loads((BASE/'classic-audit/audit.json').read_text('utf8'))
    shutil.copytree(BASE/'classic-audit/baseline/vanilla-targets',adir/'baseline/vanilla-targets')
    shutil.copytree(BUILD/'scripts',adir/'baseline/scripts')
    audit.update(sourceScripts={p.relative_to(BUILD/'scripts').as_posix():sha(p) for p in (BUILD/'scripts').rglob('*.ws')},sourceValidationPassed=False,featureCandidate='0.8.2-ai1')
    audit['sourceScriptCount']=len(audit['sourceScripts'])
    (adir/'audit.json').write_text(json.dumps(audit,indent=2),'utf8')
    lower(adir,BUILD/'classic-prepared')
def package(platform):
    part=BUILD/platform;target=part/'package'
    assert not target.exists(),'Use fresh output; completed packages are retained'
    shutil.copytree(BASE/platform/'package',target)
    mod='modBetaGwentClassic132' if platform=='classic' else 'modBetaGwent0924'
    content=target/'Mods'/mod/'content'
    if platform=='classic':
        result=json.loads((ROOT/'BetaGwent/build/universal081/classic-runtime/runs/release082-ai1-native-full/result.json').read_text('utf8'))
        assert result['compilePassed'] and not result['errors']
        prepared=BUILD/'classic-prepared/Mods'/mod/'content/scripts'
        for p in prepared.rglob('*.ws'):shutil.copy2(p,content/'scripts'/p.relative_to(prepared))
    else:
        result=json.loads((BUILD/'compile-nextgen/result.json').read_text('utf8'))
        assert result['exitCode']==0 and result['patchSourcesUnchangedDuringCompile']
        actual={p.relative_to(BUILD/'scripts').as_posix():sha(p) for p in (BUILD/'scripts').rglob('*.ws')}
        assert actual=={p['path']:p['sha256'] for p in result['patchSourcesBefore']}
        shutil.copy2(BUILD/'compile-nextgen/compiled/blob.rsblob',content/'precompiled.rsblob')
    info=target/'Mods'/mod/'info.json';data=json.loads(info.read_text('utf8'));data.update(version='0.8.2-ai1',revision='ai1',nativeGameplayVerified=False);info.write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
    docs=target/'BetaGwentDocs'
    shutil.copy2(ROOT/'docs/releases/0.8.2_AI1_RU.md',docs/'0.8.2_AI1_RU.md')
    changed=[];kept=0
    for p in (BASE/platform/'package').rglob('*'):
        if p.is_file():
            rel=p.relative_to(BASE/platform/'package')
            if sha(p)!=sha(target/rel):changed.append(rel.as_posix())
            else:kept+=1
    allowed={f'Mods/{mod}/info.json'}
    if platform=='nextgen':allowed.add(f'Mods/{mod}/content/precompiled.rsblob')
    else:allowed|={f'Mods/{mod}/content/scripts/{p.relative_to(prepared).as_posix()}' for p in prepared.rglob('*.ws')}
    assert set(changed)<=allowed,changed
    for p in target.glob('manifest-*.json'):p.unlink()
    records=[dict(path=p.relative_to(target).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(target.rglob('*')) if p.is_file()]
    (target/'manifest-0.8.2-ai1.json').write_text(json.dumps(dict(version='0.8.2-ai1',files=records),indent=2),'utf8')
    version='1.32' if platform=='classic' else '5.0+'
    dest=ROOT/f'BetaGwent/release/GwentBetaClassic-0.8.2-ai1-{version}-AllLanguages.zip'
    assert not dest.exists()
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for p in sorted(target.rglob('*')):
            if p.is_file():archive.write(p,p.relative_to(target).as_posix())
    with zipfile.ZipFile(dest) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist())==sum(p.is_file() for p in target.rglob('*'))
    digest=sha(dest);dest.with_suffix(dest.suffix+'.sha256').write_text(digest+'  '+dest.name+'\n','ascii')
    report=dict(version='0.8.2',revision='ai1',platform=platform,archive=str(dest),bytes=dest.stat().st_size,sha256=digest,changedFiles=changed,preservedFiles=kept,nativeCompilationPassed=True,gameplayVerified=False)
    (part/'ai-release-verification.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps(report))
if __name__=='__main__':
    {'prepare':prepare,'classic':lambda:package('classic'),'nextgen':lambda:package('nextgen')}[sys.argv[1]]()
