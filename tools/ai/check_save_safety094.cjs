// Actual profile WS methods are translated above this harness by the runner.
const facts=new Map(),logs=[],failures=[];
let thePlayer=null,writes=0,stopAfter=-1,checks=0,int16=false;
// int16=true models Next-Gen 5.x facts, which keep only signed 16-bit values.
function FactsSet(k,v){if(writes===stopAfter)throw Error('cut');writes++;facts.set(k,int16?((v<<16)>>16):v);}
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
function working(p){const o=copy(p);delete o.betaGwentStore;delete o.betaGwentStoreText;return S(o);}
// Next-Gen save model: only the four store fields are written; every other field resets.
const STORE_FIELDS=['betaGwentStore','betaGwentStoreText','betaGwentRewardActors','betaGwentRewardedQuests'];
function reload(p){p.BetaGwentStoreCommit();const q=new W3PlayerWitcher();for(const f of STORE_FIELDS)q[f]=copy(p[f]);thePlayer=q;q.BetaGwentStoreLoad();return q;}
function restore(){const p=player();check(p.BetaGwentRestoreProfile(),'recover complete bank');return p;}

scenario('lost or corrupt current-bank pointer',()=>{
 const p=source(),snapshot=saveFacts(),expected=view(p);
 for(const value of [0,-1,3,99]){resetFacts(snapshot);facts.set('bg_b2_cur',value);const r=restore();check(view(r)===expected,'newest verified bank survives pointer '+value);}
});
scenario('first backup interrupted after every facts write',()=>{
 const p=source(),primary=copy(p);facts.clear();writes=0;p.BetaGwentBackupProfile();const total=writes;
 for(let cut=0;cut<=total;cut++){
  resetFacts([]);const q=player(primary);stopAfter=cut;
  try{q.BetaGwentBackupProfile();}catch(e){check(e.message==='cut','only injected exception');}finally{stopAfter=-1;}
  const hasComplete=[1,2].some(b=>facts.get('bg_b2_'+b+'_done')>0);
  if(hasComplete){const r=restore();check(view(r)===view(q),'completed first bank recoverable at cut '+cut);}
 }
});
scenario('existing backup interrupted at every facts write',()=>{
 const p=source(),oldFacts=saveFacts(),primary=copy(p),before=view(p);
 p.betaGwentScraps=777;writes=0;p.BetaGwentBackupProfile();const total=writes;
 for(let cut=0;cut<=total;cut++){
  resetFacts(oldFacts);const q=player(primary);q.betaGwentScraps=777;const after=view(q);stopAfter=cut;
  try{q.BetaGwentBackupProfile();}catch(e){check(e.message==='cut','only injected exception');}finally{stopAfter=-1;}
  const r=restore();check(view(r)===before||view(r)===after,'atomic old-or-new profile at cut '+cut);
 }
});
scenario('write protects sole verified bank when pointer is lost',()=>{
 const p=source();let cur=facts.get('bg_b2_cur');facts.set('bg_b2_'+(3-cur)+'_done',0);
 const initial=saveFacts(),primary=copy(p),expected=view(p);
 for(const bad of [0,3]){
  resetFacts(initial);facts.set('bg_b2_cur',bad);const q=player(primary);q.betaGwentScraps=888;stopAfter=5;
  try{q.BetaGwentBackupProfile();}catch(e){check(e.message==='cut','injected early cut');}finally{stopAfter=-1;}
  const r=restore();check(view(r)===expected,'only valid bank remains untouched');
 }
});
scenario('each single fact in current bank is damaged or lost',()=>{
 const p=source(),old=saveFacts(),cur=facts.get('bg_b2_cur'),prefix='bg_b2_'+cur+'_';
 const other=3-cur;facts.set('bg_b2_cur',other);const fallback=view(restore());resetFacts(old);
 for(const [key,value] of old.filter(([key])=>key.startsWith(prefix))){
  for(const remove of [false,true]){
   resetFacts(old);if(remove)facts.delete(key);else facts.set(key,value+1);
   const q=restore();check(view(q)===fallback||view(q)===view(p),'only verified whole snapshot after fault '+key);
  }
 }
});
scenario('global generation loss and stale pointer do not erase bank history',()=>{
 const p=source(),old=saveFacts(),cur=facts.get('bg_b2_cur'),generation=facts.get('bg_b2_'+cur+'_gen');
 for(const value of [-1,0,2147483647]){
  resetFacts(old);facts.set('bg_b2_gen',value);p.BetaGwentBackupProfile();
  check(facts.get('bg_b2_gen')===generation+1,'generation comes from verified banks');
 }
});
scenario('unknown future schemas preserve fields and mirror',()=>{
 for(const field of ['betaGwentCollectionSchema','betaGwentDeckSchema','betaGwentStarterDeckSchema','betaGwentNewCardsSchema']){
  const p=source();p[field]=99;const before=working(p),old=saveFacts();p.BetaGwentBackupProfile();
  check(working(p)===before,'unknown schema fields intact '+field);
  const q=reload(p);check(q[field]===99,'unknown schema value survives the store '+field);check(S(saveFacts())===S(old),'unknown schema mirror intact '+field);
 }
});
scenario('collection-only loss preserves surviving newer deck and Unicode name',()=>{
 const p=source(),old=saveFacts(),deck={v:[]};BetaGwentDuelPresetDeck(17,deck);const leader=BetaGwentDuelPreset(17).leaderTemplateId;
 check(p.BetaGwentStoreDeck(1,deck.v,'Новая колода — ёж',BetaGwentDuelDefinition(leader).header.factionMask,leader),'save newer deck');
 const expected=S([p.betaGwentDeckCards,p.betaGwentDeckNames,p.betaGwentDeckLeaders,p.betaGwentDeckFactions]);
 resetFacts(old);p.betaGwentCollectionSchema=0;p.betaGwentOwnedIds=[];p.betaGwentOwnedCopies=[];
 check(p.BetaGwentRestoreProfile(),'restore collection-only loss');
 check(S([p.betaGwentDeckCards,p.betaGwentDeckNames,p.betaGwentDeckLeaders,p.betaGwentDeckFactions])===expected,'surviving primary decks and names take precedence over mirror');
});
scenario('collection-only restore respects surviving deletions and starter reset',()=>{
 const p=source(),deck={v:[]};BetaGwentDuelPresetDeck(17,deck);const leader=BetaGwentDuelPreset(17).leaderTemplateId;
 check(p.BetaGwentStoreDeck(9,deck.v,'Стартовая колода',BetaGwentDuelDefinition(leader).header.factionMask,leader),'save starter override');
 const old=saveFacts();check(p.BetaGwentClearDeck(1)&&p.BetaGwentClearDeck(9),'commit deletions in primary');
 const expected=S([p.betaGwentDeckCards,p.betaGwentDeckNames,p.betaGwentStarterDeckCards,p.betaGwentStarterDeckNames]);
 resetFacts(old);p.betaGwentCollectionSchema=0;p.betaGwentOwnedIds=[];p.betaGwentOwnedCopies=[];
 check(p.BetaGwentRestoreProfile(),'restore with intact primary empty slots');
 check(S([p.betaGwentDeckCards,p.betaGwentDeckNames,p.betaGwentStarterDeckCards,p.betaGwentStarterDeckNames])===expected,'older mirrored decks do not resurrect');
});
scenario('ownership restore leaves unknown or surviving auxiliary schema intact',()=>{
 for(const schema of [1,99]){
  const p=source();p.betaGwentNewCardsSchema=schema;p.betaGwentNewCardIds=[112101];
  p.betaGwentCollectionSchema=0;p.betaGwentOwnedIds=[];p.betaGwentOwnedCopies=[];
  check(p.BetaGwentRestoreProfile(),'restore ownership independently');
  check(p.betaGwentNewCardsSchema===schema&&S(p.betaGwentNewCardIds)==='[112101]','auxiliary data not silently replaced');
 }
});
scenario('legacy mirror preserves newer primary decks and auxiliary state',()=>{
 const p=source(),ids=p.betaGwentOwnedIds.slice(),copies=p.betaGwentOwnedCopies.slice(),oldDeck={v:[]},deck={v:[]};
 BetaGwentDuelPresetDeck(16,oldDeck);BetaGwentDuelPresetDeck(17,deck);const leader=BetaGwentDuelPreset(17).leaderTemplateId;
 check(p.BetaGwentStoreDeck(1,deck.v,'Новая колода из старого сейва',BetaGwentDuelDefinition(leader).header.factionMask,leader),'new deck saved');
 const expected=S([p.betaGwentDeckCards,p.betaGwentDeckNames,p.betaGwentDeckLeaders,p.betaGwentDeckFactions]);
 resetFacts([]);facts.set('bg_bk_schema',1);facts.set('bg_bk_cn',ids.length+1);
 ids.forEach((id,i)=>{facts.set('bg_bk_ci_'+i,id);facts.set('bg_bk_cc_'+i,copies[i]);});
 facts.set('bg_bk_d1_n',oldDeck.v.length+1);facts.set('bg_bk_d1_f',BetaGwentDuelDefinition(BetaGwentDuelPreset(16).leaderTemplateId).header.factionMask);
 facts.set('bg_bk_d1_l',BetaGwentDuelPreset(16).leaderTemplateId);oldDeck.v.forEach((id,i)=>facts.set('bg_bk_d1_'+i,id));
 p.betaGwentNewCardsSchema=99;p.betaGwentNewCardIds=[112101];p.betaGwentCollectionSchema=0;p.betaGwentOwnedIds=[];p.betaGwentOwnedCopies=[];
 check(p.BetaGwentRestoreProfile(),'legacy profile restored');
 check(S([p.betaGwentDeckCards,p.betaGwentDeckNames,p.betaGwentDeckLeaders,p.betaGwentDeckFactions])===expected,'legacy cannot overwrite newer primary deck');
 check(p.betaGwentNewCardsSchema===99&&S(p.betaGwentNewCardIds)==='[112101]','legacy preserves unknown auxiliary schema');
});
scenario('known damaged ownership recovers from verified bank with raw quarantine',()=>{
 const p=source(),old=saveFacts(),primary=copy(p),expected=view(p);
 for(const damage of ['schema','ids','copies','empty','duplicate','negative','unknown']){
  resetFacts(old);const q=player(primary);
  if(damage==='schema')q.betaGwentCollectionSchema=0;
  if(damage==='ids')q.betaGwentOwnedIds.pop();
  if(damage==='copies')q.betaGwentOwnedCopies.pop();
  if(damage==='empty'){q.betaGwentOwnedIds=[];q.betaGwentOwnedCopies=[];}
  if(damage==='duplicate')q.betaGwentOwnedIds[1]=q.betaGwentOwnedIds[0];
  if(damage==='negative')q.betaGwentOwnedCopies[0]=-1;
  if(damage==='unknown')q.betaGwentOwnedIds[0]=999999;
  const rawIds=S(q.betaGwentOwnedIds),rawCopies=S(q.betaGwentOwnedCopies);
  check(q.BetaGwentEnsureCollection(),'known damaged ownership repaired '+damage);
  check(view(q)===expected,'exact known ownership/economy recovered '+damage);
  check(q.betaGwentCollectionRecoverySchema===1&&S(q.betaGwentCollectionRecoveryIds)===rawIds&&S(q.betaGwentCollectionRecoveryCopies)===rawCopies,'raw damaged ownership preserved '+damage);
 }
});
scenario('unrecoverable or unknown ownership never silently becomes a starter collection',()=>{
 const p=source();p.betaGwentOwnedCopies.pop();const ids=S(p.betaGwentOwnedIds),copies=S(p.betaGwentOwnedCopies);resetFacts([]);
 check(!p.BetaGwentEnsureCollection(),'missing mirror cannot certify a partial collection');
 check(S(p.betaGwentOwnedIds)===ids&&S(p.betaGwentOwnedCopies)===copies,'unrecoverable primary retained');
 p.betaGwentCollectionSchema=99;const before=S(p),old=saveFacts();
 check(!p.BetaGwentEnsureCollection()&&S(p)===before&&S(saveFacts())===S(old),'unknown future ownership untouched');
});
scenario('paid keg resumes without charge or reroll and choice cannot repeat',()=>{
 const p=source();check(p.BetaGwentOpenKeg(),'open paid keg');const reservation=view(p),seed=p.betaGwentProgressionSeed;
 check(p.BetaGwentKegCount()===2&&p.betaGwentKegOffers.length===3&&p.betaGwentKegAutomatic.length===4,'one keg reserved');
 check(p.BetaGwentOpenKeg()&&view(p)===reservation&&p.betaGwentProgressionSeed===seed,'reopen cannot reroll');
 p.BetaGwentBackupProfile();const r=restore();check(view(r)===reservation,'reservation and grants restored together');
 const id=r.betaGwentKegOffers[0];check(r.BetaGwentChooseKeg(id),'choose offered card');const settled=view(r);
 check(!r.BetaGwentChooseKeg(id)&&view(r)===settled,'double submission cannot issue card twice');
 r.BetaGwentBackupProfile();check(view(restore())===settled,'choice cleared in next backup');
});
scenario('paid choice is preserved when ownership is unavailable',()=>{
 for(const damage of ['future','missing','unknown-offer','cleanup']){
  const p=source();check(p.BetaGwentOpenKeg(),'open reservation');let id=p.betaGwentKegOffers[0];
  if(damage==='future')p.betaGwentCollectionSchema=99;
  if(damage==='missing'){p.betaGwentOwnedCopies.pop();resetFacts([]);}
  if(damage==='unknown-offer'){id=999999;p.betaGwentKegOffers=[id];}
  if(damage==='cleanup')p.betaGwentCleanupPending090=true;
  const before=view(p);check(!p.BetaGwentChooseKeg(id),'unavailable choice rejected '+damage);
  check(view(p)===before,'paid choice/copies/balance remain unchanged '+damage);
 }
 const p=source();check(p.BetaGwentOpenKeg(),'new valid reservation');p.BetaGwentBackupProfile();const id=p.betaGwentKegOffers[0];p.betaGwentOwnedCopies.pop();
 check(p.BetaGwentChooseKeg(id)&&!p.BetaGwentKegPending(),'verified ownership recovery permits exactly one award');
});
scenario('craft failures preserve balance and collection',()=>{
 const p=source();p.betaGwentScraps=0;const before=view(p);
 check(!p.BetaGwentCraft(999999)&&view(p)===before,'unknown card cannot charge');
 const ids={v:[]};BetaGwentDuelCollection(ids);const missing=ids.v.find(id=>p.BetaGwentOwned(id)<BetaGwentCollectionCap(id));
 check(missing>0&&!p.BetaGwentCraft(missing)&&view(p)===before,'insufficient balance cannot grant');
 p.betaGwentScraps=1000;const prior=p.BetaGwentOwned(missing),cost=BetaGwentCraftCost(missing);
 check(p.BetaGwentCraft(missing)&&p.BetaGwentOwned(missing)===prior+1&&p.BetaGwentScraps()===1000-cost,'successful craft changes copies and balance together');
 p.BetaGwentBackupProfile();check(view(restore())===view(p),'crafted state restores');
});
scenario('cleanup latch blocks profile recreation and grants through public entry points',()=>{
 const p=source();p.betaGwentCleanupPending090=true;const before=view(p),old=saveFacts();
 check(!p.BetaGwentEnsureCollection()&&!p.BetaGwentOpenKeg()&&!p.BetaGwentCraft(112101),'cleanup blocks collection/economy');
 p.BetaGwentBackupProfile();p.BetaGwentAddKegs(3);
 check(view(p)===before&&S(saveFacts())===S(old),'cleanup cannot recreate mirror');
});

