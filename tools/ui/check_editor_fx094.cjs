// 0.9.4a deck-editor Beta effects: execute the production AS bodies
// (settleEditorUndo, drawEditorFeedback, editorFxPlan094, geometry) and check
// the generated frame data against the reviewed atlas specification.
'use strict';
const fs=require('fs'),vm=require('vm'),crypto=require('crypto'),path=require('path'),assert=require('node:assert/strict');
const board=process.argv[2]||'BetaGwent/ui/src/BetaGwentBoard.as';
const ui=path.dirname(board);
const spec=JSON.parse(fs.readFileSync(process.argv[3]||'data/beta924/design/editor_vfx094.json','utf8'));
const source=fs.readFileSync(board,'utf8'),fxSource=fs.readFileSync(path.join(ui,'BetaGwentEditorFx094.as'),'utf8');
const dataSource=fs.readFileSync(path.join(ui,'BetaGwentEditorFxData094.as'),'utf8'),artSource=fs.readFileSync(path.join(ui,'BetaGwentElementArt164.as'),'utf8');
let checks=0;const failures=[];function check(ok,label){checks++;if(!ok)failures.push(label);}
const TYPES='Object|String|Function|void|int|uint|Number|Boolean|Array|Sprite|TextField|BetaGwentEditorValid095|BetaGwentEditorFx094|\\*';
function extract(text,name){const start=text.search(new RegExp('function '+name+'\\('));assert(start>=0,name);const open=text.indexOf('{',start);let end=open+1,depth=1;
 while(depth){depth+=(text[end]==='{')-(text[end]==='}');end++;}
 return text.slice(start,end).replace(new RegExp(':\\s*(?:'+TYPES+')(?=\\s*(?:[,)=;{]|in\\b))','g'),'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))');}
// ---------- generated data ----------
const constant=(name)=>{const m=dataSource.match(new RegExp('const '+name+':\\w+=([^;]+);'));assert(m,name);return JSON.parse(m[1]);};
const RECTS=constant('RECTS'),ADD=constant('ADD'),REMOVE=constant('REMOVE');
check(JSON.stringify(RECTS)===JSON.stringify(spec.rects.slice(0,28))&&spec.rects.length===(spec.validVfx094a?29:28)+(spec.chrome096?spec.chrome096.names.length:0)+(spec.slotFx096?spec.slotFx096.cells.length:0)&&(!spec.chrome096||spec.chrome096.first===29),'card AS rects equal their reviewed atlas cells; optional cell29 belongs to ValidVFX, later cells to the 0.9.6 chrome');
check(JSON.stringify(ADD)===JSON.stringify(spec.frames.UIDBCardAdd)&&JSON.stringify(REMOVE)===JSON.stringify(spec.frames.UIDBCardRemove),'AS frames equal the specification');
check(constant('TEXELS')===spec.texelsPerUnit&&constant('FRAMES')===spec.fps&&constant('MS')===1000,'resolution, 30 Hz and 1 s pooled lifetime');
check(constant('CARD_X')===17.64&&constant('CARD_Y')===21.46&&/BETA_CARD_ASPECT:Number=17\.64\/21\.46;/.test(source),'card units match the board card aspect');
const [aw,ah]=spec.size,[bw,bh]=spec.baseSize;
check(aw===bw&&ah>bh&&(ah-bh)%16===0&&ah-bh<=320,'atlas grows only by whole BC3 stripes within the reviewed budget');
RECTS.forEach((r,i)=>{check(r.every(v=>v%4===0)&&r[0]>=0&&r[1]>=bh&&r[0]+r[2]<=aw&&r[1]+r[3]<=ah,'rect '+i+' aligned and below the original cells');
 RECTS.forEach((o,j)=>{if(j>i)check(r[0]+r[2]<=o[0]||o[0]+o[2]<=r[0]||r[1]+r[3]<=o[1]||o[1]+o[3]<=r[1],'rects '+i+'/'+j+' do not overlap');});});
