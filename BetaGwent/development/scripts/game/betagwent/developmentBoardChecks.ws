// Isolated effect-free fixture checks. Never touches the displayed session.
// These verify the development coordinator, not original Beta effect parity.
class CBetaGwentDevelopmentBoardChecks extends IScriptable
{
    private var checks : int;
    private var failures : int;

    private function Check(label : string, condition : bool)
    {
        checks += 1;
        if (condition) LogChannel('BetaGwent', "BOARD_CHECK_PASS " + label);
        else
        {
            failures += 1;
            LogChannel('BetaGwent', "BOARD_CHECK_FAIL " + label);
        }
    }

    private function NewFixture() : CBetaGwentDevelopmentBoardSession
    {
        var fixture : CBetaGwentDevelopmentBoardSession;
        fixture = new CBetaGwentDevelopmentBoardSession in this;
        fixture.InitializeFixture();
        return fixture;
    }

    private function Current(fixture : CBetaGwentDevelopmentBoardSession) : int
    {
        var snapshot : SBetaGwentMatchSnapshot;
        snapshot = fixture.Snapshot();
        return snapshot.currentPlayerId;
    }

    private function CheckActions()
    {
        var fixture : CBetaGwentDevelopmentBoardSession;
        var before : SBetaGwentMatchSnapshot;
        var after : SBetaGwentMatchSnapshot;
        var row : int;
        var i : int;
        fixture = NewFixture();
        before = fixture.Snapshot();
        Check("initial round and turn", before.roundNumber == 1 && before.currentPlayerId == 1 && before.turnActive);
        Check("initial hands", fixture.CountLocation(1, 8) == 6 && fixture.CountLocation(2, 8) == 6);
        Check("initial leaders", fixture.LeaderAvailable(1) && fixture.LeaderAvailable(2));
        Check("initial scores", fixture.Score(1) == 0 && fixture.Score(2) == 0);
        Check("unknown card rejected", !fixture.Play(1, 999999, 1));
        Check("enemy instance rejected", !fixture.Play(1, 120, 1));
        Check("invalid row rejected", !fixture.Play(1, 110, 8));
        Check("combined row mask rejected", !fixture.Play(1, 110, 3));
        Check("wrong turn rejected", !fixture.Play(2, 120, 1));
        Check("invalid player rejected", !fixture.Pass(3));
        Check("premature next round rejected", !fixture.BeginNextRound());
        after = fixture.Snapshot();
        Check("rejection preserves turn", before.turnSequence == after.turnSequence && before.currentPlayerId == after.currentPlayerId && after.turnActive);
        Check("rejection preserves hand and score", fixture.CountLocation(1, 8) == 6 && fixture.Score(1) == 0);
        Check("rejection does not make fatal", !fixture.IsFatal());
        row = 1;
        for (i = 0; i < 3; i += 1)
        {
            Check("place own row " + row, fixture.Play(1, 110 + i, row));
            Check("turn switches to enemy", Current(fixture) == 2);
            Check("replay same instance rejected", !fixture.Play(1, 110 + i, row));
            Check("place enemy row " + row, fixture.Play(2, 120 + i, row));
            Check("row population " + row, fixture.CountLocation(1, row) == 1 && fixture.CountLocation(2, row) == 1);
            row *= 2;
        }
        Check("scores sum all rows", fixture.Score(1) == 12 && fixture.Score(2) == 12);
        Check("remaining hands", fixture.CountLocation(1, 8) == 3 && fixture.CountLocation(2, 8) == 3);
        Check("own leader consumes turn", fixture.UseLeader(1) && Current(fixture) == 2);
        Check("enemy leader consumes turn", fixture.UseLeader(2) && Current(fixture) == 1);
        Check("leaders unavailable", !fixture.LeaderAvailable(1) && !fixture.LeaderAvailable(2));
        Check("leader replay rejected", !fixture.UseLeader(1));
        Check("leader has no fixture power effect", fixture.Score(1) == 12 && fixture.Score(2) == 12);
        Check("own pass", fixture.Pass(1));
        before = fixture.Snapshot();
        Check("passed player cannot place", !fixture.Play(1, 113, 1));
        Check("passed player cannot pass again", !fixture.Pass(1));
        Check("enemy can continue after own pass", fixture.Play(2, 123, 1));
        after = fixture.Snapshot();
        Check("passed boundary preserved", after.currentPlayerId == 2 && after.turnSequence == before.turnSequence + 2 && after.playerOne.hasPassed);
        Check("enemy pass ends round", fixture.Pass(2));
        after = fixture.Snapshot();
        Check("round result stored", fixture.IsWaitingRound() && !after.roundActive && !after.turnActive && after.playerTwo.crowns == 1 && after.playerOne.crowns == 0);
        Check("cannot place between rounds", !fixture.Play(2, 124, 1));
        Check("next round starts", fixture.BeginNextRound());
        after = fixture.Snapshot();
        Check("winner starts round two", after.roundNumber == 2 && after.currentPlayerId == 2 && after.turnActive);
        Check("passes reset", !after.playerOne.hasPassed && !after.playerTwo.hasPassed);
        Check("fixture board cleanup", fixture.Score(1) == 0 && fixture.Score(2) == 0);
        Check("fixture discard counts", fixture.CountLocation(1, 32) == 6 && fixture.CountLocation(2, 32) == 6);
        Check("fixture refill", fixture.CountLocation(1, 8) == 6 && fixture.CountLocation(2, 8) == 6);
        Check("fixture new leaders", fixture.LeaderAvailable(1) && fixture.LeaderAvailable(2));
        Check("old instance cannot be replayed", !fixture.Play(2, 120, 1));
        Check("opponent driver advances", fixture.OpponentStep() && Current(fixture) == 1 && fixture.Score(2) == 3);
        Check("opponent driver rejects own turn", !fixture.OpponentStep());
        Check("actions did not make fatal", !fixture.IsFatal());
    }