// ---- 0.9.4 single store (Next-Gen keeps only the first 45 saved fields) ----
const FULL=['betaGwentCollectionSchema','betaGwentOwnedIds','betaGwentOwnedCopies','betaGwentProgressionSeed','betaGwentRewardedNpcs',
 'betaGwentRewardActorWins','betaGwentRewardedQuests','betaGwentStarterSetRevision','betaGwentNewCardsSchema','betaGwentNewCardIds',
 'betaGwentAnimationTempo','betaGwentReducedEffects','betaGwentDifficulty','betaGwentAiPause','betaGwentDeckSchema','betaGwentDeckNames',
 'betaGwentDeckLeaders','betaGwentDeckFactions','betaGwentDeckLengths','betaGwentDeckCards','betaGwentPreferredDeck','betaGwentStarterDeckSchema',
 'betaGwentStarterDeckNames','betaGwentStarterDeckLeaders','betaGwentStarterDeckFactions','betaGwentStarterDeckLengths','betaGwentStarterDeckCards',
 'betaGwentKegAutomatic','betaGwentKegOffers','betaGwentKegAutomaticScraps','betaGwentKegsUnopened','betaGwentOpponentBag','betaGwentOpponentRecent',
 'betaGwentOpponentPoolSize','betaGwentCleanupPending090','betaGwentScraps','betaGwentRewardActors'];
