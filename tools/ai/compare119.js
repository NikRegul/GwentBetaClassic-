// Same real WS effects, raw deal and RNG; both policies play both decks in both seats.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto'),zlib=require('zlib');
const [candidateArg,baselineArg,outputArg,cyclesArg='1',seedArg='119']=process.argv.slice(2);
if(!candidateArg||!baselineArg||!outputArg)throw Error('candidate baseline output cycles seed');
const candidate=path.resolve(candidateArg),baseline=path.resolve(baselineArg),out=path.resolve(outputArg);
const cycles=Number(cyclesArg),seed0=Number(seedArg);
if(!Number.isInteger(cycles)||cycles<1||!Number.isSafeInteger(seed0))throw Error('Invalid cycles/seed');
if(fs.existsSync(path.join(out,'report.json')))throw Error('Use a new output directory; previous comparisons are immutable');
fs.mkdirSync(path.join(out,'matches'),{recursive:true});fs.mkdirSync(path.join(out,'errors'),{recursive:true});
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const proof=JSON.parse(fs.readFileSync(path.join(baseline,'comparison.json'),'utf8'));
const catalog=path.join(candidate,'sources/BetaGwent/development/scripts/game/betagwent/duelCatalog.ws');
if(sha(catalog)!==proof.sameDeckCatalogue||sha(path.join(baseline,'rules.js'))!==proof.baselineRules)throw Error('Comparison catalogue/proof mismatch');
function host(folder){const c=vm.createContext({console});
 vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(folder,n),'utf8')).join('\n')+'\n'+require('./comparison_bridge119'),c);
 c.bridge.setTunes(JSON.parse(fs.readFileSync(path.join(folder,'tunes.json'),'utf8')));return c.bridge;}
const fresh=host(candidate),old=host(baseline),pool=JSON.parse(fs.readFileSync(path.join(candidate,'manifest.json'),'utf8')).presets;
if(pool.length!==46||new Set(pool).size!==46)throw Error('Exactly 46 archetypes required');
const profiles=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../data/beta924/ai/researched115.json'),'utf8')).profiles;
const report={schema:1,protocol:'shared raw deal + RNG; independent mulligans; four games per pair: both versions/decks/seats',candidate,baseline,seed:seed0,cycles,
 candidateRules:sha(path.join(candidate,'rules.js')),baselineRules:proof.baselineRules,catalogue:proof.sameDeckCatalogue,trainedWeightsIncluded:true,
 plannedGames:cycles*46*4,wins:0,losses:0,draws:0,errors:0,blocks:[],perDeck:{},games:[]};
for(const id of pool){const p=profiles.find(p=>p.presetId===id);report.perDeck[id]={profile:p&&p.id,title:p&&p.title,wins:0,losses:0,draws:0,errors:0};}
let rng=seed0>>>0||1,logs=[],decisions=[];
function rnd(){rng^=rng<<13;rng>>>=0;rng^=rng>>>17;rng>>>=0;rng^=rng<<5;rng>>>=0;return rng;}
fresh.setLog(s=>logs.push({version:'candidate',text:s}));old.setLog(s=>logs.push({version:'baseline',text:s}));
function play(initial,newSeat,mirrored){let h=fresh,steps=0,lastState=initial;
 h.load(initial);if(mirrored)h.mirror();let right=newSeat===1?fresh:old;
 if(right!==h){right.load(h.dump());h=right;}
 try{h.initialMulligan();for(;steps<500;steps++){
   let s=h.view();if(s.fatal)throw Error(s.message);
   if(s.winner){let w=s.winner;if(s.reversed)w=((w&1)<<1)|((w&2)>>1);return {winner:w,steps};}
   if(!s.mulligan&&!s.pending&&!s.waiting&&s.current===1){h.swap();s=h.view();}
   const chooser=s.mulligan?1-s.actor:s.actor,target=chooser===newSeat?fresh:old;
   if(target!==h){target.load(h.dump());h=target;}
   lastState=h.dump();const before=h.view(),logStart=logs.length;h.step();
   decisions.push({step:steps,version:target===fresh?'candidate':'baseline',before,after:h.view(),logStart,logEnd:logs.length});
  }throw Error('decision limit');
 }catch(e){return {winner:0,steps,error:String(e.stack||e),lastState};}}
