// Isolated UCT prototype on public body/Scorch finals. This is NOT a game AI port.
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const out=path.resolve(process.argv[2]);
function rng(seed){let x=seed;return n=>{x^=x<<13;x^=x>>>17;x^=x<<5;return(x>>>0)%n;};}
const random=rng(923052191),models=[];
for(let i=0;i<120;i++)models.push({a:1,p:[false,false],b:[[1+random(17),1+random(12)],[1+random(17),1+random(12)]],h:[['S',1+random(17),1+random(17)],[i%3?'S':1+random(17),1+random(17),1+random(17)]]});
const terminal=s=>s.p[0]&&s.p[1];
const score=s=>Math.sign(s.b[1].reduce((a,b)=>a+b,0)-s.b[0].reduce((a,b)=>a+b,0));
const actions=s=>[-1,...s.h[s.a].map((_,i)=>i)];
function next(s,action){const n=JSON.parse(JSON.stringify(s));
 if(action<0)n.p[n.a]=true;else{const c=n.h[n.a].splice(action,1)[0];if(c==='S'){const highest=Math.max(0,...n.b[0],...n.b[1]);n.b=n.b.map(b=>b.filter(p=>p!==highest));}else n.b[n.a].push(c);}
 n.a=n.p[1-n.a]?n.a:1-n.a;return n;
}
function solve(s,memo=new Map()){if(terminal(s))return score(s);const k=JSON.stringify(s);if(memo.has(k))return memo.get(k);
 const values=actions(s).map(a=>solve(next(s,a),memo)),v=s.a===1?Math.max(...values):Math.min(...values);memo.set(k,v);return v;}
function mcts(state,limit,seed){const random=rng(seed);let transitions=0,rollouts=0;
 const node=(s,parent=null,action=null)=>({s,parent,action,n:0,w:0,children:[],untried:terminal(s)?[]:actions(s)}),root=node(state);
 while(transitions<limit){let n=root;
  while(!terminal(n.s)&&!n.untried.length&&n.children.length){
   const sign=n.s.a===1?1:-1;
   n=n.children.reduce((best,c)=>{const u=sign*c.w/c.n+Math.SQRT2*Math.sqrt(Math.log(Math.max(1,n.n))/c.n);return!best||u>best.u?{node:c,u}:best;},null).node;
  }
  if(!terminal(n.s)&&n.untried.length){const i=random(n.untried.length),a=n.untried.splice(i,1)[0],child=node(next(n.s,a),n,a);transitions++;n.children.push(child);n=child;}
  let s=n.s;
  while(!terminal(s)&&transitions<limit){const a=actions(s);s=next(s,a[random(a.length)]);transitions++;}
  // A cutoff is not a terminal result and contributes no fabricated reward.
  if(!terminal(s))break;
  const value=score(s);rollouts++;while(n){n.n++;n.w+=value;n=n.parent;}
 }
 const best=root.children.filter(c=>c.n>0).reduce((a,b)=>!a||b.n>a.n?b:a,null);
 return{action:best?best.action:-1,transitions,rollouts};
}
const reference=JSON.parse(fs.readFileSync(path.join(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/public-search-p13-fresh120.json'),'utf8'));
assert.equal(reference.seed,923052191);
const cases=[],summary=[];
for(const limit of [76,153])for(const seed of [923057101,923057102,923057103]){
 let optimal=0;
 for(let i=0;i<models.length;i++){
  const s=models[i],truth=solve(s),record=reference.cases.find(c=>c.number===i);
  assert.equal(truth,record.truth,'same independent oracle models as native-rule-verified public search audit');
  const choice=mcts(s,limit,seed+i*997),value=solve(next(s,choice.action));assert.ok(choice.transitions<=limit);optimal+=value===truth?1:0;
  cases.push({number:i,limit,seed,truth,selectedValue:value,optimal:value===truth,...choice});
 }
 summary.push({limit,seed,optimal,total:models.length});
}
const report={kind:'isolated-arithmetic-UCT-prototype',notGameAIPort:true,hiddenInformationTested:false,nativeFrameTimesMeasured:false,modelSeed:923052191,selection:'adversarial UCT; most-visited root action',rollout:'uniform legal actions until true terminal; discard final unfinished rollout',summary,cases};
fs.writeFileSync(out,JSON.stringify(report,null,2));console.log(JSON.stringify({kind:report.kind,notGameAIPort:true,summary}));
