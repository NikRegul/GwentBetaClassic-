// Reproductions of ship placement, discarded Cerys and split power/armour cues.
// Execute the actual frozen WitcherScript rules; no substitute card effects.
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const code=['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n');
vm.runInContext(code+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
function fixture(){const g=new CBetaGwentDuelSession();g.InitializeWithPresets(89,89);
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.waiting=false;
 g.weatherProfile=false;g.match.currentPlayerId=2;g.match.turnActive=true;g.match.roundActive=true;
 g.match.roundNumber=2;g.match.playerOne.hasPassed=false;g.recordVisuals=false;return g;}
function add(g,t,zone,index,side=2){const id={v:0};g.registry.Allocate(id);const c=new CBetaGwentDuelCard();
 c.Setup(g,id.v,t,side,zone,index);g.registry.Put(id.v,c);g.live.push(c);return c;}
function check(ok,label){if(!ok)throw Error(label);console.log('PASS',label);}
{
 const g=fixture(),partner=add(g,200040,2,0),ship=add(g,152309,8,0);
 const row=g.BestCardRow(2,ship.Definition());
 check(row===2 && g.AiPlacementAnchor(ship.Definition())===partner.cardState.instanceId,'Dimun selects cursed partner row and inserts before it');
 check(g.AiAdjacencyIndex(ship,row)===0,'nested Dimun uses the same insertion index');
 g.PlayBefore(2,ship.cardState.instanceId,partner.cardState.instanceId);
 check(ship.cardState.locationIndex===0 && partner.cardState.locationIndex===1,'actual ship placement leaves partner on the right');
}
{
 const g=fixture(),ship=add(g,152309,1,0),unit=add(g,200040,8,0);
 const row=g.BestCardRow(2,unit.Definition());
 check(row===1 && g.AiAdjacencyIndex(unit,row)===1,'a new partner activates an orphan Dimun by standing on its right');
}
{
 const g=fixture();add(g,200040,1,0);g.weather.hazards[3]=1;add(g,200040,4,0);
 const ship=add(g,152309,8,0);
 check(g.BestCardRow(2,ship.Definition())===4,'equivalent ship partners prefer the safe row');
}
{
 const g=fixture(),left=add(g,112101,2,0),right=add(g,200040,2,1),holger=add(g,152109,8,0);
 check(g.BestCardRow(2,holger.Definition())===2 && g.AiAdjacencyIndex(holger,2)===1,'Holger strengthens left neighbour and damages cursed unit on right');
}
{
 const g=fixture(),cerys=add(g,200177,16,0);g.archetypeAI.Refresh();
 check(g.archetypeAI.DiscardValue(cerys)===60,'Cerys remains a preferred discard setup');
 const leader=add(g,200159,64,0);g.archetypeAI.Refresh();
 check(g.archetypeAI.LeaderPriority(leader.Definition())>0,'Bran gets early setup priority while Cerys is still in the deck');
 cerys.Move(2,32,0);g.archetypeAI.Refresh();
 check(g.archetypeAI.LeaderPriority(leader.Definition())===0,'no early Bran priority without useful discard targets');
 add(g,152316,16,1);g.archetypeAI.Refresh();
 check(g.archetypeAI.LeaderPriority(leader.Definition())>0,'self-returning unit makes Bran an early setup');
 g.match.playerOne.hasPassed=true;g.archetypeAI.Refresh();
 check(g.archetypeAI.LeaderPriority(leader.Definition())===0,'setup bonus never masquerades as catch-up points after a pass');
}
{
 const g=fixture(),leader=add(g,200159,64,0);
 add(g,152209,16,0);add(g,152316,16,1);add(g,200177,16,2);
 add(g,122104,8,0);add(g,122104,8,1);add(g,152310,8,2);
 add(g,112101,8,0,1);g.archetypeAI.Refresh();
 check(g.OpponentStep() && !leader.cardState.canBePlayed && g.CountLocation(2,8)>=2,'actual opponent uses Bran for preparation before spending its last hand cards');
}
{
 const g=fixture(),source=add(g,113311,8,0),targets=[add(g,122104,2,0),add(g,122104,2,1),add(g,122104,2,2)];
 g.recordVisuals=true;g.visualFrames=[];
 check(g.Play(2,source.cardState.instanceId,1) && !g.IsPending(),'actual Thunder resolves the AI target choice');
 const frames=g.visualFrames.filter(f=>f.kind===2 && f.sourceId===source.cardState.instanceId);
 check(frames.length===1 && frames[0].attackCount===3 && targets.every(t=>t.power.GetCurrentArmor()===2 && t.power.currentPower===4),'actual Thunder applies three complete buffs in one visual frame');
}
{
 const g=fixture(),source=add(g,112101,1,0),targets=[add(g,122104,2,0),add(g,122104,2,1),add(g,122104,2,2)];
 g.recordVisuals=true;g.visualFrames=[];g.SetVisualSource(source.cardState.instanceId,source.TemplateId(),2,1);
 for(const t of targets){g.QueuePower(t,3,false);g.QueueArmor(t,2);}
 g.FlushEffects();const frames=g.visualFrames.filter(f=>f.kind===2);
 check(!g.fatal && frames.length===1 && frames[0].attackCount===3,'multi-target boost and armour share one visual impact');
 check(targets.every(t=>t.power.currentPower===t.definition.header.power+3 && t.power.GetCurrentArmor()===2),'all target power and armour values apply');
}
{
 const g=fixture(),source=add(g,112101,1,0),target=add(g,122104,2,0);
 g.recordVisuals=true;g.visualFrames=[];g.SetVisualSource(source.cardState.instanceId,source.TemplateId(),2,1);
 g.MonsterOperation(source,target,12,2,7);g.QueueArmor(target,2,source);g.FlushEffects();
 check(g.visualFrames.filter(f=>f.kind===2).length===1,'permanent strength plus armour is also a single impact');
}
{
 const g=fixture(),source=add(g,112101,1,0),ship=add(g,200042,2,0);
 g.recordVisuals=true;g.visualFrames=[];g.SetVisualSource(source.cardState.instanceId,source.TemplateId(),2,1);
 g.MonsterPower(source,ship,-1);g.FlushEffects();const frames=g.visualFrames.filter(f=>f.kind===2);
 check(frames.length===2 && frames[0].sourceId===source.cardState.instanceId && frames[1].sourceId===ship.cardState.instanceId,'reactive drakkar boost originates from itself, not the previous attacker');
}
{
 const starter={v:[]},opponent={v:[]},profiles={v:[]};
 BetaGwentDuelPresetDeck(16,starter);BetaGwentDuelPresetDeck(80,opponent);BetaGwentAIProfileIds(profiles);
 check(JSON.stringify(opponent.v)===JSON.stringify(starter.v) && BetaGwentDuelPreset(80).leaderTemplateId===BetaGwentDuelPreset(16).leaderTemplateId,'FrostWraiths uses the exact approved Wild Hunt starter, including its leader');
 check(profiles.v.length===46 && BetaGwentAIPresetProfile(80)===29,'expanded pool retains old identities and contains all 46 researched archetypes');
}
`,context,{filename:'scenarios114.bundle.js',timeout:120000});
