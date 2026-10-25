'use strict';
const assert=require('assert/strict'),fs=require('fs'),path=require('path');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {BetaHandler}=require('./beta_js092/handlers.cjs'),{personality}=require('./beta_js092/profiles.cjs');
const original=require('./beta_js092/data/personalities.json');let checks=0;
function eq(a,b,l){assert.deepEqual(a,b,l);checks++;}
function c(id,side,zone,index,power,template=100,tier=2,tags=[]){return {id,side,zone,index,power,templateId:template,templateTier:tier,semanticTags:tags};}
function filter(kind,settings,items,ctx,type='choices'){return new BetaHandler(kind,settings).filter(ctx,{kind:type,items,min:1,max:1});}
const list=[c(1,1,8,0,4,10,2,[7]),c(2,2,8,0,9,20,2,[8]),c(3,1,8,1,6,10,4,[7,8]),c(4,2,8,1,5,30,2,[])];
const context={actor:1,node:{},state:{cards:list,roundIndex:0,rows:[]},personality:{semanticTags:[{id:7,weight:3},{id:8,weight:5}],MeleePreference:2,RangedPreference:7,SiegePreference:-4}};
eq(filter('Preference',{},list,context).map(c=>c.id),[3,2,1,4],'preference sums ALL semantic matches');
eq(filter('Preference',{PlayerType:'Same',CardGroup:2},list,context).map(c=>c.id),[1],'preference player and tier');
const positions=[1,2,4].map(row=>({side:1,row,index:0}));eq(filter('Preference',{},positions,context,'play').map(x=>x.row),[2,1,4],'preference printed row weights');
eq(filter('Preference',{SortOrder:'Lowest'},positions,context,'locations').map(x=>x.row),[4,1,2],'ascending row preference');
eq(new BetaHandler('Preference').canBranchPlacement(),false,'source Preference keeps first placement only');
for(const type of ['choices','targets']){
 eq(filter('Occurrence',{Destination:'MatchSource'},list,context,type).map(c=>c.id),[1,3,2,4],'source occurrence all request entries ranked');
 eq(filter('Occurrence',{PlayerType:'Same',CardGroup:4},list,context,type).map(c=>c.id),[1,3,2,4],'raw output preserves candidates outside initial filters');
 eq(filter('OccurrenceRange',{Destination:'Hand',PlayerType:'Same',MinRange:2,MaxRange:2},list,context,type).map(c=>c.id),[1,3],'inclusive destination count bounds');
 eq(filter('OccurrenceRange',{MinRange:1,MaxRange:0},list,context,type),[],'source max0 is literal0, not unbounded');
}
// Independent histogram oracle: duplicates count by template, not by power or
// row. Request ordering determines ties, including candidates from either seat.
for(let seed=1;seed<=120;seed++){
 const cards=Array.from({length:12},(_,i)=>c(i+1,i%2+1,[8,16,32][i%3],i,seed+i,(seed*13+i*7)%5+100));
 const ctx={...context,state:{...context.state,cards}},request=cards.slice(0,8),side=seed%3===0?0:seed%2+1,zone=[8,16,32][seed%3];
 const histogram={};for(const x of cards)if(x.zone===zone&&(!side||x.side===side))histogram[x.templateId]=(histogram[x.templateId]||0)+1;
 const expected=request.map((x,i)=>({x,i,n:histogram[x.templateId]||0})).sort((a,b)=>seed%2?(b.n-a.n||a.i-b.i):(a.n-b.n||a.i-b.i));
 const got=filter('Occurrence',{Destination:{8:'Hand',16:'Deck',32:'Graveyard'}[zone],PlayerType:side===0?'Both':side===1?'Same':'Opposite',SortOrder:seed%2?'Highest':'Lowest'},request,ctx);
 eq(got.map(x=>x.id),expected.map(x=>x.x.id),'independent occurrence histogram '+seed);
}
const board=[c(1,1,1,0,2,10),c(2,1,1,1,9,20),c(3,1,1,2,5,10),c(4,1,2,0,4,20)],ctx={...context,state:{...context.state,cards:board}};
const slots=[0,1,2,3].map(index=>({side:1,row:1,index}));
eq(filter('Wedge',{WedgeType:'LeftOf'},slots,ctx,'play').map(x=>x.index),[1],'LeftOf reads card at insertion index');
eq(filter('Wedge',{WedgeType:'RightOf'},slots,ctx,'play').map(x=>x.index),[2],'RightOf reads insertion index-1');
eq(filter('Wedge',{WedgeType:'InBetween'},slots,ctx,'play').map(x=>x.index),[2],'between ranks both neighbours');
eq(filter('Wedge',{WedgeType:'InBetween',SortOrder:'Lowest'},slots,ctx,'play').map(x=>x.index),[1],'lowest neighbour sum');
eq(filter('Wedge',{WedgeType:'LeftOf',TemplateId:10},slots,ctx,'play').map(x=>x.index),[2,0],'constrained wedge retains ALL matches, sorted');
eq(filter('Wedge',{WedgeType:'LeftOf',TemplateId:10,Negate:true},slots,ctx,'play').map(x=>x.index),[1],'negated template constraint');
eq(filter('OccurrenceRange',{TemplateId:10,MinRange:3,MaxRange:4},positions,ctx,'locations').map(x=>x.row),[1,2,4],'out-of-range rows zeroed, not removed');
// Closure of all actual named associations and every Summation descendant,
// across the229 flattened profiles. This is handler coverage, not full games.
const known=new Set(['PlayAll','Random','Power','PowerRange','TemplateId','Semantic','HasTagsToken','Location','UnitOrEvent','Health','RowWithNumberOfUnits','RowWithUnitStrength','RowWithEffect','RowWithCeiling','Summation','Occurrence','OccurrenceRange','Preference','Wedge']);
let associations=0;const families=new Set();
for(const name of Object.keys(original)){
 const p=personality(name);
 for(const [type,entries]of Object.entries(p.associations))for(const a of entries){
  const handler=new BetaHandler(a.attributes.Handler,a.settings),queue=[handler];associations++;
  while(queue.length){const h=queue.pop();eq(known.has(h.kind),true,'source family closure '+name+'/'+type+'/'+h.kind);families.add(h.kind);queue.push(...h.children);}
 }
}
const report={checks,profiles:229,associations,families:[...families].sort(),nativeProcessesAllowed:false,
 scope:'Direct Preference/Occurrence/OccurrenceRange/Wedge algorithms, literal quirks,120 independent histogram oracles; all229 flattened profile associations and Summation descendants instantiate supported families. Not full behavior or strength proof.',fullMatchReady:false};
fs.writeFileSync(path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/direct-beta-js-profile-handlers-proof.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
