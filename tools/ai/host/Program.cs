using System;
using System.IO;
using System.Text.Json;
using System.Collections.Generic;
public class Batch {
 public Policy Left {get;set;}=new();public Policy Right {get;set;}=new();
 public List<int[]> Matches {get;set;}=new();
}
class Program {
 static int Main(string[] args){
  if(args.Length!=1){Console.Error.WriteLine("Usage: selfplay.dll batch.json");return 2;}
  var batch=JsonSerializer.Deserialize<Batch>(File.ReadAllText(args[0]),new JsonSerializerOptions{PropertyNameCaseInsensitive=true});
  foreach(var m in batch.Matches){bool reverse=m.Length>3&&m[3]==1;var r=SelfPlay.Play(m[0],m[1],m[2],reverse?batch.Right:batch.Left,reverse?batch.Left:batch.Right);Console.WriteLine(JsonSerializer.Serialize(r with{CandidateSeat=reverse?2:1}));}
  return 0;
 }
}
