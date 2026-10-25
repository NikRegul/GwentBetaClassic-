// Diagnostic current-vs-current matches. All deals, decisions and suspect states
// are retained; small samples describe AI behaviour, not a deck tier list.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),cp=require('child_process'),crypto=require('crypto'),zlib=require('zlib');
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
if(process.argv[2]==='--worker'){
 const config=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
 const ctx=vm.createContext({console});
 vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(config.snapshot,n),'utf8')).join('\n')+'\n'+require('../ai/comparison_bridge119.js'),ctx);
 ctx.bridge.setTunes(JSON.parse(fs.readFileSync(path.join(config.snapshot,'tunes.json'),'utf8')));ctx.bridge.setStrength(4);
 vm.runInContext(String.raw`
 function auditCards(){return active.live.filter(c=>{const s=c.Snapshot();return s.positionPlayerId===2&&(s.locationMask===8||s.locationMask===64);}).map(c=>{
  const s=c.Snapshot();let reserve=null;try{reserve=active.AiReserveCost(c.Definition());}catch(e){}
  return {id:s.instanceId,template:c.TemplateId(),title:c.Definition().title,zone:s.locationMask,power:s.power.currentPower,reserve,canPlay:Boolean(s.locationMask===64?active.LeaderAvailable(2):s.canBePlayed)};});}
 function auditPosition(){const m=active.Snapshot();return {preset:active.presetTwo,actor:bridge.view().actor,round:m.roundNumber,score:[active.Score(1),active.Score(2)],crowns:[m.playerOne.crowns,m.playerTwo.crowns],enemyPassed:m.playerOne.hasPassed,enemyHand:active.CountLocation(1,8),enemyLeader:Boolean(active.LeaderAvailable(1)),hand:auditCards()};}
 function auditProbe(id){const log=Host.log;Host.log=null;BetaGwentAISimEnter();
  try{const before=active.Snapshot(),g=active.AiSimClone();if(!g)return {id,valid:false};
   const gain=g.AiSimPlay(id);if(gain===-2147483647||g.IsFatal()||g.IsPending())return {id,valid:false};
   const lead=g.Score(2)-g.Score(1);let m=g.Snapshot();
   if(m.roundActive&&!m.playerTwo.hasPassed)g.Pass(2);
   m=g.Snapshot();if(m.roundActive&&!m.playerOne.hasPassed&&g.CountLocation(1,8)===0&&!g.LeaderAvailable(1))g.Pass(1);
   m=g.Snapshot();return {id,valid:!g.IsFatal()&&!g.IsPending(),gain,lead,roundWon:m.playerTwo.crowns>before.playerTwo.crowns&&(m.matchWinnerMask&1)===0,matchWon:m.matchWinnerMask===2};
  }catch(e){return {id,valid:false,error:String(e)};}finally{BetaGwentAISimLeave();Host.log=log;}}
 function auditRun(task,skipProbes){const logs=[],decisions=[],suspects=[];let step=0,initial=null;
  bridge.setLog(s=>logs.push({step,text:s}));
  try{initial=bridge.initialize(task.left,task.right,task.seed);bridge.initialMulligan();
   for(;step<500;step++){
    let v=bridge.view();if(v.fatal)throw Error(v.message);
    if(v.winner){let winner=v.winner;if(v.reversed)winner=((winner&1)<<1)|((winner&2)>>1);return {winner,steps:step,logs,decisions,suspects,initial};}
    if(!v.mulligan&&!v.pending&&!v.waiting&&v.current===1){bridge.swap();v=bridge.view();}
    const isDecision=!v.mulligan&&!v.pending&&!v.waiting,before=isDecision?auditPosition():null;
    // Preserve the real state only when post-decision checks need a replay.
    const state=isDecision?bridge.dump():null,logStart=logs.length,t0=Date.now();bridge.step();
    if(!isDecision)continue;
    const lines=logs.slice(logStart).map(x=>x.text),selection=lines.find(s=>/event=SELECT\b/.test(s))||lines.find(s=>/event=LEADER\b/.test(s))||'',pass=lines.find(s=>/event=PASS\b/.test(s))||'';
    const afterMatch=active.Snapshot();
    const d={step,before,after:bridge.view(),milliseconds:Date.now()-t0,selection,pass,logStart,logEnd:logs.length};decisions.push(d);
    const exhausted=before.enemyPassed||(before.enemyHand===0&&!before.enemyLeader);
    if(!skipProbes&&exhausted&&before.hand.some(c=>c.canPlay)&&((pass&&before.crowns[0]>0)||(selection&&before.enemyPassed&&before.round<3))){
     const after=bridge.dump();bridge.load(state);const probes=before.hand.filter(c=>c.canPlay).map(c=>({...auditProbe(c.id),card:c}));bridge.load(after);
     const winners=probes.filter(p=>p.valid&&p.roundWon);
     if(pass&&afterMatch.playerTwo.crowns===before.crowns[1]&&winners.length)suspects.push({kind:'pass-with-a-winning-single-action',step,before,pass,alternatives:winners,state});
     if(selection){const match=/\bcard=(\d+)/.exec(selection),picked=match?before.hand.find(c=>c.id===Number(match[1])):/action=leader\b/.test(selection)?before.hand.find(c=>c.zone===64):null;
      if(picked&&picked.reserve>0&&winners.some(p=>p.id===picked.id)){const cheaper=winners.filter(p=>p.card.id!==picked.id&&p.card.reserve!==null&&p.card.reserve<picked.reserve);
       if(cheaper.length)suspects.push({kind:'cheaper-round-win-after-enemy-pass',step,before,selection,picked,alternatives:cheaper,state});}
     }
    }
    if(lines.some(s=>/DUEL_NO_TARGET\b/.test(s)))suspects.push({kind:'no-target-cue-needs-review',step,before,selection,state});
   }throw Error('decision limit');
  }catch(e){return {winner:0,steps:step,error:String(e.stack||e),logs,decisions,suspects,initial,lastState:bridge.dump()};}
 }
 `,ctx);
 process.on('message',task=>{
  const t0=Date.now();ctx.auditTask=task;let result;
  try{result=vm.runInContext('auditRun(auditTask)',ctx,{timeout:300000});}catch(e){result={winner:0,error:String(e.stack||e),suspects:[],decisions:[],logs:[]};}
  if(config.verifyDeterminism){ctx.auditTask=task;const again=vm.runInContext('auditRun(auditTask)',ctx,{timeout:300000});
   const stable=r=>JSON.stringify({winner:r.winner,logs:r.logs,decisions:r.decisions.map(({milliseconds,...d})=>d),suspects:r.suspects});
   if(stable(result)!==stable(again))result.error='Non-deterministic replay';result.deterministic=stable(result)===stable(again);
   const control=vm.runInContext('auditRun(auditTask,true)',ctx,{timeout:300000}),withoutSuspects=r=>JSON.stringify({winner:r.winner,logs:r.logs,decisions:r.decisions.map(({milliseconds,...d})=>d)});
   result.probesDidNotChangePlay=withoutSuspects(result)===withoutSuspects(control);if(!result.probesDidNotChangePlay)result.error='Diagnostic probes changed the match';}
  const file=path.join(config.out,'matches',task.id+'.json.gz');fs.writeFileSync(file,zlib.gzipSync(JSON.stringify({task,...result})));
  const passReasons={},selections={};for(const d of result.decisions){const m=/\breason=([^ ]+)/.exec(d.pass||'');if(m)passReasons[m[1]]=(passReasons[m[1]]||0)+1;const s=/\btemplate=(\d+)/.exec(d.selection||'');if(s)selections[s[1]]=(selections[s[1]]||0)+1;}
  process.send({id:task.id,left:task.left,right:task.right,seed:task.seed,block:task.block,winner:result.winner,steps:result.steps,error:result.error,deterministic:result.deterministic,probesDidNotChangePlay:result.probesDidNotChangePlay,milliseconds:Date.now()-t0,trace:file,decisions:result.decisions.length,passReasons,selections,suspects:result.suspects.map(s=>({kind:s.kind,step:s.step,preset:s.before.preset,round:s.before.round,picked:s.picked,alternatives:s.alternatives}))});
 });process.send({ready:true});return;
}
const configPath=path.resolve(process.argv[2]),config=JSON.parse(fs.readFileSync(configPath,'utf8'));
const manifest=JSON.parse(fs.readFileSync(path.join(config.snapshot,'manifest.json'),'utf8'));
for(const [n,h] of Object.entries(manifest.snapshotFiles))if(sha(path.join(config.snapshot,n))!==h)throw Error('Frozen snapshot changed: '+n);
if(!Number.isInteger(config.workers)||config.workers<1||config.workers>12)throw Error('workers must be 1..12');
if(!Number.isInteger(config.deals)||config.deals<1||!Number.isInteger(config.matchupOffset)||config.matchupOffset<1||config.matchupOffset>=manifest.presets.length||!Number.isInteger(config.seed))throw Error('Invalid experiment');
if(config.smokeGames!==undefined&&(!Number.isInteger(config.smokeGames)||config.smokeGames<1))throw Error('Invalid smokeGames');
fs.mkdirSync(path.join(config.out,'matches'),{recursive:true});
const identity={fingerprint:manifest.fingerprint,toolSha256:sha(__filename),configSha256:sha(configPath),bridgeSha256:sha(path.resolve(__dirname,'../ai/comparison_bridge119.js'))};
const identityPath=path.join(config.out,'identity.json');if(fs.existsSync(identityPath)){if(JSON.stringify(JSON.parse(fs.readFileSync(identityPath,'utf8')))!==JSON.stringify(identity))throw Error('Changed experiment; choose a fresh output folder');}else fs.writeFileSync(identityPath,JSON.stringify(identity,null,2));
const tasks=[],pool=manifest.presets;
for(let i=0;i<pool.length;i++)for(let deal=0;deal<config.deals;deal++)for(const reverse of [false,true]){
 const a=pool[i],b=pool[(i+config.matchupOffset)%pool.length],seed=(config.seed+Math.imul(i+1,2654435761)+deal*1009)>>>0||1;
 tasks.push({id:'game-'+String(tasks.length+1).padStart(5,'0'),left:reverse?b:a,right:reverse?a:b,seed,block:i*config.deals+deal});
}
if(config.smokeGames)tasks.splice(config.smokeGames);
const reportPath=path.join(config.out,'report.json'),records=fs.existsSync(reportPath)?JSON.parse(fs.readFileSync(reportPath,'utf8')).games:[];
const done=new Set(records.map(g=>g.id));let queue=tasks.filter(t=>!done.has(t.id));
// Spread the initial sample across all 46 decks instead of finishing one deck first.
queue.sort((a,b)=>((Number(a.id.slice(5))*2654435761)>>>0)-((Number(b.id.slice(5))*2654435761)>>>0));
let alive=0;const started=Date.now();
function save(){const decks={};for(const id of pool)decks[id]={id,games:0,wins:0,losses:0,draws:0,errors:0,opponents:[],suspects:0};
 for(const g of records)for(const [seat,id,enemy] of [[1,g.left,g.right],[2,g.right,g.left]]){const d=decks[id];d.games++;if(!d.opponents.includes(enemy))d.opponents.push(enemy);if(g.winner===0)d.errors++;else if(g.winner===3)d.draws++;else if(g.winner===seat)d.wins++;else d.losses++;d.suspects+=g.suspects.filter(s=>s.preset===id).length;}
 const report={protocol:'frozen maximum vs maximum; deterministic seed blocks, swapped deck seats; diagnostic sample, not a tier list',identity,complete:records.length===tasks.length,plannedGames:tasks.length,completedGames:records.length,activeWorkers:alive,seconds:(Date.now()-started)/1000,errors:records.filter(g=>g.winner===0||g.error).length,suspects:records.reduce((n,g)=>n+g.suspects.length,0),decks:Object.values(decks),games:records};
 const temp=reportPath+'.tmp';fs.writeFileSync(temp,JSON.stringify(report,null,2));for(let attempt=0;;attempt++)try{fs.renameSync(temp,reportPath);break;}catch(e){if(!['EPERM','EBUSY','EACCES'].includes(e.code)||attempt>=20)throw e;Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,25*(attempt+1));}return report;}
save();
for(let i=0;i<config.workers;i++){
 const child=cp.fork(__filename,['--worker',configPath],{execArgv:['--max-old-space-size=1536'],stdio:['ignore','ignore','pipe','ipc']});alive++;
 child.stderr.on('data',data=>fs.appendFileSync(path.join(config.out,'worker-errors.log'),data));
 function feed(){if(fs.existsSync(path.join(config.out,'STOP'))||queue.length===0){child.disconnect();child.kill();return;}child.send(queue.shift());}
 child.on('message',m=>{if(m.ready){feed();return;}records.push(m);const r=save();console.log(JSON.stringify({completed:r.completedGames,total:r.plannedGames,errors:r.errors,suspects:r.suspects,match:m.id,seconds:Math.round(r.seconds)}));feed();});
 child.on('exit',()=>{alive--;if(alive===0){const r=save();if(!r.complete||r.errors)process.exitCode=1;}});
}
