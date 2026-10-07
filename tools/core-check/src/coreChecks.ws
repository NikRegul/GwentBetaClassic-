// Development-only, memory-local core checks. No NPC, profile or reward writes.
class CBetaGwentCoreChecks extends IScriptable
{
    private var checks : int;
    private var failures : int;

    private function Check(label : string, condition : bool)
    {
        checks += 1;
        if (condition)
            LogChannel('BetaGwent', "CORE_CHECK_PASS " + label);
        else
        {
            failures += 1;
            LogChannel('BetaGwent', "CORE_CHECK_FAIL " + label);
        }
    }

    private function CheckStatus(label : string, actual : EBetaGwentStateResult,
        expected : EBetaGwentStateResult)
    {
        Check(label + " actual=" + actual + " expected=" + expected, actual == expected);
    }

    private function PassBoth(matchStore : CBetaGwentMatchState, starter : int)
    {
        var opponent : int;

        opponent = BetaGwentOpponentId(starter);
        CheckStatus("turn starter", matchStore.ApplyTurnStarted(starter), BG_StateOK);
        CheckStatus("starter claim", matchStore.ClaimInitialMove(starter), BG_StateOK);
        CheckStatus("starter pass", matchStore.ApplyPlayerPassed(starter), BG_StateOK);
        CheckStatus("starter end", matchStore.ApplyTurnEnded(), BG_StateOK);
        CheckStatus("turn opponent", matchStore.ApplyTurnStarted(opponent), BG_StateOK);
        CheckStatus("opponent claim", matchStore.ClaimInitialMove(opponent), BG_StateOK);
        CheckStatus("opponent pass", matchStore.ApplyPlayerPassed(opponent), BG_StateOK);
        CheckStatus("opponent end", matchStore.ApplyTurnEnded(), BG_StateOK);
    }

    private function CheckRoundCalculations()
    {
        var result : SBetaGwentRoundResult;

        result = BetaGwentCalculateRoundResult(1, 1, 10, 0);
        Check("round player1 win", result.winnerMask == 1 && result.crownDeltaOne == 1 && result.crownDeltaTwo == 0);
        result = BetaGwentCalculateRoundResult(1, 1, 0, 10);
        Check("round player2 win", result.winnerMask == 2 && result.crownDeltaOne == 0 && result.crownDeltaTwo == 1);
        Check("winner starts next", BetaGwentNextStartingPlayer(result) == 2);
        result = BetaGwentCalculateRoundResult(1, 1, 0, 0);
        Check("zero tie both crowns", result.winnerMask == 3 && result.crownDeltaOne == 1 && result.crownDeltaTwo == 1);
        Check("tie starter1 alternates", BetaGwentNextStartingPlayer(result) == 2);
        result = BetaGwentCalculateRoundResult(1, 2, 9, 9);
        Check("nonzero tie", result.winnerMask == 3);
        Check("tie starter2 alternates", BetaGwentNextStartingPlayer(result) == 1);
        Check("no match winner", BetaGwentMatchWinnerMask(1, 1) == 0);
        Check("match player1", BetaGwentMatchWinnerMask(2, 1) == 1);
        Check("match player2", BetaGwentMatchWinnerMask(1, 2) == 2);
        Check("match draw", BetaGwentMatchWinnerMask(2, 2) == 3);
    }

