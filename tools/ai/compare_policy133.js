// Paired holdout smoke benchmark. Reports changed outcomes, not proof of stronger AI.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),cp=require('child_process');
const baseline=path.resolve(process.argv[2]),current=path.resolve(process.argv[3]),output=path.resolve(process.argv[4]);
if(process.argv[5]==='worker'){
 const contexts={};
 function context(folder){
  if(contexts[folder])return contexts[folder];const ctx=vm.createContext({console,performance});
  vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(folder,f),'utf8')).join('\n')+String.raw`
 const audit={times:[],boundaries:0};
 function invariant(g){
  const ids=new Set();for(const c of g.live){const s=c.Snapshot();if(ids.has(s.instanceId))throw Error('duplicate instance');ids.add(s.instanceId);if(!Number.isFinite(s.power.currentPower)||s.power.currentPower<0||s.power.armor<0)throw Error('negative power/armor');}
  for(const side of [1,2])for(const row of [1,2,4]){
   const cards=g.live.map(c=>c.Snapshot()).filter(s=>s.positionPlayerId===side&&s.locationMask===row&&!s.isWaitingToDie);
   if(cards.length>9||new Set(cards.map(c=>c.locationIndex)).size!==cards.length)throw Error('row capacity/index');
  }
  for(const side of [1,2]){const score=g.live.map(c=>c.Snapshot()).filter(s=>s.positionPlayerId===side&&(s.locationMask&7)!==0&&(s.tokenMask&8)===0&&!s.isWaitingToDie).reduce((n,s)=>n+s.power.currentPower,0);if(score!==g.Score(side))throw Error('score mismatch');}
  audit.boundaries++;
 }
 const actual=CBetaGwentDuelSession.prototype.OpponentStep;
 CBetaGwentDuelSession.prototype.OpponentStep=function(){if(this.aiSimulating)return actual.apply(this,arguments);invariant(this);const t=performance.now();const v=actual.apply(this,arguments);audit.times.push(performance.now()-t);invariant(this);return v;};
 globalThis.run=function(job){audit.times=[];audit.boundaries=0;Host.simDamp=40;const result=__harness.play(job.left,job.right,job.seed,4,4,120);return {...result,boundaries:audit.boundaries,decisionMs:audit.times};};
 `,ctx);return contexts[folder]=ctx;
 }
 process.on('message',job=>{const ctx=context(job.brain==='baseline'?baseline:current);ctx.job=job;let result;try{result=vm.runInContext('run(job)',ctx,{timeout:120000});}catch(e){result={error:String(e.stack||e)};}process.send({job,result});});
}else{
 fs.mkdirSync(path.dirname(output),{recursive:true});
 const before=JSON.parse(fs.readFileSync(path.join(baseline,'manifest.json'))),after=JSON.parse(fs.readFileSync(path.join(current,'manifest.json')));
 const pool=after.presets;if(JSON.stringify(pool)!==JSON.stringify(before.presets))throw Error('different profile pool');
 for(const n of ['duelAICatalog.ws','duelAIResearch.ws','duelCatalog.ws']){const rel='sources/BetaGwent/development/scripts/game/betagwent/'+n;if(!fs.readFileSync(path.join(baseline,rel)).equals(fs.readFileSync(path.join(current,rel))))throw Error('rosters/card data differ: '+n);}
 const jobs=[];for(let i=0;i<pool.length;i++)for(const seat of [0,1])for(const brain of ['baseline','current'])jobs.push({brain,index:i,seat,left:pool[(i+seat*17)%pool.length],right:pool[(i+(1-seat)*17)%pool.length],seed:(2026101233+i*104729)>>>0});
 const report={baseline:before.fingerprint,current:after.fingerprint,seedBase:2026101233,simDamp:40,nativeGameTested:false,protocol:'Identical current rosters, paired holdout seeds and reversed seats; both seats use the selected policy. This checks stability and changed outcomes, not head-to-head strength against a fixed opponent.',planned:jobs.length,games:[]};
 let next=0,done=0;const workers=[];
 function save(){const summaries={};for(const brain of ['baseline','current']){const games=report.games.filter(x=>x.job.brain===brain),times=games.flatMap(x=>x.result.decisionMs||[]).sort((a,b)=>a-b);summaries[brain]={games:games.length,errors:games.filter(x=>x.result.error).length,decisions:times.length,boundaries:games.reduce((n,x)=>n+(x.result.boundaries||0),0),medianMs:times[Math.floor(times.length*.5)]||0,p95Ms:times[Math.floor(times.length*.95)]||0,maxMs:times.at(-1)||0};}report.summaries=summaries;fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');}
 function assign(w){if(next<jobs.length)w.send(jobs[next++]);else w.disconnect();}
 for(let i=0;i<2;i++){const w=cp.fork(__filename,[baseline,current,output,'worker'],{stdio:['ignore','inherit','inherit','ipc']});workers.push(w);w.on('message',record=>{report.games.push(record);done++;if(done%8===0||record.result.error){save();console.log('GAMES',done,'/',jobs.length,'ERRORS',report.games.filter(x=>x.result.error).length);}assign(w);if(done===jobs.length){save();if(report.games.some(x=>x.result.error))process.exitCode=1;}});w.on('exit',code=>{if(code){process.exitCode=1;console.error('Worker failed',code);}});assign(w);}
 process.on('SIGINT',()=>{save();workers.forEach(w=>w.kill());process.exit(130);});save();
}
