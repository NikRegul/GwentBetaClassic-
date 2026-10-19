"""Generate the standalone, explicitly invoked save cleaner. Never runs it."""
from pathlib import Path
import re,json,shutil,hashlib,sys
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'BetaGwent/build/release082-polish1';OUT=ROOT/'BetaGwent/build/cleaner082'
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'\xef\xbb\xbf'+s.replace('\n','\r\n').encode('utf8'))
def main():
    assert not OUT.exists()
    fields=[];player=[];other=[]
    for p in sorted((BASE/'scripts').rglob('*.ws')):
        s=p.read_text('utf-8-sig')
        for target,decl,name,kind in re.findall(r'@addField\((\w+)\)\s*((?:private|public|protected)\s+saved\s+var\s+(\w+)\s*:\s*([^;]+);)',s):
            fields.append(dict(target=target,name=name,type=kind,source=p.name))
            if target=='W3PlayerWitcher':player.append((decl,name,kind))
            else:other.append(dict(target=target,name=name,type=kind))
    literal=set()
    for p in (BASE/'scripts').rglob('*.ws'):
        literal.update(re.findall(r'"((?:bg_|betagwent_)[A-Za-z0-9_]+)"',p.read_text('utf-8-sig')))
    # Prefixes and format fragments are handled by bounded schema sweeps below.
    literal={k for k in literal if not k.endswith('_')}
    saved='\n'.join('@addField(W3PlayerWitcher)\n'+decl for decl,_,_ in player)
    reset='\n'.join('    '+name+('.Clear();' if kind.startswith('array<') else '=false;' if kind=='bool' else '=0;') for _,name,kind in player)
    fixed='\n'.join('    BetaGwentCleanKey('+json.dumps(k)+');' for k in sorted(literal))
    owned='\n'.join('    if(key=='+json.dumps(k)+')return true;' for k in sorted(literal))
    source=saved+'''
function BetaGwentCleanOwnedKey(key : string) : bool
{
    if(StrLeft(key,6)=="bg_b2_" || StrLeft(key,6)=="bg_bk_" || StrLeft(key,7)=="bg_bkn_" || StrLeft(key,7)=="bg_bkq_")return true;
'''+owned+'''
    return false;
}
function BetaGwentCleanMessage(value : string)
{ LogChannel('BetaGwent',value);theGame.GetGuiManager().ShowNotification(value); }
function BetaGwentCleanKey(key : string)
{
    // All entry points share this namespace boundary, including imported lists.
    if(!BetaGwentCleanOwnedKey(key))return;
    if(FactsDoesExist(key))FactsRemove(key);
}
exec function bg_clean_preview()
{
    BetaGwentCleanMessage("Beta Gwent cleaner: make a backup; remove the main mod. Run bg_clean_confirm('DELETE_BETA_GWENT'), then SAVE AS NEW SLOT. No automatic cleanup.");
}
function BetaGwentCleanKeys(keys : string)
{
    var i : int;var part,letter : string;
    if(StrLen(keys)>2048)return;
    for(i=0;i<StrLen(keys);i+=1){letter=StrMid(keys,i,1);if(letter=="|"){BetaGwentCleanKey(part);part="";}else part+=letter;}
    BetaGwentCleanKey(part);
}
exec function bg_clean_keys(keys : string) { BetaGwentCleanKeys(keys); }
@addMethod(W3PlayerWitcher)
public function BetaGwentCleanProfile082()
{
    var bank,i,slot,count : int;var p,d,itemName : string;var actor : CActor;var inventory : CInventoryComponent;var items : array<SItemUniqueId>;
    // Read dynamic reward identifiers before clearing saved arrays.
    for(i=0;i<betaGwentRewardedNpcs.Size();i+=1)BetaGwentCleanKey("bg_bkn_"+betaGwentRewardedNpcs[i]);
    for(i=0;i<betaGwentRewardedQuests.Size();i+=1)BetaGwentCleanKey("bg_bkq_"+NameToString(betaGwentRewardedQuests[i]));
    // Scan valid schema capacities, including stale slots above the last count.
    for(bank=1;bank<=2;bank+=1){p="bg_b2_"+bank+"_";
        for(i=0;i<2048;i+=1){BetaGwentCleanKey(p+"ci"+i);BetaGwentCleanKey(p+"cc"+i);BetaGwentCleanKey(p+"ni"+i);}
        for(i=0;i<512;i+=1){BetaGwentCleanKey(p+"ka"+i);BetaGwentCleanKey(p+"ks"+i);BetaGwentCleanKey(p+"ko"+i);BetaGwentCleanKey(p+"ob"+i);BetaGwentCleanKey(p+"or"+i);}
        for(slot=1;slot<=13;slot+=1){d=p+"d"+slot+"_";BetaGwentCleanKey(d+"n");BetaGwentCleanKey(d+"l");BetaGwentCleanKey(d+"f");for(i=0;i<40;i+=1)BetaGwentCleanKey(d+i);}
        BetaGwentCleanKeys(p+"gen|"+p+"sc|"+p+"kg|"+p+"pf|"+p+"sd|"+p+"tm|"+p+"re|"+p+"df|"+p+"ap|"+p+"cn|"+p+"ka|"+p+"ks|"+p+"ko|"+p+"ob|"+p+"or|"+p+"fm|"+p+"fg|"+p+"nc|"+p+"sa|"+p+"sb|"+p+"done");
    }
    for(i=0;i<2048;i+=1){BetaGwentCleanKey("bg_bk_ci_"+i);BetaGwentCleanKey("bg_bk_cc_"+i);}
    for(slot=1;slot<=13;slot+=1){d="bg_bk_d"+slot+"_";BetaGwentCleanKey(d+"n");BetaGwentCleanKey(d+"l");BetaGwentCleanKey(d+"f");for(i=0;i<40;i+=1)BetaGwentCleanKey(d+i);}
'''+fixed+'\n'+reset+'''
    inventory=GetInventory();if(inventory){inventory.GetAllItems(items);for(i=0;i<items.Size();i+=1){itemName=NameToString(inventory.GetItemName(items[i]));if(StrLeft(itemName,10)=="betagwent_")inventory.RemoveItem(items[i]);}}
    BetaGwentCleanMessage("Beta Gwent profile and known mirrors cleared. Save to NEW SLOT, exit, remove cleaner, load that slot and save again. Use the read-only fact index for orphaned reward keys.");
}
exec function bg_clean_confirm(confirmation : string)
{
    var player : W3PlayerWitcher;
    if(confirmation!="DELETE_BETA_GWENT"){BetaGwentCleanMessage("Cleanup not performed: confirmation mismatch.");return;}
    player=(W3PlayerWitcher)thePlayer;if(!player)return;
    if(theGame.GetGuiManager().IsAnyMenu() || player.IsInCombat()){BetaGwentCleanMessage("Close menus and leave combat before cleanup.");return;}
    player.BetaGwentCleanProfile082();
}
'''
    scripts=OUT/'scripts';write(scripts/'game/betagwent/cleaner082.ws',source)
    # Only player saved fields are retained to read the current ledger. No main
    # callbacks/initialization/restore logic is present in the standalone cleaner.
    manifest=dict(version='0.8.2',playerFields=len(player),allSavedFields=fields,fieldsDroppedWhenMainModRemoved=other,automaticCleanup=False,saveRoundTripVerified=False)
    (OUT/'inventory.json').write_text(json.dumps(manifest,indent=2),'utf8')
    sys.path.insert(0,str(ROOT/'tools/classic132'))
    from prepare_scripts import prepare
    audit=json.loads((BASE/'classic-audit/audit.json').read_text('utf8'));adir=OUT/'classic-audit'
    vanilla='game/player/playerWitcher.ws';target=adir/'baseline/vanilla-targets'/vanilla;target.parent.mkdir(parents=True)
    shutil.copy2(BASE/'classic-audit/baseline/vanilla-targets'/vanilla,target)
    audit['vanillaScripts']={vanilla:audit['vanillaScripts'][vanilla]};shutil.copytree(scripts,adir/'baseline/scripts')
    audit['sourceScripts']={p.relative_to(scripts).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in scripts.rglob('*.ws')};audit['sourceScriptCount']=1
    (adir/'audit.json').write_text(json.dumps(audit,indent=2),'utf8');prepare(adir,OUT/'classic-prepared')
    print('Standalone cleaner prepared:',len(player),'player saved fields; no save files changed')
if __name__=='__main__':main()
