// Repeated single-elimination brackets; no policy changes in the runner.
'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process'),crypto=require('crypto');
const schedule=require('./bracket_schedule092.js');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
function atomic(p,x){const tmp=p+'.tmp';fs.writeFileSync(tmp,JSON.stringify(x,null,2));
 for(let i=0;;i++)try{fs.renameSync(tmp,p);break;}catch(e){if(i>=20||!['EPERM','EBUSY','EACCES'].includes(e.code))throw e;Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,50*(i+1));}}
if(process.argv[2]==='--version-metadata'){
 fs.writeFileSync(process.argv[5],JSON.stringify(require('./versioned_match092.js').metadata(path.resolve(process.argv[3]),path.resolve(process.argv[4])),null,2));
}else if(process.argv[2]==='--metadata'){
 const snapshot=path.resolve(process.argv[3]),manifest=read(path.join(snapshot,'manifest.json'));
 const code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n');
 const decks=new Function('ids',code+String.raw`
 return ids.map(id=>{const p=BetaGwentDuelPreset(id),leader=BetaGwentDuelDefinition(p.leaderTemplateId),cards={v:[]};BetaGwentDuelPresetDeck(id,cards);
  const legal=BetaGwentValidateDeck(cards.v,leader.header.factionMask,p.leaderTemplateId);if(!legal.valid)throw Error(legal.message);
  return {presetId:id,title:BetaGwentAIProfileTitle(BetaGwentAIPresetProfile(id)),leader:p.leaderTemplateId,faction:leader.header.factionMask,templateIds:cards.v};});`)(manifest.presets);
 fs.writeFileSync(process.argv[4],JSON.stringify({fingerprint:manifest.fingerprint,decks},null,2));
}else if(process.argv[2]==='--worker'){
 const config=read(process.argv[3]),h=config.versioned?require('./versioned_match092.js').load(config):require('./variant_decks092.js').load(config.snapshot);if(!config.versioned)h.Host.simDamp=config.simDamp;
 process.on('message',n=>{
  try{
   const start=Date.now(),games=[];
   for(let pair=0;pair<n.seeds.length;pair++){
    for(const reverse of [false,true]){
     const t=Date.now(),g=h.play(reverse?n.b:n.a,reverse?n.a:n.b,n.seeds[pair],config.strength,config.strength,100);
     if(g.error||!g.winner)throw Error(JSON.stringify(g));games.push({...g,milliseconds:Date.now()-t});
    }
    if(games.length>=4&&schedule.points(games,n.a)!==games.length/2)break;
   }
   const pointsA=schedule.points(games,n.a),lotUsed=pointsA===games.length/2;
   const winnerDeck=lotUsed?(n.lot?n.b:n.a):(pointsA>games.length/2?n.a:n.b);
   const r={id:n.id,bracket:n.bracket,stage:n.stage,a:n.a,b:n.b,games,pointsA,lotUsed,winnerDeck,loserDeck:winnerDeck===n.a?n.b:n.a,milliseconds:Date.now()-start};
   schedule.validate(n,r);process.send(r);
  }catch(e){process.send({failed:n.id,error:String(e.stack||e)});}
 });process.send({ready:true});
}else{
 const configPath=path.resolve(process.argv[2]),config=read(configPath),manifest=read(path.join(config.snapshot,'manifest.json'));
 if(config.strength!==4||manifest.presets.length!==46||config.workers<1||config.workers>18||config.simDamp<0||config.simDamp>70)throw Error('Invalid tournament configuration');
 for(const [name,hash]of Object.entries(manifest.snapshotFiles))if(sha(path.join(config.snapshot,name))!==hash)throw Error('Modified frozen rules '+name);
 if(config.versioned){for(const [name,hash]of Object.entries(config.oldPolicyFiles))if(sha(path.join(config.oldPolicy,name))!==hash)throw Error('Modified original policy '+name);}
 const pool=config.versioned?read(path.join(config.out,'deck-metadata.json')).decks.map(d=>d.presetId):manifest.presets;
 const plan=schedule.plan(pool,config.cycles,config.seed,config.maxSeedPairs,Boolean(config.benchmark));
 const planPath=path.join(config.out,'schedule.json'),serialized=JSON.stringify(plan);
 if(fs.existsSync(planPath)&&fs.readFileSync(planPath,'utf8')!==serialized)throw Error('Changed bracket schedule');
 fs.writeFileSync(planPath,serialized);
 const tools={};for(const n of ['bracket_tournament092.js','bracket_schedule092.js','variant_decks092.js',...(config.versioned?['versioned_match092.js','comparison_bridge119.js']:[])])tools[n]=sha(path.join(__dirname,n));
 const identity={fingerprint:manifest.fingerprint,configSha256:sha(configPath),scheduleSha256:sha(planPath),tools,protocol:'balanced23-bracket cycles; mirrored seed pairs;4 mandatory games, fixed bounded tie-breaks, neutral precommitted final lot; no live rule changes'};
 if(config.versioned)identity.versionComparison={originalFingerprint:config.originalFingerprint,originalVersion:'0.9.1',newVersion:config.benchmark?'0.9.2-candidate-speed-check':'0.9.2-final16:00',oldPolicyFiles:config.oldPolicyFiles,sharedBattleMechanics:true,ownHistoricalRosters:true};
 const identityPath=path.join(config.out,'identity.json');
 if(fs.existsSync(identityPath)&&JSON.stringify(read(identityPath))!==JSON.stringify(identity))throw Error('Changed experiment identity');
 atomic(identityPath,identity);
 const file=path.join(config.out,'series.jsonl'),raw=fs.existsSync(file)?fs.readFileSync(file,'utf8'):'';
 if(raw&&!raw.endsWith('\n'))throw Error('Incomplete last record; preserve and explicitly recover it before resuming');
 const done=new Map(),nodes=new Map(plan.nodes.map(n=>[n.id,n]));
 for(const line of raw.split('\n').filter(Boolean)){
  const r=JSON.parse(line),n=nodes.get(r.id);if(!n||done.has(r.id))throw Error('Unknown or duplicate series');
  const task=schedule.available(n,done);if(!task)throw Error('Record precedes its parent');schedule.validate(task,r);done.set(r.id,r);
 }
 const oldPath=path.join(config.out,'progress.json'),prior=fs.existsSync(oldPath)?read(oldPath):{};
 const beforeSeconds=prior.totalSeconds||0,start=Date.now(),busy=new Set(),children=[];
 let completedGames=Array.from(done.values()).reduce((s,r)=>s+r.games.length,0),errors=prior.errors||0,failed=false,stopping=false,lastPrint=0,finishedAt=prior.finishedAt||null;
 function save(){const complete=done.size===plan.nodes.length;
  const r={identity,complete,benchmark:Boolean(config.benchmark),brackets:plan.brackets.length,plannedSeries:plan.nodes.length,completedSeries:done.size,
   minimumGames:plan.nodes.length*4,maximumGames:plan.nodes.length*config.maxSeedPairs*2,completedGames,errors,activeWorkers:children.filter(c=>!c.exited).length,
   totalSeconds:beforeSeconds+(Date.now()-start)/1000,updatedAt:new Date().toISOString()};
  if(complete&&!finishedAt)finishedAt=r.updatedAt;r.finishedAt=finishedAt;
  atomic(oldPath,r);if(Date.now()-lastPrint>30000||complete){console.log(JSON.stringify(r));lastPrint=Date.now();}
 }
 function abort(message){failed=true;errors++;fs.appendFileSync(path.join(config.out,'worker-errors.log'),message+'\n');save();for(const c of children)if(!c.exited)c.child.kill();process.exitCode=1;}
 function dispatch(c){
  if(c.exited||c.task)return;
  if(failed||stopping||done.size===plan.nodes.length){c.child.disconnect();c.child.kill();return;}
  for(const n of plan.nodes){if(done.has(n.id)||busy.has(n.id))continue;const task=schedule.available(n,done);if(!task)continue;
   busy.add(n.id);c.task=task;c.started=Date.now();c.child.send(task);return;}
 }
 for(let i=0;i<config.workers;i++){
  const child=cp.fork(__filename,['--worker',configPath],{execArgv:['--max-old-space-size=2048'],stdio:['ignore','ignore','pipe','ipc']});
  const c={child,task:null,exited:false,ready:false};children.push(c);
  child.stderr.on('data',v=>fs.appendFileSync(path.join(config.out,'worker-errors.log'),v));
  child.on('message',r=>{
   try{
    if(r.ready){c.ready=true;dispatch(c);return;}if(r.failed)throw Error(r.failed+': '+r.error);
    if(!c.task||done.has(r.id))throw Error('Unexpected worker record');schedule.validate(c.task,r);
    fs.appendFileSync(file,JSON.stringify(r)+'\n');done.set(r.id,r);busy.delete(r.id);c.task=null;completedGames+=r.games.length;save();
    for(const other of children)if(other.ready)dispatch(other);
   }catch(e){abort(String(e.stack||e));}
  });
  child.on('exit',()=>{c.exited=true;if(c.task&&!failed)abort('Worker exited with unfinished '+c.task.id);if(children.every(v=>v.exited)){clearInterval(timer);save();if(done.size!==plan.nodes.length)process.exitCode=1;}});
 }
 const timer=setInterval(()=>{
  if(fs.existsSync(path.join(config.out,'STOP'))){stopping=true;for(const c of children)if(c.ready&&!c.task)dispatch(c);}
  for(const c of children)if(c.task&&Date.now()-c.started>900000){abort('Series timeout '+c.task.id);break;}
  save();if(children.every(c=>c.exited))clearInterval(timer);
 },15000);
 save();
}
