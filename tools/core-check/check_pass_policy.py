"""Execute actual pure WitcherScript policy bodies as C# with integer semantics.

This checks round economy decisions, not native combat or target resolution.
Uses only locally installed .NET reference packs; no network package sources.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/development/scripts/game/betagwent/duelAIPass.ws'
BUILD=ROOT/'BetaGwent/build/pass-policy85'
BUILD.mkdir(parents=True,exist_ok=True)
raw=SOURCE.read_bytes();source=raw.decode('utf-8-sig')
methods=[]
for name in ('BetaGwentAIChasePassReason','BetaGwentAIEarlyPass','BetaGwentAIConcedeOptionalRound'):
    match=re.search(r'function '+name+r'\((.*?)\)\s*:\s*(int|bool)\s*\{',source,re.S)
    pos=match.end();start=pos;depth=1
    while depth:
        depth+=(source[pos]=='{')-(source[pos]=='}');pos+=1
    body=source[start:pos-1]
    body=re.sub(r'var (\w+) : (int|bool);',r'\2 \1;',body)
    body=re.sub(r'\bMax\(', 'Math.Max(',body)
    params=', '.join(t.strip()+' '+n.strip() for n,t in (p.split(':') for p in match[1].split(',')))
    methods.append('static '+match[2]+' '+name+'('+params+') {'+body+'}')
cases=[
    ('optional two-card chase', 'BetaGwentAIChasePassReason(true,2,0,7,7,0,0)',2),
    ('cheap one-card answer', 'BetaGwentAIChasePassReason(true,1,0,6,6,0,0)',0),
    ('large retained advantage', 'BetaGwentAIChasePassReason(true,2,0,9,5,0,0)',0),
    ('avoid empty final hand', 'BetaGwentAIChasePassReason(true,2,0,3,0,0,0)',2),
    ('cumulative chase budget', 'BetaGwentAIChasePassReason(true,1,1,6,6,0,0)',2),
    ('defend match point', 'BetaGwentAIChasePassReason(true,3,0,5,6,0,1)',0),
    ('preserve deciding hand at 1:0', 'BetaGwentAIChasePassReason(true,3,0,5,6,1,0)',2),
    ('cheap match-winning reply', 'BetaGwentAIChasePassReason(true,1,0,5,5,1,0)',0),
    ('match-winning pair retains advantage', 'BetaGwentAIChasePassReason(true,2,0,7,4,1,0)',0),
    ('do not empty hand against three cards', 'BetaGwentAIChasePassReason(true,1,0,2,3,0,0)',3),
    ('leader after earlier chase remains free', 'BetaGwentAIChasePassReason(true,0,2,4,6,1,0)',0),
    ('concede optional low-hand bleed', 'BetaGwentAIConcedeOptionalRound(15,10,3,4,1,0)',True),
    ('defend decisive round under pressure', 'BetaGwentAIConcedeOptionalRound(30,10,3,4,0,1)',False),
    ('keep a realistic catch-up', 'BetaGwentAIConcedeOptionalRound(12,15,4,4,0,0)',False),
    ('unreachable round', 'BetaGwentAIChasePassReason(false,3,0,5,6,0,0)',1),
    ('leader without hand loss', 'BetaGwentAIChasePassReason(true,0,0,6,6,0,0)',0),
    ('force two replies', 'BetaGwentAIEarlyPass(28,25,0,5,6,0)',True),
    ('public leader can close gap', 'BetaGwentAIEarlyPass(28,25,25,5,6,0)',False),
    ('do not risk match on early pass', 'BetaGwentAIEarlyPass(60,25,0,6,5,1)',False),
    ('avoid optimistic division', 'BetaGwentAIEarlyPass(24,25,0,5,6,0)',False),
]
checks=[]
for name,expression,expected in cases:
    value=str(expected).lower()
    checks.append(f'if ({expression} != {value}) throw new Exception({json.dumps(name)});')
program='using System; class Program {'+'\n'.join(methods)+'static void Main(){'+'\n'.join(checks)+'Console.WriteLine("Passed '+str(len(cases))+' pass-policy cases.");}}'
(BUILD/'Program.cs').write_text(program,encoding='utf8')
(BUILD/'policy.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net7.0</TargetFramework><CheckEolTargetFramework>false</CheckEolTargetFramework></PropertyGroup></Project>',encoding='utf8')
offline=BUILD/'empty-feed';offline.mkdir(exist_ok=True)
run=subprocess.run(['dotnet','run','--project',str(BUILD/'policy.csproj'),'--property:RestoreSources='+str(offline)],cwd=BUILD,capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
report=dict(source=str(SOURCE),sha256=hashlib.sha256(raw).hexdigest(),cases=[dict(name=n,expected=e) for n,_,e in cases],passed=run.returncode==0,stdout=run.stdout,stderr=run.stderr,nativeRuntimeVerified=False)
(ROOT/'docs/evidence/pass-policy85.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(run.stdout);print(run.stderr)
raise SystemExit(run.returncode)
