// Review the last non-forced losing decision in each completed match.
'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib'),cp=require('child_process'),crypto=require('crypto');
const run=path.resolve(process.argv[2]),report=JSON.parse(fs.readFileSync(path.join(run,'report.json'),'utf8'));
if(!report.complete||report.errors)throw Error('A complete error-free diagnostic run is required');
const out=path.join(run,'counterfactuals');fs.mkdirSync(out,{recursive:true});
const replay=path.join(__dirname,'replay_deck_audit091.js'),hash=crypto.createHash('sha256').update(fs.readFileSync(replay)).digest('hex');
const jobs=[];
for(const game of report.games){if(game.winner===3)continue;const trace=JSON.parse(zlib.gunzipSync(fs.readFileSync(game.trace)));
 const decisions=trace.decisions.filter(d=>game.winner!==(d.before.actor+1)&&d.before.crowns[0]>0&&d.before.hand.filter(c=>c.canPlay).length>=2&&d.selection);
 const d=decisions.at(-1);if(d)jobs.push({id:game.id,trace:game.trace,step:d.step,preset:d.before.preset,actor:d.before.actor,selection:d.selection});
}
const records=[],queue=jobs.slice();let alive=0;
function record(job){const file=path.join(out,job.id+'-step'+job.step+'.json');const r=JSON.parse(fs.readFileSync(file,'utf8'));
 const score=x=>x.winner===job.actor+1?1:x.winner===3?.5:0,baseline=r.results[0];
 return {...job,file,originalReproduced:r.originalReproduced,error:baseline.error,alternatives:r.results.slice(1).filter(x=>!x.error&&score(x)>score(baseline)).map(x=>({card:x.card,winner:x.winner,score:score(x),afterScore:x.after.view.score,steps:x.steps})),tested:r.results.length-1,failedAlternatives:r.results.filter(x=>x.error).map(x=>({card:x.card,error:x.error}))};
}
function save(){const summary={replaySha256:hash,sourceFingerprint:report.identity.fingerprint,planned:jobs.length,completed:records.length,complete:records.length===jobs.length,originalsReproduced:records.filter(x=>x.originalReproduced).length,errors:records.filter(x=>x.error||!x.originalReproduced).length,testedAlternatives:records.reduce((n,x)=>n+(x.tested||0),0),improvedCases:records.filter(x=>x.alternatives?.length),records};fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(summary,null,2));return summary;}
save();
function next(){const job=queue.shift();if(!job)return;alive++;const file=path.join(out,job.id+'-step'+job.step+'.json');
 const child=cp.spawn(process.execPath,[replay,job.trace,String(job.step),file],{stdio:['ignore','ignore','pipe']});let error='';child.stderr.on('data',x=>error+=x);
 child.on('exit',code=>{alive--;try{if(code!==0)throw Error(error||'Replay exited '+code);records.push(record(job));}catch(e){records.push({...job,error:String(e),originalReproduced:false,tested:0});}
  const r=save();console.log(JSON.stringify({completed:r.completed,total:r.planned,reproduced:r.originalsReproduced,improved:r.improvedCases.length,errors:r.errors}));next();
  if(!alive&&!queue.length&&r.errors)process.exitCode=1;
 });
}
for(let i=0;i<4;i++)next();
