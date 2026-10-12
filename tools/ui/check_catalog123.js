// Card-local crafting uses actual AS helper, hover handlers and detail renderer.
'use strict';
const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
function extract(name){
 const start=source.indexOf('function '+name+'('),open=source.indexOf('{',start);let depth=1,end=open+1;
 if(start<0)throw Error(name);for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(start,end).replace(/:(DisplayObject|Sprite|String|Function|Object|Rectangle|void|int|Number|Array|Boolean|MouseEvent|TextField)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');
}
class Sprite{
 constructor(){this.children=[];this.handlers={};this.graphics={lineStyle(){},drawRect(){}};}
 addChild(c){this.children.push(c);return c;}get numChildren(){return this.children.length;}removeChildAt(i){return this.children.splice(i,1)[0];}
 addEventListener(name,fn){const previous=this.handlers[name];this.handlers[name]=previous?function(e){previous(e);fn(e);}:fn;}
}
const context=vm.createContext({Sprite,Math,MouseEvent:{ROLL_OVER:'over',ROLL_OUT:'out',MOUSE_DOWN:'down',CLICK:'click'},Rectangle:class{}});
vm.runInContext(`var catalogDetail=new Sprite(),previewLayer=new Sprite(),battlePreview=new Sprite(),catalogPicked=null;
var ownedCopies={},scraps=1160,skin=3,browsingCatalog=true,dragging=false,detailOpen=false,editingDeck=false;
var ready=true,entryMode=2,editorCraft=null;
var hoveredCard,hoveredDetail,lastInspectedCard,hoverCardId=0,hoverPreviewAt=0,keyboardFocusId=0,selected=0,inspection=null;
var controller={registerControl:function(){}},RIGHT_CLICK_EVENT='right',BetaGwentFonts={};
var crafted=[],cleared=0,uiMotions=[],reducedMotion=false;
function getTimer(){return 100;}
function int(v){return v|0;}function text(parent,label){var c={label};parent.addChild(c);return c;}
function cardRarity(){return 8;}function craftCost(){return 800;}
function drawBetaSidePreview(c,d,parent){if(!parent)throw Error('collection preview requires a separate container');parent.addChild({card:c});}
function editorBetaButton(parent,label,x,y,w,h,enabled,callback){var b=new Sprite();Object.assign(b,{label,x,y,w,h,enabled,callback});parent.addChild(b);if(enabled)b.addEventListener('click',function(e){e.stopPropagation();callback();});return b;}
function send(name,args){crafted.push({name,args});}function redrawCatalogDetail(){redrawBetaCatalogDetail();}
function showBattleCard(){throw Error('collection must not use transient battle preview');}
function clearBattlePreview(){cleared++;}function updateFocusedInspection(){}function showEditorCard(){}
`+extract('uiTween')+'\n'+extract('redrawBetaCatalogDetail')+'\n'+extract('attachInspect')+'\n'+extract('cardCraftButton'),context);
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
const c={templateId:201743,title:'Queen',description:'Consume allies',tier:1},tile=new Sprite();
context.attachInspect(tile,c,{description:c.description},173,231);tile.handlers.over({});
context.cardCraftButton(tile,c,173,231);
const button=tile.children.find(c=>c.callback);
check(button&&button.enabled&&button.y+button.h<=231,'missing leader exposes Craft inside the card');
check(!context.catalogDetail.children.some(c=>c.callback),'Craft is on the card instead of the side panel');
check(context.catalogPicked===c,'hover sets persistent collection selection');
const before=context.catalogDetail.numChildren;tile.handlers.out({});
check(context.catalogDetail.numChildren===before,'leaving card preserves detail and Craft button');
check(context.catalogPicked===c&&context.cleared===0,'leaving card keeps selection and does not clear preview');
let stopped=0;button.handlers.click({stopPropagation(){stopped++;}});
check(context.crafted.length===1&&context.crafted[0].name==='OnBetaGwentCollectionCraft'&&context.crafted[0].args[0]===c.templateId,'Craft sends the preserved selected template');
check(stopped>0,'Craft click does not bubble to parent card selection or Add');
context.ownedCopies[c.templateId]=1;let updated=new Sprite();context.cardCraftButton(updated,c,173,231);
check(updated.numChildren===0,'updated ownership removes crafting at the cap');
context.ownedCopies[c.templateId]=0;context.scraps=799;updated=new Sprite();context.cardCraftButton(updated,c,173,231);
check(updated.children[0].enabled===false,'insufficient scraps disables crafting');
updated.children[0].handlers.click({stopPropagation(){stopped++;}});
check(context.crafted.length===1,'disabled Craft does not send a request');
context.scraps=1160;context.editingDeck=true;context.browsingCatalog=false;
const other={templateId:132303,title:'Nekker',tier:2},editor=new Sprite();context.cardCraftButton(editor,other,164,220);
check(editor.children[0].enabled,'editor card has an enabled Craft button');
context.catalogPicked=c;editor.children[0].handlers.click({stopPropagation(){}});
check(context.crafted[1].args[0]===other.templateId,'editor button sends its own card even when another card was previewed');
context.ready=false;updated=new Sprite();context.cardCraftButton(updated,other,164,220);
check(!updated.children[0].enabled,'busy editor disables Craft');
context.ready=true;context.entryMode=0;updated=new Sprite();context.cardCraftButton(updated,other,164,220);
check(updated.numChildren===0,'unrestricted practice editor does not offer paid crafting');
for(const name of ['redrawCatalogGrid','redrawBetaCatalogGrid','redrawEditorCollection','redrawBetaCollection'])check(extract(name).includes('cardCraftButton(tile,c,'),name+' uses the common card-local control');
const report={stage:123,checks,actualActionScript:true,nativeMouseTested:false};
fs.writeFileSync('docs/evidence/catalog123.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
