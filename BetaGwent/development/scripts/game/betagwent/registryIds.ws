// Original allocator/lookup oracle16 passed; native adapter checked separately.
// Card references are opaque until the live-card layer is implemented.
class CBetaGwentRegistryCardReference extends IScriptable {
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;}

class CBetaGwentRegistryIdStore extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var initialized : bool;
    public var nextId : int;
    public var recycled : array<int>;
    public var cards : array<CBetaGwentRegistryCardReference>;

    // Local setup corresponding to observed ctor fields, not a port of ctor.
    public function Initialize() : bool
    {
        if (initialized) return false;
        nextId = 1; cards.Resize(64); recycled.Clear(); initialized = true;
        return true;
    }
    public function IsInitialized() : bool { return initialized; }
    public function Capacity() : int { return cards.Size(); }
    public function GetNextId() : int { return nextId; }
    public function RecycledCount() : int { return recycled.Size(); }
    public function Allocate(out id : int) : bool
    {
        var last : int;
        if (!initialized) return false;
        if (recycled.Size() > 0)
        {
            last = recycled.Size() - 1;
            id = recycled[last]; recycled.Erase(last);
            return true;
        }
        if (nextId == cards.Size()) cards.Resize(cards.Size() + 64);
        id = nextId;
        // Original UInt16 conversion wraps; it has no zero/exhaustion guard.
        // A future playable registry must explicitly handle exhausted IDs.
        nextId = (nextId + 1) & 65535;
        return true;
    }
    public function GetCard(id : int) : CBetaGwentRegistryCardReference
    {
        // Adapter guards for int API; original input is a UInt16.
        if (!initialized || id < 0 || id > 65535 || id >= cards.Size()) return NULL;
        return cards[id];
    }

    // Reconstruction/fixture seams, not original Register/Unregister/Copy.
    // Real unregister clears the slot, pushes the ID, then emits an event.
    protected function WriteSlot(id : int, card : CBetaGwentRegistryCardReference) : bool
    {
        if (!initialized || id < 0 || id > 65535 || id >= cards.Size()) return false;
        cards[id] = card; return true;
    }
    protected function RecycleId(id : int) : bool
    {
        if (!initialized || id < 0 || id > 65535) return false;
        recycled.PushBack(id); return true;
    }
    protected function ReconstructIdState(value : int, capacity : int) : bool
    {
        if (!initialized || value < 0 || value > 65535 || capacity < 64
            || capacity > 65536 || (capacity & 63) != 0) return false;
        nextId = value; cards.Resize(capacity); recycled.Clear(); return true;
    }
}
