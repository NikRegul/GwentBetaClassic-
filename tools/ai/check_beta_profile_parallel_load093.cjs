/* Check timer-sensitive games against a single serial execution. No schedule edits. */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const out=path.resolve(process.argv[2]),dest=path.resolve(process.argv[3]);
if(fs.existsSync(dest))throw Error('Use a fresh audit path');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const plan=JSON.parse(fs.readFileSync(path.join(out,'plan.json'),'utf8'));
for(const [n,h]of Object.entries(plan.codeFiles))if(sha(path.join(out,'frozen',n))!==h)throw Error('Frozen source changed '+n);
const {playMatch}=require(path.join(out,'frozen/tools/ai/beta_js092/matches.cjs'));
const ids=process.argv.slice(4),checks=[];
const decisions=trace=>trace.map(({finishReason,completedDepth,...rest})=>rest);
for(const id of ids){
 const job=plan.schedule.find(j=>j.id===id);if(!job)throw Error('Unknown job '+id);
 const parallel=JSON.parse(fs.readFileSync(path.join(out,'games',id+'.json'),'utf8'));
 const serial=playMatch({current:plan.current},job.left,job.right,job.seed);
 const sameState=parallel.finalStateSha256===serial.finalStateSha256;
 const sameDecisions=JSON.stringify(decisions(parallel.trace))===JSON.stringify(decisions(serial.trace));
 checks.push({id,sameState,sameDecisions,sameWinner:parallel.winner===serial.winner,parallel,serial});
 fs.writeFileSync(dest,JSON.stringify({planSha256:sha(path.join(out,'plan.json')),kind:'serial-replay-of-timer-sensitive-parallel-games',checks,finished:false},null,2)+'\n');
 console.log(JSON.stringify({id,sameState,sameDecisions,parallelForced:parallel.betaForcedSearches,serialForced:serial.betaForcedSearches}));
}
fs.writeFileSync(dest,JSON.stringify({planSha256:sha(path.join(out,'plan.json')),kind:'serial-replay-of-timer-sensitive-parallel-games',checks,finished:true,allActualDecisionsMatch:checks.every(c=>c.sameState&&c.sameDecisions&&c.sameWinner&&c.serial.status==='complete')},null,2)+'\n');
