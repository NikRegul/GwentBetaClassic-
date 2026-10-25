"""Freeze 0.9.1 AI over the latest 0.9.0 scripts; keep Classic menu/RNG fixes."""
from pathlib import Path
import argparse, hashlib, json, shutil, sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import BASE_SCRIPTS
# duelNilfDependencies.ws: 0.9.1c Ida Emean pool fix (Beta 0.9.24: Fog/Clear Skies/Alzur's Thunder).
AI_FILES=('developmentBoardMenu.ws','duelArchetypeAI.ws','duelPublicResponseAI.ws','duelStrategyAI.ws','duelReplyTreeAI.ws','duelEndgameAI.ws','duelSession.ws','duelLiveCard.ws','duelClone.ws','duelCatalog.ws','duelNilfDependencies.ws','duelEffectRuntime.ws',
          'duelAICatalog.ws','duelAIResearch.ws','duelAIPass.ws','duelNilf.ws','duelAudio.ws',
          'duelAITuning.ws','duelNorth.ws','duelAudioCatalog.ws','progressionCatalog.ws','deckProfile.ws','profileBackup.ws','collectionProfile.ws','deckBuilder.ws','profileCleanup090.ws','opponentRotation.ws')
AI_FILES += tuple(p.name for p in sorted((ROOT/'BetaGwent/development/scripts/game/betagwent').glob('betaOriginal*.ws')))
CORE_FILES=('randomGenerator.ws','matchState.ws')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=ROOT/'BetaGwent/build/release091-ai')
    p.add_argument('--base',type=Path,default=BASE_SCRIPTS)
    a=p.parse_args();out=a.out.resolve();base=a.base.resolve()
    if out.exists(): raise ValueError('Use a new output directory; sources are immutable once frozen')
    out.mkdir(parents=True)
    shutil.copytree(base/'scripts',out/'scripts')
    for name in AI_FILES:
        shutil.copy2(ROOT/'BetaGwent/development/scripts/game/betagwent'/name,out/'scripts/game/betagwent'/name)
    for name in CORE_FILES:
        shutil.copy2(ROOT/'BetaGwent/scripts/game/betagwent'/name,out/'scripts/game/betagwent'/name)
    shutil.copytree(base/'classic-audit',out/'classic-audit')
    frozen=out/'classic-audit/baseline/scripts'
    shutil.copytree(out/'scripts',frozen,dirs_exist_ok=True)
    audit_path=out/'classic-audit/audit.json'
    audit=json.loads(audit_path.read_text('utf8'))
    audit['sourceScripts']={p.relative_to(frozen).as_posix():sha(p) for p in sorted(frozen.rglob('*.ws'))}
    audit['sourceScriptCount']=len(audit['sourceScripts']);audit['featureCandidate']='0.9.1'
    audit_path.write_text(json.dumps(audit,indent=2),encoding='utf8')
    sys.path.insert(0,str(ROOT/'tools/classic132'))
    from prepare_scripts import prepare
    prepare(out/'classic-audit',out/'classic-prepared-final')
    # Apply the accepted Classic changes BEFORE compilation, rather than
    # patching a shipping .ws after checking an unrelated compiled version.
    classic=out/'classic-prepared-final'
    scripts=classic/'Mods/modBetaGwentClassic132/content/scripts'
    menu=scripts/'game/betagwent/developmentBoardMenu.ws'
    text=menu.read_text('utf16');old="theGame.RequestMenu('BetaGwentKeg',kegMenuInit);"
    assert text.count(old)==1
    menu.write_bytes(text.replace(old,"theGame.RequestMenu('TestMenu',kegMenuInit);").replace('\n','\r\n').encode('utf16'))
    player=scripts/'game/player/playerWitcher.ws';text=player.read_text('utf16')
    sys.path.insert(0,str(ROOT/'tools/features082'))
    from package_classic132keg090 import RNG_OLD, RNG_NEW
    RNG_OLD=RNG_OLD.replace('\r\n','\n');RNG_NEW=RNG_NEW.replace('\r\n','\n')
    assert text.count(RNG_OLD)==1
    player.write_bytes(text.replace(RNG_OLD,RNG_NEW).replace('\n','\r\n').encode('utf16'))
    from classic_audio091 import patch as patch_classic_audio, patch_menu as patch_classic_audio_menu
    audio=scripts/'game/betagwent/duelAudio.ws'
    audio.write_bytes(patch_classic_audio(audio.read_text('utf16')).replace('\n','\r\n').encode('utf16'))
    menu.write_bytes(patch_classic_audio_menu(menu.read_text('utf16')).replace('\n','\r\n').encode('utf16'))
    prep_path=classic/'preparation.json';prep=json.loads(prep_path.read_text('utf8'))
    prep['outputScripts']={p.relative_to(scripts).as_posix():sha(p) for p in sorted(scripts.rglob('*.ws'))}
    prep['candidate']='0.9.1';prep_path.write_text(json.dumps(prep,indent=2),encoding='utf8')
    report=dict(version='0.9.1',base=str(base),aiFiles=list(AI_FILES),coreFiles=list(CORE_FILES),
                scripts={p.relative_to(out/'scripts').as_posix():sha(p) for p in sorted((out/'scripts').rglob('*.ws'))},
                classicPrepared=str(classic),inGameVerified=False)
    (out/'source-freeze.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('Prepared immutable 0.9.1 sources:',out)

if __name__=='__main__':main()
