// Isolated request/continuation checks. Never mutate the displayed DEV match.
class CBetaGwentRequestChecks extends IScriptable
{
    private var checks : int;
    private var failures : int;

    private function Check(label : string, condition : bool)
    {
        checks += 1;
        if (condition) LogChannel('BetaGwent', "REQUEST_CHECK_PASS " + label);
        else { failures += 1; LogChannel('BetaGwent', "REQUEST_CHECK_FAIL " + label); }
    }

    private function Candidates(out values : array<SBetaGwentChoiceCandidate>)
    {
        var card : SBetaGwentChoiceCandidate;
        values.Clear();
        card.originalInstanceId = 41; card.positionPlayerId = 2; card.templateId = 401; card.deckFactionId = 5;
        values.PushBack(card);
        card.originalInstanceId = 42; card.positionPlayerId = 1; card.templateId = 402; card.deckFactionId = 3;
        values.PushBack(card);
        card.originalInstanceId = 43; card.positionPlayerId = 2; card.templateId = 403; card.deckFactionId = 5;
        values.PushBack(card);
        card.originalInstanceId = 44; card.positionPlayerId = 1; card.templateId = 404; card.deckFactionId = 3;
        values.PushBack(card);
    }

    private function CheckChoices()
    {
        var request : CBetaGwentCardRequest;
        var other : CBetaGwentCardRequest;
        var cards : array<SBetaGwentChoiceCandidate>;
        var views : array<SBetaGwentChoiceView>;
        var ids : array<int>;
        var shape : array<int>;
        var snapshot : SBetaGwentRequestSnapshot;
        var limits : SBetaGwentRequestLimits;
        Candidates(cards);
        request = new CBetaGwentCardRequest in this;
        Check("choices reject invalid player", !request.InitializeChoices(7, 3, 3, cards, 1, 2, false));
        Check("choices initialized", request.InitializeChoices(7, 1, 1, cards, 1, 2, false));
        Check("choices no second initialization", !request.InitializeChoices(8, 1, 1, cards, 0, 1, true));
        request.GetChoiceViews(1, views);
        Check("choices view count", views.Size() == 4);
        if (views.Size() == 4)
        {
            Check("choice IDs assigned before grouping", views[0].choiceId == 1001 && views[1].choiceId == 1003
                && views[2].choiceId == 1000 && views[3].choiceId == 1002);
            Check("own choices visible", views[0].revealed && views[0].templateId == 402);
            Check("enemy choice faction placeholder", !views[2].revealed && views[2].templateId == 0 && views[2].deckFactionId == 5);
            views[0].templateId = 999;
            request.GetChoiceViews(1, views);
            Check("choice view copy isolated", views[0].templateId == 402);
        }
        Check("choices reject original ID as UI ID", !request.SelectChoice(42));
        Check("choices reject finish below min", !request.Finish());
        Check("choices select valid ID", request.SelectChoice(1003));
        Check("choices reject duplicate", !request.SelectChoice(1003));
        Check("choices second valid ID", request.SelectChoice(1000));
        Check("choices finished at max", request.IsFulfilled());
        Check("choices reject over max", !request.SelectChoice(1001));
        Check("choice maps to original in selected order", request.CopyResult(ids, shape) && ids.Size() == 2);
        if (ids.Size() == 2) Check("choice original identity", ids[0] == 44 && ids[1] == 41);
        Check("choice deselect accepted before manager update", request.Deselect(1003, shape));
        Check("choice finished flag remains set", request.IsFulfilled());
        request.CopyResult(ids, shape);
        Check("choice result reflects deselect", ids.Size() == 1 && ids[0] == 41);
        snapshot = request.Snapshot(); snapshot.limits.maximum = 999;
        snapshot = request.Snapshot();
        Check("request snapshot copy isolated", snapshot.limits.maximum == 2);
        other = new CBetaGwentCardRequest in this;
        Check("choices max0 creates no request", !other.InitializeChoices(8, 1, 1, cards, 0, 0, false));
        cards.Clear();
        Check("empty choices create no request", !other.InitializeChoices(8, 1, 1, cards, 0, 2, false));
        limits = BetaGwentChoiceLimits(4, 3, 2);
        Check("choice min is not clamped to max", limits.minimum == 3 && limits.maximum == 2);
        limits = BetaGwentChoiceLimits(4, -2, 9);
        Check("choice limits bounded by pool", limits.minimum == 0 && limits.maximum == 4);
        Check("reveal enabled when target equals request owner", BetaGwentChoiceIsRevealed(2, 1, 1, true));
        Check("reveal flag does not reveal in mirrored request", !BetaGwentChoiceIsRevealed(1, 2, 1, true));
        request.Destroy();
        Check("destroyed choice cannot select", !request.SelectChoice(1001));
        request.GetChoiceViews(1, views);
        Check("destroy clears views", views.Size() == 0);
    }

