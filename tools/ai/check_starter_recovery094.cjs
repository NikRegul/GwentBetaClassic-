// Actual profile WS methods are translated above this harness by the runner.
const facts=new Map(),logs=[],failures=[];
let thePlayer=null,writes=0,stopAfter=-1,checks=0;
function FactsSet(k,v){if(writes===stopAfter)throw Error('cut');writes++;facts.set(k,v);}
function FactsRemove(k){facts.delete(k);}
function FactsDoesExist(k){return facts.has(k);}
function FactsQueryLatestValue(k){return facts.get(k)||0;}
function LogChannel(c,m){logs.push(m);}
function StrLen(v){return v.length;}
function StrLeft(v,n){return v.slice(0,n);}
function NameToString(v){return String(v);}
function IntToString(v){return String(v);}
function BetaGwentConsoleFormat(k,n){return 'Deck '+n;}
function BetaGwentConsoleText(){return 'Profile recovery unavailable';}
function EntityHandleSet(h,a){h.stableId=a.stableId;}
function EntityHandleGet(h){return entities.get(h.stableId)||null;}
const entities=new Map(),theGame={GetGuiManager:()=>({ShowNotification(){}})};
const S=JSON.stringify,copy=v=>JSON.parse(S(v));
function working(p){const o=JSON.parse(JSON.stringify(p));delete o.betaGwentStore;delete o.betaGwentStoreText;return JSON.stringify(o);}
function check(v,label){checks++;if(!v)throw Error(label);}
function scenario(label,fn){try{stopAfter=-1;fn();}catch(e){failures.push({label,error:String(e.stack||e)});}finally{stopAfter=-1;}}
function player(data){const p=new W3PlayerWitcher();if(data)Object.assign(p,copy(data));thePlayer=p;return p;}
function saveFacts(){return [...facts];}
function resetFacts(data){facts.clear();for(const [k,v] of data)facts.set(k,v);writes=0;stopAfter=-1;}
function source(){facts.clear();writes=0;const p=player();check(p.BetaGwentEnsureCollection(),'initialize');
 const deck={v:[]};BetaGwentDuelPresetDeck(16,deck);const leader=BetaGwentDuelPreset(16).leaderTemplateId;
 check(p.BetaGwentStoreDeck(1,deck.v,'Моя колода',BetaGwentDuelDefinition(leader).header.factionMask,leader),'store');
 p.betaGwentScraps=431;p.betaGwentKegsUnopened=3;p.betaGwentProgressionSeed=123456;
 p.BetaGwentBackupProfile();return p;}
function view(p){return S([p.betaGwentOwnedIds,p.betaGwentOwnedCopies,p.betaGwentScraps,p.betaGwentKegsUnopened,p.betaGwentKegOffers,p.betaGwentKegAutomatic,p.betaGwentKegAutomaticScraps]);}
function restore(){const p=player();check(p.BetaGwentRestoreProfile(),'recover complete bank');return p;}


