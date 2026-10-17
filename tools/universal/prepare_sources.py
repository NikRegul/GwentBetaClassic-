from pathlib import Path
import json,re,shutil,hashlib,sys
ROOT=Path('D:/w3mod');BASE=ROOT/'BetaGwent/build/universal081'
sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import sha
VOICES=('ru','en','de','it','pt-br')
def read(p):
 d=p.read_bytes();return d.decode('utf16' if d[:2]==b'\xff\xfe' else 'utf-8-sig').replace('\r\n','\n')
def write(p,s,classic=False):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((b'\xff\xfe'+s.replace('\n','\r\n').encode('utf-16le')) if classic else b'\xef\xbb\xbf'+s.replace('\n','\r\n').encode('utf8'))
def patch_board(s):
 s=s.replace('    private var setTextLanguage : CScriptedFlashFunction;','    private var setTextLanguage : CScriptedFlashFunction;\n    private var setLanguageSettings : CScriptedFlashFunction;')
 s=s.replace('setTextLanguage = GetMenuFlash().GetMemberFlashFunction("setTextLanguage");','setTextLanguage = GetMenuFlash().GetMemberFlashFunction("setTextLanguage");\n        setLanguageSettings = GetMenuFlash().GetMemberFlashFunction("setLanguageSettings");')
 s=re.sub(r'if\(setTextLanguage\)setTextLanguage\.InvokeSelfOneArg\(FlashArgInt\((?:BetaGwentTextLanguage137\()?FactsQueryLatestValue\("bg_text_language"\)\)?\)\);', 'BetaGwentInitializeLanguages();\n        PublishLanguageSettings();',s)
 assert s.count('BetaGwentInitializeLanguages();')==1
 old='''        if(language<1||language>13)return false;
        FactsSet("bg_text_language",language);
        if(setTextLanguage)setTextLanguage.InvokeSelfOneArg(FlashArgInt(language));'''
 new='''        if(language<0||language>13)return false;
        FactsSet("bg_text_language",language);
        PublishLanguageSettings();'''
 assert old in s;s=s.replace(old,new)
 anchor='    event OnBetaGwentTutorialSeen()'
 code='''    private function PublishLanguageSettings()
    {
        if(setLanguageSettings)setLanguageSettings.InvokeSelfFiveArgs(FlashArgInt(BetaGwentTextPreference()),FlashArgInt(BetaGwentVoicePreference()),FlashArgInt(BetaGwentVoiceLanguage()),FlashArgInt(BetaGwentGameTextLanguage()),FlashArgInt(BetaGwentResolvedTextLanguage()));
    }
    event OnBetaGwentVoiceLanguage(language : int)
    {
        if(language<0 || language>5)return false;
        if(audio)audio.Cancel();
        FactsSet("bg_voice_language",language);
        PublishLanguageSettings();
        LogChannel('BetaGwent',"AUDIO_LANGUAGE requested="+language+" resolved="+BetaGwentVoiceLanguage());
    }
'''
 assert anchor in s;s=s.replace(anchor,code+anchor)
 assert 'setLanguageSettings : CScriptedFlashFunction' in s
 return s
def patch_audio(s):
 s=s.replace('eventName="bg79_vo_ArachasQueen";','eventName=BetaGwentUniversalEvent(BetaGwentVoiceLanguage(),"bg79_vo_ArachasQueen");')
 s=s.replace('theSound.SoundEvent("bg79_stop_voice");','theSound.SoundEvent(BetaGwentUniversalEvent(BetaGwentVoiceLanguage(),"bg79_stop_voice"));')
 s=s.replace('eventName = names[RandRange(names.Size())];','eventName = BetaGwentUniversalEvent(BetaGwentVoiceLanguage(),names[RandRange(names.Size())]);')
 return s
catalogs=[];functions=None
for lang in VOICES:
 s=read(ROOT/f'BetaGwent/build/stage202/{lang}/sources/scripts/game/betagwent/duelAudioCatalog.ws')
 names=re.findall(r'^function\s+(\w+)\(([^)]*)\)\s*:\s*(\w+)',s,re.M)
 if functions is None:functions=names
 assert {(n,p,t) for n,p,t in functions}=={(n,p,t) for n,p,t in names}
 suffix=lang.replace('-','_')
 for name,params,typ in sorted(names,key=lambda x:-len(x[0])):s=re.sub(r'\b'+name+r'\b',name+'_Universal_'+suffix,s)
 catalogs.append(s)
wrappers=[]
for name,params,typ in functions:
 args=', '.join(p.strip().split(':')[0].strip() for p in params.split(',') if p.strip())
 lines=[f'function {name}({params}) : {typ}', '{']
 if name.startswith('BetaGwentAudioVoice'):
  lines+=['    var language : int;language=BetaGwentVoiceLanguage();']
  for idx,lang in [(3,'de'),(4,'it'),(5,'pt_br'),(2,'en')]:
   call=f'{name}_Universal_{lang}({args})'
   if typ=='string':call=f'BetaGwentUniversalEvent(language,{call})'
   lines.append(f'    if(language=={idx})return {call};')
 lines.append(f'    return {name}_Universal_ru({args});');lines.append('}')
 wrappers.append('\n'.join(lines))
