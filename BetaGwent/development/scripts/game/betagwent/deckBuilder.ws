// Original DefaultDeckValidatorRuleSet:25-40 non-leader cards,4 gold,6 silver,
// bronze copies3, silver/gold copies1, one non-neutral faction; no unit minimum.
struct SBetaGwentDeckValidation
{
    var total, bronze, silver, gold, units, specials : int;
    var valid : bool;
    var message : string;
}
function BetaGwentValidateDeck(ids : array<int>, faction : int, leaderId : int) : SBetaGwentDeckValidation
{
    var result : SBetaGwentDeckValidation;
    var d, leader : SBetaGwentDuelDefinition;
    var i, j, copies, limit : int;
    result.total = ids.Size(); leader = BetaGwentDuelDefinition(leaderId);
    if (!BetaGwentDuelIsLeader(leaderId) || leader.header.factionMask != faction)
    { result.message = "Выберите лидера своей фракции."; return result; }
    if (ids.Size() > 40) { result.message = "В колоде может быть не больше40 карт."; return result; }
    for (i = 0; i < ids.Size(); i += 1)
    {
        d = BetaGwentDuelDefinition(ids[i]);
        if (!BetaGwentDuelCollectible(ids[i]))
        { result.message = "Эта карта недоступна для составления колоды."; return result; }
        if (d.header.factionMask != 1 && (d.header.factionMask & faction) == 0)
        { result.message = "Карта принадлежит другой фракции."; return result; }
        if (d.header.tierMask == 8) result.gold += 1;
        else if (d.header.tierMask == 4) result.silver += 1;
        else if (d.header.tierMask == 2) result.bronze += 1;
        else { result.message = "Лидер и создаваемые карты не входят в состав колоды."; return result; }
        if (d.header.typeMask == 4) result.units += 1; else result.specials += 1;
        copies = 0;
        for (j = 0; j < ids.Size(); j += 1) if (ids[j] == ids[i]) copies += 1;
        limit = 1; if (d.header.tierMask == 2) limit = 3;
        if (copies > limit) { result.message = "Превышен лимит копий: " + d.title; return result; }
    }
    if (result.gold > 4) { result.message = "Можно выбрать до4 золотых карт."; return result; }
    if (result.silver > 6) { result.message = "Можно выбрать до6 серебряных карт."; return result; }
    if (ids.Size() < 25) { result.message = "Добавьте ещё " + (25 - ids.Size()) + " карт. Минимум 25, максимум 40."; return result; }
    result.valid = true; result.message = "Колода готова к игре."; return result;
}

class CBetaGwentDeckDraft extends IScriptable
{
    public var cards : array<int>;
    public var title : string;
    public var faction, leader, slot : int;
    public var limitedCollection : bool;
    public function Copies(id : int) : int
    { var i, count : int; for (i = 0; i < cards.Size(); i += 1) if (cards[i] == id) count += 1; return count; }
    public function Validation() : SBetaGwentDeckValidation
    {
        var result : SBetaGwentDeckValidation;var player : W3PlayerWitcher;
        result=BetaGwentValidateDeck(cards,faction,leader);player=(W3PlayerWitcher)thePlayer;
        if(result.valid && limitedCollection && (!player || !player.BetaGwentOwnsDeck(cards,leader))) {
            result.valid=false;result.message="В коллекции недостаточно копий карт этой колоды.";
        }
        return result;
    }
    public function CanAdd(id : int) : bool
    {
        var d : SBetaGwentDuelDefinition; var i, gold, silver : int;var player : W3PlayerWitcher;
        player=(W3PlayerWitcher)thePlayer;
        if(limitedCollection && (!player || Copies(id)>=player.BetaGwentOwned(id)))return false;
        if (cards.Size() >= 40 || !BetaGwentDuelCollectible(id)) return false;
        d = BetaGwentDuelDefinition(id);
        if (d.header.factionMask != 1 && (d.header.factionMask & faction) == 0) return false;
        if ((d.header.tierMask == 2 && Copies(id) >= 3) || (d.header.tierMask != 2 && Copies(id) >= 1)) return false;
        for (i = 0; i < cards.Size(); i += 1)
        { d = BetaGwentDuelDefinition(cards[i]); if (d.header.tierMask == 8) gold += 1; if (d.header.tierMask == 4) silver += 1; }
        d = BetaGwentDuelDefinition(id);
        return (d.header.tierMask != 8 || gold < 4) && (d.header.tierMask != 4 || silver < 6);
    }
    public function Change(id : int, amount : int) : bool
    {
        var i : int;
        if (amount == 1 && CanAdd(id)) { cards.PushBack(id); return true; }
        if (amount == -1)
            for (i = cards.Size() - 1; i >= 0; i -= 1)
                if (cards[i] == id) { cards.Erase(i); return true; }
        return false;
    }
}

