"""Exercise the actual Classic audio lifecycle and independently parse split banks."""
from pathlib import Path
import argparse,json,subprocess,sys,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'))
import ws2js

def main():
    p=argparse.ArgumentParser();p.add_argument('--prepared',type=Path,required=True);p.add_argument('--banks',type=Path,required=True);p.add_argument('--output',type=Path);a=p.parse_args()
    out=a.output or a.banks;out.mkdir(parents=True,exist_ok=True);manifest=json.loads((a.banks/'manifest.json').read_text('utf8'))
    source=a.prepared/'Mods/modBetaGwentClassic132/content/scripts/game/betagwent/duelAudio.ws'
    ws=out/'audio-lifecycle.ws';ws.write_text(source.read_text('utf16'),'utf8')
    code,_=ws2js.build([ws],[])
    runtime=(ROOT/'tools/ai/jshost/runtime.js').read_text('utf8')
    script=out/'lifecycle-test.js'
    sizes={b['name']:b['bytes'] for b in manifest['banks']}
    script.write_text(runtime+'\n'+code+'\nconst sizes='+json.dumps(sizes)+';\n'+r'''
let language=1,clock=0,loads=[],unloads=[],events=[],loaded=new Set(),checks=0;
function check(v,m){if(!v)throw Error(m);checks++;}
function BetaGwentVoiceLanguage(){return language;}
function BetaGwentAudioBankInstalled(){return true;}
function BetaGwentAudioUi(){return 'bg79_ui';}
function BetaGwentUniversalEvent(lang,n){return n;}
const StringToFloat=Number;
const theGame={GetEngineTimeAsSeconds(){return clock;},GetInGameConfigWrapper(){return {GetVarValue(){return '70';}};}};
const theSound={SoundIsBankLoaded(n){return loaded.has(n);},SoundLoadBank(n,async){
 check(n in sizes,'requested bank exists in the produced cache');check(async===false,'menu load completes before playback');
 check(sizes[n]+220*1024**2<400*1024**2,'selected bank fits a 220 MiB world sound mix');
 loads.push(n);loaded.add(n);
},SoundUnloadBank(n){unloads.push(n);loaded.delete(n);},SoundEvent(n){events.push(n);},SoundGlobalParameter(){}};
const a=new CBetaGwentDuelAudio();a.Initialize();
check(a.IsBankReady(),'Russian bank ready before the first cue');
const initialLoads=loads.length;a.RefreshBank();a.Tick();
check(loads.length===initialLoads,'unchanged language does not accumulate bank references');
for(const next of [2,3,4,5,1]){
 const previous=loads.at(-1);language=next;a.RefreshBank();
 check(unloads.at(-1)===previous&&!loaded.has(previous),'language change releases old bank');
 check(loaded.size===1&&a.IsBankReady(),'exactly one selected bank is resident');
}
check(new Set(loads).size===5,'all five produced language banks selectable');
const last=loads.at(-1);a.Close();
check(loaded.size===0&&unloads.at(-1)===last,'closing the menu releases the bank');
a.Close();check(unloads.filter(n=>n===last).length===2,'repeated close does not unload twice');
console.log(JSON.stringify({checks,actualTranspiledWitcherScript:true,gameplayVerified:false}));
''','utf8')
    result=subprocess.run(['node',str(script)],capture_output=True,text=True,check=True)
    report=json.loads(result.stdout);(out/'lifecycle-tests.json').write_text(json.dumps(report,indent=2),'utf8')
    print(result.stdout.strip())
    for bank in manifest['banks']:
        name=bank['name'];xml=out/(name+'.xml')
        if not xml.exists():
            subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/vendor/audio/wwiser.pyz'),'-d','xml','-dn',str(xml.with_suffix('')),str(a.banks/'banks'/name)],stdout=subprocess.DEVNULL,check=True)
        tree=ET.parse(xml).getroot();assert not tree.findall('.//error') and not tree.findall('.//skip'),name
        print('Independent bank parse passed:',name,flush=True)

if __name__=='__main__':main()
