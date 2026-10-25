/* AIPersonality.<field>Inherited getters and IsInherited, source-derived.
 * FlattenInheritedValues: child entries keep their order, then unshadowed
 * ancestors are appended from oldest to nearest, as in the original loops. */
'use strict';
const defaults=require('./data/profile-scalars.json').fields;
const original=require('./data/personalities.json');
function scalarSettings(name,profiles=original){
 const result={};
 for(const key of Object.keys(defaults)){
  let current=name;const seen=new Set();
  while(true){
   if(seen.has(current))throw Error('Cyclic Beta personality inheritance: '+current);
   seen.add(current);const p=profiles[current];if(!p)throw Error('Missing Beta personality: '+current);
   // Original IsInherited inserts true for an absent attribute. Parentless
   // records always use their own value regardless of the stored flag.
   if(p.parent&&(p.inherited[key]===undefined||p.inherited[key]===true)){current=p.parent;continue;}
   let value=p.values[key]===undefined?defaults[key].default:p.values[key];
   if(defaults[key].type==='float')value=Math.fround(value);
   result[key]=value;break;
  }
 }
 return result;
}
function chainFor(name,profiles){
 const chain=[],seen=new Set();
 while(name){
  if(seen.has(name))throw Error('Cyclic Beta personality inheritance: '+name);
  seen.add(name);const p=profiles[name];if(!p)throw Error('Missing Beta personality: '+name);
  chain.push(p);name=p.parent;
 }
 return chain;
}
function cloneRecord(v){
 if(Array.isArray(v))return v.map(cloneRecord);
 if(v!==null&&typeof v==='object'){const c={};for(const key of Object.keys(v))c[key]=cloneRecord(v[key]);return c;}
 return v;
}
function flattenList(chain,read,key){
 const result=read(chain[0]).map(cloneRecord);
 for(let i=chain.length-1;i>0;i--)for(const item of read(chain[i])){
  const id=key(item);let shadowed=result.some(x=>key(x)===id);
  for(let j=i-1;j>0&&!shadowed;j--)shadowed=read(chain[j]).some(x=>key(x)===id);
  if(!shadowed)result.push(cloneRecord(item));
 }
 return result;
}
function personality(name,profiles=original){
 const chain=chainFor(name,profiles),associations={};
 const types=['PlayCardAssociations','CardTargetsAssociations','CardChoicesAssociations','LocationTargetsAssociations'];
 for(const type of types)associations[type]=flattenList(chain,p=>p.associations?.[type]||[],a=>
  String(Number(a.attributes.TemplateId))+':'+String(Number(a.attributes.AIHIntId===undefined?1:a.attributes.AIHIntId)));
 const semanticTags=flattenList(chain,p=>p.semanticTags||[],t=>t.id);
 for(const t of semanticTags)t.weight=Math.fround(t.weight);
 return {...scalarSettings(name,profiles),name,semanticTags,associations};
}
module.exports={scalarSettings,personality,scalarSchema:defaults};
