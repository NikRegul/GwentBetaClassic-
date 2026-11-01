'use strict';
// Execute the actual drawing methods. Expected validity comes from the beta
// DeckValidatorResult / DefaultDeckValidatorRuleSet, not the renderer's formula.
const fs=require('fs'),vm=require('vm'),path=require('path');
const file=process.argv[2]||'BetaGwent/ui/src/BetaGwentBoard.as';
const raw=fs.readFileSync(file),source=(raw[0]===255&&raw[1]===254?raw.subarray(2).toString('utf16le'):raw.toString('utf8'));
const start=source.indexOf('function betaStatsWidget(');if(start<0)throw Error('Missing actual widget');
let open=source.indexOf('{',start),end=open+1,depth=1;while(depth){depth+=(source[end]==='{')-(source[end]==='}');end++;}
const body=source.slice(start,end).replace(/:\s*(?:int|uint|Number|Array|void)(?=\s*[,);={])/g,'');
const labels=[],ctx={content:{},BetaGwentDeckArt104:{stats:()=>0,DP_STAT_GOLD:1,DP_STAT_SILVER:2,DP_STAT_BRONZE:3},BetaGwentFonts:{BODY:0},paintArt(){},betaSlotLabel(...args){labels.push({text:args[1],color:args[7]});},betaLabel(...args){labels.push({text:args[1],color:args[6]});}};
vm.createContext(ctx);vm.runInContext(body,ctx);
let checks=0;const failures=[],records=[];function check(ok,label){checks++;if(!ok)failures.push(label);}
const red=0xFF6666;
for(const [g,s,b,t,expected] of [
 [0,0,0,0,[true,true,false]], [4,6,15,25,[true,true,true]],
 [4,6,30,40,[true,true,true]], [4,6,31,41,[true,true,false]],
 [5,5,15,25,[false,true,true]], [3,7,15,25,[true,false,true]],
 [5,7,12,24,[false,false,false]], [0,0,40,40,[true,true,true]]]){
 labels.length=0;ctx.betaStatsWidget(0,g,s,b,t,146);
 check(labels.length===4,'three tier counters plus total');
 const colors=labels.map(x=>x.color);
 check(colors[0]===(expected[0]?0xF6D36B:red),'gold validity '+g+'/'+t);
 check(colors[1]===(expected[1]?0xE6E6E6:red),'silver validity '+s+'/'+t);
 check(colors[2]===0xE0B07A,'bronze total has no tier cap '+b);
 check(colors[3]===(expected[2]?0xF2EEE4:red),'total validity '+t);
 check(labels[0].text===g+'/4'&&labels[1].text===s+'/6'&&labels[2].text===String(b),'counter texts retain actual counts');
 records.push({gold:g,silver:s,bronze:b,total:t,colors});
}
const report={checks,failures,records,actualActionScript:true,source:path.resolve(file),nativeGameplayVerified:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks,failures}));if(failures.length)process.exitCode=1;
