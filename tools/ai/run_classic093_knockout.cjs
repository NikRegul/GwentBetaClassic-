'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {Worker,isMainThread,parentPort,workerData}=require('worker_threads');
const {renameWithRetry}=require('./profile_trial_io093.cjs');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const mix=n=>{n=Math.imul(n^(n>>>16),0x7feb352d);n=Math.imul(n^(n>>>15),0x846ca68b);return (n^(n>>>16))>>>0;};
const seedFor=(p,g,r,s,pair)=>mix(p.masterSeed+(((g*8+r)*128+s)*8+pair));
function atomic(file,value){fs.writeFileSync(file+'.tmp',JSON.stringify(value,null,2)+'\n');renameWithRetry(file+'.tmp',file);}
function validateInputs(out,p){
 for(const [n,h]of Object.entries(p.codeFiles))if(sha(path.join(out,'frozen',n))!==h)throw Error('Frozen code changed '+n);
 if(sha(path.join(out,'entrants.json'))!==p.rosterSha256||sha(path.join(out,'profile-mapping.json'))!==p.mappingSha256||sha(path.join(p.current,'manifest.json'))!==p.commonManifestSha256)throw Error('Frozen inputs changed');
}
if(!isMainThread){
 const {out,plan,planSha256}=workerData;
 const {playMatch}=require(path.join(out,'frozen/tools/ai/beta_js092/matches.cjs'));
 const entrants=new Map(read(path.join(out,'entrants.json')).map(e=>[e.key,e]));
 parentPort.on('message',job=>{
  try{
   if(job.kind==='benchmark'){parentPort.postMessage({type:'result',id:job.id,result:playMatch({current:plan.current},entrants.get(job.left),entrants.get(job.right),job.seed)});return;}
   const records=[],left=entrants.get(job.left),right=entrants.get(job.right);let leftPoints=0,rightPoints=0;
   for(let pair=0;pair<plan.format.basePairs+plan.format.maxExtraPairs;pair++){
    for(let mirror=0;mirror<2;mirror++){
     const id=job.id+'-p'+pair+'-m'+mirror,file=path.join(out,'games',id+'.json'),seed=seedFor(plan,job.grid,job.round,job.slot,pair);
     const [a,b]=mirror?[right,left]:[left,right];let r,existing=fs.existsSync(file);
     if(existing)r=read(file);
     else{
      r={...playMatch({current:plan.current},a,b,seed),id,series:job.id,planSha256,grid:job.grid,round:job.round,slot:job.slot,pair,mirror};
      if(r.status!=='complete'){atomic(path.join(out,'errors',id+'.json'),r);throw Error('Technical game error '+id+': '+r.error);}
      atomic(file,r);
     }
     if(r.status!=='complete'||r.id!==id||r.planSha256!==planSha256||r.seed!==seed||r.left!==a.key||r.right!==b.key||![1,2,3].includes(r.winner))throw Error('Invalid saved game '+id);
     const score=r.winner===3?.5:Number(r.winner===(mirror?2:1));leftPoints+=score;rightPoints+=1-score;
     records.push({id,sha256:sha(file)});parentPort.postMessage({type:'game',id:job.id,game:id,existing});
    }
    if(pair+1>=plan.format.basePairs&&leftPoints!==rightPoints)break;
   }
   let resolution='game-points',winner=leftPoints>rightPoints?left.key:right.key;
   if(leftPoints===rightPoints){resolution='seeded-draw';const coin=crypto.createHash('sha256').update(plan.masterSeed+':tie:'+job.id).digest()[0]&1;winner=coin?left.key:right.key;}
   parentPort.postMessage({type:'result',id:job.id,result:{...job,planSha256,winner,leftPoints,rightPoints,resolution,games:records}});
  }catch(e){parentPort.postMessage({type:'error',id:job.id,error:String(e.stack)});}
 });
}else main().catch(e=>{console.error(e.stack);process.exitCode=1;});

