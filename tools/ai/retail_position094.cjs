'use strict';
// Compare logged observables only. A match does not establish unlogged queues,
// AI caches, host timing or the historical executable's identity.
function header(g){
 const m=g.Snapshot();
 return {presetOne:g.presetOne,presetTwo:g.presetTwo,round:m.roundNumber,current:m.currentPlayerId,crowns:[m.playerOne.crowns,m.playerTwo.crowns].join(','),
  passed:[m.playerOne.hasPassed?1:0,m.playerTwo.hasPassed?1:0].join(','),
  leaders:[g.LeaderAvailable(1)?1:0,g.LeaderAvailable(2)?1:0].join(','),
  weather:[1,2].flatMap(s=>[1,2,4].map(r=>g.WeatherToken(s,r))).join(',')+',',cardCount:g.live.length};
}
function compareHeader(g,expected){
 const actual=header(g),errors=[];
 for(const [key,value]of Object.entries(actual))if(expected[key]!==undefined&&String(expected[key])!==String(value))errors.push({key,expected:expected[key],actual:value});
 return errors;
}
function card(g,id){
 const c=g.FindCard(id);if(!c)return null;const s=c.Snapshot();
 return [s.instanceId,s.runtimeTemplate.templateId,s.positionPlayerId,s.ownerId,s.locationMask,s.locationIndex,
  s.power.currentPower,s.power.basePower,s.power.armor,s.tokenMask,s.timerValue,s.runtimeTierMask,s.canBePlayed?1:0];
}
function compareCard(g,tuple){
 const actual=card(g,tuple[0]);return actual&&actual.length===tuple.length&&actual.every((x,i)=>x===tuple[i])?[]:[{id:tuple[0],expected:tuple,actual}];
}
function recoverShellPass(g,expected){
 // The native menu automatically passes an empty hand with a spent leader.
 // Only the caller's explicit recovery mode may invoke this transition.
 const m=g.Snapshot(),mismatch=compareHeader(g,expected);
 if(!mismatch.length||mismatch.some(e=>!['current','passed'].includes(e.key))
  ||String(expected.current)!=='2'||expected.passed!=='1,0'||m.currentPlayerId!==1
  ||m.playerOne.hasPassed||m.playerTwo.hasPassed||g.CountLocation(1,8)!==0||g.LeaderAvailable(1)
  ||g.IsPending()||g.IsFatal()||g.IsWaitingRound()||m.matchWinnerMask)return null;
 if(!g.Pass(1))return null;
 return {action:'automatic-empty-hand-pass',side:1,inferredFromExplicitPosition:true};
}
module.exports={header,card,compareHeader,compareCard,recoverShellPass};
