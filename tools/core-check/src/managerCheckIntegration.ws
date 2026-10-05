    private function SetupIntegration(config : SBetaGwentManagerCheckConfig)
    {
        var realBefore : CBetaGwentManagerIntegrationAction;
        Setup(config);
        realBefore = new CBetaGwentManagerIntegrationAction in this;
        realBefore.Setup(fixture, context); action = realBefore; fixture.Bind(action);
    }
    private function RunExtra()
    {
        var config : SBetaGwentManagerCheckConfig;
        var driver : CBetaGwentActionDriver;
        var next : CBetaGwentManagerIntegrationAction;
        var emptyManager : CBetaGwentActionManager;
        var bareAction : CBetaGwentQueuedAction;
        var missingServices : CBetaGwentMissingActionServices;
        var missingEffect : CBetaGwentMissingEffectAction;
        var value : SBetaGwentDelay64;
        config = BetaGwentManagerCheckDefaults(); Setup(config);
        emptyManager = new CBetaGwentActionManager in this;
        Check("guard/not-initialized", !emptyManager.ApplyAction(action) && emptyManager.GetFault() == BG_ManagerNotInitialized);
        emptyManager = new CBetaGwentActionManager in this;
        Check("guard/null-context-services", !emptyManager.Initialize(NULL, services) && !emptyManager.Initialize(context, NULL));
        Check("guard/initialize-once", emptyManager.Initialize(context, services) && !emptyManager.Initialize(context, services));
        Check("guard/null-action", !emptyManager.ApplyAction(NULL) && emptyManager.GetFault() == BG_ManagerUnsupportedAction);
        config = BetaGwentManagerCheckDefaults(); Setup(config);
        bareAction = new CBetaGwentQueuedAction in this; manager.DispatchAction(bareAction);
        Check("guard/unsupported-queued-action", manager.GetFault() == BG_ManagerUnsupportedAction && manager.GetDispatchCount() == 0);
        config = BetaGwentManagerCheckDefaults(); config.failAt = 1; Setup(config); manager.ApplyAction(action);
        Check("guard/fault-latches-without-second-effect", !manager.ApplyAction(action) && manager.GetDispatchCount() == 1 && fixture.Text() == "valid|apply|");
        config = BetaGwentManagerCheckDefaults(); config.request = true; config.failAt = 5; Setup(config);
        Check("guard/add-failure-stops-before-effect", !manager.ApplyAction(action) && fixture.Text() == "valid|can:True|add|");
        config = BetaGwentManagerCheckDefaults(); config.failAt = 6; Setup(config);
        Check("guard/destroy-failure-keeps-effect", !manager.ApplyAction(action) && fixture.Text() == "valid|apply|destroy|");
        config = BetaGwentManagerCheckDefaults(); config.networkId = 5; config.failAt = 7; Setup(config);
        Check("guard/errorlog-failure-stops-network-write", !manager.ApplyAction(action) && manager.GetLastKnownNetworkId() == 10 && fixture.Text() == "log-error|");
        config = BetaGwentManagerCheckDefaults(); config.verbose = true; config.failAt = 8; Setup(config);
        Check("guard/debuglog-failure-skips-effect", !manager.ApplyAction(action) && fixture.Text() == "valid|log-debug|");
        config = BetaGwentManagerCheckDefaults(); config.stateChanging = true; config.failAt = 9; Setup(config);
        Check("guard/dirty-failure-keeps-dirty-before-effect", !manager.ApplyAction(action) && context.IsDirty() && fixture.Text() == "valid|dirty|");
        config = BetaGwentManagerCheckDefaults(); Setup(config);
        missingServices = new CBetaGwentMissingActionServices in this;
        emptyManager = new CBetaGwentActionManager in this; emptyManager.Initialize(context, missingServices);
        Check("guard/default-services-fail-closed", !emptyManager.ApplyAction(action) && emptyManager.GetFault() == BG_ManagerServiceFailed);
        config = BetaGwentManagerCheckDefaults(); Setup(config);
        missingEffect = new CBetaGwentMissingEffectAction in this; missingEffect.Prepare(context); missingEffect.SetFireTriggers(false);
        fixture.Bind(missingEffect);
        Check("guard/missing-effect-fails-closed", !manager.ApplyAction(missingEffect) && manager.GetFault() == BG_ManagerApplyFailed && fixture.Text() == "");

        value.highWord = 0; value.lowWord = 0;
        Check("guard/delay64-zero", !BetaGwentDelay64Positive(value));
        value.highWord = 0; value.lowWord = -2147483647 - 1;
        Check("guard/delay64-positive-unsigned-low-word", BetaGwentDelay64Positive(value));
        value.highWord = 1; value.lowWord = 0;
        Check("guard/delay64-positive-high-word", BetaGwentDelay64Positive(value));
        value.highWord = -1; value.lowWord = 0;
        Check("guard/delay64-negative-high-word", !BetaGwentDelay64Positive(value));

        config = BetaGwentManagerCheckDefaults(); config.before = false; SetupIntegration(config);
        driver = new CBetaGwentActionDriver in this;
        Check("integration/uninitialized-driver", !driver.Step() && !driver.Push(action, false) && driver.RunBudget(1) == 0);
        emptyManager = new CBetaGwentActionManager in this;
        Check("integration/null-or-uninitialized-manager", !driver.Initialize(NULL, manager, false) && !driver.Initialize(context, emptyManager, false));
        Check("integration/driver-initialize-once", driver.Initialize(context, manager, false) && !driver.Initialize(context, manager, false));
        driver.Push(action, false);
        Check("integration/budget-guards-preserve-queue", driver.RunBudget(0) == 0 && driver.RunBudget(257) == 0 && driver.PendingCount() == 1);
        Check("integration/before-only-first-budget", driver.RunBudget(1) == 1 && driver.PendingCount() == 1 && manager.GetDispatchCount() == 0 && fixture.Text() == "valid|valid|before|");
        Check("integration/apply-second-budget", driver.RunBudget(1) == 1 && driver.PendingCount() == 0 && manager.GetDispatchCount() == 1 && fixture.Text() == "valid|valid|before|valid|apply|destroy|");
        Check("integration/drained-queue-no-op", driver.RunBudget(1) == 0 && !manager.IsFaulted());

        config = BetaGwentManagerCheckDefaults(); config.before = false; config.validationLosesAuthority = true; SetupIntegration(config);
        driver = new CBetaGwentActionDriver in this; driver.Initialize(context, manager, false); driver.Push(action, false); driver.Step();
        Check("integration/global-authority-read-before-validation", driver.PendingCount() == 1 && manager.GetDispatchCount() == 0 && !context.HasAuthority() && fixture.Text() == "valid|valid|before|");
        config = BetaGwentManagerCheckDefaults(); config.before = false; config.validationLosesAuthority = true; SetupIntegration(config);
        driver = new CBetaGwentActionDriver in this; driver.Initialize(context, manager, true); driver.Push(action, false); driver.Step();
        Check("integration/local-authority-read-after-validation", driver.PendingCount() == 0 && manager.GetDispatchCount() == 1 && !context.HasAuthority() && fixture.Text() == "valid|diagnostic|valid|apply|destroy|");
        config = BetaGwentManagerCheckDefaults(); config.before = false; SetupIntegration(config);
        driver = new CBetaGwentActionDriver in this; driver.Initialize(context, manager, false); context.SetAuthority(false);
        Check("integration/front-gate-reads-current-authority", !driver.Push(action, true) && driver.Push(action, false));
        config = BetaGwentManagerCheckDefaults(); SetupIntegration(config);
        driver = new CBetaGwentActionDriver in this; driver.Initialize(context, manager, true); context.SetAuthority(false);
        Check("integration/local-front-has-no-authority-gate", driver.Push(action, true));

        config = BetaGwentManagerCheckDefaults(); config.failAt = 1; SetupIntegration(config);
        // Integration action starts unfired; queue sends Before first.
        driver = new CBetaGwentActionDriver in this; driver.Initialize(context, manager, false); driver.Push(action, false);
        next = new CBetaGwentManagerIntegrationAction in this; next.Setup(fixture, context); driver.Push(next, false);
        driver.RunBudget(2);
        Check("integration/fault-preserves-following-action", manager.IsFaulted() && driver.PendingCount() == 1 && manager.GetDispatchCount() == 1);
        Check("integration/fault-blocks-step-push-and-budget", !driver.Step() && !driver.Push(next, false) && driver.RunBudget(256) == 0 && driver.PendingCount() == 1);
    }
}
// Uses the real inherited HasFiredBefore/BeforeApply guard, without fixture override.
class CBetaGwentManagerIntegrationAction extends CBetaGwentManagedAction
{
    private var fixture : CBetaGwentManagerCheckFixture;
    public function Setup(value : CBetaGwentManagerCheckFixture, owner : CBetaGwentManagerContext)
    { fixture = value; Prepare(owner); SetFireTriggers(value.Fire()); }
    public function IsValid() : bool { return fixture.Validate(); }
    protected function BeforeApplyImpl() { fixture.Before(); }
    protected function ApplyImpl() : bool { return fixture.Effect(); }
}
class CBetaGwentMissingActionServices extends CBetaGwentActionServices {}
class CBetaGwentMissingEffectAction extends CBetaGwentManagedAction {}

function BetaGwentRunManagerChecks()
{
    var runner : CBetaGwentManagerChecks;
    var queueChecks : CBetaGwentActionQueueChecks;
    var applyChecks : CBetaGwentApplyChecks;
    if (!thePlayer) { LogChannel('BetaGwent', "MANAGER_CHECK_SKIPPED no player"); return; }
    LogChannel('BetaGwent', "MANAGER_SUITE_BEGIN schema=1");
    queueChecks = new CBetaGwentActionQueueChecks in thePlayer; queueChecks.Run();
    applyChecks = new CBetaGwentApplyChecks in thePlayer; applyChecks.Run();
    runner = new CBetaGwentManagerChecks in thePlayer; runner.Run();
    LogChannel('BetaGwent', "MANAGER_SUITE_END schema=1");
    theGame.GetGuiManager().ShowNotification(runner.GetDisplaySummary(), 8.0);
}

exec function bgmanager_check() { BetaGwentRunManagerChecks(); }
