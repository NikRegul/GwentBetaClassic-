"""Prepare both UI variants for the native Windows clipboard capability probe."""
from pathlib import Path
import json,re,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/build/release090-decrement-fix'
OUT=ROOT/'BetaGwent/build/release090-native-clipboard'
COPIES=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']
ERRORS=['',
'Копирование недоступно. Проверьте установку файлов bin.',
'Copy unavailable. Check that the bin files are installed.',
'Kopieren nicht verfügbar. Installation der bin-Dateien prüfen.',
'Copie indisponible. Vérifiez les fichiers du dossier bin.',
'Copia non disponibile. Controlla i file nella cartella bin.',
'Kopiowanie niedostępne. Sprawdź instalację plików bin.',
'No se puede copiar. Comprueba los archivos de la carpeta bin.',
'No se puede copiar. Revisa los archivos de la carpeta bin.',
'Cópia indisponível. Confira os arquivos da pasta bin.',
'コピーできません。binフォルダーのファイルを確認してください。',
'복사할 수 없습니다. bin 폴더의 파일 설치를 확인하세요.',
'无法复制。请检查bin文件是否已安装。',
'無法複製。請檢查bin檔案是否已安裝。']
FUNCTION='''        private function copyExchange():Boolean
        {
            if(!nameField||!nameField.text.length)return false;
            if(keyboardStage)keyboardStage.focus=nameField;
            nameField.setSelection(0,nameField.text.length);
            try {
                var clipboardClass:Object=getDefinitionByName("flash.desktop.Clipboard");
                // Unknown formats return false in the unmodified runtime. The
                // native bridge answers this side-effect-free capability probe.
                var clipboard:Object=clipboardClass.generalClipboard;
                if(!clipboard.setData("betagwent:windows-clipboard-v1",""))throw new Error("native clipboard unavailable");
                if(!clipboard.setData("air:text",nameField.text))throw new Error("Windows clipboard write failed");
                BetaGwentTextLanguage.assign(exchangeMessage,"Код колоды скопирован.");return true;
            }catch(error:Error){BetaGwentTextLanguage.assign(exchangeMessage,"Копирование недоступно. Проверьте установку файлов bin.");return false;}
        }
'''

def write(path,text):path.write_bytes(b'\xef\xbb\xbf'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))

def main():
    assert not OUT.exists()
    for platform in ['classic','nextgen']:
        target=OUT/platform;target.mkdir(parents=True)
        shutil.copytree(SOURCE/platform/'ui',target/'ui')
        path=target/'ui/src/BetaGwentBoard.as';text=path.read_text('utf-8-sig')
        start=text.index('        private function copyExchange():Boolean')
        end=text.index('        private function pasteExchange()',start)
        text=text[:start]+FUNCTION+text[end:];write(path,text)
        language=target/'ui/src/BetaGwentExchangeText082.as';text=language.read_text('utf-8-sig')
        for var in ['KEYS','VALUES']:
            m=re.search(r'private static const '+var+r':Array=(\[.*?\]);',text,re.S)
            values=json.loads(m[1])
            if var=='KEYS':values[9]=ERRORS[1]
            else:
                assert len(values)==14
                for lang in range(1,14):values[lang][9]=ERRORS[lang]
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
    print('Prepared native copy/probe for both platforms and five mirrors each.')

if __name__=='__main__':main()
