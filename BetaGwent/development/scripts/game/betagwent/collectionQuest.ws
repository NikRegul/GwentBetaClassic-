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
