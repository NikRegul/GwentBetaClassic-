// All-composition extension of compare_ai.js; original runner stays unchanged.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto'),zlib=require('zlib');
const [folder,...args]=process.argv.slice(2);
if(!folder)throw Error('Usage: compare_all093c.js output-folder [--resume] [--max-games N]');
const out=path.resolve(folder),resume=args.includes('--resume');
const limitAt=args.indexOf('--max-games'),maxGames=limitAt<0?Infinity:Number(args[limitAt+1]);
if(!(maxGames>0)||!Number.isInteger(maxGames)&&maxGames!==Infinity)throw Error('Invalid max-games');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const config=read(path.join(out,'run.json')),candidate=path.join(out,'candidate'),baseline=path.join(out,'baseline');
const proof=read(path.join(baseline,'comparison.json')),manifest=read(path.join(candidate,'manifest.json'));
const pool=config.pool,cycles=config.cycles,seed0=config.seed;
if(!Number.isInteger(cycles)||cycles<1||!Number.isInteger(seed0)||!Array.isArray(pool)||pool.length!==92||new Set(pool).size!==92||!pool.every(Number.isInteger))throw Error('Invalid92-composition experiment');
const blockStart=config.blockStart??0,blockCount=config.blockCount??pool.length;
if(!Number.isInteger(blockStart)||!Number.isInteger(blockCount)||blockStart<0||blockCount<1||blockStart+blockCount>pool.length)throw Error('Invalid experiment block slice');
const catalogue=path.join(candidate,'sources/BetaGwent/development/scripts/game/betagwent/duelCatalog.ws');
if(sha(catalogue)!==proof.sameDeckCatalogue||sha(path.join(baseline,'rules.js'))!==proof.baselineRules)throw Error('Baseline proof changed');
for(const name of ['runtime.js','harness.js'])if(sha(path.join(candidate,name))!==sha(path.join(baseline,name)))throw Error('Host adapters differ');
const bridgeFile=path.join(__dirname,'comparison_bridge119.js');
const inputs={};
for(const dir of [candidate,baseline])for(const name of ['rules.js','runtime.js','harness.js','tunes.json'])inputs[path.relative(out,path.join(dir,name))]=sha(path.join(dir,name));
for(const name of ['comparison_bridge119.js','compare_all093c.js','replay119.js','profiles.json','run.json','candidate/manifest.json','baseline/comparison.json'])inputs[name]=sha(path.join(out,name));
const reportPath=path.join(out,'report.json');
if(fs.existsSync(reportPath)&&!resume)throw Error('Use --resume or a new output directory');
if(resume&&!fs.existsSync(reportPath))throw Error('No checkpoint to resume');
const report=resume?read(reportPath):{
 schema:2,protocol:'shared current battle mechanics + decks + raw deal + RNG; independent mulligans; both policies/decks/seats'+(config.randomMatchups?'; shuffled deranged opponent permutations each cycle':''),
 candidate,baseline,candidateLabel:config.candidateLabel,baselineLabel:config.baselineLabel,
 candidateRules:sha(path.join(candidate,'rules.js')),baselineRules:proof.baselineRules,catalogue:proof.sameDeckCatalogue,
 inputs,seed:seed0,cycles,blockStart,blockCount,plannedGames:cycles*blockCount*4,completedGames:0,games:[],seconds:0,
 sharedBattleMechanics:proof.sharedBattleMechanics,trainedWeightsIncluded:true,sessionPolicyMethods:proof.sessionPolicyMethods
};
if(resume&&JSON.stringify(report.inputs)!==JSON.stringify(inputs))throw Error('Frozen experiment files changed; resume refused');
fs.mkdirSync(path.join(out,'matches'),{recursive:true});fs.mkdirSync(path.join(out,'errors'),{recursive:true});
function host(dir){let bridge;const source=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(dir,n),'utf8')).join('\n')+'\n'+require(bridgeFile);
 if(config.fastHost)bridge=new Function(source+'\nreturn globalThis.bridge;')();
 else {const context=vm.createContext({console});vm.runInContext(source,context);bridge=context.bridge;}
 bridge.setTunes(read(path.join(dir,'tunes.json')));
 const strength=dir===candidate?config.candidateStrength:config.baselineStrength;
 if(strength!==undefined)bridge.setStrength(strength);
 if(config.simDamp!==undefined)bridge.setSimDamp(config.simDamp);
 return bridge;}
