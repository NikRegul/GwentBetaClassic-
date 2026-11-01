'use strict';
// Freeze the independent graph facts for the scope198 list family. Reads only the Beta catalog.
const fs=require('fs'),crypto=require('crypto'),{catalog}=require('./source_graph095.cjs'),E=require('./beta_list_eval096.cjs');
const ids=JSON.parse(process.argv[2]),out=process.argv[3],sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const records=[];
for(const tid of ids){
 const m=E.make(tid),g=m.g,get=(n,f)=>{const c=m.child(n,f);return c&&c.attributes.V;};
 const gc=g.nodes.filter(n=>n.type==='GetCardsNode');if(gc.length!==1)throw Error('GetCards count '+tid);
 const n=gc[0],pidSrc=m.inc.get(n.nodeId+'.PlayerId'),pidNode=pidSrc&&m.nodes.get(pidSrc[0]);
 const player=pidNode?{GetOwnerPlayerIdNode:'own',GetOwnerOpponentPlayerIdNode:'enemy'}[pidNode.type]:({1:'p1',2:'p2',3:'both'})[get(n,'PlayerId')];
 const loc=+get(n,'LocationId'),types=+get(n,'CardTypes'),tiers=+get(n,'CardTiers'),ignore=+get(n,'Ignore');
 const cats=g.nodes.filter(x=>x.type==='FilterCardCategoryNode'&&get(x,'Negate')!=='True').map(x=>{const v=[];const r=y=>{for(const z of y.children){if(z.attributes.V!==undefined)v.push(BigInt(z.attributes.V));r(z);}};r(m.child(x,'CardCategory'));return v;});
 const defs=[];for(const x of g.nodes.filter(x=>x.type==='FilterDefinitionNode'||x.type==='FilterDefinitionListNode')){const s=m.inc.get(x.nodeId+'.'+(x.type==='FilterDefinitionNode'?'Definition':'Definitions'));if(s){const v=m.nodes.get(s[0]);const val=m.vars.get(v.sourceTree.attributes.VarId);if(val)defs.push(...[].concat(val.init));}}
 const req=g.nodes.find(x=>x.type==='RequestCardChoiceNode');let min=null;if(req){const s=m.inc.get(req.nodeId+'.MinChoices');min=s?+m.vars.get(m.nodes.get(s[0]).sourceTree.attributes.VarId).init:+get(req,'MinChoices');}
 const cand=catalog.templates.filter(t=>(t.fields.Type===2||t.fields.Type===4)&&(types===14||(t.fields.Type&types))&&(tiers===15||(t.fields.Tier&tiers))&&t.attributes.Availability!=='0'&&(!cats.length||cats.some(c=>c.some((w,i)=>(BigInt((t.categoryWords[i]||{decimal:'0'}).decimal)&w)!==0n)))&&(!defs.length||defs.includes(t.templateId))&&t.templateId!==tid).map(t=>t.templateId);
 const chain=JSON.parse(fs.readFileSync(process.env.HOME+'/work/aud/chains.json','utf8'))[tid];
 // Static candidates: run the independent evaluator over one fake snapshot per template in the source zone.
 const ownerT=catalog.templates.find(t=>t.templateId===tid),fake=[{instanceId:-1,runtimeTemplate:{templateId:tid},positionPlayerId:1,locationMask:2,locationIndex:0,runtimeTierMask:ownerT.fields.Tier,tokenMask:0,power:{currentPower:ownerT.fields.Power,basePower:ownerT.fields.Power,permanentPower:0,armor:0}}];
 const srcP=player==='enemy'?2:1;let k=0;
 for(const t of catalog.templates)if((t.fields.Type===2||t.fields.Type===4)&&t.attributes.Availability!=='0')fake.push({instanceId:t.templateId===tid?tid+0.5:t.templateId,runtimeTemplate:{templateId:t.templateId},positionPlayerId:srcP,locationMask:loc&-loc,locationIndex:k++,runtimeTierMask:t.fields.Tier,tokenMask:0,power:{currentPower:Math.min(t.fields.Power,ownerT.fields.Power),basePower:t.fields.Power,permanentPower:0,armor:0}});
 const x=E.run(tid,{ownerId:-1,autoDraw:true,cards:()=>fake});const passIds=(x.log&&x.log.find(l=>l.filter)||{}).filter||(x.request&&x.request.valid)||x.play||x.summon||[];
 let st=passIds.filter(i=>i>0).map(i=>Math.floor(i));const post=g.nodes.some(x=>['ChangePowerNode','ChangeArmorNode','ChangeTokensNode'].includes(x.type));
 if(post){const van=st.filter(t=>!catalog.abilities.some(a=>a.templateId===t&&a.nodes.length));if(van.length)st=van;}const pick=[];for(let i=0;i<st.length&&pick.length<8;i+=Math.max(1,Math.floor(st.length/8)))pick.push(st[i]);
 records.push({id:tid,graph:{nid:g.nid,sha256:sha(JSON.stringify(g.sourceTree))},chain,source:{player,location:loc,types,tiers,ignore},categoryFiltersPositive:cats.map(c=>c.map(String)),definitionFilters:defs,minZero:min===0,candidates:pick,staticPassCount:st.length,post,
  expected:'Played: '+chain.join(' || ')+`. GetCards ${player}/${loc} types${types} tiers${tiers} ignore${ignore}; filters, shuffle (Fisher-Yates N-1 Next(k+1)), range, GetRandom Next(count), RequestCardChoice min/max/empty-skip, PlayCards/SummonCards evaluated by beta_list_eval096 from the pre-ability snapshot.`});
}
fs.writeFileSync(out,JSON.stringify({schema:1,scope:'scope198 list family primary chains',independentExpectationsBeforeHandlers:true,allBranchesComplete:false,evaluator:{file:'tools/ai/beta_list_eval096.cjs',sha256:sha(fs.readFileSync(__dirname+'/beta_list_eval096.cjs'))},csharp:['GetCardsNode','BoardManager','Location','FilterCardListNode','FilterCardCategoryNode','BitArray','AFilterNode','FilterDefinitionNode','FilterPowerLevelNode','AListShuffleNode','ListExt','AListGetRangeNode','AListGetRandomElementNode','RequestCardChoiceNode','ARequestChoiceNode','PlayCardsNode','SummonCardsNode','EnumExtensions'].map(n=>({n,sha256:sha(fs.readFileSync('BetaGwent/build-inputs/reference/beta-original-csharp/GwentGameplay/'+n+'.cs'))})),records},null,1)+'\n');
console.log(records.length,records.map(r=>r.id+':'+r.source.player+'/'+r.source.location+':'+r.candidates.length).join(' '));
