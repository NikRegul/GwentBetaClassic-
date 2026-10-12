// Weather decisions and damage pulses run through the actual translated rules.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clearHand(g,side){g.live.filter(c=>c.Snapshot().positionPlayerId===side&&c.Snapshot().locationMask===8).forEach(c=>c.Move(side,512,0));}
{
 const g=fixture(),ship=add(g,200105,8,4),enemy=add(g,112101,1,0,1,10);
 g.recordVisuals=true;g.visualFrames=[];
 check(g.Play(2,ship.cardState.instanceId,1),'Dimun Warship plays through the real target request');
 const hits=g.visualFrames.filter(f=>f.kind===2&&f.sourceId===ship.cardState.instanceId);
 check(hits.length===4&&hits.every(f=>f.attackCount===1),'ship produces four distinct hits, not one merged attack');
 const powers=hits.map(f=>f.cards.find(c=>c.card.instanceId===enemy.cardState.instanceId).card.power.currentPower);
 check(JSON.stringify(powers)===JSON.stringify([9,8,7,6]),'all four intermediate power values reach the replay');
 check(hits.every(f=>f.audioKind===20),'each hit has its own impact audio cue');
}
{
 const g=fixture();for(const row of [1,2,4]){add(g,112101,row,0,2,10);g.weather.ApplyHazard(2,row,1);}
 g.recordVisuals=true;g.visualFrames=[];g.weather.BeforeTurn(2);
 const hits=g.visualFrames.filter(f=>f.kind===2);
 check(hits.length===3&&new Set(hits.map(f=>f.row)).size===3,'Frost records all three rows as independent hits');
}
for(const weatherProfile of [false,true]){
 const g=fixture();g.weatherProfile=weatherProfile;
 for(const row of [1,2,4])add(g,112101,row,0,1,15);
 const rag=add(g,113101,8,4),drought=add(g,200018,8,5);
 check(g.AiCardTempo(rag,false)>g.AiCardTempo(rag,true),'Ragnarok retains future damage beyond immediate simulation '+weatherProfile);
 check(g.AiCardTempo(drought,false)>g.AiCardTempo(drought,true),'Drought retains future damage beyond immediate simulation '+weatherProfile);
 const before=g.AiWeatherForecast(2,1,32);
 for(const row of [1,2,4])g.weather.ApplyHazard(1,row,32);
 check(before>0&&g.AiCardTempo(drought,false)<=0,'equal global weather does not promise extra damage on existing Ragnarok '+weatherProfile);
}
// Moonlight is worth clearing Frost even with ordinary units; eligible future units
// add value, while a passed opponent must not create phantom catch-up points.
for(const weatherProfile of [false,true]){
 const g=fixture();g.weatherProfile=weatherProfile;
 for(const row of [1,2,4]){add(g,112101,row,0,2,12);g.weather.ApplyHazard(2,row,1);}
 const moon=add(g,200067,8,4),moon2=add(g,200067,8,5),base=moon.Definition(),full=BetaGwentDuelModeDefinition(base,201746);
 check(g.specials.RowValue(full,2,2,1)>0,'Full Moon values replacement of Frost without current Beasts '+weatherProfile);
 check(g.AiCardTempo(moon,false)>g.AiCardTempo(moon,true),'Moonlight clearing value survives the exact-immediate correction '+weatherProfile);
 check(g.ModeValue(base,201746,2)>g.ModeValue(base,201747,2),'Moonlight chooses defensive Full Moon over empty enemy row '+weatherProfile);
 check(g.Play(2,moon.cardState.instanceId,1)&&!g.IsPending(),'AI resolves Moonlight mode and row '+weatherProfile);
 check([1,2,4].some(row=>g.weather.Token(2,row)===256),'actual play replaces a friendly Frost row with Full Moon '+weatherProfile);
 const row=[1,2,4].find(r=>g.weather.Token(2,r)===256);
 check(g.specials.RowValue(full,2,2,row)===0,'second Moonlight cannot claim value for identical existing Full Moon '+weatherProfile);
 g.FinishTurn();
 check(g.Snapshot().currentPlayerId===2,'opponent turn advances before second Moonlight '+weatherProfile);
 check(g.Play(2,moon2.cardState.instanceId,1),'second Moonlight play is legal '+weatherProfile);
 check([1,2,4].filter(row=>g.weather.Token(2,row)===256).length===2,'second Moonlight clears a different Frost row '+weatherProfile);
}
for(const weatherProfile of [false,true]){
 const g=fixture();g.weatherProfile=weatherProfile;clearHand(g,2);
 for(let i=0;i<4;i++)add(g,112101,8,i,2,2);
 for(const row of [1,2,4]){add(g,112101,row,0,2,12);add(g,112101,row,0,1,12);g.weather.ApplyHazard(2,row,1);}
 add(g,200067,8,4);add(g,200067,8,5);
 const decisionLog=[];Host.log=s=>decisionLog.push(s);
 const played=g.OpponentStep();Host.log=null;
 if(![1,2,4].some(row=>g.weather.Token(2,row)===256))console.log(decisionLog.filter(s=>s.includes('AI_')).join('\n'));
 check(played&&[1,2,4].some(row=>g.weather.Token(2,row)===256),'full AI decision replaces Frost with held Moonlight '+weatherProfile);
}
for(const weatherProfile of [false,true]){
 const g=fixture();g.weatherProfile=weatherProfile;clearHand(g,2);
 for(let i=0;i<4;i++)add(g,112101,8,i,2,2);
 for(const row of [1,2,4])add(g,112101,row,0,1,10);
 const rag=add(g,113101,8,4),drought=add(g,200018,8,5);
 check(g.OpponentStep()&&[1,2,4].every(row=>g.weather.Token(1,row)>0),'full AI decision uses one global weather early '+weatherProfile);
 const remaining=[rag,drought].find(c=>c.Snapshot().locationMask===8),tokens=[1,2,4].map(row=>g.weather.Token(1,row));
 g.FinishTurn();
 check(g.OpponentStep()&&remaining.Snapshot().locationMask===8&&JSON.stringify(tokens)===JSON.stringify([1,2,4].map(row=>g.weather.Token(1,row))),'AI saves the second redundant global weather for another round '+weatherProfile);
}
// Roach belongs to the acting player, not to the half receiving an enemy gold spy.
for(const side of [1,2]){
 const g=fixture(side),enemy=side===1?2:1,roach=add(g,112210,16,0,enemy),spy=add(g,122105,8,4,side);
 check(g.Play(side,spy.cardState.instanceId,1),'play Dijkstra onto opponent half '+side);
 check(roach.Snapshot().locationMask===16,'enemy gold spy cannot summon defending Roach '+side);
}
for(const side of [1,2]){
 const g=fixture(side),roach=add(g,112210,16,0,side),gold=add(g,112101,8,4,side);
 check(g.Play(side,gold.cardState.instanceId,1),'play own gold unit '+side);
 check((roach.Snapshot().locationMask&7)!==0&&roach.Snapshot().positionPlayerId===side,'own gold still summons own Roach '+side);
}
{
 const g=fixture(),c=add(g,122104,32,0);c.cardState.tokenMask|=4;
 g.NorthResurrect(c,0,1,-3,false);
 check((c.Snapshot().locationMask&7)!==0&&(c.Snapshot().tokenMask&4)!==0,'real resurrection preserves the instance lock');
}
globalThis.weatherVisualReport={checks,actualWitcherScript:true,nativeGameTested:false,releaseBuildStarted:false};
`,context,{filename:'weather-visual126.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.weatherVisualReport,null,2)+'\n');

