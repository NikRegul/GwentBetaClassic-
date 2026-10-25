'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');let checks=0;
function check(v,n){if(!v)throw Error(n);checks++;}
for(const platform of ['classic','nextgen']){
 const root=path.resolve(process.argv[2],platform,'ui');
 const files=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'].map(p=>fs.readFileSync(path.join(root,p,'BetaGwentBoard.as')));
 check(files.every(b=>b.equals(files[0])&&b.subarray(0,3).equals(Buffer.from([239,187,191]))&&!b.toString().replaceAll('\r\n','').includes('\n')),'five identical BOM/CRLF sources');
 const source=files[0].toString('utf8');
 function extract(name){const start=source.indexOf('function '+name+'(');check(start>=0,'actual AS method exists');const open=source.indexOf('{',start);let depth=1,end=open+1;
  for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
  return source.slice(start,end).replace(/:(Object|int|Array|String|Boolean|void|Sprite|Number|TextField)\b/g,'');}
 const caster={x:11,y:22,width:80,height:120},wrong={x:999,y:111,width:80,height:120};
 const c=vm.createContext({requestId:32,requestSourceId:25,requestSourceTemplate:113301,requestPlayer:1,selected:4,
  displayedCards:{25:caster,4:wrong},activeCue:{source:4},aimSourceId:4,
  BetaGwentFullCatalog:{find(id){return {leader:id===201743};}},betaLeaderRect(side){return [side*100,50,80,120];}});
 vm.runInContext(extract('aimSourcePose091'),c);
 check(c.aimSourcePose091()===caster,'pending caster overrides stale selected card, cue and remembered action');
 c.displayedCards={4:wrong};check(c.aimSourcePose091()===null,'missing caster never falls back to unrelated unit');
 c.requestSourceTemplate=201743;check(c.aimSourcePose091().x===100,'leader ability aims from its seat');
 c.requestPlayer=2;check(c.aimSourcePose091().x===200,'leader side is preserved');
 c.requestId=0;check(c.aimSourcePose091()===wrong,'direct hand targeting retains selected card');
 check(extract('updateAimPreview').includes('var source=aimSourcePose091()'),'actual arrow drawing uses tested source');
 const painted=[],faces=[],backs=[];
 function Sprite(){this.addChild=()=>{};}
 Object.assign(c,{paintArt(p,id){painted.push(id);},paintBetaFace(p,id){faces.push(id);},paintCardBack(){backs.push(true);},Sprite,
  betaVisual(){return null;},text(){return {};},betaFace(){},paintStaticCardState(){},attachInspect(){},int:n=>n|0,
  BetaGwentFonts:{TITLE:'title'}});
 vm.runInContext(extract('paintChoiceArt')+'\n'+extract('compactOverviewCard'),c);
 c.paintChoiceArt({},113402,200,282);check(painted.pop()===113402,'Rally choice renders its own embedded illustration');
 c.paintChoiceArt({},113401,200,282);check(painted.pop()===113401,'Clear Skies choice retains its illustration');
 const card={templateId:113402,side:1,typeMask:2,title:'Rally'};
 c.compactOverviewCard(new Sprite(),card,{typeMask:2},0,0,240,340,48);
 check(faces.pop()===113402,'Rally uses normal framed card in the actual choice overview');
 card.hidden=true;c.compactOverviewCard(new Sprite(),card,{typeMask:2},0,0,240,340,48);
 check(backs.length===1&&faces.length===0,'hidden cards remain card backs');
 console.log(platform,'aim source checks passed');
}
console.log(JSON.stringify({checks,actualActionScript:true}));
