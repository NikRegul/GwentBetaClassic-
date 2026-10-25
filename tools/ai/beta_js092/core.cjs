/* Direct port of original Beta AI formulas. Ordinary JS, arrays and records;
 * no native process, transport, reflection or alternate battle engine.
 * Source methods are recorded beside each component. Search/PlayMaker/handlers
 * are still separate pending work: these components are not a complete AI. */
'use strict';
const F=Math.fround;
const MIN_FLOAT=-3.4028234663852886e38;
function add(a,b){return F(F(a)+F(b));}
function mul(a,b){return F(F(a)*F(b));}
function div(a,b){return F(F(a)/F(b));}
function has(list,value){return list.indexOf(value)>=0;}
function isPass(node){return node.decision===null||node.decision.cardId===0;}
function findCard(state,id){for(let i=0;i<state.cards.length;i++)if(state.cards[i].id===id)return state.cards[i];throw Error('Missing card '+id);}
function playableCards(state,side,leader=true){
 const result=[];
 for(let i=0;i<state.cards.length;i++){
  const c=state.cards[i];if(c.side===side&&c.playable&&(c.zone===8||leader&&c.zone===64))result.push(c);
 }
 return result;
}
function carryover(card){return (card.tokens&1)!==0?card.power:0;}
function quality(cards){
 const q={bronze:0,silver:0,gold:0,leader:0,carryover:0,count:0};
 for(let i=0;i<cards.length;i++){
  const c=cards[i];if(!c.playable)continue;q.count++;
  if(c.templateTier===2)q.bronze++;else if(c.templateTier===4)q.silver++;
  else if(c.templateTier===8)q.gold++;else if(c.templateTier===1)q.leader++;
  q.carryover+=carryover(c);
 }
 return q;
}
function validRound(tag,index){
 if(tag.rounds===7)return true;if(tag.rounds===0)return false;
 if(index<0||index>2)throw Error('Invalid round index');return (tag.rounds&(1<<index))!==0;
}
function rowToken(state,side,row){
 for(let i=0;i<state.rows.length;i++)if(state.rows[i].side===side&&state.rows[i].row===row)return state.rows[i].token;
 throw Error('Missing row');
}
function rowCount(state,side,row){
 let count=0;for(let i=0;i<state.cards.length;i++)if(state.cards[i].side===side&&state.cards[i].zone===row)count++;return count;
}
function tokenType(token){
 const boon=(token&(128|256))!==0,hazard=(token&(1|2|4|8|16|32|64|512|1024|2048|4096))!==0;
 if(boon&&hazard)return 0;return boon?1:hazard?2:0;
}

