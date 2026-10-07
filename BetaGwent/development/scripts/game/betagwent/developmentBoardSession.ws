// Synthetic field fixture. Not a Beta deck, effect executor, AI or saved profile.
struct SBetaGwentDevelopmentCard
{
    var card : SBetaGwentCardSnapshot;
    var title : string;
    var createdCopy : bool;
}

class CBetaGwentDevelopmentBoardSession extends IScriptable
{
    private var matchStore : CBetaGwentMatchState;
    private var cards : array<SBetaGwentDevelopmentCard>;
    private var waitingRound : bool;
    private var fatal : bool;
    private var message : string;

    public function InitializeFixture()
    {
        matchStore = new CBetaGwentMatchState in this;
        matchStore.Initialize();
        cards.Clear();
        waitingRound = false;
        fatal = false;
        if (!RequireOK(matchStore.ApplyRoundStarted(1))) return;
        FillHands();
        if (!RequireOK(matchStore.ApplyTurnStarted(1))) return;
        message = "Выберите тестовый отряд и свой ряд. Эффекты отключены.";
    }

    private function RequireOK(result : EBetaGwentStateResult) : bool
    {
        if (result == BG_StateOK) return true;
        fatal = true;
        message = "DEV state error: " + result;
        LogChannel('BetaGwent', "BOARD_STATE_ERROR " + result);
        return false;
    }

    public function Snapshot() : SBetaGwentMatchSnapshot { return matchStore.Snapshot(); }
    public function GetMessage() : string { return message; }
    public function IsWaitingRound() : bool { return waitingRound; }
    public function IsFatal() : bool { return fatal; }
    public function GetCards(out output : array<SBetaGwentDevelopmentCard>)
    {
        var i : int;
        output.Clear();
        for (i = 0; i < cards.Size(); i += 1) output.PushBack(cards[i]);
    }

    private function FillHands()
    {
        var side : int;
        var i : int;
        var cardView : SBetaGwentDevelopmentCard;
        var snapshot : SBetaGwentMatchSnapshot;
        snapshot = matchStore.Snapshot();
        for (side = 1; side <= 2; side += 1)
        {
            for (i = 0; i < 6; i += 1)
            {
                cardView.card.instanceId = snapshot.roundNumber * 100 + side * 10 + i;
                cardView.card.originTemplateId = -1 - i;
                cardView.card.runtimeTemplate.templateId = -1 - i;
                cardView.card.runtimeTemplate.typeMask = 4;
                cardView.card.runtimeTemplate.tierMask = 2;
                cardView.card.runtimeTemplate.factionMask = 1;
                cardView.card.runtimeTemplate.power = 3 + i;
                cardView.card.runtimeTemplate.armor = 0;
                cardView.card.ownerId = side;
                cardView.card.controllerId = side;
                cardView.card.positionPlayerId = side;
                cardView.card.locationMask = 8;
                cardView.card.locationIndex = i;
                cardView.card.runtimeTierMask = 2;
                cardView.card.tokenMask = 0;
                cardView.card.power.basePower = 3 + i;
                cardView.card.power.currentPower = 3 + i;
                cardView.card.power.permanentPower = 0;
                cardView.card.power.armor = 0;
                cardView.card.canBePlayed = true;
                cardView.card.isInExecutionStack = false;
                cardView.card.isWaitingToDie = false;
                cardView.title = "DEV " + (i + 1);
                cards.PushBack(cardView);
            }
            // A separate test leader exercises availability, not an ability.
            cardView.card.instanceId = snapshot.roundNumber * 100 + side * 10 + 9;
            cardView.card.originTemplateId = -100;
            cardView.card.runtimeTemplate.templateId = -100;
            cardView.card.runtimeTemplate.tierMask = 1;
            cardView.card.runtimeTierMask = 1;
            cardView.card.locationMask = 64;
            cardView.card.locationIndex = 0;
            cardView.card.runtimeTemplate.power = 0;
            cardView.card.power.basePower = 0;
            cardView.card.power.currentPower = 0;
            cardView.title = "DEV лидер";
            cards.PushBack(cardView);
        }
    }

    public function CountLocation(side : int, locationMask : int) : int
    {
        var i : int;
        var count : int;
        count = 0;
        for (i = 0; i < cards.Size(); i += 1)
            if (cards[i].card.positionPlayerId == side && cards[i].card.locationMask == locationMask) count += 1;
        return count;
    }

    public function Score(side : int) : int
    {
        var i : int;
        var total : int;
        total = 0;
        for (i = 0; i < cards.Size(); i += 1)
            if (cards[i].card.positionPlayerId == side && BetaGwentMaskIntersects(cards[i].card.locationMask, 7))
                total += cards[i].card.power.currentPower;
        return total;
    }

    public function LeaderAvailable(side : int) : bool
    {
        var i : int;
        for (i = 0; i < cards.Size(); i += 1)
            if (cards[i].card.positionPlayerId == side && cards[i].card.locationMask == 64 && cards[i].card.canBePlayed)
                return true;
        return false;
    }

