// Frozen targeted paired experiment. Opponents always use the baseline policy.
'use strict';const fs=require('fs'),path=require('path'),cp=require('child_process'),crypto=require('crypto'),zlib=require('zlib');
const bridge=require('./comparison_bridge119.js'),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
function host(dir){const code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(dir,n),'utf8')).join('\n');
 return new Function(code+'\n'+bridge+String.raw`
bridge.inspect=()=>({hand:active.live.map(c=>c.Snapshot()).filter(s=>s.positionPlayerId===2&&s.locationMask===8).map(s=>({id:s.instanceId,template:s.runtimeTemplate.templateId,power:s.power.currentPower})),
 board:active.live.map(c=>c.Snapshot()).filter(s=>(s.locationMask&7)!==0).map(s=>({id:s.instanceId,template:s.runtimeTemplate.templateId,side:s.positionPlayerId,row:s.locationMask,power:s.power.currentPower,tokens:s.tokenMask,timer:s.timerValue}))});return bridge;`)();}
if(process.argv[2]==='--worker'){
 const config=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),versions=Object.fromEntries(Object.entries(config.versions).map(([k,dir])=>[k,host(dir)])),enemy=host(config.baseline);
 for(const [key,h]of Object.entries(versions)){const dir=config.versions[key];h.setTunes(JSON.parse(fs.readFileSync(path.join(dir,'tunes.json'))));}
 enemy.setTunes(JSON.parse(fs.readFileSync(path.join(config.baseline,'tunes.json'))));
 function play(task,key,mirror){const subject=versions[key],seat=mirror?1:0,trace=[],logs=[];let h=subject,step=0;
  subject.setStrength(task.strength);enemy.setStrength(task.strength);subject.setLog(s=>{if(config.diagnostic)logs.push(s);});enemy.setLog(null);
  try{
   // For roster changes the same seed supplies common random numbers, not
   // identical card identities. For policy-only arms the raw deal is exact.
   const initial=subject.initialize(task.deck,task.enemy,task.seed);if(mirror)subject.mirror();
   const first=seat===1?subject:enemy;if(first!==h){first.load(h.dump());h=first;}h.initialMulligan();
   for(;step<500;step++){let v=h.view();if(v.fatal)throw Error(v.message);
    if(v.winner){const winner=v.reversed?((v.winner&1)<<1)|((v.winner&2)>>1):v.winner;return {winner,score:winner===3?.5:Number(winner===seat+1),steps:step,trace};}
    if(!v.mulligan&&!v.pending&&!v.waiting&&v.current===1){h.swap();v=h.view();}
    const chooser=v.mulligan?1-v.actor:v.actor,target=chooser===seat?subject:enemy;
    if(target!==h){target.load(h.dump());h=target;}
    const capture=config.diagnostic&&target===subject&&!v.pending&&!v.mulligan&&!v.waiting;
    const before=capture?{view:h.view(),...h.inspect(),state:h.dump()}:null;logs.length=0;h.step();
    if(capture)trace.push({step,before,after:h.view(),logs:logs.slice()});
   }throw Error('decision limit');
  }catch(e){return {winner:0,score:0,error:String(e.stack||e),steps:step,trace};}
 }
 process.on('message',task=>{const results=[];for(const key of Object.keys(versions))for(const mirror of [false,true]){
   const r=play(task,key,mirror);if(config.diagnostic){const name=task.id+'-'+key+'-'+Number(mirror)+'.json.gz';fs.writeFileSync(path.join(config.out,'traces',name),zlib.gzipSync(JSON.stringify({task,key,mirror,...r})));r.traceFile=name;}delete r.trace;results.push({version:key,mirror,...r});}
  process.send({...task,results});});process.send({ready:true});
}else{
 const configPath=path.resolve(process.argv[2]),config=JSON.parse(fs.readFileSync(configPath));fs.mkdirSync(config.out,{recursive:true});if(config.diagnostic)fs.mkdirSync(path.join(config.out,'traces'),{recursive:true});
 const identity={config:sha(configPath),tool:sha(__filename),bridge:sha(path.join(__dirname,'comparison_bridge119.js')),versions:Object.fromEntries(Object.entries(config.versions).map(([k,d])=>[k,sha(path.join(d,'rules.js'))])),baseline:sha(path.join(config.baseline,'rules.js'))};
 const idfile=path.join(config.out,'identity.json');if(fs.existsSync(idfile)&&JSON.stringify(JSON.parse(fs.readFileSync(idfile)))!==JSON.stringify(identity))throw Error('Changed frozen experiment');fs.writeFileSync(idfile,JSON.stringify(identity,null,2));
 let state=config.seed>>>0||1;function random(){state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>=0;}
 const tasks=[];for(const strength of config.levels)for(const deck of config.decks)for(const opponent of config.opponents)if(deck!==opponent)for(let b=0;b<config.blocks[String(strength)];b++)tasks.push({id:'s'+strength+'-d'+deck+'-e'+opponent+'-b'+b,strength,deck,enemy:opponent,block:b,seed:random()||1});
 for(let i=tasks.length-1;i>0;i--){const j=random()%(i+1);[tasks[i],tasks[j]]=[tasks[j],tasks[i]];}
 const schedule=path.join(config.out,'schedule.json');if(fs.existsSync(schedule)&&fs.readFileSync(schedule,'utf8')!==JSON.stringify(tasks))throw Error('Schedule changed');fs.writeFileSync(schedule,JSON.stringify(tasks));
 const file=path.join(config.out,'blocks.jsonl'),records=fs.existsSync(file)?fs.readFileSync(file,'utf8').trim().split('\n').filter(Boolean).map(JSON.parse):[],done=new Set(records.map(x=>x.id)),queue=tasks.filter(x=>!done.has(x.id));let cursor=0,alive=0,last=0;
 function save(){const games=records.flatMap(x=>x.results),report={identity,complete:records.length===tasks.length,blocks:records.length,plannedBlocks:tasks.length,completedGames:games.length,plannedGames:tasks.length*Object.keys(config.versions).length*2,errors:games.filter(x=>!x.winner||x.error).length,byDeck:{}};
  for(const strength of config.levels)for(const deck of config.decks){const blocks=records.filter(x=>x.strength===strength&&x.deck===deck),row={strength,deck,blocks:blocks.length,versions:{},differences:{}};
   for(const key of Object.keys(config.versions)){const a=blocks.flatMap(x=>x.results.filter(g=>g.version===key));row.versions[key]={games:a.length,wins:a.filter(g=>g.score===1).length,draws:a.filter(g=>g.score===.5).length,losses:a.filter(g=>g.winner&&g.score===0).length,score:a.length?a.reduce((n,g)=>n+g.score,0)/a.length:null};
    if(key!=='old'){const delta=blocks.map(x=>x.results.filter(g=>g.version===key).reduce((n,g)=>n+g.score,0)/2-x.results.filter(g=>g.version==='old').reduce((n,g)=>n+g.score,0)/2),mean=delta.reduce((n,x)=>n+x,0)/delta.length,se=delta.length>1?Math.sqrt(delta.reduce((n,x)=>n+(x-mean)**2,0)/(delta.length-1)/delta.length):null;row.differences[key]={mean,approximate95:se===null?null:[mean-1.96*se,mean+1.96*se]};}}
   report.byDeck[strength+'-'+deck]=row;}
  fs.writeFileSync(path.join(config.out,'report.tmp'),JSON.stringify(report,null,2));fs.renameSync(path.join(config.out,'report.tmp'),path.join(config.out,'report.json'));if(Date.now()-last>60000||report.complete){console.log(JSON.stringify({complete:report.complete,games:report.completedGames,planned:report.plannedGames,errors:report.errors}));last=Date.now();}return report;
 }
 for(let i=0;i<config.workers;i++){const child=cp.fork(__filename,['--worker',configPath],{execArgv:['--max-old-space-size=2048'],stdio:['ignore','ignore','pipe','ipc']});alive++;child.stderr.on('data',x=>fs.appendFileSync(path.join(config.out,'errors.log'),x));
  function feed(){if(cursor>=queue.length){child.disconnect();child.kill();return;}child.send(queue[cursor++]);}
  child.on('message',x=>{if(x.ready){feed();return;}if(done.has(x.id))throw Error('Duplicate record');done.add(x.id);records.push(x);fs.appendFileSync(file,JSON.stringify(x)+'\n');save();feed();});child.on('exit',()=>{if(!--alive){const r=save();if(!r.complete||r.errors)process.exitCode=1;}});
 }save();
}
