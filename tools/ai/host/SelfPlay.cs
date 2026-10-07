using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using static Globals;

// Only the headless adapter swaps seats. The exported game script never does.
// IDs, categories, side-relative target modes and RNG are deliberately untouched.
static class Perspective {
 static readonly HashSet<string> Seats=new(){"ownerPlayerId","positionPlayerId","playerId","targetPlayerId","startingPlayerId","currentPlayerId","roundStarter","visualSide","side"};
 static readonly string[] Pairs={"player","score","crownDelta","preset","leaderTemplate","nilfInitial","nilfSpell","grave","deck","leader"};
 static int Flip(int n)=>n==1?2:n==2?1:n;
 public static void Swap(CBetaGwentDuelSession game) { Visit(game,new HashSet<object>(ReferenceEqualityComparer.Instance)); }
 static object Visit(object value,HashSet<object> seen) {
  if(value==null)return null;Type t=value.GetType();
  if(t.IsPrimitive||t.IsEnum||t==typeof(string)||t==typeof(SBetaGwentDuelDefinition)||t==typeof(SBetaGwentTemplateHeader))return value;
  if(t.IsGenericType&&t.GetGenericTypeDefinition()==typeof(WSArray<>)) {
   var size=t.GetMethod("Size");var item=t.GetProperty("Item");int n=(int)size.Invoke(value,null);
   for(int i=0;i<n;i++)item.SetValue(value,Visit(item.GetValue(value,new object[]{i}),seen),new object[]{i});
   return value;
  }
  if(!t.IsValueType&&!seen.Add(value))return value;
  // Historical observations belong to a bot, not to the seat labels.
  var fields=t.GetFields(BindingFlags.Public|BindingFlags.Instance);
  foreach(string prefix in Pairs) {
   var a=t.GetField(prefix+"One");var b=t.GetField(prefix+"Two");
   if(a!=null&&b!=null){object old=a.GetValue(value);a.SetValue(value,b.GetValue(value));b.SetValue(value,old);}
  }
  foreach(var f in fields) {
   object old=f.GetValue(value);
   if(f.FieldType==typeof(int)&&Seats.Contains(f.Name))f.SetValue(value,Flip((int)old));
   else if(f.Name=="winnerMask"||f.Name=="matchWinnerMask") { int n=(int)old;f.SetValue(value,((n&1)<<1)|((n&2)>>1)); }
   else f.SetValue(value,Visit(old,seen));
  }
  if(value is CBetaGwentDuelWeather w) {
   for(int i=0;i<3;i++){int a=w.hazards[i];w.hazards[i]=w.hazards[i+3];w.hazards[i+3]=a;}
   for(int i=0;i<w.dreamRows.Size();i++)w.dreamRows[i]=(w.dreamRows[i]+3)%6;
  }
  return value;
 }
}
public record MatchResult(int Left,int Right,int Seed,int Winner,int Decisions,string Error,string[] Trace,int CandidateSeat=1);
public partial class CBetaGwentDuelSession {
 public bool TrainingReversed;
 private int[][] memories={new int[5],new int[5]};
 public void TrainingSwap() {
  int actor=TrainingReversed?0:1;
  memories[actor]=new[]{aiChaseRound,aiChaseInitialHand,aiObservedRound,aiObservedEnemyScore,aiPublicTempo};
  Perspective.Swap(this);TrainingReversed=!TrainingReversed;actor=TrainingReversed?0:1;
  var saved=memories[actor];aiChaseRound=saved[0];aiChaseInitialHand=saved[1];aiObservedRound=saved[2];aiObservedEnemyScore=saved[3];aiPublicTempo=Math.Max(14,saved[4]);
  weatherAI.Initialize(this);weatherProfile=weatherAI.Matches(nilfInitialTwo);
  archetypeAI.Initialize(this,nilfInitialTwo,presetTwo,leaderTemplateTwo);
 }
 public void TrainingMulligan() {
  // BeginMulligan already processed side 2. Process the other bot with exactly
  // the same mulligan policy, then restore the pending human-seat request.
  TrainingSwap();AiMulligan(mulliganBudget);TrainingSwap();RefreshMulligan();FinishMulligan(requestId);
 }
 public bool TrainingPending() {
  if(!IsPending())return true;
  if(mulligan){TrainingMulligan();return !fatal;}
  if(NilfDecisionSide()==1)TrainingSwap();
  if(pendingLeader){var c=pendingLeader;pendingLeader=null;return PlaceLeader(c,2,BestCardRow(2,c.Definition()),-3);}
  if(pendingRally){int r=BestNestedRow(pendingRally);if(r==0)return false;PlaceRally(2,r,-3);return !fatal;}
  if(!pendingCard)return false;
  var d=pendingCard.Definition();
  if(pendingCard.IsMonsterAbility()) {
   int k=pendingChoice?1:pendingPileChoice?2:pendingRow?3:0;
   MonsterRequest(pendingCard,pendingIds,k,monsterMinimum,monsterMaximum);return !fatal;
  }
  if(pendingChoice) {
   if(IsModeChoice())ResolveModeChoice(BestModeChoice(d,2));
   else if(IsDagonChoice())ResolveDagonChoice(ChooseDagonWeather(2));
   else if(IsFirstLightChoice())ResolveFirstLight(ChooseFirstLight(2));
   else return false;
  } else if(pendingPileChoice) {
   int best=0,score=int.MinValue;
   for(int i=0;i<pendingIds.Size();i++){var c=FindCard(pendingIds[i]);if(!c)continue;int v=AiAbilityChoiceValue(pendingCard,c,2);if(v>score){best=pendingIds[i];score=v;}}
   if(best==0)return false;SelectPileCard(best);
  } else if(pendingRow) {
   if(d.effect==28){int s=0,r=0;specials.BestRow(d,2,ref s,ref r);ApplyRowTarget(s,r);}
   else if(d.weatherToken!=0)ApplyRowTarget(1,BestWeatherRow(2,d.weatherToken));
   else ApplyRowTarget(1,BestEnemyRow(2));
  } else ApplyCardTarget(BestTarget(2,d.effect,d.amount));
  return !fatal;
 }
}
static class SelfPlay {
 public static MatchResult Play(int left,int right,int seed,Policy a,Policy b) {
  var trace=new Queue<string>();
  HostRandom=new Random(seed);HostLog=s=>{trace.Enqueue(s);while(trace.Count>80)trace.Dequeue();};
  var game=new CBetaGwentDuelSession();int steps=0;
  try {
   if(!game.InitializeWithPresets(left,right))throw new Exception("Invalid preset");game.recordVisuals=false;
   for(;steps<500;steps++) {
    if(game.IsFatal())throw new Exception(game.GetMessage());
    var m=game.Snapshot();
    if(m.matchWinnerMask!=0) {
     int w=m.matchWinnerMask;if(game.TrainingReversed)w=((w&1)<<1)|((w&2)>>1);
     return new(left,right,seed,w,steps,null,Array.Empty<string>());
    }
    ActivePolicy=game.TrainingReversed?a:b;
    if(game.IsMulligan()){game.TrainingMulligan();continue;}
    if(game.IsPending()){if(!game.TrainingPending())throw new Exception("Unresolved choice: "+game.GetMessage());continue;}
    if(game.IsWaitingRound()){if(!game.BeginNextRound())throw new Exception("Round transition failed");game.recordVisuals=false;continue;}
    if(m.currentPlayerId==1)game.TrainingSwap();
    ActivePolicy=game.TrainingReversed?a:b;
    if(!game.OpponentStep())throw new Exception("Decision rejected: "+game.GetMessage());
   }
   throw new Exception("Decision limit exceeded");
  } catch(Exception e){return new(left,right,seed,0,steps,e.ToString(),trace.ToArray());}
  finally{HostLog=null;ActivePolicy=null;}
 }
}
