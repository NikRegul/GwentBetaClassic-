"""Freeze all RC3 mirrors and lower the revised scripts for native 1.32 compilation."""
from pathlib import Path
import sys,json,hashlib,shutil
sys.path.insert(0,str(Path(__file__).parent))
from patch_ui_intro import ROOT,BUILD
sys.path.insert(0,str(ROOT/'tools/classic132'))
from prepare_scripts import prepare
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    for platform in ['nextgen','classic']:
        ui=BUILD/platform/'ui'
        for mirror in ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
            for p in (ui/'src').glob('*.as'):shutil.copy2(p,ui/mirror/p.name)
        manifest=json.loads((BUILD/platform/'ui-inputs.json').read_text('utf8'))
        manifest['sources']={p.name:sha(p) for p in (ui/'src').glob('*.as')}
        (BUILD/platform/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
    previous=ROOT/'BetaGwent/build/features082/candidate/classic-audit'
    audit=json.loads((previous/'audit.json').read_text('utf8'))
    audit['sourceScripts']={p.relative_to(BUILD/'scripts').as_posix():sha(p) for p in (BUILD/'scripts').rglob('*.ws')}
    audit['sourceScriptCount']=len(audit['sourceScripts']);audit['sourceValidationPassed']=False
    out=BUILD/'classic-audit';assert not out.exists()
    shutil.copytree(previous/'baseline/vanilla-targets',out/'baseline/vanilla-targets')
    shutil.copytree(BUILD/'scripts',out/'baseline/scripts')
    (out/'audit.json').write_text(json.dumps(audit,indent=2),'utf8')
    prepare(out,BUILD/'classic-prepared')
    # Keep editable sources aligned with the candidate actually being compiled.
    for name in ['BetaGwentBoard.as','BetaGwentController.as','BetaGwentTextLanguage.as','BetaGwentExchangeText082.as','BetaGwentLeaderPreview.as']:
        for directory in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
            shutil.copy2(BUILD/'nextgen/ui/src'/name,ROOT/'BetaGwent/ui'/directory/name)
    for name in ['developmentBoardMenu.ws','deckBuilder.ws','duelAudio.ws']:
        shutil.copy2(BUILD/'scripts/game/betagwent'/name,ROOT/'BetaGwent/development/scripts/game/betagwent'/name)
    print('Sources frozen for native compilation')
if __name__=='__main__':main()
