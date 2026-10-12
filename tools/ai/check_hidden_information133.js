// Full decision traces must be unchanged when only unknown enemy information changes.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const ctx=vm.createContext({console});
const root=path.resolve(__dirname,'../..'),folder=path.resolve(process.argv[2]),pool=JSON.parse(fs.readFileSync(path.join(folder,'manifest.json'))).presets;
const fixture=fs.readFileSync(path.join(root,'tools/ai/check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(folder,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function decision(preset,mutate){
 Host.strength=4;Host.matchStrength=[4,4];Host.seatIndex=1;Host.tunes=[{},{}];Host.random=()=>.37;
 const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(54,preset))throw Error('initialize');
 g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;g.recordVisuals=false;g.aiSimDamp=40;
 g.match.currentPlayerId=2;g.match.turnActive=true;g.match.roundActive=true;g.match.roundNumber=2;g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 add(g,112101,1,0,1,11);add(g,112101,2,0,2,9);
 const ambush=add(g,142306,4,0,1);ambush.AddTokens(8);
 if(mutate){
  for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId!==1||!((s.locationMask===8||s.locationMask===16)&&(s.tokenMask&64)===0||(s.locationMask&7)!==0&&(s.tokenMask&8)!==0))continue;
   const hidden=(s.locationMask&7)!==0;c.definition=BetaGwentDuelDefinition(hidden?142307:122106);c.cardState.runtimeTemplate=c.definition.header;c.cardState.originTemplateId=c.TemplateId();c.power.SetCurrentPair(40,9);c.cardState.timerValue=7;
  }
  g.presetOne=99;g.nilfInitialOne=[122106,122106,122106];g.nilfSpellOne=100;
 }
 const lines=[];Host.log=s=>lines.push(s);const ok=g.OpponentStep();Host.log=null;
 const choices=[];
 for(const s of lines){if(!s.includes('event='))continue;if(/event=(OPTION|REJECT|SELECT|PASS)/.test(s)){choices.push(s);if(/event=(SELECT|PASS)/.test(s))break;}}
 return {ok,fatal:g.IsFatal(),choices};
}
globalThis.decision=decision;
`,ctx);
const manifest=JSON.parse(fs.readFileSync(path.join(folder,'manifest.json')));
const report={schema:1,fingerprint:manifest.fingerprint,kind:'full_decision_hidden_information_metamorphic',nativeGameTested:false,checks:0,results:[]};
for(const preset of pool){ctx.preset=preset;const a=vm.runInContext('decision(preset,false)',ctx,{timeout:120000});const b=vm.runInContext('decision(preset,true)',ctx,{timeout:120000});
 const pass=a.ok&&b.ok&&!a.fatal&&!b.fatal&&a.choices.length>0&&JSON.stringify(a.choices)===JSON.stringify(b.choices);
 report.results.push({preset,pass,original:a,mutated:b});report.checks++;fs.writeFileSync(path.resolve(process.argv[3]),JSON.stringify(report,null,2));console.log(pass?'PASS':'FAIL','hidden decision',preset,a.choices.length,b.choices.length);
}
if(report.results.some(r=>!r.pass))process.exitCode=1;
