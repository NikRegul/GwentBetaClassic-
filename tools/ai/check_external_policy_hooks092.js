/* Exercise the shared WS engine with both seats externally controlled.
 * No Beta strength claim: these are ownership/continuation contracts. */
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]);
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
const context=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function strict(g){
 g.externalPolicyMask=3;
 for(const k of ['AiMulligan','BestTarget','BestCardRow','BestOwnRow','BestNestedRow','BestModeChoice',
  'ChooseDagonWeather','ChooseFirstLight','BestWeatherRow','BestEnemyRow','AiPileCandidateValue',
  'AiAbilityChoiceValue','AiCreatedOptionValue','BestVranAnchor','AiAdjacencyIndex'])
  g[k]=()=>{throw Error('Current policy leaked into external choice: '+k);};
 return g;
}
function ownRequest(g,side,label){
 check(g.IsPending()&&!g.IsFatal(),label+' pending');
 check(g.RequestDecisionSide()===side&&g.GetRequestSnapshot().playerId===side,label+' correct owner');
}
{
 const g=strict(new CBetaGwentDuelSession());
 check(g.InitializeWithPresets(91,56),'external initialization');
 ownRequest(g,2,'initial side2 mulligan');
 check(g.mulliganBudget===3&&g.CountLocation(1,8)===10&&g.CountLocation(2,8)===10,'both hands untouched by current AI');
 const first=g.requestId,foreign=g.live.find(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===8);
 check(!g.SelectMulligan(first,foreign.Snapshot().instanceId),'reject other hand');
 const outgoing=g.pendingIds[0];check(g.SelectMulligan(first,outgoing),'external side2 exchange');
 check(g.FindCard(outgoing).Snapshot().locationMask===16&&g.CountLocation(2,8)===10,'real exchange conserves hand');
 check(g.FinishMulligan(first),'finish side2');ownRequest(g,1,'initial side1 mulligan');
 check(g.requestId!==first&&!g.SelectMulligan(first,g.pendingIds[0]),'stale request rejected across seats');
 check(g.SelectMulligan(g.requestId,g.pendingIds[0]),'external side1 exchange');
 check(g.FinishMulligan(g.requestId)&&!g.mulligan,'both hands complete');
 check(!g.OpponentStep(),'current AI cannot act on externally controlled side2');
 const actor=g.Snapshot().currentPlayerId;check(g.Pass(actor),'first pass');
 check(g.Pass(g.Snapshot().currentPlayerId),'second pass');
 check(g.waiting&&g.BeginNextRound(),'next round');ownRequest(g,2,'later side2 mulligan');
 check(g.mulliganBudget===1,'later exchange budget');
 const cloner=new CBetaGwentCloner(),copy=cloner.CloneSession(g,901);
 check(copy.externalPolicyMask===3&&copy.mulliganSide===2,'clone preserves external request');
 check(copy.pendingIds!==g.pendingIds&&copy.random.words!==g.random.words,'clone arrays independent');
 g.externalPolicyMask=2;const reverse=cloner.CloneSession(g,902,true);g.externalPolicyMask=3;
 check(reverse.externalPolicyMask===1&&reverse.mulliganSide===1&&reverse.GetRequestSnapshot().playerId===1,'production reverse seats preserves controller ownership');
 __swap(g);check(g.mulliganSide===1&&g.GetRequestSnapshot().playerId===1,'harness reverse preserves ownership');__swap(g);
}
for(const side of [1,2])for(const tpl of [162206,162209,162309]){
 const g=strict(fixture(side));g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const enemy=add(g,142305,1,0,3-side),own=add(g,142305,1,0,side),source=add(g,tpl,8,0,side);
 add(g,142305,16,0,3-side);add(g,112101,8,0,3-side);
 check(g.Play(side,source.Snapshot().instanceId,2),'play actual target card '+tpl+'/'+side);
 ownRequest(g,side,'target '+tpl+'/'+side);
 const target=tpl===162309?own:enemy;
 check(g.pendingIds.includes(target.Snapshot().instanceId),'legal target retained');
 check(g.SelectTarget(g.requestId,target.Snapshot().instanceId)&&!g.IsFatal(),'explicit target resolution');
}
for(const side of [1,2]){
 const g=strict(fixture(side)),victim=add(g,112101,1,0,side,3),consumer=add(g,201701,8,4,side);
 check(g.Play(side,consumer.Snapshot().instanceId,2),'play consumer '+side);ownRequest(g,side,'consume '+side);
 check(g.SelectTarget(g.requestId,victim.Snapshot().instanceId),'explicit meal');
 check(victim.Snapshot().locationMask===32&&!g.IsPending(),'consume finishes without current selector');
}
for(const side of [1,2]){
 const g=strict(fixture(side)),spell=add(g,113301,8,4,side),victim=add(g,112101,1,0,3-side);
 check(g.Play(side,spell.Snapshot().instanceId,1),'play damage spell '+side);ownRequest(g,side,'damage '+side);
 check(g.SelectTarget(g.requestId,victim.Snapshot().instanceId)&&!g.IsPending(),'explicit damage target');
}
for(const side of [1,2]){
 const g=strict(fixture(side)),leader=add(g,200169,64,0,side),anchor=add(g,112101,2,0,side);
 check(g.UseLeader(side),'request leader placement '+side);ownRequest(g,side,'leader '+side);
 check(!g.SelectRow(g.requestId,3-side,2),'leader rejects wrong side');
 check(g.SelectPlacementBefore(g.requestId,anchor.Snapshot().instanceId),'leader explicit insertion');
 check(leader.Snapshot().locationMask===2&&leader.Snapshot().locationIndex===0&&!g.IsFatal(),'leader insertion applied');
}
for(const side of [1,2])for(const nested of [false,true]){
 const g=strict(fixture(side)),enemy=add(g,112101,1,0,3-side,15);
 const caster=add(g,113208,nested?16:8,0,side);
 if(nested){
  const order=add(g,200019,8,6,side);check(g.Play(side,order.Snapshot().instanceId,1),'nested caster '+side);
  ownRequest(g,side,'nested placement '+side);check(g.IsRallyRowRequest(),'nested card waits for placement');
  check(g.SelectRow(g.requestId,side,1),'explicit nested caster row');
 }else check(g.Play(side,caster.Snapshot().instanceId,1),'direct caster '+side);
 ownRequest(g,side,'template choice '+side);
 check(g.SelectTemplateChoice(g.requestId,113301),'explicit created spell');ownRequest(g,side,'created spell target '+side);
 check(g.SelectTarget(g.requestId,enemy.Snapshot().instanceId),'explicit created spell target');
 check(enemy.Snapshot().power.currentPower===6&&!g.IsPending()&&!g.IsFatal(),'compound play completed by external choices');
}
for(const side of [1,2]){
 const g=strict(fixture(side)),spell=add(g,113305,8,4,side);
 add(g,112101,1,0,3-side,15);
 check(g.Play(side,spell.Snapshot().instanceId,1),'weather spell '+side);ownRequest(g,side,'weather row '+side);
 check(!g.SelectRow(g.requestId,side,2),'weather rejects friendly row');
 check(g.SelectRow(g.requestId,3-side,2)&&!g.IsPending()&&!g.IsFatal(),'explicit enemy weather row');
}
globalThis.report={checks,scope:'Shared-engine external decision ownership, initial/later mulligans, clone/reverse, real target/consume/damage/leader/template/weather/compound-play continuations.',
 betaPolicyUsed:false,nativeGameplayVerified:false};
`,context,{filename:'external-policy-hooks.bundle.js',timeout:180000});
const report={...context.report,fingerprint:JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8')).fingerprint};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
