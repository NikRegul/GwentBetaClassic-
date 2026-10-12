// Verify real AS preview entry points and crown half selection, without Flash export.
'use strict';
const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
function extract(name){
 const start=source.indexOf('function '+name+'('),open=source.indexOf('{',start);let depth=1,end=open+1;
 if(start<0)throw Error(name);
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(start,end).replace(/:(Sprite|TextField|String|Object|void|int|Number|Array|Boolean|uint)\b(?=\s*(?:[,)=;{]|in\b))/g,'');
}
const c=vm.createContext({Math,Number,String});
vm.runInContext(`var calls=[],skin=3;function int(v){return v|0;}
function paintBetaFace(...a){calls.push(['face',...a]);}function paintCardBack(...a){calls.push(['back',...a]);}
function paintStaticCardState(...a){calls.push(['status',...a]);}function betaPowerField(...a){calls.push(['power',...a]);}
function powerColor(){return 0xFFFFFF;}function paintArt(...a){calls.push(['legacy',...a]);}function text(...a){calls.push(['text',...a]);}
`+extract('paintPlacementCard')+extract('betaCrownHalfId'),c);
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;console.log('PASS',n);}
for(const zone of [1,2,4,8]){
 const unit={templateId:200105,side:1,zone,power:7,armor:2,tokens:7,timer:1};c.calls=[];c.paintPlacementCard({},unit,104,127);
 check(c.calls[0][0]==='face'&&c.calls[0][2]===unit.templateId,'complete Beta face used in zone '+zone);
 check(c.calls.some(v=>v[0]==='status'&&v[2]===unit),'preview keeps the same live armour, lock, resilience, spy and timer snapshot '+zone);
 check(c.calls.some(v=>v[0]==='power'&&v[2]==='7'),'preview power uses the Beta banner font '+zone);
 check(!c.calls.some(v=>v[0]==='legacy'||v[0]==='text'),'no bare art or plain number replaces the Beta face '+zone);
}
c.calls=[];c.paintPlacementCard({},{templateId:132201,zone:1,side:2,power:10,tokens:8},104,127);
check(c.calls.length===1&&c.calls[0][0]==='back','concealed enemy ambush keeps its back and hides power');
check(extract('showPlacementGhost').includes('paintPlacementCard(u,unit,')&&extract('showPlacementGhost').includes('paintPlacementCard(ghost,c,'),'both existing row cards and the insertion ghost share complete rendering');
check(extract('onDragMove').includes('paintPlacementCard(dragGhost,c,94,140)'),'dragged hand card also retains its complete face');
check(extract('drawCards').includes('paintPlacementCard(oldArt,before,'),'transformation keeps the old card frame until the flip finishes');
check([c.betaCrownHalfId(1,1),c.betaCrownHalfId(1,2)].join(',')==='-1540,-1541','player victory uses both original blue crown halves');
check([c.betaCrownHalfId(2,1),c.betaCrownHalfId(2,2)].join(',')==='-1542,-1543','opponent victory uses both original red crown halves');
check(extract('drawBetaBattleHud').includes('paintArt(crown,betaCrownHalfId(side,halfIndex)'),'live HUD uses the checked crown selection');
const report={stage:126,checks,actualActionScript:true,nativeVisualVerified:false,releaseBuildStarted:false};
fs.writeFileSync('docs/evidence/card-presentation126.json',JSON.stringify(report,null,2)+'\n');
