// Beta 0.9.24.3.432 draft. Verification status: BetaGwent/README.md.
// Gameplay enums retain original numeric values; BG identifiers are mod-local.
enum EBetaGwentPhase
{
    BG_PhaseInit = 1,
    BG_PhaseMulligan = 2,
    BG_PhaseChoosePlayer = 4,
    BG_PhaseRoundStart = 8,
    BG_PhaseTurnStart = 16,
    BG_PhaseTurn = 32,
    BG_PhaseTurnEnd = 64,
    BG_PhaseRoundEnd = 128,
    BG_PhaseClearBoard = 256,
    BG_PhaseResults = 512,
    BG_PhaseDrawCards = 1024
}

enum EBetaGwentPlayerMask
{
    BG_PlayerNone = 0,
    BG_PlayerOne = 1,
    BG_PlayerTwo = 2,
    BG_PlayerBoth = 3
}

enum EBetaGwentLocationMask
{
    BG_LocationNone = 0,
    BG_LocationMelee = 1,
    BG_LocationRanged = 2,
    BG_LocationSiege = 4,
    BG_LocationHand = 8,
    BG_LocationDeck = 16,
    BG_LocationGraveyard = 32,
    BG_LocationLeader = 64,
    BG_LocationSpawningPool = 128,
    BG_LocationPlayStack = 256,
    BG_LocationVoid = 512
}

// API failures belong to this draft, not to an original Beta enum.
enum EBetaGwentStateResult
{
    BG_StateOK,
    BG_StateNotInitialized,
    BG_StateAlreadyInitialized,
    BG_StateInvalidPlayer,
    BG_StateBoundaryConflict,
    BG_StateMatchHasWinner,
    BG_StateUnexpectedStarter,
    BG_StateInitialMoveAlreadyClaimed,
    BG_StatePlayersHaveNotPassed
}

// A decision for the future coordinator, not an executed request or action.
enum EBetaGwentTurnEntryDecision
{
    BG_TurnEntryNoRequest,
    BG_TurnEntryInitialPlayRequests,
    BG_TurnEntryAutomaticPass
}

// Minimal header, not a complete card definition or effect IR.
struct SBetaGwentTemplateHeader
{
    var templateId : int;
    var typeMask : int;
    var tierMask : int;
    var factionMask : int;
    var power : int;
    var armor : int;
}

struct SBetaGwentPower
{
    var basePower : int;
    var currentPower : int;
    var permanentPower : int;
    var armor : int;
}

struct SBetaGwentCardSnapshot
{
    var instanceId : int;
    var originTemplateId : int;
    var runtimeTemplate : SBetaGwentTemplateHeader;
    var ownerId : int;
    var controllerId : int;
    // Board-side identity from CardPosition; do not substitute ownerId.
    var positionPlayerId : int;
    var locationMask : int;
    var locationIndex : int;
    var runtimeTierMask : int;
    var tokenMask : int;
    var power : SBetaGwentPower;
    var canBePlayed : bool;
    var isInExecutionStack : bool;
    var isWaitingToDie : bool;
}

struct SBetaGwentLocationFilter
{
    // All types = 14, all tiers = 15. Zero is not a wildcard.
    var typeMask : int;
    var tierMask : int;
    var withoutTokens : int;
    var withTokens : int;
    var includeOnlyCardsThatCanBePlayed : bool;
}

struct SBetaGwentPlayRequest
{
    var playerId : int;
    // Zero selects the original general-play branch.
    var requestedInstanceId : int;
}

struct SBetaGwentPlayerState
{
    var playerId : int;
    var crowns : int;
    var hasPassed : bool;
    var hasMadeInitialMoveForCurrentTurn : bool;
}

struct SBetaGwentRoundResult
{
    // Round/turn numbers below are mod-local, one-based bookkeeping.
    var roundNumber : int;
    var startingPlayerId : int;
    var scoreOne : int;
    var scoreTwo : int;
    var winnerMask : int;
    var crownDeltaOne : int;
    var crownDeltaTwo : int;
}

struct SBetaGwentMatchSnapshot
{
    var initialized : bool;
    var roundNumber : int;
    var turnSequence : int;
    var currentPlayerId : int;
    var startingPlayerId : int;
    var roundActive : bool;
    var turnActive : bool;
    var playerOne : SBetaGwentPlayerState;
    var playerTwo : SBetaGwentPlayerState;
    var matchWinnerMask : int;
}

