"""Stage 136: facts mirror format 2 (banks, checksum, staged restore, reward ledgers).
Executes the real profile WitcherScript with a mock facts database; not native save verification."""
from pathlib import Path
import re, subprocess, sys
import ws2js

ROOT = Path(__file__).resolve().parents[2]
snapshot = Path(sys.argv[1]).resolve()
source = ROOT/'BetaGwent/development/scripts/game/betagwent'
out = ROOT/'BetaGwent/build/profile136'
out.mkdir(parents=True, exist_ok=True)
collection = (source/'collectionProfile.ws').read_text('utf-8-sig')
cap = re.search(r'function BetaGwentCollectionCap\(.*?\n}\n', collection, re.S).group()
collection = collection.replace(cap, '')
profile = collection + (source/'deckProfile.ws').read_text('utf-8-sig') + (source/'profileBackup.ws').read_text('utf-8-sig')
profile = re.sub(r'@add(?:Field|Method)\(W3PlayerWitcher\)\s*', '', profile).replace('private saved var', 'private var')
wrapper = out/'profile.ws'
wrapper.write_text('struct EntityHandle { var stableId : string; }\n'+cap+'\nclass W3PlayerWitcher extends IScriptable {\n'+profile+'''
 private var betaGwentScraps : int;
 private var betaGwentKegsUnopened : int;
 private var betaGwentKegAutomatic : array<int>;
 private var betaGwentKegOffers : array<int>;
 private var betaGwentKegAutomaticScraps : array<int>;
 private var betaGwentOpponentBag : array<int>;
 private var betaGwentOpponentRecent : array<int>;
 public function BetaGwentUpdateCollectionProgress() {}
 public function BetaGwentSyncTournamentAccess() {}
 public function BetaGwentKegPending() : bool { return false; }
 public function BetaGwentAddScraps(value : int) {}
 public function BetaGwentScraps() : int { return 0; }
 public function BetaGwentReceive(id : int) : int { return 0; }
}''', 'utf8')
extra = list(source.glob('*.ws')) + list((ROOT/'BetaGwent/scripts/game/betagwent').glob('*.ws'))
translated, _ = ws2js.build([wrapper,source/'duelCatalog.ws',source/'progressionCatalog.ws'], extra)
host = '\n'.join((snapshot/f).read_text('utf8') for f in ('runtime.js','rules.js','harness.js'))
checks = r'''
const facts=new Map();const log=[];
function FactsSet(k,v){facts.set(k,v);}
function FactsQueryLatestValue(k){return facts.get(k)||0;}
function LogChannel(c,m){log.push(m);}
function NameToString(v){return String(v);}
let notices=0;const theGame={GetGuiManager:()=>({ShowNotification:()=>{notices++;}})};
function StrLen(v){return v.length;}
function StrLeft(v,n){return v.slice(0,n);}
const entities=new Map();
function actor(id,guid){const a={stableId:id,GetGuidHash:()=>guid};entities.set(id,a);return a;}
function EntityHandleSet(h,a){h.stableId=a.stableId;}
function EntityHandleGet(h){return entities.get(h.stableId)||null;}
function player(){const p=new W3PlayerWitcher();
 p.BetaGwentKegPending=()=>p.betaGwentKegOffers.length>0;p.BetaGwentUpdateCollectionProgress=()=>{};p.BetaGwentSyncTournamentAccess=()=>{};
 p.BetaGwentAddScraps=n=>{p.betaGwentScraps=Math.max(0,(p.betaGwentScraps||0)+n);};p.BetaGwentScraps=()=>p.betaGwentScraps||0;
 p.BetaGwentReceive=id=>{p.received=(p.received||0)+1;if(!p.BetaGwentGrant(id)){p.betaGwentScraps+=200;return 200;}return 0;};p.BetaGwentProgressionPick=()=>0;return p;}
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;console.log('PASS',n);}
const snap=p=>JSON.stringify([p.betaGwentOwnedIds,p.betaGwentOwnedCopies,p.betaGwentScraps,p.betaGwentKegsUnopened,p.betaGwentDeckCards,p.betaGwentStarterDeckCards,p.betaGwentKegOffers,p.betaGwentOpponentBag]);
const S=JSON.stringify;
function rich(){const p=player();check(p.BetaGwentEnsureCollection(),'source collection');
 const deck={v:[]};BetaGwentDuelPresetDeck(19,deck);check(p.BetaGwentStoreDeck(1,deck.v,'Mine',16,200166),'store player deck');
 p.betaGwentScraps=77;p.betaGwentKegsUnopened=2;p.betaGwentDifficulty=2;p.betaGwentAiPause=3;p.betaGwentAnimationTempo=15;p.betaGwentReducedEffects=true;
 p.betaGwentProgressionSeed=123456;p.betaGwentPreferredDeck=1001;
 p.betaGwentKegAutomatic=[p.betaGwentOwnedIds[0],p.betaGwentOwnedIds[1]];p.betaGwentKegAutomaticScraps=[0,10];p.betaGwentKegOffers=[122101,122102,122105];
 p.betaGwentOpponentBag=[16,17,18];p.betaGwentOpponentRecent=[19];return p;}
// 1. Round trip of every mirrored field.
let src=rich();src.BetaGwentBackupProfile();
const cur1=facts.get('bg_b2_cur'),gen1=facts.get('bg_b2_gen');check((cur1===1||cur1===2)&&facts.get('bg_b2_'+cur1+'_done')===gen1,'current bank complete with latest generation');
let w=player();check(w.BetaGwentEnsureCollection(),'empty profile restores from current bank format');
check(S(w.betaGwentOwnedIds)===S(src.betaGwentOwnedIds)&&S(w.betaGwentOwnedCopies)===S(src.betaGwentOwnedCopies),'collection restored');
check(w.betaGwentScraps===77&&w.betaGwentKegsUnopened===2,'scraps and kegs restored');
check(w.betaGwentDifficulty===2&&w.betaGwentAiPause===3&&w.betaGwentAnimationTempo===15&&w.betaGwentReducedEffects===true,'settings restored');
check(w.betaGwentProgressionSeed===123456&&w.betaGwentPreferredDeck===1001,'seed and preferred deck restored');
check(S(w.betaGwentKegOffers)===S(src.betaGwentKegOffers)&&S(w.betaGwentKegAutomatic)===S(src.betaGwentKegAutomatic)&&S(w.betaGwentKegAutomaticScraps)===S([0,10]),'unfinished paid keg choice restored');
check(S(w.betaGwentOpponentBag)===S([16,17,18])&&S(w.betaGwentOpponentRecent)===S([19]),'opponent rotation restored');
const rc={v:[]},rn={v:''},rf={v:0},rl={v:0};
check(w.BetaGwentLoadDeck(1,rc,rn,rf,rl)&&rl.v===200166&&rf.v===16&&rc.v.length>=25,'deck restored');
// 2. Alternating banks; the previous complete copy survives a broken current bank.
src.betaGwentScraps=90;src.BetaGwentBackupProfile();
const cur2=facts.get('bg_b2_cur');check(cur2===3-cur1&&facts.get('bg_b2_'+cur2+'_done')===gen1+1&&facts.get('bg_b2_'+cur1+'_done')===gen1,'next backup goes to the other bank, previous kept');
const good2=new Map(facts);
facts.set('bg_b2_'+cur2+'_ci3',facts.get('bg_b2_'+cur2+'_ci3')+1);
w=player();check(w.BetaGwentEnsureCollection()&&w.betaGwentScraps===77,'checksum failure falls back to previous complete bank');
check(log.some(m=>m.includes('PROFILE_RESTORE_REJECTED source=bank'+cur2)),'rejection logged');
// 3. Interrupted write: completion marker missing on the current bank.
facts.clear();good2.forEach((v,k)=>facts.set(k,v));facts.set('bg_b2_'+cur2+'_done',0);
w=player();check(w.BetaGwentEnsureCollection()&&w.betaGwentScraps===77,'incomplete current bank ignored');
// 4. Duplicate card ID with a matching checksum: rejected by validation, profile untouched.
facts.clear();good2.forEach((v,k)=>facts.set(k,v));
function rewriteSum(bank){const p='bg_b2_'+bank+'_';let a=1,b=0;const mix=v=>{v=v%65521;if(v<0)v+=65521;a=(a+v)%65521;b=(b+a)%65521;};
 const keys=['gen','sc','kg','pf','sd','tm','re','df','ap','cn'];for(const k of keys)mix(facts.get(p+k)||0);
 const n=facts.get(p+'cn');for(let i=0;i<n;i++){mix(facts.get(p+'ci'+i)||0);mix(facts.get(p+'cc'+i)||0);}
 for(let s=1;s<=13;s++){const d=p+'d'+s+'_';const m=facts.get(d+'n')||0;mix(m);if(!m)continue;mix(facts.get(d+'l'));mix(facts.get(d+'f'));for(let i=0;i<m;i++)mix(facts.get(d+i));}
 for(const k of ['ka','ks','ko','ob','or']){const m=facts.get(p+k)||0;mix(m);for(let i=0;i<m;i++)mix(facts.get(p+k+i)||0);}
 if(facts.get(p+'fm')===3&&facts.get(p+'fg')===facts.get(p+'gen')){mix(3);mix(facts.get(p+'fg'));const m=facts.get(p+'nc')||0;mix(m);for(let i=0;i<m;i++)mix(facts.get(p+'ni'+i)||0);} facts.set(p+'sa',a);facts.set(p+'sb',b);}
rewriteSum(cur2);check(facts.get('bg_b2_'+cur2+'_sa')===good2.get('bg_b2_'+cur2+'_sa'),'test checksum model matches the script');
facts.set('bg_b2_'+cur2+'_ci1',facts.get('bg_b2_'+cur2+'_ci0'));rewriteSum(cur2);
facts.set('bg_b2_'+cur1+'_cc0',99);rewriteSum(cur1);
notices=0;w=player();const before=snap(w);
check(w.BetaGwentRestoreProfile()===false&&snap(w)===before&&w.betaGwentCollectionSchema===0,'invalid mirror never partially applied');
check(facts.get('bg_b2_hold')===1&&notices===1,'invalid mirror held and the player is told');
const held=new Map(facts);
check(w.BetaGwentEnsureCollection()&&w.betaGwentOwnedIds.length>0,'new profile starts');
w.BetaGwentBackupProfile();
let same=true;held.forEach((v,k)=>{if(facts.get(k)!==v)same=false;});
check(same&&facts.size===held.size,'held mirror is not overwritten');
// 5. Legacy format 1 still restores; a broken legacy entry is held, not clamped.
facts.clear();const legacy=player();legacy.BetaGwentEnsureCollection();
FactsSet('bg_bk_schema',1);FactsSet('bg_bk_scraps',41);FactsSet('bg_bk_kegs',1);FactsSet('bg_bk_pref',1);FactsSet('bg_bk_cn',legacy.betaGwentOwnedIds.length+1);
legacy.betaGwentOwnedIds.forEach((id,i)=>{FactsSet('bg_bk_ci_'+i,id);FactsSet('bg_bk_cc_'+i,legacy.betaGwentOwnedCopies[i]);});
for(let s=1;s<=13;s++)FactsSet('bg_bk_d'+s+'_n',1);
w=player();check(w.BetaGwentEnsureCollection()&&S(w.betaGwentOwnedIds)===S(legacy.betaGwentOwnedIds)&&w.betaGwentScraps===40,'format 1 mirror restores');
FactsSet('bg_bk_cc_0',0);w=player();check(!w.BetaGwentRestoreProfile()&&facts.get('bg_b2_hold')===1,'format 1 entry without copies rejected');
// 6. Reward ledgers survive a save without the mod.
facts.clear();let p=player();p.BetaGwentEnsureCollection();
const npc=actor('npc-a',555),key=p.BetaGwentRewardActorKey(npc);
for(let i=0;i<4;i++)p.BetaGwentWinReward('ordinary',555,key);
p.BetaGwentWinReward('Baron',0,0);const gotGold=p.BetaGwentOwned(122101);
p.BetaGwentBackupProfile();
check(facts.get('bg_bkn_555')===5&&facts.get('bg_bkq_Baron')===1,'reward ledgers mirrored');
const receivedBefore=p.received;
w=player();check(w.BetaGwentEnsureCollection()&&w.betaGwentRewardActors.length===0,'restored profile has no saved ledger');
w.received=0;w.betaGwentScraps=0;
const k2=w.BetaGwentRewardActorKey(actor('npc-a-reloaded',555));
check(w.betaGwentRewardActorWins[k2-1]===4,'NPC win count comes back from the mirror');
w.BetaGwentWinReward('ordinary',555,k2);check(w.received===0&&w.betaGwentScraps===20,'fifth win after restore gives scraps, not a card');
w.BetaGwentWinReward('Baron',0,0);check(w.received===0&&w.betaGwentScraps===70&&w.betaGwentRewardedQuests.includes('Baron'),'quest reward not paid twice after restore');
check(gotGold===1,'quest gold granted once originally');
// 7. Without a restore the mirror never changes ordinary reward logic.
facts.clear();facts.set('bg_bkn_555',5);const fresh=player();fresh.BetaGwentEnsureCollection();
const k3=fresh.BetaGwentRewardActorKey(actor('npc-other',555));check(fresh.betaGwentRewardActorWins[k3-1]===0,'mirror ignored in ordinary play');
// 8. Existing profile is never overwritten.
const kept=player();kept.BetaGwentEnsureCollection();kept.betaGwentScraps=5;check(!kept.BetaGwentRestoreProfile()&&kept.betaGwentScraps===5,'existing profile never overwritten');
// Format 3: auxiliary unseen state migrates separately from ownership.
facts.clear();let upgraded=player();upgraded.BetaGwentEnsureCollection();
upgraded.betaGwentNewCardsSchema=0;
check(upgraded.BetaGwentEnsureCollection()&&upgraded.betaGwentNewCardIds.length===0,'old saved collection upgrades without marking existing cards new');
upgraded.betaGwentScraps=432;upgraded.betaGwentKegsUnopened=3;upgraded.betaGwentRewardedQuests.push('claimed');
const oldClaims=S(upgraded.betaGwentRewardedQuests),oldWins=S(upgraded.betaGwentRewardedNpcs),seedBefore=upgraded.betaGwentProgressionSeed;
const given=upgraded.BetaGwentGrantAllCards();
check(given>0&&upgraded.betaGwentNewCardIds.length>0,'debug command fills missing cards and records unseen acquisitions');
check(upgraded.betaGwentOwnedIds.every((id,i)=>upgraded.betaGwentOwnedCopies[i]===BetaGwentCollectionCap(id)),'debug command grants exactly the allowed number of copies');
check(upgraded.betaGwentScraps===432&&upgraded.betaGwentKegsUnopened===3&&S(upgraded.betaGwentRewardedQuests)===oldClaims&&S(upgraded.betaGwentRewardedNpcs)===oldWins&&upgraded.betaGwentProgressionSeed===seedBefore,'debug grant preserves money, kegs, reward claims and progression RNG');
const seenId=upgraded.betaGwentNewCardIds[0];check(upgraded.BetaGwentCardIsNew(seenId)&&upgraded.BetaGwentCardSeen(seenId)&&!upgraded.BetaGwentCardIsNew(seenId),'explicit inspection clears only its unseen template');
const newBefore=S(upgraded.betaGwentNewCardIds);check(upgraded.BetaGwentGrantAllCards()===0&&S(upgraded.betaGwentNewCardIds)===newBefore&&!upgraded.BetaGwentCardIsNew(seenId),'repeated debug grant is idempotent and does not remark seen cards');
upgraded.BetaGwentBackupProfile();const markerBank=facts.get('bg_b2_cur'),prefix='bg_b2_'+markerBank+'_';
check(facts.get(prefix+'fm')===3&&facts.get(prefix+'fg')===facts.get(prefix+'gen'),'new format belongs to this completed bank generation');
let restoredMarkers=player();check(restoredMarkers.BetaGwentRestoreProfile()&&S(restoredMarkers.betaGwentNewCardIds)===newBefore,'format 3 restores exactly the unseen templates');
const markerFacts=new Map(facts);facts.set(prefix+'ni0',999999);
let brokenMarkers=player();check(!brokenMarkers.BetaGwentRestoreBank(markerBank)&&brokenMarkers.betaGwentOwnedIds.length===0,'invalid new-card reference rejects the entire bank without partial ownership changes');
facts.clear();markerFacts.forEach((v,k)=>facts.set(k,v));
facts.set(prefix+'fg',0);rewriteSum(markerBank);
let older=player();check(older.BetaGwentRestoreBank(markerBank)&&older.betaGwentNewCardIds.length===0&&S(older.betaGwentOwnedIds)===S(upgraded.betaGwentOwnedIds),'format 2 bank with stale extension keys restores all cards as seen');
facts.clear();markerFacts.forEach((v,k)=>facts.set(k,v));facts.set(prefix+'nc',facts.get(prefix+'nc')+1);
let interruptedMarkers=player();check(!interruptedMarkers.BetaGwentRestoreBank(markerBank)&&interruptedMarkers.betaGwentOwnedIds.length===0,'corrupt unseen length cannot be applied');

console.log(JSON.stringify({stage:136,checks,nativeSerializationTested:false}));
'''
script = out/'checks.js'
script.write_text(host+'\n(function(){\n'+translated+'\n'+checks+'\n})();\n','utf8')
result = subprocess.run(['node',str(script)],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
(out/'result.txt').write_text(result.stdout+result.stderr,'utf8')
print((result.stdout+result.stderr)[-5000:])
if result.returncode==0:
    import json, hashlib
    inputs = [source/name for name in ('collectionProfile.ws','deckProfile.ws','profileBackup.ws')]
    inputs.append(Path(__file__).resolve())
    proof = dict(stage=136,checks=result.stdout.count('PASS '),nativeSerializationTested=False,
                 sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    (ROOT/'docs/evidence/profile136.json').write_text(json.dumps(proof,indent=2)+'\n','utf8')
raise SystemExit(result.returncode)
