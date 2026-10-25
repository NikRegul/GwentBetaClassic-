// A concealed enemy is published as type=unit, tier=unknown (0), template=0.
// Test targeting the public stub; never reveal its hidden title, tier or power.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');let checks=0;
function check(v,n){if(!v)throw Error(n);checks++;}
const root=path.resolve(process.argv[2]||'BetaGwent/ui');
const dirs=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'];
const files=dirs.map(d=>fs.readFileSync(path.join(root,d,'BetaGwentBoard.as')));
check(files.every(b=>b.equals(files[0])&&b.subarray(0,3).equals(Buffer.from([239,187,191]))&&!b.toString().replaceAll('\r\n','').includes('\n')),'five matching Board copies with BOM/CRLF');
const source=files[0].toString('utf8');
function extract(name){
 const start=source.indexOf('function '+name+'(');if(start<0)return '';
 const open=source.indexOf('{',start);let depth=1,end=open+1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(start,end).replace(/:(Object|int|Array|String|Boolean|void|Function|RegExp|Sprite|MouseEvent)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');
}
const target={id:42,templateId:0,title:'Засада',side:2,zone:1,tokens:8,power:0,timer:-1};
const details={description:'Скрытая засада соперника.',tier:0,typeMask:4};
const rule={kind:1,side:0,types:4,tiers:15,ignore:256,maximum:0};
const context=vm.createContext({int:n=>n|0,MouseEvent:{CLICK:'click'},canAct:()=>true,canPlaceBefore:()=>false,
 ready:true,playing:false,detailOpen:false,pileOpen:false,flags:0,current:1,requestId:0,requestKind:0,rowRequest:false,
 selected:7,revision:11,cards:[target],cardDetails:{42:details},playRules:{7:rule},opened:0,sent:[],
 controller:{registerControl(){}},openCardDetail(){context.opened++;},submitBoard(name,args){context.sent.push({name,args});}});
vm.runInContext(['enemyAmbush','directTargetTier091','canDirectTarget','battleDisabledReason','controllerCardAction','attachDirectTarget'].map(extract).join('\n'),context);
const original=JSON.stringify({target,details});
check(context.canDirectTarget(target),'Shackles can select the face-down enemy without knowing its tier');
check(context.battleDisabledReason(target)==='','allowed ambush has no false rarity error');
context.controllerCardAction(42);
check(context.sent.length===1&&context.sent[0].name==='OnBetaGwentBoardPlayTarget'&&context.sent[0].args.join(',')==='11,7,42','gamepad sends authoritative target ID');
check(context.opened===0,'target activation does not inspect or reveal the ambush');
const tile={handlers:{},addEventListener(name,fn){this.handlers[name]=fn;}};
context.attachDirectTarget(tile,42);tile.handlers.click({stopPropagation(){}});
check(context.sent.length===2&&context.sent[1].args[2]===42,'mouse sends the same authoritative target ID');
context.revision=12;tile.handlers.click({stopPropagation(){}});check(context.sent.length===2,'stale click is ignored');context.revision=11;
check(JSON.stringify({target,details})===original,'selection preserves the concealed public stub');
rule.ignore=264;check(!context.canDirectTarget(target),'ordinary effects still exclude Ambush');
rule.ignore=256;rule.tiers=6;check(!context.canDirectTarget(target),'unknown tier is not guessed for rarity-restricted effects');
rule.tiers=15;rule.maximum=6;check(!context.canDirectTarget(target),'unknown power is not treated as zero for a power limit');rule.maximum=0;
target.tokens=8|256;check(!context.canDirectTarget(target),'immune targets remain excluded');target.tokens=8;
target.zone=8;check(!context.canDirectTarget(target),'face-down hand card is not a board target');target.zone=1;
target.side=1;check(!context.canDirectTarget(target),'unknown-tier exception is limited to enemy ambush stubs');
details.tier=4;check(context.canDirectTarget(target),'own ambush with known tier keeps normal targeting');
target.side=2;target.tokens=4;check(context.canDirectTarget(target),'revealed locked unit remains eligible for unlocking');
rule.side=1;check(!context.canDirectTarget(target),'side restriction remains effective');rule.side=0;
context.canAct=()=>false;check(!context.canDirectTarget(target),'targeting is disabled outside a legal player action');
check(extract('dragTarget').includes('canDirectTarget(c)'),'drag targeting uses the same eligibility check');
console.log(JSON.stringify({checks,actualActionScript:true,nativeGameTested:false}));
