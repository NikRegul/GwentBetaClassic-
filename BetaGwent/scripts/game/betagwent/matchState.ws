// Draft storage for a two-player match; not a complete FSM or intent executor.
// Apply* methods are coordinator boundaries. Their guards are mod-local.
// Source-backed mutations: Player.OnPass/OnRoundStart/OnTurnEnd, RoundInfo.SetResult.
class CBetaGwentMatchState extends IScriptable
{
    private var initialized : bool;
    private var playerOne : SBetaGwentPlayerState;
    private var playerTwo : SBetaGwentPlayerState;
    private var roundNumber : int;
    private var turnSequence : int;
    private var startingPlayerId : int;
    private var currentPlayerId : int;
    private var roundActive : bool;
    private var turnActive : bool;
    private var results : array<SBetaGwentRoundResult>;

    public function Initialize() : EBetaGwentStateResult
    {
        if (initialized)
            return BG_StateAlreadyInitialized;

        playerOne.playerId = 1;
        playerOne.crowns = 0;
        playerOne.hasPassed = false;
        playerOne.hasMadeInitialMoveForCurrentTurn = false;
        playerTwo.playerId = 2;
        playerTwo.crowns = 0;
        playerTwo.hasPassed = false;
        playerTwo.hasMadeInitialMoveForCurrentTurn = false;
        roundNumber = 0;
        turnSequence = 0;
        startingPlayerId = 0;
        currentPlayerId = 0;
        roundActive = false;
        turnActive = false;
        results.Clear();
        initialized = true;
        return BG_StateOK;
    }

    public function Snapshot() : SBetaGwentMatchSnapshot
    {
        var snapshot : SBetaGwentMatchSnapshot;

        snapshot.initialized = initialized;
        snapshot.roundNumber = roundNumber;
        snapshot.turnSequence = turnSequence;
        snapshot.startingPlayerId = startingPlayerId;
        snapshot.currentPlayerId = currentPlayerId;
        snapshot.roundActive = roundActive;
        snapshot.turnActive = turnActive;
        snapshot.playerOne = playerOne;
        snapshot.playerTwo = playerTwo;
        snapshot.matchWinnerMask = BetaGwentMatchWinnerMask(playerOne.crowns, playerTwo.crowns);
        return snapshot;
    }

    public function GetRoundResults(out history : array<SBetaGwentRoundResult>)
    {
        var i : int;

        history.Clear();
        for (i = 0; i < results.Size(); i += 1)
            history.PushBack(results[i]);
    }

    public function ApplyRoundStarted(starterId : int) : EBetaGwentStateResult
    {
        if (!initialized)
            return BG_StateNotInitialized;
        if (!BetaGwentIsPlayerId(starterId))
            return BG_StateInvalidPlayer;
        if (roundActive || turnActive)
            return BG_StateBoundaryConflict;
        if (BetaGwentMatchWinnerMask(playerOne.crowns, playerTwo.crowns) != 0)
            return BG_StateMatchHasWinner;
        if (results.Size() > 0)
        {
            if (starterId != BetaGwentNextStartingPlayer(results[results.Size() - 1]))
                return BG_StateUnexpectedStarter;
        }

        // The first starter is supplied by settings/RNG, never guessed here.
        roundNumber += 1;
        startingPlayerId = starterId;
        currentPlayerId = 0;
        playerOne.hasPassed = false;
        playerTwo.hasPassed = false;
        roundActive = true;
        return BG_StateOK;
    }

    public function ApplyTurnStarted(playerId : int) : EBetaGwentStateResult
    {
        var expectedPlayerId : int;

        if (!initialized)
            return BG_StateNotInitialized;
        if (!BetaGwentIsPlayerId(playerId))
            return BG_StateInvalidPlayer;
        if (!roundActive || turnActive || BetaGwentAllPlayersPassed(playerOne, playerTwo))
            return BG_StateBoundaryConflict;
        expectedPlayerId = startingPlayerId;
        if (currentPlayerId != 0)
            expectedPlayerId = BetaGwentOpponentId(currentPlayerId);
        if (playerId != expectedPlayerId)
            return BG_StateBoundaryConflict;

        // Passed players still receive turn-start boundaries in the original.
        currentPlayerId = playerId;
        turnSequence += 1;
        turnActive = true;
        return BG_StateOK;
    }

    public function ClaimInitialMove(playerId : int) : EBetaGwentStateResult
    {
        if (!initialized)
            return BG_StateNotInitialized;
        if (!BetaGwentIsPlayerId(playerId))
            return BG_StateInvalidPlayer;
        if (!turnActive || playerId != currentPlayerId)
            return BG_StateBoundaryConflict;
        if (playerId == 1)
        {
            if (playerOne.hasMadeInitialMoveForCurrentTurn)
                return BG_StateInitialMoveAlreadyClaimed;
            playerOne.hasMadeInitialMoveForCurrentTurn = true;
        }
        else
        {
            if (playerTwo.hasMadeInitialMoveForCurrentTurn)
                return BG_StateInitialMoveAlreadyClaimed;
            playerTwo.hasMadeInitialMoveForCurrentTurn = true;
        }
        return BG_StateOK;
    }

    public function ApplyPlayerPassed(playerId : int) : EBetaGwentStateResult
    {
        if (!initialized)
            return BG_StateNotInitialized;
        if (!BetaGwentIsPlayerId(playerId))
            return BG_StateInvalidPlayer;
        if (!roundActive || !turnActive || playerId != currentPlayerId)
            return BG_StateBoundaryConflict;

        // Call only at OnPlayerPassed, after BeforePassed has resolved and
        // the play request is marked. The coordinator emits AfterPassed later.
        // This is deliberately separate from AskPass's initial-move claim.
        if (playerId == 1)
            playerOne.hasPassed = true;
        else
            playerTwo.hasPassed = true;
        return BG_StateOK;
    }

    public function ApplyTurnEnded() : EBetaGwentStateResult
    {
        if (!initialized)
            return BG_StateNotInitialized;
        if (!turnActive)
            return BG_StateBoundaryConflict;

        if (currentPlayerId == 1)
            playerOne.hasMadeInitialMoveForCurrentTurn = false;
        else
            playerTwo.hasMadeInitialMoveForCurrentTurn = false;
        turnActive = false;
        return BG_StateOK;
    }

    public function RecordRoundResult(scoreOne : int, scoreTwo : int) : EBetaGwentStateResult
    {
        var result : SBetaGwentRoundResult;

        if (!initialized)
            return BG_StateNotInitialized;
        if (!roundActive || turnActive)
            return BG_StateBoundaryConflict;
        if (!BetaGwentAllPlayersPassed(playerOne, playerTwo))
            return BG_StatePlayersHaveNotPassed;

        // Scores must already be resolved BoardSide totals. No field cleanup.
        result = BetaGwentCalculateRoundResult(roundNumber, startingPlayerId, scoreOne, scoreTwo);
        results.PushBack(result);
        playerOne.crowns += result.crownDeltaOne;
        playerTwo.crowns += result.crownDeltaTwo;
        roundActive = false;
        // Prevents duplicate crowns, but does not execute EndGame/ClearBoard:
        // AfterRoundTrigger and OnRoundEnded must run before that decision.
        return BG_StateOK;
    }
}
