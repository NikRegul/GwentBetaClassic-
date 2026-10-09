"""Compile actual mod battle .ws rules as C#. No replacement card abilities.
Generated C# is disposable. Only logging and engine RNG are host boundaries.
"""
from pathlib import Path
import hashlib, json, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'BetaGwent/build/ai-selfplay'
CORE=ROOT/'BetaGwent/scripts/game/betagwent'
DEV=ROOT/'BetaGwent/development/scripts/game/betagwent'
FILES=list(CORE.glob('*.ws'))+[DEV/(n+'.ws') for n in (
 'duelAICatalog','duelAIResearch','duelAIPass','duelAITuning','duelArchetypeAI','duelCatalog',
 'duelEffectRuntime','duelEvents','duelLiveCard','duelMonsterDuel','duelMonsters',
 'duelNeutral','duelNilf','duelNilfDependencies','duelNorth','duelScoia','duelSession',
 'duelSkellige','duelSpecials','duelVisualFrame','duelWeather','duelWeatherAI',
 'developmentRequestFlow')]
if (DEV/'duelAITraining.ws').exists():FILES.append(DEV/'duelAITraining.ws')
def clean(s):
 return re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/',lambda m:'' if m[0].startswith(('//','/*')) else m[0],s,flags=re.S)
def blocks(s):
 start=0;depth=0
 for m in re.finditer(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[{}]',s):
  if m[0]=='{':depth+=1
  elif m[0]=='}':
   depth-=1
   if depth==0:yield s[start:m.end()].strip();start=m.end()
 if s[start:].strip():raise ValueError('Unparsed tail: '+s[start:start+100])
def kind(t):return t.strip().replace('array<','WSArray<').replace('name','string')
def init(t):
 if t=='string':return '""'
 if t in ('int','float','bool') or t.startswith('EBeta'):return 'default'
 if t.startswith(('SBeta','WSArray<')):return 'new '+t+'()'
 return 'null'
SIG=re.compile(r'(?:(public|private|protected)\s+)?(?:(abstract)\s+)?function\s+(\w+)\s*\((.*?)\)\s*(?::\s*([\w<>]+))?',re.S)
def params(raw):
 result=[]
 for p in raw.split(','):
  if not p.strip():continue
  m=re.fullmatch(r'\s*(?:(out|optional)\s+)?(\w+)\s*:\s*([\w<>]+)\s*',p)
  if not m:raise ValueError(p)
  mode,n,t=m.groups();result.append((mode,n,kind(t)))
 return result
def main():
 BUILD.mkdir(parents=True,exist_ok=True);pieces=[];sources={}
 for p in FILES:
  raw=p.read_bytes();sources[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_text(encoding='utf-8-sig').encode('utf-8')).hexdigest();s=clean(raw.decode('utf-8-sig'))
  if p.stem=='duelAITuning':s=s[:s.index('function BetaGwentAIChooseOrdinaryPreset')]
  pieces.extend(blocks(s))
 p=DEV/'deckBuilder.ws';s=clean(p.read_text(encoding='utf-8-sig'));pieces.extend(list(blocks(s))[:2]);sources[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_text(encoding='utf-8-sig').encode('utf-8')).hexdigest()
 for name in ('SBetaGwentDevelopmentCard','SBetaGwentDuelCueContext'):
  if any(re.search(r'struct\s+'+name+r'\b',s) for s in pieces):continue
  matches=[]
  for p in DEV.glob('*.ws'):
   for b in blocks(clean(p.read_text(encoding='utf-8-sig'))):
    if re.match(r'struct\s+'+name+r'\b',b):
     matches.append(b);sources[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_text(encoding='utf-8-sig').encode('utf-8')).hexdigest()
  if len(matches)!=1:raise ValueError(name)
  pieces+=matches
 enums=[re.match(r'enum\s+(\w+)',s)[1] for s in pieces if s.startswith('enum')]
 refs={};classes={};methods={}
 for s in pieces:
  cm=re.match(r'(?:abstract\s+)?class\s+(\w+)\s+extends\s+(\w+)',s)
  if cm:classes[cm[1]]=cm[2];methods[cm[1]]={m[3] for m in SIG.finditer(s)}
  for m in SIG.finditer(s):
   pp=params(m[4]);indices=tuple(i for i,p in enumerate(pp) if p[0]=='out');owner=cm[1] if cm else None
   if indices:
    minimum=len(pp)-sum(p[0]=='optional' for p in pp)
    for argc in range(minimum,len(pp)+1):refs[(owner,m[3],argc)]=indices
 def callrefs(s,cn):
  tokens=list(re.finditer(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\b\w+\s*\(|[(),]',s));edits=[]
  for index,m in enumerate(tokens):
   name=re.match(r'(\w+)\s*\(',m[0])
   if not name or not any(k[1]==name[1] for k in refs):continue
   if re.search(r'\bfunction\s*$',s[max(0,m.start()-20):m.start()]):continue
   depth=1;starts=[m.end()]
   for t in tokens[index+1:]:
    if t[0].endswith('('):depth+=1
    elif t[0]==')':
     depth-=1
     if not depth:break
    elif t[0]==',' and depth==1:starts.append(t.end())
   choices={v for k,v in refs.items() if k[1:]==(name[1],len(starts))}
   indices=refs.get((cn,name[1],len(starts)),refs.get((None,name[1],len(starts)),next(iter(choices)) if len(choices)==1 else ()))
   for i in indices:
    if i>=len(starts):raise ValueError('Bad out call '+name[1])
    pos=starts[i]
    while s[pos].isspace():pos+=1
    if not s[pos:].startswith('ref '):edits.append((pos,'ref '))
  for pos,val in sorted(set(edits),reverse=True):s=s[:pos]+val+s[pos:]
  return s
 globals=[];output=[]
 for s in pieces:
  isglobal=s.startswith('function');isstruct=s.startswith('struct');isenum=s.startswith('enum')
  cm=re.match(r'(?:abstract\s+)?class\s+(\w+)',s);cn=cm[1] if cm else None;s=callrefs(s,cn)
  strings=[]
  def hold(m):
   strings.append(json.dumps(m[0][1:-1]) if m[0].startswith("'") else m[0]);return '__WS_LITERAL_'+str(len(strings)-1)+'__'
  s=re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',hold,s)
  defaults=dict(re.findall(r'\bdefault\s+(\w+)\s*=\s*([^;]+);',s));s=re.sub(r'\bdefault\s+\w+\s*=\s*[^;]+;','',s)
  def sig(m):
   ps=[('ref ' if mode=='out' else '')+t+' '+n+(' = '+init(t) if mode=='optional' else '') for mode,n,t in params(m[4])]
   mod='public static' if isglobal else 'public virtual'
   if m[2]:mod='public abstract'
   elif cn:
    base=classes.get(cn)
    while base and base!='IScriptable':
     if m[3] in methods.get(base,set()):mod='public override';break
     base=classes.get(base)
   return mod+' '+kind(m[5] or 'void')+' '+m[3]+'('+', '.join(ps)+')'
  s=SIG.sub(sig,s);s=re.sub(r'\bnew (\w+) in (?:this|\w+)',r'new \1()',s);s=re.sub(r'\bNULL\b','null',s)
  if isglobal and 'BetaGwentAITrainingWeight(' in s:
   s=re.sub(r'(public static int BetaGwentAITrainingWeight\([^)]*\))\s*\{.*\}',r'\1 { return HostTrainingWeight(preset,index); }',s,flags=re.S)
  s=re.sub(r'\bclass (\w+) extends (\w+)',r'partial class \1 : \2',s)
  if cm:s=re.sub(r'^(abstract )?partial class',r'public \1partial class',s)
  if isenum or isstruct:s='public '+s
  def decl(m):
   t=kind(m[2]);return ('public ' if isstruct else '')+t+' '+', '.join(n.strip()+' = '+init(t) for n in m[1].split(','))+';'
  s=re.sub(r'\b(public|private|protected)\s+var\s+','public var ',s);s=re.sub(r'\bvar\s+([\w,\s]+?)\s*:\s*([\w<>]+)\s*;',decl,s)
  for n,value in defaults.items():s=re.sub(r'\b'+n+r'\s*=\s*default',n+' = '+value,s)
  if isstruct:
   s=re.sub(r'(?m)^(\s*)(?!public)([\w<>]+\s+\w+\s*=)',r'\1public \2',s);name=re.match(r'public struct\s+(\w+)',s)[1];s=s[:-1]+'public '+name+'() {}\n}'
  s=s.replace('array<','WSArray<');s=re.sub(r'\b(0x[89a-fA-F][0-9a-fA-F]{7})\b',r'unchecked((int)\1)',s)
  s=s.replace('(CBetaGwentDuelCard)GetCard(id)','(GetCard(id) as CBetaGwentDuelCard)').replace('(CBetaGwentManagedAction)action','(action as CBetaGwentManagedAction)')
  s=re.sub(r'\((CBeta\w+)\)(\w+)\b',r'(\2 as \1)',s)
  s=re.sub(r'\b(base|event|lock|params)\b',r'@\1',s)
  s=re.sub(r'__WS_LITERAL_(\d+)__',lambda m:strings[int(m[1])],s)
  (globals if isglobal else output).append(s)
 header='using System; using System.Collections.Generic; using static Globals;\n'+''.join('using static '+e+';\n' for e in enums)
 (BUILD/'Rules.cs').write_text(header+'\n'.join(output)+'\npublic static partial class Globals {\n'+'\n'.join(globals)+'\n}',encoding='utf-8')
 for p in (ROOT/'tools/ai/host').glob('*.cs'):(BUILD/p.name).write_bytes(p.read_bytes())
 (BUILD/'selfplay.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net7.0</TargetFramework><CheckEolTargetFramework>false</CheckEolTargetFramework><NoWarn>CS0219</NoWarn></PropertyGroup></Project>',encoding='utf-8')
 (BUILD/'sources.json').write_text(json.dumps(sources,indent=2)+'\n',encoding='utf-8');empty=BUILD/'empty-feed';empty.mkdir(exist_ok=True)
 run=subprocess.run(['dotnet','build',str(BUILD/'selfplay.csproj'),'--nologo','-v:q','--property:RestoreSources='+str(empty)],capture_output=True,text=True,encoding='utf-8',errors='replace')
 (BUILD/'compile.log').write_text(run.stdout+run.stderr,encoding='utf-8');print('\n'.join((run.stdout+run.stderr).splitlines()[:65]));return run.returncode
if __name__=='__main__':sys.exit(main())
