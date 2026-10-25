// Independent exact arithmetic oracle for harder six-card public finals.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js'),{context:ctx,manifest}=load(path.resolve(process.argv[2]));
const option=(name,fallback)=>Number((process.argv.find(a=>a.startsWith(name+'='))||'').split('=')[1]||fallback);
ctx.searchOracleSeed=option('--seed',923051091);ctx.searchOracleCases=option('--cases',40);
if(!Number.isSafeInteger(ctx.searchOracleSeed)||!Number.isSafeInteger(ctx.searchOracleCases)||ctx.searchOracleCases<1||ctx.searchOracleCases>1000)throw Error('Invalid oracle schedule');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
check=(v,n)=>{if(!v)throw Error(n);checks++;};
function solve(s,memo=new Map()){
 const key=JSON.stringify(s);if(memo.has(key))return memo.get(key);
 if(s.p[0]&&s.p[1])return Math.sign(s.b[1].reduce((a,b)=>a+b,0)-s.b[0].reduce((a,b)=>a+b,0));
 let best=s.a===1?-2:2;
 for(let action=-1;action<s.h[s.a].length;action++){
  const n=JSON.parse(JSON.stringify(s));
  if(action<0)n.p[n.a]=true;else{const card=n.h[n.a].splice(action,1)[0];
   if(card==='S'){const max=Math.max(0,...n.b[0],...n.b[1]);n.b=n.b.map(b=>b.filter(p=>p!==max));}else n.b[n.a].push(card);}
  n.a=n.p[1-n.a]?n.a:1-n.a;const value=solve(n,memo);best=s.a===1?Math.max(best,value):Math.min(best,value);
 }
 memo.set(key,best);return best;
}
function after(model,index){const n=JSON.parse(JSON.stringify(model));if(index<0)n.p[1]=true;
 else{const c=n.h[1].splice(index,1)[0];if(c==='S'){const max=Math.max(0,...n.b[0],...n.b[1]);n.b=n.b.map(b=>b.filter(p=>p!==max));}else n.b[1].push(c);}
 n.a=n.p[0]?1:0;return n;}
let rng=searchOracleSeed;function rnd(n){rng^=rng<<13;rng^=rng>>>17;rng^=rng<<5;return(rng>>>0)%n;}
const models=[];for(let i=0;i<searchOracleCases;i++)models.push({a:1,p:[false,false],b:[[1+rnd(17),1+rnd(12)],[1+rnd(17),1+rnd(12)]],h:[['S',1+rnd(17),1+rnd(17)],[i%3?'S':1+rnd(17),1+rnd(17),1+rnd(17)]]});
const play=CBetaGwentDuelSession.prototype.AiSimPlay;let calls=0,peak=0;CBetaGwentDuelSession.prototype.AiSimPlay=function(...a){calls++;return play.apply(this,a);};
const cases=[];
for(const damp of [40,70])for(let number=0;number<models.length;number++){
 const model=models[number],g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.aiSimDamp=damp;
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;const own=[];
 for(let side=0;side<2;side++){model.b[side].forEach((v,i)=>add(g,112405,1,i,side+1,v));model.h[side].forEach((v,i)=>{
  const c=add(g,v==='S'?113309:112405,8,i,side+1,v==='S'?undefined:v);c.AddTokens(64);if(side===1)own.push(c.Snapshot().instanceId);});}
 const original=JSON.stringify({m:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:g.random.DrawCount()}),job=new CBetaGwentAIEndgame097();job.Initialize(g);check(job.supported,'six-card model supported');let ticks=0;
 while(true){calls=0;const ready=job.Step();peak=Math.max(peak,calls);check(calls<=1,'one simulated play per callback');if(ready)break;if(++ticks>500)throw Error('search stalled');}
 check(job.nodes<=job.limit,'same node budget');check(JSON.stringify({m:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:g.random.DrawCount()})===original,'search preserves source');
 const truth=solve(model);if(job.complete){check(job.result===truth,'complete search result agrees with independent full minimax');const i=job.firstId===0?-1:own.indexOf(job.firstId);check(i>=0||job.firstId===0,'first move exists');check(solve(after(model,i))===truth,'chosen first move realizes the true result');}
 cases.push({number,damp,nodes:job.nodes,limit:job.limit,complete:job.complete,result:job.result,truth,ticks});
}
CBetaGwentDuelSession.prototype.AiSimPlay=play;
globalThis.report={checks,cases,seed:searchOracleSeed,summary:[40,70].map(damp=>({damp,complete:cases.filter(c=>c.damp===damp&&c.complete).length,total:models.length,nodes:cases.filter(c=>c.damp===damp).reduce((s,c)=>s+c.nodes,0)})),peakSearchPlays:peak,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:240000});const report={fingerprint:manifest.fingerprint,...ctx.report};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify({fingerprint:manifest.fingerprint,checks:report.checks,summary:report.summary,peakSearchPlays:report.peakSearchPlays}));