const used=new Set();
for(const [name,frames] of [['add',ADD],['remove',REMOVE]]){
 check(frames.length===30,name+' has 30 frames');check(frames[0][0]===-1&&frames[0][1]===-1,name+' frame 0 is empty as in the bake');
 for(let i=1;i<=9;i++)check(Array.isArray(frames[i][1]),name+' light layer visible on frame '+i);
 for(let i=11;i<30;i++)check(frames[i][0]===-1&&frames[i][1]===-1,name+' finished after its clip ('+i+')');
 for(const pair of frames)for(const layer of pair)if(layer!==-1){
  check(Array.isArray(layer)&&layer.length===3&&RECTS[layer[0]],name+' layer references a rect');used.add(layer[0]);
  const r=RECTS[layer[0]],left=layer[1],top=layer[2],w=r[2]/spec.texelsPerUnit,h=r[3]/spec.texelsPerUnit;
  check(left>=-40&&top>=-50&&left+w<=40&&top+h<=50,name+' layer stays inside the source 80x100 extent');}
 // The card-sized source flash (17.07 x 22.14 units) is covered on its peak frame.
 const peak=frames[5][1],r=RECTS[peak[0]],w=r[2]/spec.texelsPerUnit,h=r[3]/spec.texelsPerUnit;
 check(peak[1]<=-8.5&&peak[1]+w>=8.5&&peak[2]<=-11&&peak[2]+h>=11,name+' peak frame covers the card flash');
}
check(ADD.slice(1,10).every(p=>Array.isArray(p[0]))&&REMOVE.every(p=>p[0]===-1),'only UIDBCardAdd has the ordinary UI/UIGlow frame layer');
check(used.size===RECTS.length,'every packed rect is used');
check((ADD[5][1][1]+RECTS[ADD[5][1][0]][2]/8)<(REMOVE[5][1][1]+RECTS[REMOVE[5][1][0]][2]/8),'add flash start sits left (toward the deck list), remove right');
// ---------- effect class ----------
check(/light\.blendMode="add";addChild\(normal\);addChild\(light\);/.test(fxSource),'ordinary layer under additive light layer');
check(/unit=cardWidth\/BetaGwentEditorFxData094\.CARD_X;/.test(fxSource),'uniform Beta unit scale from card width');
const fxc=vm.createContext({Math,int:v=>v|0,BetaGwentEditorFxData094:{FRAMES:30}});vm.runInContext(extract(fxSource,'frameIndex'),fxc);
check(fxc.frameIndex(0)===0&&fxc.frameIndex(.034)===1&&fxc.frameIndex(.999)===29&&fxc.frameIndex(1)===-1&&fxc.frameIndex(-1)===-1&&fxc.frameIndex(NaN)===-1,'frame index: 30 Hz, hidden before delay and after the end');
check(/public static function region\(index:int,rect:Array,w:Number,h:Number\):Sprite \{/.test(artSource),'region() matches the Classic native-cell insertion marker');
check(/atlas\.height<rect\[1\]\+rect\[3\]\)return null;/.test(artSource),'menus without the extended atlas draw nothing');
// ---------- production editor logic ----------
const names=['editorCounts','settleEditorUndo','editorFeedbackPoint178','editorCollectionCard094','editorFxPlan094','drawEditorFeedback'];
const flightMs=Number((source.match(/EDITOR_FLIGHT_MS:Number=(\d+);/)||[])[1]);check(flightMs===320,'flight/arrival constant');
const geometry=['viewport.x=480;viewport.y=304;','tile.x=18+(i%6)*156;tile.y=int(i/6)*186-editorScroll178;','var cw:Number=128,ch:Number=Math.round(128/BETA_CARD_ASPECT);','new BetaGwentVirtualShelf178(filtered.length,6,186,964,622,editorScroll178)'];
for(const g of geometry)check(source.includes(g),'collection tile geometry unchanged: '+g);
class Sprite{constructor(){this.children=[];this.x=0;this.y=0;this.alpha=1;}addChild(c){this.children.push(c);return c;}}
function context(o={}){
 const cards=[{templateId:5,copies:1},{templateId:7,copies:0},{templateId:9,copies:2}];
 const c=vm.createContext(Object.assign({Math,int:v=>v|0,Sprite,BETA_CARD_ASPECT:17.64/21.46,EDITOR_FLIGHT_MS:flightMs,skin:3,reducedMotion:false,
  ready:true,editorUndo:[],editorUndoPending:false,editorFlight:null,editorPending:null,editorCards:cards,
  editorById:Object.fromEntries(cards.map(x=>[x.templateId,x])),editorState:{slot:3,faction:8},deckListTop178:428,
  shelves178:{collection:{columns:6,rowHeight:186,height:622,offset:0},deck:{columns:1,rowHeight:40,height:480,offset:0}},
  shelfCards178:{collection:[{templateId:1},{templateId:2},{templateId:3},{templateId:4},{templateId:5},{templateId:6},{templateId:7}],deck:[{templateId:5},{templateId:9}]},
  content:new Sprite(),animations:[],fxAvailable:true,created:[],
  BetaGwentEditorFxData094:{MS:1000},
  editorSummary:()=>'',text:()=>({}),betaFace(){},editorBetaButton(){},playDeckSlotFx096(){},uiSound(){},paintArt(){},undoEditorChange(){},BetaGwentFonts:{}},o));
 c.BetaGwentEditorFx094=function(adding,w){this.adding=adding;this.w=w;this.available=c.fxAvailable;c.created.push(this);};
 vm.runInContext(names.map(n=>extract(source,n)).join('\n'),c);return c;}
const fxOf=c=>c.animations.filter(a=>a.editorFx094);
function confirm(c,id,amount,mutate){c.editorPending={id,amount,before:c.editorCounts(),slot:3,faction:8,origin:{x:600,y:400}};
 if(mutate!==false)c.editorById[id].copies+=amount;c.settleEditorUndo();c.drawEditorFeedback();}
