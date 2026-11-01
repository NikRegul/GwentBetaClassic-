'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../..'),folders=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'];
const files=[...folders.map(n=>path.join(root,'BetaGwent/ui',n,'BetaGwentBoard.as')),path.join(root,'tools/features091/BetaGwentBoard_classic093.as')];
let checks=0;
for(const file of files){
 const raw=fs.readFileSync(file),s=raw.toString('utf8');
 assert(raw.subarray(0,3).equals(Buffer.from([239,187,191]))&&!s.replaceAll('\r\n','').includes('\n'));checks++;
 const method=/private function canceledPlacementDeparture101\(previous:Object\):Boolean\s*\{([^}]+)\}/.exec(s);assert(method);checks++;
 assert(s.includes('tentative099:int(c.id)==tentativePlay099')&&s.includes('if(canceledPlacementDeparture101(previous))continue;'));checks++;
 const fn=new vm.Script('(function(previous){'+method[1]+'})').runInNewContext({activeCue:null,int:Number});
 assert(fn({tentative099:true})&&!fn({tentative099:false}));checks++;
 for(const kind of [1,2,3,4,11,12]){
  const real=new vm.Script('(function(previous){'+method[1]+'})').runInNewContext({activeCue:{kind},int:Number});
  assert(!real({tentative099:true}),'real departure/commit must retain its animation');checks++;
 }
}
assert.equal(new Set(files.slice(0,5).map(f=>fs.readFileSync(f).toString('base64'))).size,1);checks++;
console.log(JSON.stringify({checks,files:files.length,nativeGameTested:false}));
