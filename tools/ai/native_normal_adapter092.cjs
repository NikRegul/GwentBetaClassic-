/* Experimental normal-turn seam. Uses frozen OpponentStep unchanged.
 * Memory is a caller-supplied checkpoint, not reconstructed from hidden cards.
 * Legal actions are checked against native request; full-match parity pending. */
'use strict';
const {compile,fingerprint}=require('./native_session_import092.cjs');
const decide=compile(String.raw`
const request=native.requests[0],actor=request?.player;
if(native.state!==32||native.winner!==0||request?.kind!=='RequestPlayCardAction'||request.details.forcedCard!==0||
   native.current!==actor||native.players.some(p=>p.id===actor&&p.hasMadeInitialMove))
  throw Error('Normal adapter requires an ordinary turn boundary');
if(!options.memory||options.observedThroughSequence!==native.sequence)
  throw Error('Normal adapter requires explicit policy-memory observation checkpoint');
if(native.cards.some(c=>[201601,200022].includes(c.template)))throw Error('Last-spell/moved-unit history not mapped');
const {g,flip,exportMemory}=importOriginalSession(native,configs,actor,{memory:options.memory});
let action=null;const logs=[];Host.log=line=>logs.push(line);
function capture(next){if(action)throw Error('Multiple initial policy actions');action=next;return true;}
g.Play=(side,id,row)=>capture({kind:'play',card:id,row,index:-3});
g.PlayBefore=(side,id,anchor)=>{const a=g.FindCard(anchor)?.Snapshot();if(!a)throw Error('Missing placement anchor');
  return capture({kind:'play',card:id,row:a.locationMask,index:a.locationIndex});};
g.UseLeader=()=>{const c=g.Leader(2);if(!c)throw Error('Missing own leader');
  return capture({kind:'play',card:c.Snapshot().instanceId,row:g.BestCardRow(2,c.Definition())||1,index:-3});};
g.Pass=()=>capture({kind:'pass'});
if(!g.OpponentStep()||g.IsFatal()||!action)throw Error('Frozen WS policy failed to produce normal action');
if(action.kind==='pass'){
  if(!request.details.canPass)throw Error('Frozen policy proposed forbidden pass');
}else{
  const card=g.FindCard(action.card),snapshot=card.Snapshot(),definition=card.Definition();
  const placementSide=definition.header.typeMask!==2&&BetaGwentDuelSpying(card.TemplateId())?3-actor:actor;
  const legal=request.details.moves.filter(m=>m.card===action.card);
  const move=definition.header.typeMask===2?legal[0]:legal.find(m=>m.position.side===placementSide&&m.position.zone===action.row&&
    m.position.index===(action.index<0?g.CountLocation(flip(placementSide),action.row):action.index));
  if(!move)throw Error('Frozen normal action has no exact native placement: '+JSON.stringify(action));
  // This is the frozen method PlayAtIndex invokes before resolving a hand card.
  // Capturing the external action must not lose chase-budget accounting.
  if(snapshot.locationMask===8)g.RecordChaseHandPlay(2);
  action={kind:'play',...move};
}
return {action,memory:exportMemory(),cardsImported:native.cards.length,logs,
  fullMatchReady:false,scope:'Normal-turn proposal only; ability/history/public-observation reconstruction still being validated'};
`);
module.exports={fingerprint,chooseNativeNormal:(native,configs,memory,observedThroughSequence,seed=923058801)=>
  decide(native,configs,{memory,observedThroughSequence},seed)};
