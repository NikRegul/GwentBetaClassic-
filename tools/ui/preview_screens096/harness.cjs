'use strict';
// Runs the production AS screen functions with a recording display list.
const fs=require('fs'),vm=require('vm'),path=require('path');
const ROOT=process.env.ROOT,UI=ROOT+'/BetaGwent/ui/src';
const src=fs.readFileSync(UI+'/BetaGwentBoard.as','utf8').replace(/^\uFEFF/,'');
const TYPES='Object|String|Function|void|int|uint|Number|Boolean|Array|Sprite|Shape|TextField|TextFormat|Rectangle|Matrix|Point|ColorTransform|GlowFilter|MouseEvent|Event|Error|DisplayObject|BetaGwent\\w+|\\*';
function fe(t){let out='',i=0;for(;;){const k=t.indexOf('for each',i);if(k<0){out+=t.slice(i);return out;}out+=t.slice(i,k);let p=t.indexOf('(',k),d=1,j=p+1;while(d){if(t[j]=='(')d++;else if(t[j]==')')d--;j++;}const inner=t.slice(p+1,j-1);const m=inner.match(/^\s*(?:var\s+)?(\w+)(?:\s*:\s*\S+?)?\s+in\s+([\s\S]*)$/);out+='for(var '+m[1]+' of Object.values(('+m[2]+')||{}))';i=j;}}
function extract(name,source=src){const re=new RegExp('function '+name+'\\(');const m=re.exec(source);if(!m)throw new Error('no '+name);const start=m.index;const open=source.indexOf('{',start);let end=open+1,d=1;
 while(d){d+=(source[end]==='{')-(source[end]==='}');end++;}
 return fe(source.slice(start,end)).replace(/((?:\bvar\s+|\bconst\s+|[(,]\s*)\w+)\s*:\s*(?:[A-Z][A-Za-z0-9]*[a-z][A-Za-z0-9]*|int|uint|void|\*)(?=\s*(?:[,)=;{]|in\b))/g,'$1').replace(/\)\s*:\s*(?:[A-Z][A-Za-z0-9]*|int|uint|void|\*)\s*\{/g,'){').replace(/\s+as\s+(Sprite|TextField|Shape|Array|Object|BetaGwent\w+)\b/g,'');}
// ---- display mocks ----
let uid=0;
class G{constructor(o){this.o=o;this.ops=[];}clear(){this.ops=[];}beginFill(c,a=1){this.ops.push(['fill',c,a]);}beginGradientFill(t,c,a,r,m){this.ops.push(['gradient',c,a,r]);}lineStyle(w,c,a=1){this.ops.push(['line',w||0,c,a]);}
 drawRect(x,y,w,h){this.ops.push(['rect',x,y,w,h]);}drawRoundRect(x,y,w,h){this.ops.push(['rect',x,y,w,h]);}drawCircle(x,y,r){this.ops.push(['circle',x,y,r]);}drawEllipse(x,y,w,h){this.ops.push(['ellipse',x,y,w,h]);}
 endFill(){this.ops.push(['end']);}moveTo(x,y){this.ops.push(['move',x,y]);}lineTo(x,y){this.ops.push(['lineto',x,y]);}}
 // No closePath here on purpose: AS3 Graphics does not have it, so an invented call must fail in the gate instead of in mxmlc.
class Sprite{constructor(){this.id=uid++;this.children=[];this.x=0;this.y=0;this.alpha=1;this.scaleX=1;this.scaleY=1;this.visible=true;this.graphics=new G(this);this.filters=[];this.transform={};this.mouseEnabled=true;this.mouseChildren=true;this.name='';this.rotation=0;}
 addChild(c){if(c.parent){const i=c.parent.children.indexOf(c);if(i>=0)c.parent.children.splice(i,1);}c.parent=this;this.children.push(c);return c;}
 addChildAt(c,i){if(c.parent){const k=c.parent.children.indexOf(c);if(k>=0)c.parent.children.splice(k,1);}c.parent=this;this.children.splice(i,0,c);return c;}
 removeChild(c){const i=this.children.indexOf(c);if(i>=0)this.children.splice(i,1);return c;}removeChildAt(i){this.children.splice(i,1);}get numChildren(){return this.children.length;}getChildAt(i){return this.children[i];}
 getChildIndex(c){return this.children.indexOf(c);}addEventListener(){}removeEventListener(){}hitTestPoint(){return false;}localToGlobal(p){return p;}globalToLocal(p){return p;}get stage(){return true;}contains(){return false;}}
class Shape extends Sprite{}
class TF extends Sprite{constructor(){super();this.text='';this.width=100;this.height=20;this.size=22;this.color=0xF1E8D3;this.align='left';this.bold=false;this.isText=true;this.multiline=false;this.wordWrap=false;this.type='dynamic';
  this.defaultTextFormat={};this.embedFonts=false;this.scrollV=1;this.maxScrollV=1;this.maxChars=0;}
 get textWidth(){return Math.max(...String(this.text).split('\n').map(s=>[...s].reduce((a,ch)=>a+(/[\u3000-\u9fff\uac00-\ud7af]/.test(ch)?1:.5)*this.size,0)));}get textHeight(){return String(this.text).split('\n').reduce((n,s)=>n+(this.wordWrap?Math.max(1,Math.ceil([...s].reduce((a,ch)=>a+(/[\u3000-\u9fff\uac00-\ud7af]/.test(ch)?1:.5)*this.size,0)/Math.max(1,this.width))):1),0)*this.size*1.25;}
 setTextFormat(f){if(f.size)this.size=f.size;if(f.align)this.align=f.align;if(f.color!=null)this.color=f.color;this.defaultTextFormat={...this.defaultTextFormat,...f};}getTextFormat(){return {...this.defaultTextFormat,size:this.size,align:this.align};}}
const ops=[];
function mk(){return new Sprite();}
const ctx={Math,JSON,isNaN,parseInt,parseFloat,String,Number,Boolean,Array,Object,console,Infinity,NaN,undefined,Date,RegExp,
 int:v=>v|0,uint:v=>v>>>0,trace(){},getTimer:()=>100000,
 Sprite,Shape,TextField:TF,TextFormat:function(){return {};},Rectangle:function(x,y,w,h){return {x,y,width:w,height:h};},Matrix:function(){this.createGradientBox=()=>{};},
 Point:function(x,y){this.x=x;this.y=y;},ColorTransform:function(){},GlowFilter:function(){},DropShadowFilter:function(){},GradientType:{LINEAR:'l',RADIAL:'r'},
 MouseEvent:{CLICK:'c',ROLL_OVER:'o',ROLL_OUT:'u',MOUSE_DOWN:'d',MOUSE_UP:'p',MOUSE_WHEEL:'w'},Event:{CHANGE:'ch',ENTER_FRAME:'ef'},TextFieldType:{INPUT:'input'},
 BETA_CARD_ASPECT:17.64/21.46,BETA_LARGE_CARD_ASPECT:15.85574533/22.7377556,WIDE_PAD:960,EDITOR_FLIGHT_MS:320,PASS_HOLD_MS:650};
ctx.previewLayer=new Sprite();ctx.dragLayer=new Sprite();ctx.choiceLayer=new Sprite();ctx.content=new Sprite();ctx.controller={registerControl(){},active:false,getFocus(){return null;},focusKey(){},focusTag(){},swap:false,device:0};
// ---- AS static data ----
function asText(f){return fs.readFileSync(UI+'/'+f,'utf8').replace(/^\uFEFF/,'');}
function consts(text){const o={};for(const m of text.matchAll(/([A-Z][A-Z0-9_]*):int=(-?\d+)/g))o[m[1]]=+m[2];return o;}
const hud=consts(asText('BetaGwentHud104.as'));const deck=consts(asText('BetaGwentDeckArt104.as'));
const slotsTxt=asText('BetaGwentDeckArt104.as').match(/SLOTS:Object=(\{[^}]*\})/)[1];const SLOTS=JSON.parse(slotsTxt.replace(/(\d+):/g,'"$1":'));
ctx.BetaGwentHud104=Object.assign(hud,{titleBg:f=>-1740-Math.max(0,Math.min(5,f)),infoBg:f=>-1750-Math.max(0,Math.min(5,f)),titleLine:f=>-1760-Math.max(0,Math.min(5,f)),cardBack:f=>-1830-Math.max(0,Math.min(5,f)),avatar:()=>-1700});
ctx.BetaGwentDeckArt104=Object.assign(deck,{slot:id=>SLOTS[id]?+SLOTS[id]:0,ornament:f=>-3740-Math.max(0,Math.min(4,f)),stats:f=>-3745-Math.max(0,Math.min(4,f)),factionFilter:f=>-3750-Math.max(0,Math.min(5,f))});
const chrome=asText('BetaGwentEditorChrome096.as');const CR=JSON.parse(chrome.match(/RECTS:Array=(\[.*?\]);/)[1]);const CC=consts(chrome);
ctx.BetaGwentEditorChrome096=Object.assign(CC,{cell(id,w,h){const s=new Sprite();s.chrome=CR[id];s.cw=w;s.ch=h;return s;}});
const HD=JSON.parse(asText('BetaGwentHDArt.as').match(/private static var slots:Object=(.*);/)[1]);
ctx.BetaGwentHDArt={size:id=>HD[id]?[HD[id][3],HD[id][4]]:null,has:id=>!!HD[id],clip(id,w,h,sx,sy,sw,sh){if(!HD[id])return null;const s=new Sprite();s.art={id,w,h,sub:[sx,sy,sw,sh]};return s;},view(id,w,h){const s=new Sprite();s.art={id,w,h};return s;}};
const windowArt=asText('BetaGwentWindowArt098.as');const WR=JSON.parse(windowArt.match(/RECTS:Array=(\[.*?\]);/)[1]);
ctx.BetaGwentWindowArt098=Object.assign(consts(windowArt),{cell(id,w,h){const r=WR[id];return r?(id>=18?ctx.BetaGwentHDArt.clip(-1850,w,h,r[0],r[1]-1178,r[2],r[3]):ctx.BetaGwentHDArt.clip(-3730,w,h,r[0]-333,r[1],r[2],r[3])):null;}});
ctx.controller.focusPicker=()=>{};
// catalog
const cat=asText('BetaGwentFullCatalog.as');const all=[];for(const m of cat.matchAll(/^\s*(\{"templateId".*\}),?\s*$/gm)){try{all.push(JSON.parse(m[1]));}catch(e){}}
const byId={};for(const c of all)byId[c.templateId]=c;
ctx.BetaGwentFullCatalog={all:()=>all,find:id=>byId[id]};ctx.BetaGwentRelated091={find:id=>byId[id]};
ctx.BetaGwentCardTags={text:id=>byId[id]?byId[id].tags||'':''};ctx.BetaGwentCardText={find:()=>null};
ctx.BetaGwentTextLanguage={fitButton(){},translate:s=>s,search:(a,q)=>String(a).toLowerCase().indexOf(q)>=0,forget(){},assign(f,v){f.text=v;},track(){},keywords(){},language:1,loaded:()=>true,protect(){}};
ctx.BetaGwentFonts={TITLE:'title',BODY:'body',NUMBERS:'numbers',apply(f,face,size,color,bold,align){f.size=size;f.color=color;f.bold=!!bold;if(align)f.align=align;f.face=face;return true;}};
ctx.BetaGwentTextMetrics={width:(v,f,s)=>[...String(v)].length*s*.5,numberOffset:()=>[0,0]};
ctx.BetaGwentBanners090={paint:()=>false,slot:()=>[.1,.1,.16],lastError:''};ctx.BetaGwentCovers107={cover:()=>0};
ctx.BetaGwentUi138={flashes:true,intensity:1,filters:{},deckReasons:()=>[],missingCost:()=>0,chains:false,helpLabels:false};
ctx.BetaGwentBetaMotion={duration:()=>200};ctx.BetaGwentVirtualShelf178=class extends Sprite{constructor(count,columns,rowHeight,w,h,offset){super();const lay={count,columns,rowHeight,height:h,offset:0,max:Math.max(0,Math.ceil(count/columns)*rowHeight-h),total:Math.ceil(count/columns)*rowHeight};
 lay.first=0;lay.end=Math.min(count,(Math.ceil(h/rowHeight)+1)*columns);this.layout=lay;this.body=new Sprite();this.addChild(this.body);this.clip=[0,0,w,h];}
 static position(mask,typeMask,position){if(position==0)return true;if(position==5)return typeMask==2;if(typeMask!=4)return false;if(position==4)return mask!=0&&(mask&(mask-1))!=0;return position>0&&position<4&&mask==[0,1,2,4][position];}
 static card(s,pane,i,x,y,w,h){const v=Object.assign({},s);v.viewKey=pane+s.templateId;v.shelfPane=pane;v.shelfIndex=i;return v;}};