function full(p){return S(FULL.map(f=>p[f]===undefined?null:p[f]));}
function reloadRaw(p){const q=new W3PlayerWitcher();for(const f of STORE_FIELDS)q[f]=copy(p[f]);thePlayer=q;q.BetaGwentStoreLoad();return q;}
function rich(){
 const p=source(),deck={v:[]};BetaGwentDuelPresetDeck(17,deck);const leader=BetaGwentDuelPreset(17).leaderTemplateId;
 check(p.BetaGwentStoreDeck(9,deck.v,'Стартовая — правка',BetaGwentDuelDefinition(leader).header.factionMask,leader),'starter override');
 check(p.BetaGwentStoreDeck(3,deck.v,'Третья',BetaGwentDuelDefinition(leader).header.factionMask,leader),'third deck');
 p.BetaGwentSetPresentation(15,true);p.BetaGwentSetDifficulty(2);p.BetaGwentSetAiPause(3);p.BetaGwentRememberDeck(3);
 p.betaGwentKegsUnopened=2;check(p.BetaGwentOpenKeg(),'open keg');
 p.betaGwentOpponentBag=[21,22,23];p.betaGwentOpponentRecent=[30,31];p.betaGwentOpponentPoolSize=46;
 p.betaGwentRewardedNpcs=[-12345,77];p.betaGwentRewardActorWins=[2];p.betaGwentRewardActors=[{stableId:'npc-a'}];p.betaGwentRewardedQuests=['gwent_q1'];
 p.betaGwentNewCardIds=[p.betaGwentOwnedIds[0]];p.betaGwentProgressionSeed=2147483000;p.betaGwentScraps=123456;
 p.BetaGwentStoreCommit();return p;}
