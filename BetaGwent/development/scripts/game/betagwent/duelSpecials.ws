// Original special graphs, concrete consumers. No substitute generated-unit abilities.
class CBetaGwentDuelSpecials extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var game : CBetaGwentDuelSession;
    public var weather : CBetaGwentDuelWeather;
    public function Initialize(owner : CBetaGwentDuelSession, rows : CBetaGwentDuelWeather)
    { game = owner; weather = rows; }
    private function Eligible(s : SBetaGwentCardSnapshot, d : SBetaGwentDuelDefinition, optional shape : bool) : bool
    {
        var targetDefinition : SBetaGwentDuelDefinition;
        if (s.isWaitingToDie || (s.locationMask & 7) == 0 || s.runtimeTemplate.typeMask != 4) return false;
        // TargetsInShape is filtered for Ambush after selection, independently of anchor Ignore264.
        if (shape) return (s.tokenMask & 8) == 0;
        targetDefinition = BetaGwentDuelDefinition(s.runtimeTemplate.templateId);
        if ((targetDefinition.unitTraits & d.targetExcludedTraits) != 0) return false;
        return (s.runtimeTierMask & d.targetTiers) != 0 && (s.tokenMask & d.targetIgnore) == 0;
    }
    private function Gather(side : int, rowMask : int, d : SBetaGwentDuelDefinition, out ids : array<int>)
    {
        var player, row, i : int; var cards : array<CBetaGwentDuelCard>; var s : SBetaGwentCardSnapshot;
        ids.Clear();
        for (player = 1; player <= 2; player += 1)
        {
            if (side != 0 && side != player) continue;
            for (row = 1; row <= 4; row *= 2)
            {
                if ((row & rowMask) == 0) continue; game.GetZoneCards(player, row, cards);
                for (i = 0; i < cards.Size(); i += 1)
                { s = cards[i].Snapshot(); if (Eligible(s, d)) ids.PushBack(s.instanceId); }
            }
        }
    }
    private function DamageScore(s : SBetaGwentCardSnapshot, side : int, amount : int, optional bypass : bool) : int
    {
        var value : int; value = amount;
        if (!bypass) value = Max(0, value - s.power.armor);
        value = Min(value, s.power.currentPower); if (s.positionPlayerId == side) value = -value;
        return value;
    }
    private function BoostScore(s : SBetaGwentCardSnapshot, side : int, amount : int) : int
    { if (s.positionPlayerId == side) return amount; return -amount; }
    private function Strongest(ids : array<int>, out selected : array<int>)
    {
        var i, highest, swap : int; var s : SBetaGwentCardSnapshot; selected.Clear(); highest = -1;
        for (i = 0; i < ids.Size(); i += 1)
        {
            s = game.FindCard(ids[i]).Snapshot();
            if (s.power.currentPower > highest) { highest = s.power.currentPower; selected.Clear(); }
            if (s.power.currentPower == highest) selected.PushBack(ids[i]);
        }
        // Original HighestLevel walks stable ascending-power order backwards.
        for (i = 0; i < selected.Size() / 2; i += 1)
        { swap = selected[i]; selected[i] = selected[selected.Size() - 1 - i]; selected[selected.Size() - 1 - i] = swap; }
    }
    private function Amount(source : CBetaGwentDuelCard) : int
    {
        var d : SBetaGwentDuelDefinition; var s : SBetaGwentCardSnapshot;
        var cards : array<CBetaGwentDuelCard>; var i, amount : int;
        d = source.Definition(); amount = d.amount;
        if (d.header.templateId == 200224)
        {
            s = source.Snapshot(); game.GetZoneCards(s.positionPlayerId, 32, cards);
            for (i = 0; i < cards.Size(); i += 1)
            { s = cards[i].Snapshot(); if (s.runtimeTemplate.templateId == 200224) amount += 1; }
        }
        return amount;
    }
    public function Auto(source : CBetaGwentDuelCard)
    {
        var d, targetDefinition : SBetaGwentDuelDefinition; var s, target : SBetaGwentCardSnapshot;
        var ids, selected : array<int>; var side, row, i, count, amount : int;
        d = source.Definition(); s = source.Snapshot(); side = s.positionPlayerId;
        amount = Amount(source);
        if (d.specialMode == 19) { Mirror(source); return; }
        if (d.specialMode == 14)
        { for (row = 1; row <= 4; row *= 2) weather.ApplyHazard(BetaGwentOpponentId(side), row, d.specialToken); return; }
        if (d.specialMode == 4 || d.specialMode == 5)
        {
            if (d.specialMode == 5) side = BetaGwentOpponentId(side);
            for (row = 1; row <= 4; row *= 2)
            {
                Gather(side, row, d, ids); if (d.specialMode == 5) { Strongest(ids, selected); ids = selected; }
                if (ids.Size() == 0) continue;
                i = game.RandomIndex(ids.Size());
                if (d.specialMode == 4) game.QueuePower(game.FindCard(ids[i]), amount, false);
                else game.QueuePower(game.FindCard(ids[i]), -amount, false);
                // Foreach row completes its change before querying the next row.
                game.FlushDeaths();
            }
            return;
        }
        if (d.targetSide == 2) side = BetaGwentOpponentId(side);
        else if (d.targetSide == 0) side = 0;
        Gather(side, 7, d, ids);
        if (d.specialMode == 36)
        {
            // Cache the complete parity list before any queued power change.
            for (i = 0; i < ids.Size(); i += 1)
            { target = game.FindCard(ids[i]).Snapshot(); if (target.power.currentPower % 2 == d.specialToken) selected.PushBack(ids[i]); }
            for (i = 0; i < selected.Size(); i += 1) game.QueuePower(game.FindCard(selected[i]), -amount, false);
            return;
        }
        if (d.specialMode == 36)
        {
            // Cache the complete parity list before any queued power change.
            for (i = 0; i < ids.Size(); i += 1)
            { target = game.FindCard(ids[i]).Snapshot(); if (target.power.currentPower % 2 == d.specialToken) selected.PushBack(ids[i]); }
            for (i = 0; i < selected.Size(); i += 1) game.QueuePower(game.FindCard(selected[i]), -amount, false);
            return;
        }
        if (d.specialMode == 6)
        {
            Strongest(ids, selected);
            for (i = 0; i < selected.Size(); i += 1) game.QueueDestroy(game.FindCard(selected[i])); return;
        }
        count = ids.Size();
        if (d.specialMode == 2 || d.specialMode == 3)
        { game.ShuffleIds(ids); count = Min(count, d.specialCount); }
        for (i = 0; i < count; i += 1)
        {
            if (d.specialMode == 21) { target = game.FindCard(ids[i]).Snapshot(); targetDefinition = BetaGwentDuelDefinition(target.runtimeTemplate.templateId); if ((targetDefinition.unitTraits & 4) != 0) game.QueuePower(game.FindCard(ids[i]), amount, false); }
            else if (d.specialMode == 2) game.QueuePower(game.FindCard(ids[i]), amount, false);
            else game.QueuePower(game.FindCard(ids[i]), -amount, false);
        }
    }
    public function HandPower(side : int) : int
    {
        var cards : array<CBetaGwentDuelCard>; var s : SBetaGwentCardSnapshot; var i, result : int;
        game.GetZoneCards(side, 8, cards);
        for (i = 0; i < cards.Size(); i += 1)
        { s = cards[i].Snapshot(); if (s.runtimeTemplate.typeMask == 4 && (s.runtimeTierMask & 6) != 0) result = Max(result, s.power.basePower); }
        return result;
    }
    private function Mirror(source : CBetaGwentDuelCard)
    {
        var d : SBetaGwentDuelDefinition; var s : SBetaGwentCardSnapshot; var target : CBetaGwentDuelCard;
        var ids, selected : array<int>; var i, originalTarget, lowest, amount : int;
        d = source.Definition(); Gather(0, 7, d, ids); if (ids.Size() < 2) return;
        Strongest(ids, selected); originalTarget = selected[game.RandomIndex(selected.Size())];
        target = game.FindCard(originalTarget); s = target.Snapshot(); amount = Min(d.amount, s.power.currentPower);
        game.QueuePower(target, -amount, true); if (!game.FlushEffects()) return;
        // The source graph excludes the damaged ID before finding LowestLevel.
        Gather(0, 7, d, ids); selected.Clear(); lowest = 2147483647;
        for (i = 0; i < ids.Size(); i += 1)
        {
            if (ids[i] == originalTarget) continue; s = game.FindCard(ids[i]).Snapshot();
            if (s.power.currentPower < lowest) { lowest = s.power.currentPower; selected.Clear(); }
            if (s.power.currentPower == lowest) selected.PushBack(ids[i]);
        }
        if (selected.Size() > 0) game.QueuePower(game.FindCard(selected[game.RandomIndex(selected.Size())]), amount, false);
    }
    private function MirrorValue(d : SBetaGwentDuelDefinition, side : int) : int
    {
        var ids, selected : array<int>; var i, j, lowest, amount, value, transfer, count : int;
        var a, s : SBetaGwentCardSnapshot;
        Gather(0, 7, d, ids); if (ids.Size() < 2) return 0; Strongest(ids, selected);
        for (i = 0; i < selected.Size(); i += 1)
        {
            a = game.FindCard(selected[i]).Snapshot(); amount = Min(d.amount, a.power.currentPower);
            lowest = 2147483647; transfer = 0; count = 0;
            for (j = 0; j < ids.Size(); j += 1)
            {
                if (ids[j] == selected[i]) continue; s = game.FindCard(ids[j]).Snapshot();
                if (s.power.currentPower < lowest) { lowest = s.power.currentPower; transfer = 0; count = 0; }
                if (s.power.currentPower == lowest) { count += 1; transfer += BoostScore(s, side, amount); }
            }
            value += DamageScore(a, side, amount, true); if (count > 0) value += transfer / count;
        }
        return value / selected.Size();
    }
    public function Target(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    {
        var d, targetDefinition : SBetaGwentDuelDefinition; var a, s, t : SBetaGwentCardSnapshot;
        var cards : array<CBetaGwentDuelCard>; var i, offset : int;
        if (!target) return; d = source.Definition(); a = source.Snapshot(); t = target.Snapshot();
        if (d.specialMode == 18)
        {
            targetDefinition = target.Definition();
            if ((targetDefinition.unitTraits & 1) == 0)
            { game.QueuePower(target, -d.amount, false); if (!game.FlushEffects()) return; t = target.Snapshot(); if (t.isWaitingToDie || t.power.currentPower <= 0) return; }
            game.QueueSetPower(source, target, 25); return;
        }
        if (d.specialMode == 16 || d.specialMode == 17) { game.QueuePower(target, -d.amount, false); return; }
        if (d.specialMode == 12)
        {
            if (a.positionPlayerId == t.positionPlayerId) game.QueuePower(target, d.amount, false);
            else game.QueuePower(target, -d.amount, false); return;
        }
        if (d.specialMode == 11) { game.QueueResilienceToggle(source, target); return; }
        game.GetZoneCards(t.positionPlayerId, t.locationMask, cards);
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].Snapshot(); offset = s.locationIndex - t.locationIndex;
            if (offset < -d.specialRadius || offset > d.specialRadius || !Eligible(s, d, true)) continue;
            if (d.specialMode == 7) game.QueuePower(cards[i], d.amount, false);
            else if (d.specialMode == 8) game.QueuePower(cards[i], -d.amount, false);
        }
    }
    public function Row(source : CBetaGwentDuelCard, side : int, row : int)
    {
        var d : SBetaGwentDuelDefinition; var cards : array<CBetaGwentDuelCard>;
        var i : int; var s : SBetaGwentCardSnapshot; d = source.Definition();
        // Applying a token records its own row animation. White Frost must
        // show each adjacent row once, not a generic hit plus a second frost.
        if (d.specialMode != 15 && d.specialMode != 37) game.RecordRowVisual(side, row, d.title);
        if (d.specialMode == 20)
        {
            // Query physical ends first, filter Ambush afterwards. A lone unit is hit once.
            game.GetZoneCards(side, row, cards);
            if (cards.Size() == 0) return;
            s = cards[0].Snapshot(); if (!s.isWaitingToDie && (s.tokenMask & 8) == 0) game.QueuePower(cards[0], -d.amount, false);
            if (cards.Size() > 1) { s = cards[cards.Size() - 1].Snapshot(); if (!s.isWaitingToDie && (s.tokenMask & 8) == 0) game.QueuePower(cards[cards.Size() - 1], -d.amount, false); }
            return;
        }
        if (d.specialMode == 37) { weather.ApplyHazard(side, row, d.specialToken); return; }
        if (d.specialMode == 15)
        {
            weather.ApplyHazard(side, row, d.specialToken);
            if (d.specialCount == 2) weather.ApplyHazard(side, row * 2, d.specialToken); return;
        }
        game.GetZoneCards(side, row, cards);
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].Snapshot(); if (!Eligible(s, d)) continue;
            if (d.specialMode == 9) game.QueueMultiplyPower(source, cards[i], d.powerMultiplier);
            else if (d.specialMode == 10 && s.power.currentPower > s.power.basePower + s.power.permanentPower)
                game.QueueResetPower(source, cards[i]);
            else if (d.specialMode == 13) game.QueuePower(cards[i], -d.amount, false);
        }
        if (d.specialMode == 13) { game.FlushDeaths(); weather.RemoveBoons(side, row); }
    }
    public function TargetValue(d : SBetaGwentDuelDefinition, t : SBetaGwentCardSnapshot, side : int) : int
    {
        var cards : array<CBetaGwentDuelCard>; var i, offset, value : int; var s : SBetaGwentCardSnapshot;
        if (d.specialMode == 31 || d.specialMode == 32)
        {
            value = t.power.basePower + t.power.permanentPower;
            if (d.specialMode == 32)
            { if (d.powerMultiplier != 0) value = Max(value, t.power.currentPower);
              else value = t.power.currentPower + Min(99, Max(0, value - t.power.currentPower)); }
            return BoostScore(t, side, Max(0, value + d.amount) - t.power.currentPower);
        }
        if (d.specialMode == 34) return DamageScore(t, side, d.amount);
        if (d.specialMode == 35) return BoostScore(t, side, -t.power.currentPower);
        if (d.specialMode == 31 || d.specialMode == 32)
        {
            value = t.power.basePower + t.power.permanentPower;
            if (d.specialMode == 32)
            { if (d.powerMultiplier != 0) value = Max(value, t.power.currentPower);
              else value = t.power.currentPower + Min(99, Max(0, value - t.power.currentPower)); }
            return BoostScore(t, side, Max(0, value + d.amount) - t.power.currentPower);
        }
        if (d.specialMode == 34) return DamageScore(t, side, d.amount);
        if (d.specialMode == 35) return BoostScore(t, side, -t.power.currentPower);
        if (d.specialMode == 25) return 11 - t.power.currentPower;
        if (d.specialMode == 27) return DamageScore(t, side, d.amount) + 5;
        if (d.specialMode == 28) return DamageScore(t, side, d.amount);
        if (d.specialMode == 29) return t.power.currentPower * 2;
        if (d.specialMode == 30) return t.power.basePower + t.power.permanentPower + d.amount - t.power.currentPower;
        if (d.specialMode == 22 || d.specialMode == 23)
        {
            value = HandPower(side);
            if (d.specialMode == 22) return BoostScore(t, side, value); return DamageScore(t, side, value);
        }
        if (d.specialMode == 18)
        {
            d = BetaGwentDuelDefinition(t.runtimeTemplate.templateId);
            if ((d.unitTraits & 1) == 0 && t.power.currentPower <= Max(0, 10 - t.power.armor)) return DamageScore(t, side, 10);
            return BoostScore(t, side, 25 - t.power.currentPower);
        }
        if (d.specialMode == 16 || d.specialMode == 17) return DamageScore(t, side, d.amount);
        if (d.specialMode == 12)
        { if (t.positionPlayerId == side) return d.amount; return DamageScore(t, side, d.amount); }
        if (d.specialMode == 11)
        {
            value = t.power.currentPower;
            if ((t.tokenMask & 1) != 0) value = -value;
            if (t.positionPlayerId != side) value = -value; return value;
        }
        game.GetZoneCards(t.positionPlayerId, t.locationMask, cards);
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].Snapshot(); offset = s.locationIndex - t.locationIndex;
            if (offset < -d.specialRadius || offset > d.specialRadius || !Eligible(s, d, true)) continue;
            if (d.specialMode == 7) value += BoostScore(s, side, d.amount);
            else if (d.specialMode == 8) value += DamageScore(s, side, d.amount);
        }
        return value;
    }
    public function ValidRow(d : SBetaGwentDuelDefinition, player : int, side : int, row : int) : bool
    {
        if ((row & d.specialRowMask) == 0) return false;
        return d.targetSide == 0 || (d.targetSide == 1 && side == player)
            || (d.targetSide == 2 && side == BetaGwentOpponentId(player));
    }
    public function RowValue(d : SBetaGwentDuelDefinition, player : int, side : int, row : int) : int
    {
        var cards : array<CBetaGwentDuelCard>; var i, value, token, powerDelta : int; var s : SBetaGwentCardSnapshot; var unitDefinition : SBetaGwentDuelDefinition;
        if (!ValidRow(d, player, side, row)) return -2147483647;
        game.GetZoneCards(side, row, cards);
        if (d.specialMode == 26)
            return Min(d.deploySpawnCount, Max(0, 9 - cards.Size())) * 3;
        if (d.specialMode == 37)
        {
            if (weather.Token(side, row) == d.specialToken) return 0;
            if (d.specialToken == 256)
            {
                for (i = 0; i < cards.Size(); i += 1)
                { s = cards[i].Snapshot(); unitDefinition = cards[i].Definition(); if ((s.tokenMask & 8) == 0 && !s.isWaitingToDie && (unitDefinition.unitTraits & 288) != 0) value = 4; }
                return value;
            }
            for (i = 0; i < cards.Size(); i += 1)
            { s = cards[i].Snapshot(); if ((s.tokenMask & 8) == 0 && !s.isWaitingToDie) value += DamageScore(s, player, BetaGwentDuelRowAmount(d.specialToken)); }
            // A small continuation estimate; full archetype search remains pending.
            return value + 2;
        }
        if (d.specialMode == 20)
        {
            if (cards.Size() == 0) return 0; s = cards[0].Snapshot();
            if ((s.tokenMask & 8) == 0) value += DamageScore(s, player, d.amount);
            if (cards.Size() > 1) { s = cards[cards.Size() - 1].Snapshot(); if ((s.tokenMask & 8) == 0) value += DamageScore(s, player, d.amount); } return value;
        }
        if (d.specialMode == 15)
        {
            value = Min(cards.Size(), 1) * 2;
            if (d.specialToken == 128) value = Min(cards.Size(), 2) * d.amount;
            if (d.specialToken == 64) value = Min(cards.Size(), 3) + Min(cards.Size(), 1);
            if (d.specialCount == 2) { game.GetZoneCards(side, row * 2, cards); value += Min(cards.Size(), 1) * 2; }
            token = weather.Token(side, row); if (token == d.specialToken) value = 0;
            return value * 2;
        }
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].Snapshot(); if (!Eligible(s, d)) continue;
            if (d.specialMode == 9) value += DamageScore(s, player, s.power.currentPower - s.power.currentPower * d.powerMultiplier / 100, true);
            else if (d.specialMode == 10)
            {
                powerDelta = Max(0, s.power.currentPower - s.power.basePower - s.power.permanentPower);
                value += DamageScore(s, player, powerDelta, true);
            }
            else if (d.specialMode == 13) value += DamageScore(s, player, d.amount);
        }
        if (d.specialMode == 13 && (weather.Token(side, row) & 384) != 0)
        { if (side == player) value -= 4; else value += 4; }
        return value;
    }
    public function BestRow(d : SBetaGwentDuelDefinition, player : int, out side : int, out row : int) : int
    {
        var p, r, value, best : int; best = -2147483647; side = player; row = 1;
        for (p = 1; p <= 2; p += 1) for (r = 1; r <= 4; r *= 2)
        {
            value = RowValue(d, player, p, r);
            if (value > best) { best = value; side = p; row = r; }
        }
        return best;
    }
    public function Value(source : CBetaGwentDuelCard) : int
    {
        var d, targetDefinition : SBetaGwentDuelDefinition; var a, s : SBetaGwentCardSnapshot;
        var ids, selected : array<int>; var side, row, i, j, value, rowValue, maximum, amount : int;
        d = source.Definition(); a = source.Snapshot(); side = a.positionPlayerId; amount = Amount(source);
        if (d.specialRequest == 2) return BestRow(d, side, i, j);
        if (d.specialRequest == 1)
        {
            Gather(0, 7, d, ids); maximum = -2147483647;
            for (i = 0; i < ids.Size(); i += 1)
            { s = game.FindCard(ids[i]).Snapshot(); maximum = Max(maximum, TargetValue(d, s, side)); }
            if (d.specialMode == 17 && maximum > 0) maximum *= 2;
            if (maximum == -2147483647 || d.targetMinimum == 0) return Max(0, maximum); return maximum;
        }
        if (d.specialMode == 19) return MirrorValue(d, side);
        if (d.specialMode == 14)
        {
            for (row = 1; row <= 4; row *= 2)
            { Gather(BetaGwentOpponentId(side), row, d, ids); if (weather.Token(BetaGwentOpponentId(side), row) != d.specialToken) value += Min(1, ids.Size()) * d.amount * 2; }
            return value;
        }
        if (d.specialMode == 4 || d.specialMode == 5)
        {
            for (row = 1; row <= 4; row *= 2)
            {
                if (d.specialMode == 4) Gather(side, row, d, ids); else Gather(BetaGwentOpponentId(side), row, d, ids);
                if (d.specialMode == 5) { Strongest(ids, selected); ids = selected; }
                rowValue = 0;
                for (i = 0; i < ids.Size(); i += 1)
                { s = game.FindCard(ids[i]).Snapshot(); if (d.specialMode == 4) rowValue += amount; else rowValue += DamageScore(s, side, amount); }
                if (ids.Size() > 0) value += rowValue / ids.Size();
            }
            return value;
        }
        if (d.targetSide == 2) Gather(BetaGwentOpponentId(side), 7, d, ids);
        else if (d.targetSide == 1) Gather(side, 7, d, ids); else Gather(0, 7, d, ids);
        if (d.specialMode == 6) { Strongest(ids, selected); ids = selected; }
        for (i = 0; i < ids.Size(); i += 1)
        {
            s = game.FindCard(ids[i]).Snapshot();
            if (d.specialMode == 21) { targetDefinition = BetaGwentDuelDefinition(s.runtimeTemplate.templateId); if ((targetDefinition.unitTraits & 4) != 0) value += amount; }
            else if (d.specialMode == 2) value += amount;
            else if (d.specialMode == 6) value += DamageScore(s, side, s.power.currentPower, true);
            else value += DamageScore(s, side, amount);
        }
        if ((d.specialMode == 2 || d.specialMode == 3) && ids.Size() > d.specialCount) value = value * d.specialCount / ids.Size();
        return value;
    }
}
