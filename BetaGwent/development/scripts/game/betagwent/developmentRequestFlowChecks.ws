class CBetaGwentRequestFlowChecks extends IScriptable
{
    private var checks : int;
    private var failures : int;
    private function Check(label : string, condition : bool)
    {
        checks += 1;
        if (condition) LogChannel('BetaGwent', "FLOW_CHECK_PASS " + label);
        else { failures += 1; LogChannel('BetaGwent', "FLOW_CHECK_FAIL " + label); }
    }
    public function Run()
    {
        var board : CBetaGwentDevelopmentBoardSession;
        var flow : CBetaGwentDevelopmentRequestFlow;
        var empty : CBetaGwentDevelopmentRequestFlow;
        var cards : array<SBetaGwentDevelopmentCard>;
        var noCards : array<SBetaGwentDevelopmentCard>;
        var views : array<SBetaGwentDevelopmentRequestCard>;
        var resultIds : array<int>;
        var snapshot : SBetaGwentRequestSnapshot;
        checks = 0; failures = 0;
        board = new CBetaGwentDevelopmentBoardSession in this;
        flow = new CBetaGwentDevelopmentRequestFlow in this;
        empty = new CBetaGwentDevelopmentRequestFlow in this;
        flow.SetIsolatedCheckMode(); empty.SetIsolatedCheckMode();
        board.InitializeFixture(); board.GetCards(cards);
        Check("new flow not pending", !flow.IsPending());
        Check("invalid request kind rejected", !flow.Begin(3, cards));
        Check("empty choices rejected", !empty.Begin(1, noCards) && !empty.IsPending());
        Check("empty targets rejected", !empty.Begin(2, noCards) && !empty.IsPending());
        Check("choices begin", flow.Begin(1, cards));
        Check("pending blocks nested begin", !flow.Begin(2, cards));
        snapshot = flow.Snapshot();
        Check("request1 key", snapshot.requestId == 1 && snapshot.playerId == 1 && snapshot.kind == BG_RequestChoices);
        flow.GetViews(views);
        Check("twelve choices", views.Size() == 12);
        if (views.Size() == 12)
        {
            Check("own choice revealed", views[0].revealed && views[0].title == "DEV 1");
            Check("enemy choice hidden metadata", !views[6].revealed && views[6].templateId == 0 && views[6].title == "Скрытая карта");
            Check("view synthetic ID differs from source", views[6].id == 1006);
        }
        Check("no finish before min", !flow.CanFinish() && !flow.Finish(1, 1, 1));
        Check("stale ID rejected", !flow.Select(9, 1, 1, 1000));
        Check("wrong player rejected", !flow.Select(1, 2, 1, 1000));
        Check("wrong type rejected", !flow.Select(1, 1, 2, 1000));
        Check("original ID not choice intent", !flow.Select(1, 1, 1, 110));
        Check("hidden choice selected", flow.Select(1, 1, 1, 1006));
        Check("selected view reflected", flow.IsSelected(1006) && flow.CanFinish());
        Check("choice toggle deselect", flow.Select(1, 1, 1, 1006) && !flow.IsSelected(1006) && !flow.CanFinish());
        Check("choice reselect", flow.Select(1, 1, 1, 1006));
        Check("finish resumes one node", flow.Finish(1, 1, 1) && !flow.IsPending() && flow.CompletedCount() == 1);
        flow.GetLastResult(resultIds);
        Check("hidden choice maps original after completion", resultIds.Size() == 1 && resultIds[0] == 120);
        Check("detached response rejected", !flow.Select(1, 1, 1, 1000) && !flow.Finish(1, 1, 1));
        flow.GetViews(views);
        Check("completion clears views", views.Size() == 0);
        Check("targets begin", flow.Begin(2, cards));
        snapshot = flow.Snapshot();
        Check("target key2 and clamp", snapshot.requestId == 2 && snapshot.limits.minimum == 2 && snapshot.limits.maximum == 2);
        flow.GetViews(views);
        Check("hidden enemy hand excluded from targets", views.Size() == 6 && !flow.IsTarget(120));
        Check("own hand available target", flow.IsTarget(110));
        Check("invalid target rejected", !flow.Select(2, 1, 2, 120));
        Check("first target", flow.Select(2, 1, 2, 110) && flow.IsPending() && !flow.CanFinish());
        Check("target toggle deselect", flow.Select(2, 1, 2, 110) && !flow.IsSelected(110));
        Check("target reselect", flow.Select(2, 1, 2, 110));
        Check("max completes automatically", flow.Select(2, 1, 2, 111) && !flow.IsPending() && flow.CompletedCount() == 2);
        flow.GetLastResult(resultIds);
        Check("target result order", resultIds.Size() == 2 && resultIds[0] == 110 && resultIds[1] == 111);
        Check("third request begin", flow.Begin(1, cards));
        Check("abort stale key rejected", !flow.Abort(2, 1, 1) && flow.IsPending());
        flow.Close();
        Check("close aborts only pending flow", !flow.IsPending() && flow.AbortedCount() == 1 && flow.CompletedCount() == 2);
        flow.GetLastResult(resultIds);
        Check("abort clears result", resultIds.Size() == 0);
        Check("next request fresh ID", flow.Begin(1, cards) && flow.Matches(4, 1, 1));
        Check("old response cannot hit new request", !flow.Select(3, 1, 1, 1000));
        Check("fourth request select", flow.Select(4, 1, 1, 1000));
        Check("fourth request abort", flow.Abort(4, 1, 1) && flow.AbortedCount() == 2);
        Check("board state untouched", board.Score(1) == 0 && board.Score(2) == 0 && board.CountLocation(1, 8) == 6);
        LogChannel('BetaGwent', "FLOW_CHECK_DONE checks=" + checks + " passed=" + (checks - failures) + " failed=" + failures);
    }
    public function GetDisplaySummary() : string
    { return "Выбор UI: " + (checks - failures) + "/" + checks + ", ошибок: " + failures; }
}