    private function CanAct(side : int) : bool
    {
        var snapshot : SBetaGwentMatchSnapshot;
        snapshot = matchStore.Snapshot();
        if (fatal || waitingRound || snapshot.matchWinnerMask != 0 || !snapshot.turnActive || snapshot.currentPlayerId != side)
            return false;
        if (side == 1) return !snapshot.playerOne.hasPassed;
        if (side == 2) return !snapshot.playerTwo.hasPassed;
        return false;
    }

    public function Play(side : int, instanceId : int, row : int) : bool
    {
        var i : int;
        if (!CanAct(side) || (row != 1 && row != 2 && row != 4)) return false;
        // Fixture display limit; this is not the canonical row-capacity rule.
        if (CountLocation(side, row) >= 9) return false;
        for (i = 0; i < cards.Size(); i += 1)
        {
            if (cards[i].card.instanceId != instanceId) continue;
            if (cards[i].card.positionPlayerId != side || cards[i].card.locationMask != 8 || !cards[i].card.canBePlayed)
                return false;
            if (!RequireOK(matchStore.ClaimInitialMove(side))) return false;
            cards[i].card.locationIndex = CountLocation(side, row);
            cards[i].card.locationMask = row;
            cards[i].card.canBePlayed = false;
            message = "Тестовый отряд размещён. Сила взята из fixture, без эффектов.";
            FinishTurn();
            return !fatal;
        }
        return false;
    }

    public function UseLeader(side : int) : bool
    {
        var i : int;
        if (!CanAct(side)) return false;
        for (i = 0; i < cards.Size(); i += 1)
        {
            if (cards[i].card.positionPlayerId != side || cards[i].card.locationMask != 64 || !cards[i].card.canBePlayed) continue;
            if (!RequireOK(matchStore.ClaimInitialMove(side))) return false;
            cards[i].card.canBePlayed = false;
            message = "Доступность DEV лидера снята; способность не исполнялась.";
            FinishTurn();
            return !fatal;
        }
        return false;
    }

    public function Pass(side : int) : bool
    {
        if (!CanAct(side)) return false;
        if (!RequireOK(matchStore.ClaimInitialMove(side))) return false;
        if (!RequireOK(matchStore.ApplyPlayerPassed(side))) return false;
        message = "Игрок " + side + " спасовал.";
        FinishTurn();
        return !fatal;
    }

    private function FinishTurn()
    {
        var snapshot : SBetaGwentMatchSnapshot;
        var next : int;
        if (!RequireOK(matchStore.ApplyTurnEnded())) return;
        snapshot = matchStore.Snapshot();
        if (BetaGwentAllPlayersPassed(snapshot.playerOne, snapshot.playerTwo))
        {
            if (!RequireOK(matchStore.RecordRoundResult(Score(1), Score(2)))) return;
            snapshot = matchStore.Snapshot();
            waitingRound = snapshot.matchWinnerMask == 0;
            message = "Раунд записан: " + Score(1) + ":" + Score(2);
            if (snapshot.matchWinnerMask != 0) message = message + ". Match winner mask=" + snapshot.matchWinnerMask;
            return;
        }
        next = BetaGwentOpponentId(snapshot.currentPlayerId);
        if (!RequireOK(matchStore.ApplyTurnStarted(next))) return;
        // Preserve the passed player's boundary even in this effect-free fixture.
        if ((next == 1 && snapshot.playerOne.hasPassed) || (next == 2 && snapshot.playerTwo.hasPassed))
        {
            if (!RequireOK(matchStore.ApplyTurnEnded())) return;
            RequireOK(matchStore.ApplyTurnStarted(BetaGwentOpponentId(next)));
        }
    }

    public function OpponentStep() : bool
    {
        var i : int;
        if (!CanAct(2)) return false;
        // Manual deterministic driver, not production AI or hidden-state search.
        for (i = 0; i < cards.Size(); i += 1)
            if (cards[i].card.positionPlayerId == 2 && cards[i].card.locationMask == 8)
                return Play(2, cards[i].card.instanceId, 1);
        if (LeaderAvailable(2)) return UseLeader(2);
        return Pass(2);
    }

    public function BeginNextRound() : bool
    {
        var i : int;
        var history : array<SBetaGwentRoundResult>;
        if (!waitingRound || fatal) return false;
        matchStore.GetRoundResults(history);
        if (history.Size() == 0) return false;
        if (!RequireOK(matchStore.ApplyRoundStarted(BetaGwentNextStartingPlayer(history[history.Size() - 1])))) return false;
        // Fixture cleanup/refill; not original ClearBoard or Beta draws/mulligan.
        for (i = 0; i < cards.Size(); i += 1)
        {
            if (cards[i].card.locationMask == 64) cards[i].card.canBePlayed = false;
            else if (cards[i].card.locationMask != 32) cards[i].card.locationMask = 32;
        }
        FillHands();
        waitingRound = false;
        RequireOK(matchStore.ApplyTurnStarted(BetaGwentNextStartingPlayer(history[history.Size() - 1])));
        message = "Новый fixture-раунд. Рука заполнена заново для проверки поля.";
        return !fatal;
    }
}

