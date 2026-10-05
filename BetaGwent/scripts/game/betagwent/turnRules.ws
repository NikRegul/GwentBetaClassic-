// Source: TurnGameState.OnEnterState + BoardManager/Location.GetCards.
// Evaluate only after TurnStarted effects have reached the correct boundary.
function BetaGwentDecideTurnEntry(hasAuthority : bool, player : SBetaGwentPlayerState,
    candidates : array<SBetaGwentCardSnapshot>) : EBetaGwentTurnEntryDecision
{
    var filter : SBetaGwentLocationFilter;
    var i : int;

    if (!hasAuthority || player.hasPassed)
        return BG_TurnEntryNoRequest;

    filter = BetaGwentInitialPlayFilter();
    for (i = 0; i < candidates.Size(); i += 1)
    {
        if (candidates[i].positionPlayerId == player.playerId
            && BetaGwentMaskIntersects(candidates[i].locationMask, 72)
            && BetaGwentMatchesLocationFilter(candidates[i], filter))
        {
            // This answers existence only. Creation/linkage of both original
            // play requests and their ordering belong to RequestManager.
            return BG_TurnEntryInitialPlayRequests;
        }
    }
    return BG_TurnEntryAutomaticPass;
}
