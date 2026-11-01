'use strict';
const fs=require('fs'),path=require('path');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2])),p=require('./fixtures/feedback099/harald-r1.json');
const {rebuild}=require('./reconstruct_user_positions093.cjs');let checks=0;const failures=[],records=[];
const check=(v,n)=>{checks++;if(!v)failures.push(n);};
function position(extra=0,clear=false){const g=rebuild(rt,p,{weather:true});g.mulliganReactions=false;g.leaderTemplateTwo=200161;
 if(clear)g.weather.hazards=[0,0,0,0,0,0];
 if(extra){const c=g.live.find(c=>c.Snapshot().positionPlayerId===1&&(c.Snapshot().locationMask&7));c.power.SetCurrentPair(c.Snapshot().power.currentPower+extra,c.Snapshot().power.armor);}
 return g;}
function step(g){for(let n=0;n<2000;n++){if(g.OpponentStep())return true;g.AiPreparationStep();}return false;}
{
 const g=position(),before=g.Score(2)-g.Score(1),rows=[],draws=g.random.DrawCount();
 for(const row of [1,2,4]){
  const h=g.AiSimClone();check(h.PlaceLeader(h.Leader(2),2,row,-3)&&!h.fatal&&!h.IsPending()&&h.Snapshot().currentPlayerId===1,'complete Harald turn '+row);
  const immediate=[h.Score(1),h.Score(2)];
  check(h.Pass(1)&&!h.fatal,'opponent can pass; next turn resolves Frost '+row);
  const afterPass=[h.Score(1),h.Score(2)],net=h.Score(2)-h.Score(1)-before;
  check(h.Pass(2)&&h.Snapshot().playerOne.crowns===1&&h.Snapshot().playerTwo.crowns===0,'every lane loses the actual round after Frost '+row);
  check(g.AiHaraldRow099(2,row,true)===net,'planner matches authoritative move and counterpass '+row);
  rows.push({row,immediate,afterPass,net});
 }
 check(rows[0].net===7&&rows[1].net===13&&rows[2].net===13,'Frost reduces the apparent sixteen-point catch to thirteen');
 check(g.random.DrawCount()===draws,'planning trials do not consume live RNG');
 check(step(g)&&!g.fatal&&g.Snapshot().playerTwo.hasPassed&&g.Leader(2).Snapshot().locationMask===64,'logged position: pass and preserve Harald');
 check(g.Pass(1)&&g.Snapshot().playerOne.crowns===1,'preserving the leader concedes only this optional round');
 records.push({weather:p.head.weather,rows,decision:'preserve leader'});
}
{
 const g=position(0,true);check(step(g)&&!g.fatal,'no-Frost control action completes');
 const leader=g.live.find(c=>c.TemplateId()===200161).Snapshot();
 check([2,4].includes(leader.locationMask),'without Frost Harald chooses full-damage lane');
 check(g.Pass(1)&&g.Pass(2)&&g.Snapshot().playerTwo.crowns===1,'without Frost the same catch really wins the round');
}
{
 const g=position(50);check(step(g)&&!g.fatal,'unreachable optional-round action completes');
 check(g.Snapshot().playerTwo.hasPassed&&g.Leader(2).Snapshot().locationMask===64,'no hand/follow-up: preserve leader when every row fails');
}
const report={checks,failures,records,fingerprint:rt.fingerprint,loggedPosition:p.scope,sourceSha256:p.sourceSha256,actualWitcherScript:true,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;