async function main(){
 const out=path.resolve(process.argv[2]),benchmark=process.argv.includes('--benchmark'),resume=process.argv.includes('--resume');
 const planPath=path.join(out,benchmark?'preflight-config.json':'plan.json'),p=read(planPath),planSha256=sha(planPath);validateInputs(out,p);
 const entrants=read(path.join(out,'entrants.json')),byKey=new Map(entrants.map(e=>[e.key,e])),workers=[],active=new Map();let failure=null,currentPool=null;
 const pending=[];
 const state={status:benchmark?'benchmark-running':'running',pid:process.pid,planSha256,workers:p.workers,completedGames:0,completedSeries:0,completedBrackets:0,errors:0,minimumGames:p.minimumGames,maximumGames:p.maximumGames};
 const progress=path.join(out,benchmark?'benchmark-progress.json':'progress.json');
 function save(){state.lastActivity=new Date().toISOString();state.activeSeries=[...active.values()].map(t=>t.job.id);atomic(progress,state);}
 function fail(e){if(failure)return;failure=e;if(currentPool)currentPool.reject(e);}
 function dispatch(){
  if(failure)return;
  for(const w of workers)if(!active.has(w)&&pending.length){const task=pending.shift();active.set(w,task);w.postMessage(task.job);}
 }
 function pool(jobs){
  if(failure)return Promise.reject(failure);
  return new Promise((resolve,reject)=>{
   if(!jobs.length){resolve([]);return;}
   currentPool={resolve,reject,remaining:jobs.length,results:[]};
   for(const job of jobs)pending.push({job});dispatch();
  });
 }
 for(let i=0;i<p.workers;i++){
  const w=new Worker(__filename,{workerData:{out,plan:p,planSha256}});workers.push(w);
  w.on('error',fail);w.on('exit',code=>{if(code!==0&&!failure&&currentPool)fail(Error('Worker exited '+code));});
  w.on('message',message=>{
   if(failure)return;
   try{
    const task=active.get(w);if(!task||message.id!==task.job.id)throw Error('Wrong worker response');
    if(message.type==='error')throw Error(message.error);
    if(message.type==='game'){if(!message.existing)state.completedGames++;state.lastGameActivity=new Date().toISOString();save();return;}
    if(message.type!=='result')throw Error('Unknown worker response');
    if(benchmark&&message.result.status!=='complete')throw Error('Benchmark game failed: '+message.result.error);
    if(!benchmark){
     const file=path.join(out,'series',message.id+'.json');
     if(fs.existsSync(file)){if(JSON.stringify(read(file))!==JSON.stringify(message.result))throw Error('Recorded series changed '+message.id);}
     else atomic(file,message.result);
     state.completedSeries++;
    }
    currentPool.results.push({id:message.id,job:task.job,result:message.result});active.delete(w);
    if(--currentPool.remaining===0){const done=currentPool;currentPool=null;done.resolve(done.results);}
    dispatch();save();
   }catch(e){fail(e);}
  });
 }
 const lock=path.join(out,benchmark?'benchmark.lock':'exclusive.lock');let heartbeat,ownsLock=false;
 try{
  if(fs.existsSync(lock))throw Error('Existing process lock');
  if(!benchmark&&fs.existsSync(progress)&&!resume)throw Error('Explicit resume required');
  fs.writeFileSync(lock,JSON.stringify({pid:process.pid,planSha256}),{flag:'wx'});
  ownsLock=true;
  if(benchmark){
   if(fs.existsSync(path.join(out,'benchmark.json')))throw Error('Benchmark already exists');
   const hard=entrants.filter(e=>e.group==='hard'),classic=entrants.filter(e=>e.group==='classic'),jobs=[];
   for(let i=0;i<8;i++){
    const a=i<2?hard:classic,b=i>=2&&i<5?classic:hard;
    jobs.push({kind:'benchmark',id:'benchmark-'+i,left:a[(i*13)%92].key,right:b[(i*17+11)%92].key,seed:mix(p.masterSeed+i+800000)});
   }
   const started=Date.now();save();const records=await pool(jobs);
   atomic(path.join(out,'benchmark.json'),{complete:true,records,elapsedMs:Date.now()-started,workers:p.workers,sourceConfigSha256:planSha256});state.status='benchmark-complete';save();return;
  }
  for(const directory of ['games','series','errors'])fs.mkdirSync(path.join(out,directory),{recursive:true});
  for(const file of fs.readdirSync(path.join(out,'games')).filter(n=>n.endsWith('.json'))){const r=read(path.join(out,'games',file));if(r.planSha256!==planSha256||r.status!=='complete')throw Error('Saved game invalid '+file);state.completedGames++;}
  save();heartbeat=setInterval(()=>{try{save();}catch(e){fail(e);}},10000);
  const brackets=[];
  for(let grid=0;grid<p.grids;grid++){
   let slots=p.brackets[grid];const rounds=[];
   for(let round=0;slots.length>1;round++){
    const winners=[],jobs=[],rows=[];
    for(let slot=0;slot<slots.length/2;slot++){
     const [left,right]=slots.slice(slot*2,slot*2+2);
     if(!left&&!right)throw Error('Empty pairing');
     if(!left||!right){winners[slot]=left||right;rows[slot]={left,right,winner:left||right,resolution:'bye'};continue;}
     jobs.push({kind:'series',id:`g${String(grid).padStart(2,'0')}-r${round}-s${String(slot).padStart(3,'0')}`,grid,round,slot,left,right});
    }
    const results=await pool(jobs);
    for(const {result}of results){winners[result.slot]=result.winner;rows[result.slot]=result;}
    rounds.push(rows);slots=winners;atomic(path.join(out,'brackets.json'),{planSha256,completed:brackets,current:{grid,rounds}});
   }
   brackets.push({grid,winner:slots[0],rounds});state.completedBrackets=brackets.length;save();
   console.log(JSON.stringify({grid,winner:slots[0],completedGames:state.completedGames}));
  }
  atomic(path.join(out,'brackets.json'),{planSha256,complete:true,completed:brackets});
  const policy={hard:{points:0,games:0},classic:{points:0,games:0}},champions={},lotteries=[];
  for(const b of brackets){champions[b.winner]=(champions[b.winner]||0)+1;for(const round of b.rounds)for(const series of round)if(series.resolution==='seeded-draw')lotteries.push(series.id);}
  for(const name of fs.readdirSync(path.join(out,'games')).filter(n=>n.endsWith('.json'))){
   const r=read(path.join(out,'games',name)),a=byKey.get(r.left),b=byKey.get(r.right);if(a.group===b.group)continue;
   const score=r.winner===3?.5:Number(r.winner===1);policy[a.group].points+=score;policy[b.group].points+=1-score;policy[a.group].games++;policy[b.group].games++;
  }
  const report={complete:true,planSha256,grids:p.grids,entrants:entrants.length,games:state.completedGames,series:state.completedSeries,errors:0,champions:Object.entries(champions).map(([key,wins])=>({key,wins,title:byKey.get(key).title,group:byKey.get(key).group})).sort((a,b)=>b.wins-a.wins),crossPolicy:policy,seededDrawSeries:lotteries,
   limits:'Knockout results depend on bracket/opponents. Seeded-draw qualifications are separate from game wins. Classic has hidden-information access; Hard keeps its restrictions. No claim of globally strongest AI.'};
  atomic(path.join(out,'report.json'),report);state.status='complete';save();
 }catch(e){if(ownsLock){state.status='failed';state.error=String(e.stack);state.errors++;try{save();}catch{}}throw e;}
 finally{clearInterval(heartbeat);failure=failure||Error('Shutdown');await Promise.allSettled(workers.map(w=>w.terminate()));if(fs.existsSync(lock)){const owner=read(lock);if(owner.pid===process.pid)fs.unlinkSync(lock);}}
}
