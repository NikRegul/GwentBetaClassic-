"""Copy the audited final9 source snapshot into the existing public checkout."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
FINAL=ROOT/'BetaGwent/build/release090-final9'
UI=ROOT/'BetaGwent/build/release090-ui9'
PUBLIC=ROOT/'BetaGwent/build/github-0.3.0'
AUDIT=ROOT/'BetaGwent/build/audit090-final9-20261019'
SUFFIXES={'.as','.ws','.py','.js','.cjs','.json','.md','.txt','.csv','.xml','.cs','.csproj','.ps1','.cmd','.cpp','.h','.hpp','.def'}
EXCLUDE={'vendor','__pycache__','bin','obj','node_modules','.git','assets','audio','build'}
PRIVATE={'github_auth_probe89.py','download_github_cli93.py','github_upload_batches89.py'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert (PUBLIC/'.git').is_dir()
    if '--resume' not in sys.argv:
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=PUBLIC).strip(),'Public checkout must be clean'
    audit=json.loads((AUDIT/'packages.json').read_text('utf8'))
    assert audit['releaseSource']==FINAL.name and len(audit['archives'])==2
    records={}
    def copy(source,relative):
        relative=Path(relative)
        assert not relative.is_absolute() and '..' not in relative.parts
        assert source.is_file() and not source.is_symlink()
        assert source.suffix.lower() in SUFFIXES or source.name=='AGENTS.md'
        raw=source.read_bytes()
        content=raw.decode('utf-8-sig',errors='replace')
        secrets=[r'<Property[^>]+Name="LicenseKey"[^>]+Value="[^"\s]+"',r'(?m)^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',r'\bsk-(?:proj-)?[A-Za-z0-9_-]{40,}']
        assert not any(re.search(pattern,content) for pattern in secrets),f'Possible secret: {source.name}'
        target=PUBLIC/relative
        assert target.resolve().is_relative_to(PUBLIC.resolve())
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
        assert target.read_bytes()==raw
        records[relative.as_posix()]=dict(path=relative.as_posix(),sha256=sha(source),bytes=len(raw))
    def tree(source,target,suffixes=SUFFIXES):
        for p in sorted(source.rglob('*')):
            if p.is_file() and p.suffix.lower() in suffixes and not any(part in EXCLUDE for part in p.relative_to(source).parts) and p.name not in PRIVATE:
                copy(p,Path(target)/p.relative_to(source))
    tree(FINAL/'scripts','BetaGwent/development/scripts',{'.ws'})
    tree(FINAL/'classic-prepared-final/Mods/modBetaGwentClassic132/content/scripts','BetaGwent/platforms/classic132/scripts',{'.ws'})
    tree(UI/'nextgen/ui/src','BetaGwent/ui/src',{'.as'})
    tree(UI/'classic/ui/src','BetaGwent/platforms/classic132/ui/src',{'.as'})
    for p in (ROOT/'BetaGwent/scripts/game/betagwent').glob('*.ws'):
        copy(FINAL/'scripts/game/betagwent'/p.name,Path('BetaGwent/scripts/game/betagwent')/p.name)
    tree(ROOT/'tools','tools')
    tree(ROOT/'BetaGwent/native','BetaGwent/native')
    for name in ['ai','design','duel']:
        tree(ROOT/'data/beta924'/name,'data/beta924/'+name)
    tree(ROOT/'docs/releases/0.9.0','docs/releases/0.9.0',{'.md','.txt','.json','.csv'})
    for p in (ROOT/'docs/releases').glob('0.9.0*.md'):copy(p,p.relative_to(ROOT))
    for pattern in ['2026-10-18-*','2026-10-19-*']:
        for p in (ROOT/'docs/reviews').glob(pattern):
            if p.suffix in {'.md','.json'}:copy(p,p.relative_to(ROOT))
    for rel in ['AGENTS.md','BetaGwent/ui/README.md','BetaGwent/release/0.9.0_CURRENT_RU.md','docs/BUILD_RU.md','docs/BUILD_EN.md','docs/README.md','docs/testing.md','docs/VFX_RENDERING_RULES_RU.md','docs/BUILD_0.9.0_RESOURCE_HANDOFF_RU.md']:
        copy(ROOT/rel,rel)
    # Export only the launchers matching this final9/r7 source snapshot.
    for name in ['Build-0.9.0-Final9.cmd', 'Build-Clipboard-r7.cmd']:
        copy(ROOT/name,name)
    for rel in ['packages.json','rules/manifest.json','selfplay.json','locales.json','clipboard-gate.json','cleaner/cleanup-tests.json','audio/intro-audio-tests.json','trial178.json']:
        copy(AUDIT/rel,Path('docs/evidence/final9-audit')/rel)
    copy(ROOT/'BetaGwent/release/GwentBetaClassic-0.9.0/release.json','docs/releases/0.9.0/release.json')
    report=dict(version='0.9.0',source='release090-final9',ui='release090-ui9',bridge='r7',sourceOnly=True,assetsIncluded=False,archivesIncluded=False,saveFilesIncluded=False,memoryDumpsIncluded=False,inGameVerified=False,files=list(records.values()))
    evidence=ROOT/'docs/evidence/github090-sources.json'
    evidence.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    copy(evidence,evidence.relative_to(ROOT))
    for rel in records:
        if rel.endswith('BetaGwentBoard.as'):
            raw=(PUBLIC/rel).read_bytes()
            assert raw.startswith(b'\xef\xbb\xbf') and not re.search(b'(?<!\r)\n',raw),rel
    print(json.dumps(dict(sourceFiles=len(records),publicCheckout=str(PUBLIC),bytes=sum(r['bytes'] for r in records.values()),sourceOnly=True)))

if __name__=='__main__':main()
