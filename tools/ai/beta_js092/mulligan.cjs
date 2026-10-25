/* AIModule_TreeSearch.DoMulliganRequest, using the original direct-JS pickers.
 * One exchange/finish operation per call. Shared engine owns draw/blacklist/RNG.
 * No current-policy mulligan/keep-value/AI methods are called. */
'use strict';
const {stateFromSession}=require('./session.cjs');
const {BetaSemanticMulliganPicker,chooseLowestPowerMulligan}=require('./core.cjs');
const semantic=new BetaSemanticMulliganPicker();
function chooseMulligan(cards,personality){
 switch(personality.MulliganPickerType){
 case 'SemanticPreference':return semantic.choose(cards,personality);
 case 'LowestPower':return chooseLowestPowerMulligan(cards);
 default:throw Error('Original mulligan picker not ported: '+personality.MulliganPickerType);
 }
}
function stepMulligan(game,personality,record=null,replay=null){
 if(!game.mulligan)throw Error('No mulligan request');
 const side=game.RequestDecisionSide(),requestId=game.requestId;
 if(replay!==null&&replay.side!==side)throw Error('Stored original mulligan seat changed');
 if(!game.IsExternalPolicy(side))throw Error('Mulligan seat not externally controlled: '+side);
 // Player.GetMulliganableCards == GetPlayableCardsFromHand(false). In particular,
 // do not import current policy's reserved-card or summoning heuristics here.
 const cards=stateFromSession(game).cards.filter(c=>c.side===side&&c.zone===8&&c.playable);
 const selected=replay===null?chooseMulligan(cards,personality):cards.find(c=>c.id===replay.cardId);
 if(replay!==null&&replay.cardId!==0&&!selected)throw Error('Stored original mulligan choice no longer legal');
 const cardId=selected?selected.id:0;
 const ok=cardId===0?game.FinishMulligan(requestId):game.SelectMulligan(requestId,cardId);
 if(!ok||game.IsFatal())throw Error('Shared engine rejected Beta mulligan: '+cardId);
 const decision={side,requestId,cardId};if(record!==null)record.push(decision);
 return decision;
}
module.exports={chooseMulligan,stepMulligan};
