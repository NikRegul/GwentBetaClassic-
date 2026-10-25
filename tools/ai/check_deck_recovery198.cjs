// Appended inside the translated actual profile class scope by the Python runner.
const facts=new Map(),logs=[];let writes=0,failAt=-1,thePlayer=null,checks=0;
function FactsSet(k,v){if(++writes===failAt)throw Error('simulated interruption');facts.set(k,v);}
function FactsRemove(k){facts.delete(k);}
function FactsQueryLatestValue(k){return facts.get(k)||0;}
function LogChannel(c,m){logs.push(m);}
function StrLen(v){return v.length;}
function IntToString(v){return String(v);}
function StrLeft(v,n){return v.slice(0,n);}
function NameToString(v){return String(v);}
function BetaGwentConsoleFormat(k,n){return 'Deck '+n;}
const theGame={GetGuiManager:()=>({ShowNotification(){}})};
function EntityHandleSet(h,a){h.stableId=a.stableId;}
function EntityHandleGet(){return null;}
function check(v,n){checks++;if(!v)throw Error(n);}
const S=JSON.stringify,copy=v=>JSON.parse(S(v));
function player(data){const p=new W3PlayerWitcher();if(data)Object.assign(p,copy(data));thePlayer=p;return p;}
function deck(preset=16){const ids={v:[]};BetaGwentDuelPresetDeck(preset,ids);const leader=BetaGwentDuelPreset(preset).leaderTemplateId;return {cards:ids.v,leader,faction:BetaGwentDuelDefinition(leader).header.factionMask};}
function store(p,slot,title='Deck '+slot,preset=16){thePlayer=p;const d=deck(preset);return p.BetaGwentStoreDeck(slot,d.cards,title,d.faction,d.leader);}
function load(p,slot){const c={v:[]},n={v:''},f={v:0},l={v:0};return {ok:p.BetaGwentLoadDeck(slot,c,n,f,l),cards:c.v,title:n.v,faction:f.v,leader:l.v};}
function rich(){facts.clear();const p=player();check(p.BetaGwentEnsureCollection(),'initialize collection');for(let s=1;s<=8;s++)check(store(p,s,'Моя колода '+s,16+(s-1)%5),'store all eight slots');
 for(let s=9;s<=13;s++)check(store(p,s,'Starter '+s,16+s-9),'store starter override');p.BetaGwentBackupProfile();return p;}
