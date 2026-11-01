'use strict';
const {rt,add,snap,id,check,flush,run,begin,trace,fresh,ids,place,same,want}=globalThis.__misc;
function again(g,side){g.match.currentPlayerId=side;g.match.turnActive=true;g.match.playerOne.hasMadeInitialMoveForCurrentTurn=false;g.match.playerTwo.hasMadeInitialMoveForCurrentTurn=false;g.waiting=false;}
// 152307 Queensguard: free=8-count(own row incl. itself); summon up to free copies of 152307 from own graveyard into its row.
if(want(152307))for(const side of [1,2])for(const others of [0,5,7])run(152307,side,'queensguard/'+others,g=>{
 for(let i=0;i<others;i++)add(g,132403,side,2,i,30);const gr=[0,1,2].map(i=>add(g,152307,side,32,i));add(g,152307,3-side,32,0);add(g,152307,side,16,0);
 const owner=begin(g,152307,side),free=8-others,n=gr.filter(c=>snap(c).locationMask===2&&snap(c).positionPlayerId===side).length;
 check(n===Math.max(0,Math.min(3,free)),'summons min(free, graveyard copies) from own graveyard only',{n,free});check(!g.IsPending(),'no request');
});
// 200022 Summoning circle: newest placed-on-board history card that is Unit, Bronze/Silver, no Ambush token, without category 2048 -> spawn copy, play it.
if(want(200022))for(const side of [1,2])run(200022,side,'circle newest eligible',g=>{
 const a=add(g,132403,side,8,0),b=add(g,132209,3-side,8,0),c=add(g,112103,side,8,1);
 check(g.Play(side,id(a),1),'A placed');flush(g);place(g);again(g,3-side);check(g.Play(3-side,id(b),2),'B placed (enemy, silver)');flush(g);place(g);again(g,side);check(g.Play(side,id(c),4),'C placed (gold, ineligible)');flush(g);place(g);again(g,side);
 const pre=ids(g),owner=add(g,200022,side,8,0);check(g.Play(side,id(owner),2),'circle');flush(g);place(g);
 const n=fresh(g,pre).filter(s=>s.instanceId!==id(owner));check(n.length===1&&n[0].runtimeTemplate.templateId===132209&&n[0].positionPlayerId===side&&(n[0].locationMask&7),'copy of newest eligible (enemy silver) played on own side',{n:n.map(s=>[s.runtimeTemplate.templateId,s.positionPlayerId,s.locationMask])});
});
// 113201 Decoy: own Bronze/Silver unit (Ignore 1288: Ambush8|NotTargetable256|Stubborn1024) -> hand index0 -> boost CURRENT+3 -> PlayCards (placement).
if(want(113201))for(const side of [1,2])run(113201,side,'decoy',g=>{
 const u=add(g,132209,side,1,0,20,2),gold=add(g,112103,side,1,1,10),st=add(g,132403,side,2,0,30,0,1024),amb=add(g,132403,side,2,1,30,0,8),en=add(g,132403,3-side,1,0,30);
 const owner=begin(g,113201,side);check(g.IsPending()&&same(g.pendingIds,[id(u)]),'only own Bronze/Silver without Ambush/NotTargetable/Stubborn',{mod:g.pendingIds});
 check(g.SelectTarget(g.requestId,id(u)),'pick');flush(g);check(g.IsPending()&&!!g.pendingRally&&g.CanSelectRow(g.requestId,side,4),'returned unit is replayed with placement');g.SelectRow(g.requestId,side,4);flush(g);
 const s=snap(u),b=rt.definition(132209).header.power;check(s.locationMask===4&&s.power.basePower===b&&s.power.currentPower===b+3,'reset in hand, boosted +3, played to chosen row',{s:[s.locationMask],p:s.power});
});
