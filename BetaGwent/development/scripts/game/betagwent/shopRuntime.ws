// Convert existing saved merchant stock before the native shop builds its UI.
// New loot and old inventories take the same path; original item definitions,
// player inventory, quests and native card rewards are left intact.
@wrapMethod(CR4InventoryMenu)
function OnConfigUI()
{
    var data : IScriptable;var init : W3InventoryInitData;var npc : CNewNPC;
    var inventory : CInventoryComponent;var player : W3PlayerWitcher;
    var items,current : array<SItemUniqueId>;var i,j,id,quantity,available,stockCount : int;
    data=GetMenuInitData();init=(W3InventoryInitData)data;npc=(CNewNPC)data;
    if(init)npc=(CNewNPC)init.containerNPC;
    player=(W3PlayerWitcher)thePlayer;
    if(npc && npc.HasTag('Merchant') && player && player.BetaGwentEnsureCollection()) {
        inventory=npc.GetInventory();if(inventory) {
            inventory.UpdateLoot();inventory.GetAllItems(items);
            // Expand the old single-keg stock once on existing merchant saves.
            // Fresh/replenished stock comes from the 5-keg loot overlay.
            if(!npc.betaGwentBulkKegStockMigrated && inventory.GetItemQuantityByName('betagwent_keg')>0) {
                stockCount=inventory.GetItemQuantityByName('betagwent_keg');
                if(stockCount<5)inventory.AddAnItem('betagwent_keg',5-stockCount,true,true);
                npc.betaGwentBulkKegStockMigrated=true;
            }
            for(i=0;i<items.Size();i+=1) {
                id=BetaGwentLegacyShopCard(inventory.GetItemName(items[i]));if(id==0)continue;
                quantity=inventory.GetItemQuantity(items[i]);stockCount=0;inventory.GetAllItems(current);
                for(j=0;j<current.Size();j+=1)if(BetaGwentShopCard(inventory.GetItemName(current[j]))==id)stockCount+=inventory.GetItemQuantity(current[j]);
                available=BetaGwentCollectionCap(id)-player.BetaGwentOwned(id)-stockCount;
                if(available<quantity)quantity=available;
                if(quantity>0)inventory.AddAnItem(BetaGwentModernShopItem(inventory.GetItemName(items[i])),quantity,true,true);
                inventory.RemoveItem(items[i]);
            }
            // Hide sold-out modern copies, including stock persisted before an
            // NPC/keg award. Do not let those cards take the player's money.
            inventory.GetAllItems(items);
            for(i=0;i<items.Size();i+=1) {
                id=BetaGwentShopCard(inventory.GetItemName(items[i]));
                if(id!=0 && player.BetaGwentOwned(id)>=BetaGwentCollectionCap(id))inventory.RemoveItem(items[i]);
            }
            LogChannel('BetaGwent',"SHOP_STOCK_CONVERTED npc="+npc.GetGuidHash());
        }
    }
    wrappedMethod();
}

