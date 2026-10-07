using System;
using System.Collections.Generic;
public class Policy {
 public string Name {get;set;}="baseline";
 public int[] Shared {get;set;}=new int[16];
 public Dictionary<int,int[]> Decks {get;set;}=new();
 public int Weight(int preset,int index) => Math.Clamp(Shared[index]+(Decks.TryGetValue(preset,out var row)?row[index]:0),-8,8);
}
public static partial class Globals {
 public static Policy ActivePolicy;
 public static int HostTrainingWeight(int preset,int index)=>ActivePolicy?.Weight(preset,index)??0;
}
