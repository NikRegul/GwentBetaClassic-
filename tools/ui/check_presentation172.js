'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const board=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
function fn(name){const start=board.indexOf('function '+name+'(');assert(start>=0,name);let open=board.indexOf('{',start),i=open+1,d=1;while(d){if(board[i]==='{')d++;if(board[i]==='}')d--;i++;}return board.slice(start,i).replace(/:(?:String|Object|Sprite|TextField|Event|MouseEvent|Error|void|int|uint|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/\s+as TextField\b/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))');}
let checks=0;function check(v,n){assert(v,n);checks++;}
class Layer{constructor(){this.children=[];this.graphics={clear(){}};}get numChildren(){return this.children.length;}removeChildAt(i){this.children.splice(i,1);}addChild(child){this.children.push(child);return child;}}
const c=vm.createContext({Math,String,Number,Object,Array,Error,int:v=>v|0,Sprite:Layer,TextField:Layer});
// Exercise production startup, both scene renders and controls, including a
// failing effect. Battle-specific drawing must never be entered by the gallery.
for(const match of board.matchAll(/private var (\w+)\s*:/g))c[match[1]]=null;
Object.assign(c,{effectGallery:false,galleryPending:false,galleryEntries:[],galleryIndex:0,galleryAudioAt:0,
 skin:3,animationTempo:1,flags:0,detailOpen:false,controllerMenuOpen:false,frameDuration:0,
 animations:[],weatherEffects:[],weatherRows:[],weatherFades:[],weatherBirths:{},displayedCards:{},
 aimLayer:new Layer(),previewLayer:new Layer(),choiceLayer:new Layer(),content:new Layer(),
 galleryCalls:[],errors:[],buttons:[],failRows:false,now:1000,BetaGwentUi138:{intensity:1},
 BetaGwentFullCatalog:{find:()=>({description:'Card',tier:2,typeMask:4})},
 BetaGwentSpecialVfx:{prefabs:()=>null},BetaGwentElementData164:{preset:()=>({method:0,projectile:false})},
 controller:{active:true,focusTag(tag){c.focus=tag;},registerControl(){}},
 BetaGwentEffectGallery168:{entries:()=>[{title:'Example',kind:2}],scene:()=>({before:[{id:1,templateId:1}],after:[{id:1,templateId:1}],weatherBefore:[],weatherAfter:[],cue:{kind:2,templateId:1}})},
 restoreTurnHandFocus:()=>false,rememberEditorFilters:()=>{},beginLeaderRender:()=>{},finishLeaderRender:()=>{},
 clearPlacementGhost:()=>{},clearDrag:()=>{},closeControllerMenu:()=>{},
 getTimer:()=>c.now,send:(...args)=>c.galleryCalls.push(args),reportUIError:(...args)=>c.errors.push(args),
 drawFactionBoards:()=>{},drawRows:()=>{if(c.failRows)throw Error('bad effect');},drawCards:()=>{c.displayedCards={1:{x:10,y:10}};},
 animateWeather:()=>{},drawVisualCue:()=>{},drawElement164:()=>{},cueImpactDelay:()=>180,
 drawBetaBattleHud:()=>{throw Error('gallery drew battle HUD');},
 panel:()=>new Layer(),text:()=>({}),
 editorBetaButton:(parent,title,x,y,w,h,enabled,action)=>{c.buttons.push({title,enabled,action});return new Layer();},
 editorSmallButton:(parent,title,x,y,w,h,enabled,action)=>{c.buttons.push({title,enabled,action});return new Layer();},
 requestBoardClose:()=>{c.closed=true;}
});
vm.runInContext(['startEffectGallery','galleryShow','galleryShowScene','galleryRepeat','galleryStep','gallerySound','drawEffectGallery','drawGalleryControls','render'].map(fn).join('\n'),c);
c.startEffectGallery(true);
check(c.effectGallery&&c.galleryPending&&c.buttons.length===0,'startup defers rendering outside native OnConfigUI');
c.galleryShow(0);
check(c.ready&&!c.playing&&c.focus==='galleryRepeat','gallery is interactive and focuses Repeat');
check(c.errors.length===0,'complete gallery scene transition renders without error');
check(['Назад','Повторить','Далее','Закрыть'].every(title=>c.buttons.some(b=>b.title===title&&b.enabled)),'all four gallery controls are enabled');
check(c.galleryCalls.some(a=>a[0]==='OnBetaGwentControllerTrace'),'successful scene reports to the game log');
c.buttons=[];c.failRows=true;c.galleryShow(0);
check(c.errors.length===2&&c.buttons.length===8,'both render errors are logged and neither blocks controls');
c.buttons.find(b=>b.title==='Закрыть').action();check(c.closed,'Exit works even when the effect throws');
c.failRows=false;c.buttons=[];c.errors=[];c.galleryEntries=[];c.BetaGwentEffectGallery168.entries=()=>{throw Error('bad catalogue');};c.galleryShow(0);
check(c.errors.length===1&&c.ready&&c.buttons.find(b=>b.title==='Закрыть').enabled,'catalogue initialisation failure keeps an interactive Exit');
check(fn('render').indexOf('drawGalleryControls();finishLeaderRender();return;')<fn('render').indexOf('drawBetaBattleHud()'),'gallery exits before ordinary opponent-turn HUD');

vm.runInContext(`var activeCue={},reducedMotion=false,displayedCards={},cards=[];function igniRowDelay(){return 600;}function killEffectStyle(id){return ({112102:3,113309:1,112107:1,113308:2})[id]||0;}`+fn('rowDepartureDelay')+fn('cueMinimumDuration'),c);
for(const [id,wait] of [[112102,1850],[113309,1210],[112107,1210],[113308,1200],[123,440]]){
 c.activeCue={kind:3,templateId:id};c.displayedCards={1:{side:2,zone:1},2:{side:2,zone:1},3:{side:2,zone:2}};c.cards=[{id:1,side:2,zone:1},{id:3,side:2,zone:2}];
 check(c.rowDepartureDelay(2,1)===wait,'survivor waits for removal '+id);
 check(c.rowDepartureDelay(2,2)===0&&c.rowDepartureDelay(1,1)===0,'unaffected rows are not delayed '+id);
 check(c.cueMinimumDuration(3)>=wait+280,'replay allows departure and complete compaction '+id);
 c.reducedMotion=true;check(c.rowDepartureDelay(2,1)===0,'reduced motion does not wait for an absent animation '+id);c.reducedMotion=false;
}
c.activeCue={kind:8,templateId:112102};check(c.rowDepartureDelay(2,1)===0,'intentional relocation is not held like destruction');
check(fn('drawCards').includes('delay:!isHand&&!relocation?rowDepartureDelay(c.side,c.zone):0'),'same-row layout movement uses removal completion time');

Object.assign(c,{draws:[],boosts:[],BetaGwentSpecialVfx:{prefabs(id,hurting){return hurting?{element:1,method:1,attack:'PowerPhysicalProjectile',impact:'PowerDirectPhysical'}:{element:512,method:3,attack:'PowerSideLightMagic',impact:'PowerDirectLightMagic'};}},
 BetaGwentElementData164:{preset:name=>name?{method:0}:null},cueImpactTime:()=>380,
 drawBoostCue:(fx,hit,delay)=>c.boosts.push({id:hit.id,delay}),strikes:[],drawStrike173:(fx,hit,element,delay)=>c.strikes.push({id:hit.id,element,delay}),compactProjectile173:n=>/Magic|Fire/.test(n)&&/Projectile/.test(n),drawElement164:(fx,name)=>{c.draws.push(name);return true;},
 poseX:p=>p.x,poseY:p=>p.y,poseW:()=>80,poseH:()=>110});
vm.runInContext(fn('drawElementCue164'),c);
const hits=Array.from({length:4},(_,i)=>({id:i+1,side:1,zone:1,delta:1,armorDelta:0,x:600+i*90,y:600}));
c.activeCue={kind:2,templateId:123,source:100};c.drawElementCue164({},hits,900,900,{});
check(c.draws.length===4&&c.draws.every(n=>n==='PowerDirectLightMagic')&&c.boosts.length===0,'stage 174: boosts are the per-card Direct prefab, together, without side waves or projectiles');
c.draws=[];c.drawElementCue164({},[{...hits[0],delta:-3}],900,900,{});
check(c.draws.join(',')==='PowerPhysicalProjectile,PowerDirectPhysical'&&c.strikes.length===0,'stage 174: physical shot flies (Beta footage) and lands with its Direct impact');
const motions=[];Object.assign(c,{killSprite:()=>({}),killMotion:(...args)=>motions.push(args),BetaGwentKillArt144:{SOFT_GLOW:1,SOFT_DOT:2}});
vm.runInContext(fn('drawBoostCue'),c);c.drawBoostCue({},hits[0],380);
check(motions.length===4&&motions.every(m=>m[10].fromAlpha<=.28),'compact boost glow and sparks keep restrained opacity in the actual motion');
for(const dir of ['src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder'])check(fs.readFileSync('BetaGwent/ui/'+dir+'/BetaGwentBoard.as','utf8')===board,'board mirror '+dir);
const raw=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as');check(raw.subarray(0,3).toString('hex')==='efbbbf'&&!/(?<!\r)\n/.test(raw.toString('utf8')),'BOM and Windows line endings retained');
const report={stage:172,checks,actualActionScriptMethods:true,nativeGameTested:false,releaseBuilt:false};
fs.writeFileSync('docs/evidence/presentation172.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
