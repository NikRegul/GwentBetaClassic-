// Stage 131: Kaedweni Cavalry does not strip the armour of an own Redanian Knight-Elect.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clearHand(g,side){g.live.filter(c=>c.cardState.positionPlayerId===side&&c.cardState.locationMask===8).forEach(c=>c.Move(side,512,0));}
function armored(g,t,zone,i,side,p,a){const c=add(g,t,zone,i,side,p);c.power.armor=a;return c;}
{
 const g=fixture();clearHand(g,2);
 add(g,112101,1,0,2,5);const squire=armored(g,123301,1,1,2,7,2);add(g,112101,1,2,2,5);
 const enemy=armored(g,112101,1,0,1,6,3);
 const cav=add(g,122314,8,0,2);
 const v1={v:0};
 check(g.AiAbilityChoiceValue(cav,enemy,0)>g.AiAbilityChoiceValue(cav,squire,0),'enemy armour beats own Knight-Elect armour');
 const elite=armored(g,122317,2,0,2,8,4);
 check(g.AiAbilityChoiceValue(cav,elite,0)>g.AiAbilityChoiceValue(cav,squire,0),'own Redanian Elite is a better meal than the Knight-Elect');
}
{
 const g=fixture();clearHand(g,2);
 const enemyElite=armored(g,122317,1,0,1,8,4);add(g,112101,1,1,1,4);const enemySquire=armored(g,123301,1,2,1,7,2);add(g,112101,1,3,1,4);
 const enemyPlain=armored(g,112101,2,0,1,6,3);
 const cav=add(g,122314,8,0,2);
 check(g.AiAbilityChoiceValue(cav,enemySquire,0)>g.AiAbilityChoiceValue(cav,enemyElite,0),'stopping an enemy Knight-Elect beats feeding an enemy Elite +5');
 check(g.AiAbilityChoiceValue(cav,enemyPlain,0)>g.AiAbilityChoiceValue(cav,enemyElite,0),'plain enemy armour beats an enemy Elite');
}
globalThis.cavalryReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'cavalry131.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.cavalryReport,null,2)+'\n');
