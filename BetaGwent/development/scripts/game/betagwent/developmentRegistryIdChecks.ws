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

    private function RunOriginal0()
    {
        var f : CBetaGwentRegistryIdCheckFixture;
        var card : CBetaGwentRegistryCardReference;
        var id : int;
        var ok : bool;
        card = new CBetaGwentRegistryCardReference in this;
        f = new CBetaGwentRegistryIdCheckFixture in this; f.Initialize();
        ok = true;
        ok = f.Allocate(id) && ok; ok = id == 1 && ok;
        ok = f.Allocate(id) && ok; ok = id == 2 && ok;
        ok = f.Allocate(id) && ok; ok = id == 3 && ok;
        ok = f.Allocate(id) && ok; ok = id == 4 && ok;
        ok = f.Allocate(id) && ok; ok = id == 5 && ok;
        ok = f.Allocate(id) && ok; ok = id == 6 && ok;
        ok = f.Allocate(id) && ok; ok = id == 7 && ok;
        ok = f.Allocate(id) && ok; ok = id == 8 && ok;
        Check("allocate/initial-sequence", ok && f.GetNextId() == 9 && f.Capacity() == 64);
        f = new CBetaGwentRegistryIdCheckFixture in this; f.Initialize();
        f.State(63, 64); f.Slot(2, card);
        ok = f.Allocate(id);
        ok = id == 63 && f.Capacity() == 64 && ok;
        ok = f.Allocate(id) && ok;
        Check("allocate/grow-at64-preserves-reference", ok && id == 64 && f.Capacity() == 128 && f.GetNextId() == 65 && f.GetCard(2) == card);
        f = new CBetaGwentRegistryIdCheckFixture in this; f.Initialize();
        f.State(128, 128); f.Slot(127, card); ok = f.Allocate(id);
        Check("allocate/grow-at128-preserves-reference", ok && id == 128 && f.Capacity() == 192 && f.GetNextId() == 129 && f.GetCard(127) == card);
        f = new CBetaGwentRegistryIdCheckFixture in this; f.Initialize();
        f.Recycle(9); f.Recycle(4); ok = true;
        ok = f.Allocate(id) && ok; ok = id == 4 && ok;
        ok = f.Allocate(id) && ok; ok = id == 9 && ok;
        ok = f.Allocate(id) && ok; ok = id == 1 && ok;
        Check("allocate/recycled-lifo-precedes-next", ok && f.GetNextId() == 2 && f.Capacity() == 64 && f.RecycledCount() == 0);
    }
    private function RunOriginal1()
    {
        var f : CBetaGwentRegistryIdCheckFixture;
        var card : CBetaGwentRegistryCardReference;
        var id : int;
        var ok : bool;
        card = new CBetaGwentRegistryCardReference in this;
        f = new CBetaGwentRegistryIdCheckFixture in this; f.Initialize();
        f.Recycle(7); f.Recycle(7); ok = true;
        ok = f.Allocate(id) && ok; ok = id == 7 && ok;
        ok = f.Allocate(id) && ok; ok = id == 7 && ok;
        Check("allocate/duplicate-recycled-state-not-deduped", ok && f.GetNextId() == 1);
        f = new CBetaGwentRegistryIdCheckFixture in this; f.Initialize();
        f.State(64, 64); f.Recycle(5); ok = f.Allocate(id);
        Check("allocate/recycled-skips-growth", ok && id == 5 && f.GetNextId() == 64 && f.Capacity() == 64);
        f = new CBetaGwentRegistryIdCheckFixture in this; f.Initialize();
        f.State(65535, 65536); ok = true;
        ok = f.Allocate(id) && ok; ok = id == 65535 && ok;
        ok = f.Allocate(id) && ok; ok = id == 0 && ok;
        ok = f.Allocate(id) && ok; ok = id == 1 && ok;
        Check("allocate/uint16-wrap-keeps-zero", ok && f.GetNextId() == 2 && f.Capacity() == 65536);
        f = new CBetaGwentRegistryIdCheckFixture in this; f.Initialize();
        f.Slot(1, card);
        Check("lookup/existing-same-reference", f.GetCard(1) == card);
    }
    private function RunOriginal2()
    {
        var f : CBetaGwentRegistryIdCheckFixture;
        var card : CBetaGwentRegistryCardReference;
        var id : int;
        var ok : bool;
        card = new CBetaGwentRegistryCardReference in this;
        f = new CBetaGwentRegistryIdCheckFixture in this; f.Initialize();
        f.Slot(1, card);
        Check("lookup/null-slot", !f.GetCard(2));
        f = new CBetaGwentRegistryIdCheckFixture in this; f.Initialize();
        f.Slot(1, card);
        Check("lookup/zero-slot", !f.GetCard(0));
        f = new CBetaGwentRegistryIdCheckFixture in this; f.Initialize();
        f.Slot(1, card);
        Check("lookup/at-capacity", !f.GetCard(64));
        f = new CBetaGwentRegistryIdCheckFixture in this; f.Initialize();
        f.Slot(1, card);
        Check("lookup/above-capacity", !f.GetCard(65535));
    }
    public function Run()
    {
        checks = 0; failures = 0;
        LogChannel('BetaGwent', "REGISTRY_CHECK_BEGIN schema=1 fixture=registry22 key=3c9c160e6988826e");
        RunOriginal0(); RunOriginal1(); RunOriginal2(); RunGuards();
        LogChannel('BetaGwent', "REGISTRY_CHECK_DONE checks=" + checks + " passed=" + (checks - failures) + " failed=" + failures);
    }
}

exec function bgregistry_check()
{
    var runner : CBetaGwentRegistryIdCheckRunner;
    var power : CBetaGwentPowerNumberCheckRunner;
    if (!thePlayer) { LogChannel('BetaGwent', "REGISTRY_CHECK_SKIPPED no player"); return; }
    LogChannel('BetaGwent', "REGISTRY_SUITE_BEGIN schema=1 key=3c9c160e6988826e power=59af251c490c2f86 manager=319abdd4f2a6cc31");
    BetaGwentRunManagerChecks();
    power = new CBetaGwentPowerNumberCheckRunner in thePlayer; power.Run();
    runner = new CBetaGwentRegistryIdCheckRunner in thePlayer; runner.Run();
    LogChannel('BetaGwent', "REGISTRY_SUITE_END schema=1");
    theGame.GetGuiManager().ShowNotification("ID карт: " + (22 - runner.Failures()) + "/22, ошибок: " + runner.Failures(), 8.0);
}
