// Regressions for confirmed findings from the external review, on real WS.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
for(const id of [200162,200163,200164])check(BetaGwentDuelDefinition(id).header.templateId===id,'definition lookup already correct '+id);
for(const index of [-3,-4,0,1,50]){
 const g=fixture(),first=add(g,112101,1,0,2),second=add(g,112101,1,1,2),summoned=add(g,112101,16,0,2);
 const dest=first.Snapshot();dest.locationIndex=index;
 check(g.ApplyDeckSummon(dest,summoned),'deck summon '+index);
 check(summoned.Snapshot().locationIndex===(index===-4?1:index<0?2:Math.min(2,index)),'last/source/explicit summon index '+index);
 check(g.CountLocation(2,1)===3&&!g.IsFatal(),'summon preserves row '+index);
}
{
 const g=fixture();g.Epidemic();check(g.message==='Эпидемия: нет подходящих целей.','empty Epidemic has a real no-target message');
 const a=add(g,112101,1,0,1,3),b=add(g,112101,1,0,2,3),big=add(g,112101,1,1,2,8);
 g.Epidemic();g.FlushDeaths();check(!alive(a)&&!alive(b)&&alive(big),'Epidemic still destroys every tied minimum');
}
for(const id of [113401,113302]){
 const g=fixture(1),spell=add(g,id,8,4,1);if(id===113302)spell.AddTokens(512);
 check(g.Play(1,spell.Snapshot().instanceId,1),'play doomed special '+id);
 if(g.IsPending())g.SelectRow(g.requestId,2,1);
 check(!g.IsFatal()&&!g.IsPending()&&spell.Snapshot().locationMask===512,'doomed special leaves play without entering grave '+id);
}
{
 const g=fixture(1),spell=add(g,113302,8,4,1);check(g.Play(1,spell.Snapshot().instanceId,1),'play ordinary special');
 if(g.IsPending())g.SelectRow(g.requestId,2,1);
 check(spell.Snapshot().locationMask===32,'ordinary special still enters grave');
}
{
 const g=fixture(),enemy=add(g,112101,1,0,1,20);add(g,123301,1,0,2,5);add(g,112101,1,1,2,6);
 for(const id of [113301,201657,113311]){
  const spell=add(g,id,8,5,2),d=spell.Definition();g.weatherProfile=false;const before=g.AiCardTempo(spell,true,0,0);
  g.weatherProfile=true;const after=g.AiCardTempo(spell,true,0,0);
  check(!g.weatherAI.Handles(d)&&after===before&&after>0,'weather profile preserves ordinary ability estimate '+id);
 }
 check(g.weatherAI.Handles(BetaGwentDuelDefinition(200301))&&g.weatherAI.Handles(BetaGwentDuelDefinition(113302)),'Hunt/frost retain specialized estimate');
 g.aiPlacing=BetaGwentDuelDefinition(200301);const first=g.BestOwnRow(2);
 g.aiPlacing=BetaGwentDuelDefinition(132310);check(g.BestOwnRow(2)===first,'generic row choice is independent of the previously evaluated card');
 const d=BetaGwentDuelDefinition(132310),rows=[1,2,4];const ranked=rows.map(row=>({row,cost:g.AiRowPlacementCost(2,row,d)*2+(g.AiLanePower(2,row)>=25?8:0)})).sort((a,b)=>a.cost-b.cost);
 check(g.BestOwnRow(2,132310)===ranked[0].row,'explicit row choice evaluates current definition');
}
{
 const g=fixture(1);g.pendingChoice=true;g.pendingIds=[113401,113402];let out=[];g.GetRequestViews({v:out});
 check(out.length===2&&out.every(v=>v.revealed&&v.templateId!==0),'generated choice options are always public');
 const hidden=add(g,112101,8,5,2);g.pendingChoice=false;g.pendingIds=[hidden.Snapshot().instanceId];out=[];g.GetRequestViews({v:out});
 check(out.length===1&&!out[0].revealed&&out[0].templateId===0,'hidden enemy hand remains hidden');
}
{
 const g=fixture(1),targets=[add(g,112101,2,0,2,8),add(g,112101,2,1,2,8),add(g,112101,4,0,2,8)],jotunn=add(g,200218,8,4,1);
 g.recordVisuals=true;g.visualFrames=[];check(g.Play(1,jotunn.Snapshot().instanceId,1),'play Jotunn for move/damage presentation');
 for(let guard=0;g.IsPending()&&guard<6;guard++){const id=g.pendingIds.find(id=>!jotunn.monsterIds.includes(id));if(id)g.SelectTarget(g.requestId,id);else g.FinishTarget(g.requestId);}
 check(!g.IsPending()&&!g.IsFatal()&&targets.every(t=>t.Snapshot().locationMask===1&&t.Snapshot().power.currentPower===6),'Jotunn moves all three units before dealing damage');
 const moving=g.visualFrames.map((f,i)=>({f,i})).filter(x=>x.f.kind===8&&targets.some(t=>t.Snapshot().instanceId===x.f.targetId));
 const damaging=g.visualFrames.findIndex(f=>f.kind===2&&targets.some(t=>t.Snapshot().instanceId===f.targetId));
 check(moving.length===3&&moving.every(x=>x.i<damaging),'native movement snapshots precede all Jotunn impact snapshots');
}
{
 const g=fixture(1),kambi=add(g,152104,1,0,1,1),a=add(g,112101,2,0,2,8),b=add(g,112101,4,0,1,8);
 g.recordVisuals=true;g.visualFrames=[];g.QueueDestroy(kambi);g.FlushDeaths();
 check(!g.IsFatal()&&!alive(a)&&!alive(b),'Kambi death spawns Hemdall and kills units on both sides');
 const deaths=g.visualFrames.filter(f=>f.kind===3&&[a.Snapshot().instanceId,b.Snapshot().instanceId].includes(f.targetId));
 check(deaths.length===2&&deaths.every(f=>f.templateId===152402&&f.sourceId>0),'every swept victim retains Hemdall as the Scorch visual source');
 check(g.CountLocation(1,4)+g.CountLocation(1,2)+g.CountLocation(1,1)===1,'Hemdall survives his own sweep');
}
globalThis.report={stage:168,checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'review168.bundle.js',timeout:120000});
fs.writeFileSync('docs/evidence/review168.json',JSON.stringify(context.report,null,2)+'\n');console.log(JSON.stringify(context.report));
