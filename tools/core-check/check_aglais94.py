"""Execute Aglais's actual WS selection branch and Card.Move body as C#.

Reproduces the REDkit failure: Doomed + transfer into Graveyard removes the
special before nested play. Tests both acting sides and invalid pile picks.
This checks the sequencing seam; native ability reactions remain untested.
"""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[2]
SCOIA=ROOT/'BetaGwent/development/scripts/game/betagwent/duelScoia.ws'
CARD=ROOT/'BetaGwent/development/scripts/game/betagwent/duelLiveCard.ws'
BUILD=ROOT/'BetaGwent/build/aglais94';BUILD.mkdir(parents=True,exist_ok=True)

def block(text,marker):
 start=text.index('{',text.index(marker))+1;pos=start;depth=1
 while depth:
  depth+=(text[pos]=='{')-(text[pos]=='}');pos+=1
 return text[start:pos-1]

scoia=SCOIA.read_text('utf-8-sig');card=CARD.read_text('utf-8-sig')
selection=block(scoia[scoia.index('public function Select('):],'if(id==142106)')
move=block(card,'public function Move(')
def cs(text):return text.replace("'BetaGwent'",'"BetaGwent"')
program=r'''using System;
class Header { public int typeMask=2; }
class State { public int instanceId=15,ownerId,controllerId,positionPlayerId,locationMask,locationIndex,tokenMask,runtimeTierMask=2;
 public bool canBePlayed=true,isWaitingToDie; public Header runtimeTemplate=new Header(); }
class Card { public State cardState=new State(); public int removed;
 void LogChannel(string c,string message){removed++;}
 public void AddTokens(int tokens){cardState.tokenMask|=tokens;}
 public void Move(int side,int zone,int index){MOVE_BODY}
}
class Game { public int actingSide,played,rejected;
 public void NorthMoveInactive(Card card,int side,int zone,bool reset){card.Move(side,zone,0);}
 public void MonsterPlayExisting(Card source,Card card){
  if(card.cardState.locationMask!=32||card.cardState.positionPlayerId!=actingSide)throw new Exception("Nested card missing");
  played++;card.Move(actingSide,256,0);
 }
}
class Program {
 Game game=new Game(); void LogChannel(string c,string message){} void Played(Card source){game.rejected++;}
 void Select(Card source,Card target,int side){var t=target.cardState;int enemy=3-side,selected=15;game.actingSide=side;SELECT_BODY}
 void Check(int side,int tier,int zone,bool own,bool waiting,bool doomed,bool unit,bool valid){
  game=new Game();var source=new Card();var target=new Card();var s=target.cardState;
  s.ownerId=own?side:3-side;s.positionPlayerId=s.ownerId;s.controllerId=s.ownerId;
  s.locationMask=zone;s.runtimeTierMask=tier;s.isWaitingToDie=waiting;s.tokenMask=doomed?512:0;
  s.runtimeTemplate.typeMask=unit?4:2;
  int owner=s.ownerId;Select(source,target,side);
  if(valid){
   if(game.played!=1||game.rejected!=0||target.removed!=0||s.locationMask!=256||s.ownerId!=owner)
    throw new Exception("Replay was removed early or ownership changed");
   target.Move(side,32,0);
   if(target.removed!=1||s.locationMask!=512)throw new Exception("Replayed special was not banished once");
  }else if(game.played!=0||game.rejected!=1||target.removed!=0||s.locationMask!=zone)
   throw new Exception("Invalid pick changed the card");
 }
 static void Main(){var p=new Program();
  foreach(int side in new[]{1,2})foreach(int tier in new[]{2,4})p.Check(side,tier,32,false,false,false,false,true);
  p.Check(2,8,32,false,false,false,false,false);
  p.Check(2,2,16,false,false,false,false,false);
  p.Check(2,2,32,true,false,false,false,false);
  p.Check(2,2,32,false,true,false,false,false);
  p.Check(2,2,32,false,false,true,false,false);
  p.Check(2,2,32,false,false,false,true,false);
  Console.WriteLine("Passed 10 Aglais replay/banish cases.");
 }
}'''.replace('MOVE_BODY',cs(move)).replace('SELECT_BODY',cs(selection))
(BUILD/'Program.cs').write_text(program,'utf8')
(BUILD/'aglais.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net7.0</TargetFramework><CheckEolTargetFramework>false</CheckEolTargetFramework></PropertyGroup></Project>','utf8')
offline=BUILD/'empty-feed';offline.mkdir(exist_ok=True)
run=subprocess.run(['dotnet','run','--project',str(BUILD/'aglais.csproj'),'--property:RestoreSources='+str(offline)],cwd=BUILD,capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
report=dict(passed=run.returncode==0,cases=10,sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SCOIA,CARD)},stdout=run.stdout,stderr=run.stderr,nativeRuntimeVerified=False)
(ROOT/'docs/evidence/aglais94.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
print(run.stdout);print(run.stderr);raise SystemExit(run.returncode)
