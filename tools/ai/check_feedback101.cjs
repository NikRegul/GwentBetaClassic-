'use strict';
const fs=require('fs');
const {rt,rebuild,positions}=require('./probe_feedback101.cjs');
const {fixture,add}=require('./audit_fixture095.cjs')(rt);
let checks=0;const failures=[],cases=[];
function check(ok,n){checks++;if(!ok)failures.push(n);}
function prepare(g){let ticks=0;while(!g.AiPreparationStep())if(++ticks>12000)throw Error('stalled');}
function act(g,staged){if(staged)prepare(g);let ok=false;for(let i=0;i<4&&!ok;i++){ok=g.OpponentStep();if(!ok)prepare(g);}check(ok&&!g.IsFatal()&&!g.IsPending(),'action resolves');}
{
 const p=positions.find(p=>p.name==='bran'&&p.begin.decision==='1'),choices=[];
 for(const changeHidden of [false,true]){
  const {g}=rebuild(p),before=JSON.stringify(g.live.map(c=>c.Snapshot())),draws=g.random.DrawCount();
  g.archetypeAI.BranBankedSetup101();
  check(JSON.stringify(g.live.map(c=>c.Snapshot()))===before&&g.random.DrawCount()===draws,'Bran setup estimate preserves cards and RNG');
  if(changeHidden)for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId===1&&[8,16].includes(s.locationMask)&&(s.tokenMask&64)===0)c.cardState.runtimeTemplate.templateId=112405;}
  const logs=[];rt.host.log=s=>logs.push(s);try{act(g,true);}finally{rt.host.log=null;}
  choices.push(logs.filter(s=>/event=(SELECT|TARGET_SELECT|TARGET_FINISH)/.test(s)));
 }
 check(JSON.stringify(choices[0])===JSON.stringify(choices[1]),'Bran setup and discard choices ignore real enemy hidden identities');
}
for(const p of positions.filter(p=>p.name==='scorch'||p.begin.decision==='1'))for(const staged of [false,true]){
 const {g,byId}=rebuild(p);const logs=[];rt.host.log=s=>logs.push(s);
 try{act(g,staged);}finally{rt.host.log=null;}
 if(p.name==='scorch'){
  check(byId.get(39).Snapshot().locationMask===8&&g.match.playerTwo.hasPassed,'last self-hitting Scorch is retained even in mandatory round');
  check(g.Score(2)===41&&g.Score(1)===43,'pass preserves the logged score instead of dropping our fifteen');
  // The user's counterfactual victory is not established: the logged board
  // is already behind. Do not turn a partial reconstruction into a win claim.
  check(g.Pass(1)&&g.Snapshot().matchWinnerMask===1,'this reconstructed pass still loses 41:43');
 }else{
  check(byId.get(53).Snapshot().locationMask!==64,'reported Bran is used while setup can still be spent');
  check(byId.get(28).Snapshot().locationMask===32,'Cerys is actually prepared in the grave');
  check(g.live.some(c=>c.TemplateId()===152309&&c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===32),'one Longship seeds the held resurrection tools');
  check(g.CountLocation(2,8)===10,'setup preserves the ten-card hand');
 }
 cases.push({name:p.name,decision:p.begin.decision,staged,logs:logs.filter(s=>/event=(LEADER_OPTION|TARGET_SELECT|TARGET_FINISH|SELECT|PASS)/.test(s))});
}
// The emergency pass guard must preserve the normal rejection, including when
// the opponent has passed. A negative spell must not reappear as a fallback.
for(const passed of [false,true]){
 const g=fixture(2);g.externalPolicyMask=0;g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.match.playerOne.hasPassed=passed;
 const spell=add(g,113310,2,8);add(g,112405,1,1,0,22);if(!passed)add(g,112405,1,8);
 act(g,true);check(spell.Snapshot().locationMask===8&&g.match.playerTwo.hasPassed,'emergency guard does not force an unbacked boost, passed='+passed);
}
// With no revival available, do not dump a gold into the grave merely to make
// the leader look active. The optional discard correctly remains unused.
{
 const g=fixture(2);g.externalPolicyMask=0;g.match.roundNumber=3;g.leaderTemplateTwo=200159;g.presetTwo=89;g.archetypeAI.Initialize(g,[],89,200159);
 const cerys=add(g,200177,2,16),bran=add(g,200159,2,64);
 check(g.UseLeader(2)&&!g.IsPending()&&!g.IsFatal(),'targetless final Bran resolves');
 check(cerys.Snapshot().locationMask===16,'no unreachable Cerys discard at end of match');
}
// Actual nested cancellation after the two-rider Scorch, including repeated
// placement and commitment. The mandatory child must neither vanish nor turn
// into a new free hand play; cancellation rewinds only its uncommitted deploy.
{
 const g=fixture(1);
 add(g,142205,2,1,0,8);add(g,142205,2,1,1,8);add(g,112405,1,4,0,7);
 add(g,112405,2,8);
 const scorch=add(g,113309,1,8),child=add(g,162308,1,16),parent=add(g,162314,1,8);
 check(g.Play(1,scorch.Snapshot().instanceId,1),'Scorch kills the two equal riders');
 check(g.Pass(2),'opponent can pass after losing riders');
 check(g.Play(1,parent.Snapshot().instanceId,1)&&g.SelectTarget(g.requestId,child.Snapshot().instanceId),'Emissary selects mandatory child');
 for(const row of [2,2,1]){
  check(g.SelectRow(g.requestId,1,row)&&g.CanCancelTargetRequest098(),'child may choose target after placement');
  check(g.CancelTargetRequest098(g.requestId,1),'cancel uncommitted target');
  check(g.pendingRally===g.FindCard(child.Snapshot().instanceId)&&g.playStack.length===1&&!g.CanAct(1),'same mandatory child returns to placement');
 }
 check(g.SelectRow(g.requestId,1,1)&&g.SelectTarget(g.requestId,g.pendingIds[0]),'mandatory child can commit after cancellation');
 check(!g.IsPending()&&!g.IsFatal()&&(g.FindCard(child.Snapshot().instanceId).Snapshot().locationMask&7)!==0,'no child is lost or duplicated');
}
const report={checks,failures,cases,fingerprint:rt.fingerprint,actualWitcherScript:true,historicalRuntimeVerified:false,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks,failures}));if(failures.length)process.exitCode=1;