class CBetaGwentDeckLibrary extends IScriptable
{
    private var slots : array<CBetaGwentDeckDraft>;
    private var unlimitedCollection : bool;
    public function Initialize(practice : bool)
    {
        var player : W3PlayerWitcher; var draft : CBetaGwentDeckDraft; var slot : int;
        unlimitedCollection=practice;slots.Clear(); player = (W3PlayerWitcher)thePlayer;
        if(player)player.BetaGwentEnsureCollection();
        for (slot = 1; slot <= 13; slot += 1)
        {
            draft = new CBetaGwentDeckDraft in this; draft.slot = slot;draft.limitedCollection=!unlimitedCollection;
            if (!player || !player.BetaGwentLoadDeck(slot, draft.cards, draft.title, draft.faction, draft.leader)) draft = NULL;
            slots.PushBack(draft);
        }
    }
    public function Preferred() : int
    {
        var player : W3PlayerWitcher; var ids : array<int>; var id, leader : int;
        player = (W3PlayerWitcher)thePlayer;
        if (player) { id = player.BetaGwentPreferredDeck(); if (Resolve(id, ids, leader) && (unlimitedCollection || player.BetaGwentOwnsDeck(ids,leader))) return id; }
        if(unlimitedCollection)return 3;return 16;
    }
    public function Remember(id : int)
    { var player : W3PlayerWitcher; player = (W3PlayerWitcher)thePlayer; if (player) player.BetaGwentRememberDeck(id); }
    public function Get(id : int) : CBetaGwentDeckDraft
    {
        if (slots.Size() != 13) return NULL;
        if (id >= 16 && id <= 20) return slots[id - 8];
        if (id < 1001 || id > 1008) return NULL; return slots[id - 1001];
    }
    public function FirstEmpty() : int
    { var i : int; for (i = 0; i < 8 && i < slots.Size(); i += 1) if (!slots[i]) return i + 1; return 0; }
    public function Edit(id : int) : CBetaGwentDeckDraft
    {
        var draft, storedDeck : CBetaGwentDeckDraft; var preset : SBetaGwentDuelPreset; var i : int; var leaderDefinition : SBetaGwentDuelDefinition;
        storedDeck = Get(id); draft = new CBetaGwentDeckDraft in this;draft.limitedCollection=!unlimitedCollection;
        if (storedDeck)
        {
            draft.slot = storedDeck.slot; draft.faction = storedDeck.faction; draft.leader = storedDeck.leader; draft.title = storedDeck.title;
            for (i = 0; i < storedDeck.cards.Size(); i += 1) draft.cards.PushBack(storedDeck.cards[i]); return draft;
        }
        if (id >= 16 && id <= 20) draft.slot = id - 7; else draft.slot = FirstEmpty();
        if (draft.slot == 0) return NULL;
        preset = BetaGwentDuelPreset(BetaGwentStarterPreset(2));
        draft.faction = 2; draft.leader = preset.leaderTemplateId; draft.title = "Моя колода " + draft.slot;
        if (id != 0)
        {
            preset = BetaGwentDuelPreset(id); if (preset.id == 0) return NULL;
            BetaGwentDuelPresetDeck(id, draft.cards); draft.leader = preset.leaderTemplateId; leaderDefinition = BetaGwentDuelDefinition(draft.leader); draft.faction = leaderDefinition.header.factionMask;
            draft.title = StrLeft(preset.title,48);
        }
        return draft;
    }
    public function Save(draft : CBetaGwentDeckDraft, title : string) : bool
    {
        var player : W3PlayerWitcher; var validation : SBetaGwentDeckValidation;
        if (!draft || StrLen(title) > 48) return false;
        validation = draft.Validation(); if (!validation.valid) return false;
        player = (W3PlayerWitcher)thePlayer; if (!player) return false;
        if (title == "") title = "Моя колода " + draft.slot;
        if (!player.BetaGwentStoreDeck(draft.slot, draft.cards, title, draft.faction, draft.leader)) return false;
        Initialize(unlimitedCollection); return true;
    }
    public function Resolve(id : int, out cards : array<int>, out leader : int) : bool
    {
        var draft : CBetaGwentDeckDraft; var preset : SBetaGwentDuelPreset; var validation : SBetaGwentDeckValidation; var i : int;
        cards.Clear(); draft = Get(id);
        if (draft)
        {
            validation = draft.Validation(); if (!validation.valid) return false;
            for (i = 0; i < draft.cards.Size(); i += 1) cards.PushBack(draft.cards[i]); leader = draft.leader; return true;
        }
        preset = BetaGwentDuelPreset(id); if (preset.id == 0) return false;
        leader = preset.leaderTemplateId; return BetaGwentDuelPresetDeck(id, cards);
    }
    public function ResolveOpponent(id : int, out cards : array<int>, out leader : int) : bool
    {
        var preset : SBetaGwentDuelPreset;
        if (id >= 1001 && id <= 1008) return Resolve(id, cards, leader);
        cards.Clear(); preset = BetaGwentDuelPreset(id); if (preset.id == 0) return false;
        leader = preset.leaderTemplateId; return BetaGwentDuelPresetDeck(id, cards);
    }
}
