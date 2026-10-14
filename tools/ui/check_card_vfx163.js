'use strict';
// Compare the actual generated AS routing with every original card graph and
// preserve the special-card routing from the verified 0.6.10 build.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const evidence=read('docs/evidence/card-vfx163.json');
const catalog=read('data/beta924/normalized/catalog.json');
const previous=read('docs/evidence/special-vfx142.json');
const raw=fs.readFileSync(path.join(root,'BetaGwent/ui/src/BetaGwentSpecialVfx.as'),'utf8');
const bindings=JSON.parse(/BINDINGS:Object=(\{[^\n]+\});/.exec(raw)[1]);
const body=/public static function profile\(id:int,hurting:Boolean\):Object\s*\{([\s\S]*?)\n        \}/.exec(raw)[1]
 .replace(/var (\w+):(Array|Object|int|Boolean)/g,'var $1')
 .replace(/for each\(var (\w+) in ([^)]+)\)/g,'for(var $1 of $2)');
const context={BINDINGS:bindings,int:Number,String};vm.createContext(context);
vm.runInContext('function profile(id,hurting){'+body+'}',context);
let checks=0;
function check(v,label){assert(v,label);checks++;}
function powers(c){return c.effects.filter(e=>e.node==='ChangePowerNode'&&[0,1].includes(e.fields.Operation)&&e.elementName);}
check(evidence.templateCount===catalog.templates.length,'every original template inventoried');
check(new Set(evidence.cards.map(c=>c.templateId)).size===catalog.templates.length,'no duplicate templates');
check(evidence.cards.filter(c=>c.collectible).length===479,'479 collectibles covered');
check(evidence.cards.filter(c=>c.leader).length===21,'21 leaders covered');
const abilities=new Map(catalog.abilities.filter(a=>a.type==='CardAbility').map(a=>[a.templateId,a]));
for(const card of evidence.cards){
 const nodes=abilities.get(card.templateId)?.nodes||[];
 for(const effect of card.effects){
  const node=nodes.find(n=>n.nodeId===effect.nodeId);check(node&&node.type===effect.node,'original graph node '+card.templateId+':'+effect.nodeId);
  const fields=Object.fromEntries(node.sourceTree.children.map(c=>[c.tag,c.attributes.V]));
  for(const [key,value] of Object.entries(effect.fields))check(Number(fields[key])===value,'original field '+key);
 }
 const power=powers(card);
 check(JSON.stringify(bindings[card.templateId]||[])===JSON.stringify(power.map(e=>[e.fields.ElementType,e.fields.AttackMethod||0,e.fields.Operation])),'AS bindings '+card.templateId);
 for(const hurting of [false,true]){
  const wanted=power.find(e=>e.fields.Operation===(hurting?1:0));
  const actual=context.profile(card.templateId,hurting);
  check(wanted?actual&&actual.element===wanted.fields.ElementType&&actual.method===(wanted.fields.AttackMethod||0):actual===null,'actual AS profile '+card.templateId+':'+hurting);
 }
}
for(const card of previous.specials){
 const expected=powers(card).map(e=>[e.fields.ElementType,e.fields.AttackMethod||0,e.fields.Operation]);
 check(JSON.stringify(bindings[card.templateId]||[])===JSON.stringify(expected),'0.6.10 special mapping preserved '+card.templateId);
}
const audioMap=read('docs/evidence/beta-audio86-vfx-map.json');
for(const card of evidence.cards)for(const effect of card.effects)for(const [prefab,sounds] of Object.entries(effect.sounds)){
 check(JSON.stringify(sounds)===JSON.stringify(audioMap.filter(s=>s.object===prefab)),'original sound binding '+prefab);
}
const folders=['src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder'];
for(const folder of folders)check(fs.readFileSync(path.join(root,'BetaGwent/ui',folder,'BetaGwentSpecialVfx.as'),'utf8')===raw,'source mirror '+folder);
console.log(JSON.stringify({stage:163,checks,templates:evidence.templateCount,collectibles:479,leaders:21,powerBindings:Object.keys(bindings).length,actualActionScript:true,uniquePrefabRenderingComplete:false,nativeGameTested:false}));
