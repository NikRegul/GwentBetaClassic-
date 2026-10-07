using System;
using System.Collections.Generic;
using System.Linq;
// Copy-on-write reproduces WS array value semantics.
public struct WSArray<T> {
 private List<T> items;
 public WSArray() { items=new List<T>(); }
 private void Detach() { items=items==null?new List<T>():new List<T>(items); }
 public int Size()=>items?.Count??0;
 public T this[int i] { get=>items[i];set{Detach();items[i]=value;} }
 public void PushBack(T v){Detach();items.Add(v);}
 public void Clear(){items=new List<T>();}
 public void Erase(int i){Detach();items.RemoveAt(i);}
 public void Insert(int i,T v){Detach();items.Insert(i,v);}
 public bool Contains(T v)=>items?.Contains(v)??false;
 public int FindFirst(T v)=>items?.IndexOf(v)??-1;
 public void Resize(int n){Detach();while(items.Count<n)items.Add(Activator.CreateInstance<T>());if(items.Count>n)items.RemoveRange(n,items.Count-n);}
 public T PopBack(){T v=items[^1];Erase(Size()-1);return v;}
 public IEnumerable<T> Values()=>items??Enumerable.Empty<T>();
}
public class IScriptable {
 public static implicit operator bool(IScriptable v)=>v!=null;
 public static bool operator !(IScriptable v)=>v==null;
}
public static partial class Globals {
 public static Random HostRandom=new Random(1);
 public static int RandRange(int n)=>n>0?HostRandom.Next(n):0;
 public static int Max(int a,int b)=>Math.Max(a,b);
 public static int Min(int a,int b)=>Math.Min(a,b);
 public static int Abs(int a)=>Math.Abs(a);
 public static int FloorF(float a)=>(int)Math.Floor(a);
 public static float Max(float a,float b)=>Math.Max(a,b);
 public static float Min(float a,float b)=>Math.Min(a,b);
 public static int Clamp(int a,int lo,int hi)=>Math.Clamp(a,lo,hi);
 public static void LogChannel(string channel,string message){HostLog?.Invoke(message);}
 public static Action<string> HostLog;
 public static int BetaGwentAIChooseOrdinaryPreset()=>throw new InvalidOperationException("Self play must supply an explicit pool preset.");
}
public static partial class Globals {
 public static int SimDepth;
 public static void BetaGwentLog(string message){if(SimDepth==0)HostLog?.Invoke(message);}
 public static void BetaGwentAISimEnter(){SimDepth++;}
 public static void BetaGwentAISimLeave(){SimDepth=Math.Max(0,SimDepth-1);}
}