const fresh=host(candidate),old=host(baseline),profiles=read(path.join(out,'profiles.json')).profiles;
let logs=[],decisions=[],rng=seed0>>>0||1;
function rnd(){rng^=rng<<13;rng>>>=0;rng^=rng>>>17;rng>>>=0;rng^=rng<<5;rng>>>=0;return rng;}
fresh.setLog(s=>logs.push({version:'candidate',text:s}));old.setLog(s=>logs.push({version:'baseline',text:s}));
function play(initial,newSeat,mirrored){let h=fresh,steps=0,lastState=initial;
 try{h.load(initial);if(mirrored)h.mirror();const first=newSeat===1?fresh:old;
  if(first!==h){first.load(h.dump());h=first;}lastState=h.dump();h.initialMulligan();
  for(;steps<500;steps++){
   let s=h.view();if(s.fatal)throw Error(s.message);
   if(s.winner){let winner=s.winner;if(s.reversed)winner=((winner&1)<<1)|((winner&2)>>1);return {winner,steps};}
   if(!s.mulligan&&!s.pending&&!s.waiting&&s.current===1){h.swap();s=h.view();}
   const chooser=s.mulligan?1-s.actor:s.actor,target=chooser===newSeat?fresh:old;
   if(target!==h){target.load(h.dump());h=target;}
   lastState=h.dump();const before=h.view(),logStart=logs.length,decisionStart=performance.now();h.step();
   decisions.push({step:steps,version:target===fresh?'candidate':'baseline',before,after:h.view(),milliseconds:performance.now()-decisionStart,logStart,logEnd:logs.length});
  }throw Error('decision limit');
 }catch(e){return {winner:0,steps,error:String(e.stack||e),lastState};}
}
function atomic(name,data){
 const target=path.join(out,name);fs.writeFileSync(target+'.tmp',data);
 for(let attempt=0;;attempt++)try{fs.renameSync(target+'.tmp',target);return;}
 catch(e){if(!['EPERM','EBUSY','EACCES'].includes(e.code)||attempt>=29)throw e;Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,25*(attempt+1));}
}
const csv=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
const pct=x=>x==null?'—':(100*x).toFixed(2)+'%';
function save(){
 report.wins=0;report.losses=0;report.draws=0;report.errors=0;report.blocks=[];report.perDeck={};report.perFirstSeat={};
 for(const id of pool){const p=profiles.find(p=>p.presetId===id);report.perDeck[id]={profile:p?.id,title:p?.title||String(id),wins:0,losses:0,draws:0,errors:0,steps:0};}
 const groups=new Map();
 for(const g of report.games){const d=report.perDeck[g.candidateDeck];const key=String(g.newSeat);const seat=report.perFirstSeat[key]||(report.perFirstSeat[key]={wins:0,losses:0,draws:0,errors:0});
  const result=g.error?'errors':g.winner===3?'draws':g.winner===g.newSeat+1?'wins':'losses';
  report[result]++;d[result]++;seat[result]++;d.steps+=g.steps;
  const block=groups.get(g.block)||[];block.push(g);groups.set(g.block,block);
 }
 for(const games of groups.values())if(games.length===4&&!games.some(g=>g.error))report.blocks.push(games.reduce((s,g)=>s+(g.winner===3?.5:g.winner===g.newSeat+1?1:0),0)/4);
 const n=report.blocks.length;
 report.mean=n?report.blocks.reduce((s,x)=>s+x,0)/n:null;
 report.se=n>1?Math.sqrt(report.blocks.reduce((s,x)=>s+(x-report.mean)**2,0)/(n-1)/n):null;
 report.lower99=report.se==null?null:Math.max(0,report.mean-2.576*report.se);
 report.upper99=report.se==null?null:Math.min(1,report.mean+2.576*report.se);
 const valid=report.wins+report.losses+report.draws;
 report.scoreRate=valid?(report.wins+.5*report.draws)/valid:null;
 report.completedGames=report.games.length;report.complete=report.completedGames===report.plannedGames;
 report.confirmedBetter=report.complete&&report.errors===0&&n>=46&&report.lower99>.5;
 report.matchupPairs=new Set(report.games.map(g=>[g.left,g.right].sort((a,b)=>a-b).join('-'))).size;
 atomic('games.jsonl',report.games.map(g=>JSON.stringify(g)).join('\n')+'\n');
 const rows=pool.map(id=>{const d=report.perDeck[id],v=d.wins+d.losses+d.draws,total=v+d.errors;d.scoreRate=v?(d.wins+.5*d.draws)/v:null;
  return [id,d.profile,d.title,total,d.wins,d.losses,d.draws,d.errors,d.scoreRate==null?'':d.scoreRate.toFixed(6),total?(d.steps/total).toFixed(2):''];});
 atomic('report.json',JSON.stringify(report,null,2));
 atomic('archetypes.csv','\uFEFF'+['preset,profile,title,games,wins,losses,draws,errors,score_rate,mean_steps',...rows.map(row=>row.map(csv).join(','))].join('\r\n'));
 const md=pool.map(id=>{const d=report.perDeck[id];return `| ${id} | ${d.title.replace(/\|/g,'/')} | ${d.wins} | ${d.losses} | ${d.draws} | ${d.errors} | ${pct(d.scoreRate)} |`;}).join('\n');
 atomic('REPORT_RU.md',`# Сравнение ИИ ${report.candidateLabel} и ${report.baselineLabel}\n\n`+
 `Завершено: ${report.completedGames} / ${report.plannedGames}. Ошибок: ${report.errors}. Время симуляции: ${report.seconds.toFixed(1)} с.\n\n`+
 `Новый ИИ: ${report.wins} побед, ${report.losses} поражений, ${report.draws} ничьих. Доля очков (ничья = 0,5): ${pct(report.scoreRate)}.\n\n`+
 `Полные группы из четырёх партий: ${n}. Парное среднее: ${pct(report.mean)}. Приближённый 99% интервал: ${pct(report.lower99)} – ${pct(report.upper99)}. Критерий улучшения выполнен: ${report.confirmedBetter}.\n\n`+
 `Уникальных пар разных колод: ${report.matchupPairs} / ${pool.length*(pool.length-1)/2}. Все ${pool.length} составов участвуют в каждом полном цикле. Обе версии играют обе колоды с обоими порядками хода; начальная раздача и RNG общие, обмен выбирается независимо. Правила карт и не относящиеся к решениям методы сессии общие.\n\n`+
 `Это проверка решений через перенесённые правила WitcherScript, не измерение FPS или качества игры против человека. Интервал рассчитан по группам из четырёх партий нормальным приближением. Неполный прогон или прогон с ошибками не подтверждает превосходство.\n\n`+
 `| Архетип | Название | Победы нового | Поражения нового | Ничьи | Ошибки | Доля очков |\n|---|---|---:|---:|---:|---:|---:|\n${md}\n`);
 // A portable English summary is useful when sharing benchmark results.
 atomic('REPORT.md',`# AI ${report.candidateLabel} vs ${report.baselineLabel}\n\nCompleted ${report.completedGames}/${report.plannedGames}; errors ${report.errors}.\nCandidate W/L/D: ${report.wins}/${report.losses}/${report.draws}; score rate ${pct(report.scoreRate)}.\nPaired mean ${pct(report.mean)}; approximate 99% interval ${pct(report.lower99)}–${pct(report.upper99)}; confirmed better: ${report.confirmedBetter}.\n\nShared battle mechanics, decks, raw deals and RNG; independent mulligans; four games per block. This evaluates the WS simulation host, not retail performance or strength against humans. Incomplete/errorful runs are not strength verdicts.\n`);
}
const started=Date.now(),priorSeconds=report.seconds;let executed=0,stop=false;
save();
for(let cycle=0;cycle<cycles&&!stop;cycle++){
 let opponents=pool.slice();
 if(config.randomMatchups){
  let valid=false;
  for(let attempt=0;attempt<1000&&!valid;attempt++){
   opponents=pool.slice();for(let j=opponents.length-1;j>0;j--){const k=rnd()%(j+1);[opponents[j],opponents[k]]=[opponents[k],opponents[j]];}
   valid=opponents.every((id,j)=>id!==pool[j]);
  }
  if(!valid)throw Error('Could not generate random non-self matchups');
 }
 for(let i=0;i<pool.length&&!stop;i++){
 const seed=rnd(); // Draw even for skipped blocks: partitions preserve the full-run deals.
 if(i<blockStart||i>=blockStart+blockCount)continue;
 const a=pool[i],b=config.randomMatchups?opponents[i]:pool[(i+1+((cycle+(config.matchupOffset||0))%(pool.length-1)))%pool.length],block=cycle*blockCount+i-blockStart;
 const schedule=[[0,false],[1,true],[1,false],[0,true]];
 let initial=null;
 for(let seatGame=0;seatGame<4;seatGame++){
  const index=block*4+seatGame,id=`game-${String(index+1).padStart(6,'0')}`;
  if(index<report.games.length){const g=report.games[index];if(g.id!==id||g.seed!==seed)throw Error('Checkpoint schedule mismatch');continue;}
  if(executed>=maxGames){stop=true;break;}
  logs=[];decisions=[];
  if(initial===null)initial=fresh.initialize(a,b,seed);
  logs=[];const [newSeat,mirror]=schedule[seatGame],r=play(initial,newSeat,mirror);
  const record={id,left:mirror?b:a,right:mirror?a:b,newSeat,mirror,seed,cycle,block,candidateDeck:newSeat===(mirror?1:0)?a:b,...r};
  record.policyMetrics={};for(const version of ['candidate','baseline']){
   const choices=decisions.filter(d=>d.version===version&&!d.before.mulligan&&!d.before.pending&&!d.before.waiting),events={};
   for(const log of logs)if(log.version===version){const m=/event=([A-Z_]+)/.exec(log.text);if(m)events[m[1]]=(events[m[1]]||0)+1;}
   record.policyMetrics[version]={decisions:choices.length,milliseconds:choices.reduce((s,d)=>s+d.milliseconds,0),peakMilliseconds:Math.max(0,...choices.map(d=>d.milliseconds)),events};
  }
  if(r.error || !config.traceEvery || index%config.traceEvery===0){
   const bytes=zlib.gzipSync(JSON.stringify({schema:1,record,initial,decisions,logs}));
   fs.writeFileSync(path.join(out,'matches',id+'.json.gz'),bytes);
   if(r.error)fs.writeFileSync(path.join(out,'errors',id+'.json.gz'),bytes);
  }
  delete record.lastState;report.games.push(record);executed++;report.seconds=priorSeconds+(Date.now()-started)/1000;save();
  console.log(`${report.completedGames}/${report.plannedGames}: new ${report.wins}, old ${report.losses}, draws ${report.draws}, errors ${report.errors}`);
 }
}
}
console.log(JSON.stringify({complete:report.complete,wins:report.wins,losses:report.losses,draws:report.draws,errors:report.errors,scoreRate:report.scoreRate,seconds:report.seconds}));
if(report.errors)process.exitCode=1;
