'use strict';
// Independent evaluator of Beta 0.9.24 list/choice/play graph fragments.
// It reads only the normalized Beta catalog and C#-derived semantics noted
// below, and observes the fixture through card snapshots. It never calls mod
// rule handlers. RNG values are replayed from the traced draws, with each draw
// bound validated against the Beta algorithm (ListExt.Shuffle/GetRandom).
const {catalog}=require('./source_graph095.cjs');
const T=new Map(catalog.templates.map(t=>[t.templateId,t]));
const killed=new Set(catalog.abilities.filter(a=>a.nodes.some(n=>n.type==='KilledTrigger')).map(a=>a.templateId));
const big=t=>t.categoryWords.map(w=>BigInt(w.decimal));
function graphOf(tid){const g=catalog.abilities.filter(a=>a.templateId===tid&&a.nodes.length);if(g.length!==1)throw Error('expected one graph '+tid);return g[0];}
function literal(ch){
 const a=ch.attributes;if(a.V!==undefined)return a.V;
 const defs=[];const rec=x=>{for(const y of x.children){if(y.attributes.TemplateId!==undefined)defs.push(+y.attributes.TemplateId);rec(y);}};rec(ch);
 if(a.Type==='CardDefinitionVar')return defs[0]||0;if(a.Type==='CardDefinitionListVar')return defs;
 if(a.Type==='CardCategoryVar'){const vs=[];const r=x=>{for(const y of x.children){if(y.attributes.V!==undefined)vs.push(BigInt(y.attributes.V));r(y);}};r(ch);return vs;}
 if(a.Type==='CardListVar')return [];
 if(a.Type==='AvailabilityVar'){let m=0;const r=x=>{for(const y of x.children){if(y.attributes.V!==undefined)m|=Number(y.attributes.V);r(y);}};r(ch);return m;}
 return undefined;
}
function make(tid){
 const g=graphOf(tid),nodes=new Map(g.nodes.map(n=>[n.nodeId,n])),inc=new Map(),flow=new Map(),vars=new Map();
 for(const e of g.connections){const k=e.destinationPort.nodeId+'.'+e.destinationPort.field;if(e.sourcePort.type==='FlowConnector')flow.set(e.sourcePort.nodeId+'.'+e.sourcePort.field,e.destinationPort.nodeId);else inc.set(k,[e.sourcePort.nodeId,e.sourcePort.field]);}
 for(const x of g.sourceTree.children)if(x.tag.endsWith('Variables'))for(const v of x.children)vars.set(v.attributes.Id,{name:v.attributes.Name,init:literal(v)});
 const child=(n,f)=>n.sourceTree.children.find(c=>c.tag===f);
 const trig=g.nodes.filter(n=>n.type==='PlayedTrigger');
 return {g,nodes,inc,flow,vars,child,trigger:trig.length===1?trig[0]:null};
}
// ctx: {cards():snapshots, ownerId, draws:[{n,v}]}
function run(tid,ctx){
 const m=make(tid),{nodes,inc,flow,vars,child}=m,state=new Map(),varv=new Map(),log=[],acts=[];let drawIndex=0,spawnSeq=0;
 for(const [id,v]of vars)varv.set(id,Array.isArray(v.init)?[...v.init]:v.init);
 const sim=ctx.cards().map(x=>({...x,power:{...x.power}}));const snaps=()=>sim;const byId=id=>sim.find(s=>s.instanceId===id);
 function relocate(cid,pid,loc,index){const c=byId(cid);if(!c)return;const old=c.locationMask<0?[]:sim.filter(x=>x.positionPlayerId===c.positionPlayerId&&x.locationMask===c.locationMask&&x!==c).sort((a,b)=>a.locationIndex-b.locationIndex);old.forEach((x,i)=>x.locationIndex=i);
  const dst=sim.filter(x=>x.positionPlayerId===pid&&x.locationMask===loc&&x!==c).sort((a,b)=>a.locationIndex-b.locationIndex);let i=index===-2?0:index===-3||index===undefined?dst.length:index===-5?draw(dst.length+1):Math.max(0,Math.min(index,dst.length));dst.splice(i,0,c);dst.forEach((x,k)=>x.locationIndex=k);c.positionPlayerId=pid;c.locationMask=loc;return i;}
 const draw=n=>{if(ctx.autoDraw){drawIndex++;return 0;}const d=ctx.draws[drawIndex++];if(!d&&ctx.optionalDraws){log.push({missingOptionalDraw:n});return 0;}if(!d)throw Error(`missing RNG draw bound ${n}`);if(d.n!==n)throw Error(`RNG bound ${d.n} expected ${n}`);return d.v;};
 const tmpl=s=>T.get(s.runtimeTemplate.templateId);
 function input(n,f,card){
  const k=n.nodeId+'.'+f,src=inc.get(k);if(src)return value(src[0],src[1],card);
  const c=child(n,f);if(!c)return undefined;return literal(c);
 }
 function filterFn(nid,field){
  const n=nodes.get(nid),neg=()=>String(input(n,'Negate'))==='True';
  const wrap=f=>s=>{const r=!!f(s);return neg()?!r:r;};
  switch(n.type){
   case 'FilterCardCategoryNode':{const want=input(n,'CardCategory'),meth=+input(n,'CompareMethod');return wrap(s=>{const have=big(tmpl(s));while(have.length<want.length)have.push(0n);if(meth===0)return want.every((w,i)=>(have[i]&w)===w);return want.some((w,i)=>(have[i]&w)!==0n);});}
   case 'FilterDefinitionNode':return wrap(s=>s.runtimeTemplate.templateId===+input(n,'Definition'));
   case 'FilterDefinitionListNode':return wrap(s=>input(n,'Definitions').includes(s.runtimeTemplate.templateId));
   case 'FilterCardTemplateIdNode':return wrap(s=>+input(n,'TemplateId')===s.runtimeTemplate.templateId);
   case 'FilterHasOnKilledAbilityNode':return wrap(s=>killed.has(s.runtimeTemplate.templateId));
   case 'FilterCardTemplateTokensNode':return wrap(s=>(tmpl(s).fields.Tokens&+input(n,'Tokens'))!==0);
   case 'FilterCardFactionNode':return wrap(s=>(+input(n,'Faction')&tmpl(s).fields.FactionId)!==0);
   case 'FilterCardPowerNode':return wrap(s=>{const p=s.power,type=+input(n,'PowerType'),a=[p.currentPower,p.basePower,p.permanentPower,p.armor][type],b=+input(n,'Power'),op=+input(n,'Op');return [a===b,a!==b,a<b,a>b,a<=b,a>=b][op];});
   case 'FilterCardPlacementNode':return wrap(s=>{const side=+input(n,'PlayerSide'),loc=+input(n,'Location'),pl=tmpl(s).placement;return (side&1)&&(loc&+pl.PlayerSide)!==0||(side&2)&&(loc&+pl.OpponentSide)!==0;});
   case 'FilterCardLogicNode':{const ins=n.sourceTree.children.find(c=>c.tag==='Ins').children.map(c=>{const src=inc.get(n.nodeId+'.'+c.tag);return filterFn(src[0],src[1]);}),op=+input(n,'Op');return wrap(s=>op===0?ins.every(f=>f(s)):ins.some(f=>f(s)));}
   case 'FilterCardTokensNode':return wrap(s=>(s.tokenMask&+input(n,'Tokens'))!==0);
   case 'FilterCardTypeNode':return wrap(s=>(tmpl(s).fields.Type&+(input(n,'Type')??input(n,'CardTypes')))!==0);
   case 'FilterCardTierNode':return wrap(s=>(s.runtimeTierMask&+input(n,'CardTiers'))!==0);
   default:throw Error('unsupported filter '+n.type);
  }
 }
 function value(nid,field,card){
  const n=nodes.get(nid);const key=nid+'.'+field;
  if(state.has(key))return state.get(key);
  switch(n.type){
   case 'GetOwnerPlayerIdNode':return byId(ctx.ownerId).positionPlayerId;
   case 'GetOwnerOpponentPlayerIdNode':return byId(ctx.ownerId).positionPlayerId===1?2:1;
   case 'GetAbilityOwnerCardNode':return ctx.ownerId;
   case 'PlayedTrigger':if(field==='CardPlayed')return ctx.ownerId;if(field==='To'){const o=byId(ctx.ownerId);return {player:o.positionPlayerId,loc:o.locationMask,index:o.locationIndex};}break;
   case 'GetVarNode':{const v=varv.get(n.sourceTree.attributes.VarId);return Array.isArray(v)&&typeof v[0]==='number'&&n.sourceTree.children[0].attributes.Type==='CardDefinitionVar'?v[0]:v;}
   case 'SetVarNode':if(field==='Out')return varv.get(n.sourceTree.attributes.VarId);break;
   case 'GetCardsNode':{
    const pid=+input(n,'PlayerId'),loc=+input(n,'LocationId'),types=+input(n,'CardTypes'),tiers=+input(n,'CardTiers'),ignore=+input(n,'Ignore');
    const out=[];
    for(const p of [1,2]){if((p&pid)===0)continue;for(const l of [1,2,4,8,16,32,64,128,256,512]){if((l&loc)===0)continue;
     snaps().filter(s=>s.positionPlayerId===p&&s.locationMask===l).sort((a,b)=>a.locationIndex-b.locationIndex).forEach(s=>{
      if(s.isInExecutionStack||s.isWaitingToDie)return;const t=tmpl(s);
      if(types!==14&&(t.fields.Type&types)===0)return;if(tiers!==15&&(s.runtimeTierMask&tiers)===0)return;if(ignore&&(s.tokenMask&ignore)!==0)return;out.push(s.instanceId);});}}
    return out;}
   case 'GetCardTemplateIdNode':return byId(input(n,'DS')).runtimeTemplate.templateId;
   case 'GetCardPowerNode':{const s=byId(input(n,'DS')),p=s.power;return [p.currentPower,p.basePower,p.permanentPower][+input(n,'PowerType')];}
   case 'CardListElementToListNode':{const e=input(n,'DS');return e?[e]:[];}
   case 'CardListLengthNode':return input(n,'DS').length;
   case 'CardListGetElementNode':{const l=input(n,'DS'),i=+input(n,'I');return l[i]||0;}
   case 'GetCardPlayerIdNode':{const c=byId(input(n,'DS'));return c?c.positionPlayerId:0;}
   case 'IntPlusNode':return +input(n,'A')+ +input(n,'B');
   case 'IntMinusNode':return +input(n,'A')- +input(n,'B');
   case 'IntGetRandomNode':{const a=+input(n,'Min'),b=+input(n,'Max');if(b<=a)return 0;if(!state.has(key))state.set(key,a+draw(b-a));return state.get(key);}
   case 'MakeCardPositionNode':return {player:+input(n,'PlayerId'),loc:+input(n,'Location'),index:+input(n,'Index')};
   case 'GetLastAvailableIndexNode':return -3;
   case 'GetOwnerLocationNode':return byId(ctx.ownerId).locationMask;
   case 'CardDefinitionListGetElementNode':{const l=input(n,'DS')||[],i=+input(n,'I');return l[i]||0;}
   case 'GetTemplateIdNode':return +input(n,'DS')||0;
   case 'IntCompareNode':{const a=+input(n,'A'),b=+input(n,'B'),op=+input(n,'Op');return [a===b,a!==b,a<b,a>b,a<=b,a>=b][op];}
   case 'GetCardsDefinitionsNode':case 'GetInitialDeckDefinitions':{
    const fac=+input(n,'Faction')||0,tier=+input(n,'Tier')||0,type=+input(n,'Type')||0,tok=+input(n,'Tokens')||0,kind=+input(n,'Kind'),av=input(n,'Availability'),cat=input(n,'Category'),cm=+input(n,'CategoryCompare'),ps=+input(n,'PlayerSide')||0,os=+input(n,'OpponentSide')||0;
    const avMask=Number(av)||0;const catW=Array.isArray(cat)?cat:[];
    let pool;if(n.type==='GetInitialDeckDefinitions'){const pid=+input(n,'PlayerId'),uniq=String(input(n,'Unique'))!=='False';pool=[];for(const p of [1,2])if(p&pid){for(const t of ctx.initialDeck(p))if(!uniq||!pool.includes(t))pool.push(t);}}
    // GameSharedData.LoadTemplates walks the XML source order and inserts once
    // into SharedRuntimeTemplates; GetCardsDefinitions enumerates its Values.
    else pool=[...T.values()].sort((a,b)=>a.sourceIndex-b.sourceIndex).map(t=>t.templateId);
    const out=pool.filter(id=>{const t=T.get(id);if(!t)return false;const f=t.fields;if(avMask&&!((avMask>>Number(t.attributes.Availability))&1))return false;if(kind&&!(kind&f.Kind))return false;if(fac&&!(fac&f.FactionId))return false;if(tier&&!(tier&f.Tier))return false;if(type&&!(type&f.Type))return false;if(tok&&!(tok&f.Tokens))return false;
     if(ps&&ps!==767&&!(ps&+t.placement.PlayerSide))return false;if(os&&os!==767&&!(os&+t.placement.OpponentSide))return false;
     if(catW.some(w=>w!==0n)){const have=big(t);while(have.length<catW.length)have.push(0n);if(cm===0){if(!catW.every((w,i)=>(w&have[i])===have[i]))return false;}else if(!catW.some((w,i)=>(w&have[i])!==0n))return false;}return true;});
    log.push({pool:out.slice()});return out;}
   case 'RequestCardTargetsNode':if(field==='TargetsInShape')return state.get(nid+'.SelectedTargets')||[];break;
   case 'GetLocationTokenOfType':{const ty=+input(n,'Type');return (ty&2?(128|256):0)|(ty&1?7807:0);}
   case 'GetLocationsByTokenTypeNode':case 'GetLocationsNode':{const pm=+input(n,'PlayerMask'),lm=+input(n,'LocationMask');const ty=n.type==='GetLocationsByTokenTypeNode'?+input(n,'TokenType'):0;const mask=n.type==='GetLocationsByTokenTypeNode'?((ty&2?(128|256):0)|(ty&1?7807:0)):(+input(n,'TokenMask')||0);
    const out=[];for(const p of [1,2])if(p&pm)for(const l of [1,2,4])if(l&lm){const tok=ctx.rowToken?ctx.rowToken(p,l):0;if(!mask||(tok&mask))out.push({player:p,loc:l});}return out;}
   case 'LocationIdContains':return ((+input(n,'A'))&(+input(n,'B')))!==0;
   case 'PlayerGetHasPassedNode':{const pid=+input(n,'DS');return [1,2].filter(p=>p&pid).every(p=>ctx.hasPassed?ctx.hasPassed(p):false);}
   case 'GetCardTimerNode':{const c=byId(input(n,'DS'));return c?c.timerValue:0;}
   case 'GetRandomIndexNode':return -5;
   case 'BreakCardPositionNode':{const st=nid+'.';if(state.has(st+'PlayerId'))return state.get(st+field);break;}
   case 'LocationIdNegateNode':{const a=+input(n,'DS'),m=+input(n,'LocationMask');return m&~a;}
   case 'IntGetIsEvenNode':return (+input(n,'DS'))%2===0;
   case 'GetCardLocationIdNode':{const c=byId(input(n,'DS'));return c?c.locationMask:0;}
   case 'GetFactionNode':{const c=byId(input(n,'DS'));return c?T.get(c.runtimeTemplate.templateId).fields.FactionId:0;}
   case 'GetCardDefinitionNode':{const c=byId(input(n,'DS'));return c?c.runtimeTemplate.templateId:0;}
   case 'GetRandomLastAvailablePositionNode':{if(state.has(key))return state.get(key);const pid=+input(n,'PlayerId'),loc=+input(n,'Location'),av=[];for(const p of [1,2]){if(!(p&pid))continue;for(const l of [1,2,4])if((l&loc)&&sim.filter(x=>x.positionPlayerId===p&&x.locationMask===l).length<9)av.push({player:p,loc:l,index:-3});}
    const v=av.length?av[draw(av.length)]:{player:0,loc:0,index:-3};state.set(key,v);return v;}
   case 'GetCardPositionOnLeftNode':case 'GetCardPositionOnRightNode':{const c=byId(input(n,'DS'));return c?{player:c.positionPlayerId,loc:c.locationMask,index:c.locationIndex+(n.type==='GetCardPositionOnRightNode'?1:0)}:{player:0,loc:0,index:0};}
   default:if(n.type.startsWith('Filter')&&field==='Out')return filterFn(nid,field);
  }
  throw Error(`unsupported value ${n.type}.${field}`);
 }
 function exec(nid){
  const n=nodes.get(nid),set=(f,v)=>state.set(nid+'.'+f,v);
  switch(n.type){
   case 'PlayedTrigger':return 'FlowOut';
   case 'FilterCardListNode':{const cards=input(n,'Cards'),fs=n.sourceTree.children.find(c=>c.tag==='Filters').children.map(c=>{const src=inc.get(nid+'.'+c.tag);return src?filterFn(src[0],src[1]):()=>true;});
    const keep=[],drop=[];for(const id of cards){const s=byId(id);(fs.every(f=>f(s))?keep:drop).push(id);}set('FilteredCards',keep);set('NotFilteredCards',drop);log.push({filter:keep.slice()});return keep.length?'FlowSuccess':'FlowFail';}
   case 'FilterPowerLevelNode':{
    const cards=input(n,'Cards').map(byId).filter(s=>!((s.tokenMask&8)&&(s.locationMask&7))),mode=+input(n,'PowerFilter'),num=Math.max(+input(n,'Num'),0),ord=[];
    for(const s of cards){const i=ord.findIndex(o=>s.power.currentPower<o.power.currentPower);if(i<0)ord.push(s);else ord.splice(i,0,s);}
    const out=[];const P=s=>s.power.currentPower;
    if(mode===0){for(let i=ord.length-1,k=num;i>=0&&k>0;i--,k--)out.push(ord[i]);}
    else if(mode===1){if(ord.length){let k=num,lvl=P(ord[ord.length-1]);for(let i=ord.length-1;i>=0&&k>0;i--){if(P(ord[i])<lvl){k--;lvl=P(ord[i]);if(k===0)break;}out.push(ord[i]);}}}
    else if(mode===2){for(let i=0,k=num;i<ord.length&&k>0;i++,k--)out.push(ord[i]);}
    else {if(ord.length){let k=num,lvl=P(ord[0]);for(let i=0;i<ord.length&&k>0;i++){if(P(ord[i])>lvl){k--;lvl=P(ord[i]);if(k===0)break;}out.push(ord[i]);}}}
    set('FilteredCards',out.map(s=>s.instanceId));return out.length?'FlowSuccess':'FlowFail';}
   case 'SetVarNode':{const v=input(n,'In');varv.set(n.sourceTree.attributes.VarId,Array.isArray(v)?[...v]:v);return 'FlowOut';}
   case 'CardListShuffleNode':{const src=inc.get(nid+'.List'),list=value(src[0],src[1]);for(let k=list.length;k>1;){k--;const i=draw(k+1);[list[i],list[k]]=[list[k],list[i]];}log.push({shuffle:list.length});return 'FlowOut';}
   case 'CardListGetRangeNode':{const list=input(n,'List'),i=+input(n,'Index'),len=+input(n,'Length');set('TrimmedList',list.slice(i,Math.min(list.length,i+len)));return 'FlowOut';}
   case 'CardListGetRandomElementNode':{const list=input(n,'List');if(String(input(n,'Remove'))==='True')throw Error('remove unsupported');set('Element',list.length?list[draw(list.length)]:0);return 'FlowOut';}
   case 'RequestCardChoiceNode':{const valid=input(n,'ValidChoices'),min=+input(n,'MinChoices'),max=+input(n,'MaxChoices');if(!valid.length||max===0){state.set(nid+'.SelectedChoices',[]);log.push({requestSkipped:true});return 'FlowOut';}return {request:{valid:valid.slice(),min,max,reveal:String(input(n,'RevealChoices'))==='True'},node:nid};}
   case 'MakeCardPositionNode':set('CardPosition',{player:+input(n,'PlayerId'),loc:+input(n,'Location'),index:+input(n,'Index')});return 'FlowOut';
   case 'IntBranchNode':{const a=+input(n,'A'),b=+input(n,'B');return a===b?'FlowOutEqual':a<b?'FlowOutSmaller':'FlowOutBigger';}
   case 'MoveCardsNode':{const cards=input(n,'Cards').slice(),pos=input(n,'Position');if(cards.length&&pos.loc&&pos.player){const cap=(pos.loc&7)?9-sim.filter(x=>x.positionPlayerId===pos.player&&x.locationMask===pos.loc).length:1e9;const moved=cards.slice(0,Math.max(0,cap));const res=[];for(const c of moved){const i=relocate(c,pos.player,pos.loc,pos.index);res.push({id:c,index:i});}acts.push({move:{cards:moved,to:pos,res}});}return 'FlowOut';}
   case 'DrawCardsNode':{const num=Math.max(+input(n,'Num'),0),pid=+input(n,'PlayerId'),rnd=String(input(n,'Random'))==='True';if(!num)return 'FlowOut';
    if(n.sourceTree.children.find(c=>c.tag==='Filters').children.some(c=>inc.get(nid+'.'+c.tag)))throw Error('draw filters unsupported');
    for(const p of [1,2]){if((p&pid)===0)continue;let list=sim.filter(x=>x.positionPlayerId===p&&x.locationMask===16&&!x.isInExecutionStack&&!x.isWaitingToDie).sort((a,b)=>a.locationIndex-b.locationIndex).map(x=>x.instanceId);
     const vsrc=inc.get(nid+'.ValidCards');if(vsrc&&!rnd){const v=value(vsrc[0],vsrc[1]);list=list.filter(x=>v.includes(x));}
     const out=[];for(let j=0;j<Math.min(num,list.length);j++){let c;if(rnd){const i=draw(list.length);c=list.splice(i,1)[0];}else c=list[j];out.push(c);}
     for(const c of out)relocate(c,p,8,-3);acts.push({draw:{player:p,cards:out}});}return 'FlowOut';}
   case 'SpawnCardNode':{const def=+input(n,'Definition');let pos=inc.get(nid+'.Position')?input(n,'Position'):null;const cnt=+input(n,'Count');const sp=input(n,'Spawner');
    if(!pos){const sc=byId(sp);pos={player:sc?sc.positionPlayerId:0,loc:128,index:-3};}if(pos.player===0&&sp){const sc=byId(sp);if(sc)pos={...pos,player:sc.positionPlayerId};}if(pos.loc===256)pos={...pos,loc:128};
    const out=[];if(def&&pos.loc){for(let k=0;k<cnt;k++){if((pos.loc&7)&&sim.filter(x=>x.positionPlayerId===pos.player&&x.locationMask===pos.loc).length>=9)break;const fid='spawn'+(spawnSeq++);sim.push({instanceId:fid,runtimeTemplate:{templateId:def},positionPlayerId:pos.player,locationMask:-1,locationIndex:0,runtimeTierMask:T.get(def).fields.Tier,tokenMask:T.get(def).fields.Tokens,power:{currentPower:T.get(def).fields.Power,basePower:T.get(def).fields.Power,permanentPower:0,armor:T.get(def).fields.Armor}});relocate(fid,pos.player,pos.loc,pos.index);out.push(fid);}acts.push({spawn:{def,pos,cards:out}});}
    set('SpawnedCards',out);return 'FlowOut';}
   case 'RequestCardTargetsNode':{const valid=input(n,'ValidTargets'),max=+input(n,'MaxTargets');if(!valid.length||max<=0){state.set(nid+'.SelectedTargets',[]);return 'FlowOut';}const k=Math.min(max,valid.length);return {request:{valid:valid.slice(),min:k,max:k,targets:true},node:nid,field:'SelectedTargets'};}
   case 'RequestCardTargetsNode_shape':return [];
   case 'CardListForeachNode':{const src=inc.get(nid+'.List'),list=value(src[0],src[1]).slice();for(const el of list){set('Element',el);let c=flow.get(nid+'.FlowFor'),k=0;while(c!==undefined&&k++<40){const r=exec(c);if(typeof r==='object')throw Error('request inside foreach unsupported');c=flow.get(c+'.'+r);}}state.delete(nid+'.Element');return 'FlowOut';}
   case 'CardListAddNode':{const src=inc.get(nid+'.List'),list=value(src[0],src[1]),e=input(n,'Element');if(e)list.push(e);return 'FlowOut';}
   case 'CardListAppendNode':{const src=inc.get(nid+'.List'),list=value(src[0],src[1]),o=input(n,'ListToAppend')||input(n,'Other')||[];list.push(...o);return 'FlowOut';}
   case 'CardListBranchNode':{const l=input(n,'List');return l.length?'FlowOutTrue':'FlowOutFalse';}
   case 'DestroyCardsNode':{const t=input(n,'Targets').slice(),rem=+input(n,'RemovalType');acts.push({destroy:{targets:t,removal:rem}});for(const c of t){const x=byId(c);if(x&&rem===1)relocate(c,x.positionPlayerId,512,-3);}return 'FlowOut';}
   case 'RequestTemplateChoiceNode':{const valid=input(n,'ValidChoices')||[],min=+input(n,'MinChoices'),max=+input(n,'MaxChoices');if(!valid.length||max===0){state.set(nid+'.SelectedChoices',[]);return 'FlowOut';}return {request:{valid:valid.slice(),min:Math.min(min,valid.length),max:Math.min(max,valid.length),templates:true,orderUncertain:log.some(l=>l.poolOrderUncertain)},node:nid};}
   case 'BranchNode':return input(n,'Condition')===true||String(input(n,'Condition'))==='True'?'FlowOutTrue':'FlowOutFalse';
   case 'CardDefinitionListShuffleNode':{const src=inc.get(nid+'.List'),list=value(src[0],src[1]);for(let k=list.length;k>1;){k--;const i=draw(k+1);[list[i],list[k]]=[list[k],list[i]];}return 'FlowOut';}
   case 'CardDefinitionListGetRangeNode':{const list=input(n,'List'),i=+input(n,'Index'),len=+input(n,'Length');set('TrimmedList',list.slice(i,Math.min(list.length,i+len)));return 'FlowOut';}
   case 'CardDefinitionListRemoveNode':{const src=inc.get(nid+'.List'),list=value(src[0],src[1]),e=+input(n,'Element');const i=list.indexOf(e);if(i>=0)list.splice(i,1);return 'FlowOut';}
   case 'CardDefinitionListRemoveListNode':{const src=inc.get(nid+'.List'),list=value(src[0],src[1]),rm=input(n,'ListToRemove')||[];for(const e of rm){const i=list.indexOf(e);if(i>=0)list.splice(i,1);}return 'FlowOut';}
   case 'CardDefinitionListGetRandomElementNode':{const list=input(n,'List');set('Element',list.length?list[draw(list.length)]:0);return 'FlowOut';}
   case 'HasNCopiesOfDefinitions':{const defs=(input(n,'Definitions')||[]).slice().sort((a,b)=>a-b),want=+input(n,'Count');let ok=true,prev=0,cnt=0;for(const d of defs){if(d!==prev){if(prev!==0&&cnt!==want){ok=false;break;}cnt=0;prev=d;}cnt++;}if(cnt!==want)ok=false;log.push({hasNCopies:ok});return ok?'FlowOutTrue':'FlowOutFalse';}
   case 'CardDefinitionListForeachNode':{const src=inc.get(nid+'.List'),list=value(src[0],src[1]).slice();for(const el of list){set('Element',el);let c=flow.get(nid+'.FlowFor'),k=0;while(c!==undefined&&k++<40){const r=exec(c);if(typeof r==='object')throw Error('request inside foreach unsupported');c=flow.get(c+'.'+r);}}state.delete(nid+'.Element');return 'FlowOut';}
   case 'ChangeLocationTokensNode':{const t=input(n,'Targets')||[];acts.push({rowTokens:{targets:t,op:+input(n,'Operation'),tokens:+input(n,'Tokens')}});return 'FlowOut';}
   case 'CardListRemoveNode':{const src=inc.get(nid+'.List'),list=value(src[0],src[1]),e=input(n,'Element');const i=list.indexOf(e);if(i>=0)list.splice(i,1);return 'FlowOut';}
   case 'ChangeCardTimerNode':{const c=input(n,'Card'),op=+input(n,'Operation'),v=+input(n,'Value');acts.push({timer:{card:c,op,value:v}});const x=byId(c);if(x){if(op===2)x.timerValue=v;else if(op===1)x.timerValue+=v;else if(op===0)x.timerValue-=v;}return 'FlowOut';}
   case 'BreakCardPositionNode':{const p=input(n,'CardPosition')||{player:0,loc:0,index:0};set('PlayerId',p.player);set('Location',p.loc);set('Index',p.index);return 'FlowOut';}
   case 'ChangeCategoriesNode':acts.push({categories:{targets:(input(n,'Targets')||[]).slice(),op:+input(n,'Operation')}});return 'FlowOut';
   case 'PlayCardsNode':acts.push({play:input(n,'CardsToPlay').slice()});return 'FlowOut';
   case 'SummonCardsNode':acts.push({summon:input(n,'Cards').slice(),summoner:input(n,'Summoner')});return 'FlowOut';
   case 'ChangePowerNode':{const e={targets:input(n,'Targets').slice(),op:+input(n,'Operation'),type:+input(n,'TargetedPower'),amount:+input(n,'Power'),ignoreArmor:String(input(n,'IgnoreArmor'))==='True'};acts.push({power:e});
    for(const t of e.targets){const c=byId(t);if(!c)continue;const p=c.power;if(e.op===0){if(e.type===1){p.basePower+=e.amount;p.currentPower+=e.amount;}else p.currentPower+=e.amount;}
     else if(e.op===1&&e.type===0){let d=e.amount;if(!e.ignoreArmor){const a=Math.min(p.armor,d);p.armor-=a;d-=a;}p.currentPower-=d;if(p.currentPower<=0&&(c.locationMask&7)){c.isWaitingToDie=true;relocate(t,c.positionPlayerId,32,-3);}}
     else if(e.op===2&&e.type===1){p.basePower=e.amount;}}
    return 'FlowOut';}
   case 'IntForeachNode':{const st=+input(n,'Start'),num=+input(n,'Num');for(let i=st;i<st+num;i++){set('I',i);let c=flow.get(nid+'.FlowFor'),k=0;while(c!==undefined&&k++<40){const r=exec(c);if(typeof r==='object')throw Error('request inside foreach unsupported');c=flow.get(c+'.'+r);}}return 'FlowOut';}
   case 'PopCardsFromStackNode':return 'FlowOut';
   case 'ChangeArmorNode':acts.push({armor:{targets:input(n,'Targets').slice(),op:+input(n,'Operation'),amount:+input(n,'Armor')}});return 'FlowOut';
   case 'ChangeTokensNode':acts.push({tokens:{targets:input(n,'Targets').slice(),op:+input(n,'Operation'),tokens:+input(n,'Tokens')}});return 'FlowOut';
  }
  throw Error('unsupported flow '+n.type);
 }
 // Walk from Played until first request or terminal action.
function finish(){const r={acts:acts.slice(),draws:drawIndex,log,sim};for(const a of acts){for(const k of ['play','summon'])if(a[k]&&!r[k])r[k]=a[k];}if(!acts.length)r.none=true;return r;}
 function go(cur){let steps=0;while(cur!==undefined&&steps++<60){const r=exec(cur);if(typeof r==='object'){r.draws=drawIndex;r.log=log;r.acts=acts.slice();r.resume=sel=>resume(r,sel);return r;}cur=flow.get(cur+'.'+r);}return finish();}
 return go(m.trigger.nodeId);
 function resume(r,selected){state.set(r.node+'.'+(r.field||'SelectedChoices'),selected.slice());return go(flow.get(r.node+'.FlowOut'));}
}
module.exports={run,make,T,killed};
