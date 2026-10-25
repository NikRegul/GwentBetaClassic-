/* Fixed immutable plan, exclusive lock, one durable block per game. Resume is
 * permitted only with identical inputs and a verified complete prefix. */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const out=path.resolve(process.argv[2]),resume=process.argv.includes('--resume'),planPath=path.join(out,'plan.json');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const plan=JSON.parse(fs.readFileSync(planPath,'utf8')),planSha256=sha(planPath);
for(const [name,digest]of Object.entries(plan.codeFiles))if(sha(path.join(out,'frozen',name))!==digest)throw Error('Frozen code changed: '+name);
if(sha(path.join(plan.config.current,'manifest.json'))!==plan.commonManifestSha256||sha(path.join(plan.config.policy091,'comparison.json'))!==plan.policyProofSha256||sha(plan.config.originalRosters)!==plan.originalRostersSha256)throw Error('Experiment input changed');
const progressPath=path.join(out,'progress.json'),lockPath=path.join(out,'exclusive.lock');
if(fs.existsSync(progressPath)&&!resume)throw Error('Existing run requires explicit verified --resume');
if(fs.existsSync(lockPath)){
 const prior=JSON.parse(fs.readFileSync(lockPath,'utf8'));let alive=true;try{process.kill(prior.pid,0);}catch(e){if(e.code==='ESRCH')alive=false;else throw e;}
 if(alive||!resume)throw Error('Exclusive run lock already exists');
 fs.renameSync(lockPath,path.join(out,'expired-lock-'+Date.now()+'.json'));
}
const lock=fs.openSync(lockPath,'wx');fs.writeFileSync(lock,JSON.stringify({pid:process.pid,planSha256,startedAt:new Date().toISOString(),command:process.argv}));fs.closeSync(lock);
let summary={planSha256,pid:process.pid,nodeVersion:process.version,kind:plan.kind,ratingPermitted:plan.ratingPermitted,total:plan.schedule.length,completed:0,technicalErrors:0,status:'running',lastActivity:new Date().toISOString()};
const save=()=>{summary.lastActivity=new Date().toISOString();fs.writeFileSync(progressPath+'.tmp',JSON.stringify(summary,null,2)+'\n');fs.renameSync(progressPath+'.tmp',progressPath);};
try{
 const {entrants,playMatch}=require(path.join(out,'frozen/tools/ai/beta_js092/matches.cjs')),list=entrants(plan.config),byKey=new Map(list.map(d=>[d.key,d]));
 if(new Set(plan.schedule.map(x=>x.id)).size!==plan.schedule.length)throw Error('Duplicate schedule ID');
 const allowed=new Set(plan.schedule.map(x=>x.id+'.json'));
 for(const file of fs.readdirSync(path.join(out,'games')))if(!allowed.has(file))throw Error('Unexpected saved block '+file);
 let gap=false;
 for(const entry of plan.schedule){
  const file=path.join(out,'games',entry.id+'.json');
  if(fs.existsSync(file)){
   if(gap)throw Error('Saved games must be a consecutive prefix');const saved=JSON.parse(fs.readFileSync(file,'utf8'));
   if(saved.planSha256!==planSha256||saved.id!==entry.id||saved.left!==entry.left||saved.right!==entry.right||saved.seed!==entry.seed||saved.status!=='complete')throw Error('Saved block is incompatible or failed: '+entry.id);
   summary.completed++;
  }else gap=true;
 }
 save();
 for(let index=summary.completed;index<plan.schedule.length;index++){
  const entry=plan.schedule[index],left=byKey.get(entry.left),right=byKey.get(entry.right);if(!left||!right)throw Error('Unknown entrant');
  summary.current=entry.id;save();const result=playMatch(plan.config,left,right,entry.seed);
  fs.writeFileSync(path.join(out,'games',entry.id+'.json'),JSON.stringify({...result,id:entry.id,planSha256},null,2)+'\n',{flag:'wx'});
  if(result.status!=='complete'){summary.technicalErrors++;summary.status='technical-error';summary.error=result.error;save();process.exitCode=1;break;}
  summary.completed++;summary.current=null;save();console.log(JSON.stringify({completed:summary.completed,total:summary.total,id:entry.id,ms:result.ms,betaPeakCallbackMs:result.betaPeakCallbackMs}));
 }
 if(summary.completed===summary.total){summary.status='complete';save();}
}catch(e){summary.status='failed';summary.error=String(e.stack);save();throw e;}
finally{fs.unlinkSync(lockPath);}
