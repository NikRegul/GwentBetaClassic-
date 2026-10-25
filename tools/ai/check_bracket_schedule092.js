'use strict';
const assert=require('assert/strict'),s=require('./bracket_schedule092.js');
let pool=Array.from({length:46},(_,i)=>54+i),checks=0;
function check(v){assert.ok(v);checks++;}
for(const size of [46,92])for(const cycles of [1,2]){
 pool=Array.from({length:size},(_,i)=>54+i);
 const p=s.plan(pool,cycles,923101600),again=s.plan(pool,cycles,923101600);
 assert.deepEqual(p,again);checks++;check(JSON.stringify(p)!==JSON.stringify(s.plan(pool,cycles,923101601)));
 check(p.brackets.length===23*cycles&&p.nodes.length===(size-1)*23*cycles);
 const byes=new Map(pool.map(d=>[d,0])),done=new Map(),used=new Set();
 for(const b of p.brackets)for(const d of b.byes)byes.set(d,byes.get(d)+1);
 for(const n of p.nodes){
  for(const seed of n.seeds){check(seed>0&&!used.has(seed));used.add(seed);}
  const task=s.available(n,done);check(task&&task.a!==task.b);
  const winnerDeck=Math.min(task.a,task.b),games=Array.from({length:4},(_,i)=>({left:i%2?task.b:task.a,right:i%2?task.a:task.b,seed:task.seeds[i>>1],winner:winnerDeck===(i%2?task.b:task.a)?1:2,milliseconds:1}));
  const r={...task,games,pointsA:s.points(games,task.a),winnerDeck,loserDeck:Math.max(task.a,task.b),lotUsed:false};
  s.validate(task,r);checks++;done.set(n.id,r);
  const wrong=JSON.parse(JSON.stringify(r));wrong.games[0].seed++;assert.throws(()=>s.validate(task,wrong));checks++;
 }
 check(Array.from(byes.values()).every(n=>n===9*cycles));
 for(const b of p.brackets){const records=Array.from(done.values()).filter(r=>r.bracket===b.id);check(records.length===size-1);check(done.get(b.final).winnerDeck===54);check(new Set(records.map(r=>r.loserDeck)).size===size-1);}
}
const task={...s.plan(pool,1,923101600).nodes[0],a:54,b:55};
const games=Array.from({length:12},(_,i)=>({left:i%2?55:54,right:i%2?54:55,seed:task.seeds[i>>1],winner:3,milliseconds:1}));
const winner=task.lot?55:54,r={...task,games,pointsA:6,winnerDeck:winner,loserDeck:winner===54?55:54,lotUsed:true};
s.validate(task,r);checks++;assert.throws(()=>s.validate(task,{...r,games:games.slice(0,6),pointsA:3}));checks++;
for(const seed of [0,4294967296]){assert.throws(()=>s.plan(pool,1,seed));checks++;}
console.log(JSON.stringify({checks,balancedByes:true,completeEliminationGraphs:true,deterministicSeedBanks:true,strictResumeRecords:true}));
