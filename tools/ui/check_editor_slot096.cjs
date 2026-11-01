'use strict';
// 0.9.6 Beta deck-row effects: run the production playDeckSlotFx096 body and
// check the generated data against the reviewed atlas cells.
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('node:assert/strict');
const board=process.argv[2]||'BetaGwent/ui/src/BetaGwentBoard.as',ui=path.dirname(board);
const spec=JSON.parse(fs.readFileSync(process.argv[3]||'data/beta924/design/editor_vfx094.json','utf8'));
const source=fs.readFileSync(board,'utf8'),data=fs.readFileSync(path.join(ui,'BetaGwentEditorSlotData096.as'),'utf8');
let checks=0;const failures=[];const check=(ok,label)=>{checks++;if(!ok)failures.push(label);};
function extract(name){const start=source.indexOf('function '+name+'(');assert(start>=0,name);const open=source.indexOf('{',start);let end=open+1,d=1;
 while(d){d+=(source[end]==='{')-(source[end]==='}');end++;}
 return source.slice(start,end).replace(/:\s*(?:Object|Array|int|Number|Boolean|void|BetaGwentEditorSlot096)(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))');}
const constant=n=>JSON.parse(data.match(new RegExp('const '+n+':\\w+=([^;]+);'))[1]);
const rects=constant('RECTS');
for(const [i,r] of Object.entries(rects))check(JSON.stringify(spec.rects[+i])===JSON.stringify(r),'cell '+i+' equals the reviewed atlas rect');
check(spec.slotFx096&&spec.slotFx096.sharedFlare00===28&&rects['28'],'Flare00 shared with ValidVFX');
for(const n of ['ADD','REMOVE','COUNTER']){const frames=constant(n);check(frames.length===48,n+' 48 samples');
 check(frames.every(f=>f.every(p=>p.length===10&&rects[String(p[0])]&&p.slice(1).every(Number.isFinite))),n+' particles reference known cells');}
const made=[];class Fx{constructor(kind,w,h){this.kind=kind;this.w=w;this.h=h;this.available=ctx.available;this.ms=300;made.push(this);}}
Fx.ADD=0;Fx.REMOVE=1;Fx.COUNTER=2;
const ctx=vm.createContext({Math,int:v=>v|0,BetaGwentEditorSlot096:Fx,available:true,reducedMotion:false,skin:3,EDITOR_FLIGHT_MS:320,
 deckScroll178:0,deckListTop178:338,content:{children:[],addChild(c){this.children.push(c);}},animations:[],editorCards:[],editorById:{},
 sortEditorCards:(a,b)=>a.templateId-b.templateId});
vm.runInContext(extract('playDeckSlotFx096'),ctx);
function run(cards,flight,o={}){Object.assign(ctx,{animations:[],deckScroll178:0,reducedMotion:false,skin:3,available:true},o);made.length=0;
 ctx.editorCards=cards;ctx.editorById=Object.fromEntries(cards.map(c=>[c.templateId,c]));ctx.playDeckSlotFx096(flight);return ctx.animations;}
let a=run([{templateId:1,copies:1,tier:2},{templateId:2,copies:1,tier:2}],{id:2,amount:1});
check(a.length===1&&made[0].kind===0&&a[0].delay===320&&a[0].fromY===338+40&&a[0].fromX===232&&made[0].w===372&&made[0].h===38,'new row: SlotAdd after the flight, on that row');
a=run([{templateId:1,copies:2,tier:2}],{id:1,amount:1});check(a.length===1&&made[0].kind===2,'more copies: Counter');
a=run([{templateId:1,copies:1,tier:2}],{id:1,amount:-1});check(a.length===1&&made[0].kind===2&&a[0].delay===0,'fewer copies: Counter at once');
a=run([{templateId:1,copies:1,tier:2},{templateId:2,copies:0,tier:2}],{id:2,amount:-1});check(a.length===1&&made[0].kind===1&&a[0].fromY===338+40,'last copy: SlotRemove where the row was');
check(run([{templateId:1,copies:1,tier:2}],{id:1,amount:1},{reducedMotion:true}).length===0,'reduced motion: none');
check(run([{templateId:1,copies:1,tier:2}],{id:1,amount:1},{skin:2}).length===0,'Beta layout only');
check(run([{templateId:1,copies:1,tier:2}],{id:1,amount:1},{available:false}).length===0,'menu without cells: none');
check(run([{templateId:1,copies:1,tier:2}],{id:1,amount:1},{deckScroll178:80}).length===0,'row scrolled away: none');
check(run([{templateId:1,copies:0,tier:2}],{bulk:true,amount:0}).length===0,'bulk changes: none');
const report={checks,failures,actualActionScript:true,nativeGameTested:false};
if(process.argv[4])fs.writeFileSync(process.argv[4],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;
