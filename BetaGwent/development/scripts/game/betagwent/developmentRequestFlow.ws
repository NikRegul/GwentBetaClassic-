// Interactive boundary fixture. Uses accepted request/continuation core, but
// does not execute card effects, mutate the board, or implement Beta rollback.
struct SBetaGwentDevelopmentRequestCard
{
    var id : int;
    var title : string;
    var templateId : int;
    var factionId : int;
    var revealed : bool;
    var selected : bool;
}

class CBetaGwentDevelopmentRequestFlow extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var pending : CBetaGwentCardRequest;
    public var continuation : CBetaGwentAbilityContinuation;
    public var store : CBetaGwentRequestStore;
    public var nextRequestId : int;
    public var completed : int;
    public var aborted : int;
    public var sourceCards : array<SBetaGwentDevelopmentCard>;
    public var lastResult : array<int>;
    public var message : string;
    public var isolatedCheck : bool;
    public function SetIsolatedCheckMode() { isolatedCheck = true; }
    private function Trace(text : string)
    {
        if (isolatedCheck) BetaGwentLog("REQUEST_FIXTURE_" + text);
        else BetaGwentLog("REQUEST_FLOW_" + text);
    }

    public function IsPending() : bool { if (pending) return true; return false; }
    public function CompletedCount() : int { return completed; }
    public function AbortedCount() : int { return aborted; }
    public function GetMessage() : string { return message; }
    public function Snapshot() : SBetaGwentRequestSnapshot
    {
        var empty : SBetaGwentRequestSnapshot;
        if (pending) return pending.Snapshot();
        return empty;
    }
    public function Matches(requestId : int, playerId : int, kind : int) : bool
    {
        var snapshot : SBetaGwentRequestSnapshot;
        if (!pending) return false;
        snapshot = pending.Snapshot();
        return snapshot.requestId == requestId && snapshot.playerId == playerId && (int)snapshot.kind == kind;
    }

    public function Begin(kind : int, cards : array<SBetaGwentDevelopmentCard>) : bool
    {
        var choices : array<SBetaGwentChoiceCandidate>;
        var targets : array<int>;
        var candidate : SBetaGwentChoiceCandidate;
        var cardView : SBetaGwentDevelopmentCard;
        var i : int;
        var created : bool;
        if (pending || (kind != 1 && kind != 2)) return false;
        for (i = 0; i < cards.Size(); i += 1)
        {
            cardView = cards[i];
            if (cardView.card.isWaitingToDie) continue;
            if (kind == 1 && cardView.card.locationMask == 8)
            {
                candidate.originalInstanceId = cardView.card.instanceId;
                candidate.positionPlayerId = cardView.card.positionPlayerId;
                candidate.templateId = cardView.card.runtimeTemplate.templateId;
                candidate.deckFactionId = cardView.card.runtimeTemplate.factionMask;
                choices.PushBack(candidate);
            }
            // Only cards already visible to the human may enter this target demo.
            if (kind == 2 && ((cardView.card.locationMask == 8 && cardView.card.positionPlayerId == 1)
                || cardView.card.locationMask == 1 || cardView.card.locationMask == 2 || cardView.card.locationMask == 4))
                targets.PushBack(cardView.card.instanceId);
        }
        nextRequestId += 1;
        pending = new CBetaGwentCardRequest in this;
        if (kind == 1) created = pending.InitializeChoices(nextRequestId, 1, 1, choices, 1, 2, false);
        else created = pending.InitializeTargets(nextRequestId, 1, 1, targets, 2, 2) && pending.ApplyTargets(targets);
        if (!created) { pending = NULL; return false; }
        continuation = new CBetaGwentAbilityContinuation in this;
        store = new CBetaGwentRequestStore in this;
        if (!continuation.Initialize(nextRequestId) || !continuation.BeginNode(1)
            || !continuation.PauseOn(pending) || !store.Add(pending, continuation))
        { pending.Destroy(); pending = NULL; return false; }
        sourceCards = cards;
        lastResult.Clear();
        if (kind == 1) message = "Выберите 1–2 карты. Чужая рука скрыта. Это тест выбора без эффекта.";
        else message = "Выберите две подсвеченные карты на поле или в своей руке. Это тест целей без эффекта.";
        Trace("BEGIN id=" + nextRequestId + " player=1 kind=" + kind);
        return true;
    }

    public function CanFinish() : bool
    {
        var snapshot : SBetaGwentRequestSnapshot;
        if (!pending) return false;
        snapshot = pending.Snapshot();
        return BetaGwentRequestCanFinish(snapshot.limits.minimum, snapshot.limits.maximum, snapshot.selectedCount);
    }
    public function IsTarget(value : int) : bool
    {
        var ids : array<int>;
        if (!pending || !pending.GetTargetViews(1, ids)) return false;
        return BetaGwentRequestContains(ids, value);
    }
    public function IsSelected(value : int) : bool { return pending && pending.IsSelected(value); }

    public function Select(requestId : int, playerId : int, kind : int, value : int) : bool
    {
        var shape : array<int>;
        var accepted : bool;
        if (!Matches(requestId, playerId, kind)) return false;
        if (kind == 2) shape.PushBack(value); // Single-card shape, not an AoE engine.
        if (pending.IsSelected(value)) accepted = pending.Deselect(value, shape);
        else if (kind == 1) accepted = pending.SelectChoice(value);
        else accepted = pending.SelectTarget(value, shape);
        if (!accepted) return false;
        Trace("SELECT id=" + requestId + " player=" + playerId + " kind=" + kind + " item=" + value);
        return CompleteIfFulfilled();
    }

    public function Finish(requestId : int, playerId : int, kind : int) : bool
    {
        if (!Matches(requestId, playerId, kind) || !pending.Finish()) return false;
        return CompleteIfFulfilled();
    }
    private function CompleteIfFulfilled() : bool
    {
        var shape : array<int>;
        var snapshot : SBetaGwentRequestSnapshot;
        if (!pending.IsFulfilled()) return true;
        snapshot = pending.Snapshot();
        if (!store.UpdateOne() || !continuation.CompleteRequestNode(lastResult, shape))
        {
            Trace("ERROR completion failed");
            return false;
        }
        completed += 1;
        Trace("END id=" + snapshot.requestId + " kind=" + (int)snapshot.kind
            + " count=" + lastResult.Size() + " nodes=" + continuation.GetCompletedNodes());
        message = "Тест выбора завершён: карт " + lastResult.Size() + ". Поле и счёт сохранены.";
        pending = NULL; sourceCards.Clear();
        return true;
    }

    public function Abort(requestId : int, playerId : int, kind : int) : bool
    {
        if (!Matches(requestId, playerId, kind)) return false;
        continuation.Abort(); store.UpdateOne();
        pending = NULL; sourceCards.Clear(); lastResult.Clear(); aborted += 1;
        message = "Тестовый запрос прерван. Поле и счёт сохранены.";
        Trace("ABORT id=" + requestId);
        return true;
    }
    public function Close()
    {
        var snapshot : SBetaGwentRequestSnapshot;
        if (!pending) return;
        snapshot = pending.Snapshot();
        Abort(snapshot.requestId, snapshot.playerId, (int)snapshot.kind);
    }
    public function GetLastResult(out ids : array<int>)
    {
        var i : int;
        ids.Clear();
        for (i = 0; i < lastResult.Size(); i += 1) ids.PushBack(lastResult[i]);
    }
    public function GetViews(out views : array<SBetaGwentDevelopmentRequestCard>)
    {
        var choices : array<SBetaGwentChoiceView>;
        var ids : array<int>;
        var value : SBetaGwentDevelopmentRequestCard;
        var i : int;
        var j : int;
        views.Clear();
        if (!pending) return;
        if (pending.GetChoiceViews(1, choices))
            for (i = 0; i < choices.Size(); i += 1)
            {
                value.id = choices[i].choiceId; value.templateId = choices[i].templateId;
                value.factionId = choices[i].deckFactionId; value.revealed = choices[i].revealed;
                value.selected = pending.IsSelected(value.id); value.title = "Скрытая карта";
                if (value.revealed)
                    for (j = 0; j < sourceCards.Size(); j += 1)
                        if (sourceCards[j].card.positionPlayerId == 1 && sourceCards[j].card.runtimeTemplate.templateId == value.templateId)
                        { value.title = sourceCards[j].title; break; }
                views.PushBack(value);
            }
        else if (pending.GetTargetViews(1, ids))
            for (i = 0; i < ids.Size(); i += 1)
            {
                value.id = ids[i]; value.templateId = 0; value.factionId = 0;
                value.revealed = true; value.selected = pending.IsSelected(value.id); value.title = "Цель";
                views.PushBack(value);
            }
    }
}
