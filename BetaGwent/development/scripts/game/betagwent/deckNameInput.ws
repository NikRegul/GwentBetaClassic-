// Same native keyboard API used by REDkit's modMenu/popupMenu. No typing into
// gameplay controls; returned text remains a draft until Save is pressed.
statemachine class CBetaGwentDeckNameInput extends CR4MenuBase
{
    public var ownerMenu : CR4BetaGwentBoardMenu;
    public var expectedRevision : int;
    public var purpose : int;
    public var keyboardConfig : SVirtualKeyboardConfig;
    private var active : bool;
    default autoState = 'Idle';
    public function Open(menu : CR4BetaGwentBoardMenu, value : int, title : string, inputPurpose : int) : bool
    {
        if (active) return false;
        ownerMenu=menu;expectedRevision=value;purpose=inputPurpose;
        keyboardConfig.titleStr="Название колоды";if(purpose!=0)keyboardConfig.titleStr="Поиск карт";keyboardConfig.defaultStr=title;
        active=true;GotoState('Typing');return true;
    }
    public function Finish(title : string)
    {
        if (ownerMenu) ownerMenu.FinishControllerText(expectedRevision,purpose,title);
        active=false;GotoState('Idle');
    }
}
state Idle in CBetaGwentDeckNameInput {}
state Typing in CBetaGwentDeckNameInput
{
    event OnEnterState(previous : name)
    { super.OnEnterState(previous);ReadName(); }
    entry function ReadName()
    {
        var title : string;
        theGame.GetGuiManager().ForceHideMouseCursor(true);
        title=theInput.OpenVirtualKeyboard(parent.keyboardConfig);
        Sleep(0.1);
        while(theInput.IsVirtualKeyboardActive()) Sleep(0.1);
        theGame.GetGuiManager().ForceHideMouseCursor(false);
        theGame.GetGuiManager().RequestMouseCursor(!theInput.LastUsedGamepad());
        parent.Finish(title);
    }
}
