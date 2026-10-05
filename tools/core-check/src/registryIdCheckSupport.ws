// Fixtures expose reconstruction seams, not original Register/Unregister.
class CBetaGwentRegistryIdCheckFixture extends CBetaGwentRegistryIdStore
{
    public function State(value : int, capacity : int) : bool { return ReconstructIdState(value, capacity); }
    public function Slot(id : int, card : CBetaGwentRegistryCardReference) : bool { return WriteSlot(id, card); }
    public function Recycle(id : int) : bool { return RecycleId(id); }
}

class CBetaGwentRegistryIdCheckRunner extends IScriptable
{
    private var checks, failures : int;
    public function Failures() : int { return failures; }
    private function Check(label : string, passed : bool)
    {
        checks += 1;
        if (passed) LogChannel('BetaGwent', "REGISTRY_CHECK_PASS " + label);
        else { failures += 1; LogChannel('BetaGwent', "REGISTRY_CHECK_FAIL " + label); }
    }
    private function RunGuards()
    {
        var f : CBetaGwentRegistryIdCheckFixture;
        var card, replacement, captured : CBetaGwentRegistryCardReference;
        var id : int;
        var ok : bool;
        f = new CBetaGwentRegistryIdCheckFixture in this;
        card = new CBetaGwentRegistryCardReference in this;
        id = 173;
        Check("guard/uninitialized", !f.Allocate(id) && id == 173 && !f.GetCard(0)
            && !f.Slot(0, card) && !f.Recycle(0) && !f.State(1, 64) && !f.IsInitialized());
        f.Initialize(); f.Allocate(id); f.Recycle(9); f.Slot(2, card);
        Check("guard/initialize-once", !f.Initialize() && f.GetNextId() == 2
            && f.Capacity() == 64 && f.RecycledCount() == 1 && f.GetCard(2) == card);
        Check("guard/int-domain-lookup", !f.GetCard(-1) && !f.GetCard(65536));
        Check("guard/invalid-slot-write", !f.Slot(-1, card) && !f.Slot(65536, card)
            && !f.Slot(64, card) && f.GetCard(2) == card);
        Check("guard/invalid-recycle", !f.Recycle(-1) && !f.Recycle(65536) && f.RecycledCount() == 1);
        Check("guard/invalid-reconstruction", !f.State(-1, 64) && !f.State(65536, 64)
            && !f.State(1, 0) && !f.State(1, 65) && !f.State(1, 65600)
            && f.GetNextId() == 2 && f.Capacity() == 64 && f.RecycledCount() == 1 && f.GetCard(2) == card);
        Check("guard/reconstruction-preserves-slot", f.State(3, 128) && f.GetCard(2) == card
            && f.GetNextId() == 3 && f.Capacity() == 128 && f.RecycledCount() == 0);
        f.Recycle(0); id = -1;
        Check("guard/recycled-zero-valid", f.Allocate(id) && id == 0 && f.GetNextId() == 3);
        f.Recycle(65535); id = -1;
        Check("guard/recycled-max-valid", f.Allocate(id) && id == 65535 && f.GetNextId() == 3);
        // Local slot seam demonstrates why an ID alone is not a stale intent guard.
        captured = f.GetCard(2); replacement = new CBetaGwentRegistryCardReference in this;
        ok = f.Slot(2, NULL); ok = f.Recycle(2) && ok;
        ok = f.Allocate(id) && ok; ok = id == 2 && ok;
        ok = f.Slot(id, replacement) && ok;
        Check("guard/reused-slot-reference-changes", ok && captured == card
            && f.GetCard(2) == replacement && f.GetCard(2) != captured && f.GetNextId() == 3);
    }
