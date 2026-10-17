// Boundary model only: per-instance node state, not AAbility graph execution.
enum EBetaGwentAbilityInstanceState
{
    BG_AbilityStarted = 0,
    BG_AbilityRunning = 1,
    BG_AbilityFinished = 2,
    BG_AbilityPaused = 3,
    BG_AbilityAborted = 4
}

class CBetaGwentAbilityContinuation extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var ownerInstanceId : int;
    public var nodeId : int;
    public var nodeSetup : bool;
    public var completedNodes : int;
    public var phase : EBetaGwentAbilityInstanceState;
    public var pending : CBetaGwentCardRequest;

    public function Initialize(instanceId : int) : bool
    {
        if (ownerInstanceId != 0 || instanceId <= 0) return false;
        ownerInstanceId = instanceId;
        phase = BG_AbilityRunning;
        return true;
    }

    public function BeginNode(value : int) : bool
    {
        if (ownerInstanceId == 0 || phase != BG_AbilityRunning || nodeSetup || value <= 0) return false;
        nodeId = value; nodeSetup = true;
        return true;
    }

    public function PauseOn(request : CBetaGwentCardRequest) : bool
    {
        var snapshot : SBetaGwentRequestSnapshot;
        if (!request || phase != BG_AbilityRunning || !nodeSetup || pending) return false;
        snapshot = request.Snapshot();
        if (!snapshot.initialized || snapshot.destroyed) return false;
        pending = request;
        pending.SetAutoDestroy(false);
        phase = BG_AbilityPaused;
        return true;
    }

    public function IsWaitingFor(request : CBetaGwentCardRequest) : bool
    { return phase == BG_AbilityPaused && pending == request; }

    public function ResumeFor(request : CBetaGwentCardRequest) : bool
    {
        if (!IsWaitingFor(request) || !request.IsFulfilled()) return false;
        phase = BG_AbilityRunning;
        return true;
    }

    public function CompleteRequestNode(out ids : array<int>, out shapeIds : array<int>) : bool
    {
        ids.Clear(); shapeIds.Clear();
        if (phase != BG_AbilityRunning || !nodeSetup || !pending) return false;
        if (!pending.CopyResult(ids, shapeIds)) return false;
        // Result copied before destruction. The next BeginNode performs Setup.
        pending.Destroy(); pending = NULL;
        nodeSetup = false; completedNodes += 1;
        return true;
    }

    public function Abort()
    {
        if (pending) pending.Destroy();
        pending = NULL; phase = BG_AbilityAborted;
    }
    public function GetAbilityState() : EBetaGwentAbilityInstanceState { return phase; }
    public function GetNodeId() : int { return nodeId; }
    public function GetCompletedNodes() : int { return completedNodes; }
}

struct SBetaGwentPendingRequestSlot
{
    var request : CBetaGwentCardRequest;
    var continuation : CBetaGwentAbilityContinuation;
}

class CBetaGwentRequestStore extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var slots : array<SBetaGwentPendingRequestSlot>;

    public function Find(requestId : int, playerId : int, kind : EBetaGwentCardRequestKind) : CBetaGwentCardRequest
    {
        var i : int;
        var snapshot : SBetaGwentRequestSnapshot;
        for (i = 0; i < slots.Size(); i += 1)
        {
            snapshot = slots[i].request.Snapshot();
            if (snapshot.destroyed || snapshot.requestId != requestId) continue;
            // Original Get<T>(id, player) first calls Get(id), then type/player
            // checks that first entry. It does not seek a later tuple match.
            if (snapshot.kind != kind || (playerId != 0 && snapshot.playerId != playerId)) return NULL;
            return slots[i].request;
        }
        return NULL;
    }

    public function Add(request : CBetaGwentCardRequest, continuation : CBetaGwentAbilityContinuation) : bool
    {
        var slot : SBetaGwentPendingRequestSlot;
        var snapshot : SBetaGwentRequestSnapshot;
        var i : int;
        if (!request || request.IsDestroyed()) return false;
        snapshot = request.Snapshot();
        if (!snapshot.initialized) return false;
        // Duplicate-key rejection is a local guard, separate from original Get.
        for (i = 0; i < slots.Size(); i += 1)
            if (slots[i].request.Matches(snapshot.requestId, snapshot.playerId, snapshot.kind)) return false;
        if (continuation && !continuation.IsWaitingFor(request)) return false;
        slot.request = request; slot.continuation = continuation;
        slots.PushBack(slot);
        for (i = slots.Size() - 1; i > 0; i -= 1) slots[i] = slots[i - 1];
        slots[0] = slot;
        return true;
    }

    public function UpdateOne() : bool
    {
        var i : int;
        var request : CBetaGwentCardRequest;
        for (i = 0; i < slots.Size(); i += 1)
        {
            request = slots[i].request;
            if (request.IsDestroyed()) { slots.Erase(i); return true; }
            if (!request.IsFulfilled()) continue;
            // Original HandleFulfilled precedes Remove/optional destruction.
            if (slots[i].continuation) slots[i].continuation.ResumeFor(request);
            slots.Erase(i);
            if (request.AutoDestroy()) request.Destroy();
            return true;
        }
        return false;
    }

    public function Count() : int { return slots.Size(); }
}
