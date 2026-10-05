"""Execute WS creation/row/cursor seams as C#, with native integration left pending.

Uses actual method bodies, including the generated Roar/Bear definitions. Does
not simulate a complete match or the renderer. No network restore is needed.
"""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[2]
DIR=ROOT/'BetaGwent/development/scripts/game/betagwent'
BUILD=ROOT/'BetaGwent/build/turn-liveness97';BUILD.mkdir(parents=True,exist_ok=True)
def body(text,marker):
 start=text.index('{',text.index(marker))+1;pos=start;depth=1
 while depth:
  depth+=(text[pos]=='{')-(text[pos]=='}');pos+=1
 return text[start:pos-1]
files=['duelSession.ws','duelEffectRuntime.ws','developmentBoardMenu.ws','duelCatalog.ws']
source={n:(DIR/n).read_text('utf-8-sig') for n in files}
def cs(text):
 types={'SBetaGwentCardSnapshot':'State','SBetaGwentDuelDefinition':'Definition','CBetaGwentDuelCard':'Card','bool':'bool','int':'int'}
 def decl(m):return types[m[2]]+' '+m[1]+';'
 text=re.sub(r'var ([\w, ]+)\s*:\s*(\w+)\s*;',decl,text)
 text=text.replace('new CBetaGwentDuelCard in this','new Card()').replace('NULL','null').replace("'BetaGwent'",'"BetaGwent"')
 for n in ['source','child','game','runtime','pendingCard']:text=text.replace('!'+n+' ',n+'==null ').replace('!'+n+')',n+'==null)').replace('!'+n+' ||',n+'==null ||')
 text=text.replace('registry.Find(id))','registry.Find(id)!=null)').replace('game.FindCard(instanceId))','game.FindCard(instanceId)!=null)')
 return text
