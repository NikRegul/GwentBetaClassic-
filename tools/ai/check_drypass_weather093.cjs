'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]);
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInNewContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const rows=[];
for(const strength of [2,3,4])for(const profile of [54,55,57,65,74,91])for(const crowns of [[1,0],[0,1],[1,1]])for(const withBody of [false,true]){
 const g=fixture();Host.strength=strength;g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.presetTwo=profile;g.archetypeAI.Initialize(g,[],profile,201743);g.match.roundNumber=2;g.match.playerOne.crowns=crowns[0];g.match.playerTwo.crowns=crowns[1];
 g.match.playerOne.hasPassed=true;const rag=add(g,113101,8,0),body=withBody?add(g,112405,8,1):null;g.archetypeAI.Refresh();
 const logs=[];Host.log=s=>logs.push(s);let steps=0,ok=false;while(!ok){if(++steps>10000)throw Error('Preparation cap');if(g.AiPreparationStep())ok=g.OpponentStep();}Host.log=null;
 const r={strength,profile,crowns,weather:rag.Snapshot().locationMask,body:body?.Snapshot().locationMask,passed:g.match.playerTwo.hasPassed,selected:logs.filter(s=>s.includes('event=SELECT')||s.includes('event=REJECT')||s.includes('event=PASS'))};rows.push(r);
 if(!ok||g.IsFatal()||rag.Snapshot().locationMask!=8)throw Error('Rag nar Roog wasted after empty pass: '+JSON.stringify(r));
}
console.log(JSON.stringify({cases:rows.length,errors:0,rows}));`,{console});
