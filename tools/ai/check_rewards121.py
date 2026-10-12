"""Execute save-profile WS with mock engine handles; not native save verification."""
from pathlib import Path
import re, subprocess, sys
import ws2js

ROOT = Path(__file__).resolve().parents[2]
snapshot = Path(sys.argv[1]).resolve()
source = ROOT/'BetaGwent/development/scripts/game/betagwent'
out = ROOT/'BetaGwent/build/profile121'
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
const facts=new Map();
function FactsSet(k,v){facts.set(k,v);}
function FactsQueryLatestValue(k){return facts.get(k)||0;}
function LogChannel(){}
function NameToString(v){return String(v);}
const theGame=null;
function StrLen(v){return v.length;}
function StrLeft(v,n){return v.slice(0,n);}
const entities=new Map();
function actor(id,guid){const a={stableId:id,GetGuidHash:()=>guid};entities.set(id,a);return a;}
function EntityHandleSet(h,a){h.stableId=a.stableId;}
function EntityHandleGet(h){return entities.get(h.stableId)||null;}
function player(){const p=new W3PlayerWitcher();
 p.BetaGwentKegPending=()=>false;p.BetaGwentUpdateCollectionProgress=()=>{};p.BetaGwentSyncTournamentAccess=()=>{};
 p.BetaGwentAddScraps=n=>{p.scraps=(p.scraps||0)+n;};p.BetaGwentScraps=()=>p.scraps||0;
 p.BetaGwentReceive=id=>{p.received=(p.received||0)+1;p.BetaGwentGrant(id);return 0;};p.BetaGwentProgressionPick=()=>0;return p;}
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;console.log('PASS',n);}
let p=player();check(p.BetaGwentEnsureCollection(),'initial collection');
const npc=actor('persistent-a',100),key=p.BetaGwentRewardActorKey(npc);
for(let i=0;i<4;i++)p.BetaGwentWinReward('ordinary',100,key);
check(p.received===4 && p.betaGwentRewardActorWins[key-1]===4,'four rewards per actor');
p.BetaGwentWinReward('ordinary',100,key);check(p.received===4&&p.scraps===20,'fifth win gives scraps');
const saved=JSON.parse(JSON.stringify(p));p=Object.assign(player(),saved);
const restored=actor('persistent-a',999),restoredKey=p.BetaGwentRewardActorKey(restored);
check(restoredKey===key,'mock save handles survive changed runtime GuidHash');
p.BetaGwentWinReward('ordinary',999,restoredKey);check(p.received===4&&p.scraps===40,'reload does not reissue cards');
const other=actor('persistent-b',999),otherKey=p.BetaGwentRewardActorKey(other);
check(otherKey!==key,'different NPC with same runtime hash has independent ledger');
p.BetaGwentWinReward('ordinary',999,otherKey);check(p.received===5,'different NPC still earns a card');
const old=player();old.betaGwentRewardedNpcs=[123,123,123,123,123];const migrated=old.BetaGwentRewardActorKey(actor('legacy',123));
check(old.betaGwentRewardActorWins[migrated-1]===4,'legacy matching ledger capped and migrated');
const broken=player();broken.betaGwentRewardActorWins=[2];check(broken.BetaGwentRewardActorKey(npc)===0,'malformed saved ledger not overwritten');
check(broken.betaGwentRewardActorWins.length===1&&broken.betaGwentRewardActors.length===0,'malformed fields preserved');
// Additive starter revision: old owned cards and a customized saved starter survive.
p=player();p.betaGwentCollectionSchema=1;p.betaGwentStarterSetRevision=2;
p.BetaGwentGrant(142102);const cards={v:[]};BetaGwentDuelPresetDeck(19,cards);
cards.v[cards.v.indexOf(142103)]=142102;
check(p.BetaGwentStoreStarterDeck(3,cards.v,'Customized',16,200166),'store original customized Scoia starter');
const prior=JSON.stringify([p.betaGwentStarterDeckCards,p.betaGwentStarterDeckNames,p.betaGwentStarterDeckLeaders]);
check(p.BetaGwentEnsureCollection(),'apply new starter revision');
check(p.BetaGwentOwned(142103)===1&&p.BetaGwentOwned(142102)===1,'Iorveth added while Isengrim retained');
check(JSON.stringify([p.betaGwentStarterDeckCards,p.betaGwentStarterDeckNames,p.betaGwentStarterDeckLeaders])===prior,'customized starter remains byte-for-byte unchanged');
check(p.betaGwentStarterSetRevision===3,'revision applied once');
// Rename/edit -> mock save reload -> reset exactly one override -> reload again.
check(p.BetaGwentStoreStarterDeck(0,cards.v,'Other starter',16,200166),'store independent starter override');
const untouched=JSON.stringify([p.betaGwentStarterDeckNames[0],p.betaGwentStarterDeckCards.slice(0,40)]);
const reloaded=Object.assign(player(),JSON.parse(JSON.stringify(p)));
const loadedCards={v:[]},loadedName={v:''},loadedFaction={v:0},loadedLeader={v:0};
check(reloaded.BetaGwentLoadDeck(12,loadedCards,loadedName,loadedFaction,loadedLeader)&&loadedName.v==='Customized','renamed starter survives mock reload');
check(reloaded.BetaGwentClearDeck(12),'reset chosen starter override');
const again=Object.assign(player(),JSON.parse(JSON.stringify(reloaded)));
check(!again.BetaGwentLoadDeck(12,loadedCards,loadedName,loadedFaction,loadedLeader),'reset survives mock reload and allows default fallback');
check(JSON.stringify([again.betaGwentStarterDeckNames[0],again.betaGwentStarterDeckCards.slice(0,40)])===untouched,'reset preserves independent starter');
check(again.betaGwentStarterDeckCards.slice(120,160).every(v=>v===0),'reset clears only chosen starter card range');
// Stage 131: profile mirror survives a save made without the mod.
facts.clear();
const src=player();check(src.BetaGwentEnsureCollection(),'backup source collection');
const deck={v:[]};BetaGwentDuelPresetDeck(19,deck);
check(src.BetaGwentStoreDeck(1,deck.v,'Mine',16,200166),'store player deck for backup');
src.betaGwentScraps=77;src.betaGwentKegsUnopened=2;src.BetaGwentBackupProfile();
const wiped=player();check(wiped.BetaGwentEnsureCollection(),'empty profile restores from facts');
check(JSON.stringify(wiped.betaGwentOwnedIds)===JSON.stringify(src.betaGwentOwnedIds)&&JSON.stringify(wiped.betaGwentOwnedCopies)===JSON.stringify(src.betaGwentOwnedCopies),'restored collection matches');
check(wiped.betaGwentScraps===77&&wiped.betaGwentKegsUnopened===2,'restored scraps and kegs');
const rc={v:[]},rn={v:''},rf={v:0},rl={v:0};
check(wiped.BetaGwentLoadDeck(1,rc,rn,rf,rl)&&JSON.stringify(rc.v)===JSON.stringify(deck.v)&&rl.v===200166&&rf.v===16,'restored deck cards, leader and faction');
const kept=player();kept.BetaGwentEnsureCollection();kept.betaGwentScraps=5;check(!kept.BetaGwentRestoreProfile()&&kept.betaGwentScraps===5,'existing profile is never overwritten');
console.log(JSON.stringify({stage:121,checks,nativeSerializationTested:false}));
'''
script = out/'checks.js'
script.write_text(host+'\n(function(){\n'+translated+'\n'+checks+'\n})();\n','utf8')
result = subprocess.run(['node',str(script)],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
(out/'result.txt').write_text(result.stdout+result.stderr,'utf8')
print((result.stdout+result.stderr)[-5000:])
raise SystemExit(result.returncode)
