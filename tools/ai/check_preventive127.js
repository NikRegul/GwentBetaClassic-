// Preventive weather: an empty row the opponent keeps using is worth more than one it never uses.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
{const g=fixture();g.match.currentPlayerId=1;const u=add(g,112101,8,6,1);
 check(g.Play(1,u.cardState.instanceId,1)&&g.aiEnemyRowPlays[0]===1,'opponent placement is recorded publicly');}
{const g=fixture();add(g,112101,2,0,1,8);
 const base=g.WeatherValue(2,1,1);
 g.aiEnemyRowPlays=[5,1,0];
 check(g.WeatherValue(2,1,1)>base,'favoured empty row gains preventive value');
 check(g.WeatherValue(2,4,1)===base,'unused empty row stays at the old cap');
 check(g.WeatherValue(2,1,1)<=8,'preventive value stays bounded');
 g.aiEnemyRowPlays=[1,1,0];
 check(g.WeatherValue(2,1,1)===base,'too few placements give no preference');}
globalThis.preventiveReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'preventive127.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.preventiveReport,null,2)+'\n');