function starterData(preset){const d={v:[]};BetaGwentDuelPresetDeck(preset,d);const leader=BetaGwentDuelPreset(preset).leaderTemplateId;return {cards:d.v,leader,faction:BetaGwentDuelDefinition(leader).header.factionMask};}
function put(p,slot,preset=16,title='Стартовая — ёж '+slot){const d=starterData(preset);return p.BetaGwentStoreDeck(slot,d.cards,title,d.faction,d.leader);}
function get(p,slot){const c={v:[]},n={v:''},f={v:0},l={v:0};return {ok:p.BetaGwentLoadDeck(slot,c,n,f,l),cards:c.v,title:n.v,faction:f.v,leader:l.v};}
function rich(){const p=source();for(let slot=9;slot<=13;slot++)check(put(p,slot,16+slot-9),'save starter '+slot);p.BetaGwentBackupProfile();return p;}
function starterView(p){return S([p.betaGwentStarterDeckNames,p.betaGwentStarterDeckLeaders,p.betaGwentStarterDeckFactions,p.betaGwentStarterDeckLengths,p.betaGwentStarterDeckCards]);}
scenario('schema0 surviving arrays: store does not clear other overrides',()=>{
 const p=rich(),before=Array.from({length:5},(_,i)=>get(p,9+i));p.betaGwentStarterDeckSchema=0;
 check(put(p,9,18,'Изменённая первая'),'edit after schema loss');for(let slot=10;slot<=13;slot++)check(S(get(p,slot))===S(before[slot-9]),'other named override retained '+slot);
 check(p.betaGwentStarterDeckRecoverySchema===1&&p.betaGwentStarterDeckRecoveryOriginalSchema===0,'original schema quarantined');
 check(p.betaGwentStarterDeckRecoveryNames[1]===before[1].title,'original Unicode name quarantined');
});
scenario('schema0 surviving arrays: backups retain all overrides',()=>{
 const p=rich(),expected=starterView(p);p.betaGwentStarterDeckSchema=0;p.BetaGwentBackupProfile();p.BetaGwentBackupProfile();
 check(starterView(p)===expected,'backup repairs schema without changing slots');for(const bank of [1,2])for(let slot=9;slot<=13;slot++)check(facts.get('bg_b2_'+bank+'_d'+slot+'_n')>=25,'both bank records survive '+bank+'/'+slot);
});
scenario('every truncated or extended starter field recovers',()=>{
 const p=rich(),saved=copy(p),oldFacts=saveFacts(),expected=Array.from({length:5},(_,i)=>get(p,9+i));
 for(const field of ['betaGwentStarterDeckNames','betaGwentStarterDeckLeaders','betaGwentStarterDeckFactions','betaGwentStarterDeckLengths','betaGwentStarterDeckCards'])for(const length of [0,1,4,6,199,201]){
  resetFacts(oldFacts);const q=player(saved);q[field]=Array.from({length},(_,i)=>q[field][i]??(field.endsWith('Names')?'extra':0));
  for(let slot=9;slot<=13;slot++){const actual=get(q,slot);check(actual.ok&&S(actual.cards)===S(expected[slot-9].cards)&&actual.leader===expected[slot-9].leader,'exact valid slot recovered '+field+'/'+length+'/'+slot);if(field!=='betaGwentStarterDeckNames'||length>slot-9)check(actual.title===expected[slot-9].title,'surviving name kept');}
  check(q.betaGwentStarterDeckRecoverySchema===1,'fragments quarantined');check(q.betaGwentStarterDeckRecoveryCards.length===(field.endsWith('Cards')?length:200),'raw original card array retained');
 }
});
scenario('whole collection restore also repairs partial starter arrays',()=>{
 const p=rich(),expected=Array.from({length:5},(_,i)=>get(p,9+i));p.betaGwentStarterDeckNames.pop();p.betaGwentCollectionSchema=0;p.betaGwentOwnedIds=[];p.betaGwentOwnedCopies=[];
 check(p.BetaGwentRestoreProfile(),'collection restored');for(let slot=9;slot<=13;slot++){const actual=get(p,slot);check(actual.ok&&S(actual.cards)===S(expected[slot-9].cards),'starter survives whole profile restore');if(slot<13)check(actual.title===expected[slot-9].title,'surviving name wins');}
});
scenario('empty primary slot and committed bank reset cannot resurrect',()=>{
 const p=rich();check(p.BetaGwentClearDeck(10),'clear override');p.betaGwentStarterDeckSchema=0;check(!get(p,10).ok,'explicit primary reset preserved');
 check(p.betaGwentStarterDeckLengths[1]===0&&p.betaGwentStarterDeckLeaders[1]===0,'empty header intact');
 p.BetaGwentBackupProfile();p.betaGwentStarterDeckCards=[];check(!get(p,10).ok,'latest committed bank reset blocks older mirror');for(const slot of [9,11,12,13])check(get(p,slot).ok,'other starters survive reset');
});
scenario('semantic corrupt cards repair from whole verified bank',()=>{
 const p=rich(),expected=get(p,11);p.betaGwentStarterDeckCards[80]=999999;const actual=get(p,11);check(actual.ok&&S(actual.cards)===S(expected.cards),'invalid card replaced from verified bank');check(p.betaGwentStarterDeckRecoveryCards[80]===999999,'invalid raw card quarantined');
});
scenario('invalid banks cannot inject starter overrides',()=>{
 const p=rich(),good=starterData(18),cur=facts.get('bg_b2_cur'),prefix='bg_b2_'+cur+'_d9_';facts.set(prefix+'n',good.cards.length);facts.set(prefix+'f',good.faction);facts.set(prefix+'l',good.leader);good.cards.forEach((id,i)=>facts.set(prefix+i,id));facts.set('bg_b2_'+cur+'_sa',-1);
 const expected=get(p,9);p.betaGwentStarterDeckCards=[];const actual=get(p,9);check(actual.ok&&S(actual.cards)===S(expected.cards),'bad-checksum bank cannot change recovery');
});
scenario('unknown schemas do not mutate primary or mirrors',()=>{
 const p=rich();p.betaGwentStarterDeckSchema=99;const primary=working(p),mirror=S(saveFacts());check(!get(p,9).ok&&!put(p,9)&&!p.BetaGwentClearDeck(9),'unknown schema operations rejected');p.BetaGwentBackupProfile();check(working(p)===primary&&S(saveFacts())===mirror,'future schema preserved');
});
scenario('no bank: other primary slots survive unrecoverable damage',()=>{
 const p=rich(),raw=S(p.betaGwentStarterDeckCards);facts.clear();p.betaGwentStarterDeckCards[0]=999999;check(!get(p,9).ok,'unrecoverable override not exposed');for(let slot=10;slot<=13;slot++)check(get(p,slot).ok,'intact primary starter survives');check(p.betaGwentStarterDeckRecoveryCards[0]===999999,'unrecoverable raw record preserved');check(put(p,9,16,'Новая после ремонта'),'store after repair');
});
console.log('STARTER_RECOVERY094 '+S({complete:failures.length===0,checks,failures,actualWitcherScript:true,nativeSerializationTested:false}));
if(failures.length)process.exitCode=1;
