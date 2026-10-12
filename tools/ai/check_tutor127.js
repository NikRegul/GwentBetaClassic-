// Empty deck tutors: Jan Natalis is worth his body when the only tactic left pulls nothing.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const jan=add(fixture(),122103,8,4).Definition();
{const g=fixture();add(g,123201,16,0);
 check(g.AiManagedDeployValue(jan,2,false)===0,'Natalis with an empty Reinforcement has no ability value');
 add(g,122310,16,1);
 check(g.AiManagedDeployValue(jan,2,false)>0,'Natalis values Reinforcement once a soldier is in the deck');}
{const g=fixture();check(g.AiManagedDeployValue(jan,2,false)===0,'Natalis without tactics in the deck has no ability value');}
for(const round of [1,2,3]){
 const g=fixture(),c=add(g,122103,8,4);g.match.roundNumber=round;
 add(g,112101,16,0,2,12);
 check(g.AiTutorTargetCount(c)===0,'Natalis empty tactic pool detected round '+round);
 check(g.AiTutorMulliganPriority(c)===30,'Natalis receives empty tutor replacement priority '+round);
 check(g.AiCardKeepValue(c)<=c.Snapshot().power.currentPower,'empty Natalis keep value is at most body '+round);
 g.AiMulligan(1);
 check(c.Snapshot().locationMask===16,'actual mulligan replaces empty Natalis round '+round);
}
{const g=fixture(),c=add(g,122103,8,4);add(g,123201,16,0);
 check(g.AiTutorTargetCount(c)===0,'nested empty Reinforcement does not keep Natalis');
 add(g,122310,16,1);
 check(g.AiTutorTargetCount(c)>0&&g.AiTutorMulliganPriority(c)===0,'useful nested Reinforcement keeps Natalis ability');}
{const g=fixture();for(const row of [1,2])add(g,112101,row,0,1,6);
 const empty=add(g,123201,16,0),c=add(g,122103,8,4);
 check(g.Play(2,c.cardState.instanceId,2)&&!g.IsFatal()&&!g.IsPending(),'Natalis resolves with an empty tutor');}
globalThis.tutorReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'tutor127.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.tutorReport,null,2)+'\n');
