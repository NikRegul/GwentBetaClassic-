// Add to the Classic UI source profile before rebuilding its four menus.
// Uses the existing text panel and controller keyboard; no new textures.
public function openClassicTextInput(value:int,purpose:int,title:String):void
{
    if(value!=revision||purpose<0||purpose>2)return;
    controllerTyping=false;
    openTextInput(purpose,title);
}
