"""Prepare opt-in cleanup in the main release, with a saved uninstall latch."""
from pathlib import Path
import re, json, hashlib, shutil, sys

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'BetaGwent/build/release082-polish2'
OUT=ROOT/'BetaGwent/build/release090-integrated'

def sha(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(b'\xef\xbb\xbf'+s.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))

def guard(s,name,statement):
    m=re.search(r'\bfunction '+name+r'\([^)]*\)[^{]*\{',s)
    assert m,name
    pos=m.end()
    # WitcherScript requires local variable declarations before statements.
    while True:
        v=re.match(r'\s*var\s+[^;]+;',s[pos:])
        if not v:break
        pos+=v.end()
    return s[:pos]+'\n    '+statement+s[pos:]

def main():
    assert not OUT.exists()
    shutil.copytree(BASE/'scripts',OUT/'scripts')
    scripts=OUT/'scripts/game/betagwent'
    source=(ROOT/'BetaGwent/build/cleaner082-safe/scripts/game/betagwent/cleaner082.ws').read_text('utf-8-sig')
    source=re.sub(r'@addField\(W3PlayerWitcher\)\s*(?:private|public|protected)\s+saved\s+var\s+\w+\s*:\s*[^;]+;\s*','',source)
    source='''// Cleanup is explicit. This saved latch survives a reload before uninstall.
@addField(W3PlayerWitcher)
private saved var betaGwentCleanupPending090 : bool;
@addMethod(W3PlayerWitcher)
public function BetaGwentCleanupPending() : bool { return betaGwentCleanupPending090; }
function BetaGwentCleanupBlocked() : bool
{
    var player : W3PlayerWitcher;
    player=(W3PlayerWitcher)thePlayer;return player && player.BetaGwentCleanupPending();
}
function BetaGwentCleanCanRun() : bool
{
    var player : W3PlayerWitcher;var manager : CR4GwintManager;
    if(!theGame)return false;
    player=(W3PlayerWitcher)thePlayer;if(!player)return false;
    manager=theGame.GetGwintManager();
    if(theGame.GetGuiManager().IsAnyMenu() || player.IsInCombat() || (manager && (manager.gameRequested || manager.betaNpcPending)))
    {BetaGwentCleanMessage("Close menus, finish Gwent and leave combat before cleanup.");return false;}
    return true;
}
'''+source
    source=source.replace('BetaGwentCleanProfile082','BetaGwentCleanProfile090')
    source=source.replace('make a backup; remove the main mod. Run', 'make a save backup. Built into the main mod. Run')
    source=source.replace('then SAVE AS NEW SLOT. No automatic cleanup.', 'then SAVE AS NEW SLOT, exit, uninstall the mod, load and save again. No automatic cleanup.')
    source=source.replace('exec function bg_clean_keys(keys : string) { BetaGwentCleanKeys(keys); }', '''exec function bg_clean_keys(keys : string)
{
    if(!BetaGwentCleanCanRun())return;
    if(!BetaGwentCleanupBlocked()){BetaGwentCleanMessage("Run bg_clean_confirm('DELETE_BETA_GWENT') first. No facts changed.");return;}
    BetaGwentCleanKeys(keys);
}''')
    source=source.replace('var bank,i,slot,count : int;', 'var bank,i,slot,count,quantity,failed : int;')
    source=source.replace('    // Read dynamic reward identifiers', '    betaGwentCleanupPending090=true;\n    RemoveTimer(\'BetaGwentQuestSyncTick\');betaGwentQuestSyncPasses=0;\n    betaGwentCollectionTrackingReady=false;betaGwentTrackedCollectionSize=0;\n    // Read dynamic reward identifiers')
    source=source.replace('if(StrLeft(itemName,10)=="betagwent_")inventory.RemoveItem(items[i]);', 'if(StrLeft(itemName,10)=="betagwent_"){quantity=inventory.GetItemQuantity(items[i]);if(quantity>0 && !inventory.RemoveItem(items[i],quantity))failed+=1;}')
    source=source.replace('Save to NEW SLOT, exit, remove cleaner, load that slot and save again.', 'Save to NEW SLOT, exit, uninstall Beta Gwent, load that slot and save again.')
    source=source.replace('    BetaGwentCleanMessage("Beta Gwent profile and known mirrors cleared.', '    if(failed>0)BetaGwentCleanMessage("Some Beta Gwent inventory stacks could not be removed: "+failed+". Retry before uninstalling.");\n    BetaGwentCleanMessage("Beta Gwent profile and known mirrors cleared.')
    old='''    player=(W3PlayerWitcher)thePlayer;if(!player)return;
    if(theGame.GetGuiManager().IsAnyMenu() || player.IsInCombat()){BetaGwentCleanMessage("Close menus and leave combat before cleanup.");return;}
    player.BetaGwentCleanProfile090();'''
    new='''    if(!BetaGwentCleanCanRun())return;
    player=(W3PlayerWitcher)thePlayer;
    player.BetaGwentCleanProfile090();'''
    assert old in source
    source=source.replace(old,new)
    write(scripts/'profileCleanup090.ws',source)
    patches={
        'collectionProfile.ws': [('BetaGwentEnsureCollection','if(BetaGwentCleanupPending())return false;'),('BetaGwentRewardActorKey','if(BetaGwentCleanupPending())return 0;')],
        'profileBackup.ws': [('BetaGwentBackupProfile','if(BetaGwentCleanupPending())return;'),('BetaGwentRestoreProfile','if(BetaGwentCleanupPending())return false;'),('BetaGwentMirrorNpcWins','if(BetaGwentCleanupPending())return;'),('BetaGwentMirrorQuestReward','if(BetaGwentCleanupPending())return;')],
        'kegProfile.ws': [('BetaGwentMigrateInventoryKegs','if(BetaGwentCleanupPending())return;'),('BetaGwentAddKegs','if(BetaGwentCleanupPending())return;')],
        'universalLanguages.ws': [('BetaGwentInitializeLanguages','if(BetaGwentCleanupBlocked())return;')],
        'nativeGwentEntry.ws': [('OnGwintGameRequested','if(BetaGwentCleanupBlocked()){BetaGwentCleanMessage("Beta Gwent was cleared. Save, exit and uninstall; load your original backup to keep playing.");return;}')],
        'developmentBoardMenu.ws': [('BetaGwentTextLanguage137','if(BetaGwentCleanupBlocked())return 1;')],
        'collectionQuest.ws': [('BetaGwentScheduleQuestSync','if(BetaGwentCleanupPending())return;'),('BetaGwentQuestSyncTick','if(BetaGwentCleanupPending())return;'),('BetaGwentSyncSkelligeQuestProgress','if(BetaGwentCleanupBlocked())return;')],
    }
    for name,items in patches.items():
        p=scripts/name;s=p.read_text('utf-8-sig')
        for name,statement in items:s=guard(s,name,statement)
        if p.name=='developmentBoardMenu.ws':
            s=s.replace('bg_shopcheck() · bg_shoprefill(5) · bg_help()', 'bg_shopcheck() · bg_shoprefill(5) · bg_help()\\nbg_clean_preview() · bg_clean_confirm(\'DELETE_BETA_GWENT\')')
        write(p,s)
    # Canonical development sources follow the frozen release inputs.
    for name in [*patches,'profileCleanup090.ws']:
        shutil.copy2(scripts/name,ROOT/'BetaGwent/development/scripts/game/betagwent'/name)
    inventory=json.loads((ROOT/'BetaGwent/build/cleaner082-safe/inventory.json').read_text('utf8'))
    inventory.update(version='0.9.0',embedded=True,cleanupLatch='betaGwentCleanupPending090',playerFieldsCleared=inventory['playerFields'],saveRoundTripVerified=False)
    (OUT/'inventory.json').write_text(json.dumps(inventory,indent=2),'utf8')
    sys.path.insert(0,str(ROOT/'tools/classic132'))
    from prepare_scripts import prepare
    adir=OUT/'classic-audit';audit=json.loads((BASE/'classic-phase-audit/audit.json').read_text('utf8'))
    shutil.copytree(BASE/'classic-phase-audit/baseline/vanilla-targets',adir/'baseline/vanilla-targets')
    shutil.copytree(OUT/'scripts',adir/'baseline/scripts')
    audit.update(sourceScripts={p.relative_to(OUT/'scripts').as_posix():sha(p) for p in (OUT/'scripts').rglob('*.ws')},sourceValidationPassed=False,featureCandidate='0.9.0-integrated-cleaner')
    audit['sourceScriptCount']=len(audit['sourceScripts'])
    (adir/'audit.json').write_text(json.dumps(audit,indent=2),'utf8')
    prepare(adir,OUT/'classic-prepared')
    print(json.dumps(dict(prepared=str(OUT),scriptCount=len(audit['sourceScripts']),clearedFields=inventory['playerFields'])))

if __name__=='__main__':main()