@wrapMethod(CR4InventoryMenu)
function BuyItem(item : SItemUniqueId, quantity : int) : bool
{
    var id,cost,i : int;var newItem : SItemUniqueId;var itemName : name;var stock : CInventoryComponent;
    var player : W3PlayerWitcher;var invItem : SInventoryItem;var d : SBetaGwentDuelDefinition;var message : string;
    if(_shopNpc)stock=_shopNpc.GetInventory();
    if(stock){itemName=stock.GetItemName(item);id=BetaGwentShopCard(itemName);}
    if(!stock || (id==0 && itemName!='betagwent_keg'))return wrappedMethod(item,quantity);
    player=(W3PlayerWitcher)thePlayer;
    if(!player || !player.BetaGwentEnsureCollection())return false;
    if(id!=0 && player.BetaGwentKegPending()) {
        showNotification("Сначала завершите выбор оплаченной бочки через меню колод.");return false;
    }
    if(itemName=='betagwent_keg') {
        if(quantity<1 || quantity>stock.GetItemQuantity(item) || quantity>player.BetaGwentKegPurchaseCapacity()) {
            showNotification("Нельзя купить больше бочек, чем осталось редких карт. Уже купленные бочки учтены.");return false;
        }
        // The quantity is bounded by stock and the finite rare pool before multiplication.
        cost=200*quantity;
        if(player.GetMoney()<cost){showNotification("Недостаточно крон. Бочка стоит 200 крон.");return false;}
        // Stage 110: kegs go to a save counter, never into Geralt's inventory (see kegProfile.ws).
        if(!stock.RemoveItem(item,quantity))return false;
        player.RemoveMoney(cost);stock.AddMoney(cost);player.BetaGwentAddKegs(quantity);
        LogChannel('BetaGwent',"KEG_PURCHASE quantity="+quantity+" crowns="+cost+" unopened="+player.BetaGwentKegCount());
        message="Неоткрытых бочек: "+player.BetaGwentKegCount()+". Открыть их можно в редакторе колод гвинта.";showNotification(message);
    }else {
        if(quantity<1 || quantity>stock.GetItemQuantity(item) || player.BetaGwentOwned(id)+quantity>BetaGwentCollectionCap(id)) {
            showNotification("Достигнут лимит копий этой карты.");return false;
        }
        invItem=stock.GetItem(item);cost=stock.GetInventoryItemPriceModified(invItem,false)*quantity;
        if(cost<0 || player.GetMoney()<cost){showNotification("Недостаточно крон.");return false;}
        if(!stock.RemoveItem(item,quantity))return false;
        player.RemoveMoney(cost);stock.AddMoney(cost);
        for(i=0;i<quantity;i+=1)player.BetaGwentGrant(id);
        LogChannel('BetaGwent',"SHOP_CARD_PURCHASE card="+id+" copies="+quantity+" crowns="+cost);
        d=BetaGwentDuelDefinition(id);message="В коллекцию добавлена карта: "+d.title;showNotification(message);
    }
    if(stock.GetItemQuantity(item)==0)ShopRemoveItem(item);else ShopUpdateItem(item);
    UpdatePlayerMoney();UpdateMerchantData();UpdateItemsCounter();theSound.SoundEvent("gui_inventory_buy");return true;
}

@addField(CNewNPC)
public saved var betaGwentBulkKegStockMigrated : bool;

// Native inventory supplies quantity controls; keep their displayed price exact.
@wrapMethod(CR4InventoryMenu)
function OnBuyItem(item : SItemUniqueId, quantity : int, moveToIdx : int)
{
    var maximum : int;var player : W3PlayerWitcher;
    if(!_shopNpc || _shopNpc.GetInventory().GetItemName(item)!='betagwent_keg' || quantity<=1) {
        return wrappedMethod(item,quantity,moveToIdx);
    }
    player=(W3PlayerWitcher)thePlayer;if(!player)return false;
    maximum=Min(quantity,player.BetaGwentKegPurchaseCapacity());
    maximum=Min(maximum,player.GetMoney()/200);
    if(maximum<1){showNotification("Недостаточно крон или все редкие карты уже получены/зарезервированы купленными бочками.");return false;}
    if(_quantityPopupData)delete _quantityPopupData;
    _quantityPopupData=new QuantityPopupData in this;
    _quantityPopupData.itemId=item;_quantityPopupData.actionType=QTF_Buy;_quantityPopupData.inventoryRef=this;
    _quantityPopupData.itemCost=200;_quantityPopupData.showPrice=true;
    _quantityPopupData.minValue=1;_quantityPopupData.currentValue=1;_quantityPopupData.maxValue=maximum;
    RequestSubMenu('PopupMenu',_quantityPopupData);return true;
}

// Stage 110: kegs are opened only from the deck editor (Kegs button). The
// inventory gets no Use action; if the vanilla consume path is ever reached,
// keep the keg instead of eating it.
@wrapMethod(CR4InventoryMenu)
function OnConsumeItem(item : SItemUniqueId)
{
    if(thePlayer.inv.GetItemName(item)!='betagwent_keg'){return wrappedMethod(item);}
    showNotification("Бочку можно открыть в редакторе колод гвинта.");return false;
}

