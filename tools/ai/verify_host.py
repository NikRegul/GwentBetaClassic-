"""Verify critical WS value/seat semantics independently of the training binary."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'BetaGwent/build/ai-host-check';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=r'''
using System;using System.Linq;using System.Reflection;using System.Text.Json;
using System.Text.Json.Serialization;using static Globals;
class Check {
 static void Require(bool ok,string message){if(!ok)throw new Exception(message);}
 static void RefChange(ref WSArray<int> a){a.PushBack(8);}
 static string Stamp(CBetaGwentDuelSession g)=>JsonSerializer.Serialize(new{State=g.Snapshot(),Cards=g.live.Values().Select(c=>c.Snapshot()).ToArray(),Hazards=g.weather.hazards.Values().ToArray(),g.presetOne,g.presetTwo},new JsonSerializerOptions{IncludeFields=true,ReferenceHandler=ReferenceHandler.IgnoreCycles});
 static int Main(){
  var a=new WSArray<int>();a.PushBack(3);a.PushBack(5);var b=a;b[0]=9;b.Erase(1);b.PushBack(7);RefChange(ref b);
  Require(a.Size()==2&&a[0]==3&&a[1]==5&&b.Size()==3&&b[0]==9&&b[2]==8,"Array copy/ref semantics");
  var assembly=typeof(CBetaGwentDuelSession).Assembly;var swap=assembly.GetType("Perspective").GetMethod("Swap",BindingFlags.Public|BindingFlags.Static);
  var self=assembly.GetType("SelfPlay").GetMethod("Play",BindingFlags.Public|BindingFlags.Static);
  int[] left={54,61,72,88},right={55,70,81,93};int decisions=0;
  for(int i=0;i<left.Length;i++){
   HostRandom=new Random(924+i);var game=new CBetaGwentDuelSession();Require(game.InitializeWithPresets(left[i],right[i]),"Initialize");
   game.TrainingMulligan();if(game.Snapshot().currentPlayerId==1)game.TrainingSwap();Require(game.OpponentStep(),"Play opening");
   string before=Stamp(game);swap.Invoke(null,new object[]{game});swap.Invoke(null,new object[]{game});Require(before==Stamp(game),"Double swap changed IDs, cards, counters or weather");
   var first=(MatchResult)self.Invoke(null,new object[]{left[i],right[i],100924+i,new Policy(),new Policy()});
   var second=(MatchResult)self.Invoke(null,new object[]{left[i],right[i],100924+i,new Policy(),new Policy()});
   Require(first.Error==null&&second.Error==null&&first.Winner==second.Winner&&first.Decisions==second.Decisions,"Replay is not deterministic");decisions+=first.Decisions;
  }
  var policy=new Policy();policy.Shared=Enumerable.Repeat(8,16).ToArray();ActivePolicy=policy;
  var d=new SBetaGwentDuelDefinition();d.header.tierMask=8;
  Require(BetaGwentAITrainingBias(54,d,1,10,-30,true,40,60,8,8)==0,"Learned bias entered the post-pass planner");
  Require(Math.Abs(BetaGwentAITrainingBias(54,d,1,10,-30,false,40,60,8,8))<=120,"Bias bound");
  ActivePolicy=null;Console.WriteLine(JsonSerializer.Serialize(new{arrayValueSemantics=true,doubleSeatSwap=true,deterministicReplay=true,postPassBiasZero=true,boundedBias=true,matchPairs=left.Length,decisions}));return 0;
 }
}'''
def main():
 (OUT/'Check.cs').write_text(SOURCE,'utf8')
 assembly=(ROOT/'BetaGwent/build/ai-selfplay/bin/Debug/net7.0/selfplay.dll').as_posix()
 (OUT/'check.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net7.0</TargetFramework><CheckEolTargetFramework>false</CheckEolTargetFramework></PropertyGroup><ItemGroup><Reference Include="selfplay"><HintPath>'+assembly+'</HintPath></Reference></ItemGroup></Project>','utf8')
 empty=OUT/'empty-feed';empty.mkdir(exist_ok=True)
 build=subprocess.run(['dotnet','build',str(OUT/'check.csproj'),'--nologo','-v:q','--property:RestoreSources='+str(empty)],capture_output=True,text=True,encoding='utf8',errors='replace')
 (OUT/'compile.log').write_text(build.stdout+build.stderr,'utf8')
 if build.returncode:raise RuntimeError(build.stdout+build.stderr)
 run=subprocess.run(['dotnet',str(OUT/'bin/Debug/net7.0/check.dll')],capture_output=True,text=True,encoding='utf8',errors='replace')
 if run.returncode:raise RuntimeError(run.stdout+run.stderr)
 result=json.loads(run.stdout);(ROOT/'docs/evidence/ai-host100-check.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result))
if __name__=='__main__':main()
