// Spawn/passive and empty-target AI reproductions against the frozen real WS.
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const code=['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n');
vm.runInContext(code+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
let checks=0;
function check(ok,label){if(!ok)throw Error(label);checks++;console.log('PASS',label);}
function fixture(){const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(54,56))throw Error('fixture initialization');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;
 g.weatherProfile=false;g.match.currentPlayerId=2;g.match.turnActive=true;g.match.roundActive=true;g.match.roundNumber=1;
 g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;g.recordVisuals=false;return g;}
function add(g,t,side,zone,index=0){const id={v:0};g.registry.Allocate(id);const c=new CBetaGwentDuelCard();c.Setup(g,id.v,t,side,zone,index);
 g.registry.Put(id.v,c);g.live.push(c);return c;}
function spawn(g,source,t,side,row){const p=source.Snapshot();p.positionPlayerId=side;p.locationMask=row;p.locationIndex=-3;
 g.QueueSpawn(p,t,1);check(g.FlushEffects()&&!g.fatal,'spawn queue resolves '+t);}
{
 const g=fixture(),e=add(g,162308,2,1),b=add(g,162307,2,1,1),rot=add(g,162302,2,2);
 const before=b.Snapshot().power.currentPower;spawn(g,rot,162402,1,2);
 const cow=g.live.find(c=>c.TemplateId()===162402&&(c.Snapshot().locationMask&7)!==0);
 check(cow&&(cow.Snapshot().tokenMask&128)!==0,'created Cow Carcass has Spying');
 check(e.nilfCounter===1,'one created spy counts exactly once for Impera Enforcers');
 check(b.Snapshot().power.currentPower===before+2,'created spy boosts Impera Brigade once');
 g.monsters.NilfTrigger(6,rot.Snapshot());
 check(e.nilfCounter===0&&g.nilfJobs.filter(j=>j.source===e&&j.kind===4).length===1,'end-turn queues one Enforcer shot and clears its counter');
}
{
 const g=fixture(),e=add(g,162308,2,1),rot=add(g,162302,2,2);g.match.currentPlayerId=1;
 spawn(g,rot,162402,1,2);check(e.nilfCounter===0,'spy created outside Enforcer owner turn does not queue damage');
}
{
 const g=fixture(),e=add(g,162308,2,1);e.AddLock();const rot=add(g,162302,2,2);
 spawn(g,rot,162402,1,2);check(e.nilfCounter===0,'locked Enforcer ignores created spies');
}
{
 const g=fixture(),e=add(g,162308,2,1),rot=add(g,162302,2,2);
 spawn(g,rot,132403,1,2);check(e.nilfCounter===0,'ordinary created token is not a spy trigger');
}
{
 const g=fixture(),s=add(g,201618,2,8),other=add(g,112101,2,8,1);add(g,112101,1,8);
 check(g.AiDeferEmptyDuel(s.Definition(),2),'save Seltkirk when the opposing field is empty and another play exists');
 g.archetypeAI.Refresh();check(g.OpponentStep()&&s.Snapshot().locationMask===8,'actual AI does not open with targetless Seltkirk');
}
{
 const g=fixture(),s=add(g,201618,2,8);add(g,112101,2,8,1);add(g,112101,1,1);
 check(!g.AiDeferEmptyDuel(s.Definition(),2),'a legal enemy duel target releases Seltkirk');
 g.match.playerOne.hasPassed=true;g.live.find(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===1).Move(1,512,0);
 check(!g.AiDeferEmptyDuel(s.Definition(),2),'body-only Seltkirk remains available for proven catch after a pass');
}
{
 check(BetaGwentAIProfileLeader(3)===201743&&BetaGwentDuelPreset(56).leaderTemplateId===201743,'Arachas Swarm uses Arachas Queen in catalogue and profile');
 const g=fixture(),q=add(g,201743,2,1),behemoth=add(g,132201,2,2),food=add(g,132403,2,1,1);
 behemoth.cardState.timerValue=4;g.archetypeAI.Refresh();
 check(g.AiAbilityChoiceValue(q,behemoth,0)>g.AiAbilityChoiceValue(q,food,0),'friendly consume score preserves charged Behemoth before expendable food');
 const before=g.live.filter(c=>c.TemplateId()===200174&&(c.Snapshot().locationMask&7)!==0).length;
 g.QueueConsume(q,food);g.FlushDeaths();check(!g.fatal,'Queen consume resolves');
 const after=g.live.filter(c=>c.TemplateId()===200174&&(c.Snapshot().locationMask&7)!==0).length;
 check(after===before+1&&behemoth.Snapshot().timerValue===3,'each Queen consume creates a young Arachas without a deck copy and spends one charge');
}
console.log(JSON.stringify({stage:118,checks,actualWitcherScript:true}));
`,context,{filename:'scenarios118.bundle.js',timeout:180000});
