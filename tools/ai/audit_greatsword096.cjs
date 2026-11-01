'use strict';
// Clan Greatsword (200040), source graph: Played -> timer Set(Counter=2);
// BeforeTurn of its owner -> timer -1; TimerTriggered -> timer +Counter, then
// only if WOUNDED (FilterCardPowerState 1): ResetCards(Power) on itself and
// ChangePower(Add, BasePower, Strengthen=2). Unwounded: nothing but the timer.
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
let checks=0;const failures=[];function check(v,n){checks++;if(!v)failures.push(n);}
function add(g,t,zone,index=0,side=2){const id={v:0};g.registry.Allocate(id);const c=new CBetaGwentDuelCard();
 c.Setup(g,id.v,t,side,zone,index);g.registry.Put(id.v,c);g.live.push(c);return c;}
function fixture(){const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(50,50))throw Error('initialize');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;
 g.waiting=false;g.recordVisuals=false;g.weatherProfile=false;g.match.currentPlayerId=1;
 g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=1;g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 for(let i=0;i<3;i++){add(g,112101,8,i,1);add(g,112101,8,i,2);}return g;}
for(const side of [1,2])for(const state of ['wounded','normal','boosted']){
 const g=fixture();g.match.currentPlayerId=side;const hand=add(g,200040,8,4,side);
 if(!g.Play(side,hand.Snapshot().instanceId,1))throw Error('play');g.FlushEffects();g.FlushDeaths();
 let s=hand.Snapshot();check(s.timerValue===2,'played: timer set to Counter=2 ('+side+')');
 const base=s.power.basePower;
 if(state==='wounded')hand.power.SetCurrentPair(base-3,0);if(state==='boosted')hand.power.SetCurrentPair(base+4,0);
 const before=hand.Snapshot().power.currentPower;
 g.BeforeTurnWithEvents(BetaGwentOpponentId(side));g.FlushEffects();g.FlushDeaths();
 check(hand.Snapshot().timerValue===2,'opponent turn does not tick ('+side+'/'+state+')');
 g.BeforeTurnWithEvents(side);g.FlushEffects();g.FlushDeaths();s=hand.Snapshot();
 check(s.timerValue===1&&s.power.currentPower===before,'first own turn: timer 1, no change ('+side+'/'+state+')');
 g.BeforeTurnWithEvents(side);g.FlushEffects();g.FlushDeaths();s=hand.Snapshot();
 check(s.timerValue===2,'second own turn: timer triggers and resets to 2 ('+side+'/'+state+') actual '+s.timerValue);
 if(state==='wounded')check(s.power.basePower===base+2&&s.power.currentPower===base+2,'wounded: heal to base, strengthen 2 ('+side+') actual '+s.power.basePower+'/'+s.power.currentPower);
 else check(s.power.basePower===base&&s.power.currentPower===before,'not wounded: unchanged ('+side+'/'+state+') actual '+s.power.basePower+'/'+s.power.currentPower);
 check(!g.IsFatal(),'resolves '+side+'/'+state);
}
globalThis.result={checks,failures,actualWitcherScript:true,nativeGameplayVerified:false};
`,context,{timeout:120000});
const r=context.result;if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify(r));if(r.failures.length)process.exitCode=1;