// expected centre of collection card i (row 0/1) from the production tile geometry
const centre=(i,offset=0)=>({x:480+18+(i%6)*156+64,y:304+Math.floor(i/6)*186-offset+Math.round(128/(17.64/21.46))/2});
{const c=context();confirm(c,5,1);const fx=fxOf(c);
 check(fx.length===1&&c.created[0].adding===true,'confirmed add plays UIDBCardAdd once');
 const e=centre(4);check(fx[0].fromX===e.x&&fx[0].fromY===e.y&&fx[0].toX===e.x&&fx[0].toY===e.y,'add effect centred on the collection card face');
 check(fx[0].delay===0&&fx[0].duration===1000&&fx[0].remove&&fx[0].hideBeforeDelay,'add starts at once, 1 s, removed afterwards');
 check(c.created[0].w===128,'effect scaled from the 128 px card face');
 check(c.content.children.indexOf(fx[0].sprite)<c.content.children.indexOf(c.animations.find(a=>a.betaFlight).sprite),'effect drawn under the flying card');
 check(c.editorFlight===null,'flight consumed once');c.drawEditorFeedback();check(fxOf(c).length===1,'redraw does not replay the effect');}
{const c=context();confirm(c,9,-1);const fx=fxOf(c);
 check(fx.length===0,'card not shown in collection: no effect');check(c.animations.some(a=>a.betaFlight),'flight still plays without the effect');}
{const c=context();c.shelfCards178.collection.push({templateId:9});confirm(c,9,-1);const fx=fxOf(c);
 check(fx.length===1&&c.created[0].adding===false,'confirmed removal plays UIDBCardRemove');
 check(fx[0].delay===flightMs&&fx[0].sprite.alpha===0,'removal effect waits for the returning card and is hidden meanwhile');
 const e=centre(7);check(fx[0].fromX===e.x&&fx[0].fromY===e.y,'removal effect on the receiving collection card');
 const flight=c.animations.find(a=>a.betaFlight);check(flight.duration===flightMs&&Math.abs(flight.toX+38-e.x)<1e-9&&Math.abs(flight.toY+53-e.y)<1e-9,'flight lands on the same card centre');}
{const c=context();confirm(c,5,1,false);check(!fxOf(c).length&&!c.animations.length,'rejected/unchanged reply: no effect');}
{const c=context();c.editorPending={bulk:true,before:c.editorCounts(),slot:3,faction:8,restore:null};for(const x of c.editorCards)x.copies=0;c.settleEditorUndo();c.drawEditorFeedback();check(!fxOf(c).length,'clear/restore: no per-card effect');}
{const c=context({reducedMotion:true});confirm(c,5,1);check(!fxOf(c).length&&!c.created.length,'reduced motion: no effect');}
{const c=context();c.editorPending={id:5,amount:1,before:c.editorCounts(),slot:4,faction:8};c.editorById[5].copies++;c.settleEditorUndo();c.drawEditorFeedback();check(!fxOf(c).length,'another deck snapshot: no effect');}
{const c=context({fxAvailable:false});confirm(c,5,1);check(!fxOf(c).length&&!c.content.children.some(x=>x instanceof c.BetaGwentEditorFx094),'menu without editor frames: nothing added');}
{const c=context();c.shelves178.collection.offset=300;confirm(c,5,1);check(!fxOf(c).length,'card scrolled out of the shelf: no effect');}
{const c=context();c.shelves178.collection.offset=200;c.shelfCards178.collection.push({templateId:9});confirm(c,9,-1);const e=centre(7,200);
 check(fxOf(c).length===1&&fxOf(c)[0].fromY===e.y,'scrolled shelf: effect follows the visible card');}
{const c=context();confirm(c,5,1);c.editorUndo.length===1;const undo=c.editorUndo[0];check(undo&&undo.id===5&&undo.amount===1,'change recorded for undo');
 c.editorUndoPending=true;c.animations.length=0;c.created.length=0;c.editorPending={id:5,amount:-1,before:c.editorCounts(),slot:3,faction:8};c.editorById[5].copies--;c.settleEditorUndo();c.drawEditorFeedback();
 check(fxOf(c).length===1&&c.created[0].adding===false&&c.editorUndo.length===0,'undo of an add plays the removal effect');}
{const c=context({skin:2});confirm(c,5,1);check(!fxOf(c).length,'only the Beta editor layout has the effect');}
{const c=context();const p=c.editorFeedbackPoint178(5,'collection'),e=centre(4);check(p.x===e.x&&p.y===e.y,'controller flight origin uses the real tile centre');}
const report={checks,failures,boardSha256:crypto.createHash('sha256').update(fs.readFileSync(board)).digest('hex'),
 specSha256:crypto.createHash('sha256').update(JSON.stringify(spec)).digest('hex'),rects:RECTS.length,extraRows:ah-bh,actualActionScript:true,nativeGameTested:false};
if(process.argv[4])fs.writeFileSync(process.argv[4],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;
