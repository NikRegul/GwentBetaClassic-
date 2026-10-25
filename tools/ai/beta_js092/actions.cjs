/* Node.InitialiseChildren / BaseSearchTree.TryPlayAction direct JS integration.
 * This is the source action skeleton; unported handlers fail explicitly.
 * One shared WS rules engine and production state clones, no native bridge. */
'use strict';
const {BetaSearchNode,Status}=require('./search.cjs');
const {stateFromSession,templates}=require('./session.cjs');
const {stepMulligan}=require('./mulligan.cjs');
class UnsupportedBetaPort extends Error{}
function association(personality,type,templateId,hint=1){
 const list=personality?.associations?.[type]||[];
 for(let i=0;i<list.length;i++){
  const a=list[i].attributes;
  if(Number(a.TemplateId)===templateId&&Number(a.AIHIntId===undefined?1:a.AIHIntId)===hint)return list[i];
 }
 return null;
}
// BoardManager.GetAvailablePositions. The common engine keeps contiguous row
// indices, so [max(first-1,0), min(last+1,8)] is exactly [0,count].
function availablePositions(game,card){
 const s=card.Snapshot(),t=templates[String(card.TemplateId())];
 if(!t)throw new UnsupportedBetaPort('Original placement metadata absent: '+card.TemplateId());
 // CardPosition.GetEventCardPositionForPlayer uses Graveyard, LAST_INDEX.
 if(t.type===2)return [{side:s.positionPlayerId,row:32,index:-3}];
 if(!t.placement)throw new UnsupportedBetaPort('Original placement not extracted: '+t.id);
 const result=[];
 for(const [side,mask]of [[s.positionPlayerId,t.placement.player],[3-s.positionPlayerId,t.placement.opponent]])
  for(const row of [1,2,4])if(mask&row){
   // Source placement masks are intersected with the ONE common rules engine.
   // In particular its Oak tokens currently play on the owner's side, whereas
   // Beta template metadata permits either side. Never submit an illegal
   // source position or silently mutate card ownership to make it fit.
   if(game.pendingRally===card){if(!game.CanSelectRow(game.requestId,side,row))continue;}
   else if(side!==game.MonsterPlaySide(card,s.positionPlayerId))continue;
   const count=game.CountLocation(side,row);
   if(count<9)for(let i=0;i<=count;i++)result.push({side,row,index:i});
  }
 return result;
}
class BetaGameTree {
 constructor(runtime,personality,handlers={}){
  if(!runtime.externalPolicyHooks)throw new UnsupportedBetaPort('Shared rules snapshot lacks external-policy decision hooks');
  this.runtime=runtime;this.personality=personality;this.handlers=handlers;
  this.nextId=1;this.mutations=0;
 }
 root(game){
  if(game.externalPolicyMask!==3)throw Error('Search requires external choices on both cloned seats');
  if(game.IsPending()||game.waiting||game.IsFatal())throw Error('Root must be a stable legal turn');
  const root=new BetaSearchNode(this.nextId++,0);root.game=game;root.state=stateFromSession(game);
  root.parentState=root.state;root.executingPlayerId=root.state.currentPlayerId;root.currentPlayerId=root.state.currentPlayerId;
  root.status=Status.OK;root.locationChoices=[];root.handlerScore=0;root.decision=null;
  if(this.handlers.beginSimulation)this.handlers.beginSimulation(this,game);
  this.initialiseChildren(root);return root;
 }
 child(parent,decision){
  const n=new BetaSearchNode(this.nextId++,parent.depth+1,parent);n.decision=decision;
  n.locationChoices=[];n.mulliganChoices=[];n.mulliganCursor=0;n.choiceRecords=[];n.choiceCursor=0;n.handlerScore=parent.handlerScore||0;
  n.parentState=parent.state;return n;
 }
 initialiseChildren(node){
  const game=node.game,p=this.personality,side=game.Snapshot().currentPlayerId;
  node.children=[];node.childBaseCards=[];
  if(game.Snapshot().matchWinnerMask!==0){node.terminal=true;return;}
  if(p===null||p.AllowedToPass)node.children.push(this.child(node,null));
  const hand=stateFromSession(game).cards.filter(c=>c.side===side&&c.playable&&(c.zone===8||((p===null||p.AllowedToUseLeader)&&c.zone===64))&&game.HasRequiredPlayTarget(game.FindCard(c.id)));
  for(let i=0;i<hand.length;i++){
   const c=hand[i];let duplicate=false;
   for(let j=0;j<i;j++)if(hand[j].templateId===c.templateId){duplicate=true;break;}
   if(duplicate)continue;
   const card=game.FindCard(c.id),a=association(p,'PlayCardAssociations',c.templateId,1);
   let positions=null;
   if(a){
    if(!this.handlers.playCard)throw new UnsupportedBetaPort('PlayCard handler not ported: '+a.attributes.Handler+'/'+c.templateId);
    positions=this.handlers.playCard({node,card,association:a,personality:p});
   }
   // Source falls back to all available positions if the custom handler did
   // not produce a usable decision. Unsupported handlers never return null.
   if(positions===null||positions.length===0)positions=availablePositions(game,card);
   const group={cardId:c.id,nodes:[]};node.childBaseCards.push(group);
   for(const position of positions){
    const child=this.child(node,{cardId:c.id,...position});node.children.push(child);group.nodes.push(child);
   }
  }
 }
 request(node){
  const game=node.game;
  if(game.mulligan){
   // BaseSearchTree.OnMulliganRequestReceivedRedirect explicitly finishes the
   // OTHER player's simulated mulligan. Live controllers still run their own
   // picker; do not silently grant our search a second player's mulligan.
   if(game.RequestDecisionSide()!==node.executingPlayerId){
    if(!game.FinishMulligan(game.requestId))throw Error('Other-seat simulated mulligan rejected');
   }else{
    const stored=node.mulliganChoices[node.mulliganCursor];
    if(stored)stepMulligan(game,this.personality,null,stored);
    else stepMulligan(game,this.personality,node.mulliganChoices);
    node.mulliganCursor++;
   }
   this.mutations++;return;
  }
  if(!this.handlers.request)throw new UnsupportedBetaPort('Nested request handler not ported: '+game.pendingCard?.TemplateId());
  this.handlers.request(node);this.mutations++;
 }
 performInitial(node){
  const game=node.game,decision=node.decision,side=game.Snapshot().currentPlayerId;
  node.executingPlayerId=side;
  let ok;
  if(decision===null||decision.cardId===0)ok=game.Pass(side);
  else{
   const card=game.FindCard(decision.cardId);if(!card)throw Error('Node card absent');
   const s=card.Snapshot();
   if(s.locationMask===64){
    ok=game.UseLeader(side);node.awaitingInitialPlacement=ok;
   }else if(card.Definition().header.typeMask!==4)ok=game.Play(side,decision.cardId,1);
   else{
    const anchor=game.live.find(c=>{const x=c.Snapshot();return x.positionPlayerId===decision.side&&x.locationMask===decision.row&&x.locationIndex===decision.index;});
    ok=anchor?game.PlayBefore(side,decision.cardId,anchor.Snapshot().instanceId):game.Play(side,decision.cardId,decision.row);
   }
  }
  this.mutations++;if(!ok){
   const template=decision===null?0:game.FindCard(decision.cardId)?.TemplateId();
   throw new UnsupportedBetaPort('Shared engine rejected node initial action: '+JSON.stringify({side,template,decision,message:game.GetMessage()}));
  }
 }
 placeInitialLeader(node){
  const g=node.game,d=node.decision;
  if(!g.pendingLeader)throw Error('Initial leader placement request lost');
  const anchor=g.live.find(c=>{const x=c.Snapshot();return x.positionPlayerId===d.side&&x.locationMask===d.row&&x.locationIndex===d.index;});
  const ok=anchor?g.SelectPlacementBefore(g.requestId,anchor.Snapshot().instanceId):g.SelectRow(g.requestId,d.side,d.row);
  node.awaitingInitialPlacement=false;this.mutations++;if(!ok)throw Error('Leader position rejected');
 }
 tryPlayAction(node){
  if(node.status!==Status.Uninitialised)return false;
  if(!node.game){node.game=this.runtime.cloneSession(node.parent.game);node.game.recordVisuals=false;}
  const game=node.game;
  if(!node.started){node.started=true;this.performInitial(node);}
  else if(node.awaitingInitialPlacement)this.placeInitialLeader(node);
  else if(game.IsPending())this.request(node);
  else if(game.waiting){if(!game.BeginNextRound())throw Error('Next round rejected');this.mutations++;}
  if(game.IsFatal())throw Error('Fatal shared rules error: '+game.GetMessage());
  if(game.IsPending()||game.waiting)return null;
  node.state=stateFromSession(game);node.currentPlayerId=node.state.currentPlayerId;
  node.terminal=node.state.winnerMask!==0;
  this.initialiseChildren(node);node.status=Status.OK;return true;
 }
}
module.exports={BetaGameTree,UnsupportedBetaPort,availablePositions,association};
