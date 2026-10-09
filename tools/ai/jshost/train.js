"use strict";
const fs=require('fs'),path=require('path'),os=require('os'),{fork}=require('child_process');
const {SPACE,atomic,validate}=require('./contract.js');
const arg=(k,d)=>{const i=process.argv.indexOf('--'+k);return i>0?process.argv[i+1]:d;};
if(process.argv[2]==='--child'){
 const h=require('./selfplay.js').load(process.argv[3]);
 const deckPool=JSON.parse(fs.readFileSync(path.join(path.dirname(process.argv[3]),'manifest.json'),'utf8')).presets;
 process.on('message',job=>{
  const out={blocks:[],errors:[],perDeck:{},A:0,B:0,D:0,E:0};
  for(const i of job.indices){
   const a=deckPool[i%deckPool.length];let bi=(i*17+1+Math.floor(i/deckPool.length)+job.seed)%deckPool.length;
   if(a===deckPool[bi])bi=(bi+1)%deckPool.length;const b=deckPool[bi];
   const deal=(job.seed*7919+i*104729)>>>0;let points=0;
   for(let mode=0;mode<4;mode++){
    const swapped=!!(mode&1),flipped=!!(mode&2),candidateLeft=swapped===flipped;
    const L=swapped?b:a,R=swapped?a:b;
    h.Host.tunes=candidateLeft?[job.A,job.B]:[job.B,job.A];
    const r=h.play(L,R,deal,job.strength,job.strength),deck=candidateLeft?L:R;
    const d=out.perDeck[deck]||(out.perDeck[deck]={wins:0,losses:0,draws:0});
    if(r.error){out.E++;out.errors.push({a,b,deal,mode,error:r.error});continue;}
    if(r.winner===(candidateLeft?1:2)){out.A++;d.wins++;points++;}
    else if(r.winner===(candidateLeft?2:1)){out.B++;d.losses++;}
    else{out.D++;d.draws++;points+=.5;}
   }
   out.blocks.push([i,points/4]);
  }
  process.send(out);
 });
}else{
 let pool=[];
 function close(){for(const worker of pool)worker.kill();pool=[];}
 process.on('SIGINT',()=>{close();process.exit(130);});
 process.on('SIGTERM',()=>{close();process.exit(143);});
 async function run(rules,shards,strength,seed,A,B,pairs){
  if(!pool.length)for(let i=0;i<shards;i++)pool.push(fork(__filename,['--child',rules]));
  const parts=pool.map(()=>[]);for(let i=0;i<pairs;i++)parts[i%pool.length].push(i);
  const results=await Promise.all(pool.map((worker,k)=>new Promise((resolve,reject)=>{
   if(!parts[k].length)return resolve(null);
   const timer=setTimeout(()=>done(Error('Worker timeout; checkpoint retained')),Math.max(300000,parts[k].length*120000));
   const message=o=>done(null,o),error=e=>done(e),exit=code=>done(Error('Worker exited '+code));
   function done(e,o){clearTimeout(timer);worker.removeListener('message',message);worker.removeListener('error',error);worker.removeListener('exit',exit);e?reject(e):resolve(o);}
   worker.once('message',message);worker.once('error',error);worker.once('exit',exit);
   worker.send({indices:parts[k],strength,seed,A,B},e=>{if(e)done(e);});
  })));
  const r={A:0,B:0,D:0,E:0,errors:[],blocks:[],perDeck:{}};
  for(const o of results.filter(Boolean)){
   for(const k of ['A','B','D','E'])r[k]+=o[k];r.errors.push(...o.errors);r.blocks.push(...o.blocks);
   for(const [d,v] of Object.entries(o.perDeck)){const t=r.perDeck[d]||(r.perDeck[d]={wins:0,losses:0,draws:0});for(const k of ['wins','losses','draws'])t[k]+=v[k];}
  }
  r.blocks.sort((a,b)=>a[0]-b[0]);const n=r.blocks.length;
  r.mean=r.blocks.reduce((s,b)=>s+b[1],0)/n;
  r.se=Math.sqrt(r.blocks.reduce((s,b)=>s+(b[1]-r.mean)**2,0)/Math.max(1,n-1)/n);
  // Four correlated games form one independent block; draws count as half a point.
  r.lower=r.mean-2.576*r.se;r.passed=r.E===0&&n>=40&&r.mean>.5&&r.lower>.5;
  return r;
 }
 (async()=>{
  const rules=path.resolve(arg('rules','rules.js')),out=path.resolve(arg('out','training'));
  const generations=+arg('generations',30),pairs=+arg('pairs',200),strength=+arg('strength',4),shards=+arg('shards',Math.max(1,Math.min(8,os.cpus().length-1)));
  if(!Number.isInteger(pairs)||pairs<40||generations<1||strength<1||strength>4||shards<1)throw Error('Invalid training arguments');
  const m=JSON.parse(fs.readFileSync(path.join(__dirname,'manifest.json'),'utf8'));
  const defaults=JSON.parse(fs.readFileSync(path.join(__dirname,'tunes.json'),'utf8'));delete defaults['5'];validate(defaults);
  fs.mkdirSync(out,{recursive:true});const stateFile=path.join(out,'best.json');let state;
  if(process.argv.includes('--resume')){
   state=JSON.parse(fs.readFileSync(stateFile,'utf8'));
   if(state.schema!==2||state.fingerprint!==m.fingerprint||state.pairs!==pairs||state.strength!==strength)throw Error('Incompatible checkpoint');
  }else{
   if(fs.existsSync(stateFile))throw Error('Checkpoint exists: use Resume');
   state={schema:2,fingerprint:m.fingerprint,pairs,strength,generation:0,best:defaults,history:[],rng:2654435761};atomic(stateFile,state);
  }
  // Keep historical keys for compatible checkpoints, but do not waste a
  // generation mutating retired optional-round switches. The researched
  // T/L card economy is a fixed safeguard; learn scoring and ordering instead.
  validate(state.best);const keys=Object.keys(SPACE).filter(k=>![0,1,2,3,4,18,19,22,23].includes(+k)),last=state.generation+generations;
  const rng=()=>{let x=state.rng;x^=x<<13;x^=x>>>17;x^=x<<5;state.rng=x>>>0;return state.rng/4294967296;};
  if(pairs<m.presets.length)throw Error('A training set must include the full frozen deck pool');
  console.log(`Frozen ${m.fingerprint}; ${pairs*4} games/set; ${shards} workers; all ${m.presets.length} decks`);
  try{
   for(let g=state.generation;g<last;g++){
    const candidate={...state.best};let changed=[];
    while(!changed.length){const key=keys[Math.floor(rng()*keys.length)],[lo,hi,step]=SPACE[key];candidate[key]=Math.max(lo,Math.min(hi,candidate[key]+(rng()<.5?-1:1)*step*(1+Math.floor(rng()*3))));changed=keys.filter(k=>candidate[k]!==state.best[k]);}
    const started=Date.now(),result=await run(rules,shards,strength,5000+g*97,candidate,state.best,pairs);
    let confirmation=null,historical=null,accepted=false;
    if(result.passed){confirmation=await run(rules,shards,strength,90000+g*131,candidate,state.best,pairs);if(confirmation.passed){historical=await run(rules,shards,strength,190000+g*139,candidate,defaults,pairs);accepted=historical.E===0&&historical.mean>=.5;}}
    const entry={schema:2,fingerprint:m.fingerprint,generation:g,candidate,previous:state.best,changed,result,confirmation,historical,accepted,seconds:(Date.now()-started)/1000};
    atomic(path.join(out,`gen-${String(g).padStart(4,'0')}.json`),entry);
    if(accepted){state.best=candidate;state.acceptedProof=entry;}
    state.history.push({generation:g,score:result.mean,accepted});state.generation=g+1;atomic(stateFile,state);
    console.log(`gen ${g}: ${changed.map(k=>k+'='+candidate[k])} score ${(result.mean*100).toFixed(2)}%, lower ${(result.lower*100).toFixed(2)}%, errors ${result.E}, ${accepted?'ACCEPTED':'rejected'}, ${entry.seconds.toFixed(0)}s`);
   }
  }finally{close();}
  console.log('Checkpoint: '+stateFile);
 })().catch(e=>{close();console.error(e.stack);process.exitCode=1;});
}
