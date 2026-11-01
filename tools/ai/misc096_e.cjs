'use strict';
const {rt,add,snap,id,check,flush,run,begin,trace,fresh,ids,place,same,want}=globalThis.__misc;
function again(g,side){g.match.currentPlayerId=side;g.match.turnActive=true;g.match.playerOne.hasMadeInitialMoveForCurrentTurn=false;g.match.playerTwo.hasMadeInitialMoveForCurrentTurn=false;g.waiting=false;}
function consumeWith(g,side,victim){again(g,side);const c=add(g,201701,side,8,0);check(g.Play(side,id(c),4),'consumer played');flush(g);check(g.IsPending()&&g.pendingIds.includes(id(victim)),'consume target offered');g.SelectTarget(g.requestId,id(victim));flush(g);return c;}
// 132316 Harpy egg: Killed -> spawn 200308 at a random available own row; consumed (RemovalType Consume) -> consumer boost 4 (in addition to its own consume gain).
if(want(132316))for(const side of [1,2])run(132316,side,'egg killed',g=>{
 const e=add(g,132316,side,2,0,1);const pre=ids(g),rng=trace(g);g.QueueDestroy(e);flush(g);place(g);const n=fresh(g,pre),d=rng.find(r=>r.n===3);
 check(n.length===1&&n[0].runtimeTemplate.templateId===200308&&!!d&&n[0].locationMask===[1,2,4][d.v],'hatchling at Next(3) own row',{n:n.map(s=>[s.runtimeTemplate.templateId,s.locationMask]),rng});
});
if(want(132316))for(const side of [1,2])run(132316,side,'egg consumed',g=>{
 const e=add(g,132316,side,2,0,1);const pre=ids(g),c=consumeWith(g,side,e);const s=snap(c),b=rt.definition(201701).header.power;
 check(s.power.currentPower===b+1+4,'consumer gains egg power 1 + egg boost 4',{p:s.power});
});
// 132201 Arachas behemoth: an own-side consume decrements its timer; TimerChanged (alive) spawns 200174 at a random own row.
if(want(132201))for(const side of [1,2])run(132201,side,'behemoth',g=>{
 const v=add(g,132403,side,1,0,3);const b=begin(g,132201,side);check(snap(b).timerValue===4,'timer 4 after play');const pre=ids(g),rng=trace(g);
 consumeWith(g,side,v);place(g);const n=fresh(g,pre).filter(s=>s.runtimeTemplate.templateId===200174);check(snap(b).timerValue===3&&n.length===1&&n[0].positionPlayerId===side,'own consume: timer -1 and one hatchling',{t:snap(b).timerValue,n:n.length,rng});
 const ev=add(g,132403,3-side,1,0,3);const c2=add(g,201701,3-side,8,0);again(g,3-side);g.Play(3-side,id(c2),4);flush(g);if(g.IsPending()&&g.pendingIds.includes(id(ev))){g.SelectTarget(g.requestId,id(ev));flush(g);}place(g);
 check(snap(b).timerValue===3,'enemy consume does not tick (attacker player must be the owner)',{t:snap(b).timerValue});
});
// 200174 Arachas hatchling: AfterSpawned/AfterMoved into own Active -> summon all own-deck 132304 drones to its row.
if(want(200174))for(const side of [1,2])run(200174,side,'hatchling spawn summons drones',g=>{
 const d1=add(g,132304,side,16,0),d2=add(g,132304,side,16,1),o=add(g,132304,3-side,16,0);const v=add(g,132403,side,1,0,3);const b=begin(g,132201,side);
 consumeWith(g,side,v);place(g);const h=g.live.map(snap).find(s=>s.runtimeTemplate.templateId===200174&&s.positionPlayerId===side);
 check(!!h&&[d1,d2].every(c=>snap(c).locationMask===h.locationMask&&snap(c).positionPlayerId===side)&&snap(o).locationMask===16,'drones from own deck to the hatchling row',{h:h&&h.locationMask,d:[d1,d2].map(c=>snap(c).locationMask)});
});
