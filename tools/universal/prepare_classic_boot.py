"""Prepare the Classic startup adapter without changing WitcherScript/audio."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/build/universal081-language-layout'
OUT=ROOT/'BetaGwent/build/classic081-boot-fix4'


def main():
    assert not OUT.exists(),'Keep prior candidates immutable'
    ui=OUT/'ui';shutil.copytree(SOURCE/'ui',ui)
    board=ui/'src/BetaGwentBoard.as';text=board.read_text('utf-8-sig')
    old='            background.visible=entryMode!=1;changeSkin(3); render();'
    assert text.count(old)==1
    text=text.replace(old,'            background.visible=entryMode!=1; // Render only after native registration.')
    old='            addEventListener(Event.REMOVED_FROM_STAGE,onRemoved);'
    assert text.count(old)==1
    text=text.replace(old,old+'\n            if(stage)onAdded(null); // Retail GFx may attach the document during construction.')
    start=text.index('        private function onAdded(e:Event):void')
    end=text.index('        private function onRemoved(e:Event):void',start)
    original=text[start:end]
    assert 'if(ExternalInterface.available)' in original
    bind_start=original.index('            controller.bind(keyboardStage);')
    bind_end=original.index('            if(ExternalInterface.available)')
    bindings=original[bind_start:bind_end]
    replacement='''        private var startupAttached:Boolean=false;
        private var startupError:String="";
        private function onAdded(e:Event):void
        {
            if(startupAttached)return;
            startupAttached=true;
            removeEventListener(Event.ADDED_TO_STAGE,onAdded);
            keyboardStage=stage;
            addEventListener(Event.ENTER_FRAME,waitForBridge);
            try {
                // Match the stock Classic CoreMenu protocol. The availability
                // flag is not part of its registerMenu handshake.
                ExternalInterface.call("registerMenu",registrationName(),this);
'''+bindings+'''                changeSkin(3);render();
            }catch(error:Error){
                startupError=error.toString();
                trace("BETAGWENT_AS_BOOT_ERROR "+startupError);
            }
        }
'''
    text=text[:start]+replacement+text[end:]
    old='''            connected=true; removeEventListener(Event.ENTER_FRAME,waitForBridge);
            send("OnConfigUI",[]);'''
    new='''            connected=true; removeEventListener(Event.ENTER_FRAME,waitForBridge);
            send("OnBetaGwentControllerTrace",[0,"AS_BRIDGE_READY","classic_boot_fix4",startupError]);
            if(startupError.length>0){send("OnBetaGwentBoardClose",[]);return;}
            send("OnConfigUI",[]);'''
    assert text.count(old)==1;text=text.replace(old,new)
    # Explicit object-property call, like the stock Classic GameAdapter.
    # Do not use the unqualified Function slot (Royale emits a global receiver).
    text=text.replace('_NATIVE_callGameEvent.call(this,eventName,args);','this._NATIVE_callGameEvent(eventName,args);')
    text=text.replace('_NATIVE_callGameEvent.call(this,"OnBetaGwentPerf",[eventName,spent]);','this._NATIVE_callGameEvent("OnBetaGwentPerf",[eventName,spent]);')
    text=text.replace('// Royale emits a global receiver for an unqualified Function-slot call.\n            // The native adapter requires this registered DisplayObject as receiver.',
                      '// Explicit this keeps the registered DisplayObject as native receiver.\n            // This is the direct property-call protocol used by Classic GameAdapter.')
    raw=b'\xef\xbb\xbf'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8')
    for name in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
        (ui/name/'BetaGwentBoard.as').write_bytes(raw)
    manifest=json.loads((SOURCE/'ui-inputs.json').read_text('utf8'))
    manifest['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ui/'src').glob('*.as')}
    (OUT/'ui-inputs.json').write_text(json.dumps(manifest,indent=2)+'\n','utf8')
    print('Prepared Classic fix4: early registration, attached-stage fallback, explicit native receiver, boot trace')


if __name__=='__main__':main()
