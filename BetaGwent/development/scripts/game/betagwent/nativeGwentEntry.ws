// Keep native minigame/quest signalling; replace only the project GUI resources.
@addField(CR4GwintManager)
public var betaNpcPending : bool;
@addField(CR4GwintManager)
public var betaEnemyDeckName : name;
@addField(CR4GwintManager)
public var betaTalkNpcId : int;
@addField(CR4GwintManager)
public var betaMatchNpcId : int;
@addField(CR4GwintManager)
public var betaOrdinaryDeckBag : array<int>;
@addField(CR4GwintManager)
public var betaOrdinaryLastPreset : int;
@addField(CR4GwintManager)
public var betaFactionDeckBag : array<int>;
@addField(CR4Player)
public var betaPracticeRequested : bool;
@addField(CR4GwintManager)
public var betaAiSimDepth : int;

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

function BetaGwentPresetFaction(preset : int) : int
{
    var p : SBetaGwentDuelPreset; var d : SBetaGwentDuelDefinition;
    p=BetaGwentDuelPreset(preset);d=BetaGwentDuelDefinition(p.leaderTemplateId);return d.header.factionMask;
}
// Named opponents keep their faction and rewards but draw one of the 40 adapted
// archetypes of that faction (shuffled bag, no immediate repeat).
function BetaGwentAIChooseFactionPreset(faction : int) : int
{
    var manager : CR4GwintManager;var all,mine : array<int>;var i,picked : int;
    manager=theGame.GetGwintManager();if(!manager)return BetaGwentAIRandomPreset();
    for(i=0;i<manager.betaFactionDeckBag.Size();i+=1)if(BetaGwentPresetFaction(manager.betaFactionDeckBag[i])==faction)mine.PushBack(manager.betaFactionDeckBag[i]);
    if(mine.Size()==0)
    {
        BetaGwentAIOrdinaryPresets(all);
        for(i=0;i<all.Size();i+=1)if(BetaGwentPresetFaction(all[i])==faction){manager.betaFactionDeckBag.PushBack(all[i]);mine.PushBack(all[i]);}
        if(mine.Size()==0)return BetaGwentAIRandomPreset();
    }
    picked=mine[RandRange(mine.Size())];
    if(mine.Size()>1 && picked==manager.betaOrdinaryLastPreset){for(i=0;i<mine.Size();i+=1)if(mine[i]!=picked){picked=mine[i];break;}}
    for(i=manager.betaFactionDeckBag.Size()-1;i>=0;i-=1)if(manager.betaFactionDeckBag[i]==picked){manager.betaFactionDeckBag.Erase(i);break;}manager.betaOrdinaryLastPreset=picked;
    LogChannel('BetaGwent',"DUEL_AI_POOL preset="+picked+" faction="+faction+" policy=faction_bag107");
    return picked;
}
function BetaGwentNpcPreset(deck : name) : int
{
    var assigned : int;
    assigned=BetaGwentQuestPreset(deck);
    // Named opponents (Zoltan, innkeepers, tournaments...) use their faction's archetypes.
    if(assigned!=0)return BetaGwentAIChooseFactionPreset(BetaGwentPresetFaction(assigned));
    return BetaGwentAIRandomPreset();
}

// Battle engine log. AI lookahead simulations (cloned sessions) stay silent.
function BetaGwentLog(message : string)
{
    var manager : CR4GwintManager;
    manager=theGame.GetGwintManager();
    if(manager && manager.betaAiSimDepth>0)return;
    LogChannel('BetaGwent',message);
}
function BetaGwentAISimEnter(){var manager : CR4GwintManager;manager=theGame.GetGwintManager();if(manager)manager.betaAiSimDepth+=1;}
function BetaGwentAISimLeave(){var manager : CR4GwintManager;manager=theGame.GetGwintManager();if(manager)manager.betaAiSimDepth=Max(0,manager.betaAiSimDepth-1);}
