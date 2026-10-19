'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),build=process.env.BG_UI||'release090-ui-review2';let checks=0;
function check(v,m){assert(v,m);checks++;}
function fn(s,n){const a=s.indexOf('function '+n+'('),b=s.indexOf('{',a);assert(a>=0,n);let i=b+1,d=1;for(;d;i++){if(s[i]==='{')d++;if(s[i]==='}')d--;}
 return s.slice(a,i).replace(/:(?:String|Object|void|int|uint|Number|Array|Boolean|Sprite|Event|TextField|MouseEvent|Function|Rectangle)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/\s+as Array\b/g,'').replace(/for each\(var (\w+) in ([^)]+)\)/g,'for(var $1 of Object.values($2))');}
const metrics=fs.readFileSync(path.join(root,'BetaGwent/ui/src/BetaGwentTextMetrics.as'),'utf8');
const glyphs=JSON.parse(metrics.match(/glyphs:Object=(.*);/)[1]);
const proofs=[];
for(const platform of ['classic','nextgen']){
 const dir=path.join(root,'BetaGwent/build',build,platform,'ui/src');
 const source=fs.readFileSync(path.join(dir,'BetaGwentBoard.as'),'utf8');
 const catalog=fs.readFileSync(path.join(dir,'BetaGwentFullCatalog.as'),'utf8').split(/\r?\n/).filter(x=>x.trim().startsWith('{"templateId"')).map(x=>JSON.parse(x.trim().replace(/,$/,'')));
 const byId=new Map(catalog.map(x=>[x.templateId,x]));
 let nodes=[],clock=0;
 class Sprite{constructor(){this.children=[];this.x=this.y=0;this.scaleX=this.scaleY=this.alpha=1;this.stage=true;this.transform={};this.events={};this.graphics=new Proxy({},{get:()=>()=>{}});nodes.push(this);}
  get numChildren(){return this.children.length;}addChild(n){if(n.parent)n.parent.removeChild(n);this.children.push(n);n.parent=this;return n;}
  addChildAt(n,i){this.addChild(n);this.children.splice(this.children.indexOf(n),1);this.children.splice(i,0,n);return n;}
  removeChild(n){this.children=this.children.filter(x=>x!==n);n.parent=null;}removeChildAt(i){this.removeChild(this.children[i]);}
  addEventListener(k,f){this.events[k]=f;}removeEventListener(k){delete this.events[k];}}
 const layer=new Sprite(),detail=new Sprite(),preview=new Sprite();
 function text(p,value,x,y,w,size,color){const f={kind:'text',text:String(value),x,y,width:w,height:size*1.6,size,color,scaleX:1,embedFonts:true,children:[],textHeight:size,
  defaultTextFormat:{font:'body',size},setTextFormat(){},getTextFormat(){return this.defaultTextFormat;},addEventListener(){}};p.addChild(f);return f;}
 function label(p,v,x,y,w,size,color,face,bold=false,align=null){const f=text(p,v,x,y,w,size,color);Object.assign(f,{face,bold,align});return f;}
 function panel(p,x,y,w,h,color,alpha){const s=p.addChild(new Sprite());Object.assign(s,{kind:'panel',x,y,width:w,height:h,color,alpha:alpha??1});return s;}
 const c=vm.createContext({Sprite,text,betaLabel:label,panel,betaFrame:(p,x,y,w,h)=>panel(p,x,y,w,h,0x4a3520,1),
  int:x=>x|0,String,Math,Rectangle:function(x,y,w,h){Object.assign(this,{x,y,w,h});},TextFormat:function(font,size){Object.assign(this,{font,size});},GlowFilter:function(){},
  BETA_CARD_ASPECT:17.64/21.46,DEMO_W:92,DEMO_H:92*21.46/17.64,WIDE_PAD:0,TUTORIAL:null,
  BetaGwentFonts:{NUMBERS:'Gwent Numbers',BODY:'PF Din Text Cond Pro',TITLE:'Halis GR'},
  BetaGwentHud104:{POPUP_TITLE:-1770},
  BetaGwentFullCatalog:{find:id=>byId.get(id),all:()=>catalog},BetaGwentTextLanguage:{assign:(f,t)=>f.text=t},
  BetaGwentTextMetrics:{},glyphs,
  tutorialLayer:layer,detailLayer:detail,previewLayer:preview,controller:{registerControl(){},focusTag(){}},
  tutorialFirstRun:false,detailBack:[],tutorialReturn:-1,numChildren:5,
  setChildIndex(){},clearDrag(){},clearPlacementGhost(){},betaFace(face,f,size,color,bold,align){Object.assign(f,{face,size,color,bold,align});},
  catalogByTitle:t=>catalog.find(x=>x.title===t),tutorialCardOpener:()=>()=>{},attachEditorClick(){},
  paintBetaFace(p,id,w,h){p.addChild({kind:'card',id,x:0,y:0,width:w,height:h,children:[]});},
  paintCardBack(){},paintSpyRibbon(){},betaPowerField(){},isSpyCard:id=>!!byId.get(id)?.spy,
  readableText:x=>x,getTimer:()=>clock,Event:{ENTER_FRAME:'frame',REMOVED_FROM_STAGE:'removed'},
  MouseEvent:{CLICK:'click'},
  editorBetaButton(p,title,x,y,w,h,enabled,callback){const s=panel(p,x,y,w,h,0x665035,1);Object.assign(s,{kind:'button',title,enabled,callback});return s;},
  closeCardDetail(){},roundBannerFor:null,roundBannerStart:0,ROUND_SCORE_MS:3000,reducedMotion:true,animations:[],
  ColorTransform:function(){},paintArt(p,id,w,h,x,y){p.addChild({kind:'art',id,x,y,width:w,height:h,children:[]});}});
 vm.runInContext('Array.prototype.sortOn=function(k){return this.sort((a,b)=>a[k]-b[k]);};\n'+fn(metrics,'numberOffset')+'\n'+
  ['centerBetaNumber','betaRoundCrownId','drawBetaRoundBanner','tutorialPages','openTutorial','tutorialDemo'].map(n=>fn(source,n)).join('\n'),c);
 c.BetaGwentTextMetrics.numberOffset=c.numberOffset;
 for(let own=0;own<=2;own++)for(let enemy=0;enemy<=2;enemy++){
  const parent=new Sprite();c.lastRoundResult={round:1,scores:[6,0],crowns:[own,enemy],flags:0};c.drawBetaRoundBanner(parent,false);
  const arts=nodes.flatMap(x=>x.children).filter(x=>x.kind==='art');
  check(arts.at(-2).id===[-1523,-1524,-1525][own]&&arts.at(-1).id===[-1523,-1526,-1527][enemy],'0/1/2 crowns map independently');
  const nums=nodes.flatMap(x=>x.children).filter(x=>x.kind==='text'&&x.face==='Gwent Numbers').slice(-2);
  for(const n of nums){const off=c.numberOffset(n.text,30);check(Math.abs(n.y+off[1]-103)<1e-7,'round score visible ink centered');}
  if(platform==='classic'&&((own===1&&enemy<=1)||(own===2&&enemy===1)))proofs.push({screen:'round-'+own+'-'+enemy,width:1920,height:1080,nodes:flatten(parent)});
 }
 for(let page=0;page<7;page++){
  nodes=[];clock=0;c.openTutorial(page);
  const box=layer.children.find(n=>n.kind==='panel'&&n.width===1440),demo=box.children.find(n=>n.kind==='panel'&&n.width===568);
  const body=box.children.find(n=>n.kind==='text'&&n.width===720&&n.y===140);
  check(body.x+body.width+40===demo.x&&body.y===demo.y,'tutorial columns align with 40 px gutter');
  const thumbs=box.children.filter(n=>n.children?.some(x=>x.kind==='card'));
  const first=thumbs[0],last=thumbs.at(-1);check(Math.abs((first.x+last.x+104)/2-(56+360))<1e-7,'card strip centered in reading column');
  for(const t of thumbs)check(t.children[0].height<127&&t.y+t.children[0].height+48<768,'card proportions and captions fit above footer');
  const tryButton=box.children.find(n=>n.title==='Попробовать');check(tryButton.x+tryButton.width/2===demo.x+demo.width/2,'Try button centered in demo');
  const stageView=box.children.find(n=>n.events?.frame);check(stageView,'demo frame attached');
  if(platform==='classic')proofs.push({screen:'tutorial-'+page,width:1920,height:1080,nodes:flatten(layer)});
  tryButton.callback();for(clock=0;clock<=6500;clock+=100)stageView.events.frame(null);
  const lastSay=c.tutorialPages()[page].demo.steps.filter(s=>s.op==='say'&&s.at<=6500).at(-1);
  check(stageView.children.some(n=>n.kind==='text'&&n.width===528&&n.text===lastSay.text),'all tutorial steps reach final caption '+page);
 }
 check(source.includes('shade.graphics.beginFill(0x0C0B09,1)')&&!source.includes('var shade:Sprite=panel(detailLayer,-WIDE_PAD,0,1920+2*WIDE_PAD,1080,0x0C0B09'),'opaque detail backdrop has no inherited panel stroke');
 check(source.includes('cardReading(c,detail,true,true,false,false)'),'detail omits duplicate power diagnostics');
}
function flatten(node,x=0,y=0){if(node.visible===false)return [];let out=[];x+=node.x||0;y+=node.y||0;if(node.kind)out.push({kind:node.kind,x,y,w:node.width,h:node.height,value:node.text??node.title,id:node.id,size:node.size,color:node.color,face:node.face,align:node.align});for(const child of node.children||[])out.push(...flatten(child,x,y));return out;}
const report={checks,proofs,inGameVerified:false};
fs.writeFileSync(path.join(root,'BetaGwent/build',build,'ui-review-tests.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({checks,pages:7,inGameVerified:false}));