// mocked primitives
Object.assign(ctx,{
 paintArt(p,id,w,h,x=3,y=3){const s=new Sprite();s.x=x;s.y=y;s.art={id,w,h};p.addChild(s);return !!HD[id];},
 betaNine(p,id,w,h,x=0,y=0){const s=new Sprite();s.x=x;s.y=y;s.art={id,w,h,nine:true};p.addChild(s);return s;},
 wideArt(p,id,w=1920,x=0){const s=new Sprite();s.x=x;s.art={id,w,h:1080};p.addChild(s);},
 text(p,v,x,y,w,size=22,color=0xF1E8D3){const f=new TF();f.text=String(v==null?'':v);f.x=x;f.y=y;f.width=w;f.size=size;f.height=80;f.multiline=true;f.wordWrap=true;f.color=color;f.face='body';p.addChild(f);return f;},
 betaFace(face,f,size,color,bold,align){f.size=size;f.color=color;f.bold=!!bold;if(align)f.align=align;f.face=face;},
 betaPowerField(p,v,w,h,color){const b=ctx.betaBannerRect(w,h);const size=Math.max(14,Math.round(h*.2));const f=ctx.text(p,v,b[0]-4,b[1]+b[3]*.06,b[2]+8,size,color);f.align='center';f.face='numbers';f.bold=true;return f;},
 betaBigPowerField(p,v,w,h,color){return ctx.betaPowerField(p,v,w,h,color);},
 panel(p,x,y,w,h,color,alpha=.82){const s=new Sprite();s.x=x;s.y=y;s.graphics.beginFill(color,alpha);s.graphics.drawRect(0,0,w,h);p.addChild(s);return s;},
 paintStaticCardState(){},attachInspect(){},attachEditorClick(){},attachEditorDrag178(){},attachLeaderMovie(){},buttonMotion(){},uiSound(){},send(){},render(){},
 centerBetaNumber(f,cx,cy,size){f.x=cx-f.width/2;f.y=cy-size*.6;f.align='center';},readableText:s=>s,clearLeaderPreview(){},uiTween(){},reportUIError(){},
 textChoiceLabel:()=>'Текст: Русский',voiceChoiceLabel:()=>'Озвучка: Русский',difficultyName:()=>'высокая',hasNativeClipboard090:()=>true,isKegMenu:()=>false,
 opponentName:()=>'Соперник',npcMatchHint:()=>'',offerTutorial(){},openTutorial(){},cycleTextLanguage(){},cycleVoiceLanguage(){},cycleDifficulty(){},openNameInput(){},
 requestEditorExit(){},requestBoardClose(){},closeControllerMenu(){},openTextInput(){},openDeckExchange(){},
 leadersForFaction:()=>[],markCollectionSeen(){},
});
const NAMES=['drawBetaDeckEditor','drawTitleBanner096','betaPlaque','editorSmallButton','editorBetaButton','betaWideButton','paintChevron','drawResources096','resourceItem096','betaStatsWidget','betaSlotLabel','betaLabel',
 'deckSlotRow','tierFrame','redrawDeckList178','shelfBar178','filterToggle096','filterSquares096','filterSquare096','chromeIcon096','typeIcon096','textIcon096','searchIcon096','filterSummary096',
 'editorInput','redrawEditorCollection','redrawBetaCollection','cardCraftButton','craftCost','cardRarity','drawDisabledReason','disabledReason','showEditorCard','drawBetaSidePreview','betaSidePreviewPlacement',
 'craftPanel096','editorFactionIndex','sortEditorCards','sortEditorCollection','editorPositionMatches','editorExtraFilter','editorFilterAction','editorAction','rememberEditorFilters','paintBetaFace','betaBannerRect','cardFaction','leaderOption','powerColor','sideFaction',
 'drawBetaCatalog','catalogCycle096','crownIcon096','redrawBetaCatalogGrid','redrawBetaCatalogDetail','catalogCards','catalogFilter','catalogPick','closeCatalog',
 'drawBetaMatchSetup','drawBetaDeckList','drawBetaDeckPicker','deckOption','openEditorAction','pickDeck','showBattleCard','deckDeleteIcon','drawDeckExchangeButtons','editorOwnedToggle','editorDrawExtra'];