    private function CheckTargets()
    {
        var request : CBetaGwentCardRequest;
        var empty : CBetaGwentCardRequest;
        var valid : array<int>;
        var alive : array<int>;
        var shape : array<int>;
        var ids : array<int>;
        var area : array<int>;
        var snapshot : SBetaGwentRequestSnapshot;
        valid.PushBack(51); valid.PushBack(52); valid.PushBack(53);
        alive.PushBack(51); alive.PushBack(53);
        request = new CBetaGwentCardRequest in this;
        Check("targets create", request.InitializeTargets(20, 1, 1, valid, 1, 3));
        Check("targets cannot select before Apply", !request.SelectTarget(51, shape));
        Check("targets apply after one death", request.ApplyTargets(alive));
        snapshot = request.Snapshot();
        Check("target min equals max after death", snapshot.limits.minimum == 2 && snapshot.limits.maximum == 2 && snapshot.validCount == 2);
        Check("target apply cannot repeat", !request.ApplyTargets(alive));
        Check("dead target rejected", !request.SelectTarget(52, shape));
        Check("null target rejected", !request.SelectTarget(0, shape));
        shape.PushBack(61); shape.PushBack(62); shape.PushBack(0);
        Check("first target accepted", request.SelectTarget(53, shape));
        Check("duplicate target rejected", !request.SelectTarget(53, shape));
        Check("target finish below post-Apply min rejected", !request.Finish());
        shape.Clear(); shape.PushBack(62); shape.PushBack(63);
        Check("second target accepted", request.SelectTarget(51, shape));
        Check("targets fulfilled at max", request.IsFulfilled());
        request.CopyResult(ids, area);
        Check("selected target order preserved", ids.Size() == 2 && ids[0] == 53 && ids[1] == 51);
        Check("shape duplicates retained; null skipped", area.Size() == 4 && area[0] == 61 && area[1] == 62 && area[2] == 62 && area[3] == 63);
        Check("target deselect uses supplied current shape", request.Deselect(53, shape));
        Check("target deselect does not unfinish", request.IsFulfilled());
        request.CopyResult(ids, area);
        Check("shape removes one occurrence per current card", area.Size() == 2 && area[0] == 61 && area[1] == 62);
        empty = new CBetaGwentCardRequest in this;
        Check("all-dead targets setup", empty.InitializeTargets(21, 1, 1, valid, 0, 3));
        alive.Clear();
        Check("all-dead targets Apply", empty.ApplyTargets(alive));
        Check("all-dead request immediately fulfilled", empty.IsFulfilled());
        Check("all-dead empty result valid", empty.CopyResult(ids, area) && ids.Size() == 0 && area.Size() == 0);
    }

