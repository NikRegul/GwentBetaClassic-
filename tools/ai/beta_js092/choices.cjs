/* Source request/handler integration for the common engine.
 * Unmapped simultaneous selections and ambiguous graph stages fail explicitly;
 * no P19 fallback. PlayAll siblings replay source decisions from parent state.
 * Row legality is read from the same WS validator used to submit the move. */
'use strict';
const {BetaHandler,resolveAssociation,sourceHint,decision,UnportedBetaHandler}=require('./handlers.cjs');
const {stateFromSession,templates}=require('./session.cjs');
const {availablePositions}=require('./actions.cjs');
const requestHints=require('./data/request-hints.json');
const templateInfo=require('./data/request-template-info.json');
const F=Math.fround;
// Original Abilities.xml nodes, matched to explicit phases of the ONE common
// rules engine. No AIHint is guessed from the order of UI requests.
function stagedHint(source,kind,game){
 let node;
 const stage=game.pendingCard.monsterStage;
 if(kind==='templates'&&(source===201615||source===200102)){
  if(stage!==0&&stage!==1)throw new UnportedBetaHandler('Unknown branch-choice phase: '+source+'/'+stage);
  node=stage===0?32:464;
 }
 if(kind==='templates'&&[201697,201621,201653,132215].includes(source)){
  if(stage!==0&&stage!==1)throw new UnportedBetaHandler('Unknown source creation phase: '+source+'/'+stage);
  if(source===132215)node=stage===0?51:615;
  else
  node=stage===0?32:387;
 }
 if(kind==='choices'&&(source===200048||source===200165)){
  if(stage!==0&&stage!==1)throw new UnportedBetaHandler('Unknown exchange phase: '+source+'/'+stage);
  node=source===200048?(stage===0?52:295):(stage===0?50:95);
  const zone=stage===0?8:16;
  if(game.pendingIds.some(id=>game.FindCard(id)?.Snapshot().locationMask!==zone))
   throw new UnportedBetaHandler('Exchange phase has unexpected common-rule pool');
 }
 if(kind==='choices'&&source===153201){
  if(stage!==0&&stage!==1)throw new UnportedBetaHandler('Unknown Restore phase: '+stage);
  node=stage===0?23:88;
 }
 if(kind==='targets'&&source===200037){
  if(stage!==0&&stage!==1)throw new UnportedBetaHandler('Unknown Cyclops phase: '+stage);
  node=stage===0?18:74;
 }
 if(kind==='targets'&&[163201,201611].includes(source)){
  if(stage!==0&&stage!==1)throw new UnportedBetaHandler('Unknown Treason phase: '+stage);
  node=stage===0?18:139;
 }
 if(kind==='targets'&&source===201662){
  if(![201713,201714].includes(game.pendingCard.monsterStored))throw new UnportedBetaHandler('Unknown Cadaverine mode');
  node=game.pendingCard.monsterStored===201713?74:156;
 }
 if(kind==='targets'&&source===201648)node=game.pendingCard.selectedModeId===201711?87:130;
 if(kind==='targets'&&source===201731)node=game.pendingCard.neutralChoice===201734?1199:1302;
 if(kind==='targets'&&source===201737)node=game.pendingCard.neutralChoice===201740?1166:1241;
 if(node===undefined)return sourceHint(source,kind);
 const data=(requestHints[String(source)]||[]).find(n=>n.node===node&&n.kind===kind);
 if(!data)throw new UnportedBetaHandler('Source phase metadata missing: '+source+'/'+node);
 return data.hint;
}
function fromTemplate(id,side,definition=null){
 const t=templates[String(id)];if(!t)throw new UnportedBetaHandler('Missing source choice template '+id);
 const d=definition?.header,power=d?d.power:t.power,tier=d?d.tierMask:t.tier,type=d?d.typeMask:t.type;
 return {id,templateId:id,side,zone:128,index:0,power,basePower:power,printedPower:power,
  type,templateTier:tier,runtimeTier:tier,tokens:t.tokens,playable:true,
  semanticTags:t.semanticTags,categories:t.categories,placement:t.placement};
}
class BetaChoiceHandlers {
 constructor(runtime,personality){this.runtime=runtime;this.personality=personality;this.cache=[];}
 beginSimulation(tree,game){
  this.tree=tree;this.simulatorRandom=this.runtime.cloneSession(game).random;
 }
 next(min,max){if(max<=min)throw Error('Invalid SimulatorRandom range');return min+this.simulatorRandom.NextBounded(max-min);}
 context(node){return {node,state:stateFromSession(node.game),personality:this.personality,actor:node.executingPlayerId||node.game.Snapshot().currentPlayerId,next:(a,b)=>this.next(a,b)};}
 handler(type,template,hint=1,exact=null){
  const a=exact||resolveAssociation(this.personality,type,template,hint);
  if(a){
   let entry=this.cache.find(x=>x.association===a);
   if(!entry){entry={association:a,handler:new BetaHandler(a.attributes.Handler,a.settings,Number(a.attributes.ScoreToPropagate??0))};this.cache.push(entry);}
   return entry.handler;
  }
  if(!this.defaultHandler)this.defaultHandler=new BetaHandler('Random');return this.defaultHandler;
 }
 playCard({node,card,association}){
  const positions=availablePositions(node.game,card),h=this.handler('PlayCardAssociations',card.TemplateId(),1,association);
  const ctx=this.context(node);ctx.actor=node.game.Snapshot().currentPlayerId;
  const result=h.filter(ctx,{kind:'play',items:positions,min:1,max:1});
  return result===null?null:h.canBranchPlacement()?result:result.slice(0,1);
 }
 describe(node){
  const g=node.game,actor=g.RequestDecisionSide();
  if(g.pendingRally){
   const c=g.pendingRally;return {kind:'play',source:c.TemplateId(),hint:1,min:1,max:1,actor,items:availablePositions(g,c)};
  }
  if(!g.pendingCard)throw new UnportedBetaHandler('Request has no authoritative source');
  const source=g.pendingCard.TemplateId(),r=g.GetRequestSnapshot();
  if(!requestHints[String(source)]&&templateInfo[String(source)]?.hasPlayCardsNode&&g.pendingPileChoice&&g.pendingIds.length===1){
   const state=stateFromSession(g),item=state.cards.find(c=>c.id===g.pendingIds[0]);
   if(!item)throw Error('Forced source child absent');
   // The source PlayCardsNode has NO card-choice request. The common engine
   // exposes a sole fixed top card before placement; acknowledge that mechanic
   // without a policy handler or SimulatorRandom draw.
   return {kind:'forced',source,hint:0,min:1,max:1,actor,items:[item]};
  }
  if(g.pendingRow){
   if(typeof g.CanSelectRow!=='function')throw new UnportedBetaHandler('Shared rules lack authoritative row candidates');
   const hint=sourceHint(source,'locations'),items=[];
   for(const side of [1,2])for(const row of [1,2,4])if(g.CanSelectRow(g.requestId,side,row))items.push({side,row});
   if(r.limits.maximum>1)throw new UnportedBetaHandler('Multiple source locations not connected: '+source);
   return {kind:'locations',source,hint,min:r.limits.minimum,max:r.limits.maximum,actor,items};
  }
  // UI private-pile panels do not change an original CardTargets request into
  // CardChoices. Resolve semantic kind from the source graph, not presentation.
  const kinds=[...new Set((requestHints[String(source)]||[]).map(n=>n.kind).filter(k=>k==='targets'||k==='choices'))];
  const handPowerSource=source===133301||source===201656,handThenTarget=[200162,200031,152106,200020].includes(source),adventure=[201725,201731,201737].includes(source),modeCard=source===201603,donar=source===152204,talisman=source===201598;
  if(!g.pendingChoice&&kinds.length!==1&&!handPowerSource&&!handThenTarget&&!adventure&&!modeCard&&!donar&&!talisman)throw new UnportedBetaHandler('Explicit source request-kind stage needed: '+source+'/'+kinds);
  const kind=g.pendingChoice?'templates':handPowerSource?(g.pendingHandPower?'choices':'targets'):handThenTarget?(g.pendingCard.monsterStage===0?'choices':'targets'):
   adventure?([201730,201736].includes(g.pendingCard.neutralChoice)?'choices':'targets'):modeCard?(g.pendingCard.monsterStored===201695?'choices':'targets'):
   donar?(g.pendingCard.monsterStage===0?'targets':'choices'):talisman?(g.pendingCard.selectedModeId===201703?'targets':'choices'):kinds[0];
  const hint=stagedHint(source,kind,g),state=stateFromSession(g);
  const items=g.pendingIds.map(id=>{
   if(kind==='templates')return fromTemplate(id,actor,this.runtime.definition(id));
   const c=state.cards.find(x=>x.id===id);if(!c)throw Error('Pending instance not in shared state');return c;
  });
  // Bran's source graph requests its entire 0..3 set ONCE. The common engine
  // exposes one SelectTarget call per card, refreshing requestId in between.
  // Keep one recorded source decision and drain it cooperatively below.
  const wholeSet=([200159,162103,200163,162316,200227,201616,122204,200209].includes(source)&&kind==='choices')||(source===200218&&kind==='targets');
  if(r.limits.maximum>1&&!(wholeSet&&r.selectedCount===0))
   throw new UnportedBetaHandler('Multiple selection sequencing not mapped yet: '+source);
  return {kind,source,hint,min:r.limits.minimum,max:r.limits.maximum,actor,items};
 }
 fork(node,record){
  const sibling=this.tree.child(node.parent,node.decision===null?null:{...node.decision});
  sibling.choiceRecords=node.choiceRecords.slice(0,node.choiceCursor).map(r=>({...r,chosen:r.chosen.map(x=>({...x}))}));
  sibling.choiceRecords.push(record);sibling.handlerScore=node.handlerScore;
  sibling.mulliganChoices=node.mulliganChoices.map(x=>({...x}));
  node.parent.children.push(sibling);
  const group=node.parent.childBaseCards.find(x=>x.cardId===node.decision?.cardId);if(group)group.nodes.push(sibling);
 }
 request(node){
  if(node.activeChoice){this.continueChoice(node);return;}
  const g=node.game,r=this.describe(node),ctx=this.context(node);
  if(r.actor!==node.executingPlayerId)throw new UnportedBetaHandler('Opposing reactive decision ownership not mapped: '+r.source);
  const type=r.kind==='play'?'PlayCardAssociations':r.kind==='locations'?'LocationTargetsAssociations':r.kind==='targets'?'CardTargetsAssociations':'CardChoicesAssociations';
  let record=node.choiceRecords[node.choiceCursor];
  if(record){
   if(record.source!==r.source||record.kind!==r.kind||record.hint!==r.hint)throw new UnportedBetaHandler('Original replay request identity changed');
  }else{
   const h=r.kind==='forced'?null:this.handler(type,r.source,r.hint),result=h?decision(h,ctx,r):{chosen:r.items,branches:[],propagated:0,sourceFallback:false};
   // Source placement helper selects the first item and clones each remaining
   // position only for CanAutoAddRemainingPlayCardDecisions handlers.
   if(r.kind==='play'){
    if(h.canBranchPlacement())result.branches=(result.filtered||[]).slice(1).map(x=>[x]);
   }
   const make=chosen=>({kind:r.kind,source:r.source,hint:r.hint,chosen:chosen.map(x=>({...x})),sourceFallback:result.sourceFallback});
   for(const branch of result.branches)this.fork(node,make(branch));
   record=make(result.chosen);node.choiceRecords.push(record);node.handlerScore=F(node.handlerScore+result.propagated);
  }
  node.choiceCursor++;
  const chosen=record.chosen;
  if(r.max>1){
   node.activeChoice={record,index:0,sourceId:g.pendingCard.Snapshot().instanceId,stage:g.pendingCard.monsterStage,actor:r.actor};
   this.continueChoice(node);return;
  }
  let ok;
  if(!chosen.length)ok=g.FinishTarget(g.requestId);
  else if(r.kind==='play'){
   const x=chosen[0],anchor=g.live.find(c=>{const s=c.Snapshot();return s.positionPlayerId===x.side&&s.locationMask===x.row&&s.locationIndex===x.index;});
   ok=anchor?g.SelectPlacementBefore(g.requestId,anchor.Snapshot().instanceId):g.SelectRow(g.requestId,x.side,x.row);
  }else if(r.kind==='locations')ok=g.SelectRow(g.requestId,chosen[0].side,chosen[0].row);
  else if(r.kind==='templates')ok=g.SelectTemplateChoice(g.requestId,chosen[0].templateId);
  else ok=g.SelectTarget(g.requestId,chosen[0].id);
  if(!ok)throw new UnportedBetaHandler('Original single choice rejected by shared engine: '+JSON.stringify({source:r.source,kind:r.kind,chosen,message:g.GetMessage(),pendingRally:g.pendingRally?.Snapshot(),stack:g.playStack.map(c=>c.TemplateId()),pendingCard:g.pendingCard?.TemplateId()}));
  if(r.kind==='locations')node.locationChoices.push(chosen);
 }
 continueChoice(node){
  const g=node.game,a=node.activeChoice,record=a.record;
  if(!g.pendingCard||g.pendingCard.Snapshot().instanceId!==a.sourceId||g.RequestDecisionSide()!==a.actor)
   throw new UnportedBetaHandler('Multi-choice source changed before completion');
  let ok;
  if(a.index<record.chosen.length){
   const id=record.chosen[a.index].id;
   if(!g.pendingIds.includes(id))throw new UnportedBetaHandler('Recorded multi-choice no longer legal');
   ok=g.SelectTarget(g.requestId,id);a.index++;
  }else{ok=g.FinishTarget(g.requestId);node.activeChoice=null;}
  if(!ok)throw new UnportedBetaHandler('Original multi-choice rejected by common engine');
  if(a.index===record.chosen.length&&(!g.IsPending()||!g.pendingCard||g.pendingCard.Snapshot().instanceId!==a.sourceId||g.pendingCard.monsterStage!==a.stage))node.activeChoice=null;
 }
 hooks(){return {beginSimulation:(t,g)=>this.beginSimulation(t,g),playCard:x=>this.playCard(x),request:n=>this.request(n)};}
}
module.exports={BetaChoiceHandlers,fromTemplate,stagedHint};
