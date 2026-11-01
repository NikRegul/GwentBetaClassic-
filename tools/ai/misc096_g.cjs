'use strict';
const {rt,add,snap,id,check,flush,run,begin,trace,fresh,ids,place,same,want}=globalThis.__misc;
function again(g,side){g.match.currentPlayerId=side;g.match.turnActive=true;g.match.playerOne.hasMadeInitialMoveForCurrentTurn=false;g.match.playerTwo.hasMadeInitialMoveForCurrentTurn=false;g.waiting=false;}
function turnEnd(g,side){g.match.currentPlayerId=side;g.match.turnActive=true;g.EndTurnWithEvents();flush(g);}
// 200226 Wolfsbane: hand play (timer 3) has no effect; in graveyard each own BeforeTurnEnd -1; at 0 it plays itself: random lowest own unit +6, then random highest enemy -6.
if(want(200226))for(const side of [1,2])run(200226,side,'wolfsbane',g=>{
 const l1=add(g,132403,side,1,0,2),l2=add(g,132403,side,2,0,2),hiOwn=add(g,132209,side,4,0,20),e1=add(g,132209,3-side,1,0,15),e2=add(g,132209,3-side,2,0,15),eLow=add(g,132403,3-side,4,0,3);
 const w=add(g,200226,side,8,0);again(g,side);check(g.Play(side,id(w),2),'hand play');flush(g);
 check(snap(w).locationMask===32&&[l1,l2].every(c=>snap(c).power.currentPower===2)&&[e1,e2].every(c=>snap(c).power.currentPower===15),'hand play: no effect (timer>0), to graveyard',{loc:snap(w).locationMask,t:snap(w).timerValue});
 const t0=snap(w).timerValue;turnEnd(g,3-side);check(snap(w).timerValue===t0,'enemy turn end does not tick',{t:snap(w).timerValue,t0});
 for(let k=0;k<5&&snap(w).timerValue>1;k++)turnEnd(g,side);const rng=trace(g);turnEnd(g,side);
 const d1=rng[0],d2=rng[1];check(!!d1&&d1.n===2&&snap([l1,l2][d1.v]).power.currentPower===8&&snap([l1,l2][1-d1.v]).power.currentPower===2,'random lowest own +6 FIRST draw',{rng});
 check(!!d2&&d2.n===2&&snap([e1,e2][d2.v]).power.currentPower===9&&snap([e1,e2][1-d2.v]).power.currentPower===15&&snap(eLow).power.currentPower===3,'then random highest enemy -6',{rng});
});
// 201778 Kerys: own unit (not Doomed) moved Hand|Deck -> Graveyard on own turn while timer>0 -> it is played; timer -1.
if(want(201778))for(const side of [1,2])run(201778,side,'kerys discard',g=>{
 const k=add(g,201778,side,1,0,6);k.SetTimer?k.SetTimer(1):0;const u1=add(g,132209,side,8,0),u2=add(g,132310,side,8,1);again(g,side);
 check(snap(k).timerValue===1,'template timer 1 on board',{t:snap(k).timerValue});g.NilfDiscard(u1);flush(g);place(g);
 check((snap(u1).locationMask&7)!==0&&snap(k).timerValue===0,'discarded unit played, timer 0',{loc:snap(u1).locationMask,t:snap(k).timerValue});
 g.NilfDiscard(u2);flush(g);place(g);check(snap(u2).locationMask===32,'second discard stays in graveyard');
});