    private function CheckContinuation()
    {
        var first : CBetaGwentCardRequest;
        var second : CBetaGwentCardRequest;
        var unrelated : CBetaGwentCardRequest;
        var firstFlow : CBetaGwentAbilityContinuation;
        var secondFlow : CBetaGwentAbilityContinuation;
        var store : CBetaGwentRequestStore;
        var candidates : array<SBetaGwentChoiceCandidate>;
        var ids : array<int>;
        var area : array<int>;
        Candidates(candidates);
        first = new CBetaGwentCardRequest in this;
        second = new CBetaGwentCardRequest in this;
        unrelated = new CBetaGwentCardRequest in this;
        firstFlow = new CBetaGwentAbilityContinuation in this;
        secondFlow = new CBetaGwentAbilityContinuation in this;
        store = new CBetaGwentRequestStore in this;
        Check("first request create", first.InitializeChoices(30, 1, 1, candidates, 1, 1, false));
        Check("other player request create", second.InitializeChoices(31, 2, 2, candidates, 1, 1, false));
        Check("unrelated request create", unrelated.InitializeChoices(32, 1, 1, candidates, 1, 1, false));
        Check("first continuation initialize", firstFlow.Initialize(100));
        Check("second continuation initialize", secondFlow.Initialize(200));
        Check("first node setup", firstFlow.BeginNode(10));
        Check("first node pauses", firstFlow.PauseOn(first));
        Check("node cannot setup twice while paused", !firstFlow.BeginNode(10));
        Check("second node setup", secondFlow.BeginNode(10));
        Check("second node pauses", secondFlow.PauseOn(second));
        Check("first store add", store.Add(first, firstFlow));
        Check("second store add", store.Add(second, secondFlow));
        Check("duplicate store key rejected", !store.Add(first, firstFlow));
        Check("lookup binds player", store.Find(30, 1, BG_RequestChoices) == first && store.Find(31, 2, BG_RequestChoices) == second);
        Check("lookup rejects wrong player", !store.Find(30, 2, BG_RequestChoices));
        Check("lookup rejects wrong request kind", !store.Find(30, 1, BG_RequestTargets));
        Check("lookup rejects stale ID", !store.Find(32, 1, BG_RequestChoices));
        Check("unfinished request cannot resume", !firstFlow.ResumeFor(first));
        Check("foreign request cannot resume", !firstFlow.ResumeFor(unrelated));
        Check("unfinished manager update makes no progress", !store.UpdateOne());
        Check("first complete selection", first.SelectChoice(1001));
        Check("second complete selection", second.SelectChoice(1000));
        Check("manager consumes one fulfilled", store.UpdateOne() && store.Count() == 1);
        Check("front inserted continuation resumed first", secondFlow.GetAbilityState() == BG_AbilityRunning && firstFlow.GetAbilityState() == BG_AbilityPaused);
        Check("node AutoDestroy false preserves result", !second.IsDestroyed());
        Check("same node setup not repeated after resume", !secondFlow.BeginNode(10));
        Check("node copies result then destroys", secondFlow.CompleteRequestNode(ids, area) && second.IsDestroyed());
        Check("resumed node selected original mapping", ids.Size() == 1 && ids[0] == 41);
        Check("node advances exactly once", secondFlow.GetCompletedNodes() == 1 && !secondFlow.CompleteRequestNode(ids, area));
        Check("next node may setup", secondFlow.BeginNode(11) && secondFlow.GetNodeId() == 11);
        Check("manager consumes next fulfilled separately", store.UpdateOne() && store.Count() == 0);
        Check("other node owns separate result", firstFlow.CompleteRequestNode(ids, area) && ids.Size() == 1 && ids[0] == 42);
        Check("detached request not found", !store.Find(30, 1, BG_RequestChoices));
        Check("new request can reuse completed node owner", firstFlow.BeginNode(11) && firstFlow.PauseOn(unrelated));
        Check("pending abort registered", store.Add(unrelated, firstFlow));
        firstFlow.Abort();
        Check("abort destroys own pending", unrelated.IsDestroyed() && firstFlow.GetAbilityState() == BG_AbilityAborted);
        Check("manager removes destroyed separately", store.UpdateOne() && store.Count() == 0);
        Check("aborted continuation cannot setup", !firstFlow.BeginNode(12));
        Check("empty manager does not progress", !store.UpdateOne());
    }

    private function CheckLookupRoles()
    {
        var request : CBetaGwentCardRequest;
        var shadow : CBetaGwentCardRequest;
        var mirror : CBetaGwentCardRequest;
        var target : CBetaGwentCardRequest;
        var store : CBetaGwentRequestStore;
        var cards : array<SBetaGwentChoiceCandidate>;
        var views : array<SBetaGwentChoiceView>;
        var ids : array<int>;
        Candidates(cards);
        request = new CBetaGwentCardRequest in this;
        shadow = new CBetaGwentCardRequest in this;
        target = new CBetaGwentCardRequest in this;
        store = new CBetaGwentRequestStore in this;
        Check("request owner differs from view target", request.InitializeChoices(40, 1, 2, cards, 1, 2, false));
        Check("role request store", store.Add(request, NULL));
        Check("lookup uses owner PlayerId", store.Find(40, 1, BG_RequestChoices) == request && !store.Find(40, 2, BG_RequestChoices));
        Check("view target receives choices", request.GetChoiceViews(2, views) && views.Size() == 4);
        Check("other view recipient gets no choices", !request.GetChoiceViews(1, views) && views.Size() == 0);
        mirror = new CBetaGwentCardRequest in this;
        Check("reveal mirrored request create", mirror.InitializeChoices(41, 1, 2, cards, 1, 2, true));
        mirror.GetChoiceViews(2, views);
        Check("reveal uses request owner rather than recipient", views.Size() == 4 && views[0].revealed && !views[2].revealed && views[2].templateId == 0);
        // Deliberate duplicate-ID fixture, to verify original first-ID behavior.
        Check("shadow request create", shadow.InitializeChoices(40, 2, 2, cards, 1, 2, false));
        Check("shadow request stored at front", store.Add(shadow, NULL));
        Check("first ID shadows later player match", !store.Find(40, 1, BG_RequestChoices));
        Check("first ID same player resolves", store.Find(40, 2, BG_RequestChoices) == shadow);
        Check("player0 means no player filter", store.Find(40, 0, BG_RequestChoices) == shadow);
        ids.PushBack(51);
        Check("other type same ID create", target.InitializeTargets(40, 1, 1, ids, 0, 1));
        Check("other type same ID stores at front", store.Add(target, NULL));
        Check("first ID wrong type does not scan later", !store.Find(40, 2, BG_RequestChoices));
        Check("first ID matching target type resolves", store.Find(40, 1, BG_RequestTargets) == target);
    }

