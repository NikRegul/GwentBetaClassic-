'use strict';
const fs=require('fs'),path=require('path');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));
const {fixture,add}=require('./audit_fixture095.cjs')(rt),id=c=>c.Snapshot().instanceId;
let checks=0;const failures=[],check=(v,n)=>{checks++;if(!v)failures.push(n);};
for(const side of [1,2]){
 const g=fixture(side);g.mulliganReactions=true;
 add(g,201704,side,16,0);add(g,201704,side,16,1);const unit=id(add(g,112405,side,16,2));
 const parent=id(add(g,142308,side,8));check(g.Play(side,parent,1),'Mercenary opens two Reconnaissance offers '+side);
 check(g.pendingIds.length===2&&g.pendingIds.every(x=>g.FindCard(x).TemplateId()===201704),'actual logged two-special offer shape '+side);
 check(g.GetRequestSnapshot().limits.minimum===1&&!g.FinishTarget(g.requestId),'must play one offered special '+side);
 check(g.SelectTarget(g.requestId,g.pendingIds[0]),'offered Reconnaissance accepted '+side);
 check(g.pendingPileChoice&&g.GetRequestSnapshot().limits.minimum===1&&!g.FinishTarget(g.requestId),'nested Reconnaissance must play a unit '+side);
 check(g.SelectTarget(g.requestId,unit)&&g.pendingRally,'chosen unit reaches placement '+side);
 check(g.SelectRow(g.requestId,side,2)&&!g.fatal&&!g.IsPending(),'complete nested play returns through both parents '+side);
}
const report={checks,failures,fingerprint:rt.fingerprint,actualWitcherScript:true,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;