combined='\n'.join(catalogs+wrappers)
seed=ROOT/'BetaGwent/build/stage202/ru/sources/scripts'
ng=BASE/'nextgen-sources'
if not ng.exists():shutil.copytree(seed,ng)
old=ROOT/'BetaGwent/build/classic132-0.8.0-stage202-recovery-282e70b6ecd0/ru/scripts-prepared'
classic=BASE/'classic-prepared'
if not classic.exists():shutil.copytree(old,classic)
for directory,lowered in [(ng/'game/betagwent',False),(classic/'Mods/modBetaGwentClassic132/content/scripts/game/betagwent',True)]:
 write(directory/'developmentBoardMenu.ws',patch_board(read(directory/'developmentBoardMenu.ws')),lowered)
 write(directory/'duelAudio.ws',patch_audio(read(directory/'duelAudio.ws')),lowered)
 write(directory/'duelAudioCatalog.ws',combined,lowered)
 write(directory/'universalLanguages.ws',Path(__file__).with_name('universal_languages.ws').read_text('utf8'),lowered)
manifest=json.loads((classic/'preparation.json').read_text())
scriptroot=classic/'Mods/modBetaGwentClassic132/content/scripts'
manifest['outputScripts']={p.relative_to(scriptroot).as_posix():sha(p) for p in sorted(scriptroot.rglob('*.ws'))}
manifest['outputScriptCount']=len(manifest['outputScripts']);manifest['universalVoiceSourceStage']=202
(classic/'preparation.json').write_text(json.dumps(manifest,indent=2)+'\n','utf8')
# UI edits stay in a fresh, complete copy of the pinned Stage 202 input.
ui=BASE/'ui'
if not ui.exists():shutil.copytree(ROOT/'BetaGwent/build/stage202/common/ui',ui)
p=ui/'src/BetaGwentBoard.as';s=read(p)
s=s.replace('editorSmallButton(content,BetaGwentTextLanguage.label(),56,24,364,42,true,cycleTextLanguage);','editorSmallButton(content,textChoiceLabel(),56,24,364,42,true,cycleTextLanguage);\n            editorSmallButton(content,voiceChoiceLabel(),56,78,364,42,true,cycleVoiceLanguage);')
# The pinned Stage 202 source still has the original single-button geometry.
s=s.replace('editorSmallButton(content,BetaGwentTextLanguage.label(),52,28,276,42,true,cycleTextLanguage);','editorSmallButton(content,textChoiceLabel(),56,24,364,42,true,cycleTextLanguage);\n            editorSmallButton(content,voiceChoiceLabel(),56,78,364,42,true,cycleVoiceLanguage);')
s=s.replace('{id:"language",title:"Текст: "+BetaGwentTextLanguage.label(),enabled:true,action:cycleTextLanguage},','{id:"language",title:textChoiceLabel(),enabled:true,action:cycleTextLanguage},\n                    {id:"audioLanguage",title:voiceChoiceLabel(),enabled:true,action:cycleVoiceLanguage},')
s=s.replace('send("OnBetaGwentTextLanguage",[BetaGwentTextLanguage.language]);','')
start=s.index('        private function cycleTextLanguage():void');end=s.index('\n        }',start)+len('\n        }')
s=s[:start]+'''        private var requestedTextLanguage:int=0;
        private var requestedVoiceLanguage:int=0;
        private var resolvedVoiceLanguage:int=2;
        private var gameTextLanguage:int=2;
        private const voiceNames:Array=["Auto","Русский","English","Deutsch","Italiano","Português (Brasil)"];
        private function textChoiceLabel():String
        { return "Текст: "+(requestedTextLanguage==0?"Авто · ":"")+BetaGwentTextLanguage.label(); }
        private function voiceChoiceLabel():String
        { return "Озвучка: "+(requestedVoiceLanguage==0?"Авто · ":"")+voiceNames[resolvedVoiceLanguage]; }
        public function setLanguageSettings(textChoice:int,voiceChoice:int,voiceResolved:int,gameText:int,textResolved:int):void
        {
            requestedTextLanguage=Math.max(0,Math.min(13,textChoice));
            requestedVoiceLanguage=Math.max(0,Math.min(5,voiceChoice));
            resolvedVoiceLanguage=Math.max(1,Math.min(5,voiceResolved));gameTextLanguage=gameText;
            setTextLanguage(textResolved);
            if(controllerMenuOpen){closeControllerMenu();openControllerMenu();}else if(ready)render();
        }
        private function cycleTextLanguage():void
        {
            requestedTextLanguage=(requestedTextLanguage+1)%14;
            setTextLanguage(requestedTextLanguage==0?gameTextLanguage:requestedTextLanguage);
            send("OnBetaGwentTextLanguage",[requestedTextLanguage]);
        }
        private function cycleVoiceLanguage():void
        { requestedVoiceLanguage=(requestedVoiceLanguage+1)%6;send("OnBetaGwentVoiceLanguage",[requestedVoiceLanguage]); }
'''+s[end:]
for name in ['src','src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder']:
 if (ui/name).exists():write(ui/name/'BetaGwentBoard.as',s)
record=json.loads((ROOT/'docs/evidence/stage202-completion.json').read_text());record['sources']={p.name:sha(p) for p in (ui/'src').glob('*.as')}
(BASE/'ui-inputs.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
print('Prepared',len(manifest['outputScripts']),'Classic scripts; catalog',len(combined),'bytes; UI button added')
