'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clearHand(g){g.live.filter(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8).forEach(c=>c.Move(2,512,0));}
{
 const g=fixture();clearHand(g);const sword=add(g,200040,2,0),ship=add(g,152309,8),body=add(g,112101,8,1,2,3);
 check(g.AiNeighbourEngineUtility(ship)>0,'ship gets future value from a profitable right neighbour');
 check(g.OpponentStep()&&(ship.Snapshot().locationMask&7)!==0,'actual AI plays the longship engine');
 check(ship.Snapshot().locationMask===sword.Snapshot().locationMask&&ship.Snapshot().locationIndex+1===sword.Snapshot().locationIndex,'actual ship stands left of Greatsword');
 g.match.playerOne.hasPassed=true;check(g.AiNeighbourEngineUtility(ship)===0,'future ship ticks are not guaranteed catch-up');
}
{
 const g=fixture();clearHand(g);const thunder=add(g,113311,8),unit=add(g,122308,8,1);
 add(g,122308,2,0);add(g,122308,2,1);
 check(g.BestCardRow(2,unit.Definition())===2,'third body joins the pair for Thunder');
 g.weather.ApplyHazard(2,2,4);
 check(g.BestCardRow(2,unit.Definition())!==2,'Thunder setup does not force a unit into lethal weather');
}
{
 const g=fixture();clearHand(g);for(let i=0;i<4;i++)add(g,112101,2,i,2,2);
 const ambush=add(g,142204,8);add(g,112101,8,1,2,2);
 check(g.AiNeighbourEngineUtility(ambush)===8,'Toruviel sees four potential neighbours');
 check(g.OpponentStep()&&(ambush.Snapshot().tokenMask&8)!==0,'actual AI sets Toruviel before enemy pass');
 check(ambush.Snapshot().locationMask===2&&ambush.Snapshot().locationIndex===2,'Toruviel goes between the four neighbours');
 g.match.playerOne.hasPassed=true;check(g.AiNeighbourEngineUtility(ambush)===0,'no Toruviel payoff after enemy already passed');
}
{
 const g=fixture(),morenn=add(g,142208,8,4);
 check(g.AiNeighbourEngineUtility(morenn)>0&&g.AiNeighbourEngineUtility(morenn)<=7,'Morenn has bounded future trigger utility');
 g.match.playerOne.hasPassed=true;check(g.AiNeighbourEngineUtility(morenn)===0,'no Morenn trigger after enemy pass');
}
globalThis.deckCombos128={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'deck-combos128.bundle.js',timeout:120000});
fs.writeFileSync(process.argv[3]||'docs/evidence/deck-combos128.json',JSON.stringify(context.deckCombos128,null,2)+'\n');
