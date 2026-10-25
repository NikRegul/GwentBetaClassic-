'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');let checks=0;
function check(v,n){if(!v)throw Error(n);checks++;}
function extract(source,name){const start=source.indexOf('function '+name+'(');check(start>=0,'entry exists');const open=source.indexOf('{',start);let depth=1,end=open+1;for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(start,end).replace(/:\s*(?:CR4Player|CR4GwintManager|int)\b/g,'').replace(/optional\s+/g,'');}
const build=path.resolve(process.argv[2]);
for(const platform of ['classic','nextgen']){
 const folder=platform==='classic'?'classic-prepared-final/Mods/modBetaGwentClassic132/content/scripts':'scripts';
 const raw=fs.readFileSync(path.join(build,folder,'game/betagwent/developmentBoardMenu.ws'));
 const source=raw.toString(platform==='classic'?'utf16le':'utf8');
 const manager={betaNpcPending:true,gameRequested:true},player={betaPracticeRequested:false},calls=[];let open=false;
 const c=vm.createContext({thePlayer:player,BetaGwentDebugOpponentAllowed:id=>id>=54&&id<=99,LogChannel(){},
  theGame:{GetGuiManager(){return {IsAnyMenu(){return open;}}},GetGwintManager(){return manager;},RequestMenu(name){calls.push(name);}}});
 const entry=extract(source,'bgboard_open');vm.runInContext(entry,c);c.bgboard_open(61);
 check(calls[0]===(platform==='classic'?'DeckBuilder':'BetaGwentBoard'),'practice uses supported menu '+platform);
 check(player.betaPracticeRequested&&manager.betaDebugEnemyPreset===61,'practice flag and chosen deck reach menu');
 check(manager.betaNpcPending&&manager.gameRequested,'console entry does not modify native quest flags');
 c.bgboard_open(1);check(calls.length===1,'invalid archetype rejected');open=true;c.bgboard_open(67);check(calls.length===1,'existing menu is not interrupted');
 const start=source.indexOf('entryMode=BetaGwentNativeEntryMode('),end=source.indexOf('npcMatch=entryMode==2;',start);
 check(start>=0&&end>start,'actual initialization mode block exists');
 const init=vm.createContext({entryMode:2,pendingBefore:true,requestedBefore:true,nativePlayer:player,kegOnly:false,effectGallery:false,GetMenuName(){return 'DeckBuilder';},BetaGwentNativeEntryMode(){return 2;}});
 vm.runInContext(source.slice(start,end),init);check(init.entryMode===0,'practice overrides stale native entry flags');
 init.nativePlayer={betaPracticeRequested:false};vm.runInContext(source.slice(start,end),init);check(init.entryMode===2,'normal NPC path remains native');
 console.log(platform,'practice entry checks passed');
}
console.log(JSON.stringify({checks,actualWitcherScriptEntry:true,nativeGameTested:false}));
