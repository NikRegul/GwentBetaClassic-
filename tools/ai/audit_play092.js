// Error-class audit: the same seeded deals are self-played by every version (both seats);
// decision logs are scanned for known mistakes. Counts per version show whether a class of
// error disappeared, more directly than a win rate. Resume-safe (append-only records).
//   node tools/ai/audit_play092.js config.json
// config: {versions:{old:dir,new:dir}, out, seed, workers, simDamp, gamesByStrength:{"2":n,"4":n}}
'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process'),crypto=require('crypto');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const DETECTORS={
 conceding_pass:'pass in a round whose loss loses the match, behind on score, with cards in hand',
 empty_slyzard:'Slyzard played with no gain (no bronze grave unit with a deck copy)',
 spy_boost:'a boost (effect 2) put on a spy that sits on the booster\'s side',
 nekker_deck_emptied:'a consume chain summoned the last deck Nekker before round 3'};
function load(dir){const marker='return { left, right, seed, winner: w, steps, crowns: sc };';
 let code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(dir,n),'utf8')).join('\n');
 if(!code.includes(marker))throw Error('Harness marker missing in '+dir);
 code=code.replace(marker,'return { left, right, seed, winner: w, steps, crowns: sc, trace };');
 return new Function(code+'\nreturn {h:__harness,spy:BetaGwentDuelSpying};')();}
function detect(trace,isSpy){
 const counts=Object.fromEntries(Object.keys(DETECTORS).map(k=>[k,0]));const begin={};let lastPlay=null,spies=new Set(),round=1;
 for(const line of trace){
  let m=/decision=(\d+) event=BEGIN round=(\d+).*?ownScore=(-?\d+) enemyScore=(-?\d+) ownHand=(\d+).*?enemyCrowns=(\d+)/.exec(line);
  if(m){begin[m[1]]={round:+m[2],own:+m[3],enemy:+m[4],hand:+m[5],enemyCrowns:+m[6]};round=+m[2];continue;}
  m=/decision=(\d+) event=PASS .*?ownScore=(-?\d+) enemyScore=(-?\d+) ownHand=(\d+)/.exec(line);
  if(m){const b=begin[m[1]];if(b&&b.enemyCrowns>0&&+m[2]<+m[3]&&+m[4]>0)counts.conceding_pass++;continue;}
  m=/event=SELECT action=card card=\d+ template=200539 gain=(-?\d+)/.exec(line);if(m){if(+m[1]<=0)counts.empty_slyzard++;continue;}
  m=/DUEL_PLAY player=\d+ template=(\d+)/.exec(line);if(m){lastPlay=+m[1];continue;}
  m=/DUEL_PLAY_PUSH depth=1 card=(\d+)/.exec(line);if(m){if(lastPlay&&isSpy(lastPlay))spies.add(+m[1]);lastPlay=null;continue;}
  m=/TARGET_SELECT request=\d+ target=(\d+) effect=2 /.exec(line);if(m){if(spies.has(+m[1]))counts.spy_boost++;continue;}
  if(/DUEL_DEATHWISH .*summon=132305/.test(line)){trace._pendingNekker=true;continue;}
  if(trace._pendingNekker){trace._pendingNekker=false;if(!/DUEL_DECK_SUMMON .*template=132305/.test(line)&&round<3)counts.nekker_deck_emptied++;}
 }
 return counts;}
