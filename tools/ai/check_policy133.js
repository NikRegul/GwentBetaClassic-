// Regression corpus from the 1.0 audit: rules, hidden-information invariance,
// bounded search diversity and public resource/reply policies. Emit replayable decisions.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const decisions=[];
for(const power of [1,40])for(const template of [142306,142307]){
 const g=fixture(),hidden=add(g,template,4,0,1,power);hidden.AddTokens(8);
 check(g.TargetValue(hidden.Snapshot(),2,18,0,true)===0,'Morvudd cannot count hidden power as public tempo '+template+'/'+power);
 check(g.TargetValue(hidden.Snapshot(),2,18,0,false)===2,'Morvudd uses one public ambush lock prior '+template+'/'+power);
 check(g.AiDamageChoice(hidden.Snapshot(),2,50,false)===0,'damage forecast never reads hidden armor or deathwish '+template+'/'+power);
 check(g.AiEngineValue(hidden.Snapshot(),2)===0,'hidden ambush ability never enters engine forecast '+template+'/'+power);
}
function clearHand(g,side=2){g.live.filter(c=>c.cardState.positionPlayerId===side&&c.cardState.locationMask===8).forEach(c=>c.Move(side,512,0));}
for(const caster of [1,2])for(const hiddenPower of [1,40]){
 const g=fixture(caster),low=add(g,112101,1,0,1,5),strong=add(g,112101,2,0,2,10),hidden=add(g,142306,4,0,1,hiddenPower),spell=add(g,113308,8,4,caster);hidden.AddTokens(8);low.AddTokens(256);low.power.AddArmor(30);
 check(g.Play(caster,spell.cardState.instanceId,1),'Epidemic resolves '+caster+'/'+hiddenPower);
 check(low.Snapshot().locationMask===32&&strong.Snapshot().locationMask===2&&hidden.Snapshot().locationMask===4,'Epidemic ignores ambush, includes immune and bypasses armor '+caster+'/'+hiddenPower);
 check(!g.IsFatal()&&!g.IsPending(),'Epidemic finishes safely '+caster+'/'+hiddenPower);
}
for(const caster of [1,2]){
 const g=fixture(caster),a=add(g,112101,1,0,1,5),b=add(g,112101,2,0,2,5),c=add(g,112101,4,0,2,10),spell=add(g,113308,8,4,caster);
 check(g.Play(caster,spell.cardState.instanceId,1)&&a.Snapshot().locationMask===32&&b.Snapshot().locationMask===32&&c.Snapshot().locationMask===4,'Epidemic destroys all weakest ties across both sides '+caster);
}
{
 const g=fixture(),hidden=add(g,142306,4,0,1,1),spell=add(g,113308,8,4);hidden.AddTokens(8);
 check(g.Play(2,spell.cardState.instanceId,1)&&hidden.Snapshot().locationMask===4&&!g.IsFatal(),'Epidemic with only hidden targets does nothing');
}
// This fixture previously selected different cards on easy solely from hidden power.
for(const strength of [2,3,4])for(const seed of [331,982451653,2026101233]){
 const selected=[];
 for(const hiddenPower of [1,40]){
  Host.strength=strength;Host.random=()=>.37;
  const g=fixture();clearHand(g);g.random.Initialize(seed);g.match.roundNumber=3;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=1;
  add(g,112101,1,0,1,5);add(g,112101,2,0,2,10);const hidden=add(g,142306,4,0,1,hiddenPower);hidden.AddTokens(8);
  const epi=add(g,113308,8,0),body=add(g,112101,8,1,2,2),logs=[];
  check(g.EpidemicValue(2)===5&&g.AiExactTempo(epi)===5,'heuristic and exact Epidemic agree on public targets '+strength+'/'+seed+'/'+hiddenPower);
  Host.log=s=>logs.push(s);check(g.OpponentStep()&&!g.IsFatal(),'full decision succeeds '+strength+'/'+seed+'/'+hiddenPower);Host.log=null;
  const pick=epi.Snapshot().locationMask!==8?113308:body.Snapshot().locationMask!==8?112101:0;selected.push(pick);
  check([113308,112101].includes(pick),'reasonable decision remains within declared alternatives');
  decisions.push({case:'epidemic_hidden_power',strength,seed,hiddenPower,allowed:[113308,112101],selected:pick,reason:logs.filter(s=>/event=(OPTION|SELECT|PASS)/.test(s))});
 }
 check(selected[0]===selected[1],'hidden-power mutation never changes full decision '+strength+'/'+seed);
}
// Search diversity must retain the best-ranked action and add legal role alternatives
// without expanding the cap or losing/duplicating any hand candidate.
{
 const g=fixture();clearHand(g);const candidates=[];
 for(let i=0;i<8;i++){const c=add(g,112101,8,i);c.definition.effect=0;c.definition.passiveBoost=0;c.definition.initialTimer=0;c.definition.consumePassiveBoost=0;candidates.push(c);}
 candidates[5].definition.passiveBoost=1;candidates[6].definition.effect=1;candidates[7].definition.effect=29;
 const ids=candidates.map(c=>g.live.indexOf(c));
 // out arrays are WS value parameters in the translator; use an out reference.
 const ref={v:ids.slice()};g.AiDiversifySearch(ref,4);const result=ref.v;
 check(result[0]===ids[0]&&result.slice(0,4).includes(ids[5])&&result.slice(0,4).includes(ids[6])&&result.slice(0,4).includes(ids[7]),'limited exact search covers engine, control and combo while keeping top action');
 check(new Set(result).size===ids.length&&result.length===ids.length,'diversification is a permutation of legal candidates');
 const pair={v:ids.slice()};g.AiDiversifySearch(pair,2);check(pair.v[0]===ids[0]&&pair.v[1]===ids[5],'two-sequence budget includes a distinct role');
}
check(BetaGwentAIResourcePressure(1,0,0,3,6,5)>BetaGwentAIResourcePressure(1,0,0,6,3,5),'card deficit increases future resource reservation');
check(BetaGwentAIResourcePressure(2,1,0,4,4,5)>BetaGwentAIResourcePressure(1,0,0,4,4,5),'optional bleed preserves resources for deciding round');
check(BetaGwentAIResourcePressure(3,1,1,3,6,5)===0&&BetaGwentAIResourcePressure(2,0,1,3,6,5)===0,'deciding rounds never reserve future resources');
check(BetaGwentAIReplyPassChance(1,0,0,20,3,4,false)>BetaGwentAIReplyPassChance(3,1,1,20,3,4,false),'public pass prior distinguishes optional and deciding rounds');
check(BetaGwentAIReplyPassChance(2,0,0,0,0,4,false)===100,'no cards or leader makes pass certain');
for(const strength of [2,3,4]){
 Host.strength=strength;const g=fixture();clearHand(g);g.match.roundNumber=2;g.match.playerOne.crowns=1;g.match.playerOne.hasPassed=true;
 add(g,112101,1,0,1,6);const cheap=add(g,112101,8,0,2,7),gold=add(g,112101,8,1,2,12);gold.definition.header.tierMask=8;
 const logs=[];Host.log=s=>logs.push(s);check(g.OpponentStep(),'catchup corpus decision '+strength);Host.log=null;
 check(cheap.Snapshot().locationMask!==8&&gold.Snapshot().locationMask===8,'winning ordinary card preserves more valuable reserve '+strength);
 decisions.push({case:'minimum_resource_catchup',strength,seed:g.random.InitialSeed(),allowed:['ordinary'],selected:'ordinary',reason:logs.filter(s=>/event=(OPTION|SELECT|PASS)/.test(s))});
}
globalThis.policyReport={checks,decisions,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'policy133.bundle.js',timeout:180000});
const manifest=JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8'));
context.policyReport.fingerprint=manifest.fingerprint;
context.policyReport.sources=Object.fromEntries(['duelSession','duelAIPass','duelPublicResponseAI'].map(n=>{const p='BetaGwent/development/scripts/game/betagwent/'+n+'.ws';return [p,manifest.files[p]];}));
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.policyReport,null,2)+'\n');
