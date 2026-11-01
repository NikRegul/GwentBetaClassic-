'use strict';
// 0.9.6 battle controller legend: production bodies of padGlyph096 and
// padLegendItems096; the side text box is hidden in the battle modes.
const fs=require('fs'),vm=require('vm');
const file=process.argv[2]||'BetaGwent/ui/src/BetaGwentBoard.as',source=fs.readFileSync(file,'utf8');
let checks=0;const failures=[];const check=(ok,label)=>{checks++;if(!ok)failures.push(label);};
function extract(name){const start=source.indexOf('function '+name+'(');const open=source.indexOf('{',start);let end=open+1,d=1;
 while(d){d+=(source[end]==='{')-(source[end]==='}');end++;}
 return source.slice(start,end).replace(/:\s*(?:Object|Array|int|Number|Boolean|void|String)(?=\s*(?:[,)=;{]|in\b))/g,'');}
const hud={PAD_A:1,PAD_B:2,PAD_X:3,PAD_Y:4,PAD_LB:5,PAD_RB:6,PAD_LT:7,PAD_RT:8,PAD_BACK:9,PAD_START:10,PAD_RS:11};
const c=vm.createContext({BetaGwentHud104:hud,controller:{swap:false,active:true,device:0},skin:3,detailOpen:false,pileOpen:false,controllerMenuOpen:false,nameOpen:false,
 playing:false,selected:0,mode:'battle',quick:false,caranthir:false,mulligan:false});
vm.runInContext(['padGlyph096','padLegendItems096'].map(extract).join('\n')+';function controllerContext(){return {mode:mode};}function controllerQuickSpecial(){return quick;}function isCaranthirChoice(){return caranthir;}function isMulliganHand(){return mulligan;}',c);
const labels=()=>c.padLegendItems096().map(x=>x[1]);
check(c.padGlyph096('accept')===1&&c.padGlyph096('back')===2,'A accepts, B goes back');
c.controller.swap=true;check(c.padGlyph096('accept')===2&&c.padGlyph096('back')===1,'swapped accept/cancel follows the game setting');c.controller.swap=false;
check(labels().join()==='Выбрать,Пас (удерж.),Действия,Сбросы,Осмотреть','hand: select, hold pass, actions, piles, inspect in the shared grid');
c.selected=5;c.quick=true;check(labels().join()==='Сыграть,Отменить','quick special: play / cancel');c.selected=0;c.quick=false;
for(const [mode,want] of [['inspect','Описание,К руке'],['placement','Поставить,Отменить,Ряд'],['target','Применить,Кнопки выбора'],['rows','Применить,Назад'],['choice','Выбрать,Описание'],['detail','Описание,Соседние карты,Закрыть'],['editor','Добавить / убрать,Карта,− / +,Прокрутка,Сохранить']]){c.mode=mode;check(labels().join()===want,mode+' legend');}
c.mode='target';c.caranthir=true;check(labels().join()==='Применить,Без перемещения','Caranthir: LB/RB move-free frost');c.caranthir=false;
c.mode='history';check(labels().join()==='Подробности,Страницы,Назад','history has its own page/back legend instead of card-preview controls');
c.playing=true;check(labels().join()==='Ускорить,Пропустить,Настройки','replay legend');c.playing=false;
c.controller.active=false;check(labels().length===0,'mouse: no pad legend');c.controller.active=true;
c.mode='choice';c.mulligan=true;check(labels()[0]==='Заменить','mulligan: replace');c.mulligan=false;c.mode='battle';
c.mode='battle';check(c.padLegendItems096().every(x=>x[0].length<=2)&&c.padLegendItems096().length<=6,'fits the 2 x 3 box');
check(source.includes('hintVisible:skin!=3,hintSide:')&&source.includes('hintVisible:skin!=3,hintY:1040'),'text hint widget replaced by pad glyphs on every Beta screen');
check(source.includes('var now:int=getTimer();updatePadUi096();'),'pad bar follows mode/device every frame');
check(source.includes('passHover096=!controller.active&&stage!=null&&coin.hitTestPoint('),'coin hover read from the cursor, never with a pad');
check(/mouseOnly096\(hint\)/.test(source)&&!source.includes('Колесо — прокрутить описание'),'mouse hint follows device and obsolete description hint is removed');
check(source.includes('hintRight=1880;drawPadLegend096();'),'legend drawn with the battle actions');
check(source.includes('refreshPadLegend096();return;}'),'device switch invalidates the pad bar');
const report={checks,failures,sourceSha256:require('crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex'),actualActionScript:true,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;