scenario('store alone restores the whole profile (45-field save model)',()=>{
 const p=rich(),q=reload(p);check(full(q)===full(p),'every profile field round-trips through the store');
 check(q.BetaGwentEnsureCollection()&&full(q)===full(p),'normal entry after load keeps the profile');
 const r=reload(q);check(full(r)===full(p),'second save/load cycle is stable');
 check(q.betaGwentStore[5]>=p.betaGwentStore[5],'commit number advances');
});
scenario('legacy fields from an older save migrate into the store',()=>{
 const p=rich(),legacy=copy(p);legacy.betaGwentStore=[];legacy.betaGwentStoreText=[];legacy.betaGwentStoreLoaded=false;
 const q=player(legacy);check(q.BetaGwentEnsureCollection(),'legacy profile accepted');
 check(q.betaGwentStore.length>6,'store created from legacy fields');
 const r=reloadRaw(q);check(full(r)===full(p),'migrated store restores the legacy profile');
});
scenario('every mutation reaches the store without an explicit backup',()=>{
 const ops=[
  ['scraps',p=>p.BetaGwentAddScraps(7)],['kegs',p=>p.BetaGwentAddKegs(2)],['difficulty',p=>p.BetaGwentSetDifficulty(1)],
  ['pause',p=>p.BetaGwentSetAiPause(4)],['presentation',p=>p.BetaGwentSetPresentation(20,false)],['preferred',p=>p.BetaGwentRememberDeck(5)],
  ['seen',p=>{p.betaGwentNewCardIds=[p.betaGwentOwnedIds[1]];p.BetaGwentStoreCommit();p.BetaGwentCardSeen(p.betaGwentOwnedIds[1]);}],
  ['open keg',p=>{p.betaGwentKegsUnopened=1;p.BetaGwentStoreCommit();check(p.BetaGwentOpenKeg(),'open');}],
  ['choose keg',p=>{p.betaGwentKegsUnopened=1;check(p.BetaGwentOpenKeg(),'open');check(p.BetaGwentChooseKeg(p.betaGwentKegOffers[0]),'choose');}],
  ['clear deck',p=>check(p.BetaGwentClearDeck(1),'clear')]];
 for(const [label,op] of ops){const p=source();op(p);const q=reloadRaw(p);check(full(q)===full(p),'store current after '+label);}
});
scenario('damaged store falls back to the verified facts bank',()=>{
 const p=source(),expected=view(p);
 for(const damage of ['checksum','length','header']){
  const d=copy(p);if(damage==='checksum')d.betaGwentStore[10]+=1;if(damage==='length')d.betaGwentStore.pop();if(damage==='header')d.betaGwentStore[0]=1;
  const q=reloadRaw(d);check(q.BetaGwentEnsureCollection()&&view(q)===expected,'bank recovery after store damage '+damage);
 }
});
scenario('store from a newer format is never overwritten',()=>{
 const p=source(),d=copy(p);d.betaGwentStore[1]=BetaGwentStoreFormat()+1;const before=S(d.betaGwentStore);
 const q=reloadRaw(d);q.BetaGwentAddScraps(5);q.BetaGwentStoreCommit();check(S(q.betaGwentStore)===before,'future store kept read-only');
});
scenario('cleanup latch survives through the store',()=>{
 const p=source();p.betaGwentCleanupPending090=true;p.BetaGwentStoreCommit();const q=reloadRaw(p);
 check(q.BetaGwentCleanupPending()&&!q.BetaGwentEnsureCollection(),'latch restored and still blocks');
});
scenario('facts banks survive the 16-bit Next-Gen facts model',()=>{
 int16=true;
 try{
  const p=rich();resetFacts([]);p.BetaGwentBackupProfile();
  for(const [k,v] of facts)check(v>=-32768&&v<=32767,'fact fits 16 bits '+k);
  const expected=view(p),q=player();q.betaGwentStoreLoaded=true;q.betaGwentStoreWritable=true;thePlayer=q;
  check(q.BetaGwentRestoreProfile()&&view(q)===expected,'bank restore with 16-bit facts');
  check(S(q.betaGwentDeckCards)===S(p.betaGwentDeckCards),'decks restore with 16-bit facts');
  check(q.betaGwentProgressionSeed===p.betaGwentProgressionSeed,'31-bit seed restores from 15-bit parts');
 }finally{int16=false;}
});
scenario('old 16-bit-truncated banks are rejected, not misread',()=>{
 const p=source();resetFacts([]);int16=true;
 try{for(const [k,v] of (()=>{const s=new Map();const keep=int16;int16=false;resetFacts([]);p.BetaGwentBackupProfile();for(const [a,b] of facts)s.set(a,b);int16=keep;return s;})()){}}finally{int16=false;}
 // Simulate a pre-0.9.4 bank written as single facts, then truncated by the engine.
 const legacy=saveFacts().filter(([k])=>!k.endsWith('_m')&&!k.endsWith('_x'));
 resetFacts(legacy.map(([k,v])=>[k,(v<<16)>>16]));
 const q=player();q.betaGwentStoreLoaded=true;q.betaGwentStoreWritable=true;thePlayer=q;check(!q.BetaGwentRestoreProfile(),'truncated legacy bank rejected');
});