    private function CheckMatchStorage()
    {
        var matchStore : CBetaGwentMatchState;
        var snapshot : SBetaGwentMatchSnapshot;
        var history : array<SBetaGwentRoundResult>;

        matchStore = new CBetaGwentMatchState in this;
        CheckStatus("uninitialized round", matchStore.ApplyRoundStarted(1), BG_StateNotInitialized);
        CheckStatus("initialize", matchStore.Initialize(), BG_StateOK);
        CheckStatus("repeat initialize", matchStore.Initialize(), BG_StateAlreadyInitialized);
        CheckStatus("invalid player", matchStore.ApplyRoundStarted(3), BG_StateInvalidPlayer);
        snapshot = matchStore.Snapshot();
        Check("invalid start no mutation", snapshot.roundNumber == 0 && !snapshot.roundActive);
        CheckStatus("round1 start", matchStore.ApplyRoundStarted(1), BG_StateOK);
        CheckStatus("wrong turn player", matchStore.ApplyTurnStarted(2), BG_StateBoundaryConflict);
        snapshot = matchStore.Snapshot();
        Check("wrong turn no mutation", snapshot.turnSequence == 0 && !snapshot.turnActive);
        PassBoth(matchStore, 1);
        snapshot = matchStore.Snapshot();
        Check("turn reset flags", !snapshot.playerOne.hasMadeInitialMoveForCurrentTurn && !snapshot.playerTwo.hasMadeInitialMoveForCurrentTurn);
        CheckStatus("round1 score", matchStore.RecordRoundResult(10, 0), BG_StateOK);
        CheckStatus("duplicate score", matchStore.RecordRoundResult(10, 0), BG_StateBoundaryConflict);
        snapshot = matchStore.Snapshot();
        Check("duplicate no extra crown", snapshot.playerOne.crowns == 1 && snapshot.playerTwo.crowns == 0);
        CheckStatus("wrong next starter", matchStore.ApplyRoundStarted(2), BG_StateUnexpectedStarter);
        CheckStatus("round2 start", matchStore.ApplyRoundStarted(1), BG_StateOK);
        snapshot = matchStore.Snapshot();
        Check("round reset pass", !snapshot.playerOne.hasPassed && !snapshot.playerTwo.hasPassed);
        PassBoth(matchStore, 1);
        CheckStatus("round2 score", matchStore.RecordRoundResult(0, 10), BG_StateOK);
        snapshot = matchStore.Snapshot();
        Check("split wins continue", snapshot.playerOne.crowns == 1 && snapshot.playerTwo.crowns == 1 && snapshot.matchWinnerMask == 0);
        CheckStatus("round3 start", matchStore.ApplyRoundStarted(2), BG_StateOK);
        PassBoth(matchStore, 2);
        CheckStatus("round3 tie", matchStore.RecordRoundResult(4, 4), BG_StateOK);
        snapshot = matchStore.Snapshot();
        Check("three rounds draw", snapshot.playerOne.crowns == 2 && snapshot.playerTwo.crowns == 2 && snapshot.matchWinnerMask == 3);
        CheckStatus("no round after winner", matchStore.ApplyRoundStarted(1), BG_StateMatchHasWinner);
        matchStore.GetRoundResults(history);
        Check("history count", history.Size() == 3);
        if (history.Size() == 3)
        {
            Check("score snapshots", history[0].scoreOne == 10 && history[0].scoreTwo == 0 && history[1].winnerMask == 2 && history[2].winnerMask == 3);
            history[0].scoreOne = 999;
            matchStore.GetRoundResults(history);
            Check("history detached", history[0].scoreOne == 10);
        }
        snapshot.playerOne.crowns = 999;
        snapshot = matchStore.Snapshot();
        Check("snapshot detached", snapshot.playerOne.crowns == 2);
    }

    private function CheckPassedTurn()
    {
        var matchStore : CBetaGwentMatchState;
        var snapshot : SBetaGwentMatchSnapshot;

        matchStore = new CBetaGwentMatchState in this;
        CheckStatus("passed initialize", matchStore.Initialize(), BG_StateOK);
        CheckStatus("passed round start", matchStore.ApplyRoundStarted(1), BG_StateOK);
        CheckStatus("passed turn1", matchStore.ApplyTurnStarted(1), BG_StateOK);
        CheckStatus("first move claim", matchStore.ClaimInitialMove(1), BG_StateOK);
        CheckStatus("duplicate initial move", matchStore.ClaimInitialMove(1), BG_StateInitialMoveAlreadyClaimed);
        CheckStatus("pass player1", matchStore.ApplyPlayerPassed(1), BG_StateOK);
        CheckStatus("end player1", matchStore.ApplyTurnEnded(), BG_StateOK);
        CheckStatus("opponent still playing", matchStore.ApplyTurnStarted(2), BG_StateOK);
        CheckStatus("opponent end without pass", matchStore.ApplyTurnEnded(), BG_StateOK);
        CheckStatus("passed player receives turn", matchStore.ApplyTurnStarted(1), BG_StateOK);
        snapshot = matchStore.Snapshot();
        Check("passed state retained", snapshot.playerOne.hasPassed && !snapshot.playerTwo.hasPassed && snapshot.turnSequence == 3);
        CheckStatus("passed turn end", matchStore.ApplyTurnEnded(), BG_StateOK);
        CheckStatus("cannot score before both passed", matchStore.RecordRoundResult(0, 0), BG_StatePlayersHaveNotPassed);
    }

