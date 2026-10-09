// Researched deck and economy reproductions against the actual frozen WS.
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const code=['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n');
vm.runInContext(code+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
let checks=0;
function check(ok,label){if(!ok)throw Error(label);checks++;console.log('PASS',label);}
function fixture(preset=63){const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(preset,preset))throw Error('invalid preset');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;
 g.weatherProfile=false;g.match.currentPlayerId=2;g.match.turnActive=true;g.match.roundActive=true;g.match.roundNumber=1;
 g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;g.recordVisuals=false;
 add(g,112101,8,0,1);add(g,112101,8,1,1);return g;}
function add(g,t,zone,index=0,side=2,power){const id={v:0};g.registry.Allocate(id);const c=new CBetaGwentDuelCard();
 c.Setup(g,id.v,t,side,zone,index);if(power!==undefined){c.cardState.power.currentPower=power;c.power.currentPower=power;}
 g.registry.Put(id.v,c);g.live.push(c);return c;}
{
 const pool={v:[]};BetaGwentAIProfileIds(pool);
 const presets=pool.v.map(p=>{for(let n=54;n<=99;n++)if(BetaGwentAIPresetProfile(n)===p)return n;throw Error('missing profile '+p);});
 check(pool.v.length===46 && new Set(presets).size===46,'all 46 profiles have distinct playable presets');
 check(presets.every(n=>{const d={v:[]};return BetaGwentDuelPresetDeck(n,d)&&d.v.length===(n===83?40:25);}), 'all exact deck sizes are legal, including the forty-card list');
 check([10,12,33,42,43,44].every((p,i)=>BetaGwentAIPresetProfile(94+i)===p),'six Beta adaptations use new IDs, preserving old saved identities');
 check(BetaGwentAIEngine(162307)===0,'Impera Brigade has deployment value, no invented future ticks');
}
{
 const g=fixture(),witcher=add(g,200124,8),enemy=add(g,112101,1,0,1,30);
 const alchemy=g.NilfAlchemy(2);
 check(alchemy===12,'researched Alchemy begins with twelve Alchemy cards');
 const before=enemy.Snapshot().power,gain=g.AiSimPlay(witcher.cardState.instanceId);
 check(gain!==-2147483647 && enemy.Snapshot().power.currentPower===before.currentPower-Math.max(0,12-before.armor),'Viper resolves starting-deck damage with real enemy armour');
}
{
 const g=fixture(),witcher=add(g,200124,1),trial=add(g,200078,8);
 g.AiSimPlay(trial.cardState.instanceId);
 check(witcher.Snapshot().power.currentPower===25,'Trial of the Grasses sets a live Witcher to 25');
}
{
 const g=fixture(),novice=add(g,122403,8);add(g,113311,16);g.archetypeAI.Refresh();
 const empty=g.archetypeAI.Priority(novice.Definition());
 add(g,112101,1);add(g,112101,1,1);add(g,112101,1,2);g.archetypeAI.Refresh();
 check(g.archetypeAI.Priority(novice.Definition())>empty,'Novice prefers a table with working Alchemy targets');
 const eye=add(g,200224,8);g.archetypeAI.Refresh();
 check(g.archetypeAI.Mulligan(eye)>0,'Novice opening returns drawn bronze Alchemy to its deck');
}
{
 const g=fixture(81),ithlinne=add(g,142107,8),thunder=add(g,113301,8,1);g.archetypeAI.Refresh();
 check(g.archetypeAI.Mulligan(thunder)>0,'return the only Alzur Thunder when Ithlinne is held');
 const empty=g.archetypeAI.Priority(ithlinne.Definition());thunder.Move(2,16,0);g.archetypeAI.Refresh();
 check(g.archetypeAI.Priority(ithlinne.Definition())>empty,'Ithlinne waits until its legal spell is available');
}
{
 const g=fixture(63),cahir=add(g,162104,8);g.archetypeAI.Refresh();const before=g.archetypeAI.Priority(cahir.Definition());
 add(g,g.LeaderTemplateId(2),32);g.archetypeAI.Refresh();
 check(g.archetypeAI.Priority(cahir.Definition())>before,'Cahir waits for the real leader in its own grave');
}
{
 const g=fixture(94),mage=add(g,201628,8);g.archetypeAI.Refresh();const before=g.archetypeAI.Priority(mage.Definition());
 // A bronze Item other than the three previously hard-coded names is valid.
 add(g,201619,16);g.archetypeAI.Refresh();
 check(BetaGwentNorthernCategory(201619,9) && g.archetypeAI.Priority(mage.Definition())>before,'Tormented Mage accepts any actual bronze Item in its deck');
}
{
 const g=fixture(59),mangonel=add(g,162317,8),menno=add(g,162102,8,1);g.archetypeAI.Refresh();
 const before=g.archetypeAI.Priority(mangonel.Definition());menno.Move(2,512,0);add(g,162316,8);g.archetypeAI.Refresh();
 check(g.archetypeAI.Priority(mangonel.Definition())>before,'Mangonel prepares real Reveal sources rather than Menno');
}
{
 const g=fixture(67),a=add(g,132305,8),b=add(g,132305,8,1),warrior=add(g,132211,8,2);g.archetypeAI.Refresh();
 check(g.archetypeAI.Mulligan(a)>0,'return extra Nekkers rather than all opening seeds');
 const before=g.archetypeAI.Priority(warrior.Definition());a.Move(2,1,0);g.archetypeAI.Refresh();
 check(g.archetypeAI.Priority(warrior.Definition())>before,'Nekker Warrior copies a live seed instead of opening on an empty field');
 check(g.archetypeAI.MulliganKeepBonus(b)>0,'one useful Nekker seed receives mulligan protection');
}
{
 const g=fixture(56),behemoth=add(g,132201,8);add(g,132305,8,1);g.archetypeAI.Refresh();
 const before=g.archetypeAI.Priority(behemoth.Definition());add(g,132308,8,2);g.archetypeAI.Refresh();
 check(g.archetypeAI.Priority(behemoth.Definition())>before,'Behemoth needs an actual consumer; passive Nekker is not one');
}
{
 check(BetaGwentAIRoundDecision(1,0,0,-20,5,5,7,10,false,false,0)===2,'tempo policy concedes an expensive optional first round');
 check(BetaGwentAIRoundDecision(1,0,0,-20,5,5,7,10,false,true,2)===0,'long-round policy preserves a live engine position at moderate deficit');
 check(BetaGwentAIRoundDecision(2,1,0,-15,3,4,5,10,false,true,1)===2,'stop a bleed before wasting the deciding-round hand');
 check(BetaGwentAIRoundDecision(2,0,1,-40,3,5,5,10,false,false,0)===0,'mandatory second round overrides conservation');
 check(BetaGwentAIRoundDecision(3,1,1,-40,3,5,5,10,false,false,0)===0,'deciding round overrides conservation');
 check(BetaGwentAIChasePassReason(true,1,1,6,3,0,0)===0,'a second chase card requires real card advantage and three reserves');
 check(BetaGwentAIChasePassReason(true,1,2,6,3,0,0)>0,'a third optional chase card is rejected cumulatively');
}
{
 const g=fixture(),leader=add(g,200168,64);g.match.playerOne.hasPassed=true;g.aiChaseRound=1;
 g.AiSimPlay(leader.cardState.instanceId);
 check(g.aiChaseSpent===0 && leader.playFromLocation===64,'deploying a normal leader is not a hand card');
}
{
 const g=fixture(),leader=add(g,200162,64);add(g,112101,8);add(g,132305,1);g.match.playerOne.hasPassed=true;g.aiChaseRound=1;
 g.AiSimPlay(leader.cardState.instanceId);
 check(g.aiChaseSpent===1,'Emhyr separately counts the nested card played from hand');
}
{
 const g=fixture(),spy=add(g,162210,8);add(g,112101,16);add(g,112101,16,0,1);
 g.match.playerOne.hasPassed=true;g.aiChaseRound=1;g.aiChaseSpent=1;
 g.AiSimPlay(spy.cardState.instanceId);
 check(g.aiChaseSpent===2,'a drawing spy cannot erase already spent chase cards');
 g.aiChaseSpent=7;__swap(g);g.aiChaseSpent=3;__swap(g);check(g.aiChaseSpent===7,'self-play preserves cumulative chase independently for both seats');
}
console.log(JSON.stringify({stage:115,checks,actualWitcherScript:true}));
`,context,{filename:'scenarios115.bundle.js',timeout:180000});
