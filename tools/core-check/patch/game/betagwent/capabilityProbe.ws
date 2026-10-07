// Development capability probe. No Beta gameplay or vanilla collection changes.
// Seed/increment only run through explicit debug commands.
@addField(W3PlayerWitcher)
private saved var betaGwentProbeSchema : int;

@addField(W3PlayerWitcher)
private saved var betaGwentProbeIds : array<int>;

@addField(W3PlayerWitcher)
private saved var betaGwentProbeCounter : int;

@addMethod(W3PlayerWitcher)
public function BetaGwentProbeSeed()
{
    if (betaGwentProbeSchema != 0)
    {
        BetaGwentProbeReport("PROBE_SEED_SKIPPED schema=" + betaGwentProbeSchema);
        return;
    }

    betaGwentProbeIds.Clear();
    betaGwentProbeIds.PushBack(112103);
    betaGwentProbeIds.PushBack(112110);
    betaGwentProbeCounter = 17;
    betaGwentProbeSchema = 1;
    BetaGwentProbeReport("PROBE_SEEDED schema=1 counter=17 ids=112103,112110");
}

@addMethod(W3PlayerWitcher)
public function BetaGwentProbeRead() : bool
{
    var valid : bool;

    valid = betaGwentProbeSchema == 1 && betaGwentProbeIds.Size() == 2;
    if (valid)
    {
        valid = betaGwentProbeIds[0] == 112103 && betaGwentProbeIds[1] == 112110;
    }
    BetaGwentProbeReport("PROBE_READ schema=" + betaGwentProbeSchema
        + " counter=" + betaGwentProbeCounter + " ids=" + betaGwentProbeIds.Size()
        + " valid=" + valid);
    return valid;
}

@addMethod(W3PlayerWitcher)
public function BetaGwentProbeIncrement()
{
    if (BetaGwentProbeRead())
    {
        betaGwentProbeCounter += 1;
        BetaGwentProbeReport("PROBE_INCREMENT counter=" + betaGwentProbeCounter);
    }
}

@wrapMethod(CR4Player)
function OnGwintGameRequested(deckName : name, forceFaction : eGwintFaction, additionalCards : array<name>)
{
    LogChannel('BetaGwent', "PROBE_GWENT_REQUEST deck=" + deckName
        + " forcedFaction=" + forceFaction + " additional=" + additionalCards.Size());
    wrappedMethod(deckName, forceFaction, additionalCards);
}

@wrapMethod(CR4Player)
function OnGwintGameEnded()
{
    LogChannel('BetaGwent', "PROBE_GWENT_ENDED state=" + GetGwintMinigameState());
    wrappedMethod();
}

@wrapMethod(CR4GwintGameMenu)
function SetPlayerStarts(playerFirst : bool) : void
{
    LogChannel('BetaGwent', "PROBE_UI_SET_STARTER first=" + playerFirst);
    wrappedMethod(playerFirst);
}

function BetaGwentProbeReport(message : string)
{
    LogChannel('BetaGwent', message);
    theGame.GetGuiManager().ShowNotification("BetaGwent: " + message, 8.0);
}

exec function bgprobe_seed()
{
    var player : W3PlayerWitcher;
    player = (W3PlayerWitcher)thePlayer;
    if (player)
    {
        player.BetaGwentProbeSeed();
    }
}

exec function bgprobe_read()
{
    var player : W3PlayerWitcher;
    player = (W3PlayerWitcher)thePlayer;
    if (player)
    {
        player.BetaGwentProbeRead();
    }
}

exec function bgprobe_increment()
{
    var player : W3PlayerWitcher;
    player = (W3PlayerWitcher)thePlayer;
    if (player)
    {
        player.BetaGwentProbeIncrement();
    }
}
