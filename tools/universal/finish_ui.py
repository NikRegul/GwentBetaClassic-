from pathlib import Path
import json,hashlib
base=Path('D:/w3mod/BetaGwent/build/universal081')
for parent,encoding in [(base/'nextgen-sources/game/betagwent','utf-8-sig'),(base/'classic-prepared/Mods/modBetaGwentClassic132/content/scripts/game/betagwent','utf16')]:
 p=parent/'developmentBoardMenu.ws';s=p.read_text(encoding).replace('setLanguageSettings.InvokeSelfFiveArgs(','setLanguageSettings.InvokeSelfSixArgs(').replace('FlashArgInt(BetaGwentResolvedTextLanguage()));','FlashArgInt(BetaGwentResolvedTextLanguage()),FlashArgString(BetaGwentGameVoiceName()));')
 s=s.replace('\r\n','\n').replace('\n','\r\n');p.write_bytes((b'\xff\xfe'+s.encode('utf-16le')) if encoding=='utf16' else b'\xef\xbb\xbf'+s.encode())
p=base/'ui/src/BetaGwentBoard.as';s=p.read_text('utf-8-sig')
s=s.replace('private const voiceNames:Array=["Auto","Русский","English","Deutsch","Italiano","Português (Brasil)"];','private const voiceNames:Array=["Auto","RU","EN","DE","IT","PT-BR"];\n        private var gameVoiceName:String="EN";\n        private const textWords:Array=["","Текст","Text","Text","Texte","Testo","Tekst","Texto","Texto","Texto","テキスト","텍스트","文本","文字"];\n        private const voiceWords:Array=["","Озвучка","Audio","Audio","Voix","Audio","Dźwięk","Audio","Audio","Áudio","音声","음성","语音","語音"];\n        private const autoWords:Array=["","Авто","Auto","Auto","Auto","Auto","Auto","Auto","Auto","Auto","自動","자동","自动","自動"];')
s=s.replace('return "Текст: "+(requestedTextLanguage==0?"Авто · ":"")+BetaGwentTextLanguage.label();','return textWords[BetaGwentTextLanguage.language]+": "+(requestedTextLanguage==0?autoWords[BetaGwentTextLanguage.language]+" · ":"")+BetaGwentTextLanguage.label();')
s=s.replace('return "Озвучка: "+(requestedVoiceLanguage==0?"Авто · ":"")+voiceNames[resolvedVoiceLanguage];','return voiceWords[BetaGwentTextLanguage.language]+": "+(requestedVoiceLanguage==0?autoWords[BetaGwentTextLanguage.language]+" · "+(gameVoiceName!=voiceNames[resolvedVoiceLanguage]?gameVoiceName+" → ":""):"")+voiceNames[resolvedVoiceLanguage];')
s=s.replace('gameText:int,textResolved:int):void','gameText:int,textResolved:int,gameVoice:String):void').replace('resolvedVoiceLanguage=Math.max(1,Math.min(5,voiceResolved));gameTextLanguage=gameText;','resolvedVoiceLanguage=Math.max(1,Math.min(5,voiceResolved));gameTextLanguage=gameText;gameVoiceName=gameVoice;')
for variant in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
 p=base/'ui'/variant/'BetaGwentBoard.as'
 if p.parent.exists():p.write_bytes(b'\xef\xbb\xbf'+s.replace('\r\n','\n').replace('\n','\r\n').encode())
p=base/'ui-inputs.json';m=json.loads(p.read_text());m['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (base/'ui/src').glob('*.as')};p.write_text(json.dumps(m,indent=2))
p=base/'classic-prepared/preparation.json';m=json.loads(p.read_text());d=base/'classic-prepared/Mods/modBetaGwentClassic132/content/scripts';m['outputScripts']={p.relative_to(d).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in d.rglob('*.ws')};p.write_text(json.dumps(m,indent=2))
print('UI and Classic input hashes updated')