// MiniMaxEvaluator.cs and BaseEvaluator.GetGenericPreferenceScore.
class BetaMiniMaxEvaluator {
 constructor(personality){this.personality=personality;this.handlerScore=0;}
 clone(){const e=new BetaMiniMaxEvaluator(this.personality);e.handlerScore=this.handlerScore;return e;}
 handValue(q,aggravator){
  let value=add(add(mul(q.bronze,9),mul(q.silver,12)),mul(q.gold,15));
  value=add(value,mul(q.leader,14));return mul(value,aggravator);
 }
 semanticScore(node,card){
  const p=this.personality;if(isPass(node)||p.semanticTags.length===0)return 0;
  for(let i=0;i<p.semanticTags.length;i++){
   const t=p.semanticTags[i];
   if(t.usage!==1&&has(card.semanticTags,t.id)&&validRound(t,node.state.roundIndex))
    return mul(p.SemanticEvaluatorScoringWeight,t.weight); // Original uses the FIRST matching tag.
  }
  return 0;
 }
 genericPreference(node,card){
  if(node.decision===null)return 0;
  const p=this.personality,d=node.decision;let value=0;
  if(d.row===1)value=add(value,p.MeleePreference);else if(d.row===2)value=add(value,p.RangedPreference);
  else if(d.row===4)value=add(value,p.SiegePreference);
  if(card.type===2)value=add(value,p.EventCardPreference);
  else if(card.type===4)value=add(value,card.templateTier===1?p.LeaderPreference:p.UnitCardPreference);
  else if(card.type===8)value=add(value,p.UnitEventCardPreference);
  if(card.runtimeTier===2)value=add(value,p.BronzePreference);else if(card.runtimeTier===4)value=add(value,p.SilverPreference);
  else if(card.runtimeTier===8)value=add(value,p.GoldPreference);
  const locations=node.locationChoices;
  if(has(card.categories,52)&&locations.length>0){
   let weather=F(p.WeatherCardPreference),first=locations[0];
   // Original flag is always false: same-weather preference is never selected.
   if(first!==null)for(let i=0;i<first.length;i++)if(rowToken(node.state,first[i].side,first[i].row)!==0)
    weather=add(weather,p.PlayWeatherOntoWeatherPreference);
   value=add(value,weather);
  }
  if((card.tokens&128)!==0)value=add(value,p.DisloyalCardPreference);
  if((card.tokens&8)!==0)value=add(value,p.AmbushCardPreference);
  return value;
 }
 rowStacking(node,card){
  const p=this.personality,d=node.decision;
  if(isPass(node)||card===null||d===null||p.RowStackingPreference===0||(d.row&7)===0)return 0;
  let maximum=0,minimum=9,chosen=0;
  for(let row=1;row<=4;row*=2){const count=rowCount(node.parentState,d.side,row);
   if(count>maximum&&count<9)maximum=count;if(count<minimum)minimum=count;if(row===d.row)chosen=count;
  }
  if(maximum===0||maximum===minimum)return 0;if(chosen===maximum)return F(p.RowStackingPreference);
  return mul(p.RowStackingPreference,div(chosen-minimum,maximum-minimum));
 }
 rowEffect(node){
  const d=node.decision;if(isPass(node)||d===null||(d.row&7)===0)return 0;
  const type=tokenType(rowToken(node.parentState,d.side,d.row)),sign=d.side===node.executingPlayerId?1:-1;
  if(type===1)return mul(this.personality.PlayingIntoBoonsPreference,sign);
  if(type===2)return mul(this.personality.PlayingIntoHazardsPreference,sign);return 0;
 }
 evaluate(node){return this.details(node).score;}
 details(node){
  const s=node.state,side=node.executingPlayerId,enemy=3-side;
  if(s.winnerMask!==0&&s.winnerMask!==3)return {score:s.winnerMask===side?100:0,terminal:true};
  const card=isPass(node)?null:findCard(s,node.decision.cardId);
  const own=quality(playableCards(s,side)),opp=quality(playableCards(s,enemy));
  let won=0,lost=0;
  for(let i=0;i<s.roundIndex;i++){
   // Literal original check is EPlayerId.All (0x303), NOT AllPlayers (3).
   // Ordinary drawn rounds therefore receive no round-win credit in this port.
   // Keep this visible for a separately tested correction after the baseline.
   const winner=s.rounds[i].winnerMask;if(winner===0x303){won++;lost++;}
   else if(winner===side)won++;else if(winner===enemy)lost++;
  }
  const round=won===1&&lost===1?3:s.roundId;
  const handMultiplier=round===3?F(1.5):round===2?F(1.2):1;
  const carryMultiplier=round===3?0:round===2?2:1;
  let ownCarry=own.carryover,oppCarry=opp.carryover;
  for(let i=0;i<s.cards.length;i++){const c=s.cards[i];if((c.zone&7)!==0){
   if(c.side===side)ownCarry+=carryover(c);else if(c.side===enemy)oppCarry+=carryover(c);
  }}
  let ownTurn=0,oppTurn=0;
  if(s.startingPlayerId!==s.currentPlayerId){ownTurn=s.startingPlayerId===side?1:-1;oppTurn=s.startingPlayerId===enemy?1:-1;}
  let ownValue=add(this.handValue(own,handMultiplier),mul(won,30));
  ownValue=add(ownValue,mul(ownCarry,carryMultiplier));ownValue=add(ownValue,s.players[side-1].score);
  ownValue=add(ownValue,mul(own.count-opp.count+ownTurn,5));
  let oppValue=add(this.handValue(opp,handMultiplier),mul(lost,30));
  oppValue=add(oppValue,mul(oppCarry,carryMultiplier));oppValue=add(oppValue,s.players[enemy-1].score);
  oppValue=add(oppValue,mul(opp.count-own.count+oppTurn,5));
  let total=add(ownValue,oppValue);
  const semantic=this.semanticScore(node,card),handler=F(node.handlerScore===undefined?this.handlerScore:node.handlerScore);
  const generic=this.genericPreference(node,card),stacking=this.rowStacking(node,card),row=this.rowEffect(node);
  const preference=add(add(add(add(semantic,handler),generic),stacking),row);
  if(preference!==0){ownValue=add(ownValue,mul(total,div(preference,100)));total=add(ownValue,oppValue);}
  return {score:total!==0?mul(div(ownValue,total),100):0,terminal:false,ownValue,oppValue,
   semantic,handler,generic,stacking,row,preference,round,handMultiplier,carryMultiplier};
 }
}

// SemanticPreferenceMulliganPicker.cs (double arithmetic in original).
class BetaSemanticMulliganPicker {
 score(card,personality,cards){
  let value=card.power;
  for(let i=0;i<personality.semanticTags.length;i++){
   const t=personality.semanticTags[i];if(t.usage!==2&&has(card.semanticTags,t.id))value+=F(t.weight);
  }
  if(has(card.semanticTags,2))value-=50;else if(has(card.semanticTags,4))value+=50;
  let duplicates=-1,linked=-1;
  for(let i=0;i<cards.length;i++){
   if(cards[i].templateId===card.templateId)duplicates++;
   if(card.linkedTemplateId!==0&&cards[i].linkedTemplateId===card.linkedTemplateId)linked++;
  }
  if(duplicates>0&&has(card.semanticTags,3))value-=duplicates*51;
  else if(duplicates>0&&has(card.semanticTags,5))value+=duplicates*51;
  if(card.linkedTemplateId!==0&&linked>0){if(has(card.semanticTags,19))value+=linked*55;
   else if(has(card.semanticTags,20))value-=linked*51;}
  return value;
 }
 choose(cards,personality){
  let best=null,lowest=Infinity;
  for(let i=0;i<cards.length;i++){const value=this.score(cards[i],personality,cards);
   if(value<lowest){lowest=value;best=cards[i];}}
  return lowest<=5?best:null;
 }
}
// LowestPowerMulliganPicker.cs: rank CURRENT power, test PRINTED power < 5.
function chooseLowestPowerMulligan(cards){
 let lowest=null;for(let i=0;i<cards.length;i++)if(lowest===null||cards[i].power<=lowest.power)lowest=cards[i];
 return lowest!==null&&lowest.printedPower<5?lowest:null;
}
// BestCardForPersonalityCardPicker.cs.
function chooseBestCardForPersonality(nodes){
 if(nodes.length===0)return null;let best=nodes[0];
 for(let i=1;i<nodes.length;i++)if(nodes[i].revisedScore>best.revisedScore)best=nodes[i];return best;
}
module.exports={BetaMiniMaxEvaluator,BetaSemanticMulliganPicker,chooseLowestPowerMulligan,chooseBestCardForPersonality,
 quality,validRound,MIN_FLOAT};
