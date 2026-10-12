// Decisive round ordering: time-decaying cards (weather, boosts under enemy weather) get an
// urgency bonus only when the round must be played out. Runs the translated WitcherScript.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const frost=BetaGwentDuelDefinition(113302),thunder=BetaGwentDuelDefinition(113311),body=BetaGwentDuelDefinition(112101);
function game(round,crowns,passed){
 const g=fixture();for(let i=0;i<3;i++)add(g,112101,1,i,1,6);
 g.match.roundNumber=round;g.match.playerOne.crowns=crowns;g.match.playerOne.hasPassed=passed;return g;
}
check(game(1,0,false).AiDecayUrgency(frost,5,5)===0,'no urgency in an open first round');
check(game(2,0,false).AiDecayUrgency(frost,5,5)===0,'no urgency in round two without enemy crown');
check(game(2,1,false).AiDecayUrgency(frost,5,5)>0,'weather urgent when the enemy already holds a crown');
check(game(3,0,false).AiDecayUrgency(frost,5,5)>0,'weather urgent in the final round');
check(game(3,0,true).AiDecayUrgency(frost,5,5)===0,'no urgency after the enemy passed');
check(game(3,0,false).AiDecayUrgency(frost,0,5)===0,'worthless weather is never pushed');
check(game(3,0,false).AiDecayUrgency(frost,5,1)===0,'last card needs no ordering bonus');
check(game(3,0,false).AiDecayUrgency(body,7,5)===0,'plain units get no urgency');
check(game(3,0,false).AiDecayUrgency(thunder,6,5)===0,'boost waits while own rows are safe');
{const g=game(3,0,false);add(g,112101,1,0,2,5);g.weather.ApplyHazard(2,1,1);
 check(g.AiDecayUrgency(thunder,6,5)>0,'boost urgent while enemy weather wears own bodies');}
globalThis.decisiveReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'decisive127.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.decisiveReport,null,2)+'\n');
