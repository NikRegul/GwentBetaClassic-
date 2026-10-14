// Execute the actual new-hint dictionary extension for isolated AS tests.
const fs=require('fs'),vm=require('vm');
module.exports=function(){
 const source=fs.readFileSync('BetaGwent/ui/src/BetaGwentUiText142.as','utf8');
 const dictionary=JSON.parse(source.match(/const EN:Object=(\{[\s\S]*?\n        \});/)[1]);
 const start=source.indexOf('function extend('),open=source.indexOf('{',start);let end=open+1,depth=1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 const code=source.slice(start,end).replace(/:(int|String|Object)\b/g,'');
 const context=vm.createContext({EN:dictionary,String});vm.runInContext(code,context);
 return {extend:context.extend};
};
