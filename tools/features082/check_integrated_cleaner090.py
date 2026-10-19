"""Execute actual cleanup and lifecycle guards against isolated profile fixtures."""
from pathlib import Path
import re,json,sys,subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'BetaGwent/build/release090-integrated'
S=OUT/'scripts/game/betagwent'
sys.path.insert(0,str(ROOT/'tools/ai'))
import ws2js

def method(source,name):
    m=re.search(r'(?:public|private)?\s*(?:timer\s+)?function '+name+r'\([^)]*\)[^{]*\{',source)
    assert m,name
    end=m.end();depth=1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[m.start():end]

def main():
    cleanup=(S/'profileCleanup090.ws').read_text('utf-8-sig')
    decl=r'@addField\(W3PlayerWitcher\)\s*((?:private|public) saved var [^;]+;)'
    fields=json.loads((OUT/'inventory.json').read_text('utf8'))['allSavedFields']
    fields=[f for f in fields if f['target']=='W3PlayerWitcher']
    saved='\n'.join('private var '+f['name']+' : '+f['type']+';' for f in fields)
    saved+='\n'+re.search(decl,cleanup)[1].replace('saved var','var')
    cleanup=re.sub(decl,'',cleanup)
    methods=[]
    for name in ['BetaGwentCleanupPending','BetaGwentCleanProfile090']:
        text=method(cleanup,name);methods.append(text)
        start=cleanup.index('@addMethod(W3PlayerWitcher)');opening=cleanup.index('{',start);end=opening+1;depth=1
        while depth:
            depth+=(cleanup[end]=='{')-(cleanup[end]=='}');end+=1
        cleanup=cleanup[:start]+cleanup[end:]
    for filename,names in {
        'collectionProfile.ws':['BetaGwentEnsureCollection','BetaGwentRewardActorKey'],
        'profileBackup.ws':['BetaGwentBackupProfile','BetaGwentRestoreProfile','BetaGwentMirrorNpcWins','BetaGwentMirrorQuestReward'],
        'kegProfile.ws':['BetaGwentMigrateInventoryKegs','BetaGwentAddKegs'],
        'collectionQuest.ws':['BetaGwentScheduleQuestSync','BetaGwentQuestSyncTick'],
    }.items():
        source=(S/filename).read_text('utf-8-sig')
        methods += [method(source,name) for name in names]
    for filename,names in {'universalLanguages.ws':['BetaGwentInitializeLanguages'],'developmentBoardMenu.ws':['BetaGwentTextLanguage137'],'collectionQuest.ws':['BetaGwentSyncSkelligeQuestProgress']}.items():
        source=(S/filename).read_text('utf-8-sig')
        cleanup+='\n'+'\n'.join(method(source,name) for name in names)
    wrapper='''struct EntityHandle { var stableId : string; }
class W3PlayerWitcher extends IScriptable {
'''+saved+'\n'+'\n'.join(methods)+'''
 private var betaGwentCollectionTrackingReady : bool;
 private var betaGwentTrackedCollectionSize : int;
 private var betaGwentQuestSyncPasses : int;
 private var betaGwentCollectionSeeding : bool;
 public function GetInventory() : CInventoryComponent { return NULL; }
 public function IsInCombat() : bool { return false; }
 public function RemoveTimer(value : name) {}
}
'''+cleanup
    native_types=set(re.findall(r'\((C[A-Za-z0-9_]+)\)',wrapper))
    wrapper='\n'.join('class '+name+' extends IScriptable {}' for name in sorted(native_types))+'\n'+wrapper
    path=OUT/'cleanup-wrapper.ws';path.write_text(wrapper,'utf8')
    translated,_=ws2js.build([path],list(S.glob('*.ws')))
    js=(ROOT/'tools/ai/jshost/runtime.js').read_text('utf8')+'\n'+translated+'\n'+r'''
const assert=require('assert');let checks=0;
function check(ok,label){assert(ok,label);checks++;}
const facts=new Map(),notices=[],removedTimers=[];let menu=false,combat=false,pending=false,requested=false;
function FactsDoesExist(k){return facts.has(k);}function FactsRemove(k){facts.delete(k);return true;}
function FactsSet(k,v){facts.set(k,v);}function FactsQueryLatestValue(k){return facts.get(k)||0;}
function StrLeft(v,n){return v.slice(0,n);}function StrMid(v,n,l){return v.slice(n,n+l);}function StrLen(v){return v.length;}
function NameToString(v){return v;}function LogChannel(){}
let thePlayer=new W3PlayerWitcher();
const theGame={GetGuiManager:()=>({ShowNotification:v=>notices.push(v),IsAnyMenu:()=>menu}),GetGwintManager:()=>({gameRequested:requested,betaNpcPending:pending})};
'''+f'const fields={json.dumps(fields)};'+r'''
const inventory=new Map([['betagwent_keg',7],['betagwent_legacy',3],['Crowns',120],['gwint_card_redux',2]]);
function configure(p){p.IsInCombat=()=>combat;p.RemoveTimer=n=>removedTimers.push(n);p.GetInventory=()=>({GetAllItems:a=>a.push(...inventory.keys()),GetItemName:id=>id,GetItemQuantity:id=>inventory.get(id)||0,RemoveItem:(id,n)=>{check(n===inventory.get(id),'remove whole stack');inventory.delete(id);return true;}});}
configure(thePlayer);
for(const f of fields)thePlayer[f.name]=f.type.startsWith('array<')?[1,2]:f.type==='bool'?true:17;
thePlayer.betaGwentRewardedNpcs=[123,-456];thePlayer.betaGwentRewardedQuests=['quest_deck'];
thePlayer.betaGwentCollectionTrackingReady=true;thePlayer.betaGwentTrackedCollectionSize=50;thePlayer.betaGwentQuestSyncPasses=3;
const owned=['bg_b2_cur','bg_b2_1_ci1000','bg_b2_2_cc2047','bg_b2_1_d13_39','bg_b2_2_d8_n','bg_b2_1_ni2000','bg_bk_ci_1000','bg_bk_d8_39','bg_bkn_123','bg_bkn_-456','bg_bkq_quest_deck','bg_text_language','betagwent_collection_owned'];
const foreign=['quest_native','gwint_all_cards_collected','Gwint_Card_Looted','HasGwentTournamentDeck','other_mod','bg_other_mod_fact','betagwent_other_mod_fact'];
for(const k of [...owned,...foreign,'bg_bkn_99999999'])facts.set(k,1);
const before=JSON.stringify([...facts]),beforePlayer=JSON.stringify(thePlayer);
bg_clean_preview();bg_clean_confirm('wrong');bg_clean_keys('bg_bkn_99999999');
check(before===JSON.stringify([...facts])&&beforePlayer===JSON.stringify(thePlayer),'preview, wrong token and pre-confirm key list read-only');
for(const flag of ['menu','combat','pending','requested']){
 menu=flag==='menu';combat=flag==='combat';pending=flag==='pending';requested=flag==='requested';
 bg_clean_confirm('DELETE_BETA_GWENT');
 check(before===JSON.stringify([...facts])&&!thePlayer.BetaGwentCleanupPending(),'guard '+flag);
}
menu=combat=pending=requested=false;
bg_clean_confirm('DELETE_BETA_GWENT');
check(owned.every(k=>!facts.has(k)),'all known mirrors and settings removed');
check(foreign.every(k=>facts.get(k)===1),'native quests, achievements, Redux and unrelated facts preserved');
check(!inventory.has('betagwent_keg')&&!inventory.has('betagwent_legacy')&&inventory.get('Crowns')===120&&inventory.get('gwint_card_redux')===2,'only own inventory stacks removed');
check(fields.every(f=>Array.isArray(thePlayer[f.name])?thePlayer[f.name].length===0:!thePlayer[f.name]),'38 old saved fields cleared');
check(thePlayer.BetaGwentCleanupPending(),'saved uninstall latch set');
check(!thePlayer.betaGwentCollectionTrackingReady&&thePlayer.betaGwentTrackedCollectionSize===0&&thePlayer.betaGwentQuestSyncPasses===0&&removedTimers.includes('BetaGwentQuestSyncTick'),'cached tracking and delayed quest sync stopped');
bg_clean_keys('bg_bkn_99999999|quest_native|bg_other_mod_fact|betagwent_other_mod_fact');
check(!facts.has('bg_bkn_99999999')&&foreign.every(k=>facts.get(k)===1),'post-confirm orphan cleanup constrained to owned namespaces');
const after=JSON.stringify([...facts]);
function blockedLifecycle(p){
 check(p.BetaGwentEnsureCollection()===false,'no starter regrant after cleanup');
 check(p.BetaGwentRestoreProfile()===false,'no mirror restore after cleanup');
 p.BetaGwentBackupProfile();p.BetaGwentMirrorNpcWins(123,4);p.BetaGwentMirrorQuestReward('quest_deck');
 p.BetaGwentAddKegs(7);p.BetaGwentMigrateInventoryKegs();p.BetaGwentScheduleQuestSync();p.BetaGwentQuestSyncTick(0,0);
 check(p.BetaGwentRewardActorKey(null)===0,'reward actor callbacks cannot refill ledgers');
 BetaGwentInitializeLanguages();BetaGwentTextLanguage137(1);BetaGwentSyncSkelligeQuestProgress();
 check(after===JSON.stringify([...facts])&&p.betaGwentKegsUnopened===0,'save/restore/language/reward hooks do not regenerate facts or kegs');
}
blockedLifecycle(thePlayer);
const loaded=new W3PlayerWitcher();
for(const f of fields)loaded[f.name]=JSON.parse(JSON.stringify(thePlayer[f.name]));
loaded.betaGwentCleanupPending090=thePlayer.betaGwentCleanupPending090;configure(loaded);thePlayer=loaded;
blockedLifecycle(thePlayer);
bg_clean_confirm('DELETE_BETA_GWENT');check(after===JSON.stringify([...facts]),'repeat after reload is idempotent');
facts.set('bg_bkn_123',1);bg_clean_keys('x'.repeat(2049)+'|bg_bkn_123');check(facts.has('bg_bkn_123'),'oversized imported list rejected');
menu=true;bg_clean_keys('bg_bkn_123');check(facts.has('bg_bkn_123'),'import list respects menu guard');menu=false;
combat=true;bg_clean_keys('bg_bkn_123');check(facts.has('bg_bkn_123'),'import list respects combat guard');combat=false;
const report={checks,clearedPlayerFields:fields.length,reloadLatchVerified:true,nativeSaveRoundTripVerified:false};
console.log(JSON.stringify(report));
'''
    path=OUT/'cleanup-tests.js';path.write_text(js,'utf8')
    result=subprocess.run(['node',str(path)],cwd=ROOT,check=True,capture_output=True,text=True)
    print(result.stdout)
    (OUT/'cleanup-tests.json').write_text(result.stdout,'utf8')

if __name__=='__main__':main()
