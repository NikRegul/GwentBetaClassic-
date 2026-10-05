// Source: beta-flow-il.txt and beta-legality-rounds-il.txt.
// Pure calculations: no UI, RNG, events, queues or automatic phase advancement.
function BetaGwentIsPlayerId(playerId : int) : bool
{
    return playerId == 1 || playerId == 2;
}

function BetaGwentOpponentId(playerId : int) : int
{
    if (playerId == 1)
        return 2;
    if (playerId == 2)
        return 1;
    return 0;
}

function BetaGwentCalculateRoundResult(roundNumber : int, startingPlayerId : int,
    scoreOne : int, scoreTwo : int) : SBetaGwentRoundResult
{
    var result : SBetaGwentRoundResult;

    result.roundNumber = roundNumber;
    result.startingPlayerId = startingPlayerId;
    result.scoreOne = scoreOne;
    result.scoreTwo = scoreTwo;
    result.winnerMask = 0;
    result.crownDeltaOne = 0;
    result.crownDeltaTwo = 0;
    if (scoreOne >= scoreTwo)
    {
        result.winnerMask = result.winnerMask | 1;
        result.crownDeltaOne = 1;
    }
    if (scoreTwo >= scoreOne)
    {
        result.winnerMask = result.winnerMask | 2;
        result.crownDeltaTwo = 1;
    }
    return result;
}

function BetaGwentMatchWinnerMask(crownsOne : int, crownsTwo : int) : int
{
    var mask : int;

    mask = 0;
    if (crownsOne >= 2)
        mask = mask | 1;
    if (crownsTwo >= 2)
        mask = mask | 2;
    return mask;
}

function BetaGwentNextStartingPlayer(result : SBetaGwentRoundResult) : int
{
    if (result.winnerMask == 3)
        return BetaGwentOpponentId(result.startingPlayerId);
    if (BetaGwentIsPlayerId(result.winnerMask))
        return result.winnerMask;
    return 0;
}

function BetaGwentAllPlayersPassed(playerOne : SBetaGwentPlayerState,
    playerTwo : SBetaGwentPlayerState) : bool
{
    return playerOne.hasPassed && playerTwo.hasPassed;
}
