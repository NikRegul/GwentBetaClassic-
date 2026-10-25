// Three real actions, resource limits, hidden-information isolation and UI work.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),ctx=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function position(enemy=35){
 const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.match.playerOne.hasPassed=true;
 add(g,112405,1,0,1,enemy);[152205,152310,152310].forEach((t,i)=>add(g,t,8,i,2));
 for(let i=0;i<2;i++)add(g,152303,32,i,2);
 return g;
}
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),draws:g.random.DrawCount(),request:g.requestId,weather:g.weather.hazards});}
function plan(g){const actions=g.live.filter(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8).map(c=>({id:c.Snapshot().instanceId,gain:g.AiCardTempo(c,true,0,0),cards:1,reserve:g.AiReserveCost(c.Definition())}));
 const job=new CBetaGwentAIChase188();job.Initialize(g,actions,g.Score(1)+1,Math.max(2,Math.trunc(10*(100-g.aiSimDamp)/100)));
 const play=CBetaGwentDuelSession.prototype.AiSimPlay;let calls=0,ticks=0,peak=0;
 CBetaGwentDuelSession.prototype.AiSimPlay=function(id){calls++;return play.call(this,id);};
 try{let done;do{calls=0;done=job.Step();peak=Math.max(peak,calls);if(++ticks>100)throw Error('stalled chase');}while(!done);}
 finally{CBetaGwentDuelSession.prototype.AiSimPlay=play;}
 check(peak<=1,'each chase callback resolves at most one play');
 return {best:job.best,ticks,peak};
}
const rows=[];
for(const strength of [2,3,4])for(const damp of [0,40,70,100]){
 Host.strength=strength;Host.matchStrength=[strength,strength];
 const g=position();g.aiSimDamp=damp;const before=state(g),r=plan(g);
 check(state(g)===before,'search preserves live cards, requests and RNG '+strength+'/'+damp);
 if(damp<100){
  check(r.best.reachable&&r.best.actions===3&&r.best.cards===3,'resolves three-action graveyard combo '+strength+'/'+damp);
  check(g.FindCard(r.best.firstId).TemplateId()===152205,'strengthens grave before both resurrections');
 }
 if(damp===100)check(r.best.reachable||r.best.firstId!==0,'unknown search keeps a legal fallback');
 const impossible=position(80);impossible.aiSimDamp=damp;const no=plan(impossible);
 check(!no.best.reachable&&no.best.firstId!==0,'does not invent a win or discard fallback');
 rows.push({strength,damp,...r});
}
for(const strength of [2,3,4]){
 Host.strength=strength;Host.matchStrength=[strength,strength];const g=position();g.aiSimDamp=40;
 for(let n=0;n<5&&!g.Snapshot().matchWinnerMask;n++)check(g.OpponentStep(),'combo action completes');
 check(g.Snapshot().matchWinnerMask===2,'whole deciding round won on difficulty '+strength);
 const optional=position();optional.match.roundNumber=1;optional.match.playerOne.crowns=optional.match.playerTwo.crowns=0;
 check(optional.OpponentStep()&&optional.match.playerTwo.hasPassed,'three-card search does not force optional overcommit');
}
// A large lead is not outside the one-card response envelope merely because
// both hands are equal. Optional R2 and survival decisions remain distinct.
check(BetaGwentAIRoundDecision(1,0,0,30,5,5,8,50,false)===0,'dangerous response prevents unconditional 26-point pass');
check(BetaGwentAIRoundDecision(1,0,0,40,5,5,8,25,false)===1,'safe large lead still passes');
check(BetaGwentAIRoundDecision(1,0,0,40,4,5,8,25,false)===1,'red coin can recover card disadvantage through pass');
check(BetaGwentAIRoundDecision(2,0,1,40,5,5,8,25,false)===0,'survival never uses optional-round pass');
check(BetaGwentAIPressureDiscount(12,8,25,0)===8,'same reply count removes raw eight-point overkill');
check(BetaGwentAIPressureDiscount(12,12,25,0)===12,'larger same-bucket body gets no extra pressure credit');
check(BetaGwentAIPressureDiscount(24,9,25,0)===5,'crossing a reply threshold keeps its useful tempo');
check(BetaGwentAIPressureDiscount(1,2,25,0)===0,'small safety margin retains useful points');
// A fixed human line exposes the match-level cost of spending a 12-point
// gold instead of an eight-point bronze with the same response tax.
for(const strength of [2,3,4]){
 Host.strength=strength;Host.matchStrength=[strength,strength];const g=fixture();
 g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.aiStartingDeckOne=[112405,112405,112405,112405,112405];g.aiStartingDeckTwo.Clear();
 g.match.roundNumber=1;g.aiSimDamp=40;g.archetypeAI.Initialize(g,[],54,200164);
 function body(t,z,n,side,p){const c=add(g,t,z,n,side);c.power.ResetTemplatePower(p,0);return c;}
 body(112405,1,0,2,22);body(112405,1,0,1,10);
 const gold=body(112103,8,0,2,12),cheap=[];
 for(let i=0;i<4;i++)cheap.push(body(112405,8,i+1,2,8));
 const enemy=[30,8,8,9,9].map((power,i)=>body(112405,8,i,1,power));
 check(g.OpponentStep(),'economical pressure resolves on difficulty '+strength);
 check(gold.Snapshot().locationMask===8&&cheap.some(c=>c.Snapshot().locationMask!==8),'same reply tax preserves the gold on difficulty '+strength);
 check(g.Pass(1),'human concedes R1 after the AI opening');
 if(!g.IsWaitingRound())check(g.OpponentStep(),'AI finishes already won R1');
 for(let i=0;i<50&&!g.Snapshot().matchWinnerMask;i++){
  const m=g.Snapshot();
  if(g.IsWaitingRound()){check(g.BeginNextRound(),'advance human-line round');continue;}
  if(g.IsMulligan()){__mulligan(g);continue;}
  if(m.currentPlayerId===2){check(g.OpponentStep(),'AI continues complete human-line match');continue;}
  const c=m.roundNumber===2?enemy.find(c=>c.Snapshot().locationMask===8&&c.Snapshot().power.currentPower===30):enemy.find(c=>c.Snapshot().locationMask===8);
  if(c)check(g.Play(1,c.Snapshot().instanceId,1),'human plays the fixed public continuation');
  else check(g.Pass(1),'human passes after fixed continuation');
 }
 check(g.Snapshot().matchWinnerMask===2,'saved finisher wins the complete match 36:34 on difficulty '+strength);
}
globalThis.report={checks,rows,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(ctx.report,null,2));
console.log(JSON.stringify(ctx.report));
