'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const out=path.resolve(process.argv[2]),resume=process.argv.includes('--resume');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const plan=JSON.parse(fs.readFileSync(path.join(out,'plan.json'),'utf8')),planSha256=sha(path.join(out,'plan.json'));
for(const [n,h]of Object.entries(plan.codeFiles))if(sha(path.join(out,'frozen',n))!==h)throw Error('Frozen source changed '+n);
if(sha(path.join(plan.current,'manifest.json'))!==plan.commonManifestSha256)throw Error('Common rules changed');
const progress=path.join(out,'progress.json'),lock=path.join(out,'exclusive.lock');
if(fs.existsSync(lock))throw Error('Existing trial process lock');if(fs.existsSync(progress)&&!resume)throw Error('Explicit resume required');
fs.writeFileSync(lock,JSON.stringify({pid:process.pid,planSha256}),{flag:'wx'});
const state={status:'running',completed:0,total:plan.schedule.length,errors:0,planSha256,pid:process.pid};
const save=()=>{state.lastActivity=new Date().toISOString();fs.writeFileSync(progress+'.tmp',JSON.stringify(state,null,2)+'\n');fs.renameSync(progress+'.tmp',progress);};
try{
 const {playMatch}=require(path.join(out,'frozen/tools/ai/beta_js092/matches.cjs'));
 let gap=false;for(const job of plan.schedule){const p=path.join(out,'games',job.id+'.json');if(!fs.existsSync(p)){gap=true;continue;}if(gap)throw Error('Saved results are not a prefix');const r=JSON.parse(fs.readFileSync(p,'utf8'));if(r.planSha256!==planSha256||r.status!=='complete'||r.id!==job.id)throw Error('Saved result invalid');state.completed++;}
 save();for(const job of plan.schedule.slice(state.completed)){
  state.current=job.id;save();const r=playMatch({current:plan.current},job.left,job.right,job.seed);
  fs.writeFileSync(path.join(out,'games',job.id+'.json'),JSON.stringify({...r,id:job.id,planSha256,deck:job.deck,candidate:job.candidate,baseline:job.baseline,mirror:job.mirror,block:job.block},null,2)+'\n',{flag:'wx'});
  if(r.status!=='complete'){state.errors++;state.status='failed';state.error=r.error;save();process.exitCode=1;break;}
  state.completed++;state.current=null;save();console.log(JSON.stringify({completed:state.completed,total:state.total,id:job.id,ms:r.ms}));
 }
 if(state.completed===state.total){state.status='complete';save();}
}catch(e){state.status='failed';state.error=String(e.stack);save();throw e;}
finally{fs.unlinkSync(lock);}