if(process.argv[2]==='--worker'){
 const config=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
 const versions=Object.fromEntries(Object.entries(config.versions).map(([k,d])=>{const v=load(d);v.h.Host.simDamp=config.simDamp;return [k,v];}));
 process.on('message',task=>{const out={};
  for(const [key,v]of Object.entries(versions)){const games=[];
   for(const reverse of [false,true]){const a=reverse?task.b:task.a,b=reverse?task.a:task.b;
    try{const r=v.h.play(a,b,task.seed,task.strength,task.strength,1e7);games.push({winner:r.winner,steps:r.steps,counts:detect(r.trace,t=>!!v.spy(t))});}
    catch(e){games.push({winner:0,error:String(e.stack||e).slice(0,400)});}}
   out[key]=games;}
  process.send({...task,results:out});});process.send({ready:true});
}else{
 const configPath=path.resolve(process.argv[2]),config=JSON.parse(fs.readFileSync(configPath,'utf8'));fs.mkdirSync(config.out,{recursive:true});
 const pools=Object.values(config.versions).map(d=>JSON.parse(fs.readFileSync(path.join(d,'manifest.json'),'utf8')).presets);
 const pool=pools[0].filter(p=>pools.every(q=>q.includes(p)));
 const identity={config:sha(configPath),tool:sha(__filename),versions:Object.fromEntries(Object.entries(config.versions).map(([k,d])=>[k,sha(path.join(d,'rules.js'))])),detectors:DETECTORS};
 const idf=path.join(config.out,'identity.json');if(fs.existsSync(idf)&&fs.readFileSync(idf,'utf8')!==JSON.stringify(identity,null,2))throw Error('Changed experiment; use a new out');fs.writeFileSync(idf,JSON.stringify(identity,null,2));
 let state=config.seed>>>0||1;const rnd=()=>{state^=state<<13;state>>>=0;state^=state>>>17;state^=state<<5;return state>>>=0;};
 const tasks=[];for(const [s,n]of Object.entries(config.gamesByStrength))for(let i=0;i<n;i++){const a=pool[rnd()%pool.length];let b;do{b=pool[rnd()%pool.length];}while(b===a);tasks.push({id:'s'+s+'-'+i,strength:+s,a,b,seed:rnd()||1});}
 const file=path.join(config.out,'records.jsonl'),records=fs.existsSync(file)?fs.readFileSync(file,'utf8').split('\n').filter(Boolean).map(JSON.parse):[];
 const done=new Set(records.map(r=>r.id)),queue=tasks.filter(t=>!done.has(t.id));let cursor=0,alive=0,last=0;
 function save(){const report={identity,complete:records.length===tasks.length,blocks:records.length,planned:tasks.length,versions:{}};
  for(const key of Object.keys(config.versions)){const games=records.flatMap(r=>r.results[key]);const sum=Object.fromEntries(Object.keys(DETECTORS).map(k=>[k,0]));
   for(const g of games)if(g.counts)for(const k in g.counts)sum[k]+=g.counts[k];
   report.versions[key]={games:games.length,errors:games.filter(g=>!g.winner).length,perThousandGames:Object.fromEntries(Object.entries(sum).map(([k,v])=>[k,games.length?Math.round(v*10000/games.length)/10:0])),totals:sum};}
  fs.writeFileSync(path.join(config.out,'report.json'),JSON.stringify(report,null,2));
  if(Date.now()-last>30000||report.complete){console.log(JSON.stringify({blocks:report.blocks,planned:report.planned,totals:Object.fromEntries(Object.entries(report.versions).map(([k,v])=>[k,v.totals]))}));last=Date.now();}return report;}
 for(let i=0;i<config.workers;i++){const child=cp.fork(__filename,['--worker',configPath],{execArgv:['--max-old-space-size=3072'],stdio:['ignore','ignore','pipe','ipc']});alive++;
  child.stderr.on('data',d=>fs.appendFileSync(path.join(config.out,'worker-errors.log'),d));
  const feed=()=>{if(cursor>=queue.length||fs.existsSync(path.join(config.out,'STOP'))){child.disconnect();child.kill();return;}child.send(queue[cursor++]);};
  child.on('message',x=>{if(x.ready){feed();return;}records.push(x);fs.appendFileSync(file,JSON.stringify(x)+'\n');save();feed();});
  child.on('exit',()=>{if(!--alive){const r=save();if(!r.complete)process.exitCode=1;}});}
 save();
}
