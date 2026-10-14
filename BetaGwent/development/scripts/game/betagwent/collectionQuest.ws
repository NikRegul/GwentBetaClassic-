// One of each collectible template and leader. Copies beyond the first do not
// affect collection completion. Original completed quests are not rolled back.
@addField(W3PlayerWitcher)
private var betaGwentCollectionTrackingReady : bool;
@addField(W3PlayerWitcher)
private var betaGwentTrackedCollectionSize : int;

@addMethod(W3PlayerWitcher)
public function BetaGwentCollectionCount(faction : int) : int
{
    var i,count : int;var seen : array<int>;var d : SBetaGwentDuelDefinition;
    if(betaGwentCollectionSchema!=1 || betaGwentOwnedIds.Size()!=betaGwentOwnedCopies.Size())return 0;
    for(i=0;i<betaGwentOwnedIds.Size();i+=1) {
        if(betaGwentOwnedCopies[i]<1 || seen.Contains(betaGwentOwnedIds[i]) || BetaGwentCollectionCap(betaGwentOwnedIds[i])==0)continue;
        seen.PushBack(betaGwentOwnedIds[i]);
        if(faction==0)count+=1;
        else {d=BetaGwentDuelDefinition(betaGwentOwnedIds[i]);if(d.header.factionMask==faction)count+=1;}
    }
    return count;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentUpdateCollectionProgress()
{
    var owned,total : int;
    if(betaGwentCollectionSchema!=1 || betaGwentOwnedIds.Size()!=betaGwentOwnedCopies.Size())return;
    if(betaGwentCollectionTrackingReady && betaGwentTrackedCollectionSize==betaGwentOwnedIds.Size())return;
    owned=BetaGwentCollectionCount(0);total=BetaGwentCollectionTotal(0);
    betaGwentCollectionTrackingReady=true;betaGwentTrackedCollectionSize=betaGwentOwnedIds.Size();
    if(owned>0 && !FactsDoesExist("Gwint_Card_Looted"))FactsAdd("Gwint_Card_Looted",1,-1);
    if(FactsQuerySum("betagwent_collection_owned")!=owned) {
        if(FactsDoesExist("betagwent_collection_owned"))FactsRemove("betagwent_collection_owned");
        if(owned>0)FactsAdd("betagwent_collection_owned",owned,-1);
    }
    // Disable the native legacy-item achievement scan. Its collection still
    // supplies scripted tournament/reward facts, but does not finish this quest.
    if(!FactsDoesExist("fix_for_gwent_achievement_bug_121588"))FactsAdd("fix_for_gwent_achievement_bug_121588",1,-1);
    if(owned==total && total>0 && !FactsDoesExist("betagwent_all_cards_collected")) {
        FactsAdd("betagwent_all_cards_collected",1,-1);
        if(!FactsDoesExist("gwint_all_cards_collected"))FactsAdd("gwint_all_cards_collected",1,-1);
        theGame.GetGamerProfile().AddAchievement(EA_GwintCollector);
        LogChannel('BetaGwent',"COLLECTION_COMPLETE owned="+owned+" total="+total);
    }
    LogChannel('BetaGwent',"COLLECTION_PROGRESS owned="+owned+" total="+total);
}
@addMethod(W3PlayerWitcher)
public function BetaGwentAlmanac() : string
{
    var result : string;var owned,total : int;
    if(!BetaGwentEnsureCollection())return "Коллекция Beta недоступна: неизвестная схема сохранения.";
    owned=BetaGwentCollectionCount(0);total=BetaGwentCollectionTotal(0);
    result="<b>Коллекция Beta Gwent 0.9.24</b><br>Собрано: "+owned+" / "+total+". Осталось: "+(total-owned)+".<br><br>";
    result+="Для «Собрать их все» достаточно одной копии каждой карты и каждого лидера. Три копии бронзы нужны только для колод.<br><br>Не получено по фракциям:<br>";
    result+="Нейтральные: "+(BetaGwentCollectionTotal(1)-BetaGwentCollectionCount(1))+"<br>";
    result+="Чудовища: "+(BetaGwentCollectionTotal(2)-BetaGwentCollectionCount(2))+"<br>";
    result+="Север: "+(BetaGwentCollectionTotal(8)-BetaGwentCollectionCount(8))+"<br>";
    result+="Нильфгаард: "+(BetaGwentCollectionTotal(4)-BetaGwentCollectionCount(4))+"<br>";
    result+="Скоя’таэли: "+(BetaGwentCollectionTotal(16)-BetaGwentCollectionCount(16))+"<br>";
    result+="Скеллиге: "+(BetaGwentCollectionTotal(32)-BetaGwentCollectionCount(32))+"<br><br>";
    result+="Все недостающие карты доступны из бочек у квартирмейстера в крепости Барона. Бронза и серебро также выдаются за первую победу над обычными игроками; некоторые продаются торговцами.<br>Назначенное квестовое золото и персонажей можно посмотреть в полном каталоге через меню колод.";
    if(owned==total)result+="<br><br><b>Коллекция собрана полностью!</b>";
    LogChannel('BetaGwent',"COLLECTION_ALMANAC owned="+owned+" total="+total);return result;
}

@wrapMethod(CInventoryComponent)
function GetGwentAlmanacContents() : string
{
    var player : W3PlayerWitcher;player=GetWitcherPlayer();
    if(player && player.BetaGwentEnsureCollection())return player.BetaGwentAlmanac();
    return wrappedMethod();
}

@wrapMethod(CInventoryComponent)
function OnItemAdded(data : SItemChangedData)
{
    var player : W3PlayerWitcher;var muted : array<SItemUniqueId>;var i : int;
    player=GetWitcherPlayer();
    if(player && GetEntity()==player && player.BetaGwentEnsureCollection()) {
        // Native OnItemAdded reads the first ID's collector tag while iterating
        // all items. Temporarily suppress every tagged ID, then restore it.
        for(i=0;i<data.ids.Size();i+=1) {
            if(ItemHasTag(data.ids[i],theGame.params.GWINT_CARD_ACHIEVEMENT_TAG) && RemoveItemTag(data.ids[i],theGame.params.GWINT_CARD_ACHIEVEMENT_TAG))muted.PushBack(data.ids[i]);
        }
    }
    wrappedMethod(data);
    for(i=0;i<muted.Size();i+=1)if(GetItemQuantity(muted[i])>0)AddItemTag(muted[i],theGame.params.GWINT_CARD_ACHIEVEMENT_TAG);
}

// Repair the DLC's display from permanent native quest reward claims. Owning
// a Beta starter deck qualifies for admission but must not fabricate NPC wins.
function BetaGwentSkelligeQuestClaims() : int
{
    var merchants : array<name>;var i,count : int;
    merchants.PushBack('shop_12_tournament_meadows_armourer');
    merchants.PushBack('shop_13_tournament_meadows_blacksmith');
    merchants.PushBack('shop_18_cocatrice_inn_innkeeper');
    merchants.PushBack('shop_19_rafstmen_village_innkeeper');
    merchants.PushBack('shop_09_ravello_herbalist');
    merchants.PushBack('shop_25_tournament_meadows_innkeper');
    merchants.PushBack('shop_31_trappers_village_innkeeper');
    merchants.PushBack('shop_32_trappers_village_armourer');
    merchants.PushBack('shop_37_city_west_innkeeper');
    merchants.PushBack('shop_38_city_west_armourer');
    merchants.PushBack('shop_41_city_west_alchemist');
    merchants.PushBack('shop_43_city_east_wine_merchant');
    merchants.PushBack('shop_45_city_east_merchant');
    merchants.PushBack('shop_46_city_south_herbalist');
    merchants.PushBack('shop_47_city_brothel_mom');
    merchants.PushBack('shop_14_tournament_meadows_barber');
    merchants.PushBack('shop_22_port_butcher');
    merchants.PushBack('shop_cammerlengo');
    merchants.PushBack('q705_tailor');
    for(i=0;i<merchants.Size();i+=1)if(FactsQuerySum("merchant_card_"+merchants[i]+"_card_already_given")>0)count+=1;
    return count;
}
function BetaGwentSyncSkelligeQuestProgress()
{
    var manager : CWitcherJournalManager;var entries : array<CJournalBase>;
    var objective : CJournalQuestObjective;var questEntry : CJournalQuest;var phase : CJournalQuestPhase;var i,j,k,count,current : int;
    manager=theGame.GetJournalManager();if(!manager)return;
    count=BetaGwentSkelligeQuestClaims();if(count==0)return;
    // Follow the native quest-menu traversal. Activated roots are quests;
    // their objectives live inside phases, not in the root registry.
    manager.GetActivatedOfType('CJournalQuest',entries);
    for(i=0;i<entries.Size();i+=1){
        questEntry=(CJournalQuest)entries[i];
        if(!questEntry || questEntry.baseName!="cg700_all_cards" || manager.GetEntryStatus(questEntry)!=JS_Active)continue;
        for(j=0;j<questEntry.GetNumChildren();j+=1){
            phase=(CJournalQuestPhase)questEntry.GetChild(j);if(!phase)continue;
            for(k=0;k<phase.GetNumChildren();k+=1){
                objective=(CJournalQuestObjective)phase.GetChild(k);
                if(!objective || objective.GetCount()!=19 || manager.GetEntryStatus(objective)!=JS_Active)continue;
                current=manager.GetQuestObjectiveCount(objective.guid);
                if(current<count){manager.SetQuestObjectiveCount(objective.guid,count);LogChannel('BetaGwent',"SKELLIGE_QUEST_PROGRESS old="+current+" claimed="+count);}
            }
        }
    }
}
// Run outside the reward graph, which can increment its counter later in the
// same frame. Never double-increment, reset completed quests or alter admission.
@wrapMethod(CR4JournalQuestMenu)
function OnConfigUI()
{
    BetaGwentSyncSkelligeQuestProgress();wrappedMethod();
}

// Wait until the native reward graph has left its win branch before repairing
// the HUD counter. Read claims; never increment or award a second card.
@addField(W3PlayerWitcher)
private var betaGwentQuestSyncPasses : int;
@addMethod(W3PlayerWitcher)
public function BetaGwentScheduleQuestSync()
{
    RemoveTimer('BetaGwentQuestSyncTick');betaGwentQuestSyncPasses=3;
    AddTimer('BetaGwentQuestSyncTick',3.0f,false);
}
@addMethod(W3PlayerWitcher)
private timer function BetaGwentQuestSyncTick(deltaTime : float, timerId : int)
{
    BetaGwentSyncSkelligeQuestProgress();betaGwentQuestSyncPasses-=1;
    if(betaGwentQuestSyncPasses>0)AddTimer('BetaGwentQuestSyncTick',3.0f,false);
}
