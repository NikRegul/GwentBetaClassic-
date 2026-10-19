"""Freeze bidirectional Windows clipboard UI inputs on top of the reviewed UI."""
from pathlib import Path
import hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/build/release090-ui-review2'
OUT=ROOT/'BetaGwent/build/release090-windows-paste'
COPIES=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']
ERRORS=['',
'Не удалось вставить код BG1. Скопируйте код в Windows и проверьте файлы bin.',
'Could not paste a BG1 code. Copy the code in Windows and check the bin files.',
'BG1-Code konnte nicht eingefügt werden. Code in Windows kopieren und bin-Dateien prüfen.',
'Impossible de coller le code BG1. Copiez-le dans Windows et vérifiez les fichiers bin.',
'Impossibile incollare il codice BG1. Copialo in Windows e controlla i file bin.',
'Nie można wkleić kodu BG1. Skopiuj kod w Windows i sprawdź pliki bin.',
'No se pudo pegar el código BG1. Cópialo en Windows y comprueba los archivos bin.',
'No se pudo pegar el código BG1. Cópialo en Windows y revisa los archivos bin.',
'Não foi possível colar o código BG1. Copie-o no Windows e confira os arquivos bin.',
'BG1コードを貼り付けられません。Windowsでコードをコピーし、binのファイルを確認してください。',
'BG1 코드를 붙여넣을 수 없습니다. Windows에서 코드를 복사하고 bin 파일을 확인하세요.',
'无法粘贴BG1代码。请在Windows中复制代码并检查bin文件。',
'無法貼上BG1代碼。請在Windows中複製代碼並檢查bin檔案。']
READER='''        private function clipboardText():String
        {
            try {
                var clipboardClass:Object=getDefinitionByName("flash.desktop.Clipboard");
                var clipboard:Object=clipboardClass.generalClipboard;
                if(!clipboard.setData("betagwent:windows-paste-v1",""))return "";
                if(!clipboard.setData("betagwent:windows-paste-begin-v1",""))return "";
                // One immutable Windows snapshot, decoded through the existing
                // Boolean API. Never fall back to stale internal Flash text.
                var alphabet:String="0123456789:,BG",value:String="";
                for(var position:int=0;position<=320;position++){
                    var symbol:int=0;
                    for(var bit:int=0;bit<4;bit++)
                        if(clipboard.setData("betagwent:windows-paste-bit-v1",position+":"+bit))symbol|=1<<bit;
                    if(symbol==0)return /^BG1:(2|4|8|16|32):[1-9][0-9]*:[1-9][0-9]*(,[1-9][0-9]*){24,39}$/.test(value)?value:"";
                    if(symbol>alphabet.length)return "";
                    value+=alphabet.charAt(symbol-1);
                }
                return "";
            }catch(error:Error){return "";}
        }
'''

def write(path,text):
    path.write_bytes(b'\xef\xbb\xbf'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))

def main():
    assert not OUT.exists(),'Preserve frozen candidates'
    for platform in ['classic','nextgen']:
        target=OUT/platform;target.mkdir(parents=True)
        shutil.copytree(SOURCE/platform/'ui',target/'ui')
        path=target/'ui/src/BetaGwentBoard.as';text=path.read_text('utf-8-sig')
        start=text.index('        private function clipboardText():String')
        end=text.index('        private function copyExchange()',start)
        text=text[:start]+READER+text[end:]
        old='else if(e.ctrlKey&&key==86&&exchangeImport){if(clipboardText().length>0){pasteExchange();e.preventDefault();e.stopImmediatePropagation();}}'
        assert text.count(old)==1
        text=text.replace(old,'else if(e.ctrlKey&&key==86&&exchangeImport){pasteExchange();e.preventDefault();e.stopImmediatePropagation();}')
        assert text.count('"Буфер пуст. Вставьте код вручную."')==1
        text=text.replace('"Буфер пуст. Вставьте код вручную."',json.dumps(ERRORS[1],ensure_ascii=False))
        write(path,text)
        language=target/'ui/src/BetaGwentExchangeText082.as';text=language.read_text('utf-8-sig')
        for name in ['KEYS','VALUES']:
            m=re.search(r'private static const '+name+r':Array=(\[.*?\]);',text,re.S);values=json.loads(m[1])
            if name=='KEYS':
                index=values.index('Буфер пуст. Вставьте код вручную.');values[index]=ERRORS[1]
            else:
                assert len(values)==14
                for lang in range(1,14):values[lang][index]=ERRORS[lang]
            text=text[:m.start(1)]+json.dumps(values,ensure_ascii=False,separators=(',',':'))+text[m.end(1):]
        write(language,text)
        for folder in COPIES:
            for name in ['BetaGwentBoard.as','BetaGwentExchangeText082.as']:
                if folder!='src':shutil.copy2(target/'ui/src'/name,target/'ui'/folder/name)
                if platform=='nextgen':shutil.copy2(target/'ui/src'/name,ROOT/'BetaGwent/ui'/folder/name)
        manifest=json.loads((SOURCE/platform/'ui-inputs.json').read_text('utf8'))
        manifest['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (target/'ui/src').glob('*.as')}
        (target/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
        if platform=='classic':shutil.copy2(SOURCE/'classic/subimages.json',target/'subimages.json')
    shutil.copytree(SOURCE/'scripts',OUT/'scripts')
    print('Prepared Windows paste UI for both platforms, five BOM/CRLF mirrors, 13 languages.')

if __name__=='__main__':main()
