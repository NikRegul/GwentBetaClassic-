'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),crypto=require('crypto');
const dir=process.argv[2]||'BetaGwent/ui/src',s=fs.readFileSync(dir+'/BetaGwentEditorValid095.as','utf8'),d=fs.readFileSync(dir+'/BetaGwentEditorValidData095.as','utf8');
const constant=n=>JSON.parse(d.match(new RegExp('const '+n+':\\w+=([^;]+);'))[1]);
const frames=constant('FRAMES'),rect=constant('RECT'),ms=constant('MS');let checks=0;
function eq(v,w,n){assert.deepEqual(v,w,n);checks++;}
eq(frames.length,48,'48 source timeline samples');eq(frames.reduce((n,f)=>n+f.length,0),158,'158 source particles');eq(Math.round(ms),300,'source lifetime');
const spec=JSON.parse(fs.readFileSync('data/beta924/design/editor_vfx094.json','utf8'));eq(rect,spec.rects[spec.validVfx094a.index],'exact native texture cell');
eq(spec.validVfx094a.outputAlpha,1,'source output alpha1');eq(/cell\.blendMode="add"/.test(s),true,'per-particle source One/One blend');
eq(/cell\.alpha\s*=/.test(s),false,'vertex alpha must not be applied a second time');
const start=s.indexOf('function render('),open=s.indexOf('{',start);let end=open+1,depth=1;while(depth){depth+=(s[end]==='{')-(s[end]==='}');end++;}
const body=s.slice(start,end).replace(/:\s*(?:int|Number|void|Sprite|Array)(?=\s*[,);={]|\s+in\b)/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');
const c=vm.createContext({Math,Number,int:v=>Math.trunc(v),Sprite:function(){},ColorTransform:function(...args){this.args=args;},BetaGwentEditorValidData095:{FRAMES:frames},unit:372/400,shown:-2,available:true,cells:Array.from({length:4},()=>({transform:{}}))});
vm.runInContext(body,c);
for(let i=0;i<47;i++){
 c.render((i+.25)/47);
 eq(c.cells.filter(x=>x.visible).length,frames[i].length,'visible source count frame'+i);
 frames[i].forEach((p,k)=>{
  const a=c.cells[k];eq(a.x,p[0]*.93,'source x');eq(a.y,(p[1]-15)*.93,'source root offset');
  eq(a.scaleX,p[2]*.93/128,'source width');eq(a.scaleY,-p[3]*.93/128,'source UV orientation');eq(a.rotation,p[4],'source rotation');
  eq(Array.from(a.transform.colorTransform.args),[p[5]*(2*p[8]),p[6]*(2*p[8]),p[7]*(2*p[8]),1],'source RGB brightness/vertex alpha');
 });
}
for(const p of [-1,1,2]){c.render(p);eq(c.cells.some(x=>x.visible),false,'outside lifetime hides all cells');}
const art=fs.readFileSync(dir+'/BetaGwentElementArt164.as','utf8'),classic=art.includes('BetaGwentClassicEffects.view("editor:"');
if(classic){
 const start=art.indexOf('function region('),open=art.indexOf('{',start);let end=open+1,depth=1;
 while(depth){depth+=(art[end]==='{')-(art[end]==='}');end++;}
 const body=art.slice(start,end).replace(/:\s*(?:Sprite|int|Array|Number|Bitmap|BitmapData|Error)\b/g,'').replace(/\s+as\s+(?:Bitmap|BitmapData)\b/g,'');
 function Sprite(){this.x=this.y=0;this.children=[];this.addChild=x=>this.children.push(x);}
 const ctx=vm.createContext({Sprite,BetaGwentClassicEffects:{view:()=>new Sprite()}});vm.runInContext(body,ctx);
 for(const [w,h]of [[128,128],[234,335]]){
  const cell=ctx.region(28,rect,w,h);eq(cell.children.length,1,'native cell keeps its bitmap inside a centred wrapper');
  eq([cell.children[0].x,cell.children[0].y],[-w/2,-h/2],'native image offset is inside wrapper');
  cell.x=500;cell.y=200;eq(cell.x+cell.children[0].x,500-w/2,'moving wrapper preserves horizontal centre');
  eq(cell.y+cell.children[0].y,200-h/2,'moving wrapper preserves vertical centre');
 }
}
const report={checks,failures:[],nativeCellCenteringChecked:classic,sourceShader:'AdditiveAlpha, One/One, textureRGB*textureAlpha^2*vertexRGB*2*vertexAlpha',actualActionScript:true,nativeAppearanceVerified:false,sha256:crypto.createHash('sha256').update(s+d).digest('hex')};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
