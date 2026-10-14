// 0.6.2: a spying False Ciri returns to the side that played her when the
// player she spies for passes. Exact simulations and Fringilla placement
// must count her as that side's deferred points, not as damage to the opponent.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clearHand(g,side){g.live.filter(c=>c.cardState.positionPlayerId===side&&c.cardState.locationMask===8).forEach(c=>c.Move(side,512,0));}
function spy(c){c.cardState.tokenMask|=128;return c;}
{ // Projection: her power counts for the AI until the enemy passes.
 const g=fixture();clearHand(g,2);clearHand(g,1);
 add(g,112101,1,0,2,10);add(g,112101,1,0,1,12);const ciri=spy(add(g,162212,1,1,1,9));
 const raw=g.Score(2)-g.Score(1);
 check(g.AiProjectedLead()===raw+18,'returning False Ciri is a deferred swing of twice her power');
 check(g.AiReturningSpy(ciri.Snapshot(),2)&&!g.AiReturningSpy(ciri.Snapshot(),1),'returning spy recognised for its owner only');
 g.match.playerOne.hasPassed=true;
 check(g.AiProjectedLead()===raw&&!g.AiReturningSpy(ciri.Snapshot(),2),'after the enemy pass nothing more is deferred');
}
{ // Fringilla never lowers a returning False Ciri when another pair exists.
 const g=fixture();clearHand(g,2);clearHand(g,1);
 add(g,112101,1,0,1,2);spy(add(g,162212,1,1,1,9));add(g,112101,1,2,1,3);add(g,112101,1,3,1,10);
 const row={v:0},index={v:0},gain={v:0};
 g.AiFringillaSlot(2,row,index,gain);
 check(row.v===1&&index.v===3&&gain.v===7,'Fringilla copies 3 onto 10, not 2 onto her own returning spy (index '+index.v+', gain '+gain.v+')');
}
{ // Exact play value of a spy placement that would shrink her is negative.
 const g=fixture();clearHand(g,2);clearHand(g,1);
 add(g,112101,1,0,1,2);const ciri=spy(add(g,162212,1,1,1,9));
 const before=g.AiProjectedLead();ciri.power.SetCurrentPair(2,0);
 check(g.AiProjectedLead()-before===-7,'shrinking her costs the AI her lost power');
}
{ // Reproduce round two, 32:76, AI with no crown. Run the actual Fringilla
  // deploy and queued Mangonel response, rather than changing power by hand.
 const g=fixture();clearHand(g,2);clearHand(g,1);g.match.roundNumber=2;
 g.match.playerOne.crowns=1;g.match.playerTwo.crowns=0;
 add(g,112101,1,0,1,2);const ciri=spy(add(g,162212,1,1,1,9));
 const enemy=add(g,112101,1,2,1,21),mangonel=add(g,162308,1,0,2,4);
 add(g,112101,2,0,2,72);
 const fringilla=add(g,162205,8,0,2);mangonel.nilfCounter=1;
 check(g.Score(1)===32&&g.Score(2)===76,'reported round-two score reproduced');
 check(g.Play(2,fringilla.cardState.instanceId,1),'AI resolves Fringilla and Mangonel');
 check(alive(ciri)&&ciri.power.currentPower>=9,'returning False Ciri is not shrunk or killed');
 check(alive(fringilla),'Fringilla survives without triggering False Ciri deathwish');
 check(!g.IsFatal()&&!g.IsPending(),'Fringilla reaction chain completes');
}
for(const token of [4,8]){ // Locked or face-down Ciri cannot trigger her return.
 const g=fixture();clearHand(g,2);clearHand(g,1);
 const ciri=spy(add(g,162212,1,0,1,9));ciri.cardState.tokenMask|=token;
 check(g.AiProjectedLead()===g.Score(2)-g.Score(1),'inactive Ciri has no projected return '+token);
 check(!g.AiReturningSpy(ciri.Snapshot(),2),'inactive Ciri is an ordinary enemy target '+token);
}
{ // The projection must match the real pass-triggered relocation.
 const g=fixture(1);const ciri=spy(add(g,162212,1,0,1,9));
 const projected=g.AiProjectedLead();check(g.Pass(1),'player passes with False Ciri on their side');
 check(ciri.cardState.positionPlayerId===2,'False Ciri actually returns to the AI');
 check(g.Score(2)-g.Score(1)===projected,'projection equals the resolved pass score');
}
globalThis.report={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'ciri062.bundle.js',timeout:120000});
console.log('PASS: '+context.report.checks+' False Ciri return regressions');
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