function save(){const n=report.blocks.length;
 report.mean=n?report.blocks.reduce((a,b)=>a+b,0)/n:null;
 report.se=n>1?Math.sqrt(report.blocks.reduce((a,b)=>a+(b-report.mean)**2,0)/(n-1)/n):null;
 report.lower99=report.se===null?null:report.mean-2.576*report.se;
 report.confirmedBetter=report.errors===0&&report.completedGames===report.plannedGames&&n>=46&&report.lower99>.5;
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));
 fs.writeFileSync(path.join(out,'archetypes.csv'),'preset,profile,title,wins,losses,draws,errors,score_rate\n'+pool.map(id=>{
  const d=report.perDeck[id],n=d.wins+d.losses+d.draws;return [id,d.profile,JSON.stringify(d.title),d.wins,d.losses,d.draws,d.errors,n?(d.wins+.5*d.draws)/n:''].join(',');}).join('\n'));
 const rows=pool.map(id=>{const d=report.perDeck[id];return `| ${id} | ${d.title} | ${d.wins} | ${d.losses} | ${d.draws} | ${d.errors} |`;});
 fs.writeFileSync(path.join(out,'REPORT.md'),`# AI comparison\n\nGames: ${report.completedGames||0}/${report.plannedGames}; errors: ${report.errors}.\n\nCandidate: ${report.wins} wins, ${report.losses} losses, ${report.draws} draws.\n\nPaired mean: ${report.mean}; lower 99% normal approximation: ${report.lower99}. Confirmed better: ${report.confirmedBetter}.\n\nThis tests the frozen WS host, not visual/runtime performance in retail. A result with errors is not a strength verdict.\n\n| Preset | Archetype | W | L | D | Errors |\n|---|---|---|---|---|---|\n${rows.join('\n')}\n`);
}
const started=Date.now();let game=0;save();
for(let cycle=0;cycle<cycles;cycle++)for(let i=0;i<46;i++){
 const a=pool[i],b=pool[(i+1+(cycle%45))%46],seed=rnd();logs=[];const initial=fresh.initialize(a,b,seed);let block=0,valid=0;
 for(const [newSeat,mirror] of [[0,false],[1,true],[1,false],[0,true]]){
  logs=[];decisions=[];const r=play(initial,newSeat,mirror),id=`game-${String(++game).padStart(6,'0')}`;
  const deck=newSeat===(mirror?1:0)?a:b,d=report.perDeck[deck],record={id,left:mirror?b:a,right:mirror?a:b,newSeat,mirror,seed,cycle,...r};
  const replay={schema:1,record,initial,decisions,logs};
  // Every match is replayable; failures additionally preserve the exact pre-error state.
  const replayBytes=zlib.gzipSync(JSON.stringify(replay));fs.writeFileSync(path.join(out,'matches',id+'.json.gz'),replayBytes);
  if(r.error){report.errors++;d.errors++;fs.writeFileSync(path.join(out,'errors',id+'.json.gz'),replayBytes);}
  else{valid++;if(r.winner===3){report.draws++;d.draws++;block+=.5;}else if(r.winner===newSeat+1){report.wins++;d.wins++;block++;}else{report.losses++;d.losses++;}}
  delete record.lastState;fs.appendFileSync(path.join(out,'games.jsonl'),JSON.stringify(record)+'\n');report.games.push(record);report.completedGames=game;
 }
 if(valid===4)report.blocks.push(block/4);report.seconds=(Date.now()-started)/1000;save();
 console.log(`${game}/${report.plannedGames}: candidate ${report.wins}, baseline ${report.losses}, draws ${report.draws}, errors ${report.errors}`);
}
if(report.errors)process.exitCode=1;
