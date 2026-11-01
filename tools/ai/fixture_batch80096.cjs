'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),sourceEvidence=require('./source_batch80096.cjs'),{catalog}=require('./source_graph095.cjs');
module.exports=function(snapshot){
 const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(snapshot)),api=require('./audit_fixture095.cjs')(rt);
 let checks=0,label='';const failures=[],cases=[],snap=c=>c.Snapshot(),id=c=>snap(c).instanceId,byId=new Map(catalog.templates.map(t=>[Number(t.attributes.Id),t]));
 const check=(v,s,detail)=>{checks++;if(!v)failures.push({case:label,assertion:s,...(detail?{detail}:{})});};
 function flush(g){g.FlushEffects();g.FlushDeaths();while(g.nilfJobs.length&&!g.IsPending()){g.NilfNextReaction();g.FlushEffects();g.FlushDeaths();}}
 function run(tid,side,mode,body){label=tid+'/'+side+'/'+mode;const g=api.fixture(side,59573+side);try{body(g);check(!g.IsFatal(),'no fatal');cases.push({id:tid,side,mode});}catch(e){failures.push({case:label,fixtureError:e.stack});}}
 function begin(g,tid,side,row=2,power=30,armor=0,from=8,tokens=0){
  g.mulliganReactions=true;const source=api.add(g,tid,side,from,40,power,armor,tokens);
  if(from===8)check(g.Play(side,id(source),row),'real hand deploy');
  else{const parent=api.add(g,from===32?113316:201704,side,256,0);parent.playFromLocation=8;g.playStack=[parent];g.PlayFromPile(parent,source,row,g.CountLocation(side,row));}
  flush(g);return source;
 }
 function choose(g,c){check(!!g.IsPending()&&g.pendingIds.includes(id(c)),'exact target offered',{pending:g.pendingIds,target:id(c)});if(!g.IsPending()||!g.pendingIds.includes(id(c)))return false;check(g.SelectTarget(g.requestId,id(c)),'target accepted');flush(g);return true;}
 function trace(g){const draws=[],orig=g.random.NextBounded.bind(g.random);g.random.NextBounded=n=>{const v=orig(n);draws.push({n,v});return v;};return draws;}
 const category=(tid,mask)=>!!(BigInt(byId.get(tid).categoryWords[0].decimal)&BigInt(mask));
 function categoryTemplate(mask,{tier=0,type=4,exclude=[]}={}){return catalog.templates.find(t=>{const tid=Number(t.attributes.Id);return rt.definition(tid).header.templateId===tid&&t.fields.Type===type&&(!tier||t.fields.Tier===tier)&&!exclude.includes(tid)&&category(tid,mask);})?.attributes.Id*1;}
 function finish(output,scope){const report={schema:1,fingerprint:rt.fingerprint,checks,failures,cases,sourceEvidence,scope,semanticCoverageComplete:false};if(output){assert(!fs.existsSync(output),'fresh report');fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,cases:cases.length,cards:new Set(cases.map(c=>c.id)).size,failures:failures.length,firstFailures:failures.slice(0,20),fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;return report;}
 return {...api,rt,byId,snap,id,check,flush,run,begin,choose,trace,category,categoryTemplate,finish};
};
