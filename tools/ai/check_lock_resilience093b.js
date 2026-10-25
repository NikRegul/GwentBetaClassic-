// Source ChangeTokensAction.Toggle splits lock into Add/Remove; Add clears
// Resilience, Ambush and Disloyal. Exercise real locks and real round cleanup.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const {context:ctx,manifest}=load(path.resolve(process.argv[2]));ctx.observe=process.argv.includes('--observe');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const failures=[],cases=[];check=(v,n)=>{checks++;if(!v){failures.push(n);if(!observe)throw Error(n);}};
function position(side=1){const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=1;g.match.playerOne.crowns=g.match.playerTwo.crowns=0;g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();return g;}
function nextRound(g){let m=g.Snapshot();check(g.Pass(m.currentPlayerId),'first actual pass');m=g.Snapshot();check(g.Pass(m.currentPlayerId),'second actual pass');
 check(g.IsWaitingRound()&&!g.IsFatal(),'real first round waits for cleanup');check(g.BeginNextRound()&&!g.IsFatal(),'real next round starts');}
for(const side of [1,2])for(const row of [1,2,4])for(const template of [142213,142306,201701])for(const locked of [false,true]){
 const g=position(3-side),unit=add(g,template,row,0,side,12),spell=add(g,113319,8,0,3-side);
 if(locked){check(g.Play(3-side,spell.Snapshot().instanceId,1),'real Shackles locks resilient target');
  if(g.IsPending())check(g.SelectTarget(g.requestId,unit.Snapshot().instanceId),'manual lock request selects the real target');
  check(!g.IsPending()&&!g.IsFatal(),'locking play finishes');
  check((unit.Snapshot().tokenMask&5)===4,'lock removes the current resilience status');}
 nextRound(g);
 const zone=unit.Snapshot().locationMask;
 check(locked?zone===32:(zone&7)!==0,'only actually resilient unit carries: '+template+'/'+side+'/'+row+'/'+locked);
 if(!locked)check((unit.Snapshot().tokenMask&1)===0,'a normal carry consumes resilience');
 cases.push({template,side,row,locked,zone,tokens:unit.Snapshot().tokenMask});
}
// Unlocking restores the ability, not the status removed by the earlier lock.
for(const side of [1,2]){
 const g=position(),unit=add(g,142213,1,0,side);unit.ToggleLock();unit.ToggleLock();
 check((unit.Snapshot().tokenMask&5)===0,'unlock does not regrant removed resilience');nextRound(g);
 check(unit.Snapshot().locationMask===32,'unlocked Yarpen still needs resilience reapplied to carry');
}
// Granting resilience AFTER a lock is a separate legal status change. Do not
// fix the bug by making cleanup ignore every locked resilient unit.
for(const side of [1,2]){
 const g=position(),unit=add(g,142213,1,0,side);unit.ToggleLock();
 check((unit.Snapshot().tokenMask&5)===4,'fixture starts locked without resilience');
 unit.ToggleResilience();check((unit.Snapshot().tokenMask&5)===5,'later resilience can coexist with lock');
 nextRound(g);check((unit.Snapshot().locationMask&7)!==0,'newly granted resilience still carries');
 check((unit.Snapshot().tokenMask&5)===4,'cleanup consumes new resilience and keeps the lock');
}
// All lock entry points agree on the removal mask; independent tokens remain.
for(const method of ['ToggleLock','AddLock']){
 const g=position(),unit=add(g,142213,1,0);unit.AddTokens(128|16|64|1024);unit[method]();
 check((unit.Snapshot().tokenMask&137)===0,'lock removes resilience/ambush/disloyal: '+method);
 check((unit.Snapshot().tokenMask&(4|16|64|1024))===(4|16|64|1024),'lock preserves independent statuses: '+method);
}
globalThis.result={checks,failures,cases,actualWitcherScript:true,nativeGameplayVerified:false};
`,ctx,{timeout:120000});
const report={fingerprint:manifest.fingerprint,...ctx.result};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));if(report.failures.length)process.exitCode=1;