let p=player();for(let s=1;s<=8;s++)check(!load(p,s).ok,'fresh empty load has no out-of-bounds deck');check(p.BetaGwentDeckProfileValid(),'fresh profile initialized safely');
p=rich();const primary=copy(p),goodFacts=new Map(facts),expected=Array.from({length:8},(_,i)=>load(p,i+1));
function reset(){facts.clear();goodFacts.forEach((v,k)=>facts.set(k,v));return player(primary);}
function all(p,missing=0){for(let s=1;s<=8;s++){const x=load(p,s);check(x.ok===(s!==missing),'slot existence '+s);if(x.ok)check(S(x.cards)===S(expected[s-1].cards)&&x.leader===expected[s-1].leader,'exact deck preserved '+s);}}
for(const field of ['betaGwentDeckNames','betaGwentDeckLeaders','betaGwentDeckFactions','betaGwentDeckLengths','betaGwentDeckCards'])for(const n of [0,1,7,9,319]){
 p=reset();p[field]=Array.from({length:n},(_,i)=>p[field][i]??(field==='betaGwentDeckNames'?'extra':0));all(p);check(p.BetaGwentDeckProfileValid(),'repaired shape '+field+'/'+n);check(p.betaGwentDeckRecoverySchema===1,'raw damaged arrays quarantined');
 check(store(p,1,'После восстановления'),'save works after shape repair');all(p);
}
p=reset();p.betaGwentDeckSchema=0;all(p);check(p.BetaGwentDeckProfileValid(),'missing schema preserves surviving arrays');
for(const damaged of ['checksum','incomplete','generation']){
 p=reset();const cur=facts.get('bg_b2_cur'),pre='bg_b2_'+cur+'_';if(damaged==='checksum'){facts.set(pre+'sa',facts.get(pre+'sa')+1);const alt=deck(17),d=pre+'d1_';facts.set(d+'n',alt.cards.length);facts.set(d+'l',alt.leader);facts.set(d+'f',alt.faction);alt.cards.forEach((id,i)=>facts.set(d+i,id));}if(damaged==='incomplete')facts.set(pre+'done',0);if(damaged==='generation')facts.set(pre+'gen',-1);
 p.betaGwentDeckCards=[];all(p);check(logs.some(x=>x.includes('PROFILE_RESTORE_REJECTED')),'bad bank rejection logged');
}
p=reset();const before=S(p),fBefore=S([...facts]);p.betaGwentDeckSchema=99;const unknown=S(p);check(!store(p,1),'unknown schema rejected');check(S(p)===unknown&&S([...facts])===fBefore,'unknown schema neither changes data nor facts');p.BetaGwentBackupProfile();check(S([...facts])===fBefore,'unknown schema cannot replace backup banks');
p=reset();p.betaGwentDeckCards[0]=999999;all(p);check(p.betaGwentDeckRecoveryCards[0]===999999,'invalid original record remains quarantined');
for(const count of [-1,0,24,41,999999]){p=reset();p.betaGwentDeckLengths[0]=count;all(p);check(p.betaGwentDeckRecoveryLengths[0]===count,'invalid semantic length remains quarantined');}
p=reset();p.betaGwentDeckLengths[0]=0;p.betaGwentDeckLeaders[0]=0;p.betaGwentDeckFactions[0]=0;all(p);check(p.betaGwentDeckRecoveryCards.length===320,'zeroed header with surviving cards is not a committed deletion');
p=reset();p.betaGwentDeckLengths[0]=41;p.BetaGwentBackupProfile();all(p);check(p.BetaGwentVerifiedBackupBank(facts.get('bg_b2_cur'),{v:new SBetaGwentProfileBackup()}),'invalid length repaired before it can become an empty backup record');
p=reset();p.betaGwentBkA=17;p.betaGwentBkB=29;const b={v:new SBetaGwentProfileBackup()};check(p.BetaGwentVerifiedBackupBank(facts.get('bg_b2_cur'),b),'read verified bank');check(p.betaGwentBkA===17&&p.betaGwentBkB===29,'nested validation preserves running checksum state');
p=reset();p.betaGwentDeckCards=[];p.BetaGwentBackupProfile();const verified={v:new SBetaGwentProfileBackup()};check(p.BetaGwentVerifiedBackupBank(facts.get('bg_b2_cur'),verified),'backup with repair still has a valid checksum');all(p);
p=reset();p.betaGwentDeckCards[0]=999999;p.BetaGwentBackupProfile();check(p.BetaGwentVerifiedBackupBank(facts.get('bg_b2_cur'),{v:new SBetaGwentProfileBackup()}),'semantic repair nested inside backup preserves its checksum');all(p);
p=reset();check(p.BetaGwentClearDeck(3),'explicit deletion');p.betaGwentDeckCards=[];all(p,3);check(!load(p,3).ok,'current committed empty slot never resurrects from older bank');
p=reset();p.betaGwentDeckCards[0]=999999;facts.set('bg_b2_1_done',0);facts.set('bg_b2_2_done',0);check(!load(p,1).ok,'unrecoverable slot is not exposed as valid');for(let s=2;s<=8;s++)check(load(p,s).ok,'other primary slots survive corrupt banks');check(p.betaGwentDeckRecoveryCards[0]===999999,'unrecoverable raw record preserved');check(store(p,1,'Новая колода'),'new save remains usable without any old mirror');all(p);
p=reset();failAt=writes+5;try{p.BetaGwentBackupProfile();}catch(e){check(e.message==='simulated interruption','inject interruption');}failAt=-1;p.betaGwentDeckCards=[];all(p);
p=reset();const hydrated=player(copy(p));all(hydrated);check(hydrated.betaGwentDeckNames[0]==='Моя колода 1','Unicode names survive modeled serialized round trip');
// Full restore exercises the same validator but is allowed to apply collection/settings.
facts.clear();goodFacts.forEach((v,k)=>facts.set(k,v));p=player();check(p.BetaGwentRestoreProfile(),'whole profile restores');all(p);for(let s=9;s<=13;s++)check(load(p,s).ok,'starter override restored');
thePlayer=p;const library=new CBetaGwentDeckLibrary();library.Initialize(true);check(library.FirstEmpty()===0,'all recovered custom slots occupied in actual library');
console.log('REPORT198 '+S({complete:true,checks,actualWitcherScript:true,bankChecksumsValidated:true,nativeSerializationTested:false,scope:'Current WS methods, real catalog/library, modeled field loss and interrupted facts writes'}));
