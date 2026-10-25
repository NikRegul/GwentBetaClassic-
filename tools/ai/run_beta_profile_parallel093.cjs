/* Parallel orchestration only: immutable jobs and frozen match code stay intact.
 * Workers spool results; only the parent commits a contiguous schedule prefix. */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {Worker,isMainThread,parentPort,workerData}=require('worker_threads');
const {renameWithRetry}=require('./profile_trial_io093.cjs');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(!isMainThread){
 const {playMatch}=require(path.join(workerData.out,'frozen/tools/ai/beta_js092/matches.cjs'));
 parentPort.on('message',({index,job,current})=>{
  try{parentPort.postMessage({index,result:playMatch({current},job.left,job.right,job.seed)});}
  catch(e){parentPort.postMessage({index,error:String(e.stack)});}
 });
}else{
 main().catch(e=>{console.error(e.stack);process.exitCode=1;});
}
async function main(){
 const out=path.resolve(process.argv[2]),args=process.argv.slice(3);
 const option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
 const count=Number(option('--workers',6)),verify=Number(option('--verify-existing',0));
 if(!Number.isInteger(count)||count<1||count>12)throw Error('Workers must be1..12');
 const planPath=path.join(out,'plan.json'),plan=JSON.parse(fs.readFileSync(planPath,'utf8')),planSha256=sha(planPath);
 for(const [n,h]of Object.entries(plan.codeFiles))if(sha(path.join(out,'frozen',n))!==h)throw Error('Frozen source changed '+n);
 if(sha(path.join(plan.current,'manifest.json'))!==plan.commonManifestSha256)throw Error('Common rules changed');
 const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
 function validate(r,job){
  if(r.planSha256!==planSha256||r.status!=='complete'||r.id!==job.id||r.seed!==job.seed||r.left!==job.left.key||r.right!==job.right.key||![1,2,3].includes(r.winner))throw Error('Invalid result '+job.id);
 }
 let prefix=0,gap=false;const saved=[];
 for(const job of plan.schedule){
  const file=path.join(out,'games',job.id+'.json');
  if(!fs.existsSync(file)){gap=true;continue;}
  if(gap)throw Error('Saved results are not a prefix');
  const r=read(file);validate(r,job);saved.push(r);prefix++;
 }
 const proof={planSha256,runnerSha256:sha(__filename),workers:count,frozenInputsVerified:true,originalCompleted:prefix,started:new Date().toISOString()};
 const workers=[],inFlight=new Map();let failPool=null;
 async function shutdown(){await Promise.allSettled(workers.map(w=>w.terminate()));}
 function pool(indices,onResult){
  return new Promise((resolve,reject)=>{
   let next=0,done=0,failed=false;
   const fail=e=>{if(!failed){failed=true;reject(e);}};failPool=fail;
   const send=w=>{
    if(failed)return;
    if(next>=indices.length){if(done===indices.length)resolve();return;}
    const index=indices[next++];inFlight.set(w,index);
    w.postMessage({index,job:plan.schedule[index],current:plan.current});
   };
   if(!indices.length){resolve();return;}
   for(let i=0;i<Math.min(count,indices.length);i++){
    const w=new Worker(__filename,{workerData:{out}});workers.push(w);
    w.on('error',fail);w.on('exit',code=>{if(code!==0&&!failed&&done<indices.length)fail(Error('Worker exited '+code));});
    w.on('message',message=>{
     if(failed)return;
     try{
      if(message.index!==inFlight.get(w))throw Error('Worker returned wrong job');
      inFlight.delete(w);
      if(message.error)throw Error(message.error);
      onResult(message.index,message.result);done++;send(w);
     }catch(e){fail(e);}
    });send(w);
   }
  });
 }
 if(verify){
  if(verify>prefix)throw Error('Not enough saved games for preflight');
  // Sample both candidate and incumbent, preserving adjacent paired jobs.
  const indices=Array.from({length:verify},(_,i)=>Math.min(prefix-1,2*Math.floor(Math.floor(i/2)*(prefix-2)/(2*Math.max(1,Math.ceil(verify/2)-1)))+i%2)),checks=[];
  let failure=null;
  try{
   await pool(indices,(index,r)=>{
    const old=saved[index],same=r.status==='complete'&&r.finalStateSha256===old.finalStateSha256&&r.winner===old.winner&&JSON.stringify(r.trace)===JSON.stringify(old.trace);
    checks.push({id:old.id,same,serialMs:old.ms,parallelMs:r.ms,serialForced:old.betaForcedSearches,parallelForced:r.betaForcedSearches,serialWinner:old.winner,parallelWinner:r.winner});
    if(!same)fs.writeFileSync(path.join(out,'parallel-preflight-difference-workers'+count+'.json'),JSON.stringify({serial:old,parallel:r},null,2)+'\n');
    if(!same)throw Error('Parallel preflight differs: '+old.id);
   });
  }catch(e){failure=e;}
  finally{
   await shutdown();
   fs.writeFileSync(path.join(out,'parallel-preflight.json'),JSON.stringify({...proof,checks,passed:!failure,error:failure?String(failure.stack):null,finished:new Date().toISOString()},null,2)+'\n');
  }
  if(failure)throw failure;
  console.log(JSON.stringify({preflight:true,workers:count,checks:checks.length,passed:true}));
  return;
 }
 const progress=path.join(out,'progress.json'),lock=path.join(out,'exclusive.lock'),spool=path.join(out,'parallel-spool');
 if(fs.existsSync(lock))throw Error('Existing trial process lock');
 if(fs.existsSync(progress)&&!args.includes('--resume'))throw Error('Explicit resume required');
 fs.writeFileSync(lock,JSON.stringify({pid:process.pid,planSha256,workers:count}),{flag:'wx'});
 const state={status:'running',completed:prefix,total:plan.schedule.length,errors:0,planSha256,pid:process.pid,workers:count,computed:prefix};
 const save=()=>{
  state.lastActivity=new Date().toISOString();state.current=[...inFlight.values()].map(i=>plan.schedule[i].id);
  fs.writeFileSync(progress+'.tmp',JSON.stringify(state,null,2)+'\n');renameWithRetry(progress+'.tmp',progress);
 };
 fs.mkdirSync(spool,{recursive:true});
 const pending=new Map();
 function commit(){
  while(pending.has(state.completed)){
   const i=state.completed,job=plan.schedule[i],source=pending.get(i),dest=path.join(out,'games',job.id+'.json');
   if(fs.existsSync(dest))throw Error('Canonical result already exists '+job.id);
   renameWithRetry(source,dest);pending.delete(i);state.completed++;
   console.log(JSON.stringify({completed:state.completed,total:state.total,id:job.id,workers:count}));
  }
 }
 let heartbeat;
 try{
  const executionPath=path.join(out,'parallel-execution.json');
  const previous=fs.existsSync(executionPath)?read(executionPath):null;
  const previousExecutions=previous?[...(previous.previousExecutions||[]),Object.fromEntries(Object.entries(previous).filter(([k])=>k!=='previousExecutions'))]:[];
  fs.writeFileSync(executionPath,JSON.stringify({...proof,pid:process.pid,ioHelperSha256:sha(path.join(__dirname,'profile_trial_io093.cjs')),previousExecutions},null,2)+'\n');
  const indices=[];
  for(let i=prefix;i<plan.schedule.length;i++){
   const file=path.join(spool,plan.schedule[i].id+'.json');
   if(fs.existsSync(file)){validate(read(file),plan.schedule[i]);pending.set(i,file);state.computed++;}
   else indices.push(i);
  }
  commit();save();heartbeat=setInterval(()=>{try{save();}catch(e){if(failPool)failPool(e);}},10000);
  await pool(indices,(index,r)=>{
   const job=plan.schedule[index],record={...r,id:job.id,planSha256,deck:job.deck,candidate:job.candidate,baseline:job.baseline,mirror:job.mirror,block:job.block};
   if(r.status!=='complete'){
    fs.writeFileSync(path.join(spool,job.id+'.error.json'),JSON.stringify(record,null,2)+'\n');
    state.errors++;throw Error('Technical match error '+job.id+': '+r.error);
   }
   validate(record,job);
   const file=path.join(spool,job.id+'.json');
   fs.writeFileSync(file+'.tmp',JSON.stringify(record,null,2)+'\n',{flag:'wx'});renameWithRetry(file+'.tmp',file);
   pending.set(index,file);state.computed++;commit();save();
  });
  if(state.completed!==state.total)throw Error('Incomplete committed prefix');
  state.status='complete';save();
 }catch(e){state.status='failed';state.error=String(e.stack);try{save();}catch(ioError){console.error(ioError.stack);}throw e;}
 finally{clearInterval(heartbeat);await shutdown();fs.unlinkSync(lock);}
}
