"""Exercise the real win hook and finite post-reward timer sequence."""
from pathlib import Path
import sys,json,subprocess
import ws2js
ROOT=Path(__file__).resolve().parents[2]
def function(text,name):
 a=text.index('function '+name+'(');start=text.rfind('\n',0,a)+1;b=text.index('{',a);i=b+1;depth=1
 while depth:
  if text[i]=='{':depth+=1
  elif text[i]=='}':depth-=1
  i+=1
 return text[start:i]
dev=ROOT/'BetaGwent/development/scripts/game/betagwent'
quest=(dev/'collectionQuest.ws').read_text('utf-8-sig');native=(dev/'nativeGwentEntry.ws').read_text('utf-8-sig')
base=ROOT/'BetaGwent/build/elements164/quest-timer';base.mkdir(parents=True,exist_ok=True)
source=base/'probe.ws';source.write_text('''class CR4GwintManager extends IScriptable { public var testMatch,betaNpcPending,gameRequested : bool; }
function BetaGwentSyncSkelligeQuestProgress() {}
class W3PlayerWitcher extends IScriptable {
 public var betaGwentQuestSyncPasses,outcome,cleanups : int;
 public function GetGwintMinigameState() : int { return outcome; }
 public function wrappedMethod() { cleanups+=1;outcome=0; }
 public function AddTimer(key : name, delay : float, repeat : bool) {}
 public function RemoveTimer(key : name) {}
'''+function(quest,'BetaGwentScheduleQuestSync')+'\n'+function(quest,'BetaGwentQuestSyncTick')+'\n'+function(native,'OnGwintGameEnded')+'\n}\n','utf8')
code,_=ws2js.build([source],[])
host=(Path(sys.argv[1])/'runtime.js').read_text('utf8')
tests=r'''
globalThis.EMS_End_PlayerWon=4;const manager=new CR4GwintManager();globalThis.theGame={GetGwintManager:()=>manager};
let timers=[],ticks=0,checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
W3PlayerWitcher.prototype.RemoveTimer=function(key){timers=timers.filter(t=>t.key!==key);};
W3PlayerWitcher.prototype.AddTimer=function(key,delay,repeat){timers.push({key,delay,repeat});};
BetaGwentSyncSkelligeQuestProgress=()=>ticks++;
for(const state of [0,8,16,24]){timers=[];const p=new W3PlayerWitcher();p.outcome=state;p.OnGwintGameEnded();check(timers.length===0&&p.cleanups===1,'loss/forfeit still cleans up and cannot start a win timer');}
timers=[];const p=new W3PlayerWitcher();p.outcome=4;p.OnGwintGameEnded();check(timers.length===1&&timers[0].delay===3&&!timers[0].repeat,'victory schedules one deferred pass outside the reward graph');
check(p.cleanups===1&&p.outcome===0,'native end-game cleanup remains intact');
for(let i=0;i<3;i++){const timer=timers.shift();p.BetaGwentQuestSyncTick(3,i);check(ticks===i+1&&timers.length===(i<2?1:0),'finite synchronization pass '+i);}
p.outcome=4;p.OnGwintGameEnded();p.outcome=4;p.OnGwintGameEnded();check(timers.length===1&&p.betaGwentQuestSyncPasses===3,'repeated scheduling replaces its own timer');
timers=[];manager.testMatch=true;const test=new W3PlayerWitcher();test.outcome=4;test.OnGwintGameEnded();check(timers.length===0,'native test matches cannot schedule quest progress');
console.log(JSON.stringify({checks,actualWitcherScript:true,nativeGameTested:false}));
'''
script=base/'test.js';script.write_text(host+'\n'+code+'\n'+tests,'utf8')
r=subprocess.run(['node',str(script)],capture_output=True,text=True,encoding='utf8');print(r.stdout,r.stderr,end='');assert r.returncode==0
(ROOT/'docs/evidence/quest-timer167.json').write_text(json.dumps(json.loads(r.stdout),indent=2)+'\n','utf8')
