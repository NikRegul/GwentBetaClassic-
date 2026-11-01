// Actual board-target registration -> controller focus -> actual aiming renderer.
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),crypto=require('crypto');
const file=process.argv[2]||'BetaGwent/ui/src/BetaGwentBoard.as',source=fs.readFileSync(file,'utf8');
function strip(text){return text.replace(/:\s*(?:Object|String|Function|void|int|uint|Number|Boolean|Array|Sprite|TextField|MouseEvent)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))');}
function extract(name){const start=source.indexOf('function '+name+'(');assert(start>=0,name);const open=source.indexOf('{',start);let end=open+1,d=1;while(d){d+=(source[end]==='{')-(source[end]==='}');end++;}return strip(source.slice(start,end));}
const at=source.indexOf('var target:Object=requestKind==2?findRequestCard(c.id):null;');assert(at>=0);
const start=source.indexOf('if(requestId>0 && target!=null)',at),open=source.indexOf('{',start);let end=open+1,depth=1;
while(depth){depth+=(source[end]==='{')-(source[end]==='}');end++;}
const registration=strip(source.slice(at,end));
let checks=0;const failures=[];function check(v,label){checks++;if(!v)failures.push(label);}
const caster={id:7,zone:8,side:1},first={id:44,zone:1,side:2},second={id:45,zone:4,side:1};
function context(){
 const c=vm.createContext({Math,MouseEvent:{CLICK:'click'},int:v=>v|0,uint:v=>v>>>0,requestId:91,requestKind:2,requestPlayer:1,requestSourceId:7,requestSourceTemplate:123,
  selected:99,revision:3,rowRequest:false,ready:true,keyboardFocusId:0,cardWidth:80,cardHeight:110,detailOpen:false,pileOpen:false,playing:false,editingDeck:false,selectingDecks:false,browsingCatalog:false,
  cards:[caster,first,second],requestCards:[{id:44,title:'Target 1'},{id:45,title:'Target 2'}],
  displayedCards:{7:{x:600,y:900,width:100,height:140},44:{x:400,y:100,width:80,height:110},45:{x:700,y:300,width:80,height:110},99:{x:1,y:1,width:80,height:110}},
  hoveredCard:first,aimKey:'',arrows:[],clears:0,markTarget(){},canPlacePending:()=>false,canDirectTarget:()=>false,
  BetaGwentFullCatalog:{find:()=>null},betaLeaderRect:()=>[10,10,80,100],requestAction:()=>()=>{},cardDetails:{44:{description:'first'},45:{description:'second'}},
 });
 c.aimLayer={graphics:{clear(){c.clears++;}}};c.drawCueArrow=(...args)=>c.arrows.push(args.slice(1));
 c.controller={active:true,focus:null,getFocus(){return this.focus;},registerControl(sprite,label,action,card,detail,tag){
  this.focus={sprite,card,detail,tag};}};
 c.p={addEventListener(){}};
 vm.runInContext(['findRequestCard','cardById','attachRequestCard','aimSourcePose091','updateAimPreview'].map(extract).join('\n'),c);
 c.register=card=>{c.c=card;c.detail=c.cardDetails[card.id];vm.runInContext(registration,c);};
 return c;
}
// Real rendering path, with only drawing/host objects replaced by spies.
{const c=context();c.controller.active=false;c.updateAimPreview();check(c.arrows.length===1,'mouse draws legal board target');
 const mouse=JSON.stringify(c.arrows[0]);c.arrows=[];c.aimKey='';c.controller.active=true;c.register(first);c.updateAimPreview();
 check(c.controller.focus.card===first,'controller retains complete live card at registration');
 check(c.arrows.length===1&&JSON.stringify(c.arrows[0])===mouse,'controller arrow equals mouse arrow including caster');
 check(c.arrows[0]&&c.arrows[0][0]===600&&c.arrows[0][1]===900,'request caster overrides stale selected card');
 c.arrows=[];c.updateAimPreview();check(c.arrows.length===0,'same target does not redraw unnecessarily');
 c.register(second);c.updateAimPreview();check(c.arrows.length===1&&c.arrows[0][4]===700&&c.arrows[0][5]===300,'focus navigation updates destination');
 c.controller.focus={tag:'control',card:null};c.updateAimPreview();check(c.aimKey===''&&c.clears>0,'leaving target clears arrow');}
for(const guard of ['detailOpen','pileOpen','playing','editingDeck','selectingDecks','browsingCatalog']){
 const c=context();c.register(first);c[guard]=true;c.updateAimPreview();check(c.arrows.length===0,'no arrow while '+guard);
}
for(const [zone,label]of [[8,'hand'],[16,'deck'],[32,'graveyard']]){
 const c=context();const target={id:44,side:1,zone};c.controller.focus={card:target};c.displayedCards[44].zone=zone;c.updateAimPreview();
 check(c.arrows.length===0,'no board arrow into '+label+' choice');
}
{const c=context();c.register(first);c.requestPlayer=2;c.updateAimPreview();check(c.arrows.length===0,'opponent request has no human aim arrow');}
{const c=context();c.register(first);c.rowRequest=true;c.updateAimPreview();check(c.arrows.length===0,'row choice does not invent a unit target');}
{const c=context();c.register(first);c.canPlacePending=()=>true;c.updateAimPreview();check(c.arrows.length===0,'placement keeps its own preview');}
{const c=context();c.controller.focus={card:{id:999,zone:1,side:2}};c.updateAimPreview();check(c.arrows.length===0,'unoffered card has no arrow');}
{const c=context();c.register(first);delete c.displayedCards[44];c.updateAimPreview();check(c.arrows.length===0,'missing target geometry has no arrow');}
{const c=context();c.requestId=0;c.selected=7;c.canDirectTarget=card=>card===first;c.controller.focus={card:first};c.updateAimPreview();check(c.arrows.length===1&&c.arrows[0][0]===600,'direct targeting from hand remains intact');}
{const c=context();const hidden={id:44,hidden:true,zone:32,title:'Hidden'};c.attachRequestCard(c.p,44,hidden,{});check(c.controller.focus.card===hidden,'explicit hidden choice presentation is preserved');}
const report={checks,failures,sourceSha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),actualActionScript:true,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;
