// Memory-local card requests. Original event bus, card cloning, timeout RNG and
// cancellation/rollback are deliberately left to the future coordinator.
// Request kind and guards below are mod-local; ability-state values are original.
enum EBetaGwentCardRequestKind
{
    BG_RequestChoices = 1,
    BG_RequestTargets = 2
}

struct SBetaGwentRequestLimits
{
    var minimum : int;
    var maximum : int;
    var finished : bool;
}

struct SBetaGwentChoiceCandidate
{
    var originalInstanceId : int;
    var positionPlayerId : int;
    var templateId : int;
    var deckFactionId : int;
}

// No original ID is exported to the view, including for a hidden card.
struct SBetaGwentChoiceView
{
    var choiceId : int;
    var revealed : bool;
    var templateId : int;
    var deckFactionId : int;
}

struct SBetaGwentChoiceEntry
{
    var view : SBetaGwentChoiceView;
    var originalInstanceId : int;
    var positionPlayerId : int;
}

struct SBetaGwentRequestSnapshot
{
    var initialized : bool;
    var requestId : int;
    var playerId : int;
    var targetPlayerId : int;
    var kind : EBetaGwentCardRequestKind;
    var limits : SBetaGwentRequestLimits;
    var selectedCount : int;
    var validCount : int;
    var applied : bool;
    var destroyed : bool;
    var autoDestroy : bool;
}

function BetaGwentChoiceLimits(validCount : int, minimum : int, maximum : int) : SBetaGwentRequestLimits
{
    var result : SBetaGwentRequestLimits;
    result.maximum = Min(validCount, maximum);
    result.minimum = Min(validCount, Max(0, minimum));
    result.finished = result.maximum <= 0;
    return result;
}

function BetaGwentAppliedTargetLimits(validCount : int, maximum : int,
    selectedCount : int, alreadyFinished : bool) : SBetaGwentRequestLimits
{
    var result : SBetaGwentRequestLimits;
    result.maximum = Min(maximum, validCount);
    result.minimum = result.maximum;
    result.finished = alreadyFinished || selectedCount == result.maximum;
    return result;
}

function BetaGwentRequestCanFinish(minimum : int, maximum : int, selectedCount : int) : bool
{
    return selectedCount >= minimum && selectedCount <= maximum;
}

function BetaGwentChoiceIsRevealed(positionPlayerId : int, targetPlayerId : int,
    requestPlayerId : int, revealChoices : bool) : bool
{
    return positionPlayerId == targetPlayerId || (revealChoices && targetPlayerId == requestPlayerId);
}

function BetaGwentRequestContains(ids : array<int>, value : int) : bool
{
    var i : int;
    for (i = 0; i < ids.Size(); i += 1)
        if (ids[i] == value) return true;
    return false;
}

