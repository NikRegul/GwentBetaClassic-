// 094b: a face-down enemy ambush is searched under public hypotheses instead
// of disabling the reply frontier. Hidden identities must not leak.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const {context:ctx,manifest}=load(path.resolve(process.argv[2]));
ctx.observe=process.argv.includes('--observe');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const cases=[],failures=[];
check=(v,n)=>{checks++;if(!v){failures.push(n);if(!observe)throw Error(n);}};
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()],request:g.requestId,waiting:g.waiting});}
function empty(round){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=round||1;g.match.playerOne.crowns=g.match.playerTwo.crowns=0;g.aiSimDamp=0;
 g.aiStartingDeckOne=[142208,142204,112405,112405];g.aiStartingDeckTwo.Clear();return g;}
let calls=0,peak=0;
const play=CBetaGwentDuelSession.prototype.AiSimPlay,pass=CBetaGwentDuelSession.prototype.Pass;
CBetaGwentDuelSession.prototype.AiSimPlay=function(...a){calls++;return play.apply(this,a);};
CBetaGwentDuelSession.prototype.Pass=function(...a){calls++;return pass.apply(this,a);};
function run(g,first,own){
 const ids=own.map(c=>c.Snapshot().instanceId),values=own.map(c=>g.AiExactTempo(c));
 const model=new CBetaGwentPublicResponseAI();model.Initialize(g,1);
 const job=new CBetaGwentAIReplyTree097();job.Initialize(g,first.Snapshot().instanceId,ids,values,model);
 const before=state(g);let ticks=0;
 while(true){calls=0;const done=job.Step();peak=Math.max(peak,calls);
  check(calls<=1,'one simulated card or pass per callback');
  check(state(g)===before,'search preserves live match, cards, requests and RNG');
  if(done)break;if(++ticks>400)throw Error('frontier stalled');}
 return job;
}
// Position: our unit 6 and a second unit in hand; one hidden enemy card on
// the melee row; enemy has visible units and two unknown cards in hand.
function position(hidden,opts={}){
 const g=empty(opts.round);if(opts.list)g.aiStartingDeckOne=opts.list;if(opts.damp!==undefined)g.aiSimDamp=opts.damp;
 add(g,112405,1,0,1,4);add(g,112405,2,0,1,5);add(g,112405,1,0,2,6);
 const traps=[];for(let i=0;i<(opts.hiddenCount||1);i++)traps.push(add(g,hidden,1,1+i,1,6));
 const first=add(g,112405,8,0,2,6),second=add(g,112405,8,1,2,3);
 add(g,112405,8,0,1,4);add(g,112405,8,1,1,4);add(g,112405,16,0,1,4);add(g,112405,16,1,2,4);
 return {g,first,second,traps};
}
Host.strength=4;Host.matchStrength=[4,4];
// 1. The tree no longer silently exits: hypotheses run and price the trap.
{
 const {g,first,second,traps}=position(142208);
 check((traps[0].Snapshot().tokenMask&8)!==0,'fixture ambush is face down');
 const job=run(g,first,[first,second]);
 check(job.hypCount>0,'hidden board yields public hypotheses');
 check(job.branches>0||job.hypTotal>0,'frontier evaluates replies under a hypothesis');
 cases.push({kind:'morenn-priced',hyp:job.hypCount,result:job.result,trap:job.hypTrap,base:job.hypBase});
 // Real rules: a Morenn hypothesis kills our 6 on play; the price is negative.
 const h=g.AiSimClone();if(typeof h.AiApplyAmbushHypothesis!=='function'){check(false,'hypothesis API exists');}else{h.AiApplyAmbushHypothesis([traps[0].Snapshot().instanceId],[142208],[-1],0);
 const lead=h.AiTrapBalance([traps[0].Snapshot().instanceId]);h.AiSimPlay(first.Snapshot().instanceId);
 check(h.AiTrapBalance([traps[0].Snapshot().instanceId])<lead+6,'Morenn hypothesis really damages the played unit');}
 check(job.result<0,'a plausible Morenn makes the unit play cost something (result '+job.result+')');
}
// 2. Independence: same public view, different real hidden identity.
{
 const out=[142208,142204,142210].map(t=>{const {g,first,second}=position(t);const j=run(g,first,[first,second]);return JSON.stringify([j.hypCount,j.hypTemplates,j.hypTimers,j.result,j.hypTrap,j.hypWeighted]);});
 check(out[0]===out[1]&&out[1]===out[2],'result ignores the concealed identity of the real ambush');
}
// 3. Conservative exits are preserved.
for(const [name,opts,expect] of [
 ['no-ambush-in-list',{list:[112405,112405]},0],
 ['slow-device',{damp:70},0],
 ['three-hidden',{hiddenCount:3},0],
 ['damp50-one-hypothesis',{damp:50},1],
 ['two-hidden',{hiddenCount:2},-1]]){
 const {g,first,second}=position(142208,opts);const job=run(g,first,[first,second]);
 if(expect===0)check(job.hypCount===0&&job.result===0,'old exit kept: '+name);
 else if(expect===1)check(job.hypCount===1,'reduced budget uses one hypothesis');
 else check(job.hypCount>0&&(job.hypTemplates||[]).length===2*job.hypCount,'two hidden cards get paired hypotheses');
 cases.push({name,hyp:job.hypCount,result:job.result});
}
// 4. Strength 3 without the starting list: all five, capped at two.
{
 Host.strength=3;Host.matchStrength=[3,3];
 const {g,first,second}=position(142208);const job=run(g,first,[first,second]);
 check(job.hypCount>=1&&job.hypCount<=2,'strength 3 cap is two hypotheses');
 Host.strength=4;Host.matchStrength=[4,4];
}
// 5. Copies already public leave the pool: both Morenn copies seen -> no Morenn.
{
 const {g,first,second}=position(142204,{list:[142208,142204]});
 const seen=add(g,142208,32,0,1,8);seen.cardState.tokenMask=0;
 const job=run(g,first,[first,second]);
 check(job.hypCount>0&&!(job.hypTemplates||[]).includes(142208),'graveyard Morenn is not hypothesised again');
}
// 6. Short mandatory round also runs with hypotheses.
{
 const {g,first,second}=position(142208,{round:3});g.match.playerOne.crowns=g.match.playerTwo.crowns=1;
 const job=run(g,first,[first,second]);check(job.hypCount>0,'short round hypotheses');cases.push({kind:'short',result:job.result,short:job.shortRound});
}
// 7. Bench-only open information: default off; when set, search copies keep
// the real hidden identities (measurement of the hidden-information ceiling).
{
 const {g,traps}=position(142210);const hand=add(g,113309,8,2,1);
 check(!g.aiOpenInfoBench,'open-information bench is off by default');
 let c=g.AiSimClone();check(c.FindCard(hand.Snapshot().instanceId).Snapshot().runtimeTemplate.templateId!==113309,'normal search hides the real hand card');
 check(c.FindCard(traps[0].Snapshot().instanceId).Snapshot().runtimeTemplate.templateId!==142210,'normal search hides the real ambush');
 g.aiOpenInfoBench=true;c=g.AiSimClone();
 check(c.FindCard(hand.Snapshot().instanceId).Snapshot().runtimeTemplate.templateId===113309,'bench search sees the real hand card');
 check(c.FindCard(traps[0].Snapshot().instanceId).Snapshot().runtimeTemplate.templateId===142210,'bench search sees the real ambush');
 g.aiOpenInfoBench=false;
}
CBetaGwentDuelSession.prototype.AiSimPlay=play;CBetaGwentDuelSession.prototype.Pass=pass;
globalThis.result={checks,failures,cases,peakActions:peak,nativeGameplayVerified:false,observedBaseline:observe};
`,ctx,{timeout:170000});
ctx.result.fingerprint=manifest.fingerprint;
if(process.argv[3]&&!process.argv[3].startsWith('--'))fs.writeFileSync(process.argv[3],JSON.stringify(ctx.result,null,2)+'\n');
console.log(JSON.stringify(ctx.result,null,1));
if(ctx.result.failures.length)process.exitCode=1;
