'use strict';
// Additional exploratory checks; always use the frozen 0.8.2 audit input.
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(__dirname,'../..'),out=path.resolve(process.argv[4]||path.join(root,'BetaGwent/build/audit082-20261018'));
fs.mkdirSync(out,{recursive:true});
const snapshot=path.resolve(process.argv[3]||path.join(out,'rules')),ctx=vm.createContext({console:{log(){}}});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+'\nHost.strength=4;'+fixture,ctx);
const manifest=JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8'));
if(process.argv[2]==='selfplay'){
 const results=[];
 for(let i=0;i<manifest.presets.length;i++){
  const a=manifest.presets[i],b=manifest.presets[(i*17+1)%manifest.presets.length],seed=924082+i*104729;
  for(const [l,r] of [[a,b],[b,a]]){
   ctx.job={l,r,seed};
   const result=vm.runInContext('__harness.play(job.l,job.r,job.seed,4,4,120)',ctx,{timeout:90000});
   results.push(result);
   fs.writeFileSync(path.join(out,'selfplay.json'),JSON.stringify({source:manifest.source,fingerprint:manifest.fingerprint,nativeGameTested:false,games:results.length,errors:results.filter(r=>r.error).length,results},null,2));
   console.log(JSON.stringify({game:results.length,left:l,right:r,steps:result.steps,winner:result.winner,error:result.error?.split('\n')[0]}));
  }
 }
}else if(process.argv[2]==='human'){
 const catalogue=fs.readFileSync(path.join(manifest.source,'scripts/game/betagwent/duelCatalog.ws'),'utf8');
 const lookup=catalogue.slice(catalogue.indexOf('function BetaGwentDuelDefinitionLookup0'),catalogue.indexOf('function BetaGwentDuelDefinitionGroup0'));
 ctx.templates=[...new Set([...lookup.matchAll(/case (\d+):/g)].map(m=>+m[1]))];
 vm.runInContext(String.raw`
 const exploration={attempted:0,completed:0,rejected:[],failures:[],excluded:[]};
 function humanPending(g){
  if(g.pendingChoice)return g.SelectTemplateChoice(g.requestId,g.pendingIds[0]);
  if(g.pendingRow||g.pendingRally||g.pendingLeader){
   for(const side of [1,2])for(const row of [1,2,4])if(g.SelectRow(g.requestId,side,row))return true;
   return g.FinishTarget(g.requestId);
  }
  if(g.pendingIds.length)return g.SelectTarget(g.requestId,g.pendingIds[0]);
  return g.FinishTarget(g.requestId);
 }
 for(const id of templates){
  const d=BetaGwentDuelDefinition(id);if(d.header.typeMask!==2&&d.header.typeMask!==4)continue;
  if(!BetaGwentDuelCollectible(id)){exploration.excluded.push(id);continue;}
  for(const count of [0,2,8]){
   const g=fixture(1);g.aiSimulating=true;g.aiSimDamp=100;
   for(const side of [1,2])for(const row of [1,2,4]){
    for(let i=0;i<count;i++)add(g,i%2?112101:132314,row,i,side,5+i);
    if(count){add(g,132314,32,row,side,5);add(g,112101,16,row,side,5);}
   }
   const c=add(g,id,8,4,1);exploration.attempted++;
   try{
    if(!g.Play(1,c.Snapshot().instanceId,1)){if(g.IsFatal())throw Error(g.GetMessage());exploration.rejected.push({id,count,title:d.title});continue;}
    let steps=0;
    while(g.IsPending()&&!g.IsFatal()){
     if(++steps>40)throw Error('request did not finish');
     if(!humanPending(g))throw Error('no legal pending continuation '+g.GetMessage());
    }
    if(g.IsFatal())throw Error(g.GetMessage());
    for(const side of [1,2])for(const row of [1,2,4]){
     const cards=g.live.filter(c=>c.Snapshot().positionPlayerId===side&&c.Snapshot().locationMask===row);
     if(cards.length>9)throw Error('row overflow '+side+'/'+row+': '+cards.length);
     const indices=cards.map(c=>c.Snapshot().locationIndex).sort((a,b)=>a-b);
     if(indices.some((x,i)=>x!==i))throw Error('noncontiguous row '+side+'/'+row+': '+indices);
    }
    exploration.completed++;
   }catch(e){exploration.failures.push({id,count,title:d.title,error:String(e.stack||e)});}
  }
 }
 globalThis.exploration=exploration;
 `,ctx,{timeout:180000});
 fs.writeFileSync(path.join(out,'human-card-exploration.json'),JSON.stringify({source:manifest.source,fingerprint:manifest.fingerprint,nativeGameTested:false,...ctx.exploration},null,2));
 console.log(JSON.stringify(ctx.exploration));
}else{
 const catalogue=fs.readFileSync(path.join(manifest.source,'scripts/game/betagwent/duelCatalog.ws'),'utf8');
 const lookup=catalogue.slice(catalogue.indexOf('function BetaGwentDuelDefinitionLookup0'),catalogue.indexOf('function BetaGwentDuelDefinitionGroup0'));
 const templates=[...new Set([...lookup.matchAll(/case (\d+):/g)].map(m=>+m[1]))];
 ctx.templates=templates;
 vm.runInContext(String.raw`
 const exploration={attempted:0,played:0,rejected:[],failures:[],pending:[]};
 for(const id of templates)for(const populated of [false,true]){
  const d=BetaGwentDuelDefinition(id);if(d.header.typeMask!==2&&d.header.typeMask!==4)continue;
  const g=fixture(2);g.aiSimulating=true;g.aiSimDamp=100;
  if(populated)for(const side of [1,2])for(const row of [1,2,4]){
   add(g,132314,row,0,side,5);add(g,112101,row,1,side,11);
   add(g,132314,32,row,side,5);add(g,112101,16,row,side,5);
  }
  const c=add(g,id,8,4,2);exploration.attempted++;
  try{
   if(!g.Play(2,c.Snapshot().instanceId,1)){if(g.IsFatal())throw Error(g.GetMessage());exploration.rejected.push({id,populated,title:d.title});continue;}
   exploration.played++;
   if(g.IsFatal())throw Error(g.GetMessage());
   if(g.IsPending())exploration.pending.push({id,populated,title:d.title,source:g.pendingCard?.TemplateId(),side:g.NilfDecisionSide(),ids:[...g.pendingIds]});
   for(const side of [1,2])for(const row of [1,2,4]){
    const cards=g.live.filter(c=>c.Snapshot().positionPlayerId===side&&c.Snapshot().locationMask===row);
    if(cards.length>9)throw Error('row overflow '+side+'/'+row+': '+cards.length);
    const indices=cards.map(c=>c.Snapshot().locationIndex).sort((a,b)=>a-b);
    if(indices.some((x,i)=>x!==i))throw Error('noncontiguous row '+side+'/'+row+': '+indices);
   }
  }catch(e){exploration.failures.push({id,populated,title:d.title,error:String(e.stack||e)});}
 }
 globalThis.exploration=exploration;
 `,ctx,{timeout:180000});
 fs.writeFileSync(path.join(out,'card-exploration.json'),JSON.stringify({source:manifest.source,fingerprint:manifest.fingerprint,nativeGameTested:false,...ctx.exploration},null,2));
 console.log(JSON.stringify(ctx.exploration));
}
