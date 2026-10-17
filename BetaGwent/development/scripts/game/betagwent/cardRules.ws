// Source: beta-card-rules-il.txt. These predicates are not full legal actions.
function BetaGwentMaskIntersects(value : int, mask : int) : bool
{
    // Original EnumExtensions.Contains means ANY shared bit, not ALL bits.
    return (value & mask) != 0;
}

function BetaGwentMatchesLocationFilter(card : SBetaGwentCardSnapshot,
    filter : SBetaGwentLocationFilter) : bool
{
    if (card.isInExecutionStack || card.isWaitingToDie)
        return false;
    if (filter.typeMask != 14 && !BetaGwentMaskIntersects(card.runtimeTemplate.typeMask, filter.typeMask))
        return false;
    if (filter.tierMask != 15 && !BetaGwentMaskIntersects(card.runtimeTierMask, filter.tierMask))
        return false;
    if (filter.withoutTokens != 0 && BetaGwentMaskIntersects(card.tokenMask, filter.withoutTokens))
        return false;
    if (filter.withTokens != 0 && !BetaGwentMaskIntersects(card.tokenMask, filter.withTokens))
        return false;
    if (filter.includeOnlyCardsThatCanBePlayed && !card.canBePlayed)
        return false;
    return true;
}

function BetaGwentFilterLocationCards(orderedCards : array<SBetaGwentCardSnapshot>,
    filter : SBetaGwentLocationFilter, out instanceIds : array<int>)
{
    var i : int;

    // Caller supplies exactly one Location's stored order, not a registry scan.
    instanceIds.Clear();
    for (i = 0; i < orderedCards.Size(); i += 1)
    {
        if (BetaGwentMatchesLocationFilter(orderedCards[i], filter))
            instanceIds.PushBack(orderedCards[i].instanceId);
    }
}

function BetaGwentInitialPlayFilter() : SBetaGwentLocationFilter
{
    var filter : SBetaGwentLocationFilter;

    filter.typeMask = 14;
    filter.tierMask = 15;
    filter.withoutTokens = 0;
    filter.withTokens = 0;
    filter.includeOnlyCardsThatCanBePlayed = true;
    return filter;
}

function BetaGwentMatchesPlayRequestCard(card : SBetaGwentCardSnapshot,
    request : SBetaGwentPlayRequest) : bool
{
    if (request.requestedInstanceId == 0)
    {
        return card.canBePlayed
            && BetaGwentMaskIntersects(card.locationMask, 72)
            && card.positionPlayerId == request.playerId;
    }
    // Preserve the original selected-card branch's narrower conditions.
    return card.instanceId == request.requestedInstanceId
        && (card.locationMask == 8 || card.locationMask == 256);
}

function BetaGwentCalculatePowerReset(power : SBetaGwentPower,
    runtimeTemplate : SBetaGwentTemplateHeader, resetToTemplate : bool) : SBetaGwentPower
{
    var result : SBetaGwentPower;

    result = power;
    if (resetToTemplate)
    {
        result.basePower = runtimeTemplate.power;
        result.permanentPower = 0;
        result.armor = runtimeTemplate.armor;
    }
    result.currentPower = result.basePower + result.permanentPower;
    // SetPowerAndArmor clamps the new current values, not the base layers.
    if (result.currentPower < 0)
        result.currentPower = 0;
    if (result.armor < 0)
        result.armor = 0;
    // This only calculates values. Original SetPowerAndArmor/event delivery
    // and Card.Reset's other flags belong to a future resolution action.
    return result;
}
