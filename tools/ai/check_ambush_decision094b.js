// 094b: real 0.9.1d position (audit-00130-step34): hidden Morenn, our hand
// Tortured Mage + Margarita. The whole decision must not depend on the
// concealed identity, and must pick the move that wins across plausible worlds.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),zlib=require('zlib');
const dir=path.resolve(process.argv[2]),observe=process.argv.includes('--observe');
function mk(d){const ctx=vm.createContext({console});
 vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(d,n),'utf8')).join('\n')+'\n'+require('./comparison_bridge119.js'),ctx);
 ctx.bridge.setTunes(JSON.parse(fs.readFileSync(path.join(d,'tunes.json'),'utf8')));ctx.bridge.setStrength(4);return ctx;}
const ctx=mk(dir);
const fx=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(__dirname,'fixtures/deck_order091e.json.gz'))));
const f=fx.cases.find(c=>c.name==='audit-00130-step34');
let checks=0;const failures=[],cases=[];
function check(v,n){checks++;if(!v){failures.push(n);if(!observe)throw Error(n);}}
const worlds=[[142208,-1],[201779,-1],[142204,-1],[142210,1],[142210,2],[142307,1],[142307,2]];
function setWorld(t,timer){ctx.t=t;ctx.timer=timer;vm.runInContext(`{const c=active.FindCard(4);c.definition=BetaGwentDuelDefinition(t);c.cardState.originTemplateId=t;c.cardState.runtimeTemplate=c.definition.header;c.cardState.runtimeTierMask=c.definition.header.tierMask;c.cardState.tokenMask=8;c.cardState.timerValue=timer>0?timer:c.definition.initialTimer;c.power.ResetTemplatePower(c.definition.header.power,0);}`,ctx);}
function decide(t,timer,staged){ctx.bridge.load(f.state);setWorld(t,timer);const logs=[];ctx.bridge.setLog(s=>logs.push(s));
 if(staged){let k=0;while(!vm.runInContext('active.AiPreparationStep()',ctx)){if(++k>600)throw Error('Preparation stalled');}}
 ctx.bridge.step();ctx.bridge.setLog(null);const line=logs.find(s=>/event=SELECT\b/.test(s))||'';const m=/template=(\d+)/.exec(line);return m&&Number(m[1]);}
const picks=worlds.map(([t,timer])=>decide(t,timer,false)),staged=worlds.map(([t,timer])=>decide(t,timer,true));
check(new Set(picks).size===1,'decision independent of the concealed ambush identity: '+picks.join(','));
check(JSON.stringify(picks)===JSON.stringify(staged),'cooperative and synchronous decisions agree');
// Ground truth: both first moves continued by the SAME frozen policy to the end.
function outcome(t,timer,first){ctx.bridge.load(f.state);setWorld(t,timer);ctx.first=first;
 const ok=vm.runInContext('active.Play(2,first,2)',ctx);for(let i=0;i<80;i++){const v=ctx.bridge.view();if(v.winner||v.fatal)break;ctx.bridge.step();}
 const v=ctx.bridge.view();return {ok:!!ok,winner:v.winner};}
let mageWins=0,margWins=0;
for(const [t,timer] of worlds){const a=outcome(t,timer,33),b=outcome(t,timer,34);check(a.ok&&b.ok,'forced first moves are legal');
 if(a.winner===2)mageWins++;if(b.winner===2)margWins++;cases.push({world:t,timer,mage:a.winner,margarita:b.winner});}
check(mageWins>margWins,'Tortured Mage first wins in more plausible worlds ('+mageWins+' vs '+margWins+')');
check(picks[0]===201628,'policy plays the bait first (got '+picks[0]+')');
const report={fingerprint:JSON.parse(fs.readFileSync(path.join(dir,'manifest.json'),'utf8')).fingerprint,checks,failures,picks,mageWins,margWins,cases,continuationPolicy:'same snapshot, both sides',kind:'real-position-witness-not-strength-trial',nativeGameplayVerified:false};
if(process.argv[3]&&!process.argv[3].startsWith('--'))fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;
