'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
const snapshot=path.resolve(process.argv[2]||'BetaGwent/build/audit082-20261018/rules');
const out=path.resolve(process.argv[3]||'BetaGwent/build/audit082-20261018/weather-horizon');
fs.mkdirSync(out,{recursive:true});fs.copyFileSync(__filename,path.join(out,'runner.js'));
const ctx=vm.createContext({console:{log(){}}});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.seatIndex=1;Host.random=()=>.37;
function add(g,id,zone,index,side,power,armor){const key={v:0};g.registry.Allocate(key);const c=new CBetaGwentDuelCard();c.Setup(g,key.v,id,side,zone,index);if(power!==undefined)c.power.SetCurrentPair(power,armor||0);g.registry.Put(key.v,c);g.live.push(c);return c;}
function blank(preset){const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(54,preset))throw Error('initialize');for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);
 g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.pendingRally=null;g.pendingChoice=false;g.pendingPileChoice=false;g.pendingRow=false;g.pendingIds=[];g.waiting=false;g.recordVisuals=false;
 g.match.roundNumber=3;g.match.currentPlayerId=2;g.match.roundActive=true;g.match.turnActive=true;g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 for(const side of [1,2])for(let i=0;i<6;i++)add(g,112405,8,i,side,1,0);return g;}
function row(g,lane,powers,armor=0,id=112405){return powers.map((p,i)=>add(g,id,lane,i,1,p,armor));}
const specs=[
 {id:'armour-delay',title:'Броня снимается; длинный горизонт меняет лучший ряд',setup(g){return [...row(g,1,[20,20,20,20],2),...row(g,2,[1,1,1])];}},
 {id:'armour-too-thick',title:'Броня не пробивается за доступные ходы',setup(g){return [...row(g,1,[20,20,20,20],50),...row(g,2,[20,20,20])];}},
 {id:'targets-die',title:'Слабый плотный ряд быстро заканчивается',setup(g){return [...row(g,1,[1,1,1,1]),...row(g,2,[20,20,20])];}},
 {id:'redanian-knight',title:'Рыцарь восстанавливает броню и получает силу',setup(g){return [...row(g,1,[10,10,10],2,122308),...row(g,2,[20,20])];}},
 {id:'redanian-elite',title:'Элита получает пять при потере последней брони',setup(g){return [...row(g,1,[10,10,10],4,122317),...row(g,2,[20,20])];}},
 {id:'redanian-squire',title:'Оруженосец прекращает усиливать соседей без брони',setup(g){return [add(g,112405,1,0,1,20,0),add(g,123301,1,1,1,6,2),add(g,112405,1,2,1,20,0),...row(g,2,[20,20])];}},
 {id:'hidden-front',title:'Скрытый сосед занимает физическое место, но не получает усиление',setup(g){const hidden=add(g,112405,1,0,1,10,0);hidden.AddTokens(8);return [hidden,add(g,123301,1,1,1,6,2),add(g,112405,1,2,1,20,0),...row(g,2,[20,20])].filter(c=>c!==hidden);}},
 {id:'locked-knight',title:'Заблокированный рыцарь не восстанавливает броню',setup(g){const cards=row(g,1,[10,10,10],2,122308);cards.forEach(c=>c.AddTokens(4));return [...cards,...row(g,2,[20,20])];}}
];
function run(spec,preset,forced,ticks){
 const g=blank(preset),tracked=spec.setup(g),c=add(g,152105,8,6,2);const choices=[];const original=g.MonsterRequest;
 const before=JSON.stringify(g.live.map(c=>c.Snapshot())),draws=g.random.DrawCount();
 const forecasts=[1,2].map(row=>({row,value:typeof g.weather.ForecastTokenLoss==='function'?g.weather.ForecastTokenLoss(1,row,64,ticks*10):null}));
 if(before!==JSON.stringify(g.live.map(c=>c.Snapshot()))||draws!==g.random.DrawCount())throw Error('forecast mutated state or RNG');
 g.MonsterRequest=function(source,ids,kind,min,max){if(kind===3&&source.TemplateId()===152105){if(forced===0){this.MonsterComplete(source);return;}if(forced){this.monsters.Row(source,1,forced);return;}}return original.call(this,source,ids,kind,min,max);};
 const logs=[];Host.log=s=>logs.push(s);if(!g.Play(2,c.Snapshot().instanceId,4))throw Error('Birna play');Host.log=null;
 const selected=[1,2,4].find(r=>g.WeatherToken(1,r)===64)||0;
 const states=[];
 function capture(){states.push(tracked.map(c=>{const s=c.Snapshot();return {id:c.TemplateId(),zone:s.locationMask,power:s.power.currentPower,armor:s.power.armor};}));}
 capture();
 for(let tick=1;tick<ticks;tick++){
  for(const side of [1,2]){const card=g.live.find(c=>{const s=c.Snapshot();return s.positionPlayerId===side&&s.locationMask===8;});if(!card||!g.Play(side,card.Snapshot().instanceId,4))throw Error('turn progression '+side);}
  capture();
 }
 if(g.IsFatal()||g.IsPending())throw Error('fatal/pending');
 return {selected,forecasts,states,score:tracked.reduce((sum,c)=>{const s=c.Snapshot();return sum+((s.locationMask&7)!==0?s.power.currentPower:0);},0),logs:logs.filter(s=>s.includes('event=TARGET_SELECT'))};
}
globalThis.weatherHorizon={specs,run(specId,preset,ticks){const spec=specs.find(s=>s.id===specId),baseline=run(spec,preset,0,ticks),actual=run(spec,preset,null,ticks),rows=[1,2].map(row=>({row,...run(spec,preset,row,ticks)}));
 for(const r of [actual,...rows])r.prevented=baseline.score-r.score;
 for(const r of rows){const predicted=r.forecasts.find(f=>f.row===r.row).value;if(predicted!==null&&predicted!==r.prevented)throw Error('forecast parity row='+r.row+' predicted='+predicted+' actual='+r.prevented);}
 return {id:specId,title:spec.title,preset,ticks,baseline,actual,rows,best:Math.max(...rows.map(r=>r.prevented)),pass:actual.prevented>=Math.max(...rows.map(r=>r.prevented))};},choice(specId,preset,handCount){
 const g=blank(preset),spec=specs.find(s=>s.id===specId);spec.setup(g);
 // In the final round a trailing opponent has a reason to keep playing.
 add(g,112405,4,0,2,250,0);
 for(const c of g.live)if(c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8)c.Move(2,512,0);
 for(let i=1;i<handCount;i++)add(g,112405,8,i,2,1,0);const c=add(g,152105,8,0,2);
 const ticks=g.AiRowTicks(2),values=[1,2,4].map(row=>({row,value:g.weather.ForecastTokenLoss(1,row,64,ticks)}));
 if(!g.Play(2,c.Snapshot().instanceId,4))throw Error('horizon choice play');const selected=[1,2,4].find(r=>g.WeatherToken(1,r)===64);
 if(values.find(r=>r.row===selected).value!==Math.max(...values.map(r=>r.value)))throw Error('row choice disagrees with public horizon');
 if(specId==='armour-delay'&&selected!==(handCount===1?2:1))throw Error('hand horizon must reverse armour choice');
 return {specId,preset,handCount,ticks,selected,values};}};
