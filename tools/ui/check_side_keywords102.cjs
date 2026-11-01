'use strict';
// Beta CardSidePreviewTooltipHandler port: keyword tooltips appear LEFT of the
// battle side preview after the tooltip delay, stacked downwards, only for
// cards with a glossary, never for hidden cards, cleared when the preview is
// rebuilt or closed, and hidden by the same switch as the full-view pane.
// Runs the production AS functions in the preview harness (layout, not raster).
// Usage: node check_side_keywords102.cjs [BetaGwentBoard.as] [report.json]
const fs=require('fs'),path=require('path'),vm=require('vm');
process.env.ROOT=path.resolve(__dirname,'../..');
const H=require('./preview_screens096/harness.cjs'),c=H.ctx;
const boardFile=process.argv[2]||process.env.ROOT+'/BetaGwent/ui/src/BetaGwentBoard.as',board=fs.readFileSync(boardFile,'utf8');
let checks=0;const failures=[];function check(v,label){checks++;if(!v)failures.push(label);}
const texts=Object.fromEntries([...fs.readFileSync(process.env.ROOT+'/BetaGwent/ui/src/BetaGwentCardText.as','utf8').matchAll(/values\[(\d+)\]=(.*);/g)].map(m=>[m[1],JSON.parse(m[2])]));
let now=1000;
Object.assign(c,{detailOpen:false,detailKeywordsHidden096:false,reducedMotion:false,animations:[],getTimer:()=>now,
 sideKeywordParent102:null,sideKeywordAnchor102:null,sideKeywordPane102:null,sideKeywordCard102:0,sideKeywordFaction102:0,sideKeywordAt102:0,SIDE_KEYWORD_DELAY102:750});
c.BetaGwentCardText.find=id=>texts[id];c.BetaGwentTextLanguage.translate=s=>s;
vm.runInContext(['detailKeywordEntries096','scheduleSideKeywords102','clearSideKeywords102','updateSideKeywords102'].map(n=>H.extract(n,board)).join('\n'),c);
const withGlossary=Object.keys(texts).map(Number).find(id=>texts[id].glossary&&texts[id].glossary.split(/\n\s*\n/).length>=2);
const without=Object.keys(texts).map(Number).find(id=>!texts[id].glossary);
function preview(){const parent=new c.Sprite(),card=new c.Sprite();card.x=1539;card.y=173;parent.addChild(card);return {parent,card};}
// 1. Delay, placement left of the card, one tooltip per entry, downward stack.
{const {parent,card}=preview();c.scheduleSideKeywords102(parent,card,withGlossary,2);
 c.updateSideKeywords102();check(!c.sideKeywordPane102,'nothing before the tooltip delay');
 now+=749;c.updateSideKeywords102();check(!c.sideKeywordPane102,'still nothing at 749 ms');
 now+=1;c.updateSideKeywords102();const pane=c.sideKeywordPane102;
 check(pane&&pane.parent===parent,'tooltips appear after 750 ms in the preview');
 const n=c.detailKeywordEntries096(withGlossary).length;check(pane&&pane.numChildren===n,'one tooltip per glossary entry ('+n+')');
 check(pane&&pane.children.every((t,i)=>i===0||t.y>pane.children[i-1].y),'tooltips stack downwards');
 const anim=c.animations.find(a=>a.sprite===pane);check(anim&&anim.toX===1539-20-312&&anim.toY===173,'final column is 20 px left of the card, top aligned');
 check(pane&&!pane.mouseEnabled&&!pane.mouseChildren,'tooltips never take the mouse from the board');
 c.updateSideKeywords102();check(pane.parent===parent&&parent.children.filter(x=>x===pane).length===1,'no duplicate column on later frames');
 // Preview rebuilt for another card: the old card sprite is removed.
 // The harness mock keeps child.parent after removeChild; Flash clears it.
 parent.removeChild(card);card.parent=null;c.updateSideKeywords102();check(!c.sideKeywordPane102&&!parent.children.includes(pane),'rebuilt preview clears the column');}
// 2. Cards without glossary never get a column.
{const {parent,card}=preview();c.scheduleSideKeywords102(parent,card,without,2);now+=1000;c.updateSideKeywords102();check(!c.sideKeywordPane102&&!c.sideKeywordParent102,'no glossary: no column');}
// 3. Hidden switch, full view and closed preview.
{const {parent,card}=preview();c.detailKeywordsHidden096=true;c.scheduleSideKeywords102(parent,card,withGlossary,2);now+=1000;c.updateSideKeywords102();
 check(!c.sideKeywordPane102,'hidden switch suppresses side tooltips');c.detailKeywordsHidden096=false;
 c.scheduleSideKeywords102(parent,card,withGlossary,2);now+=1000;c.updateSideKeywords102();check(!!c.sideKeywordPane102,'shown again when the switch is on');
 c.detailKeywordsHidden096=true;c.updateSideKeywords102();check(!c.sideKeywordPane102,'switching off removes a shown column');c.detailKeywordsHidden096=false;
 c.scheduleSideKeywords102(parent,card,withGlossary,2);c.detailOpen=true;now+=1000;c.updateSideKeywords102();check(!c.sideKeywordPane102,'full card view replaces the side column');c.detailOpen=false;
 c.scheduleSideKeywords102(parent,card,withGlossary,2);Object.defineProperty(parent,'stage',{get:()=>null});now+=1000;c.updateSideKeywords102();check(!c.sideKeywordPane102,'closed preview gets no late column');}
// 4. Reduced motion: no delay and no slide.
{c.reducedMotion=true;c.animations=[];const {parent,card}=preview();c.scheduleSideKeywords102(parent,card,withGlossary,2);c.updateSideKeywords102();
 check(c.sideKeywordPane102&&c.sideKeywordPane102.x===1539-20-312&&c.animations.length===0,'reduced motion: immediate, no animation');c.reducedMotion=false;c.clearSideKeywords102();}
// 5. Long glossaries stay on screen.
{const {parent,card}=preview();card.y=900;c.scheduleSideKeywords102(parent,card,withGlossary,2);now+=1000;c.updateSideKeywords102();
 const pane=c.sideKeywordPane102,a=c.animations.find(x=>x.sprite===pane);check(a&&a.toY<900&&a.toY>=20,'long column moved up inside the screen');c.clearSideKeywords102();}
// 6. Source wiring: battle hover only, hidden cards excluded, frame update.
check(/updateDetailKeywords096\(\);updateSideKeywords102\(\);/.test(board),'frame loop updates the side column');
check(board.includes('if(!previewParent&&!big&&!pileOpen&&!browsingCatalog&&!editingDeck&&!selectingDecks&&!hidden&&int(c.templateId)>0)scheduleSideKeywords102(parent,card,int(c.templateId),fi);'),'only the battle hover preview of a visible card schedules tooltips');
const report={checks,failures,glossaryCard:withGlossary,sourceSha256:require('crypto').createHash('sha256').update(fs.readFileSync(boardFile)).digest('hex'),actualActionScript:true,nativeGameTested:false,scope:'Production AS functions in the layout harness; native raster, fonts and timing in game are not verified.'};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks,failures}));if(failures.length)process.exitCode=1;
