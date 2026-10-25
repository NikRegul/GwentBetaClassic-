// Fixed behavioural opponents probe human-like pressure/retention patterns.
// They are stress policies, not a claim to reproduce a human player's skill.
'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process'),crypto=require('crypto');
const bridgeSource=require('./comparison_bridge119.js');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
function host(dir,style){const code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(dir,n),'utf8')).join('\n');
 const custom=String.raw`
const regularStep=CBetaGwentDuelSession.prototype.OpponentStep,regularReserve=CBetaGwentDuelSession.prototype.AiReserveCost;
CBetaGwentDuelSession.prototype.OpponentStep=function(){
 const m=this.Snapshot();
 if(!this.aiSimulating&&this.CanAct(2)&&!m.playerOne.hasPassed){
  if(style==='dry-pass'&&m.roundNumber===2&&m.playerTwo.crowns>0&&this.Score(1)===0&&this.Score(2)===0)return this.Pass(2);
  if(style==='save-hand'&&m.roundNumber===1&&m.playerOne.crowns===0&&this.CountLocation(2,8)>=this.CountLocation(1,8)+2&&this.Score(1)-this.Score(2)>=12)return this.Pass(2);
 }
 return regularStep.call(this);
};
CBetaGwentDuelSession.prototype.AiReserveCost=function(d){
 const base=regularReserve.call(this,d),m=this.Snapshot();
 if(style==='tempo'&&m.roundNumber<3&&!m.playerOne.hasPassed)return Math.min(0,base);
 if(style==='late-control'&&m.roundNumber<3&&!m.playerOne.hasPassed&&this.CountLocation(2,8)>2&&BetaGwentAIControlCard(d))return base+12;
 return base;
};
`;
 const make=new Function('style',code+'\n'+bridgeSource+'\n'+(style?custom:'')+'\nreturn globalThis.bridge;');
 const h=make(style);h.setTunes(JSON.parse(fs.readFileSync(path.join(dir,'tunes.json'),'utf8')));h.setStrength(4);return h;
}
if(process.argv[2]==='--worker'){
 const config=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
 const subject={new:host(config.candidate),old:host(config.baseline)},opponents=Object.fromEntries(config.styles.map(s=>[s,host(config.baseline,s)]));
 function play(initial,version,mirror){const player=subject[version],enemy=opponents[current.style];let h=player,step=0;
  try{h.load(initial);if(mirror)h.mirror();const seat=mirror?1:0;
   // The initial mulligan belongs to the raw right seat. Other choices use
   // the same actor calculation as the verified paired comparison runner.
   const first=seat===1?player:enemy;if(first!==h){first.load(h.dump());h=first;}h.initialMulligan();
   for(;step<500;step++){
    let v=h.view();if(v.fatal)throw Error(v.message);
    if(v.winner){const winner=v.reversed?((v.winner&1)<<1)|((v.winner&2)>>1):v.winner;return {winner,subjectSeat:seat+1,steps:step,score:winner===3?.5:Number(winner===seat+1)};}
    if(!v.mulligan&&!v.pending&&!v.waiting&&v.current===1){h.swap();v=h.view();}
    const chooser=v.mulligan?1-v.actor:v.actor,target=chooser===seat?player:enemy;
    if(target!==h){target.load(h.dump());h=target;}h.step();
   }throw Error('decision limit');
  }catch(e){return {winner:0,error:String(e.stack||e),steps:step};}
 }
 let current;
 process.on('message',task=>{current=task;const initial=subject.new.initialize(task.a,task.b,task.seed),results=[];
  for(const version of ['old','new'])for(const mirror of [false,true])results.push({version,mirror,...play(initial,version,mirror)});
  process.send({...task,results});
 });process.send({ready:true});
}else{
 const file=path.resolve(process.argv[2]),config=JSON.parse(fs.readFileSync(file,'utf8'));fs.mkdirSync(config.out,{recursive:true});
 const pool=JSON.parse(fs.readFileSync(path.join(config.candidate,'manifest.json'),'utf8')).presets;
 const identity={configSha256:sha(file),toolSha256:sha(__filename),bridgeSha256:sha(path.join(__dirname,'comparison_bridge119.js')),candidate:sha(path.join(config.candidate,'rules.js')),baseline:sha(path.join(config.baseline,'rules.js'))};
 const identityPath=path.join(config.out,'identity.json');if(fs.existsSync(identityPath)&&JSON.stringify(JSON.parse(fs.readFileSync(identityPath)))!==JSON.stringify(identity))throw Error('Changed arena inputs');fs.writeFileSync(identityPath,JSON.stringify(identity,null,2));
 let rng=config.seed>>>0||1;const random=()=>{rng^=rng<<13;rng>>>=0;rng^=rng>>>17;rng^=rng<<5;return rng>>>=0;};
 const tasks=[];for(let cycle=0;cycle<config.cycles;cycle++)for(const style of config.styles){let order;
  do{order=pool.slice();for(let i=45;i>0;i--){const j=random()%(i+1);[order[i],order[j]]=[order[j],order[i]];}}while(order.some((d,i)=>d===pool[i]));
  for(let i=0;i<46;i++)tasks.push({id:`${cycle}-${style}-${i}`,style,a:pool[i],b:order[i],seed:random()||1});
 }
 if(config.smokePerStyle)for(let i=tasks.length-1;i>=0;i--)if(Number(tasks[i].id.split('-').at(-1))>=config.smokePerStyle)tasks.splice(i,1);
 fs.writeFileSync(path.join(config.out,'schedule.json'),JSON.stringify(tasks));
 const recordsFile=path.join(config.out,'blocks.jsonl'),records=fs.existsSync(recordsFile)?fs.readFileSync(recordsFile,'utf8').trim().split('\n').filter(Boolean).map(s=>JSON.parse(s)):[],done=new Set(records.map(r=>r.id)),queue=tasks.filter(t=>!done.has(t.id));
 let cursor=0,alive=0,last=0;
 function save(){const report={identity,complete:records.length===tasks.length,plannedGames:tasks.length*4,completedGames:records.length*4,errors:records.reduce((n,r)=>n+r.results.filter(g=>!g.winner||g.error).length,0),styles:{}};
  for(const style of config.styles){const blocks=records.filter(r=>r.style===style),row={blocks:blocks.length,games:blocks.length*4};
   for(const version of ['old','new']){const games=blocks.flatMap(r=>r.results.filter(g=>g.version===version));row[version]={games:games.length,wins:games.filter(g=>g.score===1).length,draws:games.filter(g=>g.score===.5).length,score:games.reduce((n,g)=>n+(g.score||0),0)/games.length};}
   const differences=blocks.map(r=>r.results.filter(g=>g.version==='new').reduce((n,g)=>n+(g.score||0),0)/2-r.results.filter(g=>g.version==='old').reduce((n,g)=>n+(g.score||0),0)/2),mean=differences.reduce((n,x)=>n+x,0)/differences.length;
   const se=differences.length>1?Math.sqrt(differences.reduce((n,x)=>n+(x-mean)**2,0)/(differences.length-1)/differences.length):null;
   row.pairedDifference=mean;row.approximate95=se===null?null:[mean-1.96*se,mean+1.96*se];report.styles[style]=row;
  }
  fs.writeFileSync(path.join(config.out,'report.tmp'),JSON.stringify(report,null,2));fs.renameSync(path.join(config.out,'report.tmp'),path.join(config.out,'report.json'));
  if(Date.now()-last>15000||report.complete){console.log(JSON.stringify({completedGames:report.completedGames,plannedGames:report.plannedGames,errors:report.errors}));last=Date.now();}return report;
 }
 for(let i=0;i<config.workers;i++){
  const child=cp.fork(__filename,['--worker',file],{execArgv:['--max-old-space-size=2048'],stdio:['ignore','ignore','pipe','ipc']});alive++;
  child.stderr.on('data',x=>fs.appendFileSync(path.join(config.out,'errors.log'),x));
  function feed(){if(cursor>=queue.length){child.disconnect();child.kill();return;}child.send(queue[cursor++]);}
  child.on('message',r=>{if(r.ready){feed();return;}records.push(r);fs.appendFileSync(recordsFile,JSON.stringify(r)+'\n');save();feed();});
  child.on('exit',()=>{if(!--alive){const r=save();if(!r.complete||r.errors)process.exitCode=1;}});
 }save();
}
