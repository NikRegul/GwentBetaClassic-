"""Prepare compact, muted language controls in five isolated UI copies."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'BetaGwent/build/universal081'
OUT=ROOT/'BetaGwent/build/universal081-language-layout'


def main():
    assert not OUT.exists(),'Preserve previous candidates'
    ui=OUT/'ui';shutil.copytree(BASE/'ui',ui)
    path=ui/'src/BetaGwentBoard.as';raw=path.read_bytes()
    assert raw.startswith(b'\xef\xbb\xbf') and b'\n' not in raw.replace(b'\r\n',b'')
    text=raw.decode('utf-8-sig').replace('\r\n','\n')
    old='''            editorSmallButton(content,textChoiceLabel(),52,28,276,42,true,cycleTextLanguage);
            editorSmallButton(content,voiceChoiceLabel(),340,28,276,42,true,cycleVoiceLanguage);'''
    new='''            languageButton(textChoiceLabel(),48,88,188,cycleTextLanguage);
            languageButton(voiceChoiceLabel(),244,88,188,cycleVoiceLanguage);'''
    assert text.count(old)==1;text=text.replace(old,new)
    marker='        private function betaPlaque(title:String):void'
    helper='''        private function languageButton(title:String,x:Number,y:Number,w:Number,callback:Function):void
        {
            // One quiet row aligned with the left panel, below the title.
            var button:Sprite=new Sprite();button.x=x;button.y=y;content.addChild(button);
            button.graphics.lineStyle(1,0xAA9875,.30);
            button.graphics.beginFill(0x171B19,.38);button.graphics.drawRect(0,0,w,30);button.graphics.endFill();
            var hover:Sprite=new Sprite();hover.mouseEnabled=false;
            hover.graphics.beginFill(0xCAB78F,.14);hover.graphics.drawRect(0,0,w,30);hover.graphics.endFill();
            hover.alpha=0;button.addChild(hover);
            var label:TextField=text(button,title,8,4,w-16,16,0xCBBE9E);
            label.multiline=false;label.wordWrap=false;
            if(label.textWidth>w-16)BetaGwentFonts.apply(label,BetaGwentFonts.BODY,Math.max(12,Math.floor(16*(w-16)/label.textWidth)),0xCBBE9E);
            var format:TextFormat=label.defaultTextFormat;format.align="center";
            label.defaultTextFormat=format;label.setTextFormat(format);
            label.y=Math.round((30-label.textHeight)/2)-2;label.height=label.textHeight+4;
            button.buttonMode=true;button.mouseChildren=false;buttonMotion(button,hover);
            controller.registerControl(button,title,callback,null,null,"control",null,new Rectangle(0,0,w,30));
            button.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();uiSound();callback();});
        }
'''
    assert text.count(marker)==1;text=text.replace(marker,helper+marker)
    output=b'\xef\xbb\xbf'+text.replace('\n','\r\n').encode('utf8')
    variants=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']
    for name in variants:
        folder=ui/name
        if not folder.exists():shutil.copytree(ui/'src',folder)
        (folder/'BetaGwentBoard.as').write_bytes(output)
    manifest=json.loads((BASE/'ui-inputs.json').read_text('utf8'))
    manifest['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ui/'src').glob('*.as')}
    (OUT/'ui-inputs.json').write_text(json.dumps(manifest,indent=2)+'\n','utf8')
    assert all((ui/name/'BetaGwentBoard.as').read_bytes()==output for name in variants)
    print('Prepared five identical BOM/CRLF board sources; language controls x=48/244, y=88, 188x30')


if __name__=='__main__':main()
