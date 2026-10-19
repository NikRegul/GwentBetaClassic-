from pathlib import Path
import json,re,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'BetaGwent/build/release090-integrated'
MESSAGES=['',
'Код выделен. Ctrl+C; если вставка не работает, используйте Copy-Deck-Code.cmd.',
'Code selected. Ctrl+C; if pasting fails, use Copy-Deck-Code.cmd.',
'Code markiert. Strg+C; falls Einfügen nicht klappt: Copy-Deck-Code.cmd.',
'Code sélectionné. Ctrl+C ; si le collage échoue : Copy-Deck-Code.cmd.',
'Codice selezionato. Ctrl+C; se non si incolla: Copy-Deck-Code.cmd.',
'Kod zaznaczony. Ctrl+C; jeśli wklejanie nie działa: Copy-Deck-Code.cmd.',
'Código seleccionado. Ctrl+C; si no se pega: Copy-Deck-Code.cmd.',
'Código seleccionado. Ctrl+C; si no se pega: Copy-Deck-Code.cmd.',
'Código selecionado. Ctrl+C; se não colar: Copy-Deck-Code.cmd.',
'コードを選択しました。Ctrl+Cでコピーできない場合はCopy-Deck-Code.cmdを使用してください。',
'코드를 선택했습니다. Ctrl+C로 복사되지 않으면 Copy-Deck-Code.cmd를 사용하세요.',
'已选中代码。Ctrl+C后无法粘贴时，请使用Copy-Deck-Code.cmd。',
'已選取代碼。Ctrl+C後無法貼上時，請使用Copy-Deck-Code.cmd。']

def write(p,s):p.write_bytes(b'\xef\xbb\xbf'+s.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

for platform in ['classic','nextgen']:
 ui=BUILD/platform/'ui';p=ui/'src/BetaGwentBoard.as';s=p.read_text('utf-8-sig')
 start=s.index('            try {\n                var systemClass:Object=')
 end=s.index('            try {\n                var clipboardClass:Object=',start)
 s=s[:start]+s[end:]
 s=s.replace('Выделен весь код. Нажмите Ctrl+C и проверьте вставку в сообщении.','Буфер недоступен. Используйте Ctrl+C.')
 write(p,s)
 p=ui/'src/BetaGwentExchangeText082.as';s=p.read_text('utf-8-sig')
 m=re.search(r'private static const VALUES:Array=(\[.*?\]);',s,re.S);values=json.loads(m[1])
 assert len(values)==14
 for i in range(1,14):values[i][9]=MESSAGES[i]
 s=s[:m.start(1)]+json.dumps(values,ensure_ascii=False,separators=(',',':'))+s[m.end(1):];write(p,s)
 for mirror in ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
  for name in ['BetaGwentBoard.as','BetaGwentExchangeText082.as']:shutil.copy2(ui/'src'/name,ui/mirror/name)
 manifest=json.loads((BUILD/platform/'ui-inputs.json').read_text('utf8'));manifest['sources']={p.name:sha(p) for p in (ui/'src').glob('*.as')}
 (BUILD/platform/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
for mirror in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
 for name in ['BetaGwentBoard.as','BetaGwentExchangeText082.as']:shutil.copy2(BUILD/'nextgen/ui'/mirror/name,ROOT/'BetaGwent/ui'/mirror/name)
print('Unimplemented System.setClipboard removed; all 13 clipboard instructions localized.')
