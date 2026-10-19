'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.resolve(__dirname,'../..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const board=read('BetaGwent/ui/src/BetaGwentBoard.as'),status=read('BetaGwent/ui/src/BetaGwentStatus191.as');
const proof=JSON.parse(read('docs/evidence/status-source191.json')),recipes=JSON.parse(read('BetaGwent/ui/assets/elements164/recipes.json'));
const generated=read('BetaGwent/ui/src/BetaGwentStatusData191.as');
const tableContext=vm.createContext({});
vm.runInContext('var cache={};'+generated.replace(/^.*?private static var cache:Object=\{\};/s,'').replace(/\s*}\s*}\s*$/,'').replace(/(?:public|private) static function/g,'function').replace(/:(?:String|Object)\b/g,''),tableContext);
for(const [key,table] of Object.entries(proof.tables)){
 const at=key.lastIndexOf('_');const actual=tableContext.clip(key.slice(0,at),key.slice(at+1));
 assert.deepStrictEqual(JSON.parse(JSON.stringify(actual)),table,'lazy compiled status table equals extracted samples '+key);
 assert.strictEqual(actual,tableContext.clip(key.slice(0,at),key.slice(at+1)),'clip is cached');
}
function extract(src,name){const start=src.indexOf('function '+name+'('),open=src.indexOf('{',start);assert(start>=0,name);let end=open+1,d=1;while(d){if(src[end]==='{')d++;if(src[end]==='}')d--;end++;}return src.slice(start,end).replace(/:(?:Sprite|String|Object|void|int|uint|Number|Array|Boolean|BetaGwentElement164)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))');}
let checks=0;const check=(v,n)=>{assert(v,n);checks++;};
const c=vm.createContext({Math,Object,Array,String,int:v=>v|0,Number,reducedMotion:false,activeCue:{kind:8},
 BetaGwentStatusData191:{clip:(n,p)=>proof.tables[n+'_'+p]},cueImpactTime:()=>180,
 presentationDuration178:n=>recipes.presets[n]?recipes.presets[n].duration*1000:0});
