// Concrete row abilities: Frost, Fog, Rain, Drought, RaghNarRoog, SkelligeStorm, GoldenFroth.
// One row token: original Add/Set both replace the existing row token.
class CBetaGwentDuelWeather extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var game : CBetaGwentDuelSession;
    public var hazards : array<int>;
    public var dreamRows : array<int>;
    public function Initialize(owner : CBetaGwentDuelSession)
    {
        var i : int; game = owner; hazards.Clear(); dreamRows.Clear();
        for (i = 0; i < 6; i += 1) hazards.PushBack(0);
    }
    private function Slot(side : int, row : int) : int
    {
        var ordinal : int;
        if ((side != 1 && side != 2) || (row != 1 && row != 2 && row != 4)) return -1;
        if (row == 2) ordinal = 1; else if (row == 4) ordinal = 2;
        return (side - 1) * 3 + ordinal;
    }
    public function Token(side : int, row : int) : int
    { var index : int; index = Slot(side, row); if (index < 0) return 0; return hazards[index]; }
    public function ApplyHazard(side : int, row : int, token : int) : bool
    {
        var index, previous : int; index = Slot(side, row);
        if (index < 0 || (token != 1 && token != 2 && token != 4 && token != 16 && token != 32 && token != 64 && token != 128 && token != 256 && token != 512 && token != 1024 && token != 2048)) return false;
        previous = hazards[index]; hazards[index] = token;
        game.RecordRowVisual(side, row, "Эффект наложен на ряд");
        // Add token fires AfterChangedLocationToken: contact hazards hit existing cards too.
        if (token == 512 || token == 2048) ContactRow(side, row, token);
        game.MonsterWeatherChanged(side, row, previous, token);
        BetaGwentLog("DUEL_WEATHER_APPLY side=" + side + " row=" + row + " token=" + token + " previous=" + previous); return true;
    }
    public function ClearRow(side : int, row : int)
    {
        var index, previous : int; index = Slot(side, row); if (index < 0) return;
        previous = hazards[index]; hazards[index] = 0;
        if (previous != 0) game.RecordRowVisual(side, row, "Архигрифон: свой ряд очищен");
        BetaGwentLog("DUEL_ROW_CLEAR side=" + side + " row=" + row + " previous=" + previous);
    }
    public function RemoveBoons(side : int, row : int)
    {
        var index, token : int; index = Slot(side, row); if (index < 0) return;
        token = hazards[index]; if ((token & 384) == 0) return;
        hazards[index] = token - (token & 384); game.RecordRowVisual(side, row, "Благо снято");
        BetaGwentLog("DUEL_BOON_REMOVE side=" + side + " row=" + row + " previous=" + token);
    }
    public function Reset()
    { var i : int; for (i = 0; i < hazards.Size(); i += 1) hazards[i] = 0; dreamRows.Clear(); }
    private function ContactRow(side : int, row : int, token : int)
    {
        var cards : array<CBetaGwentDuelCard>; var ids : array<int>; var i, templateId : int; var s : SBetaGwentCardSnapshot;
        game.GetZoneCards(side, row, cards);
        for (i = 0; i < cards.Size(); i += 1) { s = cards[i].Snapshot(); ids.PushBack(s.instanceId); }
        templateId = 200228; if (token == 2048) templateId = 200067;
        game.QueueRowAbility(8, token, side, row, templateId, ids);
    }
    public function Contact(card : CBetaGwentDuelCard)
    {
        var s : SBetaGwentCardSnapshot; var token, templateId : int; var ids : array<int>;
        if (!card) return; s = card.Snapshot(); if ((s.locationMask & 7) == 0) return;
        token = Token(s.positionPlayerId, s.locationMask); if (token != 512 && token != 2048) return;
        templateId = 200228; if (token == 2048) templateId = 200067;
        ids.PushBack(s.instanceId); game.QueueRowAbility(8, token, s.positionPlayerId, s.locationMask, templateId, ids);
    }
    public function CaptureDreamRows()
    {
        var i : int; dreamRows.Clear();
        // One global BoardManager graph: BeforeTurn priority0, all players/active rows.
        for (i = 0; i < hazards.Size(); i += 1) if (hazards[i] == 1024) dreamRows.PushBack(i);
        BetaGwentLog("DUEL_DREAM_CAPTURE rows=" + dreamRows.Size());
    }
    public function AfterPlayed(card : CBetaGwentDuelCard)
    {
        var s : SBetaGwentCardSnapshot; var i : int; var active : bool;
        if (!card) return; s = card.Snapshot();
        if (s.runtimeTemplate.typeMask != 2 || s.runtimeTemplate.templateId == 201637) return;
        for (i = 0; i < hazards.Size(); i += 1) if (hazards[i] == 1024) active = true;
        if (!active || dreamRows.Size() == 0) return;
        game.QueueRowAbility(9, 1024, 0, 0, 201637, dreamRows);
    }
    public function ResolveRowAbility(item : CBetaGwentDuelEvent)
    {
        var i, j, slot, side, row, amount : int; var target : CBetaGwentDuelCard;
        var cards : array<CBetaGwentDuelCard>; var ids : array<int>; var s : SBetaGwentCardSnapshot;
        if (item.kind == 8)
        {
            amount = DamageFor(item.source.positionPlayerId, item.source.locationMask, item.rowToken);
            for (i = 0; i < item.rowTargets.Size(); i += 1)
            {
                target = game.FindCard(item.rowTargets[i]); if (!target) continue; s = target.Snapshot();
                if ((s.tokenMask & 8) != 0 || (s.locationMask & 7) == 0 || s.isWaitingToDie) continue;
                game.QueuePower(target, -amount, false);
                BetaGwentLog("DUEL_ROW_CONTACT token=" + item.rowToken + " target=" + s.instanceId + " damage=" + amount);
            }
            return;
        }
        // Stored LocationList is not re-filtered for token1024; remove ONLY Dream.
        for (i = 0; i < item.rowTargets.Size(); i += 1)
        {
            slot = item.rowTargets[i]; side = 1; if (slot >= 3) side = 2;
            row = 1; if (slot % 3 == 1) row = 2; else if (slot % 3 == 2) row = 4;
            game.RecordRowVisual(side, row, "Мечта дракона: взрыв");
            game.GetZoneCards(side, row, cards);
            for (j = 0; j < cards.Size(); j += 1) { s = cards[j].Snapshot(); if ((s.tokenMask & 8) == 0 && !s.isWaitingToDie) ids.PushBack(s.instanceId); }
            if (hazards[slot] == 1024) hazards[slot] = 0;
        }
        amount = BetaGwentDuelRowAmount(1024);
        for (i = 0; i < ids.Size(); i += 1) game.QueuePower(game.FindCard(ids[i]), -amount, false);
        BetaGwentLog("DUEL_DREAM_EXPLODE rows=" + item.rowTargets.Size() + " targets=" + ids.Size() + " damage=" + amount);
    }
    public function Damage(side : int, row : int) : int
    { return DamageFor(side, row, Token(side, row)); }
    // Harmful part only: Golden Froth (128) and token 256 boost the row's units.
    public function Hazard(side : int, row : int) : int
    { if ((Token(side, row) & 384) != 0) return 0; return Damage(side, row); }
    public function Boon(side : int, row : int) : int
    { if ((Token(side, row) & 384) == 0) return 0; return Damage(side, row); }
    public function DamageFor(side : int, row : int, token : int) : int
    {
        var cards : array<CBetaGwentDuelCard>; var i, total, templateId : int;
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        if (token == 1) templateId = 113302; else if (token == 2) templateId = 113305;
        else if (token == 4) templateId = 113312;
        else if (token == 16) templateId = 200018; else if (token == 32) templateId = 113101;
        else if (token == 64) templateId = 113203; else if (token == 128) templateId = 201749;
        else if (token == 256 || token == 512 || token == 1024 || token == 2048) return BetaGwentDuelRowAmount(token);
        else return 0;
        d = BetaGwentDuelDefinition(templateId); total = d.amount;
        if (token != 1) return total;
        game.GetZoneCards(BetaGwentOpponentId(side), row, cards);
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].Snapshot();
            if (s.runtimeTemplate.templateId == 132310 && !s.isWaitingToDie && (s.tokenMask & 4) == 0) total += 1;
        }
        return total;
    }
    public function BeforeTurn(side : int)
    {
        var row, i, extreme, targetId, amount, token, count : int;
        var cards : array<CBetaGwentDuelCard>; var candidates, targets : array<int>;
        var s : SBetaGwentCardSnapshot; var target : CBetaGwentDuelCard; var definition : SBetaGwentDuelDefinition;
        // Original priorities -5,-10,-15: Melee, Ranged, Siege.
        for (row = 1; row <= 4; row *= 2)
        {
            token = Token(side, row); if (token == 0 || token == 512 || token == 1024 || token == 2048) continue;
            game.GetZoneCards(side, row, cards); candidates.Clear(); targets.Clear();
            extreme = 2147483647; if (token == 2 || token == 32) extreme = (-2147483647 - 1);
            for (i = 0; i < cards.Size(); i += 1)
            {
                s = cards[i].Snapshot(); if (s.isWaitingToDie) continue;
                // Storm slices the physical row before filtering each slice for Ambush.
                if (token == 64) { candidates.PushBack(s.instanceId); continue; }
                if ((s.tokenMask & 8) != 0) continue;
                if (token == 256)
                { definition = cards[i].Definition(); if ((definition.unitTraits & 288) != 0) candidates.PushBack(s.instanceId); continue; }
                if (token == 4 || token == 64 || token == 128) { candidates.PushBack(s.instanceId); continue; }
                if (((token == 1 || token == 16) && s.power.currentPower < extreme) || ((token == 2 || token == 32) && s.power.currentPower > extreme))
                { candidates.Clear(); extreme = s.power.currentPower; }
                if (s.power.currentPower == extreme) candidates.PushBack(s.instanceId);
            }
            if (candidates.Size() == 0) continue;
            if (token == 64)
            { count = Min(3, candidates.Size()); for (i = 0; i < count; i += 1) targets.PushBack(candidates[i]); }
            else if (token == 4 || token == 128)
            {
                // Shuffle FULL eligible list, then range [0,2), no duplicate targets.
                game.ShuffleIds(candidates); count = Min(2, candidates.Size());
                for (i = 0; i < count; i += 1) targets.PushBack(candidates[i]);
            }
            else
            {
                // HighestLevel traverses stable ascending power order backwards.
                // Thus Fog tie order is reverse row order; Frost is forward.
                i = game.RandomIndex(candidates.Size());
                if (token == 2 || token == 32) i = candidates.Size() - 1 - i;
                targets.PushBack(candidates[i]);
            }
            amount = Damage(side, row);
            // Presentation source is the affected weather row, never an RNG draw.
            if (token == 1) game.SetVisualSource(0, 113302, side, row);
            else if (token == 2) game.SetVisualSource(0, 113305, side, row);
            else if (token == 4) game.SetVisualSource(0, 113312, side, row);
            else if (token == 16) game.SetVisualSource(0, 200018, side, row);
            else if (token == 32) game.SetVisualSource(0, 113101, side, row);
            else if (token == 64) game.SetVisualSource(0, 113203, side, row);
            else if (token == 256) game.SetVisualSource(0, 200067, side, row);
            else game.SetVisualSource(0, 201749, side, row);
            for (i = 0; i < targets.Size(); i += 1)
            {
                targetId = targets[i]; target = game.FindCard(targetId);
                if (token == 64) { s = target.Snapshot(); if ((s.tokenMask & 8) != 0) continue; }
                if (token == 64) { if (i == 0) amount = 2; else amount = 1; }
                if (token == 128 || token == 256) game.QueuePower(target, amount, false); else game.QueuePower(target, -amount, false);
                BetaGwentLog("DUEL_WEATHER_TICK side=" + side + " row=" + row + " token=" + token + " target=" + targetId + " damage=" + amount);
            }
            // Complete the multi-target damage before draining deaths.
            game.FlushDeaths();
            game.SetVisualSource(0, 0, 0, 0);
        }
    }
    public function ClearSkies(side : int, boost : int)
    {
        var row, i : int; var cards : array<CBetaGwentDuelCard>; var damaged : array<CBetaGwentDuelCard>;
        var s : SBetaGwentCardSnapshot;
        // Snapshot damaged allies under hazards BEFORE clearing, boost AFTER.
        for (row = 1; row <= 4; row *= 2)
        {
            if (Token(side, row) == 0 || (Token(side, row) & 384) != 0) continue;
            game.GetZoneCards(side, row, cards);
            for (i = 0; i < cards.Size(); i += 1)
            {
                s = cards[i].Snapshot();
                if (!s.isWaitingToDie && s.power.currentPower < s.power.basePower + s.power.permanentPower) damaged.PushBack(cards[i]);
            }
        }
        for (row = 1; row <= 4; row *= 2)
        { if ((Token(side, row) & 384) == 0) hazards[Slot(side, row)] = 0; }
        game.RecordRowVisual(side, 0, "Чистое небо: погода снята");
        for (i = 0; i < damaged.Size(); i += 1) game.QueuePower(damaged[i], boost, false);
        BetaGwentLog("DUEL_WEATHER_CLEAR side=" + side + " boosted=" + damaged.Size() + " boost=" + boost);
    }
    public function ClearValue(side : int, boost : int, optional immediate : bool) : int
    {
        var row, i, total, targets : int; var cards : array<CBetaGwentDuelCard>; var s : SBetaGwentCardSnapshot;
        for (row = 1; row <= 4; row *= 2)
        {
            if (Token(side, row) == 0 || (Token(side, row) & 384) != 0) continue;
            game.GetZoneCards(side, row, cards); targets = Min(1, cards.Size());
            if (Token(side, row) == 4) targets = Min(2, cards.Size());
            if (Token(side, row) == 64) { if(!immediate)total += (Min(3, cards.Size()) + Min(1, cards.Size())) * 2; targets = 0; }
            if(!immediate)total += Damage(side, row) * targets * 2;
            for (i = 0; i < cards.Size(); i += 1)
            { s = cards[i].Snapshot(); if (!s.isWaitingToDie && s.power.currentPower < s.power.basePower + s.power.permanentPower) total += boost; }
        }
        return total;
    }
}
