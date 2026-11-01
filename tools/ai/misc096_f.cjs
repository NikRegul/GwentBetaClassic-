'use strict';
const {rt,add,snap,id,check,flush,run,begin,trace,fresh,ids,place,same,want}=globalThis.__misc;
function again(g,side){g.match.currentPlayerId=side;g.match.turnActive=true;g.match.playerOne.hasMadeInitialMoveForCurrentTurn=false;g.match.playerTwo.hasMadeInitialMoveForCurrentTurn=false;g.waiting=false;}
function settle(g){let k=0;while(g.IsPending()&&k++<20){let ok=false;if(g.pendingRally||g.pendingRow){for(const s of [1,2])for(const r of [2,1,4])if(!ok&&g.CanSelectRow(g.requestId,s,r))ok=g.SelectRow(g.requestId,s,r);}else if(g.pendingChoice){for(const x of [...g.pendingIds])if(!ok)ok=g.SelectTemplateChoice(g.requestId,x);}else for(const x of [...g.pendingIds])if(!ok)ok=g.SelectTarget(g.requestId,x);if(!ok)ok=g.FinishTarget(g.requestId);if(!ok)break;flush(g);}}
// 201624: Played timer Set 1; own later play of a spell/item special (category 2^20|2^54) on own turn with timer>0 -> timer -1 -> TimerTriggered: copy 201624 at own row END with Doomed512.
if(want(201624))for(const side of [1,2])for(const kind of ['spell','unit'])run(201624,side,'revenant/'+kind,g=>{
 add(g,132403,side,1,0,30);add(g,132403,side,1,1,30);const r=begin(g,201624,side);check(snap(r).timerValue===1,'timer 1 after play');
 const pre=ids(g);again(g,side);const c=add(g,kind==='spell'?113310:132310,side,8,0);check(g.Play(side,id(c),2),'own card played');flush(g);settle(g);
 const n=fresh(g,pre).filter(s=>s.runtimeTemplate.templateId===201624),row=g.live.map(snap).filter(s=>s.positionPlayerId===side&&s.locationMask===snap(r).locationMask).sort((a,b)=>a.locationIndex-b.locationIndex);
 if(kind==='spell')check(n.length===1&&(n[0].tokenMask&512)!==0&&row[row.length-1].instanceId===n[0].instanceId&&snap(r).timerValue===0,'copy at row end with Doomed, timer 0',{n:n.map(s=>[s.locationMask,s.locationIndex,s.tokenMask]),t:snap(r).timerValue});
 else check(n.length===0&&snap(r).timerValue===1,'unit play does not tick');
});
// 200114 Alpha werewolf: Played / Moonlight Add on its row / moved into its row -> if its row has Moonlight256: wolves 132403 left and right.
if(want(200114))for(const side of [1,2])for(const moon of [true,false])run(200114,side,'alpha played/'+moon,g=>{
 add(g,132209,side,2,0,30);if(moon){g.weather.hazards[(side-1)*3+1]=256;}const pre=ids(g),w=begin(g,200114,side);const order=g.live.map(snap).filter(s=>s.positionPlayerId===side&&s.locationMask===2).sort((a,b)=>a.locationIndex-b.locationIndex).map(s=>s.runtimeTemplate.templateId);const i=order.indexOf(200114);
 if(moon)check(order[i-1]===132403&&order[i+1]===132403&&fresh(g,pre).filter(s=>s.runtimeTemplate.templateId===132403).length===2,'two wolves adjacent under Moonlight',{order});else check(fresh(g,pre).filter(s=>s.runtimeTemplate.templateId===132403).length===0,'no moonlight: no wolves');
});
if(want(200114))for(const side of [1,2])run(200114,side,'alpha moonlight later',g=>{
 const w=add(g,200114,side,2,0,10);const pre=ids(g);g.weather.ApplyHazard(side,2,256);flush(g);settle(g);check(fresh(g,pre).filter(s=>s.runtimeTemplate.templateId===132403&&s.positionPlayerId===side&&s.locationMask===2).length===2,'Moonlight added to its row spawns two wolves');
});
