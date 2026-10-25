'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {createRuntime}=require('./beta_js092/session.cjs');const rt=createRuntime(path.resolve(process.argv[2]));let checks=0;
const check=(v,n)=>{checks++;assert(v,n);};
function add(g,id,zone,index){const r={v:0};g.registry.Allocate(r);const c=rt.newCard();c.Setup(g,r.v,id,1,zone,index);g.registry.Put(r.v,c);g.live.push(c);return c;}
const records=[];
for(const keepIndex of [0,1]){
 const g=rt.newSession();g.InitializeWithPresets(72,72);for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);
 g.mulligan=false;g.waiting=false;g.pendingCard=g.pendingLeader=null;g.recordVisuals=false;
 g.match.currentPlayerId=1;g.match.roundActive=g.match.turnActive=true;g.match.roundNumber=1;g.match.playerOne.hasPassed=g.match.playerTwo.hasPassed=false;
 const spy=add(g,162210,8,0),old=add(g,112405,8,1),offered=[add(g,113310,16,0),add(g,112101,16,1)],tail=add(g,112405,16,2);
 check(g.Play(1,spy.Snapshot().instanceId,1),'real Cantarella plays');check(g.IsPending(),'real offer pauses for human selection');
 check(g.pendingIds.length===2&&offered.every(c=>g.pendingIds.includes(c.Snapshot().instanceId)),'only the actual top two cards offered');
 check(!g.SelectTarget(g.requestId,old.Snapshot().instanceId),'unoffered hand card cannot be selected');
 check(g.IsPending(),'invalid hand click does not dismiss offer');
 const kept=offered[keepIndex],returned=offered[1-keepIndex];check(g.SelectTarget(g.requestId,kept.Snapshot().instanceId),'either offered card may be kept');
 check(!g.IsPending()&&!g.IsFatal(),'keep choice resolves ability');
 check(kept.Snapshot().locationMask===8&&old.Snapshot().locationMask===8,'selected and pre-existing hand cards remain');
 check(returned.Snapshot().locationMask===16&&returned.Snapshot().locationIndex>tail.Snapshot().locationIndex,'other offered card returns below the deck tail');
 records.push({keepIndex,kept:kept.Snapshot().instanceId,returned:returned.Snapshot().instanceId});
}
const report={checks,records,fingerprint:rt.fingerprint,actualWitcherScript:true,nativeGameplayVerified:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
