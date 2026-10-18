"""Curate only 0.8.2 sources and release documents into the public checkout."""
from pathlib import Path
import hashlib,json,shutil,subprocess

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'BetaGwent/build/release082-final'
PUBLIC=ROOT/'BetaGwent/build/github-0.3.0'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assert (BUILD/'final-audit.json').is_file(),'Both release archives must pass verification first'
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=PUBLIC).strip(),'Public checkout must be clean before preparation'
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=PUBLIC,text=True).strip().startswith('69bb604'),'Unexpected source baseline'
    records=[]
    def copy(source,target):
        assert source.is_file() and source.suffix.lower() in {'.as','.ws','.py','.js','.json','.md','.txt','.csv'}
        assert target.resolve().is_relative_to(PUBLIC.resolve())
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        records.append(dict(path=target.relative_to(PUBLIC).as_posix(),sha256=sha(source)))
    for source,target,suffix in [
        (BUILD/'scripts',PUBLIC/'BetaGwent/development/scripts',{'.ws'}),
        (BUILD/'classic-prepared/Mods/modBetaGwentClassic132/content/scripts',PUBLIC/'BetaGwent/platforms/classic132/scripts',{'.ws'}),
        (BUILD/'nextgen/ui/src',PUBLIC/'BetaGwent/ui/src',{'.as'}),
        (BUILD/'classic/ui/src',PUBLIC/'BetaGwent/platforms/classic132/ui/src',{'.as'}),
        (ROOT/'tools/features082',PUBLIC/'tools/features082',{'.py','.js'}),
        (ROOT/'docs/releases/0.8.2',PUBLIC/'docs/releases/0.8.2',{'.md','.txt','.json','.csv'}),
    ]:
        for p in sorted(source.rglob('*')):
            if p.is_file() and p.suffix.lower() in suffix:copy(p,target/p.relative_to(source))
    for rel in ['data/beta924/design/ui-exchange082.json','data/beta924/design/nexus082_updates.json',
                'data/beta924/compatibility/redux_inventory.json','tools/ai/gen_clone.py',
                'tools/universal/prepare_nexus081.py','tools/recon/run_redkit_compile.py',
                'tools/classic132/native_compile.py']:
        copy(ROOT/rel,PUBLIC/rel)
    for lang in ['en','ru','de','fr','it','pl','es','es-mx','pt-br','ja','ko','zh-cn','zh-tw']:
        rel=f'docs/releases/0.8.1/nexus/{lang}/description.md';copy(ROOT/rel,PUBLIC/rel)
    for name in ['0.8.2_RC1_RU.md','0.8.2_RC2_RU.md','0.8.2_RC3_RU.md','0.8.2_UI_INTRO_PLAN_RU.md','0.8.2_FEATURES_RU.md','0.8.2_PLAN_RU.md']:
        rel='docs/releases/'+name;copy(ROOT/rel,PUBLIC/rel)
    report=dict(version='0.8.2',sourceOnly=True,sourceCodeChangesSinceFinalRC3=False,
                assetsIncluded=False,saveFilesIncluded=False,memoryDumpsIncluded=False,
                files=records,archives=json.loads((BUILD/'final-audit.json').read_text('utf8')))
    path=ROOT/'docs/evidence/github082-sources.json';path.write_text(json.dumps(report,indent=2)+'\n','utf8')
    copy(path,PUBLIC/'docs/evidence/github082-sources.json')
    print(json.dumps(dict(sourceFiles=len(records),publicCheckout=str(PUBLIC),assetsIncluded=False)))

if __name__=='__main__':main()
