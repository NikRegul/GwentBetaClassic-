"""Freeze 0.9.1 AI over the latest 0.9.0 scripts; keep Classic menu/RNG fixes."""
from pathlib import Path
import argparse, hashlib, json, shutil, sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import BASE_SCRIPTS
# duelNilfDependencies.ws: 0.9.1c Ida Emean pool fix (Beta 0.9.24: Fog/Clear Skies/Alzur's Thunder).
AI_FILES=('developmentBoardMenu.ws','duelArchetypeAI.ws','duelPublicResponseAI.ws','duelStrategyAI.ws','duelReplyTreeAI.ws','duelEndgameAI.ws','duelSession.ws','duelVisualFrame.ws','duelLiveCard.ws','duelClone.ws','duelCatalog.ws','duelMonsters.ws','duelNilfDependencies.ws','duelEffectRuntime.ws','duelEvents.ws','duelWeather.ws',
          'duelAICatalog.ws','duelAIResearch.ws','duelAIPass.ws','duelNilf.ws','duelAudio.ws',
          'duelAITuning.ws','duelNorth.ws','duelSkellige.ws','duelScoia.ws','duelNeutral.ws','duelAudioCatalog.ws','progressionCatalog.ws','deckProfile.ws','profileBackup.ws','collectionProfile.ws','collectionQuest.ws','deckBuilder.ws','profileCleanup090.ws','kegProfile.ws','opponentRotation.ws',
          # 0.9.4 single save-backed store and its commit points.
          'aaProfileStore.ws','scrapsProfile.ws','capabilityProbe.ws')
AI_FILES += tuple(p.name for p in sorted((ROOT/'BetaGwent/development/scripts/game/betagwent').glob('betaOriginal*.ws')))
CORE_FILES=('randomGenerator.ws','matchState.ws')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=ROOT/'BetaGwent/build/release091-ai')
    p.add_argument('--base',type=Path,default=BASE_SCRIPTS)
    p.add_argument('--rules-snapshot',type=Path,help='Overlay verified WS from this frozen snapshot instead of the live shared checkout')
    a=p.parse_args();out=a.out.resolve();base=a.base.resolve()
    manifest=None
    if a.rules_snapshot:
        a.rules_snapshot=a.rules_snapshot.resolve()
        manifest=json.loads((a.rules_snapshot/'manifest.json').read_text('utf8'))
        for name,digest in manifest['snapshotFiles'].items():
            assert sha(a.rules_snapshot/name)==digest,'Changed rules snapshot: '+name
    def source(relative):
        if manifest is None:return ROOT/relative
        frozen_source=a.rules_snapshot/'sources'/relative
        assert sha(frozen_source)==manifest['files'][relative.as_posix()],'Changed frozen source: '+str(relative)
        return frozen_source
    if out.exists(): raise ValueError('Use a new output directory; sources are immutable once frozen')
    out.mkdir(parents=True)
    shutil.copytree(base/'scripts',out/'scripts')
    for name in AI_FILES:
        shutil.copy2(source(Path('BetaGwent/development/scripts/game/betagwent')/name),out/'scripts/game/betagwent'/name)
    for name in CORE_FILES:
        shutil.copy2(source(Path('BetaGwent/scripts/game/betagwent')/name),out/'scripts/game/betagwent'/name)
    shutil.copytree(base/'classic-audit',out/'classic-audit')
    frozen=out/'classic-audit/baseline/scripts'
    shutil.copytree(out/'scripts',frozen,dirs_exist_ok=True)
    audit_path=out/'classic-audit/audit.json'
    audit=json.loads(audit_path.read_text('utf8'))
    audit['sourceScripts']={p.relative_to(frozen).as_posix():sha(p) for p in sorted(frozen.rglob('*.ws'))}
    audit['sourceScriptCount']=len(audit['sourceScripts']);audit['featureCandidate']='0.9.1'
    # 0.9.4 hooks CR4Game.OnSaveStarted: retain its exact Classic 1.32 source,
    # verified against the vanilla manifest recorded by the original audit.
    rel='game/r4Game.ws';target=out/'classic-audit/baseline/vanilla-targets'/rel
    if not target.exists():
        from build_inputs import CLASSIC_RUNTIME
        vanilla=CLASSIC_RUNTIME/'content/content0/scripts'/rel
        assert sha(vanilla)==audit['vanillaScripts'][rel],'Classic r4Game.ws differs from the audited 1.32 game'
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(vanilla,target)
        audit['targetClasses']=sorted(set(audit['targetClasses'])|{'CR4Game'})
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
    text=text.replace(RNG_OLD,RNG_NEW)
    # 0.9.4: Classic keeps the legacy profile fields saved (see classic_legacy094).
    sys.path.insert(0,str(ROOT/'tools/features094'))
    from classic_legacy094 import patch as keep_legacy_saved
    if 'betaGwentStore' in text:text=keep_legacy_saved(text)
    player.write_bytes(text.replace('\n','\r\n').encode('utf16'))
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
    if manifest is not None:report.update(rulesSnapshot=str(a.rules_snapshot),rulesFingerprint=manifest['fingerprint'])
    (out/'source-freeze.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('Prepared immutable 0.9.1 sources:',out)

if __name__=='__main__':main()
