'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js'),{context:ctx,manifest}=load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
function position(mid){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.presetTwo=95;g.leaderTemplateTwo=201580;
 const cards={v:[]};BetaGwentDuelPresetDeck(95,cards);cards.v.forEach((t,i)=>add(g,t,i<10?8:16,i<10?i:i-10,2));for(let i=0;i<8;i++)add(g,112405,8,i,1,6);
 if(mid){add(g,112405,1,0,2,6);add(g,112405,2,0,2,5);const s=add(g,123301,1,0,1,8);s.power.SetCurrentPair(8,3);const b=add(g,132201,2,0,1,5);b.cardState.timerValue=3;}
 g.archetypeAI.Initialize(g,[],95,201580);g.archetypeAI.Refresh();return g;}
function bank(g,zone){let n=0;for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId===2&&s.locationMask===zone&&s.runtimeTemplate.typeMask===4&&!BetaGwentDuelSpying(s.runtimeTemplate.templateId))n+=s.power.currentPower-s.power.basePower;}return n;}
const pool={v:[]};BetaGwentNilfPool(201580,pool);const rows=[];
for(const mid of [false,true])for(const id of pool.v){const g=position(mid),d=BetaGwentDuelDefinition(id),value=g.AiCreatedOptionValue(d,2,false),source=add(g,id,64,0,2),before=g.Score(2)-g.Score(1),hand=g.CountLocation(2,8),h=bank(g,8),deck=bank(g,16);
 const ok=g.UseLeader(2);rows.push({mid,id,title:d.title,power:d.header.power,effect:d.effect,mode:d.specialMode,value,ok,pending:g.IsPending(),fatal:g.IsFatal(),boardGain:g.Score(2)-g.Score(1)-before,handCountDelta:g.CountLocation(2,8)-hand,handBoost:bank(g,8)-h,deckBoost:bank(g,16)-deck});}
globalThis.report={rows,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...ctx.report};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));
