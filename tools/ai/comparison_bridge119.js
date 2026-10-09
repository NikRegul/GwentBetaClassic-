module.exports=String.raw`
function pack(g){
 const nodes=[],seen=new Map();
 function visit(v){if(v===undefined)return {u:1};if(v===null||typeof v!=='object')return v;
  if(seen.has(v))return {r:seen.get(v)};const i=nodes.length;seen.set(v,i);
  const node={type:Array.isArray(v)?'Array':v.constructor.name,fields:{}};nodes.push(node);
  for(const k of Object.keys(v)){
   if(k==='bgCloneEpoch'||k==='bgCloneRef'||k==='aiSimCloner'||k==='visualFrames')continue;
   node.fields[k]=visit(v[k]);}
  return {r:i};}
 const root=visit(g);return JSON.stringify({root,nodes,mem:__mem.get(g),engineRandom:randomState});
}
function unpack(text){const data=JSON.parse(text),objects=data.nodes.map(n=>{
 if(n.type==='Array')return [];if(n.type==='Object')return {};
 if(!/^[SC]BetaGwent\w+$/.test(n.type))throw Error('Unexpected state type '+n.type);
 const Kind=eval(n.type);return new Kind();});
 function value(v){if(v&&typeof v==='object'){if(v.u)return undefined;if('r' in v)return objects[v.r];}return v;}
 for(let i=0;i<objects.length;i++)for(const [k,v] of Object.entries(data.nodes[i].fields))objects[i][k]=value(v);
 const g=value(data.root);if(data.mem)__mem.set(g,data.mem);randomState=data.engineRandom;g.recordVisuals=false;__context(g);return g;
}
let active=null,randomState=1;
Host.tunes=[{},{}];Host.matchStrength=[4,4];Host.strength=4;Host.log=null;
Host.random=()=>{randomState^=randomState<<13;randomState>>>=0;randomState^=randomState>>>17;randomState>>>=0;randomState^=randomState<<5;randomState>>>=0;return randomState/4294967296;};
globalThis.bridge={
 setLog(callback){Host.log=callback;},
 setTunes(tunes){Host.tunes=[tunes,tunes];},
 policyValue(preset,index){return BetaGwentAITrainingWeight(preset,index);},
 initialize(left,right,seed){randomState=seed>>>0||1;Host.seatIndex=1;__simDepthHost=0;
  active=new CBetaGwentDuelSession();active.AiMulligan=()=>{};
  if(!active.InitializeWithPresets(left,right))throw Error('invalid preset');delete active.AiMulligan;
  active.recordVisuals=false;active.aiSimDamp=40;return pack(active);},
 load(text){active=unpack(text);},dump(){return pack(active);},
 view(){const s=active.Snapshot();return {winner:s.matchWinnerMask,actor:__reversed(active)?0:1,
   mulligan:Boolean(active.IsMulligan()),pending:Boolean(active.IsPending()),waiting:Boolean(active.IsWaitingRound()),current:s.currentPlayerId,fatal:Boolean(active.IsFatal()),message:active.GetMessage(),round:s.roundNumber,score:[active.Score(1),active.Score(2)],hand:[active.CountLocation(1,8),active.CountLocation(2,8)],leader:[Boolean(active.LeaderAvailable(1)),Boolean(active.LeaderAvailable(2))],request:active.requestId,reversed:Boolean(__reversed(active))};},
 initialMulligan(){__context(active);active.AiMulligan(active.mulliganBudget);active.RefreshMulligan();},
 mirror(){__swap(active);const m=__mem.get(active);m.rev=false;m.slots.reverse();__context(active);},
 step(){if(active.IsFatal())throw Error(active.GetMessage());
  if(active.IsMulligan()){__mulligan(active);return;}
  if(active.IsPending()){if(!__pending(active))throw Error('unresolved choice '+active.GetMessage());return;}
  if(active.IsWaitingRound()){if(!active.BeginNextRound())throw Error('round transition');return;}
  if(active.Snapshot().currentPlayerId===1)__swap(active);
  __context(active);if(!active.OpponentStep())throw Error('decision rejected '+active.GetMessage());
 },swap(){__swap(active);}
};`;
