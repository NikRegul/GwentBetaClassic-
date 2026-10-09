// Universal invariants exercised with a real card from each of the 46 authored decks.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),output=process.argv[3];
const pool=JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8')).presets;
const context=vm.createContext({console,pool});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
const coverage=[];let checks=0;
function check(value,name){if(!value)throw Error(name);checks++;}
function add(g,t,side,zone,index=0,power){const id={v:0};g.registry.Allocate(id);const c=new CBetaGwentDuelCard();c.Setup(g,id.v,t,side,zone,index);
 if(power!==undefined){c.cardState.power.currentPower=power;c.power.currentPower=power;}
 g.registry.Put(id.v,c);g.live.push(c);return c;}
function fixture(p){const g=new CBetaGwentDuelSession();check(g.InitializeWithPresets(p,p),'initialize '+p);
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;g.weatherProfile=false;
 g.match.currentPlayerId=2;g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=1;g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 g.recordVisuals=false;return g;}
for(const preset of pool){const ids={v:[]};BetaGwentDuelPresetDeck(preset,ids);
 const ordinary=ids.v.find(t=>{const d=BetaGwentDuelDefinition(t);return d.header.typeMask===4&&d.header.tierMask===2&&!BetaGwentDuelSpying(t)&&!([15,23].includes(d.effect))&&!gAdj(t)&&!d.deathwishDamage;});
 function gAdj(t){return [152309,152109,123301,132308].includes(t);}
 check(ordinary,'ordinary real roster card '+preset);
 const c={preset,profile:BetaGwentAIPresetProfile(preset),weather:false,adjacency:false,chase:false,fullPlay:false,spawnOrSummon:false,discardSetup:'not_present',engineProtection:'not_present'};
 {const g=fixture(preset);g.weather.hazards[3]=1;g.weather.hazards[4]=1;
  const d=BetaGwentDuelDefinition(ordinary);check(g.BestCardRow(2,d)===4,'safe row '+preset);c.weather=true;}
 {const g=fixture(preset),squire=add(g,123301,2,2);squire.power.armor=5;squire.cardState.power.armor=5;add(g,112101,2,2,1);
  const unit=add(g,ordinary,2,8),row=g.BestCardRow(2,unit.Definition());
  check(row===2&&g.AiAdjacencyIndex(unit,row)===0,'outside adjacent buff slot '+preset);c.adjacency=true;}
 {const g=fixture(preset);const unit=add(g,ordinary,2,8);for(const row of [1,2,4])add(g,112101,1,row,0,500).AddTokens(256);g.match.playerOne.hasPassed=true;
  const hand=g.CountLocation(2,8);const ok=g.OpponentStep();check(ok&&(g.match.Snapshot().playerTwo.hasPassed||g.IsWaitingRound())&&g.CountLocation(2,8)===hand,'unreachable optional chase saves card '+preset);c.chase=true;}
 {const g=fixture(preset),card=add(g,ordinary,2,8);ids.v.filter(t=>t!==ordinary).forEach((t,i)=>add(g,t,2,16,i));
  add(g,112101,1,1,0,8);add(g,112101,2,2,0);add(g,112101,2,2,1);
  const before=JSON.stringify(g.live.map(x=>x.Snapshot())),draws=g.random.DrawCount(),exact=g.AiExactTempo(card);
  check(exact!==-2147483647&&!g.fatal,'complete simulated play '+preset);
  check(before===JSON.stringify(g.live.map(x=>x.Snapshot()))&&draws===g.random.DrawCount(),'lookahead does not alter live state/RNG '+preset);c.fullPlay=true;}
 const summon=ids.v.find(t=>{const d=BetaGwentDuelDefinition(t);return d.deploySummonTemplate||d.deploySpawnCount;});
 if(summon){const g=fixture(preset),source=add(g,summon,2,8);let removed=false;
  ids.v.forEach((t,i)=>{if(t===summon&&!removed){removed=true;return;}add(g,t,2,16,i);});
  const gain=g.AiSimPlay(source.Snapshot().instanceId);
  check(gain!==-2147483647&&!g.fatal,'resolved play including summons '+preset);c.spawnOrSummon=true;}
 if(ids.v.some(t=>[200177,152316].includes(t))){const g=fixture(preset),target=add(g,ids.v.includes(200177)?200177:152316,2,16);g.archetypeAI.Refresh();
  check(g.archetypeAI.DiscardValue(target)>0,'real self-return discard preparation '+preset);c.discardSetup=true;}
 if(ids.v.includes(132201)&&ids.v.some(t=>BetaGwentDuelDefinition(t).effect===23||BetaGwentDuelDefinition(t).specialMode===11)){
  const g=fixture(preset),engine=add(g,132201,2,1),food=add(g,132305,2,1,1),source=add(g,201743,2,64);engine.monsterTimer=4;
  check(g.AiAbilityChoiceValue(source,engine,0)>g.AiAbilityChoiceValue(source,food,0),'charged consumer engine preserved '+preset);c.engineProtection=true;}
 const leader=BetaGwentDuelDefinition(BetaGwentDuelPreset(preset).leaderTemplateId);
 check(BetaGwentAILeaderUseful(leader.header.templateId,1,5,leader.header.power,leader.header.power,0,false,100)===false,'body-only leader reserve '+preset);c.leaderTiming=true;
 coverage.push(c);console.log('PASS profile',c.profile,'preset',preset);}
{const g=fixture(54);check(g.ActionPreviewGeometry(BetaGwentDuelDefinition(113311)).startsWith('1,1,'),'Thunder three-card public shape');
 check(BetaGwentAITrainingWeight(61,2)===-2,'default host uses actual exported trained weights');
 const trace=[];Host.log=s=>trace.push(s);const a=add(g,112101,2,8),b=add(g,122104,2,8,1);add(g,112101,1,8);
 check(g.OpponentStep(),'diagnostic decision executes');
 check(trace.some(s=>s.includes('event=BEGIN'))&&trace.filter(s=>s.includes('event=OPTION')).length===2&&trace.some(s=>s.includes('event=SELECT'))&&trace.filter(s=>s.includes('event=ROW')).length===3,'one linked decision records alternatives, selection and rows');
 const n=trace.length;g.aiSimulating=true;g.AiExplain('TEST','reason=simulation');check(trace.length===n,'lookahead diagnostics suppressed');Host.log=null;}
globalThis.result119={stage:119,checks,profiles:coverage.length,actualWitcherScript:true,coverage};
`,context,{filename:'scenarios119.bundle.js',timeout:240000});
if(output)fs.writeFileSync(output,JSON.stringify(context.result119,null,2));
console.log(JSON.stringify({stage:119,checks:context.result119.checks,profiles:context.result119.profiles}));