vm.runInContext(['statusVisible191','statusPhase191','statusFloor191','timerTick191'].map(n=>extract(board,n)).join('\n'),c);
const card=(tokens=0,zone=1)=>({id:7,templateId:132308,tokens,zone,side:1,timer:3,armor:2});
for(const [name,bit,zone] of [['ResilienceToken',1,1],['SpyingToken',128,1],['RevealToken',64,8]]){
 const a=card(0,zone),b=card(bit,zone);
 check(c.statusPhase191(a,b,name)==='show',name+' acquisition');
 check(c.statusPhase191(b,a,name)==='hide',name+' removal');
 check(c.statusPhase191(b,b,name)==='',name+' repaint never restarts');
 check(c.statusPhase191(null,b,name)==='',name+' loading never replays');
 check(!c.statusVisible191(card(bit|8,1),name),name+' concealed card remains concealed');
 c.activeCue={kind:8};check(c.statusFloor191(c.activeCue,[a],[b])>=proof.tables[name+'_show'].ms+180,name+' playback includes the original clip');
 check(c.statusFloor191(c.activeCue,[b],[a])>=proof.tables[name+'_hide'].ms+180,name+' removal is not truncated');
 c.reducedMotion=true;check(c.statusPhase191(a,b,name)===''&&c.statusFloor191(c.activeCue,[a],[b])===0,name+' reduced motion');c.reducedMotion=false;
}
check(c.statusPhase191(card(128),card(4),'SpyingToken')==='hide','locking clears the dynamic spy marker');
check(c.statusPhase191(card(),card(128),'SpyingToken')==='show','non-spy template charmed onto the opposite side gains the marker');
check(!c.statusVisible191(card(2),'SpyingToken'),'bit 2 is not the spying instance flag');
check(c.statusPhase191(card(64,8),card(0,1),'RevealToken')==='','playing a revealed card removes hand badge without a separate reveal event');
check(c.statusPhase191(card(64,8),{...card(0,8),templateId:0},'RevealToken')==='hide','sanitizing a newly hidden enemy card does not suppress badge removal');
for(const name of ['ResilienceToken','SpyingToken','RevealToken'])check(!c.statusVisible191({...card(1|128,8),side:2},name),'closed enemy hand never exposes a status '+name);
check(c.statusVisible191({...card(1|64,8),side:2},'ResilienceToken'),'publicly revealed enemy card may show its resilience');
const draws=[];Object.assign(c,{drawStatus191:(parent,name,w,h,phase)=>draws.push({name,phase}),drawElement164:()=>{},statusBudget191:{remaining:600}});
vm.runInContext(extract(board,'drawCardStatuses191'),c);
c.drawCardStatuses191({},card(0,8),{...card(1,8),side:2},80,112);check(draws.length===0,'production handler draws no badge or effect on hidden enemy card');
check(c.statusFloor191({kind:0},[card()],[card(1)])===0,'no cue has no pause');
check(c.statusFloor191({kind:8,massFollow:true},[card()],[card(1)])===0,'merged follower has no extra pause');
check(c.statusFloor191({kind:8},[card()],[{...card(1),zone:32}])===0,'departed cards have no status pause');
for(const [after,expected,why] of [[{timer:2},true,'decrement'],[{timer:0},true,'expiry'],[{timer:4},false,'reset'],[{timer:-1},false,'removed timer'],[{timer:2,tokens:4},false,'lock'],[{timer:2,tokens:8},false,'ambush'],[{timer:2,zone:32},false,'grave']])check(!!c.timerTick191(card(),{...card(),...after},{kind:8})===expected,'timer '+why);
check(recipes.presets.CardTimerVFX.emitters.every(e=>e.id!==3044),'dynamic timer numeral never uses a baked default zero');
for(const id of [3052,3287,3283]){
 const emitter=recipes.presets.ArmorDecrease.emitters.find(e=>e.id===id);
 check(emitter&&emitter.births.length===1&&emitter.maxParticles===1,'each source shield fragment is emitted once '+id);
}
for(const name of ['ResilienceTokenShow','SpyingTokenShow','RevealTokenShow','ArmorIncrease','ArmorDecrease'])check(recipes.presets[name].emitters.length>0,'original status/armor recipe contains live particles '+name);
for(const [oldArmor,newArmor] of [[0,2],[2,4],[4,0]])check(c.statusFloor191({kind:2},[{...card(),armor:oldArmor}],[{...card(),armor:newArmor}])>=180+c.presentationDuration178(newArmor>oldArmor?'ArmorIncrease':'ArmorDecrease'),'armour effect has time to complete');
check(c.statusFloor191({kind:2},[{...card(),armor:4}],[{...card(),armor:2}])===0,'partial armour damage does not shatter shield');
const strengths=[];Object.assign(c,{uint:v=>v>>>0,revision:1,animations:[],activeCue:{kind:8,source:1},BetaGwentElementData164:{preset:n=>recipes.presets[n]},BetaGwentElement164:function(...a){strengths.push(a[8]);this.durationMs=400;this.particleCount=4;}});c.BetaGwentElement164.MAX_UNITS=55;
vm.runInContext(extract(board,'drawElement164'),c);
for(const strength of [1,.55,.25]){c.drawElement164({addChild(){}},'ArmorIncrease',0,0,80,112,180,{remaining:600},48,0,0,0,0,false,strength);check(strengths.at(-1)===strength,'production particles respect brightness '+strength);}
for(const strength of [1,.55]){c.drawElement164({addChild(){}},'PowerDirectLightMagic',0,0,80,112,180,{remaining:600},48,0,0,0,0,true,strength);check(strengths.at(-1)===.45*strength,'accepted soft boost strength is preserved '+strength);}
vm.runInContext(extract(status,'sample')+'\n'+extract(status,'render'),c);
for(const [key,clip] of Object.entries(proof.tables)){
 c.clip=clip;c.unit=80/22;c.hiding=key.endsWith('_hide');c.parts=Object.keys(clip.parts).map(k=>({key:k,x:10,y:20,sprite:{}}));
 for(const progress of [0,.1,.3,.5,.8,1]){c.render(progress);for(const part of c.parts){const s=part.sprite;check([s.scaleX,s.scaleY,s.x,s.y,s.alpha].every(Number.isFinite),'source curve finite '+key);check(s.scaleX>=0&&s.scaleY>=0&&s.alpha>=0&&s.alpha<=1,'source curve bounds '+key);}}
 if(c.hiding)check(c.parts.every(p=>p.sprite.visible===false),'removed status leaves no persistent badge '+key);
 else check(c.parts.every(p=>Math.abs(p.sprite.scaleX-1)<.0001&&Math.abs(p.sprite.scaleY-1)<.0001),'show converges to the static layout '+key);
}
check(!extract(board,'drawArmorHit').includes('var shard'),'zero armour uses source fragments, not three duplicated full shields');
check(board.includes('drawCardStatuses191(p,before,c,cardWidth,cardHeight)'),'board uses instance status transitions');
check(board.includes('pendingImpacts.push({field:timerField191'),'timer numeral changes at the same impact as the tick');
check(board.includes('statusFloor191(timed.cue,priorCards,timed.cards)'),'replay uses source status durations');
for(const folder of ['src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder'])for(const file of ['BetaGwentBoard.as','BetaGwentStatus191.as','BetaGwentStatusData191.as']){
 const raw=fs.readFileSync(path.join(root,'BetaGwent/ui/src',file));check(raw.equals(fs.readFileSync(path.join(root,'BetaGwent/ui',folder,file))),'mirrored '+folder+'/'+file);check(raw.subarray(0,3).equals(Buffer.from([239,187,191]))&&!raw.toString('utf8').replace(/\r\n/g,'').includes('\n'),'BOM/CRLF '+file);
}
console.log(JSON.stringify({stage:191,checks,actualActionScript:true,sourceClips:9,nativeGameTested:false}));