    private function CheckCards()
    {
        var card : SBetaGwentCardSnapshot;
        var filter : SBetaGwentLocationFilter;
        var cards : array<SBetaGwentCardSnapshot>;
        var ids : array<int>;
        var player : SBetaGwentPlayerState;
        var request : SBetaGwentPlayRequest;
        var power : SBetaGwentPower;

        card.instanceId = 1;
        card.runtimeTemplate.templateId = 112103;
        card.runtimeTemplate.typeMask = 4;
        card.runtimeTemplate.power = 5;
        card.runtimeTemplate.armor = 2;
        card.runtimeTierMask = 2;
        card.positionPlayerId = 1;
        card.locationMask = 64;
        card.canBePlayed = true;
        card.tokenMask = 4;
        card.isInExecutionStack = false;
        card.isWaitingToDie = false;
        filter = BetaGwentInitialPlayFilter();
        Check("playable leader candidate", BetaGwentMatchesLocationFilter(card, filter));
        filter.withTokens = 12;
        Check("withTokens any bit", BetaGwentMatchesLocationFilter(card, filter));
        filter.withTokens = 0;
        filter.withoutTokens = 12;
        Check("withoutTokens any bit", !BetaGwentMatchesLocationFilter(card, filter));
        filter = BetaGwentInitialPlayFilter();
        filter.typeMask = 0;
        Check("zero type not wildcard", !BetaGwentMatchesLocationFilter(card, filter));
        filter = BetaGwentInitialPlayFilter();
        card.isInExecutionStack = true;
        Check("execution stack excluded", !BetaGwentMatchesLocationFilter(card, filter));
        card.isInExecutionStack = false;
        card.isWaitingToDie = true;
        Check("waiting death excluded", !BetaGwentMatchesLocationFilter(card, filter));
        card.isWaitingToDie = false;
        player.playerId = 1;
        player.hasPassed = false;
        cards.PushBack(card);
        Check("empty hand leader prevents auto pass", BetaGwentDecideTurnEntry(true, player, cards) == BG_TurnEntryInitialPlayRequests);
        cards[0].canBePlayed = false;
        Check("no available card automatic pass", BetaGwentDecideTurnEntry(true, player, cards) == BG_TurnEntryAutomaticPass);
        cards[0].canBePlayed = true;
        cards[0].positionPlayerId = 2;
        Check("opponent leader not available", BetaGwentDecideTurnEntry(true, player, cards) == BG_TurnEntryAutomaticPass);
        cards[0].positionPlayerId = 1;
        player.hasPassed = true;
        Check("passed no request", BetaGwentDecideTurnEntry(true, player, cards) == BG_TurnEntryNoRequest);
        player.hasPassed = false;
        Check("no authority no request", BetaGwentDecideTurnEntry(false, player, cards) == BG_TurnEntryNoRequest);
        cards.Clear();
        card.instanceId = 7;
        cards.PushBack(card);
        card.instanceId = 3;
        card.canBePlayed = false;
        cards.PushBack(card);
        card.instanceId = 9;
        card.canBePlayed = true;
        cards.PushBack(card);
        BetaGwentFilterLocationCards(cards, filter, ids);
        Check("filtered count", ids.Size() == 2);
        if (ids.Size() == 2)
            Check("location order preserved", ids[0] == 7 && ids[1] == 9);
        request.playerId = 1;
        request.requestedInstanceId = 0;
        Check("general request leader", BetaGwentMatchesPlayRequestCard(card, request));
        card.canBePlayed = false;
        Check("general request unavailable", !BetaGwentMatchesPlayRequestCard(card, request));
        request.requestedInstanceId = card.instanceId;
        card.locationMask = 256;
        card.positionPlayerId = 2;
        Check("selected request playstack predicate", BetaGwentMatchesPlayRequestCard(card, request));
        card.power.basePower = 5;
        card.power.permanentPower = 3;
        card.power.currentPower = 12;
        card.power.armor = 7;
        power = BetaGwentCalculatePowerReset(card.power, card.runtimeTemplate, false);
        Check("ordinary reset preserves permanent armor", power.basePower == 5 && power.permanentPower == 3 && power.currentPower == 8 && power.armor == 7);
        power = BetaGwentCalculatePowerReset(card.power, card.runtimeTemplate, true);
        Check("template reset", power.basePower == 5 && power.permanentPower == 0 && power.currentPower == 5 && power.armor == 2);
        card.power.basePower = -3;
        card.power.permanentPower = 1;
        card.power.armor = -2;
        power = BetaGwentCalculatePowerReset(card.power, card.runtimeTemplate, false);
        Check("reset clamps current only", power.basePower == -3 && power.permanentPower == 1 && power.currentPower == 0 && power.armor == 0);
    }

