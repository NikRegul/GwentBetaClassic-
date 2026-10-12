// Round-one concession: a deficit card advantage cannot cover is conceded early.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const D=(lead,own,enemy,best,ec=0,oc=0)=>BetaGwentAIRoundDecision(1,oc,ec,lead,own,enemy,best,14,false,false,0);
check(D(-30,6,5,10)===2,'30 behind with one extra card concedes');
check(D(-30,5,5,10)===2,'30 behind with equal cards concedes');
check(D(-30,8,4,10)===0,'four extra cards can still catch 30');
check(D(-12,6,6,8)===0,'small deficit keeps playing');
check(D(-30,6,5,32)===0,'one strong card that takes the lead keeps playing');
check(D(-30,6,5,10,1)===0,'never concede when the enemy holds a crown');
check(D(-30,2,5,10)===0,'two cards left are not saved by conceding');
globalThis.concedeReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'concede127.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.concedeReport,null,2)+'\n');
