'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const board=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8'),source=fs.readFileSync('BetaGwent/ui/src/BetaGwentEffectGallery168.as','utf8'),routing=fs.readFileSync('BetaGwent/ui/src/BetaGwentSpecialVfx.as','utf8'),native=fs.readFileSync('BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws','utf8');
function fn(src,name){let a=src.indexOf('function '+name+'('),o=src.indexOf('{',a),i=o+1,d=1;assert(a>=0,name);while(d){if(src[i]==='{')d++;if(src[i]==='}')d--;i++;}return src.slice(a,i).replace(/:(?:String|Object|Sprite|void|int|uint|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2))');}
const recipes=JSON.parse(fs.readFileSync('BetaGwent/ui/assets/elements164/recipes.json','utf8')),catalog=JSON.parse(fs.readFileSync('data/beta924/planning/full_catalog.json','utf8')).cards;
const c=vm.createContext({Math,String,Number,Object,int:v=>v|0});c.catalog=catalog;c.recipes=recipes;
c.PREFABS=JSON.parse(/PREFABS:Object=(\{[^\n]+\});/.exec(routing)[1]);
vm.runInContext(fn(routing,'prefabs')+`var BetaGwentSpecialVfx={prefabs},BetaGwentElementData164={names(){return Object.keys(recipes.presets);}},BetaGwentFullCatalog={all(){return catalog;},find(id){return catalog.find(c=>c.templateId==id);}};`+['entries','card','scene'].map(n=>fn(source,n)).join('\n'),c);
let checks=0;function check(v,n){assert(v,n);checks++;}
const entries=c.entries();check(entries.length>270,'gallery includes current card operations and scenario cases');
check(entries.filter(x=>x.preset).length===0,'default gallery never bypasses the current battle renderer with old raw presets');
check(c.entries(true).filter(x=>x.preset).length===Object.keys(recipes.presets).length,'raw source presets remain available only when explicitly requested internally');
for(const id of [201657,200301,200218,200224,113301,113309,112102,113303,113401])check(entries.some(x=>x.templateId===id),'reported card reachable '+id);
for(const entry of entries){const scene=c.scene(entry);check(scene.before.length===4&&scene.after.length>=1&&scene.after.length<=4,'bounded scene '+entry.title);check(new Set(scene.before.map(c=>c.id)).size===4,'stable unique identities '+entry.title);check(scene.before!==scene.after&&scene.before[0]!==scene.after[0],'detached before/after '+entry.title);check(scene.after.every(c=>[1,2].includes(c.side)&&Number.isFinite(c.power)&&Number.isFinite(c.index)),'finite public fixture '+entry.title);}
// Exercise the current damage/boost renderer with real scene deltas and bindings,
// rather than merely checking that the gallery contains card names.
c.BetaGwentElementData164.preset=name=>recipes.presets[name];
Object.assign(c,{activeCue:{},reducedMotion:false,draws:[],strikes:[],boosts:[],cueImpactTime:()=>380,
 poseX:p=>p.x+p.width/2,poseY:p=>p.y+p.height/2,poseW:p=>p.width,poseH:p=>p.height,
 rowGeometry:(side,row)=>({x:500,y:row*100,w:900,h:100}),
 drawElement164:(fx,name)=>{c.draws.push(name);return true;},drawStrike173:()=>c.strikes.push('strike'),drawBoostCue:()=>c.boosts.push('boost')});
vm.runInContext(fn(board,'drawElementCue164'),c);
const plans=new Set();
for(const entry of entries.filter(e=>e.kind===2)){
 const scene=c.scene(entry);c.activeCue=scene.cue;c.draws=[];c.strikes=[];c.boosts=[];
 const hits=scene.cue.hitTargets.map(id=>{const a=scene.after.find(p=>p.id===id),b=scene.before.find(p=>p.id===id);return {...a,x:500,y:a.zone*100,width:80,height:110,delta:a.power-b.power,armorDelta:a.armor-b.armor};});
 c.drawElementCue164({},hits,800,700,{});plans.add([...c.draws,...c.strikes,...c.boosts].join(','));
 if(entry.mode==='crow')check(c.draws.filter(n=>n==='PowerDarkMagicProjectile').length===3,'Crow sends one dark projectile to each of three rows');
 if(entry.mode==='parasiteBoost')check(hits[0].delta===12&&c.draws.includes('PowerDirectLightMagic')&&!c.draws.includes('PowerDarkMagicProjectile'),'Parasite boost uses +12 and current light impact');
 if(entry.mode==='parasiteDamage')check(hits[0].delta===-9&&c.draws.includes('PowerDarkMagicProjectile'),'Parasite damage has its own dark projectile');
 if(entry.mode==='huntBoost')check(hits.length===3&&hits.every(h=>h.delta>0)&&!c.draws.some(n=>/SideIce/.test(n)),'Hunt boost uses compact current arrivals');
}
check(plans.size>=10,'gallery reaches distinct current rendering plans instead of one generic effect');
check(new Set(entries.slice(0,12).map(e=>e.kind)).size>=4,'opening samples include several real operations');
for(const id of [113309,112102,113308]){const scene=c.scene(entries.find(e=>e.templateId===id&&e.kind===3));check(scene.after.length===1&&scene.cue.hitTargets.length===3,'mass destruction previews all victims '+id);}
vm.runInContext(`var galleryEntries=entries(),galleryIndex=0,effectGallery=true,shown=[];function galleryShow(index){galleryIndex=index;shown.push(index);}`+['galleryStep','galleryRepeat'].map(n=>fn(board,n)).join('\n'),c);
c.galleryStep(-1);check(c.galleryIndex===entries.length-1,'previous wraps from first');c.galleryStep(1);check(c.galleryIndex===0,'next wraps from last');c.galleryRepeat();check(c.shown.at(-1)===0,'repeat retains selected sample');
check(!/send\("OnBetaGwent(?:BoardPlay|Leader|DeckEditor|Collection|Keg)/.test(fn(board,'galleryShowScene')),'preview never sends a gameplay/collection action');
check(fn(board,'canAct').includes('!this.effectGallery')&&fn(board,'canInspectPile').includes('!this.effectGallery'),'ordinary battle actions and piles disabled in gallery');
check(native.includes('exec function bgboard_effects()')&&native.includes('if(effectGallery)entryMode=0;'),'console entry cannot become an NPC match');
check(native.includes('if(backupPlayer && !effectGallery)')&&native.includes('else {PublishCollection();Publish(session.GetMessage());}'),'gallery bypasses collection publication and close-time writes');
check(native.includes('if(!configured || !effectGallery || !audio')&&native.includes('audio.SpellLaunch(id,kind-100)'),'preview audio isolated behind gallery gate');
check(fn(board,'galleryShowScene').includes('controller.focusTag("galleryRepeat")'),'controller returns to Repeat after every sample');
for(const dir of ['src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder'])check(fs.readFileSync('BetaGwent/ui/'+dir+'/BetaGwentEffectGallery168.as','utf8')===source,'gallery mirror '+dir);
const report={stage:168,checks,samples:entries.length,rawPresetsInDefault:0,sourcePresets:Object.keys(recipes.presets).length,actualActionScript:true,nativeGameTested:false};fs.writeFileSync('docs/evidence/gallery168.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