class CBetaGwentCardRequest extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var requestState : SBetaGwentRequestSnapshot;
    public var choices : array<SBetaGwentChoiceEntry>;
    public var validTargets : array<int>;
    public var selected : array<int>;
    public var targetsInShape : array<int>;

    private function CanInitialize(requestId : int, playerId : int, targetPlayerId : int) : bool
    {
        return !requestState.initialized && requestId > 0 && BetaGwentIsPlayerId(playerId) && BetaGwentIsPlayerId(targetPlayerId);
    }

    public function InitializeChoices(requestId : int, playerId : int, targetPlayerId : int,
        candidates : array<SBetaGwentChoiceCandidate>, minimum : int, maximum : int, revealChoices : bool) : bool
    {
        var choiceEntry : SBetaGwentChoiceEntry;
        var i : int;
        var j : int;
        var index : int;
        if (!CanInitialize(requestId, playerId, targetPlayerId)) return false;
        // CreateAction returns null for empty choices or max==0. The upper size
        // guard is local: do not wrap synthetic ushort IDs in an invalid input.
        if (candidates.Size() == 0 || maximum == 0 || candidates.Size() > 64536) return false;
        for (i = 0; i < candidates.Size(); i += 1)
            if (candidates[i].originalInstanceId <= 0) return false;
        for (i = 0; i < candidates.Size(); i += 1)
        {
            choiceEntry.originalInstanceId = candidates[i].originalInstanceId;
            choiceEntry.positionPlayerId = candidates[i].positionPlayerId;
            choiceEntry.view.choiceId = 1000 + i;
            choiceEntry.view.deckFactionId = candidates[i].deckFactionId;
            choiceEntry.view.revealed = BetaGwentChoiceIsRevealed(choiceEntry.positionPlayerId, targetPlayerId, playerId, revealChoices);
            choiceEntry.view.templateId = 0;
            if (choiceEntry.view.revealed) choiceEntry.view.templateId = candidates[i].templateId;
            // Assign IDs before stable target-side grouping, as original Init.
            index = choices.Size();
            if (choiceEntry.positionPlayerId == targetPlayerId)
            {
                index = 0;
                for (j = choices.Size() - 1; j >= 0; j -= 1)
                    if (choices[j].positionPlayerId == targetPlayerId) { index = j + 1; break; }
            }
            choices.PushBack(choiceEntry);
            for (j = choices.Size() - 1; j > index; j -= 1) choices[j] = choices[j - 1];
            choices[index] = choiceEntry;
        }
        requestState.initialized = true;
        requestState.kind = BG_RequestChoices;
        requestState.requestId = requestId;
        requestState.playerId = playerId;
        requestState.targetPlayerId = targetPlayerId;
        requestState.limits = BetaGwentChoiceLimits(choices.Size(), minimum, maximum);
        requestState.validCount = choices.Size();
        requestState.applied = true;
        requestState.autoDestroy = true;
        return true;
    }

    public function InitializeTargets(requestId : int, playerId : int, targetPlayerId : int, ids : array<int>,
        minimum : int, maximum : int) : bool
    {
        var i : int;
        if (!CanInitialize(requestId, playerId, targetPlayerId) || ids.Size() == 0 || maximum <= 0) return false;
        for (i = 0; i < ids.Size(); i += 1) if (ids[i] <= 0) return false;
        for (i = 0; i < ids.Size(); i += 1) validTargets.PushBack(ids[i]);
        requestState.initialized = true;
        requestState.kind = BG_RequestTargets;
        requestState.requestId = requestId;
        requestState.playerId = playerId;
        requestState.targetPlayerId = targetPlayerId;
        requestState.limits.minimum = Min(Max(0, minimum), maximum);
        requestState.limits.maximum = maximum;
        requestState.validCount = ids.Size();
        requestState.autoDestroy = true;
        return true;
    }

    // Coordinator supplies IDs whose cards are alive at Apply, not at Setup.
    public function ApplyTargets(aliveIds : array<int>) : bool
    {
        var i : int;
        if (!requestState.initialized || requestState.destroyed || requestState.applied || requestState.kind != BG_RequestTargets) return false;
        for (i = validTargets.Size() - 1; i >= 0; i -= 1)
            if (!BetaGwentRequestContains(aliveIds, validTargets[i])) validTargets.Erase(i);
        requestState.validCount = validTargets.Size();
        requestState.limits = BetaGwentAppliedTargetLimits(validTargets.Size(), requestState.limits.maximum,
            selected.Size(), requestState.limits.finished);
        requestState.applied = true;
        return true;
    }

    public function Snapshot() : SBetaGwentRequestSnapshot
    {
        var result : SBetaGwentRequestSnapshot;
        result = requestState;
        result.selectedCount = selected.Size();
        return result;
    }

    public function Matches(requestId : int, playerId : int, kind : EBetaGwentCardRequestKind) : bool
    {
        return requestState.initialized && !requestState.destroyed && requestState.requestId == requestId
            && requestState.playerId == playerId && requestState.kind == kind;
    }

    public function SetAutoDestroy(value : bool) { requestState.autoDestroy = value; }
    public function IsFulfilled() : bool { return requestState.initialized && requestState.applied && !requestState.destroyed && requestState.limits.finished; }
    public function IsDestroyed() : bool { return requestState.destroyed; }
    public function AutoDestroy() : bool { return requestState.autoDestroy; }
    public function IsSelected(value : int) : bool
    { return requestState.initialized && !requestState.destroyed && BetaGwentRequestContains(selected, value); }

    public function GetTargetViews(receivingPlayerId : int, out ids : array<int>) : bool
    {
        var i : int;
        ids.Clear();
        if (!requestState.initialized || requestState.destroyed || !requestState.applied
            || requestState.kind != BG_RequestTargets || receivingPlayerId != requestState.targetPlayerId) return false;
        for (i = 0; i < validTargets.Size(); i += 1) ids.PushBack(validTargets[i]);
        return true;
    }

    private function ChoiceOriginal(choiceId : int) : int
    {
        var i : int;
        for (i = 0; i < choices.Size(); i += 1)
            if (choices[i].view.choiceId == choiceId) return choices[i].originalInstanceId;
        return 0;
    }

    public function SelectChoice(choiceId : int) : bool
    {
        if (!requestState.initialized || requestState.destroyed || requestState.kind != BG_RequestChoices) return false;
        if (selected.Size() >= requestState.limits.maximum || ChoiceOriginal(choiceId) == 0
            || BetaGwentRequestContains(selected, choiceId)) return false;
        selected.PushBack(choiceId);
        if (!requestState.limits.finished) requestState.limits.finished = selected.Size() == requestState.limits.maximum;
        return true;
    }

    public function SelectTarget(cardId : int, shapeIds : array<int>) : bool
    {
        var i : int;
        if (!requestState.initialized || requestState.destroyed || !requestState.applied || requestState.kind != BG_RequestTargets) return false;
        if (cardId <= 0 || BetaGwentRequestContains(selected, cardId) || !BetaGwentRequestContains(validTargets, cardId)
            || selected.Size() >= requestState.limits.maximum) return false;
        selected.PushBack(cardId);
        // The adapter represents a missing Card as ID0; ListExt.AddCards skips nulls.
        for (i = 0; i < shapeIds.Size(); i += 1)
            if (shapeIds[i] > 0) targetsInShape.PushBack(shapeIds[i]);
        if (!requestState.limits.finished) requestState.limits.finished = selected.Size() == requestState.limits.maximum;
        return true;
    }

    public function Deselect(value : int, currentShapeIds : array<int>) : bool
    {
        var i : int;
        var j : int;
        if (!requestState.initialized || requestState.destroyed || !BetaGwentRequestContains(selected, value)) return false;
        for (i = 0; i < selected.Size(); i += 1)
            if (selected[i] == value) { selected.Erase(i); break; }
        if (requestState.kind == BG_RequestTargets)
            for (i = 0; i < currentShapeIds.Size(); i += 1)
                for (j = 0; j < targetsInShape.Size(); j += 1)
                    if (targetsInShape[j] == currentShapeIds[i]) { targetsInShape.Erase(j); break; }
        // Original RemoveChoice/RemoveTarget does not clear the finished flag.
        return true;
    }

    public function Finish() : bool
    {
        if (!requestState.initialized || requestState.destroyed || !requestState.applied) return false;
        if (!BetaGwentRequestCanFinish(requestState.limits.minimum, requestState.limits.maximum, selected.Size())) return false;
        requestState.limits.finished = true;
        return true;
    }

    public function GetChoiceViews(receivingPlayerId : int, out views : array<SBetaGwentChoiceView>) : bool
    {
        var i : int;
        views.Clear();
        if (requestState.destroyed || !requestState.initialized || requestState.kind != BG_RequestChoices
            || receivingPlayerId != requestState.targetPlayerId) return false;
        for (i = 0; i < choices.Size(); i += 1) views.PushBack(choices[i].view);
        return true;
    }

    public function CopyResult(out resultIds : array<int>, out shapeIds : array<int>) : bool
    {
        var i : int;
        resultIds.Clear(); shapeIds.Clear();
        if (!IsFulfilled()) return false;
        for (i = 0; i < selected.Size(); i += 1)
            if (requestState.kind == BG_RequestChoices) resultIds.PushBack(ChoiceOriginal(selected[i]));
            else resultIds.PushBack(selected[i]);
        for (i = 0; i < targetsInShape.Size(); i += 1) shapeIds.PushBack(targetsInShape[i]);
        return true;
    }

    public function Destroy()
    {
        requestState.destroyed = true;
        choices.Clear(); validTargets.Clear(); selected.Clear(); targetsInShape.Clear();
        requestState.validCount = 0;
    }
}
