/* Direct BaseCardHandler / source handler algorithms. No current mod policy.
 * Records/arrays and bounded request lists are suitable for a later WS port.
 * Source quirks are retained, not silently repaired during the baseline port. */
'use strict';
const sheets=require('./data/summations.json'),hintData=require('./data/request-hints.json');
const F=Math.fround;
class UnportedBetaHandler extends Error{}
const tokenNames={Resilience:1,Lock:4,Ambush:8,ImmuneToWeather:16,RevealedOnHand:64,Disloyal:128,NotTargetable:256,Doomed:512,Stubborn:1024,Mark:2048,Berserk:4096};
const locationNames={Invalid:0,Melee:1,Ranged:2,Siege:4,Hand:8,Deck:16,Graveyard:32,Leader:64,SpawningPool:128,PlayStack:256,Void:512,Active:7,Inactive:248,Ignore:767};
function flags(value,names){
 if(typeof value==='number')return value;
 if(/^[-+]?\d+$/.test(String(value)))return Number(value);
 let result=0;for(const name of String(value).split(',').map(s=>s.trim())){
  if(names[name]===undefined)throw new UnportedBetaHandler('Unknown source flag '+name);result|=names[name];
 }return result;
}
function asSettings(list){
 if(!Array.isArray(list))return {...list};const s={};for(const a of list)s[a.type]=a.value;return s;
}
// These original *Setting.ReadFromXML methods use int.TryParse, NOT enum
// name parsing. Historical XML strings such as "NotGold" leave the source
// constructor default in place; Number(string)/NaN is not that behavior.
const integerSettingDefaults={CardGroup:15,SemanticTagId:1,TagsTokenType:1,Location:7,UnitOrEvent:14,Health:1,TemplateId:0,MinRange:0,MaxRange:0};
function originalSettings(values){
 const s=asSettings(values);
 for(const [key,fallback]of Object.entries(integerSettingDefaults))if(key in s){
  const raw=String(s[key]).trim(),value=/^[+-]?\d+$/.test(raw)?Number(raw):NaN;
  s[key]=Number.isInteger(value)&&value>=-2147483648&&value<=2147483647?value:fallback;
 }
 return s;
}
function byPlayer(items,actor,loyalty='Both'){
 if(loyalty==='Both')return items.slice();const side=loyalty==='Same'?actor:3-actor;return items.filter(c=>c.side===side);
}
function byTier(items,tier=15){return tier===0?items.slice():items.filter(c=>(c.templateTier&tier)!==0);}
function rowCards(ctx,x,tier=15){return ctx.state.cards.filter(c=>c.side===x.side&&c.zone===x.row&&(c.templateTier&tier)!==0);}
function rowPower(ctx,x,tier=15){
 if((x.row&7)===0)return 0;
 return rowCards(ctx,x,tier).filter(c=>c.visibleToBoth!==false&&!c.inExecution).reduce((a,c)=>a+c.power,0);
}
function tokenType(token){const boon=(token&384)!==0,hazard=(token&7807)!==0;return boon&&hazard?0:boon?2:hazard?1:0;}
function itemKey(x,kind){return kind==='play'||kind==='locations'?`${x.side}:${x.row}:${kind==='play'?x.index:''}`:String(x.id);}
// Original LocationData.GetHashCode = PlayerId ^ Loc. These collisions also
// exist in the original uint-keyed propagated score map and must be retained.
function propagatedKey(x,kind){return kind==='play'||kind==='locations'?(x.side^x.row)>>>0:x.id>>>0;}
function resolveAssociation(personality,type,templateId,hint){
 const list=personality.associations[type]||[];
 for(const [template,tag]of [[templateId,hint],[templateId,1],[0,hint]]){
  for(const a of list)if(Number(a.attributes.TemplateId)===template&&Number(a.attributes.AIHIntId??1)===tag)return a;
 }return null;
}
function sourceHint(templateId,kind){
 const nodes=(hintData[String(templateId)]||[]).filter(n=>n.kind===kind);
 if(nodes.length===0)throw new UnportedBetaHandler(`No source request hint: ${templateId}/${kind}`);
 const ids=[...new Set(nodes.map(n=>n.hint))];
 if(ids.length!==1)throw new UnportedBetaHandler(`Explicit request stage needed: ${templateId}/${kind}/${ids}`);
 return ids[0];
}
const advanced=new Set(['PowerRange','OccurrenceRange','Wedge','RowWithCeiling','RowWithEffect','RowWithNumberOfUnits','RowWithUnitStrength']);
function summationWeight(a,position,total,min,max){
 let type=advanced.has(a.handler)?a.scoring:'Linear';const weight=F(a.weight);
 if(type==='MaxNumberFromRequestStaggered'){
  if(position>=max)return 0;total=max;type='StaggeredPercentile';
 }
 switch(type){
 case 'StaggeredPercentile':return total<=1?weight:F(F((total-position)/total)*weight);
 case 'MinNumberFromRequest':return position>=min?0:weight;
 case 'MaxNumberFromRequest':return position>=max?0:weight;
 case 'SingleBest':return position===0?weight:0;
 default:return weight;
 }
}
const roundMasks={None:0,One:1,Two:2,Three:4,NotOne:6,NotTwo:5,NotThree:3,All:7};
class BetaHandler {
 constructor(kind,settings={},propagate=0,ancestors=[],sourceXml=false){
  this.kind=kind;this.settings=sourceXml||Array.isArray(settings)?originalSettings(settings):asSettings(settings);this.propagate=F(propagate);this.scores=[];
  this.sheet=null;this.children=[];
  if(kind==='Summation'){
   const id=this.settings.SummationName;
   if(ancestors.includes(id))throw new UnportedBetaHandler('Recursive source summation '+id);
   this.sheet=sheets[id]||null;
   if(this.sheet)for(const a of this.sheet.entries)this.children.push(new BetaHandler(a.handler,a.settings,a.propagate,ancestors.concat(id),true));
  }
 }
 add(node,key,value){
  if(value===0||this.kind==='Summation')return;
  const found=this.scores.find(x=>x.node===node&&x.key===key);
  if(found)found.value=F(found.value+F(value));else this.scores.push({node,key,value:F(value)});
 }
 get(node,key){
  if(this.kind==='Summation'){let score=0;for(const c of this.children)score=F(score+c.get(node,key));return score;}
  return this.scores.find(x=>x.node===node&&x.key===key)?.value||0;
 }
 cleanup(){this.scores=[];} // Source Summation does NOT override child cleanup.
 addAll(node,items,kind){for(const x of items)this.add(node,propagatedKey(x,kind),this.propagate);}
 canBranchPlacement(){return ['PlayAll','Power','PowerRange','Location','Wedge','Occurrence','OccurrenceRange'].includes(this.kind);}
 filter(ctx,request){
  const s=this.settings,k=request.kind,raw=request.items;
  const actor=ctx.actor,loyalty=s.PlayerType??'Both',tier=Number(s.CardGroup??15);
  const high=(s.SortOrder??'Highest')==='Highest',negate=s.Negate??false;
  const cards=k==='targets'||k==='choices'||k==='templates';
  let items=byPlayer(raw,actor,loyalty);
  switch(this.kind){
  case 'Preference':{
   const p=ctx.personality;
   if(!p)throw new UnportedBetaHandler('Preference handler needs source personality');
   if(cards)items=byTier(items,tier);
   const preference=x=>cards?p.semanticTags.reduce((score,t)=>score+(x.semanticTags.includes(t.id)?t.weight:0),0):
    x.row===1?p.MeleePreference:x.row===2?p.RangedPreference:x.row===4?p.SiegePreference:0;
   return items.sort((a,b)=>(preference(b)-preference(a))*(high?1:-1));
  }
  case 'Occurrence':case 'OccurrenceRange':{
   const fits=count=>this.kind==='Occurrence'||(count>=Number(s.MinRange??0)&&count<=Number(s.MaxRange??0));
   const template=Number(s.TemplateId??0);
   if(!cards){
    const count=x=>{const value=ctx.state.cards.filter(c=>c.side===x.side&&c.zone===x.row&&(template===0||c.templateId===template)).length;return fits(value)?value:0;};
    // Out-of-range rows get score0, rather than being removed by the source.
    return items.sort((a,b)=>(count(b)-count(a))*(high?1:-1));
   }
   // Literal source: target path overwrites its player filter with raw tier
   // filtering; both card paths ultimately rank ALL original request items.
   let source=byTier(k==='targets'?raw:items,tier);
   if(template!==0)source=source.filter(c=>c.templateId===template);
   const destination={Deck:16,Hand:8,Graveyard:32,Board:7}[s.Destination??'MatchSource'];
   const pool=destination===undefined?byPlayer(source,actor,loyalty):byPlayer(ctx.state.cards.filter(c=>(c.zone&destination)!==0),actor,loyalty);
   const count=x=>pool.filter(c=>c.templateId===x.templateId).length;
   return raw.slice().sort((a,b)=>(count(b)-count(a))*(high?1:-1)).filter(c=>fits(count(c)));
  }
  case 'Wedge':{
   if(k!=='play')return null; // Source registers None for target/choice/row.
   const template=Number(s.TemplateId??0),semantic=Number(s.SemanticTagId??1),wedge=s.WedgeType??'LeftOf';
   const unconstrained=semantic<=1&&template===0&&tier===15;
   const passes=c=>c&&(c.templateTier&tier)!==0&&(template===0||((c.templateId===template)!==negate))&&
    (semantic<=1||(c.semanticTags.includes(semantic)!==negate));
   const scored=[];let maximum=-2147483648;
   for(const position of items){
    const relevant=wedge==='InBetween'?[position.index,position.index-1]:[wedge==='LeftOf'?position.index:position.index-1];
    const neighbours=relevant.map(index=>ctx.state.cards.find(c=>c.side===position.side&&c.zone===position.row&&c.index===index));
    if(neighbours.some(c=>!c||(!unconstrained&&!passes(c))))continue;
    const value=neighbours.reduce((sum,c)=>sum+c.power*(high?1:-1),0);
    if(unconstrained){if(value<maximum)continue;if(value>maximum){scored.length=0;maximum=value;}}
    scored.push({position,value});
   }
   return scored.sort((a,b)=>b.value-a.value).map(x=>x.position);
  }
  case 'PlayAll':
   if(k!=='play'&&request.min!==1&&request.max!==1)return null;
   return items;
  case 'Random':{
   if(!ctx.next)throw new UnportedBetaHandler('Source SimulatorRandom not supplied');
   if(k==='play')return raw.length?[raw[ctx.next(0,raw.length)]]:null; // Source ignores PlayerType here.
   if(cards)items=byTier(items,tier);
   const count=ctx.next(request.min,request.max+1),pool=items.slice(),picked=[];
   while(picked.length<count&&pool.length){const i=ctx.next(0,pool.length);picked.push(pool[i]);pool.splice(i,1);}return picked;
  }
  case 'Power':case 'PowerRange':{
   if(cards)items=byTier(items,tier);
   const power=x=>cards?x.power:rowPower(ctx,x,k==='play'?tier:15);
   if(this.kind==='PowerRange'&&k!=='play')items=items.filter(x=>power(x)>=Number(s.MinRange??0)&&(Number(s.MaxRange??0)===0||power(x)<=Number(s.MaxRange)));
   if(k==='play'){
    if(!items.length)return [];
    const best=Math.max(...items.map(x=>rowPower(ctx,x,tier)*(high?1:-1)));
    return items.filter(x=>rowPower(ctx,x,tier)*(high?1:-1)===best);
   }
   return items.sort((a,b)=>(power(b)-power(a))*(high?1:-1));
  }
  case 'TemplateId':
   if(!cards)return null;
   // Original computes FilterByPlayer, then accidentally uses the raw list.
   return raw.filter(x=>(x.templateId===Number(s.TemplateId??0))!==negate);
  case 'Semantic':
   return cards?byTier(items,tier).filter(x=>x.semanticTags.includes(Number(s.SemanticTagId??1))!==negate):null;
  case 'HasTagsToken':{
   const mask=flags(s.TagsTokenType??'Resilience',tokenNames);
   return cards?byTier(items,tier).filter(x=>((x.tokens&mask)!==0)!==negate):null;
  }
  case 'Location':{
   const mask=flags(s.Location??'Active',locationNames);
   if(cards){
    const at=(s.LocationAction??'CanGotoLocation')==='IsAtLocation';
    return byTier(items,tier).filter(x=>at?(mask===767||(x.zone&mask)!==0):((((x.placement?.player??0)|(x.placement?.opponent??0))&7&mask)!==0));
   }
   return items.filter(x=>(x.row&mask)!==0);
  }
  case 'UnitOrEvent':{
   if(!cards)return null;
   const mask=flags(s.UnitOrEvent??14,{Event:2,Unit:4,UnitEvent:8});
   return byTier(items.filter(x=>(x.type&mask)!==0),tier);
  }
  case 'Health':{
   if(!cards)return null;const health=flags(s.Health??'Neutral',{Neutral:1,Damaged:2,Boosted:4});
   return byTier(items,tier).filter(c=>((c.power===c.basePower?1:c.power<c.basePower?2:4)&health)!==0);
  }
  case 'RowWithNumberOfUnits':case 'RowWithUnitStrength':case 'RowWithEffect':case 'RowWithCeiling':{
   const row=x=>({side:x.side,row:cards?x.zone:x.row});
   const score=x=>{
    const r=row(x),onRow=rowCards(ctx,r,tier);
    if(this.kind==='RowWithNumberOfUnits')return onRow.length;
    if(this.kind==='RowWithUnitStrength')return onRow.reduce((n,c)=>n+c.power,0);
    // Original GetCeiling iterates the cleared scratch list without filling it.
    if(this.kind==='RowWithCeiling')return 0;
    const effect=flags(s.EffectType??'Hazard',{Invalid:0,Hazard:1,Boon:2,All:3});
    const token=ctx.state.rows.find(x=>x.side===r.side&&x.row===r.row)?.token||0;
    return (((effect&tokenType(token))!==0)===!negate)?1:0;
   };
   // Source multiplies by -1 for Lowest AND sorts ascending: both orderings
   // rank greater underlying row scores first. Retain this literal behavior.
   return items.sort((a,b)=>score(b)-score(a));
  }
  case 'Summation':{
   if(this.sheet===null)return null;
   const rankings=raw.map(x=>({item:x,value:0}));
   for(let j=0;j<this.children.length;j++){
    const a=this.sheet.entries[j],mask=roundMasks[a.rounds]??7;
    if(mask!==0&&mask!==7&&(ctx.state.roundIndex<0||ctx.state.roundIndex>2))throw Error('Invalid source summation round');
    if((mask&(1<<ctx.state.roundIndex))===0)continue;
    const child=this.children[j],filtered=child.filter(ctx,request);
    if(filtered===null)continue;
    for(let i=0;i<filtered.length;i++){
     const key=itemKey(filtered[i],k),entry=rankings.find(x=>itemKey(x.item,k)===key);
     if(!entry)throw Error('Source handler returned candidate outside request');
     entry.value=F(entry.value+summationWeight(a,i,filtered.length,k==='play'?1:request.min,k==='play'?1:request.max));
    }
    child.addAll(ctx.node,filtered,k);
   }
   return rankings.sort((a,b)=>b.value-a.value).map(x=>x.item);
  }
  default:throw new UnportedBetaHandler('Original handler not ported: '+this.kind);
  }
 }
}
// BaseCardHandler.Get*Decision picks up to max, regardless of the NumCards
// setting of subclasses. Original invalid-decision repair adds request-order
// candidates until min; this is source fallback, never the mod's policy.
function decision(handler,ctx,request){
 const filtered=handler.filter(ctx,request);let chosen=[];
 if(filtered!==null)for(const x of filtered)if(chosen.length<request.max&&!chosen.some(y=>itemKey(y,request.kind)===itemKey(x,request.kind)))chosen.push(x);
 const valid=chosen.length>=request.min&&chosen.length<=request.max;
 if(!valid)for(const x of request.items){
  if(!chosen.some(y=>itemKey(y,request.kind)===itemKey(x,request.kind)))chosen.push(x);
  if(chosen.length>=request.min)break;
 }
 let propagated=0;
 if(valid){for(const x of chosen)propagated=F(propagated+handler.get(ctx.node,propagatedKey(x,request.kind)));handler.cleanup();}
 const branches=handler.kind==='PlayAll'&&filtered!==null?filtered.slice(1).map(x=>[x]):[];
 return {chosen,branches,propagated,filtered,sourceFallback:!valid};
}
module.exports={BetaHandler,UnportedBetaHandler,resolveAssociation,sourceHint,summationWeight,decision,originalSettings,
 byPlayer,byTier,rowPower,propagatedKey,tokenType,flags};
