'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const board=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
const recipes=JSON.parse(fs.readFileSync('BetaGwent/ui/assets/elements164/recipes.json','utf8'));
const proof=JSON.parse(fs.readFileSync('docs/evidence/elements164.json','utf8'));
const catalog=JSON.parse(fs.readFileSync('data/beta924/planning/full_catalog.json','utf8')).cards;
function fn(name){const start=board.indexOf('function '+name+'('),open=board.indexOf('{',start);assert(start>=0,name);let i=open+1,d=1;while(d){if(board[i]==='{')d++;if(board[i]==='}')d--;i++;}return board.slice(start,i).replace(/:(?:Sprite|String|Object|void|int|uint|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))');}
let checks=0;function check(v,n){assert(v,n);checks++;}
const c=vm.createContext({Math,Object,Array,int:v=>v|0});
Object.assign(c,{weatherRows:[],previousPoses:{},reducedMotion:false,activeCue:{kind:1,source:1},animations:[],draws:[],
 BetaGwentElementData164:{preset:n=>recipes.presets[n]},BetaGwentFullCatalog:{find:id=>catalog.find(x=>x.templateId===id)},
 poseX:p=>p.x+p.width/2,poseY:p=>p.y+p.height/2,poseW:p=>p.width,poseH:p=>p.height,cueImpactTime:()=>420,
 drawElement164:(fx,name,x,y,w,h,delay,budget,cap)=>{c.draws.push({name,x,y,w,h,delay,cap});return true;}});
vm.runInContext(['landingPrefab178','transformPrefab178','presentationDuration178','presentationFloor178','drawPresentation178','drawLandingCue','drawSummonCue','queueTransformation178'].map(fn).join('\n'),c);
const pose={id:1,x:500,y:600,width:80,height:112,zone:1,side:1,templateId:132308};
for(const [token,name] of [[0,'CardLandingEffect'],[1,'CardFrostLandingEffect'],[2,'CardMistLandingEffect'],[4,'CardRainLandingEffect'],[64,'CardRainLandingEffect']]){
 c.weatherRows=[{side:1,zone:1,token}];c.draws=[];c.drawLandingCue({},pose,0,600);
 check(c.draws.length===1&&c.draws[0].name===name&&c.draws[0].delay===600,'landing chooses source prefab and arrival');
 check(recipes.presets[name].emitters.length>0&&recipes.presets[name].duration>.7,'step emission produces actual landing particles');
}
c.draws=[];c.drawLandingCue({},Object.assign({},pose,{templateId:112101}),0,600);check(c.draws.map(d=>d.name).includes('GoldLanding'),'gold adds its original landing overlay');
c.previousPoses[1]={zone:1};c.draws=[];c.drawLandingCue({},Object.assign({},pose,{templateId:112101}),0,600);check(c.draws.filter(d=>d.name==='GoldLanding').length===1,'intermediate placed-card snapshot cannot suppress gold landing');
c.activeCue={kind:8,source:1};c.draws=[];c.drawLandingCue({},Object.assign({},pose,{templateId:112101}),0,600);check(c.draws.every(d=>d.name!=='GoldLanding'),'gold timer/turn trigger never repeats landing');c.previousPoses={};
c.activeCue={kind:1,source:1};c.draws=[];c.drawLandingCue({},Object.assign({},pose,{templateId:200055}),0,600);check(c.draws.every(d=>d.name!=='GoldLanding'),'leader never gets gold landing overlay');
c.activeCue={kind:15,source:5,target:1};c.draws=[];c.drawSummonCue({},null,pose);check(c.draws[0].name==='SpawnBlink'&&c.draws[0].delay===420&&c.draws.length===2,'summon blink and landing share card arrival');
c.reducedMotion=true;c.draws=[];c.drawSummonCue({},null,pose);check(c.draws.length===0,'reduced motion suppresses presentation particles');c.reducedMotion=false;
for(const [a,b,name] of [[132308,112101,'NatureTransform'],[112101,132308,'NatureTransform'],[132308,201624,'NatureTransform']]){
 const before={id:2,templateId:a},after={id:2,templateId:b};check(c.transformPrefab178(before,after)===name,'template tier change never substitutes a promote operation');
 check(c.presentationFloor178({kind:10,target:2},[before],[after])>=recipes.presets[name].duration*1000,'transform is not truncated by replay');
}
check(c.presentationFloor178({kind:1,templateId:200055},[],[])===0,'leader play adds no VFX pause');
check(c.presentationFloor178({kind:1,templateId:112101},[],[])>=2100,'gold overlay finishes after landing');
check(c.presentationFloor178({kind:8,target:2},[{id:2,tokens:8}],[{id:2,tokens:0}])>=1500,'ambush leaves finish after flip');
check(c.presentationFloor178({kind:8,target:2},[{id:2,tokens:0}],[{id:2,tokens:0}])===0,'ordinary triggers do not inherit ambush pause');
const old={x:10,y:20},next={x:10,y:20,alpha:1};c.animations=[];c.queueTransformation178(old,next);
check(c.animations.length===2&&c.animations.every(m=>m.fromX===m.toX&&m.fromY===m.toY&&!m.fromScaleX)&&next.alpha===0,'transformation replaces art in place without mirrored flip');
const registry=JSON.parse(fs.readFileSync('docs/evidence/special-vfx142.json','utf8')).registry;
check(registry.CardTransformAttackVFXHandlerData.rows[0].effects['0'].prefab==='NatureTransform','source registry default for transformation');
const blend=fs.readFileSync('BetaGwent/ui/src/BetaGwentElementBlend173.as','utf8');
const ids=new Set([...blend.matchAll(/"(\d+)":1/g)].map(m=>+m[1]));
for(const e of proof.sourceParticles)check(ids.has(e.particle)===e.shader.includes('Additive'),'blend matches material '+e.particle);
check(!fn('drawSummonCue').includes('betaBurst')&&!fn('drawLandingCue').includes('drawEllipse'),'no substitute rings or generic summon sparkles');
check(!fn('drawVisualCue').includes('beginFill(0x7BD6C4'),'no painted rectangle over transformation');
check(!fn('drawCards').includes('ЗАСАДА!'),'ambush does not cover cards with redundant label');
check(board.includes('presentationFloor178(timed.cue,priorCards,timed.cards)'),'production replay timing uses source effect duration');
// Acquired markers only disappear after an explicit inspection acknowledgement.
vm.runInContext(`var collectionNew={42:true},collectionSeenPending={},collectionBadges178={},effectGallery=false,editingDeck=true,browsingCatalog=false,sent=[];
function send(n,a){sent.push([n,a]);}var content={contains(){return false;}};function uiTween(){}`+['markCollectionSeen','setCollectionNew'].map(fn).join('\n'),c);
c.markCollectionSeen(42);c.markCollectionSeen(42);check(c.sent.length===1&&c.collectionNew[42],'hover sends one acknowledgement request without prematurely clearing saved flag');
c.setCollectionNew(42,false);check(!c.collectionNew[42]&&!c.collectionSeenPending[42],'native acknowledgement clears marker without rerender');
c.effectGallery=true;c.collectionNew[43]=true;c.markCollectionSeen(43);check(c.sent.length===1,'debug gallery never mutates new-card flags');
const report={stage:178,checks,actualActionScript:true,sourceMaterials:true,nativeGameTested:false};fs.writeFileSync('docs/evidence/presentation178.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
