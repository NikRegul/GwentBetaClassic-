'use strict';
// Observer for the frozen tournament runner. No added clock/RNG calls and no
// policy fallback. The callback at the first force-stop permits deterministic
// replay of a wall-time-limited search without recording every clock sample.
function createRecorder(Controller){
 const original=Controller.prototype.step,forcedAt=new WeakMap();let active=null;
 function record(c,error=null){
  if(!active)return;
  try{
  const m=c.live.Snapshot(),r={schema:1,side:m.currentPlayerId,round:m.roundNumber,profile:c.personality.name,
   searchCallbacks:c.searchCallbacks,forceAtCallback:forcedAt.get(c)??null,
   finishReason:c.search.finishReason,completedDepth:c.search.completedDepth,
   decision:c.chosen?.decision?{...c.chosen.decision}:null,playmakerError:c.playmakerError||null};
  if(error)r.exception=String(error.stack||error);
  if(error||c.playmakerError){r.position=c.runtime.serialize(c.live);r.positionPhase=error?'at-exception':'before-live-replay';}
  active.push(r);
  }catch(diagnosticError){active.push({schema:1,diagnosticError:String(diagnosticError.stack||diagnosticError)});}
 }
 Controller.prototype.step=function(...args){
  if(!active)return original.apply(this,args);
  const before=this.searchCallbacks,wasForced=this.forceRequested;let result;
  try{result=original.apply(this,args);}catch(error){record(this,error);throw error;}
  if(!wasForced&&this.forceRequested)forcedAt.set(this,before);
  if(result.phase==='pick')record(this);
  return result;
 };
 return {play(fn,...args){
  if(active)throw Error('Nested diagnostic match');
  active=[];try{const result=fn(...args);return {...result,betaDecisionDiagnostics:active};}finally{active=null;}
 },restore(){Controller.prototype.step=original;}};
}
module.exports={createRecorder};
