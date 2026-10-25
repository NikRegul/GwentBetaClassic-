'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const dir=path.resolve(process.argv[2]),ctx=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(dir,f),'utf8')).join('\n')+String.raw`
Host.random=()=>.37;let checks=0;
function check(v,s){if(!v)throw Error(s);checks++;console.log('PASS',s);}
for(const strength of [2,3,4]){
 Host.strength=strength;Host.matchStrength=[strength,strength];Host.tunes=[{},{}];Host.seatIndex=1;const g=new CBetaGwentDuelSession();check(g.InitializeWithPresets(54,61),'initialize '+strength);
 check((g.aiStartingDeckOne.length>0)===(strength===4),'starting-list capture is maximum-only '+strength);
 check((g.aiStartingDeckTwo.length>0)===(strength===4),'both seats have symmetric maximum-only capture '+strength);
 const before=JSON.stringify([g.aiStartingDeckOne,g.aiStartingDeckTwo]);
 let model=new CBetaGwentPublicResponseAI();model.Initialize(g,3);
 const prediction=JSON.stringify([model.templates,model.weights,model.controlChance,model.comboChance,model.publicBurst]);
 const draws=g.random.DrawCount();
 for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId===1&&(s.locationMask===8||s.locationMask===16)&&(s.tokenMask&64)===0){
  c.definition=BetaGwentDuelDefinition(201781);c.cardState.runtimeTemplate=c.definition.header;c.power.SetCurrentPair(50,9);
 }}
 model=new CBetaGwentPublicResponseAI();model.Initialize(g,3);
 check(prediction===JSON.stringify([model.templates,model.weights,model.controlChance,model.comboChance,model.publicBurst]),'predictions ignore current hidden identities/powers '+strength);
 check(before===JSON.stringify([g.aiStartingDeckOne,g.aiStartingDeckTwo]),'snapshot is not refreshed after mutations '+strength);
 check(draws===g.random.DrawCount(),'belief update does not consume live RNG '+strength);
 const flipped=new CBetaGwentCloner().CloneSession(g,++checks,true);
 check(JSON.stringify(flipped.aiStartingDeckTwo)===JSON.stringify(g.aiStartingDeckOne),'reverse clone exchanges starting lists '+strength);
 const twice=new CBetaGwentCloner().CloneSession(flipped,++checks,true);
 check(before===JSON.stringify([twice.aiStartingDeckOne,twice.aiStartingDeckTwo]),'double reverse restores starting lists '+strength);
 g.archetypeAI.planRound=2;g.archetypeAI.roundPlan=3;g.archetypeAI.planEnemyInvestment=5;g.archetypeAI.planOwnInvestment=8;
 __swap(g);
 check(JSON.stringify(g.aiStartingDeckTwo)===JSON.stringify(twice.aiStartingDeckOne),'live host swaps the starting-list seats '+strength);
 g.archetypeAI.planRound=1;g.archetypeAI.roundPlan=2;
 __swap(g);
 check(before===JSON.stringify([g.aiStartingDeckOne,g.aiStartingDeckTwo]),'host double swap restores starting lists '+strength);
 check(g.archetypeAI.planRound===2&&g.archetypeAI.roundPlan===3&&g.archetypeAI.planEnemyInvestment===5&&g.archetypeAI.planOwnInvestment===8,'host retains each seat own plan '+strength);
 if(strength<4){
  g.aiStartingDeckOne=[113309,113309,113309,113309];model=new CBetaGwentPublicResponseAI();model.Initialize(g,3);
  check(prediction===JSON.stringify([model.templates,model.weights,model.controlChance,model.comboChance,model.publicBurst]),'lower difficulty ignores any captured list '+strength);
 }
}
globalThis.result={checks,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(ctx.result,null,2));
