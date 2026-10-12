// Draw spies: real card rules on cloned positions, with unknown deck order.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const spies=[122203,132204,142203,152214,162210];
function position(id,deck=[3,3],hand=[],lead=2,round=1){
 const g=fixture();
 g.live.filter(c=>c.Snapshot().locationMask===8&&c.cardState.positionPlayerId===2).forEach(c=>c.Move(2,512,0));
 g.Leader(2)?.Move(2,512,0);g.match.roundNumber=round;
 add(g,112101,1,0,2,10+lead);add(g,112101,1,0,1,10);
 const spy=add(g,id,8,0);
 hand.forEach((p,i)=>add(g,112101,8,i+1,2,p));deck.forEach((p,i)=>add(g,112101,16,i,2,p));
 return {g,spy};
}
function forecast(g,spy){const unsafe={v:false},risk={v:0},tempo={v:0};const draw=g.AiSpyDrawForecast(spy,unsafe,risk,tempo);return {unsafe:unsafe.v,risk:risk.v,tempo:tempo.v,draw};}
function liveState(g){return JSON.stringify({cards:g.live.map(c=>c.Snapshot()),match:g.match.Snapshot(),seed:g.random.InitialSeed(),draws:g.random.DrawCount()});}
for(const id of spies){
 const {g,spy}=position(id);const state=liveState(g),r=forecast(g,spy);
 check(r.unsafe&&r.risk>0,'weak last draw cannot throw away lead '+id);
 check(r.draw<=3&&r.tempo<=-11,'draw benefit and enemy body remain separate '+id);
 check(liveState(g)===state,'forecast preserves live cards, match and RNG '+id);
 check(g.OpponentStep()&&g.match.playerTwo.hasPassed&&spy.Snapshot().locationMask===8,'actual AI passes instead of a losing last spy '+id);
}
for(const round of [1,2,3]){
 const {g,spy}=position(162210,[20,20],[],2,round),r=forecast(g,spy);
 check(!r.unsafe&&r.draw>=20,'strong playable draw can recover in round '+round);
 check(g.OpponentStep()&&spy.Snapshot().locationMask!==8&&!g.IsFatal(),'AI retains useful draw as legal action in round '+round);
}
{
 const {g,spy}=position(162210,[20,20],[],-2,1);
 check(forecast(g,spy).risk===0,'strong last draw has a viable continuation while behind');
 check(g.OpponentStep()&&spy.Snapshot().locationMask!==8&&!g.match.playerTwo.hasPassed,'last-card conservation does not discard a viable spy continuation');
}
{
 const {g,spy}=position(162210,[],[],2),r=forecast(g,spy);
 check(r.unsafe&&r.draw===0,'empty deck provides no phantom draw');
}
{
 const {g,spy}=position(162210,[3,3],[],20),r=forecast(g,spy);
 check(!r.unsafe,'a spy that leaves a safe lead is not forbidden');
}
{
 const {g,spy}=position(162210,[3,3],[],-10,3),r=forecast(g,spy);
 check(!r.unsafe,'when already behind, a draw remains a legal last chance');
}
{
 const {g,spy}=position(162210,[3,8,15,20],[8,8],0),before=forecast(g,spy);
 const deck=g.live.filter(c=>c.Snapshot().locationMask===16&&c.cardState.positionPlayerId===2);
 deck.forEach((c,i)=>c.Move(2,16,deck.length-i-1));
 check(JSON.stringify(forecast(g,spy))===JSON.stringify(before),'forecast does not peek at remaining own deck order');
 const hidden=g.live.find(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===8);
 hidden.cardState.runtimeTemplate=BetaGwentDuelDefinition(112111).header;
 check(JSON.stringify(forecast(g,spy))===JSON.stringify(before),'opponent hidden hand template does not change the forecast');
}
{
 const {g,spy}=position(122203,[10,10],[6,6,6,6,6]);
 check(g.AiDrawUtility(spy.Definition(),2)>0,'Thaler shares early draw utility with the other factions');
 g.match.playerOne.hasPassed=true;
 check(g.AiDrawUtility(spy.Definition(),2)===0,'no future card-pressure bonus after opponent pass');
}
{
 const {g,spy}=position(162210,[15,15],[5,5,5,5,5],-1),r=forecast(g,spy);
 check(r.draw>=15&&r.risk===0,'early ordering values the newly drawn playable card');
 check(g.OpponentStep()&&spy.Snapshot().locationMask!==8,'actual early AI uses a useful spy before leaving it to the end');
}
{
 const {g,spy}=position(162210,[3,3],[],2);g.weather.ApplyHazard(1,2,2048);g.FlushEffects();
 check(g.BestCardRow(2,spy.Definition())===2,'spy still uses damaging contact weather');
 check(forecast(g,spy).tempo>-13,'forecast includes contact damage to the spy');
}
globalThis.spyReport={stage:125,checks,actualWitcherScript:true,nativeGameTested:false,releaseBuildStarted:false};
`,context,{filename:'scenarios125.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.spyReport,null,2)+'\n');
console.log(JSON.stringify(context.spyReport));
