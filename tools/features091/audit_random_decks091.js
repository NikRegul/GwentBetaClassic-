// Balanced deck coverage with shuffled opponents, seats and independent game seeds.
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),cp=require('child_process');
const configPath=path.resolve(process.argv[2]),config=JSON.parse(fs.readFileSync(configPath,'utf8'));
const manifest=JSON.parse(fs.readFileSync(path.join(config.snapshot,'manifest.json'),'utf8')),pool=manifest.presets;
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
if(!Number.isInteger(config.rounds)||config.rounds<1||config.rounds>=pool.length||!Number.isInteger(config.seed)||!Number.isInteger(config.workers)||config.workers<1||config.workers>12||pool.length%2)throw Error('Invalid random audit configuration');
for(const [name,hash] of Object.entries(manifest.snapshotFiles))if(sha(path.join(config.snapshot,name))!==hash)throw Error('Frozen snapshot changed: '+name);
const worker=path.join(__dirname,'audit_decks091.js'),bridge=path.resolve(__dirname,'../ai/comparison_bridge119.js');
fs.mkdirSync(path.join(config.out,'matches'),{recursive:true});
const identity={fingerprint:manifest.fingerprint,toolSha256:sha(__filename),workerSha256:sha(worker),configSha256:sha(configPath),bridgeSha256:sha(bridge)};
const identityPath=path.join(config.out,'identity.json');
if(fs.existsSync(identityPath)){if(JSON.stringify(JSON.parse(fs.readFileSync(identityPath,'utf8')))!==JSON.stringify(identity))throw Error('Experiment inputs changed');}else fs.writeFileSync(identityPath,JSON.stringify(identity,null,2));
let rng=config.seed>>>0||1;function random(){rng^=rng<<13;rng>>>=0;rng^=rng>>>17;rng>>>=0;rng^=rng<<5;return rng>>>=0;}
const seen=new Set(),seeds=new Set(),tasks=[];
for(let round=0;round<config.rounds;round++){
 let pairs=null;for(let attempt=0;attempt<10000&&!pairs;attempt++){
  const order=pool.slice();for(let i=order.length-1;i>0;i--){const j=random()%(i+1);[order[i],order[j]]=[order[j],order[i]];}
  const next=[];let valid=true;for(let i=0;i<order.length;i+=2){const a=order[i],b=order[i+1],key=[a,b].sort((x,y)=>x-y).join(':');if(seen.has(key)){valid=false;break;}next.push({a,b,key});}if(valid)pairs=next;
 }if(!pairs)throw Error('Could not avoid repeated opponents; use fewer rounds');
 for(const {a,b,key} of pairs){seen.add(key);const flip=(random()&1)!==0;let seed;do{seed=random();}while(!seed||seeds.has(seed));seeds.add(seed);
  tasks.push({id:'game-'+String(tasks.length+1).padStart(5,'0'),left:flip?b:a,right:flip?a:b,seed,block:round});
 }
}
const schedulePath=path.join(config.out,'schedule.json');
if(fs.existsSync(schedulePath)&&JSON.stringify(JSON.parse(fs.readFileSync(schedulePath,'utf8')))!==JSON.stringify(tasks))throw Error('Schedule changed');
fs.writeFileSync(schedulePath,JSON.stringify(tasks,null,2));
const reportPath=path.join(config.out,'report.json'),records=fs.existsSync(reportPath)?JSON.parse(fs.readFileSync(reportPath,'utf8')).games:[],done=new Set(records.map(x=>x.id)),queue=tasks.filter(x=>!done.has(x.id));
let alive=0;const started=Date.now();
function save(){const decks=Object.fromEntries(pool.map(id=>[id,{id,games:0,wins:0,losses:0,draws:0,errors:0,opponents:[],suspects:0}]));
 for(const g of records)for(const [seat,id,enemy] of [[1,g.left,g.right],[2,g.right,g.left]]){const d=decks[id];d.games++;if(!d.opponents.includes(enemy))d.opponents.push(enemy);d[g.error||!g.winner?'errors':g.winner===3?'draws':g.winner===seat?'wins':'losses']++;d.suspects+=g.suspects.filter(s=>s.preset===id).length;}
 const r={protocol:'frozen maximum vs maximum; shuffled perfect matchings without repeated opponents; random seats; independent recorded game seeds; diagnostic sample, not a tier list',identity,complete:records.length===tasks.length,plannedGames:tasks.length,completedGames:records.length,activeWorkers:alive,seconds:(Date.now()-started)/1000,errors:records.filter(g=>g.error||!g.winner).length,suspects:records.reduce((n,g)=>n+g.suspects.length,0),decks:Object.values(decks),games:records};
 const temp=reportPath+'.tmp';fs.writeFileSync(temp,JSON.stringify(r,null,2));for(let attempt=0;;attempt++)try{fs.renameSync(temp,reportPath);break;}catch(e){if(!['EPERM','EBUSY','EACCES'].includes(e.code)||attempt>=20)throw e;Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,25*(attempt+1));}return r;
}
save();
for(let i=0;i<config.workers;i++){
 const child=cp.fork(worker,['--worker',configPath],{execArgv:['--max-old-space-size=1536'],stdio:['ignore','ignore','pipe','ipc']});alive++;
 child.stderr.on('data',x=>fs.appendFileSync(path.join(config.out,'worker-errors.log'),x));
 function feed(){if(!queue.length||fs.existsSync(path.join(config.out,'STOP'))){child.disconnect();child.kill();return;}child.send(queue.shift());}
 child.on('message',m=>{if(m.ready){feed();return;}records.push(m);const r=save();console.log(JSON.stringify({completed:r.completedGames,total:r.plannedGames,errors:r.errors,suspects:r.suspects}));feed();});
 child.on('exit',()=>{alive--;if(!alive){const r=save();if(!r.complete||r.errors)process.exitCode=1;}});
}
