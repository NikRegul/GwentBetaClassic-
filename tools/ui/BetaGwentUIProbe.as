package
{
    import flash.display.Sprite;
    import flash.events.Event;
    import flash.events.MouseEvent;
    import flash.events.KeyboardEvent;
    import flash.external.ExternalInterface;
    import flash.text.TextField;
    import flash.text.TextFormat;

    [SWF(width="1920", height="1080", frameRate="30", backgroundColor="#10202A")]
    public class BetaGwentUIProbe extends Sprite
    {
        private var label:TextField;
        private var counter:int = 0;
        private var initialized:Boolean = false;
        // The native menu binding injects these hooks, as in CoreComponent.as.
        public var _NATIVE_callGameEvent:Function;
        public var _NATIVE_registerDataBinding:Function;
        public var _NATIVE_unregisterDataBinding:Function;
        public var _NATIVE_registerChild:Function;
        public var _NATIVE_unregisterChild:Function;
        public var _NATIVE_registerRenderTarget:Function;
        public var _NATIVE_unregisterRenderTarget:Function;

        public function BetaGwentUIProbe()
        {
            graphics.beginFill(0x10202A);
            graphics.drawRect(0, 0, 1920, 1080);
            graphics.endFill();
            label = new TextField();
            label.defaultTextFormat = new TextFormat("$NormalFont", 32, 0xFFFFFF);
            label.x = 80; label.y = 80; label.width = 1650; label.height = 260;
            label.multiline = true; label.selectable = false;
            addChild(label);
            show("BetaGwent UI probe\nClick to send an intent; script responds through setProbeState.");
            addEventListener(MouseEvent.CLICK, onClick);
            addEventListener(Event.ADDED_TO_STAGE, onAdded);
        }

        private function onAdded(event:Event):void
        {
            removeEventListener(Event.ADDED_TO_STAGE, onAdded);
            stage.addEventListener(KeyboardEvent.KEY_DOWN, onKey);
            // Registration supplies the script bridge; poll until it is available.
            if (ExternalInterface.available) ExternalInterface.call("registerMenu", "BetaGwentUIProbe", this);
            addEventListener(Event.ENTER_FRAME, waitForBridge);
        }

        private function waitForBridge(event:Event):void
        {
            if (initialized || _NATIVE_callGameEvent == null) return;
            initialized = true;
            removeEventListener(Event.ENTER_FRAME, waitForBridge);
            _NATIVE_callGameEvent("OnConfigUI", []);
        }

        public function setProbeState(value:int, message:String):void
        {
            counter = value;
            show("BetaGwent UI probe\nCounter: " + counter + "\n" + message);
        }

        private function onClick(event:MouseEvent):void
        {
            if (_NATIVE_callGameEvent != null) _NATIVE_callGameEvent("OnBetaGwentProbeIntent", [counter + 1]);
        }

        private function show(message:String):void { label.text = message; }

        private function onKey(event:KeyboardEvent):void
        {
            if (event.keyCode == 27 && _NATIVE_callGameEvent != null)
                _NATIVE_callGameEvent("OnBetaGwentProbeClose", []);
        }
    }
}
