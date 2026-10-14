from pathlib import Path
import json,re,subprocess,sys
import ws2js
ROOT=Path(__file__).resolve().parents[2]
src=(ROOT/'BetaGwent/development/scripts/game/betagwent/collectionQuest.ws').read_text('utf-8-sig')
body=src[src.index('function BetaGwentSkelligeQuestClaims()'):src.index('// Run outside the reward graph')]
out=ROOT/'BetaGwent/build/fixes126/quest-test';out.mkdir(parents=True,exist_ok=True)
p=out/'quest.ws';p.write_text('''class CJournalBase extends IScriptable { public var guid : string; }
class CJournalContainer extends CJournalBase {
 public var children : array<CJournalBase>;
 public function GetNumChildren() : int { return children.Size(); }
 public function GetChild(i : int) : CJournalBase { return children[i]; }
}
class CJournalQuest extends CJournalContainer { public var baseName : string; }
class CJournalQuestPhase extends CJournalContainer {}
class CJournalQuestObjective extends CJournalContainer {
 public var quest : CJournalQuest;public var count : int;
 public function GetParentQuest() : CJournalQuest { return quest; }
 public function GetCount() : int { return count; }
}
'''+body,'utf8')
code,_=ws2js.build([p],[])
host=(Path(sys.argv[1])/'runtime.js').read_text('utf8')
tests=r'''
var facts={},entries=[],statuses={},counts={},writes=[];globalThis.JS_Active=1;
globalThis.FactsQuerySum=n=>facts[n]||0;globalThis.LogChannel=()=>{};
globalThis.theGame={GetJournalManager:()=>({GetActivatedOfType:(t,a)=>{a.length=0;if(t==='CJournalQuest')a.push(...entries);},GetEntryStatus:o=>statuses[o.guid],GetQuestObjectiveCount:g=>counts[g]||0,SetQuestObjectiveCount:(g,n)=>{counts[g]=n;writes.push([g,n]);}})};
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
function objective(id,name,status,count=19){let q=new CJournalQuest();q.baseName=name;q.guid='quest-'+id;statuses[q.guid]=1;let phase=new CJournalQuestPhase();q.children.push(phase);let o=new CJournalQuestObjective();o.guid=id;o.quest=q;o.count=count;phase.children.push(o);entries.push(q);statuses[id]=status;return o;}
objective('active','cg700_all_cards',1);objective('complete','cg700_all_cards',2);objective('other','other_quest',1);objective('main','cg700_all_cards',1,24);
BetaGwentSyncSkelligeQuestProgress();check(writes.length===0,'starter ownership does not invent wins');
facts.merchant_card_shop_12_tournament_meadows_armourer_card_already_given=1;
BetaGwentSyncSkelligeQuestProgress();check(counts.active===1,'permanent NPC reward advances the active objective');
check(!counts.complete&&!counts.other&&!counts.main,'completed and unrelated objectives remain intact');
BetaGwentSyncSkelligeQuestProgress();check(writes.length===1,'reload/repeated refresh does not increment twice');
facts.merchant_card_shop_12_tournament_meadows_armourer_card_already_given=9;
check(BetaGwentSkelligeQuestClaims()===1,'repeat rewards still count once');
facts.merchant_card_shop_13_tournament_meadows_blacksmith_card_already_given=1;
BetaGwentSyncSkelligeQuestProgress();check(counts.active===2,'a distinct quest opponent advances the counter');
counts.active=8;BetaGwentSyncSkelligeQuestProgress();check(counts.active===8,'higher native progress is never reduced');
facts.merchant_card_ordinary_npc_card_already_given=1;
check(BetaGwentSkelligeQuestClaims()===2,'ordinary four-win farming does not advance Skellige quest');
facts.merchant_card_q705_tailor_card_already_given=1;
check(BetaGwentSkelligeQuestClaims()===3,'the nineteenth native map-pin opponent is included');
for(const quest of entries)statuses[quest.guid]=2;
counts.active=0;BetaGwentSyncSkelligeQuestProgress();check(counts.active===0,'completed quest root cannot be repaired');
for(const quest of entries)statuses[quest.guid]=1;
BetaGwentSyncSkelligeQuestProgress();check(counts.active===3,'native quest-phase-objective hierarchy restores actual wins');
console.log('PASS Skellige quest',checks);
require('fs').writeFileSync(process.argv[2]||'docs/evidence/quest126.json',JSON.stringify({checks,actualWitcherScript:true,nativeGameTested:false,nativeRewardClaims:19},null,2)+'\n');
'''
f=out/'test.js';f.write_text(host+'\n'+code+'\n'+tests,'utf8')
subprocess.run(['node',str(f),*sys.argv[2:3]],check=True,cwd=ROOT)
subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/ai/check_quest_sync167.py'),sys.argv[1]],check=True,cwd=ROOT)
