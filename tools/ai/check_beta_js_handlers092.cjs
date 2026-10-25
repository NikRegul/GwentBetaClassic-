'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {BetaHandler,decision,summationWeight,sourceHint,resolveAssociation,rowPower,propagatedKey,UnportedBetaHandler,originalSettings}=require('./beta_js092/handlers.cjs');
const {personality}=require('./beta_js092/profiles.cjs');
const sheets=require('./beta_js092/data/summations.json'),ordered=require('./beta_js092/data/summations-ordered.json');
let checks=0;function eq(a,b,label){assert.deepEqual(a,b,label);checks++;}
eq(originalSettings({CardGroup:'NotGold',SemanticTagId:'Peasant',TagsTokenType:'Immune',Location:'Board',UnitOrEvent:'Any'}),{CardGroup:15,SemanticTagId:1,TagsTokenType:1,Location:7,UnitOrEvent:14},'literal source int.TryParse leaves constructor defaults for named XML values');
for(const raw of ['2147483648','-2147483649','NaN','1.5',''])eq(originalSettings({CardGroup:raw}).CardGroup,15,'source signed32 parsing fallback');
eq(originalSettings([{type:'CardGroup',value:' +6 '},{type:'SemanticTagId',value:'47'}]),{CardGroup:6,SemanticTagId:47},'source numeric XML settings');
function card(id,side,power,tier=2,tokens=0,tags=[]){return {id,templateId:100+id,side,zone:1,power,basePower:5,templateTier:tier,type:4,tokens,semanticTags:tags,placement:{player:7,opponent:0},visibleToBoth:true};}
const cards=[card(1,1,8,2,4,[9]),card(2,2,4,4,0,[9]),card(3,1,2,8,1,[]),card(4,2,7,2,0,[])];
const ctx={node:{},actor:1,state:{cards,roundIndex:0,rows:[{side:1,row:1,token:1},{side:2,row:1,token:128},{side:1,row:2,token:0}]}};
const req={kind:'targets',items:cards,min:1,max:1};
function ids(kind,s={},r=req,c=ctx){return new BetaHandler(kind,s).filter(c,r)?.map(x=>x.id);}
eq(ids('Power'),[1,4,2,3],'power descending');eq(ids('Power',{SortOrder:'Lowest'}),[3,2,4,1],'power ascending');
eq(ids('Power',{PlayerType:'Same',CardGroup:2}),[1],'player/tier applied');
eq(ids('PowerRange',{MinRange:3,MaxRange:7}),[4,2],'inclusive range');eq(ids('PowerRange',{MinRange:7,MaxRange:0}),[1,4],'zero max means unbounded');
eq(ids('TemplateId',{TemplateId:102,PlayerType:'Same'}),[2],'original TemplateId ignores computed player filter');
eq(ids('TemplateId',{TemplateId:102,Negate:true}),[1,3,4],'negated template');
eq(ids('Semantic',{SemanticTagId:9}),[1,2],'semantic tag membership');eq(ids('Semantic',{SemanticTagId:9,Negate:true}),[3,4],'negated semantic');
eq(ids('HasTagsToken',{TagsTokenType:'Lock, Resilience'}),[1,3],'source Contains uses any bit');
eq(ids('HasTagsToken',{TagsTokenType:0,Negate:true}),[1,2,3,4],'zero-mask negate');
eq(ids('Health',{Health:'Boosted'}),[1,4],'boosted current vs base');eq(ids('Health',{Health:'Damaged'}),[2,3],'damaged current vs base');
eq(ids('Location',{Location:'Hand',LocationAction:'IsAtLocation'}),[],'current zone');
eq(ids('Location',{Location:'Ranged',LocationAction:'CanGotoLocation'}),[1,2,3,4],'template placement union');
eq(ids('PlayAll',{}, {...req,min:2,max:2}),undefined,'source both-not-one guard');
eq(decision(new BetaHandler('PlayAll'),ctx,req).branches.map(x=>x[0].id),[2,3,4],'PlayAll alternative siblings');
eq(decision(new BetaHandler('Semantic',{SemanticTagId:999}),ctx,req).chosen.map(x=>x.id),[1],'source invalid-decision minimum repair');
eq(decision(new BetaHandler('Semantic',{SemanticTagId:999}),ctx,{...req,min:0}).chosen,[],'valid optional empty stays empty');
let sequence=[2,1,0],calls=0;
const randomContext={...ctx,next:(min,max)=>{calls++;const n=sequence.shift();assert(n>=0&&n<max-min);return min+n;}};
eq(new BetaHandler('Random').filter(randomContext,{...req,min:0,max:3}).map(x=>x.id),[2,1],'source random count then sample without replacement');eq(calls,3,'random stream call count');
sequence=[2];calls=0;eq(new BetaHandler('Random',{PlayerType:'Same'}).filter(randomContext,{kind:'play',items:cards,min:1,max:1}).map(x=>x.id),[3],'source random play ignores player filter');eq(calls,1,'random placement calls once');
const rows=[{side:1,row:1,index:0},{side:2,row:1,index:0},{side:1,row:2,index:0}];
eq(new BetaHandler('RowWithNumberOfUnits').filter(ctx,{kind:'play',items:rows,min:1,max:1}),rows,'row count stable ties');
eq(new BetaHandler('RowWithNumberOfUnits',{SortOrder:'Lowest'}).filter(ctx,{kind:'play',items:rows,min:1,max:1}),rows,'literal Lowest double reversal');
eq(new BetaHandler('RowWithEffect',{EffectType:'Boon'}).filter(ctx,{kind:'play',items:rows,min:1,max:1})[0].side,2,'boon row');
eq(new BetaHandler('RowWithEffect',{EffectType:'Hazard',Negate:true}).filter(ctx,{kind:'play',items:rows,min:1,max:1})[0].side,2,'non-hazard row');
const scratch=cards.map(x=>({...x}));scratch[0].inExecution=true;scratch[2].visibleToBoth=false;
eq(rowPower({...ctx,state:{...ctx.state,cards:scratch}},{side:1,row:1}),0,'row score excludes executing/hidden cards');
eq(propagatedKey({side:1,row:1},'play'),propagatedKey({side:2,row:2},'locations'),'original LocationData xor collision');
const h=new BetaHandler('Power',{},3);h.addAll(ctx.node,[rows[0],{side:2,row:2}],'play');eq(h.get(ctx.node,0),6,'colliding propagated keys accumulate');h.cleanup();eq(h.get(ctx.node,0),0,'ordinary cleanup');
eq(ordered.length,54,'all source sheets preserved');eq(Object.keys(sheets).length,53,'source duplicate id');
eq(sheets['87440b51-48a9-45c0-af85-dc20692d988d'].name,'Basic_LockTarget','original first duplicate wins');
eq(sourceHint(113301,'targets'),23,'actual damage AI hint');eq(sourceHint(201701,'targets'),40,'actual consume AI hint');eq(sourceHint(113208,'templates'),26,'actual template-choice hint');
const p=personality('Base');eq(resolveAssociation(p,'CardTargetsAssociations',113301,23).attributes.TemplateId,'113301','template1 before global hint');
eq(resolveAssociation(p,'CardTargetsAssociations',999999,23).attributes.AIHIntId,'23','global hint');
eq(resolveAssociation(p,'CardTargetsAssociations',999999,999),null,'no global1 extra fallback');
for(const type of ['Linear','StaggeredPercentile','MinNumberFromRequest','MaxNumberFromRequest','MaxNumberFromRequestStaggered','SingleBest']){
 const got=Array.from({length:4},(_,i)=>summationWeight({handler:'PowerRange',scoring:type,weight:8},i,4,1,2));
 const want={Linear:[8,8,8,8],StaggeredPercentile:[8,6,4,2],MinNumberFromRequest:[8,0,0,0],MaxNumberFromRequest:[8,8,0,0],MaxNumberFromRequestStaggered:[8,4,0,0],SingleBest:[8,0,0,0]}[type];eq(got,want,'source summation '+type);
}
eq(summationWeight({handler:'Semantic',scoring:'SingleBest',weight:7},2,4,1,1),7,'advanced unsupported handler forced linear');
// Independent manual rankings from semantic membership + staggered power.
for(let seed=1;seed<=80;seed++){
 const list=Array.from({length:7},(_,i)=>card(i+1,i%2+1,(seed*7+i*3)%17+1,2,0,(seed+i)%3===0?[9]:[]));
 const context={...ctx,node:{},state:{...ctx.state,cards:list,roundIndex:seed%3}};
 const sum=new BetaHandler('Summation');sum.sheet={entries:[
  {handler:'Semantic',rounds:'All',scoring:'SingleBest',weight:3,propagate:2},
  {handler:'PowerRange',rounds:'All',scoring:'StaggeredPercentile',weight:5,propagate:1}]};
 sum.children=[new BetaHandler('Semantic',{SemanticTagId:9},2),new BetaHandler('PowerRange',{},1)];
 const powerOrder=list.slice().sort((a,b)=>b.power-a.power);
 const expected=list.map(c=>({c,value:Math.fround((c.semanticTags.includes(9)?3:0)+Math.fround(Math.fround((7-powerOrder.indexOf(c))/7)*5))})).sort((a,b)=>b.value-a.value);
 const result=decision(sum,context,{...req,items:list});eq(result.chosen[0].id,expected[0].c.id,'independent summation ranking');
 const propagated=expected[0].c.semanticTags.includes(9)?3:1;eq(result.propagated,propagated,'source child propagation');
 // Summation inherits base cleanup, leaving CHILD score maps intact.
 eq(sum.get(context.node,expected[0].c.id),propagated,'literal child propagation survives outer cleanup');
}
eq(new BetaHandler('Wedge').filter(ctx,req),null,'Wedge has source None card-target handler');
const report={checks,sourceSheets:54,sourceRequestNodes:357,defaultPolicyCalls:0,nativeProcessLaunch:false,
 scope:'Direct source handler filters, first duplicate sheet, source request hints, exact resolver precedence, random draws, six summation scoring methods, propagation and source quirks. Not a full Beta match.',
 implemented:['PlayAll','Random','Power','PowerRange','TemplateId','Semantic','HasTagsToken','Location','UnitOrEvent','Health','RowWithNumberOfUnits','RowWithUnitStrength','RowWithEffect','RowWithCeiling','Summation'],
 pending:['Full mixed-policy integration and complete profile-path validation'],fullMatchReady:false};
fs.writeFileSync(path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/direct-beta-js-handlers-proof.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
