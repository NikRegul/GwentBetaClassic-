/* Experimental, fail-closed pending-choice seam. Calls the frozen P16 handlers;
 * it does not implement a substitute target evaluator. Only the three explicitly
 * checked original graphs below are supported. NOT a general match adapter. */
'use strict';
const {compile,fingerprint}=require('./native_session_import092.cjs');
const decide=compile(String.raw`
const request=native.requests[0],actor=request?.player,d=request?.details;
const original=native.cards.find(c=>c.id===d?.requester);
if(native.kind!=='original-authoritative-state-not-policy-observation'||native.state!==32||native.winner!==0||
   ![1,2].includes(actor)||!original||!original.inExecutionStack||!original.beingPlayed)
  throw Error('Choice adapter requires an original paused deploy choice');
const contract={
  152103:{request:'RequestCardChoicesAction',node:47,kind:2,count:2},
  152315:{request:'RequestCardTargetsAction',node:24,kind:0,count:3},
  112102:{request:'RequestLocationTargetsAction',node:104,kind:3,count:1}
}[original.template];
if(!contract||request.kind!==contract.request||request.ability?.graph!==original.template||request.ability?.currentNode!==contract.node||
   d.min!==Math.min(contract.count,request.kind==='RequestCardTargetsAction'?d.valid.length:contract.count)||d.max!==contract.count||
   (d.selected?.length||0)!==0)
  throw Error('Unmapped native choice graph/phase: '+original.template);
if(!Array.isArray(native.locations))throw Error('Choice adapter requires explicit native locations');
if(native.locations.some(l=>l.tokens!==0)||native.boardPersistent?.length||
   native.globalAbilityPersistent?.some(x=>x.variables?.length)||native.cards.some(c=>!supportedNativePersistent(c)))
  throw Error('Unmapped weather or persistent ability state');
if(native.cards.some(c=>c.id!==original.id&&(c.inExecutionStack||c.beingPlayed||c.waitingToDie)))
  throw Error('Nested parent/reaction stack not mapped');
if(request.ability.persistent?.length||request.ability.temporary?.some(v=>v.dynamicGetter||v.sourceVariable!==null))
  throw Error('Dynamic choice phase not mapped');
const {g,flip,scoreConvention}=importOriginalSession(native,configs,actor,{pendingCard:original.id});
if(g.match.currentPlayerId!==2)throw Error('Off-turn choice requires explicit actor context');
const sourceCard=g.FindCard(original.id);sourceCard.monsterStage=0;sourceCard.monsterRemaining=contract.count;sourceCard.monsterIds=[];
const chosen=[],logs=[];Host.log=line=>logs.push(line);
const select=g.monsters.Select.bind(g.monsters),rowChoice=g.monsters.Row.bind(g.monsters),requestChoice=g.MonsterRequest.bind(g);
let completed=false;
g.MonsterComplete=card=>{if(card!==sourceCard)throw Error('Unexpected nested completion');g.FlushDeaths();completed=true;};
g.monsters.Select=(card,id)=>{
  if(card!==sourceCard||id===0||chosen.includes(id))throw Error('Unexpected/duplicate/empty frozen selection');
  chosen.push(id);return select(card,id);
};
g.monsters.Row=(card,side,row)=>{
  if(card!==sourceCard||!d.valid.some(l=>flip(l.side)===side&&l.zone===row))throw Error('Illegal native row selected');
  chosen.push({side:flip(side),zone:row});return rowChoice(card,side,row);
};
const initial=d.originalChoices||d.valid;
g.MonsterRequest=(card,ids,kind,min,max)=>{
  // MonsterRequest itself removes the deploy source before evaluating targets.
  const effective=kind===0?ids.filter(id=>g.CanDeployTarget(card,g.FindCard(id))):ids;
  if(card!==sourceCard||kind!==contract.kind||effective.some(id=>!initial.includes(id)||chosen.includes(id)))
    throw Error('Continuation candidate set outside native choice');
  return requestChoice(card,ids,kind,min,max);
};
if(contract.kind===2){
  if(d.originalChoices.length!==d.choices.length||d.originalChoices.some((id,i)=>g.FindCard(id)?.TemplateId()!==d.choices[i].template))
    throw Error('Native fake choice IDs do not map to original instances');
  g.MonsterRequest(sourceCard,d.originalChoices.slice(),2,1,1);
}else if(contract.kind===0)g.MonsterRequest(sourceCard,d.valid.slice(),0,0,1);
else requestChoice(sourceCard,d.valid.map(l=>l.zone),3,1,1);
if(!completed||g.IsFatal()||chosen.length<d.min||chosen.length>d.max)throw Error('Frozen pending choice did not complete');
if(contract.kind!==3&&new Set(chosen).size!==chosen.length)throw Error('Duplicate batch choice');
const action=contract.kind===2?{kind:'choices',cards:chosen.map(id=>d.choices[d.originalChoices.indexOf(id)].id)}:
  contract.kind===0?{kind:'targets',cards:chosen}:{kind:'locations',locations:chosen};
return {action,sourceTemplate:original.template,originalInstanceChoices:contract.kind===2?chosen:undefined,
  scoreConvention,logs,cardsImported:native.cards.length,randomCheckpoint:{seed:native.random.initialSeed,draws:native.random.draws},
  choiceProjection:(contract.kind===3?native.cards.filter(c=>chosen.some(l=>l.side===c.position.side&&l.zone===c.position.zone)).map(c=>c.id):chosen).map(id=>{const c=g.FindCard(id),s=c.Snapshot();return {
    id,template:c.TemplateId(),side:flip(s.positionPlayerId),zone:s.locationMask,power:s.power.currentPower,armor:s.power.armor
  };})};
`);
module.exports={fingerprint,chooseNativeChoice:(native,configs,seed=923058501)=>decide(native,configs,{},seed)};
