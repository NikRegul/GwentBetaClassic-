'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),ctx=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const output={v:[]};check(BetaGwentDuelPresetDeck(96,output),'Bran deck resolves');const deck=output.v;
check(deck.length===25&&!deck.includes(201773)&&deck.filter(i=>i===152109).length===1,'Triss replaced once without changing deck size');
check(deck.filter(i=>BetaGwentDuelDefinition(i).header.tierMask===8).length===4,'four gold limit preserved');
check(deck.filter(i=>{const d=BetaGwentDuelDefinition(i);return d.header.tierMask===2&&d.header.typeMask===2;}).length===0,'original Triss had no own bronze special target');
const g=fixture();g.live.filter(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8).forEach(c=>c.Move(2,512,0));
g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();g.aiSimDamp=40;
const left=add(g,112405,2,0,2,9),right=add(g,200040,2,1),ship=add(g,152109,8,0),leftBase=left.Snapshot().power.basePower,rightPower=right.Snapshot().power.currentPower;
check(g.OpponentStep()&&!g.IsFatal()&&!g.IsPending(),'real AI plays the replacement');
check(ship.Snapshot().locationMask===2&&ship.Snapshot().locationIndex===1&&right.Snapshot().locationIndex===2,'ship is between useful left unit and right Greatsword');
check(left.Snapshot().power.basePower===leftBase+1,'ship really strengthens the left unit');
check(right.Snapshot().power.currentPower===rightPower-1,'ship really wounds its Greatsword neighbour');
globalThis.report={checks,preset:96,removed:201773,added:152109,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(ctx.report,null,2));
