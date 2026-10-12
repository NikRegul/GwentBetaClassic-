// Contextual mulligan, complete-hand concession and actual spy activation.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clear(g,side,zone=8){g.live.filter(c=>c.Snapshot().positionPlayerId===side&&c.Snapshot().locationMask===zone).forEach(c=>c.Move(side,512,0));}
{
 const g=fixture(),dwarfTutor=add(g,142207,8,4),sage=add(g,201676,8,5);
 add(g,142316,16,0);check(g.AiTutorTargetCount(dwarfTutor)===0,'non-Dwarf unit cannot satisfy a Dwarf tutor');
 check(g.AiTutorTargetCount(sage)===0,'ordinary unit cannot satisfy an Item tutor');
 add(g,113311,16,1);check(g.AiTutorTargetCount(sage)===1,'eligible Bronze Item satisfies Sage');
}
for(const round of [1,2,3]){
 const g=fixture();clear(g,2);g.match.roundNumber=round;
 const elf=add(g,142308,8),unit=add(g,142316,16);
 add(g,113101,16,1); // Gold special is not in Mercenary's bronze pool.
 check(g.AiTutorTargetCount(elf)===0,'Mercenary has no eligible bronze specials '+round);
 check(g.AiCardKeepValue(elf)<=1,'empty tutor is valued by its body '+round);
 g.AiMulligan(1);
 check(elf.Snapshot().locationMask===16&&unit.Snapshot().locationMask===8,'empty tutor is actually replaced '+round);
}
{
 const g=fixture(),elf=add(g,142308,8,4),special=add(g,113311,16);
 check(g.AiTutorTargetCount(elf)===1&&g.AiTutorMulliganPriority(elf)===0,'eligible bronze special preserves tutor ability');
 special.Move(2,32,0);check(g.AiTutorTargetCount(elf)===0,'graveyard special cannot satisfy a deck tutor');
 special.Move(1,16,0);check(g.AiTutorTargetCount(elf)===0,'opponent deck cannot satisfy a friendly tutor');
}
{
 const g=fixture();clear(g,2);const thunder=add(g,113311,8);
 check(g.AiCardKeepValue(thunder)===0,'Thunder alone has no guaranteed bodies');
 add(g,142316,8,1);check(g.AiCardKeepValue(thunder)<=3,'one body caps Thunder at one boost');
 add(g,142316,8,2);check(g.AiCardKeepValue(thunder)<=6,'two bodies cap Thunder below full value');
 add(g,142316,8,3);check(g.AiCardKeepValue(thunder)>6,'three bodies support full Thunder');
}
{
 const g=fixture();clear(g,2);const thunder=add(g,113311,8),spawn=add(g,132310,8,1);
 spawn.definition.deploySpawnTemplate=132312;spawn.definition.deploySpawnCount=2;
 check(g.AiMulliganBodies(thunder)===3,'known created bodies count for a short hand');
}
{
 const g=fixture();clear(g,2);add(g,112101,1,0,1,35);add(g,142316,8,0,2,7);add(g,142316,8,1,2,7);
 check(g.AiRoundOneUnreachable(),'whole ordinary hand cannot close a 35 point gap');
 check(g.OpponentStep()&&g.match.playerTwo.hasPassed&&g.CountLocation(2,8)===2,'AI concedes round one without wasting either card');
}
{
 const g=fixture();clear(g,2);add(g,112101,1,0,1,30);for(let i=0;i<3;i++)add(g,142316,8,i,2,12);
 check(!g.AiRoundOneUnreachable(),'whole hand can catch up even if two cards cannot');
 const leader=add(g,142316,64,0,2,40);clear(g,2);
 check(!g.AiRoundOneUnreachable(),'available leader counts toward catch-up');
 leader.SetPlayable(false);check(g.AiRoundOneUnreachable(),'spent leader has no phantom catch-up value');
 for(const r of [2,3]){g.match.roundNumber=r;check(!g.AiRoundOneUnreachable(),'first-round concession policy disabled in round '+r);}
}
{
 const g=fixture();clear(g,2);add(g,112101,1,0,1,2);const right=add(g,112101,1,1,1,15);
 add(g,112101,2,0,1,8);add(g,112101,2,1,1,3);const fringilla=add(g,162205,8);
 const row={v:0},index={v:0},gain={v:0};
 check(g.AiFringillaSlot(2,row,index,gain)&&row.v===1&&index.v===1&&gain.v===13,'Fringilla finds the useful ordered pair');
 check(g.PlayBefore(2,fringilla.Snapshot().instanceId,right.Snapshot().instanceId),'Fringilla plays between chosen neighbours');
 check(right.Snapshot().power.currentPower===2,'Fringilla actually copies left power to the right');
}
{
 const g=fixture();clear(g,2);const iris=add(g,112215,8);for(let i=0;i<5;i++)add(g,142316,1,i,2,4);
 check(g.AiSpyActivationValue(iris)===-2147483647,'Iris without a killing plan is rejected');
 add(g,113301,8,1);
 check(g.AiSpyActivationValue(iris)>0,'Iris with actual removal has a profitable deathwish plan');
 check(g.OpponentStep()&&iris.Snapshot().locationMask!==8,'AI deploys a prepared Iris combo');
 g.FinishTurn();check(g.OpponentStep()&&iris.Snapshot().locationMask===32&&g.Score(2)===45,'AI follows through, kills Iris and boosts its five units');
}
{
 const g=fixture();clear(g,2);for(let i=0;i<3;i++)add(g,142316,1,i,1,[1,12,15][i]);
 add(g,142316,2,0,1,4);add(g,142316,2,1,1,5);
 const sabrina=add(g,122206,8);add(g,113301,8,1);
 check(g.AiBestSpyRow(2,sabrina.Definition())===1,'Sabrina chooses the row with greatest reset payoff');
 check(g.AiSpyActivationValue(sabrina)>0,'Sabrina is valued through actual kill and reset');
}
globalThis.followupsReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'followups126.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.followupsReport,null,2)+'\n');
