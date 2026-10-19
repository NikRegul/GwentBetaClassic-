"""Keep native copy events and add an explicit log-to-Windows clipboard fallback."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'BetaGwent/build/release090-integrated'
BASE=ROOT/'BetaGwent/build/release082-polish2'

def write(p,s):p.write_bytes(b'\xef\xbb\xbf'+s.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    for platform in ['classic','nextgen']:
        for name in ['ui','extra-resources']:shutil.copytree(BASE/platform/name,OUT/platform/name)
        for name in ['ui-inputs.json','subimages.json']:
            if (BASE/platform/name).exists():shutil.copy2(BASE/platform/name,OUT/platform/name)
        ui=OUT/platform/'ui';p=ui/'src/BetaGwentBoard.as';s=p.read_text('utf-8-sig')
        old='else if(e.ctrlKey&&key==67&&!exchangeImport){if(copyExchange()){e.preventDefault();e.stopImmediatePropagation();}}'
        new='else if(e.ctrlKey&&key==67&&!exchangeImport){if(nameField&&keyboardStage){keyboardStage.focus=nameField;nameField.setSelection(0,nameField.text.length);}/* Keep the native copy event; API success need not mean Windows clipboard. */}'
        assert old in s;s=s.replace(old,new)
        old='''            if(!nameField||!nameField.text.length)return false;
            try {
                var clipboardClass:Object=getDefinitionByName("flash.desktop.Clipboard");'''
        new='''            if(!nameField||!nameField.text.length)return false;
            if(keyboardStage)keyboardStage.focus=nameField;
            nameField.setSelection(0,nameField.text.length);
            try {
                var systemClass:Object=getDefinitionByName("flash.system.System");
                systemClass.setClipboard(nameField.text);
                BetaGwentTextLanguage.assign(exchangeMessage,"Буфер недоступен. Используйте Ctrl+C.");
                exchangeMessage.appendText("\\nBG1 → scriptslog.txt → Copy-Deck-Code.cmd");return true;
            }catch(systemError:Error){}
            try {
                var clipboardClass:Object=getDefinitionByName("flash.desktop.Clipboard");'''
        assert old in s;s=s.replace(old,new)
        s=s.replace('BetaGwentTextLanguage.assign(exchangeMessage,"Код колоды скопирован.");return true;', 'BetaGwentTextLanguage.assign(exchangeMessage,"Буфер недоступен. Используйте Ctrl+C.");exchangeMessage.appendText("\\nBG1 → scriptslog.txt → Copy-Deck-Code.cmd");return true;')
        s=s.replace('BetaGwentTextLanguage.assign(exchangeMessage,"Буфер недоступен. Используйте Ctrl+C.");return false;', 'BetaGwentTextLanguage.assign(exchangeMessage,"Буфер недоступен. Используйте Ctrl+C.");exchangeMessage.appendText("\\nBG1 → scriptslog.txt → Copy-Deck-Code.cmd");return false;')
        old='''            if(keyboardStage)keyboardStage.focus=nameField;
            controller.focusTag("control");
        }
        public function setDeckExchange'''
        new='''            controller.focusTag("control");
            if(keyboardStage)keyboardStage.focus=nameField;
        }
        public function setDeckExchange'''
        assert old in s;s=s.replace(old,new)
        old='if(code.length){nameField.text=code;nameField.setSelection(0,code.length);copyExchange();}'
        new='if(code.length){nameField.text=code;nameField.setSelection(0,code.length);copyExchange();if(keyboardStage)keyboardStage.focus=nameField;}'
        assert old in s;s=s.replace(old,new)
        # Existing translated clipboard error now becomes an honest instruction,
        # irrespective of whether this runtime connects GFx to the OS clipboard.
        translations={
            'Буфер недоступен. Используйте Ctrl+C.':'Выделен весь код. Нажмите Ctrl+C и проверьте вставку в сообщении.',
            'Clipboard unavailable. Use Ctrl+C.':'The full code is selected. Press Ctrl+C and test pasting into your message.',
        }
        lang=ui/'src/BetaGwentTextLanguage.as';t=lang.read_text('utf-8-sig')
        for a,b in translations.items():
            # Translation keys in both Board and dictionary must stay identical.
            s=s.replace(a,b);t=t.replace(a,b)
        write(p,s);write(lang,t)
        for mirror in ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
            for name in ['BetaGwentBoard.as','BetaGwentTextLanguage.as']:shutil.copy2(ui/'src'/name,ui/mirror/name)
        manifest=json.loads((OUT/platform/'ui-inputs.json').read_text('utf8'))
        manifest['sources']={p.name:sha(p) for p in (ui/'src').glob('*.as')}
        (OUT/platform/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
    for mirror in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
        for name in ['BetaGwentBoard.as','BetaGwentTextLanguage.as']:shutil.copy2(OUT/'nextgen/ui'/mirror/name,ROOT/'BetaGwent/ui'/mirror/name)
    # The export line contains only the user's own validated deck, no save data.
    for p in [OUT/'scripts/game/betagwent/developmentBoardMenu.ws',ROOT/'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws']:
        s=p.read_text('utf-8-sig');old='        PublishDeckExchange(code,"",false);return true;'
        assert s.count(old)==1
        write(p,s.replace(old,'        LogChannel(\'BetaGwent\',"BG1_EXPORT "+code);\n'+old))
    print('Export focus/native Ctrl+C repaired; OS clipboard needs game acceptance; log fallback enabled.')

if __name__=='__main__':main()
