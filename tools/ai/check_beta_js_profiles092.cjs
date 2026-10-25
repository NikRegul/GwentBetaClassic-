'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const cp=require('node:child_process');for(const name of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[name]=()=>{throw Error('Native runtime forbidden');};
const {scalarSettings,personality,scalarSchema}=require('./beta_js092/profiles.cjs');
const profiles=require('./beta_js092/data/personalities.json');let checks=0;
const eq=(a,b)=>{assert.deepEqual(a,b);checks++;};
// XML child deliberately stores a stale local value; inherited getter must use
// AI_TestPlayer's explicit29.2 instead of local-4.9 or Base's1.
eq(scalarSettings('AI_TestPlayer Child').EventCardPreference,Math.fround(29.2));
eq(scalarSettings('Base').EventCardPreference,1);
eq(scalarSettings('Default 9770699').CanDryPassOnRound2,false);
eq(scalarSettings('Default 9770699').PlayingIntoHazardsPreference,-5);
eq(scalarSettings('Default 9770699').RowStackingPreference,Math.fround(-0.15));
const p=(parent,values={},inherited={})=>({parent,values,inherited});
const chain={R:p('',{DepthOfChecking:3}),M:p('R',{DepthOfChecking:9}),C:p('M',{DepthOfChecking:6},{DepthOfChecking:false})};
eq(scalarSettings('M',chain).DepthOfChecking,3);eq(scalarSettings('C',chain).DepthOfChecking,6);
chain.M.inherited.DepthOfChecking=false;eq(scalarSettings('M',chain).DepthOfChecking,9);
chain.R.inherited.DepthOfChecking=true;eq(scalarSettings('R',chain).DepthOfChecking,3);
const before=JSON.stringify(profiles);
for(const name of Object.keys(profiles)){
 const settings=scalarSettings(name);eq(Object.keys(settings).length,74);
 for(const [key,schema]of Object.entries(scalarSchema)){
  if(['float','double','int'].includes(schema.type))assert(Number.isFinite(settings[key]));
  else if(schema.type==='bool')assert.equal(typeof settings[key],'boolean');
  checks++;
 }
}
eq(JSON.stringify(profiles),before);
assert.throws(()=>scalarSettings('missing'));checks++;
assert.throws(()=>scalarSettings('A',{A:p('B'),B:p('A')}));checks++;
const own=scalarSettings('Base');own.DepthOfChecking=999;eq(scalarSettings('Base').DepthOfChecking,1);
const tags=(...ids)=>ids.map(id=>({id,weight:id,usage:0,rounds:7}));
chain.R.semanticTags=tags(1,2,4);chain.M.semanticTags=tags(3,1);chain.C.semanticTags=tags(2);
eq(personality('C',chain).semanticTags.map(x=>x.id),[2,4,3,1]);
const assoc=(template,hint,handler)=>({attributes:{TemplateId:String(template),AIHIntId:String(hint),Handler:handler},settings:[{type:'PlayerType',value:'Both'}]});
chain.R.associations={CardTargetsAssociations:[assoc(10,1,'Root'),assoc(10,2,'Root2'),assoc(20,1,'Old')]};
chain.M.associations={CardTargetsAssociations:[assoc(20,1,'Near')]};
chain.C.associations={CardTargetsAssociations:[assoc(10,1,'Child')]};
eq(personality('C',chain).associations.CardTargetsAssociations.map(x=>x.attributes.Handler),['Child','Root2','Near']);
const resolved=personality('C',chain);resolved.associations.CardTargetsAssociations[0].settings[0].value='changed';
eq(chain.C.associations.CardTargetsAssociations[0].settings[0].value,'Both');
for(const name of Object.keys(profiles)){
 const resolved=personality(name);eq(resolved.name,name);eq(Object.keys(resolved.associations).length,4);
 for(const t of resolved.semanticTags){assert(Number.isFinite(t.weight));checks++;}
}
eq(JSON.stringify(profiles),before);
const report={schema:1,checks,profiles:Object.keys(profiles).length,inheritedScalarProperties:74,
 missingScalarDefaultsSupported:true,listsAndHandlersFlattened:true,handlerAlgorithmsExercised:false,
 fullMatchReady:false,nativeProcessLaunch:false};
fs.writeFileSync(path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/direct-beta-js-profiles-proof.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
