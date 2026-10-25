// All researched decks, fixed independent deal blocks and mirrored seats.
// This runner changes no policy or battle rule. Append-only records allow resume.
'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process'),crypto=require('crypto'),vm=require('vm');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
function replaceProgress(tmp,dst){
 for(let attempt=0;;attempt++)try{fs.renameSync(tmp,dst);return;}
 catch(e){if(!['EPERM','EBUSY','EACCES'].includes(e.code)||attempt>=29)throw e;Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,25*(attempt+1));}
}
function load(snapshot,mode='function',diagnostic=false,extras=[]) {
 let code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n');
 if(diagnostic){const marker='return { left, right, seed, winner: w, steps, crowns: sc };';if(!code.includes(marker))throw Error('Parity marker missing');code=code.replace(marker,'return { left, right, seed, winner: w, steps, crowns: sc, trace };');}
 code+='\n'+require('./variant_decks092.js').adapter(extras);
 if(mode==='vm'){const ctx=vm.createContext({console});vm.runInContext(code,ctx);return ctx.__harness;}
 // Function scope avoids the VM global proxy. Native WS policy, RNG and
 // seat swapping are identical; parity is checked separately before use.
 return new Function(code+'\nreturn __harness;')();
}
if(process.argv[2]==='--worker') {
 const config=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),h=load(config.snapshot,'function',false,config.extraDecks||[]);
 h.Host.simDamp=config.simDamp;
 process.on('message',task=>{
  const start=Date.now(),games=[];
  for(const reverse of [false,true]){
   const left=reverse?task.b:task.a,right=reverse?task.a:task.b;
   const r=h.play(left,right,task.seed,task.strength,task.strength,100);
   games.push({...r,reverse});
  }
  process.send({...task,games,milliseconds:Date.now()-start});
 });process.send({ready:true});
} else if(process.argv[2]==='--parity') {
 const snapshot=path.resolve(process.argv[3]),out=process.argv[4],manifest=JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8'));
 const a=load(snapshot,'function',true),b=load(snapshot,'vm',true),rows=[];
 for(const strength of [2,3,4])for(let i=0;i<6;i++){
  const args=[manifest.presets[i*7%46],manifest.presets[(i*7+19)%46],(952381+7919*i+strength*100003)>>>0,strength,strength,100000];
  const x=a.play(...args),y=b.play(...args);
  if(JSON.stringify(x)!==JSON.stringify(y)||!x.winner)throw Error('Runner parity failure '+JSON.stringify({args,x,y}));
  rows.push({args,winner:x.winner,steps:x.steps,traceLines:x.trace.length,traceSha256:crypto.createHash('sha256').update(JSON.stringify(x.trace)).digest('hex')});
 }
 const report={fingerprint:manifest.fingerprint,checks:rows.length,identicalCompleteResults:true,identicalFullDecisionLogs:true,rows};
 if(out)fs.writeFileSync(out,JSON.stringify(report,null,2));console.log(JSON.stringify(report));
} else {
 const configPath=path.resolve(process.argv[2]),config=JSON.parse(fs.readFileSync(configPath,'utf8'));
 const manifest=JSON.parse(fs.readFileSync(path.join(config.snapshot,'manifest.json'),'utf8'));
 const fullPool=manifest.presets.concat((config.extraDecks||[]).map(d=>d.presetId));
 const pool=config.benchmark===true?config.benchmarkPool:fullPool;
 if(!Array.isArray(pool)||pool.some(id=>!fullPool.includes(id)))throw Error('Invalid benchmark pool');
 if(manifest.presets.length!==46||new Set(pool).size!==pool.length||!Number.isInteger(config.seed)||!Number.isInteger(config.workers)||config.workers<1||config.workers>18)throw Error('Invalid tournament configuration');
 if(!Number.isInteger(config.simDamp)||config.simDamp<0||config.simDamp>100)throw Error('Invalid simulation budget');
 for(const [n,hash]of Object.entries(manifest.snapshotFiles))if(sha(path.join(config.snapshot,n))!==hash)throw Error('Changed snapshot: '+n);
 for(const [s,n]of Object.entries(config.blocksByStrength))if(![2,3,4].includes(Number(s))||!Number.isInteger(n)||n<1||n>256)throw Error('Invalid sample');
 fs.mkdirSync(config.out,{recursive:true});
 const identity={fingerprint:manifest.fingerprint,configSha256:sha(configPath),toolSha256:sha(__filename),adapterSha256:sha(path.join(__dirname,'variant_decks092.js')),protocol:'fixed all-pairs; unique seeded deal blocks; both seats; no optional stopping; same native WS decision methods'};
 const identityPath=path.join(config.out,'identity.json');
 if(fs.existsSync(identityPath)&&JSON.stringify(JSON.parse(fs.readFileSync(identityPath)))!==JSON.stringify(identity))throw Error('Changed experiment');
 fs.writeFileSync(identityPath,JSON.stringify(identity,null,2));
 let state=config.seed>>>0||1;function random(){state^=state<<13;state>>>=0;state^=state>>>17;state>>>=0;state^=state<<5;return state>>>=0;}
 const tasks=[],seeds=new Set();let pair=0;
 for(let i=0;i<pool.length;i++)for(let j=i+1;j<pool.length;j++){
  for(let block=0;block<Math.max(...Object.values(config.blocksByStrength));block++){
   let seed;do{seed=random();}while(!seed||seeds.has(seed));seeds.add(seed);
   for(const [strength,count]of Object.entries(config.blocksByStrength))if(block<count)tasks.push({id:`s${strength}-p${pair}-b${block}`,strength:Number(strength),a:pool[i],b:pool[j],pair,block,seed});
  }pair++;
 }
 // Shuffle before dispatch so an interrupted run has broad coverage. A
 // report is final only after EVERY scheduled block has completed.
 for(let i=tasks.length-1;i>0;i--){const j=random()%(i+1);[tasks[i],tasks[j]]=[tasks[j],tasks[i]];}
 const schedule=path.join(config.out,'schedule.json');
 const scheduleText=JSON.stringify(tasks);
 if(fs.existsSync(schedule)&&fs.readFileSync(schedule,'utf8')!==scheduleText)throw Error('Schedule changed');
 fs.writeFileSync(schedule,scheduleText);
 const file=path.join(config.out,'blocks.jsonl'),old=fs.existsSync(file)?fs.readFileSync(file,'utf8'):'';
 if(old&&!old.endsWith('\n'))throw Error('Incomplete final record; recover it explicitly before resume');
 const done=new Set(),counts={};let errors=0;
 for(const line of old.split('\n').filter(Boolean)){const r=JSON.parse(line);if(done.has(r.id))throw Error('Duplicate record');done.add(r.id);counts[r.strength]=(counts[r.strength]||0)+r.games.length;errors+=r.games.filter(g=>!g.winner||g.error).length;}
 const queue=tasks.filter(t=>!done.has(t.id));let cursor=0,alive=0,completed=done.size,lastOutput=0;
 const previousPath=path.join(config.out,'progress.json');
 const prior=fs.existsSync(previousPath)?JSON.parse(fs.readFileSync(previousPath,'utf8')):{};
 const beforeSeconds=prior.totalSessionSeconds||prior.sessionSeconds||0;
 const start=Date.now(),children=[];
 function save(){const report={identity,complete:completed===tasks.length,plannedGames:tasks.length*2,completedGames:completed*2,countsByStrength:counts,errors,activeWorkers:alive,sessionSeconds:(Date.now()-start)/1000,totalSessionSeconds:beforeSeconds+(Date.now()-start)/1000,updatedAt:new Date().toISOString()};
  const tmp=path.join(config.out,'progress.tmp'),dst=path.join(config.out,'progress.json');fs.writeFileSync(tmp,JSON.stringify(report,null,2));replaceProgress(tmp,dst);
  if(Date.now()-lastOutput>30000||report.complete){console.log(JSON.stringify({complete:report.complete,games:report.completedGames,planned:report.plannedGames,errors,workers:alive,totalSeconds:report.totalSessionSeconds}));lastOutput=Date.now();}
 }
 function stop(){return fs.existsSync(path.join(config.out,'STOP'));}
 for(let i=0;i<config.workers;i++){
  const child=cp.fork(__filename,['--worker',configPath],{execArgv:['--max-old-space-size=2048'],stdio:['ignore','ignore','pipe','ipc']});children.push(child);alive++;
  child.stderr.on('data',data=>fs.appendFileSync(path.join(config.out,'worker-errors.log'),data));
  let dispatchedAt=Date.now(),inFlight=null;
  const watchdog=setInterval(()=>{if(inFlight && Date.now()-dispatchedAt>300000){fs.appendFileSync(path.join(config.out,'worker-errors.log'),'Task timeout: '+inFlight.id+'\n');child.kill();}},10000);
  function feed(){inFlight=null;if(cursor>=queue.length||stop()){child.disconnect();child.kill();return;}inFlight=queue[cursor++];dispatchedAt=Date.now();child.send(inFlight);}
  child.on('message',r=>{if(r.ready){feed();return;}if(done.has(r.id))throw Error('Duplicate worker record');
   if(!inFlight||['id','a','b','seed','pair','block','strength'].some(k=>r[k]!==inFlight[k])||!Array.isArray(r.games)||r.games.length!==2)throw Error('Invalid worker record');
   fs.appendFileSync(file,JSON.stringify(r)+'\n');done.add(r.id);completed++;counts[r.strength]=(counts[r.strength]||0)+2;
   errors+=r.games.filter(g=>!g.winner||g.error).length;save();feed();
  });
  child.on('exit',()=>{clearInterval(watchdog);alive--;if(!alive){save();if(completed!==tasks.length||errors)process.exitCode=1;}});
 }
 save();
}
