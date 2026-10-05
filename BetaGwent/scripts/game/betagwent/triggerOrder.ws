// Pure metadata helpers for AbilityManager.AddAbilityInstance's local batch.
// Does not resolve nodes, register triggers or schedule live ability instances.
struct SBetaGwentTriggerTicket
{
    var instanceId : int;
    var ownerPresent : bool;
    var priority : int;
    var locationMask : int;
    var ownerPlayerId : int;
    var ownerIndex : int;
}

function BetaGwentTriggerLocationPriority(locationMask : int) : int
{
    // Exact keys/values in original AbilityManager constructor dictionary.
    switch (locationMask)
    {
        case 1: return 9;
        case 2: return 8;
        case 4: return 7;
        case 8: return 6;
        case 64: return 5;
        case 16: return 4;
        case 32: return 3;
        case 256: return 2;
        case 767: return 1;
        case 512: return 0;
        default: return -1;
    }
    // Draft guard: no invented priority for unrecognized dictionary keys.
}

function BetaGwentTriggerInsertionIndex(existing : array<SBetaGwentTriggerTicket>,
    candidate : SBetaGwentTriggerTicket, currentPlayerId : int) : int
{
    var i : int;
    var candidateLocation : int;
    var oldLocation : int;
    // Original bypasses the entire comparison scan for an ownerless instance.
    if (!candidate.ownerPresent) return existing.Size();
    candidateLocation = BetaGwentTriggerLocationPriority(candidate.locationMask);
    if (candidateLocation < 0) return -1;
    for (i = 0; i < existing.Size(); i += 1)
    {
        if (candidate.priority > existing[i].priority) return i;
        if (candidate.priority != existing[i].priority) continue;
        // Original reads the existing owner's location here. The draft reports
        // unsupported metadata rather than reproducing a null dereference.
        if (!existing[i].ownerPresent) return -1;
        oldLocation = BetaGwentTriggerLocationPriority(existing[i].locationMask);
        if (oldLocation < 0) return -1;
        if (candidateLocation > oldLocation) return i;
        if (candidateLocation != oldLocation) continue;
        if (candidate.ownerPlayerId == existing[i].ownerPlayerId)
        {
            if (candidate.ownerIndex < existing[i].ownerIndex) return i;
        }
        else if (candidate.ownerPlayerId == currentPlayerId) return i;
    }
    // Equal keys retain registration order; instance ID is not a tie-breaker.
    return existing.Size();
}