    private function CheckTriggerOrder()
    {
        var existing : array<SBetaGwentTriggerTicket>;
        var old : SBetaGwentTriggerTicket;
        var candidate : SBetaGwentTriggerTicket;
        Check("trigger melee priority", BetaGwentTriggerLocationPriority(1) == 9);
        Check("trigger ranged priority", BetaGwentTriggerLocationPriority(2) == 8);
        Check("trigger siege priority", BetaGwentTriggerLocationPriority(4) == 7);
        Check("trigger hand priority", BetaGwentTriggerLocationPriority(8) == 6);
        Check("trigger leader priority", BetaGwentTriggerLocationPriority(64) == 5);
        Check("trigger deck priority", BetaGwentTriggerLocationPriority(16) == 4);
        Check("trigger grave priority", BetaGwentTriggerLocationPriority(32) == 3);
        Check("trigger playstack priority", BetaGwentTriggerLocationPriority(256) == 2);
        Check("trigger ignore key priority", BetaGwentTriggerLocationPriority(767) == 1);
        Check("trigger void priority", BetaGwentTriggerLocationPriority(512) == 0);
        Check("trigger unknown key rejected", BetaGwentTriggerLocationPriority(128) == -1);
        old.instanceId = 100;
        old.ownerPresent = true;
        old.priority = 0;
        old.locationMask = 2;
        old.ownerPlayerId = 2;
        old.ownerIndex = 4;
        candidate = old;
        existing.PushBack(old);
        candidate.priority = 5;
        Check("higher trigger priority first", BetaGwentTriggerInsertionIndex(existing, candidate, 1) == 0);
        candidate.priority = -5;
        Check("lower trigger priority last", BetaGwentTriggerInsertionIndex(existing, candidate, 1) == 1);
        candidate.priority = 0;
        candidate.locationMask = 1;
        Check("melee before ranged at equal priority", BetaGwentTriggerInsertionIndex(existing, candidate, 1) == 0);
        candidate.locationMask = 4;
        Check("siege after ranged at equal priority", BetaGwentTriggerInsertionIndex(existing, candidate, 1) == 1);
        candidate.locationMask = 2;
        candidate.ownerPlayerId = 1;
        candidate.ownerIndex = 99;
        Check("current side before opposing side", BetaGwentTriggerInsertionIndex(existing, candidate, 1) == 0);
        Check("other current side keeps opposing last", BetaGwentTriggerInsertionIndex(existing, candidate, 2) == 1);
        candidate.ownerPlayerId = 2;
        candidate.ownerIndex = 3;
        Check("same side lower index first", BetaGwentTriggerInsertionIndex(existing, candidate, 1) == 0);
        candidate.ownerIndex = 5;
        Check("same side higher index last", BetaGwentTriggerInsertionIndex(existing, candidate, 1) == 1);
        candidate.ownerIndex = 4;
        candidate.instanceId = 1;
        Check("equal keys stable without id sort", BetaGwentTriggerInsertionIndex(existing, candidate, 1) == 1);
        candidate.ownerPresent = false;
        candidate.priority = 100;
        candidate.locationMask = 128;
        Check("ownerless always appended", BetaGwentTriggerInsertionIndex(existing, candidate, 1) == 1);
        candidate.ownerPresent = true;
        Check("unsupported candidate metadata", BetaGwentTriggerInsertionIndex(existing, candidate, 1) == -1);
        candidate.priority = 0;
        candidate.locationMask = 2;
        old.ownerPresent = false;
        existing.Clear();
        existing.PushBack(old);
        Check("unsupported old owner metadata", BetaGwentTriggerInsertionIndex(existing, candidate, 1) == -1);
        existing.Clear();
        Check("empty trigger batch", BetaGwentTriggerInsertionIndex(existing, candidate, 1) == 0);
    }

    public function GetSummary() : string
    {
        return "CORE_CHECK_DONE checks=" + checks + " passed=" + (checks - failures) + " failed=" + failures;
    }

    public function GetDisplaySummary() : string
    {
        return "Core: " + (checks - failures) + "/" + checks + ", ошибок: " + failures;
    }

    public function Run()
    {
        var summary : string;

        checks = 0;
        failures = 0;
        LogChannel('BetaGwent', "CORE_CHECK_BEGIN schema=1");
        CheckRoundCalculations();
        CheckMatchStorage();
        CheckPassedTurn();
        CheckCards();
        CheckTriggerOrder();
        summary = "CORE_CHECK_DONE checks=" + checks + " passed=" + (checks - failures) + " failed=" + failures;
        LogChannel('BetaGwent', summary);
        theGame.GetGuiManager().ShowNotification(summary, 12.0);
    }
}

exec function bgcore_test()
{
    var runner : CBetaGwentCoreChecks;

    if (!thePlayer)
    {
        LogChannel('BetaGwent', "CORE_CHECK_SKIPPED no player");
        return;
    }
    runner = new CBetaGwentCoreChecks in thePlayer;
    runner.Run();
}

