"""Exercise production WS exchange/acquisition/shop code with host API shims."""
from pathlib import Path
import sys,json,subprocess,re
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'))
import ws2js,build_js
DEV=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'BetaGwent/development/scripts/game/betagwent'
OUT=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else ROOT/'BetaGwent/build/features082/tests'
OUT.mkdir(parents=True,exist_ok=True)

def read(name):return (DEV/(name+'.ws')).read_text('utf-8-sig')
def block(source,marker):
    a=source.index(marker);b=source.index('{',a);i=b+1;depth=1
    while depth:
        if source[i]=='{':depth+=1
        elif source[i]=='}':depth-=1
        i+=1
    return source[a:i]
def fn(source,name):return block(source,'function '+name+'(')

deck=read('deckBuilder');collection=read('collectionProfile');scraps=read('scrapsProfile');shop=read('shopRuntime');menu=read('developmentBoardMenu')
probe=OUT/'probe.ws'
source='class CNewNPC extends IScriptable {} class CInventoryComponent extends IScriptable {} class W3MerchantComponent extends IScriptable {}\n'
source+=block(deck,'struct SBetaGwentDeckValidation')+'\n'+fn(deck,'BetaGwentValidateDeck')+'\n'
source+=deck[deck.index('// Public exchange format:'):].split('@addMethod',1)[0]
source+=fn(collection,'BetaGwentCollectionCap')+'\n'
source+='class W3PlayerWitcher extends IScriptable {\npublic var betaGwentCollectionSchema,betaGwentScraps,kegs,backups : int; public var betaGwentOwnedIds,betaGwentOwnedCopies : array<int>;public var pending : bool;\n'
source+='public function BetaGwentEnsureCollection() : bool { return betaGwentCollectionSchema==1 && betaGwentOwnedIds.Size()==betaGwentOwnedCopies.Size(); }\npublic function BetaGwentKegCount() : int {return kegs;} public function BetaGwentAddKegs(count : int) {kegs+=count;}\n'
source+='public function BetaGwentMarkNewCard(id : int) {} public function BetaGwentUpdateCollectionProgress() {} public function BetaGwentSyncTournamentAccess() {} public function BetaGwentBackupProfile(){backups+=1;} public function BetaGwentKegPending() : bool {return pending;}\npublic var betaGwentCollectionSeeding : bool;\n'
for name in ['BetaGwentOwned','BetaGwentGrant','BetaGwentConsoleGrant','BetaGwentConsoleFaction']:source+=fn(collection,name)+'\n'
for name in ['BetaGwentScraps','BetaGwentAddScraps','BetaGwentCanCraft','BetaGwentCraft']:source+=fn(scraps,name)+'\n'
for name in ['BetaGwentExchangeMissing','BetaGwentCraftExchange']:source+=fn(deck,name)+'\n'
source+='}\n'+fn(scraps,'BetaGwentRareBronze')+'\n'+fn(scraps,'BetaGwentCardRarity')+'\n'+fn(scraps,'BetaGwentCraftCost')+'\n'
source+='class CR4InventoryMenu extends IScriptable {\npublic var _shopNpc : CNewNPC; public function ShopUpdateItem(id : int) {} public function UpdateMerchantData() {} public function UpdateItemsCounter() {}\n'+fn(shop,'BetaGwentShopDiagnostic')+'\n}\n'
# Native event guards are exercised, too; only the UI publishers are mocked.
source+='class CR4BetaGwentBoardMenu extends IScriptable {\npublic var configured,selectingDecks,npcMatch,libraryOnly : bool;public var revision,forcedBetaFaction,editorPublishedFaction : int;public var deckDraft : CBetaGwentDeckDraft;public var deckLibrary : CBetaGwentDeckLibrary;public var deckClearHistory : array<int>;\n'
source+='public function PublishCollection() {} public function PublishDeckEditor(message : string) {} public function PublishDeckExchange(code : string, message : string, accepted : bool) {}\n'
source+=block(menu,'event OnBetaGwentDeckImport').replace('event OnBetaGwentDeckImport','function OnBetaGwentDeckImport')+'\n}\n'
source+=menu[menu.index('function BetaGwentConsoleMessage('):]
probe.write_text(source,'utf8')
files=sorted(build_js.CORE.glob('*.ws'))+[DEV/(n+'.ws') for n in build_js.NAMES if (DEV/(n+'.ws')).exists()]+[probe]
code,_=ws2js.build(files,sorted(DEV.glob('*.ws')),excluded_functions={'BetaGwentAITune','BetaGwentAIStrength','BetaGwentAIChooseOrdinaryPreset','BetaGwentAIRandomPreset'})
host=(ROOT/'tools/ai/jshost/runtime.js').read_text('utf8')
tests=r'''
function StrLen(s){return s.length;}function StrMid(s,a,n){return s.substr(a,n);}function StrLeft(s,n){return s.slice(0,n);}function StrFindFirst(s,q){return s.indexOf(q);}function IntToString(n){return String(n);}
function StrLower(s){return s.toLowerCase();}function StrLowerUTF(s){return s.toLowerCase();}
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
function player(){const p=new W3PlayerWitcher();p.betaGwentCollectionSchema=1;return p;}
let compositions=[];
for(let preset=1;preset<=46;preset++){
 const list={v:[]};if(!BetaGwentDuelPresetDeck(preset,list))continue;
 const d=BetaGwentDuelPreset(preset),leader=d.leaderTemplateId,def=BetaGwentDuelDefinition(leader),faction=def.header.factionMask;
 if(!BetaGwentValidateDeck(list.v,faction,leader).valid)continue;
 const before=list.v.join(','),code=BetaGwentExportDeckExchange(list.v,faction,leader),result=BetaGwentParseDeckExchange(code);
 check(result.valid&&result.cards.length===list.v.length&&result.leader===leader&&result.faction===faction,'real preset round trip '+preset);
 check(list.v.join(',')===before,'export never mutates input');
 check(BetaGwentExportDeckExchange([...list.v].reverse(),faction,leader)===code,'canonical code independent of order');
 compositions.push({code,result});
}
check(compositions.length>=30,'real catalog coverage');
const good=compositions[0].code,r=compositions[0].result;
const invalid=['','BG2'+good.slice(3),' '+good,good+' ',good+',',good+':1',good.replace(':', '::'),good.replace('BG1:','BG1:0'),good.replace(/\d+$/,'999999'),good.replace(/\d+$/,'-1'),good.replace(/\d+$/,'1.5'),'BG1:2:132101:','BG1:1:132101:'+r.cards.join(','),'BG1:2:999999:'+r.cards.join(','),good.replace(/\d+$/,'100000000000000000000000000000'),good.replace(/\d+$/,'1e5'),good.replace(/\d+$/,'132102x'),'BG1:2:132101:'+Array(41).fill(132102).join(','),'BG1:2:132101:'+Array(25).fill(132102).join(',')];
for(const bad of invalid)check(!BetaGwentParseDeckExchange(bad).valid,'reject malformed/wrong faction/unknown/limits '+bad.slice(0,40));
for(const item of compositions){
 const p=player(),v=item.result,missing={v:[]},counts={v:[]};
 const cost=p.BetaGwentExchangeMissing(v.cards,v.leader,missing,counts);
 check(cost>0&&missing.v.includes(v.leader),'missing includes leader');
 p.betaGwentScraps=cost-1;const before=JSON.stringify(p);
 check(!p.BetaGwentCraftExchange(v.cards,v.faction,v.leader)&&JSON.stringify(p)===before,'insufficient funds are atomic');
 p.betaGwentScraps=cost;p.pending=true;const pending=JSON.stringify(p);
 check(!p.BetaGwentCraftExchange(v.cards,v.faction,v.leader)&&JSON.stringify(p)===pending,'paid keg reservation blocks crafting');
 p.pending=false;check(p.BetaGwentCraftExchange(v.cards,v.faction,v.leader)&&p.BetaGwentScraps()===0&&p.backups===1,'exact cost craft and backup');
 check(p.BetaGwentExchangeMissing(v.cards,v.leader,missing,counts)===0&&missing.v.length===0,'all missing copies acquired');
 check(p.BetaGwentCraftExchange(v.cards,v.faction,v.leader)&&p.BetaGwentScraps()===0,'repeat import spends nothing');
}
for(const id of [r.leader,...new Set(r.cards)]){
 const p=player(),cap=BetaGwentCollectionCap(id);
 check(p.BetaGwentConsoleGrant(id,1000)===cap&&p.BetaGwentOwned(id)===cap,'console cap');
 check(p.BetaGwentConsoleGrant(id,1)===0&&p.BetaGwentScraps()===0,'repeat grant never mills');
 for(const count of [-1,0,1001])check(p.BetaGwentConsoleGrant(id,count)===-1,'invalid grant count');
 check(p.BetaGwentConsoleGrant(999999,1)===-1,'invalid ID');
}
for(const faction of [1,2,4,8,16,32]){
 const p=player();check(p.BetaGwentConsoleFaction(faction,false)>0,'faction populated');
 check(p.BetaGwentConsoleFaction(faction,false)===0,'repeat faction idempotent');
 for(const id of p.betaGwentOwnedIds)check(BetaGwentDuelDefinition(id).header.factionMask===faction,'faction boundaries');
}
const corrupt=player();corrupt.betaGwentCollectionSchema=99;
check(corrupt.BetaGwentConsoleGrant(r.leader,1)===-1&&corrupt.backups===0,'unknown schema preserved');
// Merchant inventory shim: run the real stock diagnostic against successful,
// failed and partial AddAnItem, existing overstock, normal and NG+ flags.
let ng=0;globalThis.FactsQuerySum=()=>ng;
globalThis.theGame={GetDefinitionsManager(){return {GetItemCategory(){return 'usable';}};}};
function shop(quantity,limit=99,innkeeper=true){
 let stock=quantity;const inv={GetItemQuantityByName(){return stock;},AddAnItem(n,q){stock+=Math.min(q,limit);},GetAllItems(a){a.v=stock?[1]:[];},GetItemName(){return 'betagwent_keg';}};
 const menu=new CR4InventoryMenu();menu._shopNpc={GetInventory(){return inv;},GetGuidHash(){return 42;},GetComponentByClassName(){return {GetMapPinType(){return innkeeper?'Innkeeper':'Blacksmith';}};}};
 menu.ShopUpdateItem=()=>{};menu.UpdateMerchantData=()=>{};menu.UpdateItemsCounter=()=>{};return {menu,stock:()=>stock};
}
for(ng of [0,1])for(const stock of [0,1,5,8]){
 const s=shop(stock);s.menu.BetaGwentShopDiagnostic(0,false);check(s.stock()===stock,'read-only diagnostic');
 s.menu.BetaGwentShopDiagnostic(5,true);check(s.stock()===Math.max(5,stock),'refill target');
 s.menu.BetaGwentShopDiagnostic(5,true);check(s.stock()===Math.max(5,stock),'repeat refill idempotent');
}
for(const limit of [0,2]){const s=shop(0,limit);const message=s.menu.BetaGwentShopDiagnostic(5,true);check(s.stock()===limit&&!s.menu._shopNpc.betaGwentInnkeeperKegsStocked&&message.includes('Предмет не создан'),'failed/partial add does not mark stocked');}
const blacksmith=shop(0,99,false);blacksmith.menu.BetaGwentShopDiagnostic(5,true);check(blacksmith.stock()===0,'not an innkeeper');
const closed=new CR4InventoryMenu();check(closed.BetaGwentShopDiagnostic(5,true).includes('Откройте'),'closed shop rejected');
globalThis.thePlayer=player();
function board(){const b=new CR4BetaGwentBoardMenu();b.configured=true;b.selectingDecks=true;b.libraryOnly=true;b.revision=7;b.deckDraft={slot:1,cards:[12],title:'Keep'};b.deckLibrary={FirstEmpty:()=>1,Edit:()=>({slot:1,title:'New'})};b.PublishCollection=()=>{};b.PublishDeckEditor=()=>b.revision++;b.PublishDeckExchange=(code,message,accepted)=>b.reply={code,message,accepted};return b;}
for(const invalid of ['',good+',']){const b=board(),before=JSON.stringify(b.deckDraft),profile=JSON.stringify(thePlayer);b.OnBetaGwentDeckImport(7,invalid,true);check(JSON.stringify(b.deckDraft)===before&&JSON.stringify(thePlayer)===profile,'invalid native event leaves draft and profile untouched');}
let b=board();check(!b.OnBetaGwentDeckImport(6,good,false)&&!b.reply,'stale import ignored');
b=board();b.npcMatch=true;b.forcedBetaFaction=r.faction===2?4:2;check(!b.OnBetaGwentDeckImport(7,good,true),'forced quest faction');
b=board();b.deckDraft=null;b.deckLibrary.FirstEmpty=()=>0;check(!b.OnBetaGwentDeckImport(7,good,true)&&thePlayer.backups===0,'no slot before spending');
b=board();check(!b.OnBetaGwentDeckImport(7,good,false)&&b.deckDraft.cards[0]===12&&b.reply.message.includes('Недостающие'),'missing preview preserves draft');
thePlayer.betaGwentScraps=100000;b=board();check(b.OnBetaGwentDeckImport(7,good,true)&&b.deckDraft.cards.length===r.cards.length&&b.deckDraft.title==='Keep'&&b.reply.accepted,'confirmed craft imports draft without storing slot');
let isMenu=false,messages=[],rootMenu=null;
theGame.GetGuiManager=()=>({IsAnyMenu:()=>isMenu,ShowNotification:s=>messages.push(s),GetRootMenu:()=>rootMenu});
thePlayer=player();
for(const bad of [-1,0,1000001,2147483647]){bg_kegs(bad);bg_scraps(bad);check(thePlayer.kegs===0&&thePlayer.betaGwentScraps===0&&thePlayer.backups===0,'invalid resource request preserves profile');}
bg_kegs(10);bg_scraps(1000);check(thePlayer.kegs===10&&thePlayer.betaGwentScraps===1000&&thePlayer.backups===2,'counter grants mirror immediately');
thePlayer.kegs=2000000000;thePlayer.betaGwentScraps=2000000000;bg_kegs(1);bg_scraps(1);check(thePlayer.kegs===2000000000&&thePlayer.betaGwentScraps===2000000000&&thePlayer.backups===2,'integer overflow refused');
isMenu=true;bg_kegs(5);bg_scraps(5);bg_card(r.leader,1);check(thePlayer.backups===2&&thePlayer.BetaGwentOwned(r.leader)===0,'resource mutation blocked in menus');isMenu=false;
bg_card(r.leader,0);check(thePlayer.BetaGwentOwned(r.leader)===0,'zero card count rejected');
bg_card(r.leader,1);bg_card(r.leader,3);check(thePlayer.BetaGwentOwned(r.leader)===1,'card command obeys cap');
const beforeFaction=thePlayer.backups;bg_faction('unknown');check(thePlayer.backups===beforeFaction,'unknown faction refused');
bg_leaders();const allLeaders={v:[]};BetaGwentDuelLeaders(allLeaders);for(const id of allLeaders.v)check(thePlayer.BetaGwentOwned(id)===1,'leader command complete');
bg_find('zzzzzzz');check(messages.at(-1).includes('0'),'search no results');
bg_help();for(const command of ['bg_kegs','bg_scraps','bg_card','bg_find','bg_faction','bg_leaders','bg_allcards','bg_status','bg_shopcheck','bg_shoprefill','bg_help'])check(messages.at(-1).includes(command),'help covers '+command);
bg_shoprefill(5);check(messages.at(-1).includes('Откройте'),'shop console refuses missing context');
rootMenu=shop(0).menu;bg_shoprefill(5);bg_shoprefill(5);bg_shopcheck();check(messages.at(-1).includes('stock=5'),'shop commands use actual stock');
bg_status();check(messages.at(-1).includes('NG+'),'status contains NG+');
console.log(JSON.stringify({checks,compositions:compositions.length,actualWitcherScript:true,gameTested:false}));
'''
# Host cast checks use these two native types.
# These types are native, so object shims need permissive casts in this harness.
host=host.replace('return v instanceof cls ? v : null;','return v;')
script=OUT/'test.js';script.write_text(host+'\n'+code+'\n'+tests,'utf8')
r=subprocess.run(['node',str(script)],cwd=ROOT,capture_output=True,text=True,encoding='utf8');print(r.stdout,r.stderr,end='');assert r.returncode==0
(ROOT/'docs/evidence/features082-ws.json').write_text(json.dumps(json.loads(r.stdout),indent=2)+'\n','utf8')
