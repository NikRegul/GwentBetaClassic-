// Reported 26.10.2026: AI Cyclops destroyed a 7-power ally to hit the player's
// strengthened An Craite Swordsman (14/14, timer 2). The 7 damage healed back
// (+2 strength) after the AI's next turn while a lethal target was available.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
let checks=0;
function check(v,n){if(!v)throw Error(n);checks++;console.log('PASS',n);}
function add(g,t,zone,index=0,side=2,power){const id={v:0};g.registry.Allocate(id);const c=new CBetaGwentDuelCard();
 c.Setup(g,id.v,t,side,zone,index);if(power!==undefined)c.power.SetCurrentPair(power,0);
 g.registry.Put(id.v,c);g.live.push(c);return c;}
function fixture(enemyHand){const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(50,50))throw Error('initialize');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;
 g.waiting=false;g.recordVisuals=false;g.weatherProfile=false;g.match.currentPlayerId=2;
 g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=2;
 g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 for(let i=0;i<enemyHand;i++)add(g,112101,8,i,1);for(let i=0;i<3;i++)add(g,112101,8,i,2);return g;}
function swordsman(g){const c=add(g,200040,1,0,1);c.power.basePower+=6;c.power.SetCurrentPair(14,0);c.cardState.timerValue=2;return c;}
function play(g){const cy=add(g,200037,8,3,2);check(g.Play(2,cy.cardState.instanceId,2),'AI plays Cyclops');
 for(let k=0;k<8&&g.IsPending();k++)check(__pending(g),'AI resolves Cyclops request');g.FlushEffects();g.FlushDeaths();
 check(!g.IsFatal()&&!g.IsPending(),'Cyclops completes');}
{
 const g=fixture(4),sw=swordsman(g),weak=add(g,152213,2,0,1,4);add(g,132213,1,0,2,7);
 check(sw.Snapshot().power.basePower+sw.Snapshot().power.permanentPower===14,'swordsman strengthened to 14');
 play(g);
 check(sw.Snapshot().power.currentPower===14,'regenerating swordsman is not the target');
 check((weak.Snapshot().locationMask&7)===0,'lethal 7 damage kills the 4-power unit instead');
}
// Alone, the swordsman is still a legal and taken target.
{
 const g=fixture(4),sw=swordsman(g);add(g,132213,1,0,2,7);
 play(g);check(sw.Snapshot().power.currentPower===7,'only target: swordsman is hit');
}
// Lethal damage is never discounted by regeneration.
{
 const g=fixture(4),sw=swordsman(g);sw.power.SetCurrentPair(6,0);const other=add(g,152213,2,0,1,4);add(g,132213,1,0,2,7);
 play(g);check((sw.Snapshot().locationMask&7)===0,'damaged swordsman in kill range is finished');
}
globalThis.cyclopsReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'cyclops197.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.cyclopsReport,null,2)+'\n');