methods={n:cs(body(source['duelSession.ws'],'function '+n+'(')) for n in ('CreationAllowed','ApplyCreatedCard','BestNestedRow','ValidMonsterRow','IsPlayAncestor','ExistingChildAvailable','FailAbility')}
action=source['duelEffectRuntime.ws'].split('class CBetaGwentDuelCreatedCardAction',1)[1]
methods['CreatedValid']=cs(body(action,'function IsValid('))
methods['Cursor']=cs(body(source['developmentBoardMenu.ws'],'function SetOwnedMouseCursor('))
# Parse generated fields for the actual Roar and Bear cards, rather than
# inventing their creation IDs in the fixtures.
catalog=source['duelCatalog.ws']
roar=catalog[catalog.index('value.title = "Леденящий кровь рык"'):]
roar=roar[:roar.index('return value;')]
assert re.search(r'value.effect\s*=\s*28;',roar) and re.search(r'value.specialMode\s*=\s*25;',roar)
bear=int(re.search(r'value.playTemplateId\s*=\s*(\d+);',roar)[1]);assert bear==152406
program=r'''using System;using System.Collections.Generic;
class Header {public int templateId,typeMask;}
class Definition {public Header header=new Header();public int effect,specialMode,playTemplateId,deploySpawnTemplate;}
class State {public int instanceId,locationMask,positionPlayerId;public bool isWaitingToDie;}
class Card {public State s=new State();public Definition d=new Definition();public bool createdCopy,playable,spy;
 public State Snapshot()=>s;public Definition Definition()=>d;
 public void Setup(Game g,int id,int template,int side,int zone,int index){s=new State{instanceId=id,positionPlayerId=side,locationMask=zone};d=g.BetaGwentDuelDefinition(template);}
 public void SetPlayable(bool p){playable=p;}}
class Items<T>:List<T>{public int Size()=>Count;public void PushBack(T v)=>Add(v);}
class Registry {public Dictionary<int,Card> cards=new Dictionary<int,Card>();public Card Find(int id)=>cards.GetValueOrDefault(id);public bool Put(int id,Card c)=>cards.TryAdd(id,c);}
class Game {
 public Registry registry=new Registry();public Items<Card> live=new Items<Card>(),playStack=new Items<Card>();public Items<int> pendingIds=new Items<int>();
 public Card pendingCard;public bool pendingRow,approved=true,fatal;public int mode=9,preferred=1;public string message="";
 public HashSet<(int,int)> full=new HashSet<(int,int)>();
 public Definition BetaGwentDuelDefinition(int id)=>new Definition{header=new Header{templateId=id==999999?0:id,typeMask=4}};
 public Card FindCard(int id)=>registry.Find(id);
 public bool MonsterCreationAllowed(Card s,int t)=>approved;
 public int NorthActingSide(Card c)=>c.s.positionPlayerId;
 public int BetaGwentOpponentId(int side)=>3-side;
 public int MonsterPlaySide(Card c,int side)=>c.spy?3-side:side;
 public int BestCardRow(int side,Definition d)=>preferred;
 public bool CanInsertUnit(int side,int row,int index)=>(row==1||row==2||row==4)&&!full.Contains((side,row));
 public int BestOwnRow(int side){foreach(int r in new[]{1,2,4})if(CanInsertUnit(side,r,-3))return r;return 0;}
 public int SpecialRowMode()=>mode;public void LogChannel(string c,string t){}
 public bool CreationAllowed(Card source,int templateId){BODY_CreationAllowed}
 public bool ApplyCreatedCard(Card source,int templateId,int id){BODY_ApplyCreatedCard}
 public int BestNestedRow(Card card){BODY_BestNestedRow}
 public bool ValidMonsterRow(int side,int row){BODY_ValidMonsterRow}
 public bool IsPlayAncestor(Card card){BODY_IsPlayAncestor}
 public bool ExistingChildAvailable(Card source,Card child){BODY_ExistingChildAvailable}
 public void FailAbility(string reason){BODY_FailAbility}
}
class Creation {public Game game;public object runtime=new object();public Card source;public int instanceId,templateId;public bool IsValid(){BODY_CreatedValid}}
class Gui {public int balance,calls;public void RequestMouseCursor(bool v){balance+=v?1:-1;calls++;if(balance<0)throw new Exception("Cursor underflow");}}
class NativeGame {public Gui gui=new Gui();public Gui GetGuiManager()=>gui;}
class Menu {public NativeGame theGame=new NativeGame();public bool mouseCursorOwned;public void Set(bool visible){BODY_Cursor}}
class Program {
 static int cases;static void Check(bool value,string message){cases++;if(!value)throw new Exception(message);}
 static Card Source(int effect,int mode,int zone)=>new Card{d=new Definition{effect=effect,specialMode=mode,playTemplateId=152406,deploySpawnTemplate=113302},s=new State{instanceId=1,positionPlayerId=2,locationMask=zone}};
 static void Main(){
  var g=new Game();var roar=Source(28,25,256);var a=new Creation{game=g,source=roar,instanceId=100,templateId=152406};
  Check(a.IsValid(),"Roar preparation rejects Bear");Check(g.ApplyCreatedCard(roar,152406,100),"Roar application rejects Bear");
  Check(g.FindCard(100).s.locationMask==128 && g.FindCard(100).s.positionPlayerId==2 && g.FindCard(100).playable,"Bear not playable in Spawn");
  Check(!a.IsValid() && !g.ApplyCreatedCard(roar,152406,100),"Duplicate creation accepted");
  Check(!g.CreationAllowed(roar,113305),"Roar creates unrelated weather");Check(!g.CreationAllowed(roar,999999),"Unknown definition accepted");
  var ale=Source(28,24,256);Check(g.CreationAllowed(ale,113302),"Ale second mode rejected");Check(g.CreationAllowed(ale,152406),"Ale first mode rejected");
  foreach(int zone in new[]{1,2,4})foreach(int weather in new[]{113305,113312})Check(g.CreationAllowed(Source(24,0,zone),weather),"Dagon weather rejected");
  Check(!g.CreationAllowed(Source(24,0,32),113305),"Dead Dagon creates weather");Check(!g.CreationAllowed(Source(28,25,32),152406),"Inactive special creates Bear");
  Check(!g.CreationAllowed(null,152406),"Null creator accepted");roar.s.isWaitingToDie=true;Check(!g.CreationAllowed(roar,152406),"Dying creator accepted");
  var monster=Source(34,0,1);Check(g.CreationAllowed(monster,152406),"Approved monster spawn rejected");g.approved=false;Check(!g.CreationAllowed(monster,152406),"Unapproved monster spawn accepted");g.approved=true;
  Check(!g.CreationAllowed(Source(34,0,32),152406),"Dead monster creates child");
  foreach(int side in new[]{1,2})foreach(bool spy in new[]{false,true}){
   var c=Source(34,0,16);c.s.positionPlayerId=side;c.spy=spy;int actual=spy?3-side:side;
   g.preferred=1;g.full.Clear();g.full.Add((actual,1));Check(g.BestNestedRow(c)==2,"Full preferred row used");
   g.preferred=0;Check(g.BestNestedRow(c)==2,"Invalid preferred row used");g.full.Add((actual,2));g.full.Add((actual,4));Check(g.BestNestedRow(c)==0,"Full board accepts nested unit");
  }
  g.pendingCard=Source(34,0,1);g.pendingRow=true;g.pendingIds.AddRange(new[]{1,2,4});
  foreach(int actor in new[]{1,2}){g.pendingCard.s.positionPlayerId=actor;g.mode=8;Check(g.ValidMonsterRow(actor,1),"Own-row spell rejected");Check(!g.ValidMonsterRow(3-actor,1),"Own-row spell accepts enemy");
   g.mode=9;Check(g.ValidMonsterRow(3-actor,4),"Enemy weather rejected");Check(!g.ValidMonsterRow(actor,4),"Enemy weather accepts ally");
   g.mode=1;Check(g.ValidMonsterRow(actor,2)&&g.ValidMonsterRow(3-actor,2),"Any-side movement/reset rejected");}
  Check(!g.ValidMonsterRow(1,8),"Unlisted row accepted");g.pendingRow=false;Check(!g.ValidMonsterRow(1,1),"Non-row request accepted");
  var ancestor=Source(34,0,32);g.playStack.Add(ancestor);Check(g.IsPlayAncestor(ancestor),"Dead active parent available for resurrection");Check(!g.IsPlayAncestor(Source(34,0,32)),"Unrelated grave card excluded");
  var parent=Source(34,0,1);Check(!g.ExistingChildAvailable(parent,ancestor),"Existing play accepts active ancestor");Check(!g.ExistingChildAvailable(parent,null),"Missing nested child accepted");
  foreach(int side in new[]{1,2})foreach(int zone in new[]{8,16,32,128}){parent.s.positionPlayerId=side;var c=Source(34,0,zone);c.s.positionPlayerId=side;Check(g.ExistingChildAvailable(parent,c),"Legal existing child rejected");}
  parent.s.positionPlayerId=2;foreach(int zone in new[]{1,2,4,256,512})Check(!g.ExistingChildAvailable(parent,Source(34,0,zone)),"Unavailable child accepted");
  var foreign=Source(34,0,32);foreign.s.positionPlayerId=1;Check(!g.ExistingChildAvailable(parent,foreign),"Foreign existing child accepted");foreign.s.positionPlayerId=2;foreign.s.isWaitingToDie=true;Check(!g.ExistingChildAvailable(parent,foreign),"Dying nested child accepted");
  g.FailAbility("first");g.FailAbility("cleanup");Check(g.fatal&&g.message=="first","Failure cause overwritten");
  var menu=new Menu();for(int i=0;i<10;i++)menu.Set(true);Check(menu.theGame.gui.balance==1&&menu.theGame.gui.calls==1,"Refresh accumulates cursor requests");
  menu.Set(false);menu.Set(false);Check(menu.theGame.gui.balance==0,"Close leaks cursor");menu.Set(true);menu.Set(false);menu.Set(true);menu.Set(false);Check(menu.theGame.gui.balance==0,"Device switch leaks cursor");
  Console.WriteLine("Passed "+cases+" creation, nested-row, side-mask, cycle and cursor cases.");
 }
}'''
for name,code in methods.items():program=program.replace('BODY_'+name,code)
(BUILD/'Program.cs').write_text(program,'utf8')
(BUILD/'checks.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net7.0</TargetFramework><CheckEolTargetFramework>false</CheckEolTargetFramework></PropertyGroup></Project>','utf8')
feed=BUILD/'empty-feed';feed.mkdir(exist_ok=True)
run=subprocess.run(['dotnet','run','--project',str(BUILD/'checks.csproj'),'--property:RestoreSources='+str(feed)],cwd=BUILD,capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
report=dict(passed=run.returncode==0,sources={str(DIR/n):hashlib.sha256((DIR/n).read_bytes()).hexdigest() for n in files},stdout=run.stdout,stderr=run.stderr,nativeRuntimeVerified=False)
(ROOT/'docs/evidence/turn-liveness97.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
print(run.stdout);print(run.stderr);raise SystemExit(run.returncode)
