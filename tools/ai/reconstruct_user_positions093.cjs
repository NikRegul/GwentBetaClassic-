// Rebuild logged card fields, without claiming unlogged engine/queue state.
'use strict';
const fs=require('fs'),path=require('path');
const {createRuntime}=require('./beta_js092/session.cjs');
const fixtureRoot=path.resolve(__dirname,'fixtures/user093');
function rebuild(runtime,p){
 const g=runtime.newSession(),preset=Number(p.head.presetTwo);
 if(!g.InitializeWithPresets(21,preset))throw Error('Fixture initialisation');
 const Registry=g.registry.constructor;g.registry=new Registry();g.registry.Initialize();g.live.Clear();g.dying.Clear();g.playStack.Clear();
 g.recordVisuals=false;g.visualFrames.Clear();g.mulligan=false;g.waiting=false;g.pendingCard=null;g.pendingLeader=null;g.pendingIds.Clear();
 g.pendingRally=null;g.pendingChoice=false;g.pendingPileChoice=false;g.pendingHandPower=false;
 for(const c of p.cards){
  let allocated={v:0};do {g.registry.Allocate(allocated);}while(allocated.v<c.id);
  if(allocated.v!==c.id)throw Error('Logged registry order');
  const card=runtime.newCard();card.Setup(g,c.id,c.template,c.side,c.zone,c.index);
  card.cardState.ownerId=c.owner;card.cardState.tokenMask=c.tokens;card.cardState.timerValue=c.timer;card.cardState.runtimeTierMask=c.tier;
  card.power.basePower=c.base;card.power.permanentPower=0;card.power.currentPower=c.power;card.power.currentArmor=c.armor;
  card.cardState.canBePlayed=Boolean(c.playable);g.registry.Put(c.id,card);g.live.PushBack(card);
 }
 const m=g.match;m.roundNumber=Number(p.head.round);m.currentPlayerId=2;m.roundActive=true;m.turnActive=true;
 const crowns=p.head.crowns.split(',').map(Number),passed=p.head.passed.split(',').map(Number);
 m.playerOne.crowns=crowns[0];m.playerTwo.crowns=crowns[1];m.playerOne.hasPassed=Boolean(passed[0]);m.playerTwo.hasPassed=Boolean(passed[1]);
 g.presetOne=Number(p.head.presetOne);g.presetTwo=preset;g.aiSimDamp=p.damp;
 g.aiStartingDeckOne.Clear();for(const t of p.head.known.split(',').filter(Boolean).map(Number))g.aiStartingDeckOne.PushBack(t);
 if(p.head.weather.split(',').filter(Boolean).some(Number))throw Error('Weather needs explicit reconstruction');
 if(g.Score(1)!==Number(p.begin.enemyScore)||g.Score(2)!==Number(p.begin.ownScore))throw Error('Rebuilt scores differ from the user log');
 return g;
}
function run(snapshot,output){
 const runtime=createRuntime(path.resolve(snapshot)),records=[];
 for(const [name,sourceId] of [['cantarella-ambassador',23],['greatsword-damage',35]]){
  const p=JSON.parse(fs.readFileSync(path.join(fixtureRoot,name+'.json'),'utf8')),g=rebuild(runtime,p),logs=[];
  runtime.host.log=s=>logs.push(s);const source=g.FindCard(sourceId),template=source.TemplateId();
  const ok=g.Play(2,sourceId,1);runtime.host.log=null;
  if(!ok||g.IsFatal()||g.IsPending())throw Error('Actual target request did not resolve: '+g.GetMessage());
  const chosen=logs.find(s=>s.includes('event=TARGET_SELECT source='+template+' '));
  records.push({name,template,ok,chosen,score:[g.Score(1),g.Score(2)],choices:logs.filter(s=>s.includes('event=TARGET_OPTION'))});
 }
 const report={fingerprint:runtime.fingerprint,scope:'Logged public card-field reconstruction; matching logged scores, not a claim of complete historical runtime replay.',records};
 if(output)fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}
module.exports={rebuild,fixtureRoot};
if(require.main===module)run(process.argv[2],process.argv[3]);
