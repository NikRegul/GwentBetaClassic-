// Fringilla uses any weak left neighbour; a weak spy can prepare that pair.
// Draig Bon-Dhu strengthens the bronze soldier a Priestess of Freya will raise.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clearHand(g,side){g.live.filter(c=>c.cardState.positionPlayerId===side&&c.cardState.locationMask===8).forEach(c=>c.Move(side,512,0));}
function resolve(g){for(let n=0;n<8&&g.IsPending()&&!g.IsFatal();n++){if(!g.OpponentStep())break;}}
// No Emissary is required: use ordinary units, other spies and modified live power.
for(const weakId of [112101,142316,162307]){
 const g=fixture();clearHand(g,2);add(g,weakId,1,0,1,2);const strong=add(g,112101,1,1,1,16);
 add(g,112101,2,0,2,12);const fringilla=add(g,162205,8);add(g,112101,8,1,2,3);
 check(g.OpponentStep()&&!g.IsFatal(),'AI acts on an ordinary weak neighbour '+weakId);resolve(g);
 check(fringilla.Snapshot().positionPlayerId===1&&fringilla.Snapshot().locationIndex===1&&strong.Snapshot().power.currentPower===2,'AI uses any weak left unit without an Emissary '+weakId);
}
for(const weakId of [112101,142316,162307,162314])for(const actor of [1,2]){
 const g=fixture(actor);clearHand(g,actor);const enemy=3-actor;
 const weak=add(g,weakId,1,0,enemy,2),strong=add(g,112101,1,1,enemy,16);
 const fringilla=add(g,162205,8,0,actor),row={v:0},index={v:0},gain={v:0};
 check(g.AiFringillaSlot(actor,row,index,gain)&&row.v===1&&index.v===1&&gain.v===14,'any weak neighbour supplies Fringilla '+weakId+'/'+actor);
 check(g.PlayBefore(actor,fringilla.Snapshot().instanceId,strong.Snapshot().instanceId),'Fringilla fits the ordered pair '+weakId+'/'+actor);
 if(actor===1)resolve(g);
 check(strong.Snapshot().power.currentPower===2&&weak.Snapshot().power.currentPower===2,'copies actual weak power without changing left neighbour '+weakId+'/'+actor);
}
{
 const g=fixture();clearHand(g,2);add(g,112101,1,0,1,16);add(g,142316,1,1,1,2);
 const row={v:0},index={v:0},gain={v:0};g.AiFringillaSlot(2,row,index,gain);
 check(gain.v===0,'strong-left weak-right pair is never treated as a useful reduction');
}
{
 const g=fixture();clearHand(g,2);
 const strong=add(g,112101,1,0,1,12);add(g,112101,2,0,1,3);
 for(let i=0;i<3;i++)add(g,112101,16,i,2,4);
 const emissary=add(g,162314,8,0,2),fringilla=add(g,162205,8,1,2);add(g,112101,8,2,2,3);
 check(g.OpponentStep()&&!g.IsFatal(),'AI acts with Emissary and Fringilla in hand');resolve(g);
 const e=emissary.Snapshot(),s=strong.Snapshot();
 check(e.positionPlayerId===1&&e.locationMask===s.locationMask&&e.locationIndex===s.locationIndex-1,'Emissary lands directly left of the strongest enemy unit');
 check(fringilla.Snapshot().locationMask===8,'Fringilla waits for the next turn');
 g.match.currentPlayerId=2;g.match.turnActive=true;
 check(g.OpponentStep()&&!g.IsFatal(),'AI follows up');resolve(g);
 check((fringilla.Snapshot().locationMask&7)!==0,'Fringilla is played between them');
 check(strong.Snapshot().power.currentPower<=4,'strongest enemy unit drops to the spy power');
}
{
 const g=fixture();clearHand(g,2);add(g,112101,1,0,1,6);
 const soldiers=[];for(const id of [152303,152303])soldiers.push(add(g,id,32,soldiers.length,2));
 const draig=add(g,152205,8,0,2),priestess=add(g,152310,8,1,2);add(g,112101,8,2,2,4);
 check(g.archetypeAI!==undefined,'archetype AI present');
 check(g.OpponentStep()&&!g.IsFatal(),'AI acts with Draig and a Priestess');resolve(g);
 check((draig.Snapshot().locationMask&7)!==0,'Draig is played before the Priestess');
 check(priestess.Snapshot().locationMask===8,'Priestess waits');
 check(soldiers.every(c=>{const p=c.Snapshot().power;return p.basePower+p.permanentPower>=15;}),'both grave soldiers are strengthened by 3');
 g.match.currentPlayerId=2;g.match.turnActive=true;
 check(g.OpponentStep()&&!g.IsFatal(),'AI follows Draig with resurrection');resolve(g);
 check((priestess.Snapshot().locationMask&7)!==0&&soldiers.some(c=>{const s=c.Snapshot();return (s.locationMask&7)!==0&&s.power.basePower+s.power.permanentPower>=15;}),'Priestess raises a strengthened soldier (before its self-damage)');
}
{
 const g=fixture();clearHand(g,2);for(let i=0;i<3;i++)add(g,142316,1,i,1,[1,12,15][i]);
 add(g,112101,2,0,2,5);const sabrina=add(g,122206,8);add(g,113301,8,1);
 check(g.AiSpyActivationValue(sabrina)>0,'Sabrina has a profitable actual killing plan with a weak row neighbour');
 check(g.OpponentStep()&&!g.IsFatal(),'AI deploys prepared Sabrina');resolve(g);
 check(sabrina.Snapshot().positionPlayerId===1&&sabrina.Snapshot().locationMask===1,'Sabrina goes to the row containing the weak unit');
 g.match.currentPlayerId=2;g.match.turnActive=true;
 check(g.OpponentStep()&&!g.IsFatal(),'AI activates Sabrina');resolve(g);
 check(sabrina.Snapshot().locationMask===32&&g.Score(1)===3,'Sabrina is killed and the three row units actually become weak');
}
{
 const g=fixture();clearHand(g,2);for(let i=0;i<3;i++)add(g,142316,1,i,1,[1,12,15][i]);
 const sabrina=add(g,122206,8);
 check(g.AiSpyActivationValue(sabrina)===-2147483647,'weak neighbour alone does not justify Sabrina without an activation');
}
globalThis.comboReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'combo127.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.comboReport,null,2)+'\n');
