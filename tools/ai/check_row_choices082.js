'use strict';
// Compare the real AI row decision with explicitly selected legal rows on 0.8.2.
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..'),base=path.join(root,'BetaGwent/build/audit082-20261018');
const args=process.argv.slice(2),option=(name,fallback)=>args.includes(name)?args[args.indexOf(name)+1]:fallback;
const snapshot=path.resolve(option('--snapshot',path.join(base,'rules'))),out=path.resolve(option('--output',path.join(base,'row-choice-audit')));
fs.mkdirSync(out,{recursive:true});fs.copyFileSync(__filename,path.join(out,'runner.js'));
const manifest=JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8'));
if(manifest.schema===2){
 for(const [name,digest] of Object.entries(manifest.snapshotFiles)){
  if(crypto.createHash('sha256').update(fs.readFileSync(path.join(snapshot,name))).digest('hex')!==digest)throw Error('Frozen snapshot changed: '+name);
 }
}else if(!/\/release(?:082|090|091)-[^/]+$/.test(manifest.source?.replaceAll('\\','/')))throw Error('Expected frozen release sources');
const ctx=vm.createContext({console:{log(){}}});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.seatIndex=1;Host.random=()=>.37;
function add(g,id,zone,index=0,side=2,power,armor=0){const key={v:0};g.registry.Allocate(key);const c=new CBetaGwentDuelCard();c.Setup(g,key.v,id,side,zone,index);if(power!==undefined)c.power.SetCurrentPair(power,armor);g.registry.Put(key.v,c);g.live.push(c);return c;}
function blank(preset){
 const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(54,preset))throw Error('initialize');
 for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);
 g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.pendingRally=null;g.pendingChoice=false;g.pendingPileChoice=false;g.pendingRow=false;g.pendingIds=[];g.waiting=false;
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.match.currentPlayerId=2;g.match.roundActive=true;g.match.turnActive=true;g.recordVisuals=false;g.aiSimDamp=40;
 for(const side of [1,2])for(let i=0;i<4;i++)add(g,112405,8,i,side);
 return g;
}
function row(g,side,lane,powers,armor=0){return powers.map((p,i)=>add(g,112405,lane,i,side,p,armor));}
const specifications=[
 {id:'igni',card:112102,title:'Игни: 20 против 30',options:[[1,1],[1,2],[1,4]],metric:'lead',setup(g){row(g,1,1,[20,5]);row(g,1,2,[30,1]);}},
 {id:'igni-threshold',card:112102,title:'Игни: три слабых ниже порога против одного допустимого',options:[[1,1],[1,2],[1,4]],metric:'lead',setup(g){row(g,1,1,[8,8,8]);row(g,1,2,[30]);}},
 {id:'yrden-enemy',card:201523,title:'Ирден: слабые усиления против одного огромного',options:[[1,1],[1,2],[1,4],[2,1],[2,2],[2,4]],metric:'lead',setup(g){row(g,1,1,[12,12,12]);row(g,1,2,[100]);}},
 {id:'yrden-own',card:201523,title:'Ирден: восстановить своих вместо исцеления врага',options:[[1,1],[1,2],[1,4],[2,1],[2,2],[2,4]],metric:'lead',setup(g){row(g,1,1,[5]);row(g,2,1,[1,1,1]);}},
 {id:'birna-armour',card:152105,title:'Бирна: плотный бронированный ряд против трёх уязвимых',options:[[1,1],[1,2],[1,4]],metric:'lead',setup(g){row(g,1,1,[20,20,20,20],50);row(g,1,2,[20,20,20]);}},
 {id:'rot-full',card:162302,title:'Разносчик заразы: заполненный ряд против свободного места',options:[[1,1],[1,2],[1,4]],metric:'created',spawn:162402,setup(g){row(g,1,1,Array(9).fill(11));row(g,1,2,[11,11]);}},
 {id:'trap-full',card:142304,title:'Ловчий: заполненный ряд против свободного места',options:[[1,1],[1,2],[1,4]],metric:'created',spawn:143301,setup(g){row(g,1,1,Array(9).fill(11));row(g,1,2,[11,11]);}},
 {id:'nivellen-weather',card:200089,title:'Нивеллен: не выводить врага из собственной погоды',options:[[1,1],[1,2],[1,4],[2,1],[2,2],[2,4]],metric:'lead',setup(g){row(g,1,1,[20,20,20,20]);row(g,1,2,[20,20,20]);g.weather.ApplyHazard(1,1,64);}},
 {id:'troll-overwrite',card:201700,title:'Тролль: перенос не должен стирать полезную погоду',options:[[[1,1],[1,2]],[[1,1],[1,4]],[[1,2],[1,1]],[[1,2],[1,4]]],metric:'lead',multi:true,setup(g){row(g,1,1,[20,20,20]);row(g,1,2,[20,20]);row(g,1,4,[20]);g.weather.ApplyHazard(1,1,2);g.weather.ApplyHazard(1,2,64);}}
];
function position(preset,spec,forced){
 const g=blank(preset);spec.setup(g);const c=add(g,spec.card,8,4);
 let step=0;const selected=[],logs=[];
 const original=g.MonsterRequest;
 g.MonsterRequest=function(source,ids,kind,min,max){
  if(kind!==3||source.TemplateId()!==spec.card)return original.call(this,source,ids,kind,min,max);
  if(!forced)return original.call(this,source,ids,kind,min,max);
  const choice=spec.multi?forced[step++]:forced;
  if(!choice||!ids.includes(choice[1]))throw Error('Illegal authored row');
  selected.push(choice);this.monsters.Row(source,choice[0],choice[1]);
 };
 const before=g.Score(2)-g.Score(1);Host.log=s=>logs.push(s);let ok;
 try{ok=g.Play(2,c.Snapshot().instanceId,4);}finally{Host.log=null;}
 if(!ok||g.IsFatal()||g.IsPending())throw Error('unfinished play: '+g.GetMessage());
 const cards=g.live.map(c=>c.Snapshot()).filter(s=>(s.locationMask&7)!==0);
 return {forced,selected:forced?selected:logs.filter(s=>s.includes('event=TARGET_SELECT')).map(s=>({row:+s.match(/target=(\d+)/)[1]})),
  gain:g.Score(2)-g.Score(1)-before,scores:[g.Score(1),g.Score(2)],created:spec.spawn?cards.filter(s=>s.runtimeTemplate.templateId===spec.spawn).length:null,
  weather:[1,2,4].map(r=>g.WeatherToken(1,r)),logs:logs.filter(s=>/event=(TARGET_OPTION|TARGET_SELECT)|DUEL_WEATHER_TICK/.test(s))};
}
globalThis.rowAudit={specifications,run(preset,id){
 const spec=specifications.find(s=>s.id===id),actual=position(preset,spec,null),alternatives=spec.options.map(choice=>position(preset,spec,choice));
 const value=o=>spec.metric==='created'?o.created:o.gain;
 const best=Math.max(...alternatives.map(value));
 return {preset,id,title:spec.title,card:spec.card,metric:spec.metric,pass:value(actual)>=best,actual,best,alternatives};
}};
`,ctx,{timeout:30000});
const report={version:'0.8.2',source:manifest.source,fingerprint:manifest.fingerprint,runnerSha256:crypto.createHash('sha256').update(fs.readFileSync(__filename)).digest('hex'),
 nativeGameTested:false,notes:['Explicit rows use real ability handlers; AI still places the source normally.','Lead is actual resolved material through the first enemy turn start, not a full strategic forecast.','A synthetic hand probes each unchanged archetype; it does not claim the shipping deck contains every test card.'],results:[]};
const requested=args.filter(x=>/^\d+$/.test(x)).map(Number),pool=requested.length?requested:manifest.presets;
for(const preset of pool){
 for(const spec of ctx.rowAudit.specifications){
  ctx.job={preset,id:spec.id};try{report.results.push(vm.runInContext('rowAudit.run(job.preset,job.id)',ctx,{timeout:30000}));}
  catch(e){report.results.push({preset,id:spec.id,title:spec.title,error:String(e.stack||e)});}
 }
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({preset,failures:report.results.filter(x=>x.preset===preset&&!x.pass).map(x=>x.id)}));
}
const summary=ctx.rowAudit.specifications.map(s=>({id:s.id,title:s.title,total:report.results.filter(x=>x.id===s.id).length,failed:report.results.filter(x=>x.id===s.id&&x.pass===false).length,errors:report.results.filter(x=>x.id===s.id&&x.error).length}));
report.summary=summary;fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(summary));
process.exitCode=report.results.some(x=>!x.pass)?1:0;
