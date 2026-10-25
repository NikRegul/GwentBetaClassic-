/* Shared authoritative-state model import into frozen WS runtime.
 * This transfers enumerated fields, not every semantic field of a live session.
 * Persistent ability/global state and unsupported locations fail closed.
 * A successful import is NOT proof that a full policy/match adapter is ready. */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {rules}=require('./native_bridge_paths092.cjs');
const manifest=JSON.parse(fs.readFileSync(path.join(rules,'manifest.json'),'utf8'));
for(const [file,sha]of Object.entries(manifest.snapshotFiles))
  if(crypto.createHash('sha256').update(fs.readFileSync(path.join(rules,file))).digest('hex')!==sha)
    throw Error('Frozen control changed: '+file);
const runtime=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n');
const importSource=String.raw`
function nativePersistentContract(card){
  // Exact original Abilities.xml contracts: Ciri's unused Bool354,
  // Olgierd's Killed348, and Ice Giant's exhausted one-shot Counter102.
  // Only their observed inactive values are mapped.
  // Active return state also needs death-position/history parity and remains
  // unsupported; an unknown variable is never silently discarded.
  return {112101:{id:354,names:['Bool'],type:'BoolVar',value:false,semantics:'inactive-flag'},
    112207:{id:348,names:['Killed'],type:'BoolVar',value:false,semantics:'inactive-flag'},
    132212:{id:102,names:['Counter',null],type:'IntVar',value:0,semantics:'exhausted-frost-charge'},
    // The three original counters below are never written. Mutable timer state
    // is transferred from CardData.Timer, independently of these constants.
    132201:{id:345,names:['RealCounter'],type:'IntVar',value:4,semantics:'immutable-timer-config'},
    200040:{id:37,names:['Counter'],type:'IntVar',value:2,semantics:'immutable-timer-config'},
    200177:{id:184,names:['Counter'],type:'IntVar',value:4,semantics:'unused-timer-declaration'},
    // Exact original graphs have no reads, writes or connections for these
    // declarations. Accept only their original default, not arbitrary state.
    200022:{id:578,names:['SummonedCard'],type:'CardDefinitionVar',emptyDefinition:true,semantics:'unused-declaration'},
    201601:{id:232,names:['SummonedCard'],type:'CardDefinitionVar',emptyDefinition:true,semantics:'unused-declaration'},
    201776:{id:72,names:['Bool'],type:'BoolVar',value:false,semantics:'unused-declaration'}}[card.template];
}
function supportedNativePersistent(card){
  const contract=nativePersistentContract(card);
  return !card.persistent?.length || card.persistent.length===1 && !!contract && card.persistent.every(v=>
    v.id===contract.id&&contract.names.includes(v.name)&&v.type==='GwentGameplay.'+contract.type&&
    (contract.emptyDefinition?v.storedValue?.template===0&&v.storedValue?.premium===false&&Object.keys(v.storedValue).length===2:v.storedValue===contract.value)&&
    v.dynamicGetter===false&&v.sourceVariable===null&&v.encoding==='raw-stored-field-no-evaluation');
}
function importOriginalSession(native,configs,actor,options={}){
  const totalErrors=native.loggerErrors,handled=native.loggerHandledFallbacks??0,fatal=native.loggerFatalErrors??totalErrors,replay=native.loggerDiagnosticReplayErrors??0;
  if(native.kind!=='original-authoritative-state-not-policy-observation'||![1,2].includes(actor)||fatal!==0||
     ![totalErrors,handled,fatal,replay].every(n=>Number.isInteger(n)&&n>=0)||totalErrors!==handled+fatal+replay||
     replay>0&&native.diagnosticOnly!==true||native.diagnosticOnly&&native.ratingPermitted!==false||
     (native.diagnosticOnly||replay>0)&&options.diagnosticAnalysis!==true)
    throw Error('Invalid original authoritative model');
  if(!Array.isArray(native.locations)||!Array.isArray(native.rounds)||!Array.isArray(native.roundHands))
    throw Error('Original state metadata missing');
  if(native.boardPersistent?.length||native.globalAbilityPersistent?.some(x=>x.variables?.length)||
     native.cards.some(c=>!supportedNativePersistent(c)))throw Error('Unmapped persistent ability state');
  if(native.cards.some(c=>c.waitingToDie||(c.inExecutionStack||c.beingPlayed)&&c.id!==options.pendingCard))
    throw Error('Unmapped execution/death stack');
  const flip=n=>n===actor?2:n===3-actor?1:n;
  const cfg=n=>configs[(n===2?actor:3-actor)-1];
  const one=cfg(1),two=cfg(2),g=new CBetaGwentDuelSession();
  if(!g.InitializeWithDecks(one.deck.cards,two.deck.cards,one.deck.leader,two.deck.leader,one.preset||0,two.preset||0))
    throw Error('WS does not support source roster');
  if(native.random?.encoding!=='original-beta-scalar-cursor-v1'||native.random.words.length!==625)
    throw Error('Native random checkpoint missing or unsupported');
  g.random.words=native.random.words.map(x=>x|0);g.random.cursor=native.random.cursor|0;g.random.remaining=native.random.remaining;
  g.random.reseedValue=native.random.reseedValue|0;g.random.initialSeed=native.random.initialSeed|0;g.random.draws=native.random.draws|0;
  g.live=[];g.registry=new CBetaGwentDuelRegistry();g.registry.Initialize();
  const ids=new Set();
  for(const c of native.cards){if(!Number.isInteger(c.id)||c.id<=0||ids.has(c.id))throw Error('Invalid/duplicate card ID');ids.add(c.id);}
  while(g.registry.nextId<=Math.max(...ids)){const id={v:0};if(!g.registry.Allocate(id))throw Error('Allocate');}
  for(const c of native.cards){
    if(![1,2,4,8,16,32,64,128,256,512].includes(c.position.zone))throw Error('Unknown native zone');
    const def=BetaGwentDuelDefinition(c.template);if(def.header.templateId!==c.template)throw Error('Unknown WS template: '+c.template);
    const card=new CBetaGwentDuelCard();card.Setup(g,c.id,c.template,flip(c.position.side),c.position.zone,c.position.index);
    const s=card.cardState;
    s.ownerId=flip(c.position.side);s.controllerId=s.ownerId;
    s.canBePlayed=c.playable;s.runtimeTierMask=c.tier;s.tokenMask=c.tokens;s.timerValue=c.timer;
    s.isInExecutionStack=c.inExecutionStack;s.isWaitingToDie=c.waitingToDie;
    s.power.basePower=c.basePower;s.power.permanentPower=c.permanentPower;s.power.currentPower=c.power;s.power.armor=c.armor;
    card.power.initialized=false;card.power.InitFromFields(s.power);
    card.playFromLocation=c.fromPosition?.zone||0;card.lastActiveRow=(c.position.zone&7)!==0?c.position.zone:0;
    if(c.template===112207&&c.persistent?.length)card.monsterOnce=0; // Killed=false
    if(c.template===132212&&c.persistent?.length)card.monsterOnce=0; // Counter102 exhausted
    if(!g.registry.Put(c.id,card))throw Error('Insert native card');g.live.push(card);
  }
  const locationKeys=new Set();
  for(const l of native.locations){
    const key=l.side+':'+l.zone;if(locationKeys.has(key))throw Error('Duplicate native location');locationKeys.add(key);
    const imported=g.live.filter(c=>c.cardState.positionPlayerId===flip(l.side)&&c.cardState.locationMask===l.zone)
      .sort((a,b)=>a.cardState.locationIndex-b.cardState.locationIndex).map(c=>c.cardState.instanceId);
    if(JSON.stringify(imported)!==JSON.stringify(l.cards))throw Error('Native location ordering mismatch');
    if([1,2,4].includes(l.zone)){
      if(![0,1,2,4,16,32,64,128,256,512,1024,2048].includes(l.tokens))throw Error('Unmapped location token');
      g.weather.hazards[(flip(l.side)-1)*3+({1:0,2:1,4:2})[l.zone]]=l.tokens;
    }else if(l.tokens!==0)throw Error('Token on inactive location');
  }
  if(native.cards.some(c=>!locationKeys.has(c.position.side+':'+c.position.zone)))throw Error('Native card outside listed locations');
  g.mulligan=false;g.waiting=false;g.pendingCard=null;g.pendingLeader=null;g.pendingRally=null;g.recordVisuals=false;
  g.playStack=options.pendingCard?[g.FindCard(options.pendingCard)]:[];
  g.match.roundNumber=native.round;g.match.startingPlayerId=flip(native.starting);g.match.currentPlayerId=flip(native.current);
  g.match.turnSequence=native.rounds.reduce((n,r)=>n+r.turn,0);g.match.roundActive=true;g.match.turnActive=true;g.match.results=[];
  const scoreConvention=[];
  for(const p of native.players){const dest=flip(p.id)===1?g.match.playerOne:g.match.playerTwo;
    dest.crowns=p.crowns;dest.hasPassed=p.passed;dest.hasMadeInitialMoveForCurrentTurn=p.hasMadeInitialMove;
    const pendingBody=native.cards.filter(c=>c.position.side===p.id&&(c.position.zone&7)!==0&&c.inExecutionStack&&(c.tokens&8)===0)
      .reduce((n,c)=>n+c.power,0);
    if(g.Score(flip(p.id))!==p.score+pendingBody)throw Error('Native/WS pending-score convention mismatch');
    scoreConvention.push({nativeSide:p.id,nativeScore:p.score,wsScore:g.Score(flip(p.id)),pendingBody});
  }
  for(const r of native.rounds.filter(r=>r.finished)){
    const dest=new SBetaGwentRoundResult();dest.roundNumber=r.id;dest.startingPlayerId=flip(r.starting);
    dest.scoreOne=r.scores[2-actor];dest.scoreTwo=r.scores[actor-1];
    dest.winnerMask=actor===2?r.winner:((r.winner&1)<<1)|((r.winner&2)>>1);
    dest.crownDeltaOne=(dest.winnerMask&1)?1:0;dest.crownDeltaTwo=(dest.winnerMask&2)?1:0;g.match.results.push(dest);
  }
  g.aiRoundHandOne=native.roundHands[2-actor];g.aiRoundHandTwo=native.roundHands[actor-1];g.aiSimDamp=40;g.ClearAiPreparation();
  // Only persistent observation/intent fields, never search caches from an old
  // board. Live action accounting must be performed by the eventual bridge.
  const memory=options.memory||{};
  const fields=['aiChaseRound','aiChaseInitialHand','aiChaseSpent','aiObservedRound','aiObservedEnemyScore','aiPublicTempo','aiDecisionSerial'];
  for(const k of fields)if(memory[k]!==undefined)g[k]=memory[k];
  if(memory.aiEnemyRowPlays){if(memory.aiEnemyRowPlays.length!==3)throw Error('Invalid row observation memory');g.aiEnemyRowPlays=memory.aiEnemyRowPlays.slice();}
  const plans=['planRound','roundPlan','planEnemyInvestment','planOwnInvestment'];
  for(const k of plans)if(memory.archetype?.[k]!==undefined)g.archetypeAI[k]=memory.archetype[k];
  function exportMemory(){
    const result={archetype:{},aiEnemyRowPlays:g.aiEnemyRowPlays.slice()};
    for(const k of fields)result[k]=g[k];for(const k of plans)result.archetype[k]=g.archetypeAI[k];return result;
  }
  return {g,flip,scoreConvention,exportMemory};
}
`;
const prelude=String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[tunes,tunes];Host.seatIndex=1;
let random=seed>>>0||1;Host.random=()=>{random^=random<<13;random>>>=0;random^=random>>>17;random>>>=0;random^=random<<5;random>>>=0;return random/4294967296;};
`;
const tunes=JSON.parse(fs.readFileSync(path.join(rules,'tunes.json'),'utf8'));
function compile(body){const fn=new Function('native','configs','options','tunes','seed',runtime+importSource+prelude+body);
  return (native,configs,options={},seed=923058701)=>fn(native,configs,options,tunes,seed);}
const inspect=compile(String.raw`
const {g,flip,scoreConvention,exportMemory}=importOriginalSession(native,configs,options.actor,options);
return {cards:g.live.map(c=>{const s=c.Snapshot();return {id:s.instanceId,template:c.TemplateId(),side:flip(s.positionPlayerId),
  zone:s.locationMask,index:s.locationIndex,tier:s.runtimeTierMask,tokens:s.tokenMask,timer:s.timerValue,playable:s.canBePlayed,
  basePower:s.power.basePower,power:s.power.currentPower,permanentPower:s.power.permanentPower,armor:s.power.armor,
  inExecutionStack:s.isInExecutionStack,waitingToDie:s.isWaitingToDie};}),
  hazards:g.weather.hazards,scoreConvention,round:g.match.roundNumber,current:flip(g.match.currentPlayerId),
  crowns:[g.match.playerOne.crowns,g.match.playerTwo.crowns],results:g.match.results,
  roundHands:[g.aiRoundHandOne,g.aiRoundHandTwo],memory:exportMemory(),
  random:{words:g.random.words.map(x=>x>>>0),cursor:g.random.cursor>>>0,remaining:g.random.remaining,
    reseedValue:g.random.reseedValue>>>0,initialSeed:g.random.initialSeed,draws:g.random.draws>>>0},
  persistentMappings:native.cards.filter(c=>c.persistent?.length).map(c=>({id:c.id,template:c.template,
    variable:c.persistent[0].id,inactive:true,semantics:nativePersistentContract(c).semantics,
    monsterOnce:g.FindCard(c.id).monsterOnce,timer:g.FindCard(c.id).Snapshot().timerValue})),
  missingSemanticFields:['active/other persistent ability counters','last spell/moved-unit history','public enemy row observation reconstruction','live action accounting'],
  fullMatchReady:false};
`);
module.exports={compile,inspectNativeModel:inspect,fingerprint:manifest.fingerprint,rules};
