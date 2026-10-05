// Isolated development UI capability probe. Requires its own registered CMenuResource.
// Kept outside the active project until .redswf/config registration is verified.
class CR4BetaGwentUIProbeMenu extends CR4Menu
{
    private var probeCounter : int;
    private var probeConfigured : bool;
    private var probeSetState : CScriptedFlashFunction;

    event OnConfigUI()
    {
        if (probeConfigured)
            return false;
        probeConfigured = true;
        probeCounter = 0;
        theInput.StoreContext('EMPTY_CONTEXT');
        theGame.GetGuiManager().RequestMouseCursor(true);
        probeSetState = GetMenuFlash().GetMemberFlashFunction("setProbeState");
        LogChannel('BetaGwent', "UI_PROBE_CONFIGURED");
        SendProbeState("Script connected. Click to test intent and response; Esc closes.");
    }

    event OnBetaGwentProbeIntent(value : int)
    {
        if (!probeConfigured || value != probeCounter + 1)
        {
            LogChannel('BetaGwent', "UI_PROBE_REJECT value=" + value);
            return false;
        }
        probeCounter = value;
        LogChannel('BetaGwent', "UI_PROBE_INTENT counter=" + probeCounter);
        SendProbeState("Intent accepted by WitcherScript.");
    }

    event OnBetaGwentProbeClose()
    {
        CloseMenu();
    }

    event OnClosingMenu()
    {
        if (probeConfigured)
        {
            theInput.RestoreContext('EMPTY_CONTEXT', false);
            theGame.GetGuiManager().RequestMouseCursor(false);
            probeConfigured = false;
        }
        LogChannel('BetaGwent', "UI_PROBE_CLOSED counter=" + probeCounter);
    }

    private function SendProbeState(message : string)
    {
        if (probeSetState)
        {
            probeSetState.InvokeSelfTwoArgs(FlashArgInt(probeCounter), FlashArgString(message));
            LogChannel('BetaGwent', "UI_PROBE_RESPONSE counter=" + probeCounter);
        }
        else
            LogChannel('BetaGwent', "UI_PROBE_MISSING setProbeState");
    }
}

exec function bgui_open()
{
    if (theGame.GetGuiManager().IsAnyMenu())
    {
        LogChannel('BetaGwent', "UI_PROBE_OPEN_SKIPPED existing menu");
        return;
    }
    theGame.RequestMenu('BetaGwentUIProbe');
}

exec function bgui_close()
{
    var menu : CR4BetaGwentUIProbeMenu;
    menu = (CR4BetaGwentUIProbeMenu)theGame.GetGuiManager().GetRootMenu();
    if (menu)
        menu.CloseMenu();
}
