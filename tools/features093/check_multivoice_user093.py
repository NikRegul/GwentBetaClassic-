"""Execute live WS language selection and the actual card dialogue queue."""
from pathlib import Path
import argparse,json,re,struct,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'))
import ws2js


def main():
    p=argparse.ArgumentParser();p.add_argument('catalog',type=Path);p.add_argument('out',type=Path);p.add_argument('--snapshot',type=Path);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True);dev=ROOT/'BetaGwent/development/scripts/game/betagwent'
    if a.snapshot:
        import hashlib
        frozen=a.snapshot/'sources/BetaGwent/development/scripts/game/betagwent'
        for name in ['duelAudioCatalog.ws','duelAudio.ws','universalLanguages.ws','developmentBoardMenu.ws']:
            assert hashlib.sha256((frozen/name).read_bytes()).hexdigest()==hashlib.sha256((dev/name).read_bytes()).hexdigest(),name
        assert a.catalog.read_bytes()==(frozen/'duelAudioCatalog.ws').read_bytes()
        dev=frozen
    board=(dev/'developmentBoardMenu.ws').read_text('utf-8-sig')
    start=board.index('    event OnBetaGwentVoiceLanguage(');end=board.index('    event OnBetaGwentTutorialSeen(',start)
    body=board[start:end].replace('event OnBetaGwentVoiceLanguage(', 'public function OnBetaGwentVoiceLanguage(')
    gate=a.out/'menu.ws';gate.write_text('class CVoiceMenu093 extends IScriptable {\npublic var audio : CBetaGwentDuelAudio;public var publications : int;\npublic function PublishLanguageSettings(){publications+=1;}\n'+body+'}\n','utf8')
    code,_=ws2js.build([ROOT/'tools/universal/native_language_signatures.ws',dev/'universalLanguages.ws',a.catalog,dev/'duelAudio.ws',gate],[])
    runtime=(a.snapshot/'runtime.js') if a.snapshot else ROOT/'BetaGwent/build/release093c-ai-plans-20261025-01/rules/runtime.js'
    script=a.out/'check.js'
    ids=sorted(set(map(int,re.findall(r'case (\d+):',a.catalog.read_text('utf-8-sig')))))
    script.write_text(runtime.read_text('utf8')+'\n'+code+'\n'+r'''
let clock=0,events=[],facts={},speech='EN',checks=0;
const StringToFloat=Number;
function FactsQueryLatestValue(key){return facts[key]||0;}
function FactsSet(key,value){facts[key]=value;}
function BetaGwentCleanupBlocked(){return false;}
const theGame={GetEngineTimeAsSeconds(){return clock;},GetGameLanguageName(a,t){a.v=speech;t.v='RU';},GetInGameConfigWrapper(){return {GetVarValue(){return '70';}};}};
const theSound={SoundIsBankLoaded(){return true;},SoundLoadBank(){},SoundUnloadBank(){},SoundGlobalParameter(){},SoundEvent(name){events.push(name);}};
Host.random=()=>0;
function check(ok,label){checks++;if(!ok)throw Error(label);}
const suffix=['','','_en','_de','_it','_pt_br'],records=[];
for(const language of [1,2,3,4,5,0]){
 clock+=10;const audio=new CBetaGwentDuelAudio();audio.Initialize();audio.SetClock(clock*1000);
 const menu=new CVoiceMenu093();menu.audio=audio;menu.OnBetaGwentVoiceLanguage(language);
 check(BetaGwentVoicePreference()===language&&menu.publications===1,'actual menu callback persists voice preference');
 const resolved=language||2;check(BetaGwentVoiceLanguage()===resolved,'Auto follows game speech independently of RU text');
 events=[];audio.Cue(1,200168,0,0,0,0,0);clock+=.5;audio.SetClock(clock*1000);audio.Tick();
 const voice=events.find(n=>n.startsWith('bg79_vo_'));check(Boolean(voice),'actual queue dispatches a leader line');
 check(resolved===1?!/_(en|de|it|pt_br)$/.test(voice):voice.endsWith(suffix[resolved]),'actual playback event uses selected language: '+language+' '+voice);
 check(audio.voiceUntil>clock,'selected language duration keeps voice alive');
 check(BetaGwentGameTextLanguage()===1,'speech choice does not alter game text');
 records.push({requested:language,resolved,event:voice,duration:audio.voiceUntil-clock});audio.Cancel();
}
globalThis.voiceReport={checks,records,actualWitcherScript:true,nativePlaybackVerified:false};
'''+f'\nconst templateIds={json.dumps(ids)};\n'+r'''
const allEvents={};
for(let lang=1;lang<=5;lang++){
 FactsSet('bg_voice_language',lang);const names=new Set();
 for(const id of templateIds)for(let roll=0;roll<100;roll++){
  const name=BetaGwentAudioVoiceVariant(id,roll);if(!name)continue;
  check(lang===1?!/_(en|de|it|pt_br)$/.test(name):name.endsWith(suffix[lang]),'all selected-language variants use the proper event');
  check(BetaGwentAudioVoiceVariantDuration(id,roll)>0,'selected-language variant has its own duration');names.add(name);
 }
 allEvents[lang]=Array.from(names);
}
voiceReport.checks=checks;voiceReport.templates=templateIds.length;
'''+f'\nrequire("fs").writeFileSync({json.dumps(str(a.out/"events.json"))},JSON.stringify(allEvents));\nrequire("fs").writeFileSync({json.dumps(str(a.out/"report.json"))},JSON.stringify(voiceReport,null,2));console.log(JSON.stringify(voiceReport));','utf8')
    subprocess.run(['node',str(script)],cwd=ROOT,check=True)
    sys.path.insert(0,str(ROOT/'tools/classic132'));from formats import sound_index
    cache=ROOT/'BetaGwent/build-inputs/classic-audio/soundspc.cache'
    _,index=sound_index(cache);expected=json.loads((a.out/'events.json').read_text('utf8'));coverage=[]
    def fnv(name):
        value=2166136261
        for byte in name.lower().encode('utf8'):value=((value*16777619)^byte)&0xffffffff
        return value
    for number,language in enumerate(['ru','en','de','it','pt_br'],1):
        bank='betagwent091_'+language+'.bnk';offset,size=index[bank];events=set()
        with cache.open('rb') as stream:
            stream.seek(offset);end=offset+size
            while stream.tell()<end:
                tag,length=struct.unpack('<4sI',stream.read(8))
                if tag!=b'HIRC':stream.seek(length,1);continue
                data=stream.read(length);count=struct.unpack_from('<I',data)[0];cursor=4
                for _ in range(count):
                    kind,extent=struct.unpack_from('<BI',data,cursor);cursor+=5
                    if kind==4:events.add(struct.unpack_from('<I',data,cursor)[0])
                    cursor+=extent
                assert cursor==len(data)
        missing=[name for name in expected[str(number)] if fnv(name) not in events];assert not missing,(language,missing[:10])
        coverage.append(dict(language=language,voiceEventsChecked=len(expected[str(number)]),missing=0))
    report=json.loads((a.out/'report.json').read_text('utf8'));report['actualClassicBankCoverage']=coverage
    (a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(coverage))


if __name__=='__main__':main()
