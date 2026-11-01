'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
process.env.ROOT=path.resolve(__dirname,'../..');
const H=require('./preview_screens096/harness.cjs'),c=H.ctx;
const file=process.argv[2]||process.env.ROOT+'/BetaGwent/ui/src/BetaGwentBoard.as',source=fs.readFileSync(file,'utf8');
let checks=0;const failures=[],check=(v,n)=>{checks++;if(!v)failures.push(n);};
const language=fs.readFileSync(path.join(path.dirname(file),'BetaGwentTextLanguage.as'),'utf8');
vm.runInContext(['betaWideButtonIn097','updatePadUi096','setTentativePlay099'].map(n=>H.extract(n,source)).join('\n')+'\n'+H.extract('layoutButton',language),c);
c.BetaGwentTextLanguage.fitButton=(field,size,minimum,height)=>c.layoutButton(field,{buttonFit:{size,minimum,height,originY:0,padding:4,align:'center'}});
Object.assign(c,{skin:3,padSwaps096:[],padMouseOnly096:[],padBar096:new c.Sprite(),padBarKey096:'',playing:false,selected:0,
 padIcon096(){},padGlyph096:()=>1,controllerContext:()=>({mode:'choice'}),padLegendItems096:()=>[],isMulliganHand:()=>false,
 getChildIndex:()=>0,numChildren:0,addChild(item){item.parent=c;},setChildIndex(){}});
for(const title of ['Закончить обмен','Скрыть карты','Очень длинная надпись для проверки переноса']){
 c.controller.active=false;const b=c.betaWideButtonIn097(new c.Sprite(),title,0,984,284,true,()=>{},'back');
 const caption=b.children.find(x=>x.isText);
 check(caption.x+caption.width/2===142,'mouse caption centered: '+title);
 check(Math.abs(caption.y+caption.height/2-24)<=.5,'caption vertically centered: '+title);
 c.controller.active=true;c.updatePadUi096();
 check(caption.x===58&&caption.width===208&&b.y===984,'pad reserves visible glyph and moves button: '+title);
 c.controller.active=false;c.updatePadUi096();
 check(caption.x===18&&caption.width===248&&b.y===1000,'return to mouse removes glyph inset: '+title);
 check(Math.abs(caption.y+caption.height/2-24)<=.5,'refit remains centered after device switch: '+title);
}
c.incoming={revision:9};c.setTentativePlay099(8,77);check(!c.incoming.tentativePlay099,'stale tentative source rejected');
c.setTentativePlay099(9,77);check(c.incoming.tentativePlay099===77,'current tentative source accepted');
check(!source.includes('Колесо — прокрутить описание'),'obsolete description hint removed');
// Execute the production pose adjustment independently of the rest of the
// display tree; verify the visible effect, not its particular offset formula.
const pose=source.match(/if\(!isHand&&int\(c\.id\)==tentativePlay099\)g=\{[^;]+;/);
function placed(hand,id){return vm.runInNewContext('var g={x:10,y:100,w:50,h:70};'+(pose?pose[0]:'')+';g',
 {isHand:hand,c:{id},tentativePlay099:77,cardHeight:70,Math,int:v=>v|0});}
const lifted=placed(false,77);
check(lifted.y<=80&&lifted.x===10&&lifted.w===50&&placed(true,77).y===100&&placed(false,78).y===100,'only the tentative board card is visibly lifted');
const menu=fs.readFileSync('BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws','utf8');
check(!/cancelPlayHistory098\.Invoke/.test(menu),'cancel does not erase an earlier committed history entry');
const report={checks,failures,sourceSha256:require('crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex'),actualActionScript:true,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;
