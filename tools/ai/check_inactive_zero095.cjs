'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../../BetaGwent/build-inputs/reference/beta-original-csharp/GwentGameplay/CardPower.cs'),'utf8');
assert(source.includes('CurrentPower == 0 && BasePower + PermanentPower <= 0'));
assert(source.includes('ELocation.Inactive.Contains(card.Position.Location)'));
assert(source.includes('CreateAction<CardBanishAttackAction>().Init(null'));
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const records=[],failures=[];function verify(v,n){checks++;if(!v)failures.push(n);}
for(const side of [1,2])for(const zone of [8,16,32,64,128])for(const kind of ['zero-base','positive-base','boosted-zero-base']){
 const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const card=add(g,112405,zone,0,side);card.power.SetBasePowerAndArmor(2,0);card.power.SetCurrentPair(kind==='boosted-zero-base'?5:2,0);
 const before=card.Snapshot();let killed=0;const kill=card.Kill;card.Kill=function(){killed++;return kill.call(this);};
 if(kind==='positive-base')card.ChangePower(-2,true);else card.ChangeBasePower(-2,true);
 g.FlushEffects();g.FlushDeaths();const s=card.Snapshot(),expected=kind==='zero-base'?512:zone;
 verify(s.locationMask===expected,'inactive strength '+side+'/'+zone+'/'+kind);
 verify(killed===0,'banish uses no Killed/deathwish '+side+'/'+zone+'/'+kind);
 verify(s.instanceId===before.instanceId&&s.ownerId===before.ownerId,'identity preserved');
 verify(!g.IsFatal(),'queue resolves');records.push({side,zone,kind,result:s.locationMask,current:s.power.currentPower,base:s.power.basePower,killed});
}
globalThis.result={checks,records,failures,actualWitcherScript:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks:report.checks,cases:report.records.length,failures:report.failures}));if(report.failures.length)process.exitCode=1;
