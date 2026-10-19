// Cleanup is explicit. This saved latch survives a reload before uninstall.
@addField(W3PlayerWitcher)
private saved var betaGwentCleanupPending090 : bool;
@addMethod(W3PlayerWitcher)
public function BetaGwentCleanupPending() : bool { return betaGwentCleanupPending090; }
function BetaGwentCleanupBlocked() : bool
{
    var player : W3PlayerWitcher;
    player=(W3PlayerWitcher)thePlayer;return player && player.BetaGwentCleanupPending();
}
function BetaGwentCleanCanRun() : bool
{
    var player : W3PlayerWitcher;var manager : CR4GwintManager;
    if(!theGame)return false;
    player=(W3PlayerWitcher)thePlayer;if(!player)return false;
    manager=theGame.GetGwintManager();
    if(theGame.GetGuiManager().IsAnyMenu() || player.IsInCombat() || (manager && (manager.gameRequested || manager.betaNpcPending)))
    {BetaGwentCleanMessage("Close menus, finish Gwent and leave combat before cleanup.");return false;}
    return true;
}
function BetaGwentCleanOwnedKey(key : string) : bool
{
    if(StrLeft(key,6)=="bg_b2_" || StrLeft(key,6)=="bg_bk_" || StrLeft(key,7)=="bg_bkn_" || StrLeft(key,7)=="bg_bkq_")return true;
    if(key=="betagwent_all_cards_collected")return true;
    if(key=="betagwent_collection_owned")return true;
    if(key=="betagwent_tournament_access_ready")return true;
    if(key=="bg_b2_cur")return true;
    if(key=="bg_b2_gen")return true;
    if(key=="bg_b2_hold")return true;
    if(key=="bg_b2_restored")return true;
    if(key=="bg_bk_cn")return true;
    if(key=="bg_bk_d")return true;
    if(key=="bg_bk_kegs")return true;
    if(key=="bg_bk_pref")return true;
    if(key=="bg_bk_schema")return true;
    if(key=="bg_bk_scraps")return true;
    if(key=="bg_hide_help")return true;
    if(key=="bg_language_preferences_initialized")return true;
    if(key=="bg_static_leaders")return true;
    if(key=="bg_text_language")return true;
    if(key=="bg_text_language_package")return true;
    if(key=="bg_tutorial_seen")return true;
    if(key=="bg_voice_language")return true;
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
    BetaGwentCleanMessage("Beta Gwent cleaner: make a save backup. Built into the main mod. Run bg_clean_confirm('DELETE_BETA_GWENT'), then SAVE AS NEW SLOT, exit, uninstall the mod, load and save again. No automatic cleanup.");
}
function BetaGwentCleanKeys(keys : string)
{
    var i : int;var part,letter : string;
    if(StrLen(keys)>2048)return;
    for(i=0;i<StrLen(keys);i+=1){letter=StrMid(keys,i,1);if(letter=="|"){BetaGwentCleanKey(part);part="";}else part+=letter;}
    BetaGwentCleanKey(part);
}
exec function bg_clean_keys(keys : string)
{
    if(!BetaGwentCleanCanRun())return;
    if(!BetaGwentCleanupBlocked()){BetaGwentCleanMessage("Run bg_clean_confirm('DELETE_BETA_GWENT') first. No facts changed.");return;}
    BetaGwentCleanKeys(keys);
}
@addMethod(W3PlayerWitcher)
public function BetaGwentCleanProfile090()
{
    var bank,i,slot,count,quantity,failed : int;var p,d,itemName : string;var actor : CActor;var inventory : CInventoryComponent;var items : array<SItemUniqueId>;
    betaGwentCleanupPending090=true;
    RemoveTimer('BetaGwentQuestSyncTick');betaGwentQuestSyncPasses=0;
    betaGwentCollectionTrackingReady=false;betaGwentTrackedCollectionSize=0;
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
    BetaGwentCleanKey("betagwent_all_cards_collected");
    BetaGwentCleanKey("betagwent_collection_owned");
    BetaGwentCleanKey("betagwent_tournament_access_ready");
    BetaGwentCleanKey("bg_b2_cur");
    BetaGwentCleanKey("bg_b2_gen");
    BetaGwentCleanKey("bg_b2_hold");
    BetaGwentCleanKey("bg_b2_restored");
    BetaGwentCleanKey("bg_bk_cn");
    BetaGwentCleanKey("bg_bk_d");
    BetaGwentCleanKey("bg_bk_kegs");
    BetaGwentCleanKey("bg_bk_pref");
    BetaGwentCleanKey("bg_bk_schema");
    BetaGwentCleanKey("bg_bk_scraps");
    BetaGwentCleanKey("bg_hide_help");
    BetaGwentCleanKey("bg_language_preferences_initialized");
    BetaGwentCleanKey("bg_static_leaders");
    BetaGwentCleanKey("bg_text_language");
    BetaGwentCleanKey("bg_text_language_package");
    BetaGwentCleanKey("bg_tutorial_seen");
    BetaGwentCleanKey("bg_voice_language");
    betaGwentProbeSchema=0;
    betaGwentProbeIds.Clear();
    betaGwentProbeCounter=0;
    betaGwentCollectionSchema=0;
    betaGwentOwnedIds.Clear();
    betaGwentOwnedCopies.Clear();
    betaGwentProgressionSeed=0;
    betaGwentRewardedNpcs.Clear();
    betaGwentRewardActors.Clear();
    betaGwentRewardActorWins.Clear();
    betaGwentRewardedQuests.Clear();
    betaGwentStarterSetRevision=0;
    betaGwentNewCardsSchema=0;
    betaGwentNewCardIds.Clear();
    betaGwentAnimationTempo=0;
    betaGwentReducedEffects=false;
    betaGwentDifficulty=0;
    betaGwentAiPause=0;
    betaGwentDeckSchema=0;
    betaGwentDeckNames.Clear();
    betaGwentDeckLeaders.Clear();
    betaGwentDeckFactions.Clear();
    betaGwentDeckLengths.Clear();
    betaGwentDeckCards.Clear();
    betaGwentPreferredDeck=0;
    betaGwentStarterDeckSchema=0;
    betaGwentStarterDeckNames.Clear();
    betaGwentStarterDeckLeaders.Clear();
    betaGwentStarterDeckFactions.Clear();
    betaGwentStarterDeckLengths.Clear();
    betaGwentStarterDeckCards.Clear();
    betaGwentKegAutomatic.Clear();
    betaGwentKegOffers.Clear();
    betaGwentKegAutomaticScraps.Clear();
    betaGwentKegsUnopened=0;
    betaGwentOpponentBag.Clear();
    betaGwentOpponentRecent.Clear();
    betaGwentScraps=0;
    inventory=GetInventory();if(inventory){inventory.GetAllItems(items);for(i=0;i<items.Size();i+=1){itemName=NameToString(inventory.GetItemName(items[i]));if(StrLeft(itemName,10)=="betagwent_"){quantity=inventory.GetItemQuantity(items[i]);if(quantity>0 && !inventory.RemoveItem(items[i],quantity))failed+=1;}}}
    if(failed>0)
    {
        // One result only: a later success notification must not hide this.
        BetaGwentCleanMessage("Beta Gwent cleanup is INCOMPLETE: "+failed+" inventory stack(s) could not be removed. Do not uninstall yet. Drop or sell the remaining Beta Gwent items, then run bg_clean_confirm('DELETE_BETA_GWENT') again.");
        return;
    }
    BetaGwentCleanMessage("Beta Gwent profile and known mirrors cleared. Save to NEW SLOT, exit, uninstall Beta Gwent, load that slot and save again. Use the read-only fact index for orphaned reward keys.");
}
exec function bg_clean_confirm(confirmation : string)
{
    var player : W3PlayerWitcher;
    if(confirmation!="DELETE_BETA_GWENT"){BetaGwentCleanMessage("Cleanup not performed: confirmation mismatch.");return;}
    if(!BetaGwentCleanCanRun())return;
    player=(W3PlayerWitcher)thePlayer;
    player.BetaGwentCleanProfile090();
}
