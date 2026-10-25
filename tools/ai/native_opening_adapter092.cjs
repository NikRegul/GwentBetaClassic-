/* Narrow, fail-closed first seam between a native Beta state and frozen WS AI.
 * ONLY a fresh first-round empty board is supported. Persistent ability state,
 * weather, nested requests and a complete match are deliberately rejected.
 */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {root,rules}=require('./native_bridge_paths092.cjs');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const manifest=JSON.parse(fs.readFileSync(path.join(rules,'manifest.json'),'utf8'));
for(const [file,hash] of Object.entries(manifest.snapshotFiles))
  if(sha(path.join(rules,file))!==hash)throw new Error('Frozen control changed: '+file);
const source=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n');
const choose=new Function('native','configs','tunes','seed',source+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[tunes,tunes];Host.seatIndex=1;
let random=seed>>>0||1;
Host.random=()=>{random^=random<<13;random>>>=0;random^=random>>>17;random>>>=0;random^=random<<5;random>>>=0;return random/4294967296;};
const request=native.requests[0],actor=request?.player;
if(native.diagnosticOnly||(native.loggerDiagnosticReplayErrors||0)!==0)
  throw Error('Diagnostic native state cannot enter the opening policy adapter');
if(native.kind!=='original-authoritative-state-not-policy-observation'||native.state!==32||native.round!==1||
   native.winner!==0||![1,2].includes(actor)||request.kind!=='RequestPlayCardAction'||request.details.forcedCard!==0||
   native.players.some(p=>p.passed||p.crowns||p.hasMadeInitialMove)||
   native.cards.some(c=>(c.position.zone&7)!==0||c.inExecutionStack||c.beingPlayed||c.waitingToDie))
  throw Error('Opening adapter rejects state outside first normal empty-board decision');
if(native.players.some(p=>native.cards.filter(c=>c.position.side===p.id&&c.position.zone===8).length!==10))
  throw Error('Opening adapter requires complete initial ten-card hands');
const side=n=>n===actor?2:n===3-actor?1:n;
const cfg=n=>configs[(n===2?actor:3-actor)-1];
const one=cfg(1),two=cfg(2),g=new CBetaGwentDuelSession();
if(!g.InitializeWithDecks(one.deck.cards,two.deck.cards,one.deck.leader,two.deck.leader,one.preset||0,two.preset||0))
  throw Error('Current WS does not support original deck configuration');
g.live=[];g.registry=new CBetaGwentDuelRegistry();g.registry.Initialize();
const maximum=Math.max(...native.cards.map(c=>c.id));
while(g.registry.nextId<=maximum){const id={v:0};if(!g.registry.Allocate(id))throw Error('ID allocation failed');}
for(const source of native.cards) {
  if(![8,16,64].includes(source.position.zone))throw Error('Opening contains unsupported zone');
  const definition=BetaGwentDuelDefinition(source.template);
  if(definition.header.templateId!==source.template)throw Error('Template absent from WS control: '+source.template);
  const c=new CBetaGwentDuelCard();c.Setup(g,source.id,source.template,side(source.position.side),source.position.zone,source.position.index);
  const s=c.cardState;
  s.ownerId=side(source.position.side);s.controllerId=s.ownerId;
  s.runtimeTierMask=source.tier;s.tokenMask=source.tokens;s.timerValue=source.timer;s.canBePlayed=source.playable;
  s.power.basePower=source.basePower;s.power.permanentPower=source.permanentPower;s.power.currentPower=source.power;s.power.armor=source.armor;
  c.power.initialized=false;c.power.InitFromFields(s.power);
  if(!g.registry.Put(source.id,c))throw Error('ID insertion failed');g.live.push(c);
}
g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.pendingRally=null;g.waiting=false;g.recordVisuals=false;
g.match.roundNumber=1;g.match.turnSequence=native.turn||1;g.match.startingPlayerId=side(native.starting);g.match.currentPlayerId=2;
g.match.roundActive=true;g.match.turnActive=true;g.match.results=[];
g.match.playerOne.crowns=0;g.match.playerTwo.crowns=0;g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
g.match.playerOne.hasMadeInitialMoveForCurrentTurn=false;g.match.playerTwo.hasMadeInitialMoveForCurrentTurn=false;
g.aiRoundHandOne=10;g.aiRoundHandTwo=10;g.aiSimDamp=40;g.ClearAiPreparation();
for(const p of native.players)if(g.Score(side(p.id))!==p.score)throw Error('Native/WS score mismatch on import');
for(const original of native.cards){const c=g.FindCard(original.id),s=c.Snapshot();
 if(c.TemplateId()!==original.template||s.power.currentPower!==original.power||s.power.armor!==original.armor||s.power.basePower!==original.basePower||s.power.permanentPower!==original.permanentPower||s.tokenMask!==original.tokens||s.timerValue!==original.timer||s.runtimeTierMask!==original.tier||s.locationMask!==original.position.zone||s.locationIndex!==original.position.index||s.positionPlayerId!==side(original.position.side))
  throw Error('Native/WS card mismatch on import id='+original.id);
}
let action=null;const logs=[];Host.log=line=>logs.push(line);
function capture(next){if(action)throw Error('More than one initial action');action=next;return true;}
g.Play=(s,id,row)=>capture({kind:'play',card:id,row,requestedIndex:-3});
g.PlayBefore=(s,id,anchor)=>{const a=g.FindCard(anchor).Snapshot();return capture({kind:'play',card:id,row:a.locationMask,requestedIndex:a.locationIndex});};
g.UseLeader=s=>{const c=g.Leader(2);return capture({kind:'play',card:c.Snapshot().instanceId,row:g.BestCardRow(2,c.Definition())||1,requestedIndex:-3});};
g.Pass=s=>capture({kind:'pass'});
if(!g.OpponentStep()||!action||g.IsFatal())throw Error('Frozen WS AI failed to produce initial action');
if(action.kind==='pass'){
 if(!request.details.canPass)throw Error('WS selected forbidden pass');
 return {action:{kind:'pass'},logs,cardsImported:native.cards.length};
}
const card=g.FindCard(action.card),definition=card.Definition();
let targetSide=actor;
if(definition.header.typeMask!==2&&BetaGwentDuelSpying(card.TemplateId()))targetSide=3-actor;
const legal=request.details.moves.filter(m=>m.card===action.card);
let move;
if(definition.header.typeMask===2)move=legal[0];
else move=legal.find(m=>m.position.side===targetSide&&m.position.zone===action.row&&
 (action.requestedIndex<0||m.position.index===action.requestedIndex));
if(!move)throw Error('WS opening has no exact native legal placement: '+JSON.stringify(action));
return {action:{kind:'play',...move},logs,cardsImported:native.cards.length};
`);
const tunes=JSON.parse(fs.readFileSync(path.join(rules,'tunes.json'),'utf8'));
module.exports={chooseOpening:(native,configs,seed=923058301)=>choose(native,configs,tunes,seed),fingerprint:manifest.fingerprint};
