// Replay neighbouring engines on disposable public-state clones, including real deathwishes.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function state(g){return JSON.stringify({cards:g.live.map(c=>c.Snapshot()),match:g.Snapshot(),seed:g.random.InitialSeed(),draws:g.random.DrawCount()});}
const cases=[];
for(const strength of [2,3,4])for(const row of [1,2,4])for(const engine of [152309,152109,132308]){
 Host.strength=strength;const g=fixture();
 const left=add(g,engine,row,0,1);if(engine===132308)left.cardState.timerValue=1;
 const right=add(g,engine===132308?132305:200040,row,1,1);
 if(engine===132308){
  add(g,132305,16,0,1);add(g,132305,16,1,1);for(let j=2;j<8;j++)add(g,112101,16,j,1);
  g.aiStartingDeckOne.Clear();for(let j=0;j<3;j++)g.aiStartingDeckOne.PushBack(132305);
 }
 const spy=add(g,162210,8,4,2);spy.cardState.timerValue=0;
 const before=state(g),d=spy.Definition(),best=g.BestCardRow(2,d),index=g.AiAdjacencyIndex(spy,best);
 const append=g.AiSpyInsertionForecast(2,d,row,-3),insert=g.AiSpyInsertionForecast(2,d,row,1);
 if(engine!==132308)check(insert>append,'insertion beats append for engine '+engine+', row '+row+', strength '+strength+' ('+insert+' vs '+append+')');
 check(best===row&&index===1,'spy chooses the engine gap '+engine+'/'+row+'/'+strength);
 check(g.AiPlacementAnchor(d)===right.cardState.instanceId,'ordinary play uses the same insertion anchor');
 check(state(g)===before,'placement probe preserves live state and RNG');
 const clone=g.AiSimClone(),copy=clone.FindCard(spy.cardState.instanceId);
 check(clone.AiAdjacencyIndex(copy,row)===index,'exact play simulation chooses the same gap');
 check(clone.AiPlacementAnchor(copy.Definition())===right.cardState.instanceId,'exact play uses the same insertion anchor');
 cases.push({engine,row,strength,append,insert,index,hiddenDeckHypotheses:engine===132308});
}
for(const engine of [152309,152109,132308]){
 const g=fixture(),left=add(g,engine,2,0,1);left.cardState.tokenMask|=4;left.cardState.timerValue=1;
 add(g,engine===132308?132305:200040,2,1,1);add(g,132305,16,0,1);
 const spy=add(g,162210,8,4,2),r={v:0},i={v:0},v={v:0};
 check(!g.AiSpyDisruptionSlot(2,spy.Definition(),2,r,i,v),'locked engine is not a disruption target '+engine);
}
{
 const g=fixture(),vran=add(g,132308,2,0,1);vran.cardState.timerValue=1;add(g,112101,2,1,1,6);
 const spy=add(g,162210,8,4,2),r={v:0},i={v:0},v={v:0};
 check(!g.AiSpyDisruptionSlot(2,spy.Definition(),2,r,i,v),'feeding Vran instead of a plain body has no invented deathwish benefit');
}
// Recompute after changing private enemy cards: a warm cache must not hide a leak.
for(const strength of [2,3,4]){
 Host.strength=strength;const g=fixture(),vran=add(g,132308,2,0,1);vran.cardState.timerValue=1;
 add(g,132305,2,1,1);for(let i=0;i<8;i++)add(g,132305,16,i,1);
 g.aiStartingDeckOne.Clear();for(let i=0;i<3;i++)g.aiStartingDeckOne.PushBack(132305);
 const spy=add(g,162210,8,4,2),r={v:0},i={v:0},v={v:0};
 g.AiSpyDisruptionSlot(2,spy.Definition(),0,r,i,v);const before=[r.v,i.v,v.v];
 for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId===1&&(s.locationMask===8||s.locationMask===16)&&(s.tokenMask&64)===0){
  c.definition=BetaGwentDuelDefinition(122106);c.cardState.runtimeTemplate=c.definition.header;c.power.SetCurrentPair(40,9);
 }}
 g.aiSpySlotRevision='';r.v=i.v=v.v=0;g.AiSpyDisruptionSlot(2,spy.Definition(),0,r,i,v);
 check(JSON.stringify(before)===JSON.stringify([r.v,i.v,v.v]),'fresh neighbour estimate ignores actual private hand/deck '+strength);
 vran.cardState.tokenMask|=4;g.AiSpyDisruptionSlot(2,spy.Definition(),0,r,i,v);
 check(v.v===0,'a changed public lock invalidates the cached gap '+strength);
}
// Exercise the full AI action, including PlayBefore, not just its helper's output.
for(const strength of [2,3,4]){
 Host.strength=strength;const g=fixture();
 const left=add(g,152309,2,0,1),right=add(g,200040,2,1,1),spy=add(g,162210,8,0,2);
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;
 add(g,112101,1,0,2,10);add(g,112101,8,0,1);for(let j=0;j<4;j++)add(g,112101,16,j,2,40);
 const pre={row:g.BestCardRow(2,spy.Definition()),anchor:g.AiPlacementAnchor(spy.Definition()),horizon:g.AiHorizon(2)};
 const logs=[];Host.log=s=>logs.push(s);const ok=g.OpponentStep();Host.log=null;
 check(ok&&!g.IsFatal()&&!g.IsPending(),'whole spy decision resolves '+strength);
 check(spy.Snapshot().locationMask===2&&spy.Snapshot().positionPlayerId===1,'AI plays spy into the enemy engine row '+strength+' expected='+JSON.stringify(pre));
 check(left.Snapshot().locationIndex<spy.Snapshot().locationIndex&&spy.Snapshot().locationIndex<right.Snapshot().locationIndex,'real AI inserts between ship and sword '+strength);
}
globalThis.report={checks,cases,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'spy-neighbours.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