    private function CheckOutcome(winner : int)
    {
        var fixture : CBetaGwentDevelopmentBoardSession;
        var snapshot : SBetaGwentMatchSnapshot;
        var round : int;
        var starter : int;
        fixture = NewFixture();
        for (round = 1; round <= 2; round += 1)
        {
            starter = Current(fixture);
            if (winner == 3)
            {
                Check("draw starter pass " + round, fixture.Pass(starter));
                Check("draw opponent pass " + round, fixture.Pass(BetaGwentOpponentId(starter)));
            }
            else
            {
                if (starter != winner) Check("loser passes first " + round, fixture.Pass(starter));
                Check("winner places " + winner + "/" + round, fixture.Play(winner, round * 100 + winner * 10, 1));
                if (starter == winner) Check("loser passes second " + round, fixture.Pass(BetaGwentOpponentId(winner)));
                Check("winner ends round " + round, fixture.Pass(winner));
            }
            snapshot = fixture.Snapshot();
            Check("round closed " + winner + "/" + round, !snapshot.turnActive && !snapshot.roundActive);
            if (round == 1)
            {
                Check("no premature match winner " + winner, snapshot.matchWinnerMask == 0 && fixture.IsWaitingRound());
                Check("outcome next round " + winner, fixture.BeginNextRound());
                Check("outcome next starter " + winner, Current(fixture) == (winner == 3 ? 2 : winner));
            }
        }
        snapshot = fixture.Snapshot();
        Check("final mask " + winner, snapshot.matchWinnerMask == winner && !fixture.IsWaitingRound());
        Check("ended match cannot advance " + winner, !fixture.BeginNextRound());
        Check("ended match cannot act " + winner, !fixture.Pass(1) && !fixture.Pass(2) && !fixture.Play(1, 211, 1) && !fixture.UseLeader(2));
        Check("outcome not fatal " + winner, !fixture.IsFatal());
        fixture.InitializeFixture();
        snapshot = fixture.Snapshot();
        Check("restart resets outcome " + winner, snapshot.matchWinnerMask == 0 && snapshot.roundNumber == 1 && snapshot.currentPlayerId == 1 && snapshot.playerOne.crowns == 0 && snapshot.playerTwo.crowns == 0);
        Check("restart resets cards " + winner, fixture.CountLocation(1, 8) == 6 && fixture.CountLocation(2, 8) == 6 && fixture.CountLocation(1, 32) == 0 && fixture.CountLocation(2, 32) == 0);
    }

    public function GetSummary() : string
    {
        return "BOARD_CHECK_DONE checks=" + checks + " passed=" + (checks - failures) + " failed=" + failures;
    }

    public function GetDisplaySummary() : string
    {
        return "Поле: " + (checks - failures) + "/" + checks + ", ошибок: " + failures;
    }

    public function Run()
    {
        checks = 0;
        failures = 0;
        LogChannel('BetaGwent', "BOARD_CHECK_BEGIN fixture=true");
        CheckActions();
        CheckOutcome(1);
        CheckOutcome(2);
        CheckOutcome(3);
        LogChannel('BetaGwent', GetSummary());
    }
}
