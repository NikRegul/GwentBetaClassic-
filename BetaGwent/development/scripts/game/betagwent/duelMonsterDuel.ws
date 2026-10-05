// A half-strike is one managed action. Reactions resolve before the next half-strike.
// Continuations append to the same FIFO, so long duels do not grow passive depth.
class CBetaGwentMonsterDuelAction extends CBetaGwentManagedAction
{
    private var runtime : CBetaGwentDuelEffectRuntime;
    private var game : CBetaGwentDuelSession;
    private var source, target : CBetaGwentDuelCard;
    private var retaliation : bool;
    private var heal, armor : int;
    public function Setup(owner : CBetaGwentDuelEffectRuntime, session : CBetaGwentDuelSession,
        first : CBetaGwentDuelCard, second : CBetaGwentDuelCard, counterAttack : bool,
        healing : int, protection : int, context : CBetaGwentActionContext) : bool
    {
        runtime = owner; game = session; source = first; target = second; retaliation = counterAttack; heal = healing; armor = protection;
        SetStateChanging(true); return Prepare(context);
    }
    public function IsValid() : bool { return (bool)source && (bool)target && (bool)game; }
    protected function BeforeApplyImpl() { runtime.RecordBefore(); }
    protected function ApplyImpl() : bool
    {
        var a, b, before, after : SBetaGwentCardSnapshot; var attacking, defending : CBetaGwentDuelCard; var damage : int;
        a = source.Snapshot(); b = target.Snapshot();
        if ((a.locationMask & 7) == 0 || a.isWaitingToDie || a.power.currentPower <= 0) return true;
        if ((b.locationMask & 7) == 0 || b.isWaitingToDie || b.power.currentPower <= 0)
        { if (heal > 0) source.Power().RestorePower(heal); if (armor > 0) source.Power().AddArmor(armor); return true; }
        attacking = source; defending = target; damage = a.power.currentPower;
        if (retaliation) { attacking = target; defending = source; damage = b.power.currentPower; }
        else if (a.runtimeTemplate.templateId == 200502 && game.WeatherToken(b.positionPlayerId, b.locationMask) == 1) damage *= 2;
        before = defending.Snapshot(); if (!defending.ChangePower(-damage, false)) return false; after = defending.Snapshot();
        game.NilfPowerChanged(attacking,defending,before,after,1);
        if (after.power.currentPower + after.power.basePower < before.power.currentPower + before.power.basePower)
            game.MonsterDamaged(attacking, defending);
        // Original graph reads live power between strikes; armor and triggered damage are respected.
        if (!runtime.EnqueueMonsterDuel(source, target, !retaliation, heal, armor)) return false;
        runtime.RecordApplied(); return true;
    }
    protected function AfterApplyImpl() : bool { runtime.RecordAfter(); return true; }
}