scenario('review: failed read cannot authorize an autosave; verified recovery preserves rejected bytes',()=>{
 const p=rich(),d=copy(p);d.betaGwentStore[0]=1;const q=reloadRaw(d),raw=S(q.betaGwentStore),text=S(q.betaGwentStoreText);
 check(!q.BetaGwentStoreLoad(),'repeat failed read remains a failure');q.BetaGwentStoreCommit();
 check(S(q.betaGwentStore)===raw&&S(q.betaGwentStoreText)===text,'autosave before recovery does not replace raw store');
 check(q.BetaGwentEnsureCollection(),'valid facts recover profile');check(q.betaGwentStoreRecoverySchema===1&&S(q.betaGwentStoreRecoveryData)===raw&&S(q.betaGwentStoreRecoveryText)===text,'rejected source preserved during recovery');
 const r=reload(q);check(S(r.betaGwentStoreRecoveryData)===raw&&S(r.betaGwentStoreRecoveryText)===text,'raw evidence survives next save/load');
 resetFacts([]);const u=reloadRaw(d);const before=S(u.betaGwentStore);check(!u.BetaGwentEnsureCollection(),'unrecoverable rejected store cannot initialize starters');u.BetaGwentStoreCommit();check(S(u.betaGwentStore)===before,'unrecoverable source preserved');
});
scenario('review: all raw recovery fields survive store-only serialization',()=>{
 const p=rich();resetFacts([]);p.betaGwentDeckCards[0]=999999;const c={v:[]},n={v:''},f={v:0},l={v:0};check(!p.BetaGwentLoadDeck(1,c,n,f,l),'unrecoverable slot quarantined');
 p.betaGwentStarterDeckCards[0]=999998;check(!p.BetaGwentLoadDeck(9,c,n,f,l),'starter original quarantined');
 p.betaGwentOwnedCopies.pop();check(!p.BetaGwentEnsureCollection(),'collection fragments quarantined');
 const fields=Object.keys(p).filter(k=>/^betaGwent(?:Collection|Deck|StarterDeck)Recovery/.test(k)),before=S(fields.map(k=>p[k]));
 const q=reload(p);check(S(fields.map(k=>q[k]))===before,'all recovery arrays, metadata and Unicode names survive');
});
scenario('review: unknown format blocks collection, currency, kegs and setters',()=>{
 const p=rich(),d=copy(p);d.betaGwentStore[1]=BetaGwentStoreFormat()+1;const q=reloadRaw(d),before=S(q.betaGwentStore),text=S(q.betaGwentStoreText),mirror=S(saveFacts());
 check(!q.BetaGwentEnsureCollection(),'future format refuses gameplay profile');const state=full(q);
 q.BetaGwentAddKegs(2);q.BetaGwentAddScraps(27);q.BetaGwentSetDifficulty(1);q.BetaGwentSetPresentation(20,false);q.BetaGwentRememberDeck(5);q.BetaGwentBackupProfile();
 check(full(q)===state,'future format cannot create apparently saved progress');check(S(q.betaGwentStore)===before&&S(q.betaGwentStoreText)===text&&S(saveFacts())===mirror,'future source and mirrors untouched');
});
scenario('review: lazy first mutation loads authoritative fields before applying changes',()=>{
 for(const [name,action,field,delta] of [['kegs',p=>p.BetaGwentAddKegs(2),'betaGwentKegsUnopened',2],['scraps',p=>p.BetaGwentAddScraps(7),'betaGwentScraps',7]]){
  const p=rich(),q=new W3PlayerWitcher();for(const k of STORE_FIELDS)q[k]=copy(p[k]);thePlayer=q;action(q);
  check(q[field]===p[field]+delta,'first '+name+' applies after load');check(reloadRaw(q)[field]===q[field],'first '+name+' saved');
 }
});
scenario('review: text count, pair, length and commit are validated before applying fields',()=>{
 const p=rich();
 for(const kind of ['missing','pair','length','commit']){
  const d=copy(p);if(kind==='missing')d.betaGwentStoreText=[];if(kind==='pair')d.betaGwentStoreText[1]+='x';if(kind==='length'){d.betaGwentStoreText[1]+='x';d.betaGwentStoreText[2]+='x';}if(kind==='commit')d.betaGwentStoreText[0]='not-this-commit';
  const q=new W3PlayerWitcher();for(const k of STORE_FIELDS)q[k]=copy(d[k]);thePlayer=q;check(!q.BetaGwentStoreLoad(),'bad text rejected '+kind);check(q.betaGwentDeckNames.length===0&&q.betaGwentOwnedIds.length===0,'rejection applied no partial fields');
 }
});
scenario('review: format 1 migrates to format 2 without changing profile',()=>{
 const p=rich(),d=copy(p),old=[],scalars=[];let pos=6;
 while(pos<d.betaGwentStore.length){const tag=d.betaGwentStore[pos],n=d.betaGwentStore[pos+1],v=d.betaGwentStore.slice(pos+2,pos+2+n);pos+=2+n;if(tag>19)continue;const values=tag===1?v.slice(0,17):v;old.push(tag,values.length,...values);}
 let a=1,b=0;for(let v of old){v%=65521;if(v<0)v+=65521;a=(a+v)%65521;b=(b+a)%65521;}d.betaGwentStore=[4719,1,old.length,a,b,p.betaGwentStore[5],...old];d.betaGwentStoreText=p.betaGwentDeckNames.concat(p.betaGwentStarterDeckNames);
 const q=reloadRaw(d);check(full(q)===full(p),'format1 complete profile read');const r=reload(q);check(r.betaGwentStore[1]===2&&full(r)===full(p),'format1 upgraded with profile unchanged');
});
scenario('reported log: surviving headers, missing deck arrays and empty banks retain fragments',()=>{
 const p=rich(),names=S(p.betaGwentDeckNames),leaders=S(p.betaGwentDeckLeaders);p.betaGwentDeckFactions=[];p.betaGwentDeckLengths=[];p.betaGwentDeckCards=[];
 facts.set('bg_b2_1_cn',0);facts.set('bg_b2_2_cn',0);const c={v:[]},n={v:''},f={v:0},l={v:0};
 check(!p.BetaGwentLoadDeck(1,c,n,f,l),'missing compositions cannot be invented');check(S(p.betaGwentDeckRecoveryNames)===names&&S(p.betaGwentDeckRecoveryLeaders)===leaders,'surviving reported headers quarantined');
 const q=reload(p);check(S(q.betaGwentDeckRecoveryNames)===names&&S(q.betaGwentDeckRecoveryLeaders)===leaders,'reported fragments survive save-only store');
});
scenario('review: recovery must fit a committed envelope before allowing progress',()=>{
 for(const kind of ['text','payload']){
  const p=rich(),d=copy(p);if(kind==='text')d.betaGwentStoreText=Array(32769).fill('x');else d.betaGwentStore=Array(999990).fill(0);
  if(kind==='text')d.betaGwentStore[0]=1;const q=reloadRaw(d),raw=S(q.betaGwentStore),text=S(q.betaGwentStoreText);
  check(!q.BetaGwentEnsureCollection(),'unserializable recovery rejected '+kind);check(!q.BetaGwentStoreReady(),'cannot authorize mutations '+kind);
  const kegs=q.betaGwentKegsUnopened,scraps=q.betaGwentScraps;q.BetaGwentAddKegs(2);q.BetaGwentAddScraps(9);q.BetaGwentStoreCommit();
  check(q.betaGwentKegsUnopened===kegs&&q.betaGwentScraps===scraps,'no unsaved progress '+kind);
  check(S(q.betaGwentStore)===raw&&S(q.betaGwentStoreText)===text,'oversized rejected source intact '+kind);
 }
});
scenario('presentation: cold menu reads restore the stored preferences',()=>{
 for(const tempo of [10,15,20])for(const reduced of [false,true]){
  const p=source();p.BetaGwentSetPresentation(tempo,reduced);check(p.BetaGwentAnimationTempo()===tempo&&p.BetaGwentReducedEffects()===reduced,'live presentation preferences accepted');
  let q=new W3PlayerWitcher();for(const f of STORE_FIELDS)q[f]=copy(p[f]);thePlayer=q;
  // No explicit StoreLoad/EnsureCollection: a new menu calls these getters first.
  check(q.BetaGwentAnimationTempo()===tempo&&q.BetaGwentReducedEffects()===reduced,'cold getters retain tempo and effects');
  check(q.BetaGwentAnimationTempo()===tempo&&q.BetaGwentReducedEffects()===reduced,'second battle keeps preferences');
  check(!q.BetaGwentSetPresentation(12,!reduced)&&q.BetaGwentAnimationTempo()===tempo&&q.BetaGwentReducedEffects()===reduced,'invalid event cannot overwrite preferences');
 }
});
scenario('all profile readers initialize a cold profile without writing it',()=>{
 const p=rich(),card=p.betaGwentOwnedIds[0];
 const readers=[
  ['difficulty',q=>q.BetaGwentDifficulty()],['pause',q=>q.BetaGwentAiPause()],
  ['tempo',q=>q.BetaGwentAnimationTempo()],['effects',q=>q.BetaGwentReducedEffects()],
  ['preferred deck',q=>q.BetaGwentPreferredDeck()],['scraps',q=>q.BetaGwentScraps()],
  ['owned',q=>q.BetaGwentOwned(card)],['new card',q=>q.BetaGwentCardIsNew(card)],
  ['collection count',q=>q.BetaGwentCollectionCount(0)],['pending keg',q=>q.BetaGwentKegPending()],
  ['keg count',q=>q.BetaGwentKegCount()],['keg scraps',q=>q.BetaGwentKegReceivedScraps(0)],
  ['keg contents',q=>{const a={v:[]},b={v:[]};q.BetaGwentKegContents(a,b);return [a.v,b.v];}],
  ['cleanup latch',q=>q.BetaGwentCleanupPending()]
 ];
 for(const [label,read] of readers){
  const expected=S(read(p)),q=new W3PlayerWitcher();for(const f of STORE_FIELDS)q[f]=copy(p[f]);thePlayer=q;
  const before=S(STORE_FIELDS.map(f=>q[f]));
  check(S(read(q))===expected&&q.betaGwentStoreLoaded,'cold '+label+' restores saved value');
  check(S(read(q))===expected,'repeated '+label+' remains stable');
  check(S(STORE_FIELDS.map(f=>q[f]))===before,'reading '+label+' never changes saved bytes');
  const bad=new W3PlayerWitcher();for(const f of STORE_FIELDS)bad[f]=copy(p[f]);bad.betaGwentStore[1]=99;thePlayer=bad;
  const raw=S(STORE_FIELDS.map(f=>bad[f]));read(bad);
  check(bad.betaGwentStoreReadOnly&&S(STORE_FIELDS.map(f=>bad[f]))===raw,'unknown store preserved by '+label);
 }
});
console.log('SAVE_SAFETY094 '+S({complete:failures.length===0,checks,failures,actualWitcherScript:true,nativeSerializationTested:false}));
if(failures.length)process.exitCode=1;
