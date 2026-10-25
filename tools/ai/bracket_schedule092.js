'use strict';
// Seed banks, byes and every possible bracket node are committed before play.
function plan(pool,cycles,seed,maxPairs=6,benchmark=false){
 if(![46,92].includes(pool.length)||new Set(pool).size!==pool.length||!Number.isInteger(cycles)||cycles<1||!Number.isInteger(seed)||seed<1||seed>0xffffffff||!Number.isInteger(maxPairs)||maxPairs<2||maxPairs>12)throw Error('Invalid bracket plan');
 const size=pool.length,mainSize=size===46?32:64,byeCount=mainSize*2-size,qualifying=(size-byeCount)/2;
 let state=seed>>>0;const rnd=()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>=0;};
 const shuffle=a=>{for(let i=a.length-1;i>0;i--){const j=rnd()%(i+1);[a[i],a[j]]=[a[j],a[i]];}return a;};
 const nodes=[],brackets=[];
 function node(id,bracket,stage,a,b){const seeds=Array.from({length:maxPairs},rnd);const n={id,bracket,stage,a,b,seeds,lot:rnd()%2};nodes.push(n);return {winner:id};}
 if(benchmark){for(let i=0;i<size;i++)node('speed-'+i,0,0,{deck:pool[i]},{deck:pool[(i+19)%size]});return {benchmark:true,nodes,brackets:[]};}
 for(let cycle=0;cycle<cycles;cycle++){
  const rotation=shuffle(pool.slice());
  for(let r=0;r<23;r++){
   const bracket=cycle*23+r,prefix='b'+String(bracket).padStart(3,'0');
   const byes=Array.from({length:byeCount},(_,j)=>rotation[(r*byeCount+j)%size]),byeSet=new Set(byes);
   const qualifiers=shuffle(pool.filter(d=>!byeSet.has(d))),slots=byes.map(deck=>({deck}));
   for(let i=0;i<qualifying;i++)slots.push(node(prefix+'-q'+String(i).padStart(2,'0'),bracket,0,{deck:qualifiers[i*2]},{deck:qualifiers[i*2+1]}));
   shuffle(slots);let level=slots;
   for(let stage=1;level.length>1;stage++){
    const next=[];for(let i=0;i<level.length;i+=2)next.push(node(prefix+'-r'+stage+'-'+String(i/2).padStart(2,'0'),bracket,stage,level[i],level[i+1]));
    level=next;
   }
   brackets.push({id:bracket,cycle,byes,final:level[0].winner});
  }
 }
 return {benchmark:false,nodes,brackets};
}
function resolve(ref,done){return ref.deck??done.get(ref.winner)?.winnerDeck??null;}
function available(n,done){const a=resolve(n.a,done),b=resolve(n.b,done);return a&&b?{...n,a,b}:null;}
function points(games,a){return games.reduce((n,g)=>n+(g.winner===3?.5:g.winner===(g.left===a?1:2)?1:0),0);}
function validate(n,r){
 if(['id','bracket','stage','a','b'].some(k=>r[k]!==n[k])||!Array.isArray(r.games)||r.games.length<4||r.games.length>n.seeds.length*2||r.games.length%2)throw Error('Invalid series identity '+n.id);
 for(let i=0;i<r.games.length;i++){
  const g=r.games[i],reverse=i%2===1;
  if(g.error||![1,2,3].includes(g.winner)||g.seed!==n.seeds[Math.floor(i/2)]||g.left!==(reverse?n.b:n.a)||g.right!==(reverse?n.a:n.b))throw Error('Invalid played game '+n.id);
  if(i%2===1&&i>=3&&i<r.games.length-1&&points(r.games.slice(0,i+1),n.a)!==(i+1)/2)throw Error('Continued a decided series '+n.id);
 }
 const p=points(r.games,n.a),tied=p===r.games.length/2;
 if(tied&&r.games.length!==n.seeds.length*2)throw Error('Unfinished tied series '+n.id);
 const winner=tied?(n.lot?n.b:n.a):(p>r.games.length/2?n.a:n.b);
 if(r.winnerDeck!==winner||r.loserDeck!==(winner===n.a?n.b:n.a)||r.lotUsed!==tied||r.pointsA!==p)throw Error('Wrong series winner '+n.id);
 return r;
}
module.exports={plan,resolve,available,points,validate};