    // GENERATED_ORACLE_LIMITS: produced by tools/core-check/generate_request_limits.py
    private function CheckCopiedILLimits()
    {
        var limits : SBetaGwentRequestLimits;
        limits = BetaGwentAppliedTargetLimits(0, 3, 0, false);
        Check("copied IL targets/all-dead", limits.minimum == 0 && limits.maximum == 0 && limits.finished == true);
        limits = BetaGwentAppliedTargetLimits(2, 4, 0, false);
        Check("copied IL targets/two-survive", limits.minimum == 2 && limits.maximum == 2 && limits.finished == false);
        limits = BetaGwentAppliedTargetLimits(5, 2, 0, false);
        Check("copied IL targets/max-smaller-than-pool", limits.minimum == 2 && limits.maximum == 2 && limits.finished == false);
        limits = BetaGwentAppliedTargetLimits(3, 2, 2, false);
        Check("copied IL targets/selected-at-max", limits.minimum == 2 && limits.maximum == 2 && limits.finished == true);
        limits = BetaGwentAppliedTargetLimits(3, 2, 0, true);
        Check("copied IL targets/sticky-finished", limits.minimum == 2 && limits.maximum == 2 && limits.finished == true);
        limits = BetaGwentAppliedTargetLimits(4, 0, 0, false);
        Check("copied IL targets/zero-max", limits.minimum == 0 && limits.maximum == 0 && limits.finished == true);
        Check("copied IL target-finish/below-min", (false || BetaGwentRequestCanFinish(2, 2, 1)) == false);
        Check("copied IL target-finish/at-min", (false || BetaGwentRequestCanFinish(1, 2, 1)) == true);
        Check("copied IL target-finish/above-max", (false || BetaGwentRequestCanFinish(1, 2, 3)) == false);
        Check("copied IL target-finish/empty-allowed", (false || BetaGwentRequestCanFinish(0, 2, 0)) == true);
        Check("copied IL target-finish/sticky", (true || BetaGwentRequestCanFinish(1, 2, 0)) == true);
        Check("copied IL choice-finish/below-min", BetaGwentRequestCanFinish(1, 2, 0) == false);
        Check("copied IL choice-finish/at-min", BetaGwentRequestCanFinish(1, 2, 1) == true);
        Check("copied IL choice-finish/at-max", BetaGwentRequestCanFinish(1, 2, 2) == true);
        Check("copied IL choice-finish/above-max", BetaGwentRequestCanFinish(1, 2, 3) == false);
        Check("copied IL choice-finish/min-exceeds-max", BetaGwentRequestCanFinish(3, 2, 2) == false);
        Check("copied IL choice-finish/empty-allowed", BetaGwentRequestCanFinish(0, 2, 0) == true);
        Check("copied IL choice-finish/sticky-outside-range", BetaGwentRequestCanFinish(1, 2, 0) == false);
    }

    public function GetDisplaySummary() : string
    { return "Запросы: " + (checks - failures) + "/" + checks + ", ошибок: " + failures; }

    public function Run()
    {
        checks = 0; failures = 0;
        LogChannel('BetaGwent', "REQUEST_CHECK_BEGIN schema=1");
        CheckCopiedILLimits(); CheckChoices(); CheckTargets(); CheckContinuation(); CheckLookupRoles();
        LogChannel('BetaGwent', "REQUEST_CHECK_DONE checks=" + checks + " passed=" + (checks - failures) + " failed=" + failures);
    }
}

exec function bgrequest_test()
{
    var runner : CBetaGwentRequestChecks;
    if (!thePlayer) { LogChannel('BetaGwent', "REQUEST_CHECK_SKIPPED no player"); return; }
    runner = new CBetaGwentRequestChecks in thePlayer;
    runner.Run();
}