let code='';for(const n of NAMES){try{code+=extract(n).replace(/^function /,'function ')+'\n';}catch(e){if(!/editorDrawExtra/.test(n))console.error('skip',n,e.message);}}
// betaLabel/betaSlotLabel wrappers rely on text(); keep real ones but BetaGwentTextMetrics mocked
// Beta geometry comes from the production source, so no preview can drift from it.
for(const m of src.matchAll(/\b(CHOICE_[A-Z0-9_]+):(?:Number|int)=(-?[\d.]+)/g))if(!(m[1] in ctx))ctx[m[1]]=+m[2];
vm.createContext(ctx);vm.runInContext(code,ctx);
module.exports={ctx,all,byId,extract,dump(root){const out=[],masks=new Set();function collect(s){if(s.mask)masks.add(s.mask);for(const c of s.children)collect(c);}collect(root);function walk(s,ox,oy,sx,sy,a,clip){if(!s.visible||masks.has(s))return;let x=ox+s.x*sx,y=oy+s.y*sy;const nsx=sx*s.scaleX,nsy=sy*s.scaleY,na=a*s.alpha;
  if(s.mask){const rect=s.mask.graphics.ops.find(o=>o[0]==='rect');if(rect)clip=[ox+(s.mask.x+rect[1])*sx,oy+(s.mask.y+rect[2])*sy,rect[3]*sx,rect[4]*sy];}
  if(s.clip)clip=[x,y,s.clip[2]*nsx,s.clip[3]*nsy];
  if(s.scrollRect){const r=s.scrollRect,next=[x,y,r.width*nsx,r.height*nsy];if(clip){const l=Math.max(clip[0],next[0]),t=Math.max(clip[1],next[1]),rr=Math.min(clip[0]+clip[2],next[0]+next[2]),bb=Math.min(clip[1]+clip[3],next[1]+next[3]);clip=[l,t,Math.max(0,rr-l),Math.max(0,bb-t)];}else clip=next;x-=r.x*nsx;y-=r.y*nsy;}
  if(s.graphics.ops.length)out.push({g:['reset']});for(const g of s.graphics.ops)out.push({g,x,y,sx:nsx,sy:nsy,a:na,clip});
  if(s.art)out.push({art:s.art,x,y,sx:nsx,sy:nsy,a:na,clip});if(s.chrome)out.push({chrome:s.chrome,w:s.cw,h:s.ch,x,y,a:na,clip});
  if(s.isText&&s.text)out.push({text:s.text,x,y,w:s.width*nsx,h:s.height*nsy,size:s.size*nsx,wrap:s.wordWrap,color:s.color,align:s.align,bold:s.bold,face:s.face,a:na,clip});
  for(const c of s.children)walk(c,x,y,nsx,nsy,na,clip);}
 walk(root,0,0,1,1,1,null);return out;}};
