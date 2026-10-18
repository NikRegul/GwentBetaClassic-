'use strict';
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),build=path.resolve(root,process.argv[2]||'BetaGwent/build/release082-rc3-ready');
let checks=0;const codes=['','ru_ru','en_us','de_de','fr_fr','it_it','pl_pl','es_es','es_mx','pt_br','jp_jp','kr_kr','zh_cn','zh_tw'];
function fn(s,name){const a=s.indexOf('function '+name+'('),b=s.indexOf('{',a);let d=1,i=b+1;for(;d;i++){if(s[i]==='{')d++;if(s[i]==='}')d--;}return s.slice(a,i).replace(/:(?:String|Object|void|int|uint|Number|Array|Boolean|TextField)\b(?=\s*[,)=;{])/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');}
for(const platform of ['nextgen','classic']){
 const s=fs.readFileSync(path.join(build,platform,'ui/src/BetaGwentExchangeText082.as'),'utf8');
 const KEYS=JSON.parse(s.match(/KEYS:Array=(.*);/)[1]),VALUES=JSON.parse(s.match(/VALUES:Array=(.*);/)[1]);
 const c=vm.createContext({KEYS,VALUES});vm.runInContext(fn(s,'extend'),c);
 for(let language=1;language<=13;language++){
  const table=c.extend(language,{});assert(KEYS.every((key,i)=>table[key]===VALUES[language][i]&&table[key.toUpperCase()]===VALUES[language][i].toUpperCase()));checks++;
  if(language>1){assert(KEYS.every(key=>!/[А-Яа-яЁё]/.test(table[key])));checks++;}
  const folder=['jp_jp','kr_kr','zh_cn','zh_tw'].includes(codes[language])?'BetaGwent/build/release082-rc3/exchange-fonts':'BetaGwent/build/text138';
  const fontSource=fs.readFileSync(path.join(root,folder,codes[language],'BetaLocale137.as'),'utf8');
  const encoded=fontSource.slice(fontSource.indexOf('public var characters:String=')+29);const characters=JSON.parse(encoded.slice(0,encoded.indexOf('";')+1));
  assert([...VALUES[language].join('')].every(ch=>characters.includes(ch)),codes[language]+' glyphs');checks++;
 }
}
const report={checks,languages:13,allExchangeStringsLocalized:true,allRequiredGlyphsEmbedded:true};fs.writeFileSync(path.join(build,'exchange-language-tests.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
