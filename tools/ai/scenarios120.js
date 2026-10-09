// Actual WitcherScript rules transpiled from the release input snapshot.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]);
const context=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.random=()=>.37;
let checksPassed=0;
function check(value,name){if(!value)throw Error(name);checksPassed++;console.log('PASS',name);}
function fixture(){const g=new CBetaGwentDuelSession();check(g.InitializeWithPresets(54,54),'initialize');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;g.recordVisuals=false;
 g.match.currentPlayerId=2;g.match.roundActive=true;g.match.turnActive=true;return g;}
function add(g){const id={v:0};g.registry.Allocate(id);const c=new CBetaGwentDuelCard();c.Setup(g,id.v,112101,2,1,0);
 g.registry.Put(id.v,c);g.live.push(c);return c;}
for(const cleanup of [false,true]){
 const g=fixture(),c=add(g);c.AddTokens(4);c.power.SetCurrentPair(0,0);g.DrainDeaths(cleanup);
 const s=c.Snapshot();check(s.locationMask===32,'dead card enters graveyard '+cleanup);
 check((s.tokenMask&4)!==0,'lock survives graveyard reset '+cleanup);
 check(s.power.currentPower===c.power.GetBasePower(),'graveyard power reset '+cleanup);
}
{const g=fixture(),c=add(g);c.AddTokens(4|1|2);c.Move(2,32,0);c.ResetInGraveyard();
 check((c.Snapshot().tokenMask&4)!==0,'inactive reset preserves lock');
 check((c.Snapshot().tokenMask&3)===0,'transient spying/resilience still reset');}
globalThis.lockReport={stage:120,checks:checksPassed,actualWitcherScript:true,graveyardLockPassed:true};
`,context,{filename:'scenarios120.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(path.resolve(process.argv[3]),JSON.stringify(context.lockReport,null,2)+'\n');