`,ctx,{timeout:30000});
const report={snapshot,runnerSha256:crypto.createHash('sha256').update(fs.readFileSync(__filename)).digest('hex'),nativeGameTested:false,results:[],choices:[]};
for(const spec of ctx.weatherHorizon.specs)for(const preset of [54,80])for(const ticks of [1,2,3,5]){
 ctx.job={id:spec.id,preset,ticks};try{report.results.push(vm.runInContext('weatherHorizon.run(job.id,job.preset,job.ticks)',ctx,{timeout:30000}));}catch(e){report.results.push({...ctx.job,error:String(e.stack||e)});}
}
for(const id of ['armour-delay','targets-die','redanian-knight','redanian-elite','redanian-squire'])for(const preset of [54,80])for(const handCount of [1,6]){
 ctx.choiceJob={id,preset,handCount};try{report.choices.push(vm.runInContext('weatherHorizon.choice(choiceJob.id,choiceJob.preset,choiceJob.handCount)',ctx,{timeout:30000}));}catch(e){report.choices.push({...ctx.choiceJob,error:String(e.stack||e)});}
}
fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify(report.results.map(r=>({id:r.id,preset:r.preset,ticks:r.ticks,row:r.actual?.selected,value:r.actual?.prevented,best:r.best,error:r.error?.split('\n')[0]}))));
console.log(JSON.stringify({parityCases:report.results.length,horizonChoiceCases:report.choices.length,choiceErrors:report.choices.filter(r=>r.error)}));
process.exitCode=[...report.results,...report.choices].some(r=>r.error)?1:0;
