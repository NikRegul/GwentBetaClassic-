// Immutable presentation snapshot. Capturing it never executes rules or RNG.
class CBetaGwentDuelVisualFrame extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var matchState : SBetaGwentMatchSnapshot;
    public var cards : array<SBetaGwentDevelopmentCard>;
    public var weatherTokens, weatherDamage : array<int>;
    public var scoreOne, scoreTwo, flags : int;
    public var enemyHand, graveOne, graveTwo, deckOne, deckTwo : int;
    public var leaderOne, leaderTwo : bool;
    public var status : string;
    // 0 final, 1 play, 2 power/armor, 3 death, 4 weather, 5 pass,
    // 6 round/result, 7 round start. Milliseconds are presentation only.
    // 8 passive/timer,9 lock,10 transform,11 consume,12 grave consume,13 deathwish,14 draw.
    // 15 existing deck summon,16 created token,17 round cleanup (no Killed abilities).
    public var kind, sourceId, targetId, side, row, templateId, duration : int;
    public var targetTemplateId, targetPower, targetSide, targetZone : int;
    public var audioKind : int;
    // Original Beta ACardAttack grouping: one attack, attackCount targets (presentation only).
    public var attackId, attackCount : int;
}
