'use strict';
const fs=require('fs'),vm=require('vm'),path=require('path'),crypto=require('crypto');
process.env.ROOT=path.resolve(__dirname,'../..');const H=require('./preview_screens096/harness.cjs'),c=H.ctx;
const file=process.argv[2]||process.env.ROOT+'/BetaGwent/ui/src/BetaGwentBoard.as',as=fs.readFileSync(file,'utf8');
const menu=fs.readFileSync('BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws','utf8');
const name='OnBetaGwentPresentation100',start=menu.indexOf('event '+name+'('),open=menu.indexOf('{',start);let end=open+1,depth=1;
while(depth){depth+=(menu[end]==='{')-(menu[end]==='}');end++;}
const code=menu.slice(start,end).replace(/^event /,'function ').replace(/:\s*(int|bool|W3PlayerWitcher)\b/g,'').replace(/\(W3PlayerWitcher\)/g,'');
let checks=0;const failures=[],check=(v,n)=>{checks++;if(!v)failures.push(n);};
const p={tempo:10,reduced:false,BetaGwentSetPresentation(t,r){this.tempo=t;this.reduced=r;return true;}};
Object.assign(c,{thePlayer:p,configured:true,presentationTempo:10,presentationReduced:false,LogChannel(){},
 animationTempo:1,reducedMotion:false,soundEnabled:true,voiceEnabled:true,playing:false,controllerMenuOpen:false,
 tempoLabel:null,motionLabel:null,clearLeaderMovies(){},render(){},closeControllerMenu(){},openControllerMenu(){}});
vm.runInContext(code+'\n'+['cycleTempo','toggleMotion','setAudioStatus'].map(n=>H.extract(n,as)).join('\n'),c);
const sent=[];c.send=(name,args)=>{sent.push({name,args});if(typeof c[name]==='function')c[name](...args);};
for(const expected of [15,20,10]){
 c.cycleTempo();check(sent.at(-1).name==='OnBetaGwentPresentation100'&&sent.at(-1).args.length===2,'tempo uses exact two-argument event '+expected);
 check(p.tempo===expected&&c.presentationTempo===expected,'menu and profile receive tempo '+expected);
 c.setAudioStatus(true,true,c.presentationTempo,c.presentationReduced);check(c.animationTempo===expected/10,'audio tick does not reset selected tempo '+expected);
}
for(const reduced of [true,false]){
 c.toggleMotion();check(p.reduced===reduced&&c.presentationReduced===reduced,'effect mode reaches menu and profile '+reduced);
 c.animationTempo=1;c.reducedMotion=!reduced;c.setAudioStatus(true,true,p.tempo,p.reduced);
 check(c.reducedMotion===reduced,'next menu restores effect mode '+reduced);
}
const before=[p.tempo,p.reduced];check(!c.OnBetaGwentPresentation100(12,true)&&p.tempo===before[0]&&p.reduced===before[1],'invalid tempo leaves preferences intact');
c.configured=false;check(!c.OnBetaGwentPresentation100(20,true)&&p.tempo===before[0],'unconfigured menu cannot change preferences');
const report={checks,failures,sourceSha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),actualActionScript:true,actualWitcherScript:true,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;
