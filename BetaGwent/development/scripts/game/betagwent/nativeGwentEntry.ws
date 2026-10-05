// Keep native minigame/quest signalling; replace only the project GUI resources.
@addField(CR4GwintManager)
public var betaNpcPending : bool;
@addField(CR4GwintManager)
public var betaEnemyDeckName : name;
@addField(CR4GwintManager)
public var betaTalkNpcId : int;
@addField(CR4GwintManager)
public var betaMatchNpcId : int;
@addField(CR4Player)
public var betaPracticeRequested : bool;

@wrapMethod(CR4Player)
function OnGwintGameRequested(deckName : name, forceFaction : eGwintFaction, additionalCards : array<name>)
{
    var player : W3PlayerWitcher;var manager : CR4GwintManager;
    player=(W3PlayerWitcher)this;manager=theGame.GetGwintManager();
    if(player && player.BetaGwentEnsureCollection()) {
        // The original tutorial teaches TW3 rules and its Flash handlers are
        // absent from the Beta menu. Begin directly with our deck selection.
        manager.SetHasDoneTutorial(true);manager.SetHasDoneDeckTutorial(true);
    }
    wrappedMethod(deckName,forceFaction,additionalCards);
}

@wrapMethod(CR4GwintManager)
function SetEnemyDeck(deckName : name) : void
{
    betaEnemyDeckName=deckName;betaNpcPending=true;
    betaMatchNpcId=betaTalkNpcId;
    wrappedMethod(deckName);
}

// Capture the actual actor receiving Talk. Generic merchant deck names are
// shared by many actors and must never be used as their reward identity.
@wrapMethod(CNewNPC)
function OnInteraction(actionName : string, activator : CEntity)
{
    var manager : CR4GwintManager;manager=theGame.GetGwintManager();
    if(actionName=="Talk" && activator==thePlayer)manager.betaTalkNpcId=GetGuidHash();
    wrappedMethod(actionName,activator);
}
@wrapMethod(W3MerchantNPC)
function OnInteraction(actionName : string, activator : CEntity)
{
    var manager : CR4GwintManager;manager=theGame.GetGwintManager();
    if(actionName=="Talk" && activator==thePlayer)manager.betaTalkNpcId=GetGuidHash();
    wrappedMethod(actionName,activator);
}

@wrapMethod(CR4Player)
function OnGwintGameEnded()
{
    var manager : CR4GwintManager;manager=theGame.GetGwintManager();
    manager.betaNpcPending=false;manager.gameRequested=false;
    wrappedMethod();
}

// Native NPC requests go through DeckBuilder before GwintGame. The same menu
// from pause is a library. A practice root never inherits stale quest flags.
function BetaGwentNativeEntryMode(menuName : name, pending : bool, requested : bool) : int
{
    if(menuName == 'BetaGwentBoard') return 0;
    if(menuName == 'GwintGame') return 2;
    if(menuName == 'DeckBuilder' && (pending || requested)) return 2;
    return 1;
}

function BetaGwentNativeFaction(faction : eGwintFaction) : int
{
    switch(faction)
    {
    case GwintFaction_NothernKingdom:return 8;
    case GwintFaction_Nilfgaard:return 4;
    case GwintFaction_Scoiatael:return 16;
    case GwintFaction_NoMansLand:return 2;
    case GwintFaction_Skellige:return 32;
    default:return 0;
    }
}
function BetaGwentNativePreset(faction : int) : int
{
    switch(faction)
    {
    case 8:return 6;
    case 4:return 8;
    case 16:return 11;
    case 32:return 14;
    default:return 15;
    }
}

function BetaGwentNpcPreset(deck : name) : int
{
    var assigned : int;
    assigned=BetaGwentQuestPreset(deck);if(assigned!=0)return assigned;
    // Named quest opponents retain their fixed lists and rewards above.
    // Ordinary players draw from the adapted user archetypes and legacy lists.
    return BetaGwentAIRandomPreset();
}
