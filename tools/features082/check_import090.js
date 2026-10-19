'use strict';
// Import with crafting: the real ActionScript functions in a mocked host.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..');let checks=0;
const uiBuild='BetaGwent/build/'+(process.env.BG_UI||'release090-bannersUI');
function check(ok,msg){assert(ok,msg);checks++;}
function fn(s,name){const a=s.indexOf('function '+name+'('),b=s.indexOf('{',a);assert(a>=0,name);let n=1,i=b+1;for(;n;i++){if(s[i]==='{')n++;if(s[i]==='}')n--;}
 return s.slice(a,i).replace(/:(?:String|Object|void|int|uint|Number|Array|Boolean|Sprite|TextField|Event|MouseEvent|Function)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((?:var )?(\w+) in (\w+)\)/g,'for(var $1 of $2)');}
function host(source){
 const sent=[],buttons=[];const sprite=()=>({children:[],get numChildren(){return this.children.length},addChild(c){this.children.push(c);return c},removeChildAt(){this.children.shift()}});
 const c=vm.createContext({sent,buttons,ready:true,nameOpen:true,exchangeImport:true,revision:7,nameRevision:7,scraps:0,
  nameField:{text:''},exchangeMessage:{text:''},exchangeGrid:sprite(),exchangeActions:sprite(),
  exchangeMissing:[],exchangeCost:0,exchangeBlocked:false,exchangeChecked:false,exchangePage:0,exchangeQuotedCode:'',
  Math,int:x=>x|0,String,Sprite:function(){return sprite();},
  send(n,a){sent.push([n,...a]);},BetaGwentTextLanguage:{assign(f,t){f.text=t;}},
  BetaGwentFullCatalog:{find:id=>({title:'Card '+id,typeMask:4,power:5,tier:2,templateId:id})},
  BetaGwentFonts:{TITLE:'t'},craftCost:c=>c.templateId===1?800:30,
  paintBetaFace(){},betaPowerField(){},betaLabel(){return {};},text(){return {};},closeNameInput(){},pasteExchange(){},
  editorSmallButton(p,title,x,y,w,h,enabled,cb){buttons.push({title,enabled,cb});},
  editorBetaButton(p,title,x,y,w,h,enabled,cb){buttons.push({title,enabled,cb,tile:true});return {};}});
 c.Sprite=function(){return Object.assign(sprite(),{x:0,y:0});};
 vm.runInContext(['exchangeCode','exchangeCurrent','checkDeckExchange','submitDeckExchange','exchangeCraft','setDeckExchangeMissing','redrawExchange'].map(n=>fn(source,n)).join('\n'),c);
 return c;
}
const btn=(c,t)=>c.buttons.filter(b=>b.title.startsWith(t)).pop();
for(const platform of ['classic','nextgen']){
 const s=fs.readFileSync(path.join(root,uiBuild,platform,'ui/src/BetaGwentBoard.as'),'utf8');
 const c=host(s);const code='BG1:32:200160:'+Array(25).fill(112102).join(',');
 c.nameField.text=code;c.redrawExchange();
 check(!btn(c,'Импортировать').enabled,'import disabled before check');
 c.submitDeckExchange();check(c.sent.pop()[0]==='OnBetaGwentDeckImportCheck','import first checks, never imports unchecked');
 c.buttons.length=0;c.setDeckExchangeMissing(7,'1,112102','1,2',860,100,false);
 check(c.exchangeMissing.length===2&&c.exchangeMissing[1].count===2,'missing list parsed');
 check(!btn(c,'Импортировать').enabled,'import disabled while cards are missing');
 check(!btn(c,'Создать все').enabled,'craft all disabled without enough scraps');
 const tiles=c.buttons.filter(b=>b.tile);check(tiles.length===2&&!tiles[0].enabled&&tiles[1].enabled,'per-card craft enabled by own price');
 tiles[1].cb();check(JSON.stringify(c.sent.pop())===JSON.stringify(['OnBetaGwentDeckImportCraft',7,code,112102]),'per-card craft sends that card');
 c.submitDeckExchange();check(c.sent.length===0&&c.exchangeMessage.text.includes('Сначала создайте'),'import refused while missing');
 c.buttons.length=0;c.setDeckExchangeMissing(7,'1,112102','1,2',860,900,false);
 btn(c,'Создать все').cb();check(c.sent.pop()[3]===0,'craft all sends id 0');
 c.buttons.length=0;c.setDeckExchangeMissing(7,'1','1',800,900,true);
 check(!btn(c,'Создать все').enabled&&c.buttons.filter(b=>b.tile).every(b=>!b.enabled)&&c.exchangeMessage.text.includes('бочки'),'keg choice blocks crafting');
 c.buttons.length=0;c.setDeckExchangeMissing(7,'','',0,40,false);
 check(btn(c,'Импортировать').enabled&&c.exchangeMessage.text.includes('Все карты есть'),'import enabled when nothing is missing');
 btn(c,'Импортировать').cb();check(JSON.stringify(c.sent.pop())===JSON.stringify(['OnBetaGwentDeckImport',7,code,false]),'import sends the checked code');
 c.nameField.text=code+',1';c.buttons.length=0;c.redrawExchange();check(!btn(c,'Импортировать').enabled,'edited code needs a new check');
 c.setDeckExchangeMissing(6,'','',0,0,false);check(!c.exchangeCurrent(),'stale revision ignored');
 const many=Array.from({length:20},(_,i)=>200000+i).join(',');c.nameField.text=code;c.exchangeQuotedCode=code;c.buttons.length=0;
 c.setDeckExchangeMissing(7,many,Array(20).fill(1).join(','),600,0,false);check(c.buttons.filter(b=>b.tile).length===16&&btn(c,'→'),'paging over 16 cards');

 // Card inspection (Beta UICardPreview): neighbour navigation and layout markers.
 const nav=vm.createContext({detailOpen:true,opened:[],detailNav:[{templateId:1,description:'a'},{templateId:2,description:'b'},{templateId:3,description:'c'}],detailNavCard:{templateId:2},int:x=>x|0});
 nav.openCardDetail=(t,d,kb,kn)=>{nav.opened.push([t.templateId,kb,kn]);nav.detailNavCard=t;};
 vm.runInContext(fn(s,'stepCardDetail'),nav);
 nav.stepCardDetail(1);nav.stepCardDetail(1);nav.stepCardDetail(-1);
 check(JSON.stringify(nav.opened)===JSON.stringify([[3,false,true],[2,false,true]]),'inspect ←/→ steps within the list and stops at its end');
 const detail=fn(s,'openCardDetail');
 check(detail.includes('"СИЛА"')&&detail.includes('"Назад"')&&detail.includes('original.flavor')&&detail.includes('cardReading(c,detail,true,true,false'),'Beta inspect layout: power row, flavour on top, Back button');
 check(!detail.includes('Вернуться к игре'),'old return button removed');
 let depth=0,bad=false;for(const ch of s.replace(/"(?:[^"\\]|\\.)*"/g,'""').replace(/\/\/[^\n]*/g,'')){if(ch==='{')depth++;if(ch==='}')depth--;if(depth<0)bad=true;}
 check(!bad&&depth===0,'balanced braces '+platform);

 const round=fn(s,'drawBetaRoundBanner');
 check(round.includes('ROUND_SCORE_MS')&&(round.includes('betaRoundCrownId')||round.includes('-1525')&&round.includes('-1527')&&round.includes('-1523'))&&round.includes('scoreRow.visible=!second'),'round end: crowns + score first, then next-round line');
 check(s.includes('case 6:return 6000;'),'round end lasts ~6 s like Beta');
 const set=fn(s,'setDeckExchange');check(set.includes('split("\\\\n").join("\\n")'),'literal \\n converted');
 for(const dir of ['src-BetaGwentBoard','src-DeckBuilder','src-GwintGame','src-BetaGwentKeg'])
  check(fs.readFileSync(path.join(root,uiBuild,platform,'ui',dir,'BetaGwentBoard.as')).equals(fs.readFileSync(path.join(root,uiBuild,platform,'ui/src/BetaGwentBoard.as'))),'mirror '+platform+'/'+dir);
}
const ws=fs.readFileSync(path.join(root,uiBuild,'scripts/game/betagwent/developmentBoardMenu.ws'),'utf8');
check(/event OnBetaGwentDeckImportCheck\(/.test(ws)&&/event OnBetaGwentDeckImportCraft\(/.test(ws),'script events exist');
check(/missing\.Size\(\)>0\)\{PublishExchangeMissing\(parsed,"Сначала создайте/.test(ws),'script refuses import while missing');
check(!/BetaGwentCraftExchange[^\n]*\n[^\n]*PublishDeckExchange\("","Колода импортирована/.test(ws),'crafting never imports');
console.log(JSON.stringify({checks}));
