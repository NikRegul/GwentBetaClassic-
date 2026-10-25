"""Prepare a read-only merchant trace against the exact installed Classic scripts."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
GAME = Path(r'D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt')
OUT = ROOT / 'BetaGwent/build/classic090-shop-trace1'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists(), 'Keep diagnostic candidates immutable'
    source = GAME / 'Mods/modBetaGwentClassic132/content/scripts'
    target = OUT / 'Mods/modBetaGwentClassic132/content/scripts'
    shutil.copytree(source, target)
    original = {p.relative_to(source).as_posix(): sha(p) for p in source.rglob('*.ws')}
    path = target / 'game/gui/menus/inventoryMenu.ws'
    s = path.read_text('utf-16')
    anchor = '            inventory.UpdateLoot();inventory.GetAllItems(items);'
    assert s.count(anchor) == 1
    s = s.replace(anchor, '''            inventory.GetAllItems(current);
            LogChannel('BetaGwent',"SHOP_TRACE stage=before_update npc="+npc.GetGuidHash()+" stacks="+current.Size());
''' + anchor + '''
            LogChannel('BetaGwent',"SHOP_TRACE stage=after_update npc="+npc.GetGuidHash()+" stacks="+items.Size());''')
    anchor = '    BetaGwentClassicOriginal_OnConfigUI_12();'
    assert s.count(anchor) == 1
    s = s.replace(anchor, '''    if(inventory){inventory.GetAllItems(current);LogChannel('BetaGwent',"SHOP_TRACE stage=after_conversion stacks="+current.Size());}
''' + anchor + '''
    BetaGwentShopTrace090();''')
    end = s.rfind('}')
    s = s[:end] + '''
public function BetaGwentShopTrace090()
{
    var inventory : CInventoryComponent;
    var items : array<SItemUniqueId>;
    var i : int;
    LogChannel('BetaGwent',"SHOP_TRACE stage=native menuState="+m_menuState+" defaultState="+(int)_defaultInventoryState+" currentState="+(int)_currentState+" tab="+currentlySelectedTab+" shop="+(_shopNpc!=NULL)+" shopUI="+(_shopInv!=NULL));
    if(!_shopNpc){LogChannel('BetaGwent',"SHOP_TRACE no_shop_npc");return;}
    inventory=_shopNpc.GetInventory();
    if(!inventory){LogChannel('BetaGwent',"SHOP_TRACE no_inventory");return;}
    inventory.GetAllItems(items);
    LogChannel('BetaGwent',"SHOP_TRACE stage=native_stock npc="+_shopNpc.GetGuidHash()+" stacks="+items.Size()+" kegs="+inventory.GetItemQuantityByName('betagwent_keg'));
    for(i=0;i<Min(8,items.Size());i+=1)
        LogChannel('BetaGwent',"SHOP_TRACE item="+inventory.GetItemName(items[i])+" quantity="+inventory.GetItemQuantity(items[i])+" category="+inventory.GetItemCategory(items[i]));
}
''' + s[end:]
    path.write_bytes(b'\xff\xfe' + s.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-16le'))
    menu = target / 'game/betagwent/developmentBoardMenu.ws'
    s = menu.read_text('utf-16')
    s += '''
exec function bg_shoptrace()
{
    var menu : CR4InventoryMenu;
    LogChannel('BetaGwent',"SHOP_TRACE command=begin");
    menu=(CR4InventoryMenu)theGame.GetGuiManager().GetRootMenu();
    if(!menu){LogChannel('BetaGwent',"SHOP_TRACE root_is_not_inventory");return;}
    menu.BetaGwentShopTrace090();
}
'''
    menu.write_bytes(b'\xff\xfe' + s.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-16le'))
    prep = json.loads((ROOT / 'BetaGwent/build/release090-final12/classic-prepared-final/preparation.json').read_text('utf8'))
    prep['outputScripts'] = {p.relative_to(target).as_posix(): sha(p) for p in target.rglob('*.ws')}
    prep['diagnostic'] = 'Read-only stock counts; no inventory or save mutations added'
    (OUT / 'preparation.json').write_text(json.dumps(prep, indent=2), 'utf8')
    changed = [n for n in original if original[n] != prep['outputScripts'][n]]
    assert changed == sorted(changed) or len(changed) == 2
    assert set(changed) == {'game/gui/menus/inventoryMenu.ws', 'game/betagwent/developmentBoardMenu.ws'}
    (OUT / 'installed-before.json').write_text(json.dumps(original, indent=2), 'utf8')
    print(json.dumps({'out': str(OUT), 'changed': changed}))


if __name__ == '__main__':
    main()
