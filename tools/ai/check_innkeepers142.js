// Execute the production stock migration with native inventory/NPC stubs.
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync('BetaGwent/development/scripts/game/betagwent/shopRuntime.ws','utf8');
const body=source.slice(source.indexOf('function OnConfigUI()'),source.indexOf('@wrapMethod(CR4InventoryMenu)',source.indexOf('function OnConfigUI()')))
 .replace(/:\s*array<\w+>/g,'')
 .replace(/:\s*(?:IScriptable|W3InventoryInitData|CNewNPC|CInventoryComponent|W3PlayerWitcher|W3MerchantComponent|int)\b/g,'')
 .replace(/\((W3InventoryInitData|CNewNPC|W3PlayerWitcher|W3MerchantComponent)\)/g,'')
 .replace(/items\.Size\(\)/g,'items.length').replace(/current\.Size\(\)/g,'current.length');
const c=vm.createContext({console});
vm.runInContext(`var npc,thePlayer={BetaGwentEnsureCollection(){return true;}},wrapped=0;
function GetMenuInitData(){return {containerNPC:npc};}function wrappedMethod(){wrapped++;}function LogChannel(){}
function BetaGwentLegacyShopCard(){return 0;}function BetaGwentShopCard(){return 0;}
`+body,c);
let checks=0;function check(v,n){assert(v,n);checks++;}
function merchant(kind,stock=0,tag=true){const inventory={count:stock,adds:0,UpdateLoot(){},GetAllItems(a){},GetItemQuantityByName(){return this.count;},AddAnItem(name,n){assert(name==='betagwent_keg');this.count+=n;this.adds+=n;}};
 return {inventory,HasTag(){return tag;},GetComponentByClassName(){return kind?{GetMapPinType(){return kind;}}:null;},GetInventory(){return inventory;},GetGuidHash(){return 42;}};}
// GetAllItems fills output arrays in the real engine; initialise these WS defaults.
const patched=body.replace('data=GetMenuInitData();','items=[];current=[];data=GetMenuInitData();');vm.runInContext(patched,c);
for(const tag of [false,true])for(const old of [0,1,3,5,9]){
 c.npc=merchant('Innkeeper',old,tag);c.OnConfigUI();check(c.npc.inventory.count===Math.max(5,old),'all innkeepers receive stock, even without Merchant tag');
 c.OnConfigUI();check(c.npc.inventory.count===Math.max(5,old),'reopening does not duplicate stock');
 c.npc.inventory.count=0;c.OnConfigUI();check(c.npc.inventory.count===0,'sold-out shop is not refilled by reopening');
}
for(const kind of ['Blacksmith','Armorer','Shopkeeper',null]){
 c.npc=merchant(kind);c.OnConfigUI();check(c.npc.inventory.count===0,'non-innkeeper without existing kegs is untouched '+kind);
}
c.npc=merchant('Shopkeeper',1);c.OnConfigUI();check(c.npc.inventory.count===5,'old keg merchant retains the existing bulk migration');
const report={stage:142,checks,actualWitcherScriptBody:true,nativeGameTested:false};
const output=process.argv[3]||process.argv[2];
if(output)fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
