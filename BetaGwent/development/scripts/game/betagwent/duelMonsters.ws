// Concrete pinned Beta 0.9.24 Monster graphs; display choices never become played cards.
class CBetaGwentDuelMonsters extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var game : CBetaGwentDuelSession;
    public var north : CBetaGwentDuelNorth;
    public var nilf : CBetaGwentDuelNilf;
    public var neutral : CBetaGwentDuelNeutral;
    public var skellige : CBetaGwentDuelSkellige;
    public var scoia : CBetaGwentDuelScoia;
    public function Initialize(owner : CBetaGwentDuelSession) { game = owner;neutral=new CBetaGwentDuelNeutral in this;neutral.Initialize(owner); skellige=new CBetaGwentDuelSkellige in this;skellige.Initialize(owner); north = new CBetaGwentDuelNorth in this; north.Initialize(owner); nilf = new CBetaGwentDuelNilf in this; nilf.Initialize(owner); scoia=new CBetaGwentDuelScoia in this;scoia.Initialize(owner); }
    private function Query(side : int, locations : int, tiers : int, ignore : int, traits : int, out ids : array<int>, optional types : int)
    {
        var cards : array<SBetaGwentDevelopmentCard>; var s : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition; var i : int;
        ids.Clear(); if (types == 0) types = 4; game.GetCards(cards);
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].card; d = BetaGwentDuelDefinition(s.runtimeTemplate.templateId);
            if (side != 0 && s.positionPlayerId != side) continue;
            if ((s.locationMask & locations) == 0 || (s.runtimeTemplate.typeMask & types) == 0 || (s.runtimeTierMask & tiers) == 0
                || s.isWaitingToDie || (s.tokenMask & ignore) != 0 || (traits != 0 && (d.unitTraits & traits) == 0)) continue;
            ids.PushBack(s.instanceId);
        }
    }
    private function EnemyRandom(source : CBetaGwentDuelCard, amount : int)
    {
        var ids : array<int>; var s : SBetaGwentCardSnapshot;
        s = source.Snapshot(); Query(BetaGwentOpponentId(s.positionPlayerId), 7, 15, 8, 0, ids);
        if (ids.Size() > 0) game.MonsterPower(source, game.FindCard(ids[game.RandomIndex(ids.Size())]), -amount);
    }
    private function Strengthen(source : CBetaGwentDuelCard, traits : int, amount : int, locations : int, ignore : int)
    {
        var ids : array<int>; var s : SBetaGwentCardSnapshot; var i : int;
        s = source.Snapshot(); Query(s.positionPlayerId, locations, 15, ignore, traits, ids);
        for (i = 0; i < ids.Size(); i += 1) if (ids[i] != s.instanceId) game.MonsterOperation(source, game.FindCard(ids[i]), 12, amount, locations);
    }
    private function RequestTargets(source : CBetaGwentDuelCard)
    {
        var ids, deck, valid : array<int>; var s, t, copy : SBetaGwentCardSnapshot;
        var d, td : SBetaGwentDuelDefinition; var i, j, side, zones, traits, tiers, ignore, kind : int;
        s = source.Snapshot(); d = source.Definition(); side = 0; zones = 7; traits = d.pileTraitMask; tiers = d.targetTiers; ignore = d.targetIgnore; kind = 0;
        if (d.targetSide == 1) side = s.positionPlayerId; else if (d.targetSide == 2) side = BetaGwentOpponentId(s.positionPlayerId);
        if (d.specialMode == 20) { zones = 8; kind = 2; }
        if (d.specialMode == 21 || d.specialMode == 24) { zones = 32; kind = 2; }
        if (d.specialMode == 25 || d.specialMode == 29) { zones = 16; kind = 2; }
        if (d.specialMode == 27) { zones = 16; traits = 1024; tiers = 6; ignore = 0; side = s.positionPlayerId; kind = 2; }
        if (d.specialMode == 22 && source.monsterStage == 1) side = BetaGwentOpponentId(s.positionPlayerId);
        if (d.specialMode == 23 || d.specialMode == 24) Query(s.positionPlayerId, 16, 2, 0, 0, deck);
        Query(side, zones, tiers, ignore, traits, ids, d.targetTypes);
        for (i = 0; i < ids.Size(); i += 1)
        {
            t = game.FindCard(ids[i]).Snapshot();
            if (d.specialMode == 22 && source.monsterStage == 0 && t.instanceId == s.instanceId) continue;
            if ((d.specialMode == 16 || d.specialMode == 17 || d.specialMode == 18 || d.specialMode == 32) && t.locationMask == s.locationMask) continue;
            if((d.specialMode==16 || d.specialMode==17 || d.specialMode==18 || d.specialMode==32) && game.CountLocation(t.positionPlayerId,s.locationMask)>=9)continue;
            if (d.specialMode == 23 || d.specialMode == 24)
            {
                if (t.runtimeTemplate.templateId == 200026 && d.specialMode == 23) continue;
                for (j = 0; j < deck.Size(); j += 1)
                { copy = game.FindCard(deck[j]).Snapshot(); if (copy.runtimeTemplate.templateId == t.runtimeTemplate.templateId) break; }
                if (j == deck.Size()) continue;
            }
            if (source.monsterIds.Contains(ids[i]) && d.specialMode == 18) continue;
            valid.PushBack(ids[i]);
        }
        if (d.specialMode == 25 || d.specialMode == 27) game.ShuffleIds(valid);
        if (valid.Size() == 0) { Select(source, 0); return; }
        game.MonsterRequest(source, valid, kind, d.targetMinimum, 1);
    }
    public function Played(source : CBetaGwentDuelCard)
    {
        var d : SBetaGwentDuelDefinition; var s : SBetaGwentCardSnapshot;
        var ids, other : array<int>; var i, row : int;
        if (source.MonsterMode() >= 800) {neutral.Played(source);return;}
        if (source.MonsterMode() >= 600) {skellige.Played(source);return;}
        if (source.MonsterMode() >= 500) { scoia.Played(source); return; }
        if (source.MonsterMode() >= 200) { nilf.Played(source); return; }
        if (source.MonsterMode() >= 100) { north.Played(source); return; }
        d = source.Definition(); s = source.Snapshot(); source.monsterStage = 0; source.monsterIds.Clear();
        if (d.header.templateId == 200534) { source.monsterOnce = 1; source.monsterStored = 0; }
        source.monsterRemaining = d.specialCount;
        BetaGwentLog("DUEL_MONSTER_PLAY template=" + d.header.templateId + " mode=" + d.specialMode);
        if (d.specialMode == 1 || d.specialMode == 2)
        {
            if (d.specialMode == 1) { s.locationMask = 1; s.locationIndex = -3; }
            else s.locationIndex += 1;
            game.QueueSpawn(s, d.deploySpawnTemplate, d.deploySpawnCount);
            if (d.specialMode == 1) { s = source.Snapshot(); game.MonsterWeather(BetaGwentOpponentId(s.positionPlayerId), s.locationMask, 2); }
            game.MonsterComplete(source); return;
        }
        if (d.specialMode == 3)
        { Strengthen(source, d.pileTraitMask, d.amount, d.pileLocation, d.targetIgnore); game.MonsterComplete(source); return; }
        if (d.specialMode == 4)
        {
            Query(BetaGwentOpponentId(s.positionPlayerId), s.locationMask, 15, 8, 0, ids); game.ShuffleIds(ids);
            for (i = 0; i < ids.Size() && i < d.specialCount; i += 1) game.MonsterPower(source, game.FindCard(ids[i]), -d.amount);
            game.MonsterComplete(source); return;
        }
        if (d.specialMode == 12) { game.MonsterCreate(source, d.playTemplateId); return; }
        if (d.specialMode == 13) { EnemyRandom(source, d.amount); game.MonsterComplete(source); return; }
        if (d.specialMode == 14 || d.specialMode == 33 || d.specialMode == 34 || d.specialMode == 35)
        {
            BetaGwentMonsterTemplates(d.header.templateId, ids);
            if (d.specialMode == 33 || d.specialMode == 34)
            { game.ShuffleIds(ids); while (ids.Size() > 3) ids.Erase(ids.Size() - 1); }
            game.MonsterRequest(source, ids, 1, d.targetMinimum, 1); return;
        }
        if (d.specialMode == 15) { DeployPassive(source); game.MonsterComplete(source); return; }
        if (d.specialMode == 19)
        {
            Query(s.positionPlayerId, 32, 6, 0, 0, ids, 12);
            for (i = 0; i < ids.Size(); i += 1) game.QueueConsume(source, game.FindCard(ids[i]));
            game.MonsterPower(source, source, ids.Size() * d.amount); game.MonsterComplete(source); return;
        }
        if (d.specialMode == 20) game.MonsterDraw(s.positionPlayerId, true);
        if (d.specialMode == 26) { PlayDeckCopy(source, d.playTemplateId); return; }
        if (d.specialMode == 27)
        { ids.PushBack(201666); ids.PushBack(201667); game.MonsterRequest(source, ids, 1, 1, 1); return; }
        if (d.specialMode == 28) { ResurrectDraug(source); return; }
        if (d.specialMode == 29)
        {
            Query(s.positionPlayerId, 16, 4, 0, 0, ids, 14);
            if (ids.Size() > 0) source.monsterIds.PushBack(ids[game.RandomIndex(ids.Size())]);
            Query(s.positionPlayerId, 16, 8, 0, 0, ids, 14);
            if (ids.Size() > 0) source.monsterIds.PushBack(ids[game.RandomIndex(ids.Size())]);
            game.MonsterRequest(source, source.monsterIds, 2, d.targetMinimum, 1); return;
        }
        if (d.specialMode == 30)
        {
            Query(s.positionPlayerId, 7, 15, 8, 4096, ids);
            for (i = 0; i < ids.Size(); i += 1) if (ids[i] != s.instanceId) game.MonsterPower(source, game.FindCard(ids[i]), d.amount);
            game.MonsterComplete(source); return;
        }
        if (d.specialMode == 32)
        {
            if (s.timerValue != 1) { game.MonsterComplete(source); return; }
            game.MonsterDraw(BetaGwentOpponentId(s.positionPlayerId), false);
        }
        if (d.header.templateId == 201700) { BeginHazardMove(source); return; }
        if (d.specialMode == 36) { game.QueueDeployCopies(source, d.deploySummonTemplate); game.MonsterComplete(source); return; }
        if (d.specialMode == 37) { game.MonsterPower(source, source, d.amount); game.MonsterComplete(source); return; }
        RequestTargets(source);
    }
    public function Select(source : CBetaGwentDuelCard, id : int)
    {
        var target : CBetaGwentDuelCard; var d, td : SBetaGwentDuelDefinition;
        var s, t, pos : SBetaGwentCardSnapshot; var ids : array<int>; var amount, i, row : int;
        if (source.MonsterMode() >= 800) {neutral.Select(source,id);return;}
        if (source.MonsterMode() >= 600) {skellige.Select(source,id);return;}
        if (source.MonsterMode() >= 500) { scoia.Select(source, id); return; }
        if (source.MonsterMode() >= 200) { nilf.Select(source, id); return; }
        if (source.MonsterMode() >= 100) { north.Select(source, id); return; }
        s = source.Snapshot(); d = source.Definition(); target = game.FindCard(id);
        if (d.specialMode == 18)
        {
            if (id != 0) source.monsterIds.PushBack(id);
            if (id != 0 && source.monsterIds.Size() < Min(d.specialCount,Max(0,9-game.CountLocation(BetaGwentOpponentId(s.positionPlayerId),s.locationMask)))) { RequestTargets(source); return; }
            CommitJotunn(source); return;
        }
        if (d.specialMode == 16 || d.specialMode == 17 || d.specialMode == 32)
        {
            if (target)
            {
                t = target.Snapshot(); game.QueueRelocation(target, t.positionPlayerId, s.locationMask, false);
                if (d.specialMode == 17)
                { amount = d.amount; if (game.MonsterIsHazard(game.WeatherToken(t.positionPlayerId, s.locationMask))) amount = d.conditionalDamage; game.MonsterPower(source, target, -amount); }
            }
            if (d.specialMode == 16) game.MonsterWeather(BetaGwentOpponentId(s.positionPlayerId), s.locationMask, 1);
            if (d.specialMode == 32) game.QueueTimer(source, 0, 1);
            game.MonsterComplete(source); return;
        }
        if (d.specialMode == 11)
        {
            if (target)
            { t = target.Snapshot(); game.QueueConsume(source, target); game.MonsterPower(source, source, t.power.currentPower); game.FlushDeaths(); }
            source.monsterRemaining -= 1; s = source.Snapshot();
            if (target && source.monsterRemaining > 0 && (s.locationMask & 7) != 0 && !s.isWaitingToDie) { RequestTargets(source); return; }
            game.MonsterComplete(source); return;
        }
        if (d.specialMode == 22)
        {
            if (source.monsterStage == 0)
            {
                if (!target) { game.MonsterComplete(source); return; }
                t = target.Snapshot(); source.monsterStored = t.power.currentPower; source.monsterStage = 1;
                game.QueueDestroy(target); game.FlushDeaths(); RequestTargets(source); return;
            }
            if (target) game.MonsterPower(source, target, -source.monsterStored);
            game.MonsterComplete(source); return;
        }
        if (d.specialMode == 27 && source.monsterStage == 0)
        {
            if (id == 201666) { Strengthen(source, 1024, d.amount, 31, 0); game.MonsterComplete(source); return; }
            if (id == 201667) { source.monsterStage = 1; RequestTargets(source); return; }
        }
        if (d.specialMode == 14 || d.specialMode == 33 || d.specialMode == 34 || d.specialMode == 35)
        { if (id != 0) game.MonsterCreate(source, id); else game.MonsterComplete(source); return; }
        if (!target) { ChildReturned(source); game.MonsterComplete(source); return; }
        t = target.Snapshot();
        if (d.specialMode == 5)
        { Query(s.positionPlayerId, 8, 14, 0, 4096, ids); game.MonsterPower(source, target, -d.amount - ids.Size() * d.conditionalDamage); }
        else if (d.specialMode == 6)
        { amount = d.amount; if (game.WeatherToken(t.positionPlayerId, t.locationMask) == 2048) amount = d.conditionalDamage; game.MonsterPower(source, target, -amount); }
        else if (d.specialMode == 7)
        {
            game.MonsterPower(source, target, -d.amount); game.FlushDeaths(); Query(BetaGwentOpponentId(s.positionPlayerId), 7, 15, 8, 0, ids);
            for (i = 0; i < ids.Size(); i += 1)
            { t = game.FindCard(ids[i]).Snapshot(); if (game.WeatherToken(t.positionPlayerId, t.locationMask) == 2048) game.MonsterPower(source, game.FindCard(ids[i]), -d.conditionalDamage); }
        }
        else if (d.specialMode == 8) game.QueueResetPower(source, target);
        else if (d.specialMode == 9) game.MonsterDeckCopies(s.positionPlayerId, t.runtimeTemplate.templateId, d.specialCount);
        else if (d.specialMode == 10) game.MonsterForceDeathwish(target);
        else if (d.specialMode == 20 || d.specialMode == 21)
        { game.QueueConsume(source, target); game.MonsterPower(source, source, t.power.currentPower); }
        else if (d.specialMode == 23) { PlayDeckCopy(source, t.runtimeTemplate.templateId); return; }
        else if (d.specialMode == 24)
        { game.QueueConsume(source, target); game.FlushDeaths(); PlayDeckCopy(source, t.runtimeTemplate.templateId); return; }
        else if (d.specialMode == 25 || d.specialMode == 27)
        { source.monsterStored = id; game.MonsterPlayExisting(source, target); return; }
        else if (d.specialMode == 29)
        { for (i = source.monsterIds.Size() - 1; i >= 0; i -= 1) if (source.monsterIds[i] == id) source.monsterIds.Erase(i); game.MonsterPlayExisting(source, target); return; }
        else if (d.specialMode == 31) game.MonsterDuel(source, target, 0, 0);
        game.MonsterComplete(source);
    }
    private function CommitJotunn(source : CBetaGwentDuelCard)
    {
        var i, amount : int; var target : CBetaGwentDuelCard; var s, t : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        s = source.Snapshot(); d = source.Definition(); amount = d.amount;
        if (game.WeatherToken(BetaGwentOpponentId(s.positionPlayerId), s.locationMask) == 1) amount = d.conditionalDamage;
        for (i = 0; i < source.monsterIds.Size(); i += 1)
        { target = game.FindCard(source.monsterIds[i]); if (target) { t = target.Snapshot(); game.QueueRelocation(target, t.positionPlayerId, s.locationMask, false); } }
        for (i = 0; i < source.monsterIds.Size(); i += 1) game.MonsterPower(source, game.FindCard(source.monsterIds[i]), -amount);
        game.MonsterComplete(source);
    }
    private function PlayDeckCopy(source : CBetaGwentDuelCard, templateId : int)
    {
        var ids, valid : array<int>; var i : int; var s, t : SBetaGwentCardSnapshot;
        s = source.Snapshot(); Query(s.positionPlayerId, 16, 14, 0, 0, ids, 14);
        for (i = 0; i < ids.Size(); i += 1) { t = game.FindCard(ids[i]).Snapshot(); if (t.runtimeTemplate.templateId == templateId) valid.PushBack(ids[i]); }
        if (valid.Size() == 0) { game.MonsterComplete(source); return; }
        game.MonsterPlayExisting(source, game.FindCard(valid[game.RandomIndex(valid.Size())]));
    }
    public function ChildReturned(source : CBetaGwentDuelCard) : bool
    {
        var d : SBetaGwentDuelDefinition; var child : CBetaGwentDuelCard; var s, t : SBetaGwentCardSnapshot; var i : int;
        if (source.MonsterMode() >= 800) return neutral.ChildReturned(source);
        if (source.MonsterMode() >= 600) return skellige.ChildReturned(source);
        if (source.MonsterMode() >= 500) return scoia.ChildReturned(source);
        if (source.MonsterMode() >= 200) return nilf.ChildReturned(source);
        if (source.MonsterMode() >= 100) return north.ChildReturned(source);
        d = source.Definition(); s = source.Snapshot(); child = source.TakePlayedChild();
        if (child)
        {
            t = child.Snapshot();
            if (d.header.templateId == 133302) game.MonsterPower(source, child, d.amount);
            if (d.specialMode == 27) game.MonsterOperation(source, child, 12, d.conditionalDamage, 7);
        }
        if (d.specialMode == 29)
        {
            for (i = source.monsterIds.Size() - 1; i >= 0; i -= 1) game.MonsterTopDeck(game.FindCard(source.monsterIds[i]));
            source.monsterIds.Clear();
        }
        return false;
    }
    public function AfterPlayed(child : CBetaGwentDuelCard)
    {
        var ids : array<int>; var i : int; var source : CBetaGwentDuelCard; var s, t : SBetaGwentCardSnapshot;
        if (!child) return; t = child.Snapshot(); Query(0, 7, 15, 12, 0, ids);
        for (i = 0; i < ids.Size(); i += 1)
        {
            source = game.FindCard(ids[i]); s = source.Snapshot();
            if (source.TemplateId() != 200534 || source.monsterOnce <= 0) continue;
            // Graph92 consumes its counter on the first AfterPlayed, before comparing the stored child.
            source.monsterOnce = 0;
            if (source.monsterStored == t.instanceId && (t.locationMask & 7) != 0 && !t.isWaitingToDie)
            { game.QueueConsume(source, child); game.MonsterPower(source, source, t.power.basePower); }
        }
    }
    private function ResurrectDraug(source : CBetaGwentDuelCard)
    {
        var ids : array<int>; var i, count : int; var s : SBetaGwentCardSnapshot;
        s = source.Snapshot(); Query(s.positionPlayerId, 32, 15, 0, 0, ids); game.ShuffleIds(ids);
        count = Max(0, 9 - game.CountLocation(s.positionPlayerId, s.locationMask));
        for (i = 0; i < ids.Size() && i < count; i += 1)
        { game.MonsterResurrect(source, game.FindCard(ids[i])); }
        game.MonsterComplete(source);
    }
    private function BeginHazardMove(source : CBetaGwentDuelCard)
    {
        var ids : array<int>; var row, side : int; var s : SBetaGwentCardSnapshot;
        s = source.Snapshot(); side = BetaGwentOpponentId(s.positionPlayerId);
        for (row = 1; row <= 4; row *= 2) if (game.MonsterIsHazard(game.WeatherToken(side, row))) ids.PushBack(row);
        if (ids.Size() == 0) { game.MonsterComplete(source); return; }
        game.MonsterRequest(source, ids, 3, 1, 1);
    }
    public function Row(source : CBetaGwentDuelCard, side : int, row : int)
    {
        var ids : array<int>; var next : int;
        if(source.MonsterMode()>=800){neutral.Row(source,side,row);return;}
        if(source.MonsterMode()>=600){skellige.Row(source,side,row);return;}
        if (source.MonsterMode() >= 200) { nilf.Row(source, side, row); return; }
        if (source.MonsterMode() >= 100) { north.Row(source, side, row); return; }
        if (source.monsterStage == 0)
        {
            source.monsterStored = row; source.monsterStage = 1;
            for (next = 1; next <= 4; next *= 2) if (next != row) ids.PushBack(next);
            game.MonsterRequest(source, ids, 3, 1, 1); return;
        }
        game.MonsterMoveWeather(side, source.monsterStored, row); game.MonsterComplete(source);
    }
    private function MoonContact(source : CBetaGwentDuelCard)
    {
        var s, pos : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        s = source.Snapshot(); d = source.Definition();
        if ((s.locationMask & 7) == 0 || game.WeatherToken(s.positionPlayerId, s.locationMask) != 256) return;
        if (d.header.templateId == 201600 && s.timerValue > 0)
        { game.MonsterPower(source, source, d.amount); game.QueueTimer(source, 0, 1); }
        if (d.header.templateId == 200114)
        { pos = s; game.QueueSpawn(pos, 132403, 1); pos.locationIndex = s.locationIndex + 2; game.QueueSpawn(pos, 132403, 1); }
    }
    private function DeployPassive(source : CBetaGwentDuelCard)
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        s = source.Snapshot(); d = source.Definition();
        if (d.header.templateId == 132108) game.QueueTimer(source, 2, d.timerPeriod);
        else if (d.header.templateId == 132201) game.QueueTimer(source, 2, d.specialCount);
        else if (d.header.templateId == 132212) source.monsterOnce = 1;
        else if (d.header.templateId == 201600 || d.header.templateId == 200114) MoonContact(source);
    }
    private function FrostContact(source : CBetaGwentDuelCard)
    {
        var side, row : int; var d : SBetaGwentDuelDefinition;
        if (source.monsterOnce <= 0) return; d = source.Definition();
        for (side = 1; side <= 2; side += 1) for (row = 1; row <= 4; row *= 2)
            if (game.WeatherToken(side, row) == 1) { source.monsterOnce = 0; game.MonsterPower(source, source, d.amount); return; }
    }
    public function ScoiaBeforePlayed(card : CBetaGwentDuelCard) : bool {return scoia.BeforePlayed(card);}
    public function ScoiaHistory(card : CBetaGwentDuelCard) {scoia.History(card);skellige.History(card);}
    public function AddedPowerChanged(card : CBetaGwentDuelCard, old : SBetaGwentCardSnapshot, current : SBetaGwentCardSnapshot){skellige.PowerChanged(card,old,current);}
    public function NilfTrigger(kind : int, cause : SBetaGwentCardSnapshot) { nilf.Trigger(kind,cause);skellige.Trigger(kind,cause);neutral.Trigger(kind,cause); }
    public function NilfReaction(source : CBetaGwentDuelCard, kind : int) { nilf.Reaction(source,kind); }
    public function Event(item : CBetaGwentDuelEvent)
    {
        var source, target : CBetaGwentDuelCard; var s, t, pos : SBetaGwentCardSnapshot;
        var d, td : SBetaGwentDuelDefinition; var ids, valid, rows : array<int>; var i, highest, kind, row : int;
        if (item.kind == 11) { north.Event(item); return; }
        source = game.FindCard(item.source.instanceId); if (!source) return; s = source.Snapshot(); d = source.Definition(); kind = item.rowToken;
        if (s.isWaitingToDie || (s.tokenMask & 12) != 0 || s.power.currentPower <= 0) return;
        if (kind != 8 && (s.locationMask & 7) == 0 && !((d.header.templateId == 132301 || d.header.templateId == 132315) && s.locationMask == 16)) return;
        if (kind == 1)
        {
            if (d.header.templateId == 132108 && s.timerValue > 0)
            {
                game.QueueTimer(source, 0, 1);
                if (s.timerValue == 1)
                {
                    Query(BetaGwentOpponentId(s.positionPlayerId), s.locationMask, 15, 8, 0, ids); highest = -1;
                    for (i = 0; i < ids.Size(); i += 1) { t = game.FindCard(ids[i]).Snapshot(); highest = Max(highest, t.power.currentPower); }
                    for (i = 0; i < ids.Size(); i += 1) { t = game.FindCard(ids[i]).Snapshot(); if (t.power.currentPower == highest) valid.PushBack(ids[i]); }
                    if (valid.Size() > 0) game.QueueRelocation(game.FindCard(valid[game.RandomIndex(valid.Size())]), s.positionPlayerId, s.locationMask, false);
                }
            }
            if (d.header.templateId == 200038)
            {
                for (row = 1; row <= 4; row *= 2) if (row != s.locationMask && game.CountLocation(s.positionPlayerId, row) < 9) rows.PushBack(row);
                if (rows.Size() > 0) game.QueueRelocation(source, s.positionPlayerId, rows[game.RandomIndex(rows.Size())], false);
                EnemyRandom(source, d.amount);
            }
        }
        else if (kind == 2)
        {
            Query(BetaGwentOpponentId(s.positionPlayerId), 7, 15, 8, 0, ids); highest = -1;
            for (i = 0; i < ids.Size(); i += 1) { t = game.FindCard(ids[i]).Snapshot(); highest = Max(highest, t.power.currentPower); }
            for (i = 0; i < ids.Size(); i += 1) { t = game.FindCard(ids[i]).Snapshot(); if (t.power.currentPower == highest) valid.PushBack(ids[i]); }
            if (valid.Size() > 0) game.MonsterDuel(source, game.FindCard(valid[game.RandomIndex(valid.Size())]), d.amount, d.addedArmor);
        }
        else if (kind == 3)
        {
            if (d.header.templateId == 132212 && item.cause.timerValue == 1) FrostContact(source);
            if ((d.header.templateId == 201600 || d.header.templateId == 200114) && item.cause.timerValue == 256
                && item.cause.positionPlayerId == s.positionPlayerId && item.cause.locationMask == s.locationMask) MoonContact(source);
            if (d.header.templateId == 132301 && item.cause.timerValue == 2 && item.cause.positionPlayerId != s.positionPlayerId)
            {
                Query(s.positionPlayerId, 16, 14, 0, 0, ids);
                for (i = 0; i < ids.Size(); i += 1) { t = game.FindCard(ids[i]).Snapshot(); if (t.runtimeTemplate.templateId == 132301) valid.PushBack(ids[i]); }
                if (valid.Size() > 0)
                { pos = s; pos.locationMask = item.cause.locationMask; pos.locationIndex = -3; game.MonsterSummon(pos, game.FindCard(valid[game.RandomIndex(valid.Size())])); }
            }
        }
        else if (kind == 4)
        {
            target = game.FindCard(item.cause.instanceId); if (!target) return; t = target.Snapshot(); td = target.Definition();
            if (d.header.templateId == 200301 && t.instanceId != s.instanceId && t.positionPlayerId == s.positionPlayerId && (t.locationMask & 7) != 0 && (td.unitTraits & 4096) != 0)
                game.MonsterPower(source, target, d.amount);
            if (t.instanceId == s.instanceId)
            {
                if ((d.header.templateId == 201600 || d.header.templateId == 200114) && (item.cause.locationMask & 7) != 0) MoonContact(source);
                if (d.header.templateId == 132212 && (item.cause.locationMask & 248) != 0) FrostContact(source);
                if (d.header.templateId == 200174 && (item.cause.locationMask & 184) != 0) game.QueueDeployCopies(source, 132304);
            }
            if (d.header.templateId == 132315 && item.cause.positionPlayerId == s.positionPlayerId && (item.cause.locationMask & 7) != 0 && t.locationMask == 32 && (td.unitTraits & 32) != 0)
            {
                Query(s.positionPlayerId, 16, 14, 0, 0, ids);
                for (i = 0; i < ids.Size(); i += 1) { t = game.FindCard(ids[i]).Snapshot(); if (t.runtimeTemplate.templateId == 132315) valid.PushBack(ids[i]); }
                if (valid.Size() > 0) { pos = item.cause; game.MonsterSummon(pos, game.FindCard(valid[game.RandomIndex(valid.Size())])); }
            }
        }
        else if (kind == 5)
        { if (d.header.templateId == 132404) EnemyRandom(source, d.amount); else if (d.header.templateId == 200174) game.QueueDeployCopies(source, 132304); }
        else if (kind == 6 && s.timerValue > 0 && item.cause.positionPlayerId == s.positionPlayerId)
        { game.QueueTimer(source, 0, 1); game.QueueRandomRowSpawn(s, d.deploySpawnTemplate, 1); }
        else if (kind == 7 && item.cause.instanceId != s.instanceId) game.MonsterPower(source, source, -d.conditionalDamage);
    }
    public function Deathwish(source : CBetaGwentDuelCard, fromPosition : SBetaGwentCardSnapshot)
    {
        var ids : array<int>; var d : SBetaGwentDuelDefinition;
        d = source.Definition(); Query(BetaGwentOpponentId(fromPosition.positionPlayerId), 7, 15, 8, 0, ids);
        if (ids.Size() > 0) game.MonsterPower(source, game.FindCard(ids[game.RandomIndex(ids.Size())]), -d.conditionalDamage);
    }
}
