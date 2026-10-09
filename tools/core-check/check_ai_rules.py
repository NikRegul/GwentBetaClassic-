"""Deck legality, preserved NPC lists, and actual pure WS decisions run with .NET.

This is not native battle acceptance. Pure functions are extracted, not copied.
"""
from collections import Counter
from pathlib import Path
import hashlib,json,re,subprocess

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/development/scripts/game/betagwent/duelArchetypeAI.ws'
raw=SOURCE.read_bytes();source=raw.decode('utf-8-sig')
read=lambda name:json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
rules=read('data/beta924/ai/rules.json')
presets=read('data/beta924/duel/presets.json')['presets']
full={c['templateId']:c for c in read('data/beta924/planning/full_catalog.json')['cards']}
active=[p for p in rules['profiles'] if p['active']]
assert len(active)==46 and len(presets)==99
assert rules['sourceSha256']==hashlib.sha256((ROOT/'deck_rules_researched_114.md').read_bytes()).hexdigest()
assert [p['id'] for p in presets]==list(range(1,100))
for p in presets:
    assert 25<=len(p['templateIds'])<=40
    assert full[p['leader']]['leader'] and full[p['leader']]['faction']==p['faction']
    counts=Counter(p['templateIds']);tiers=Counter(full[i]['tier'] for i in p['templateIds'])
    assert tiers[8]<=4 and tiers[4]<=6
    for ident,copies in counts.items():
        c=full[ident];assert c['faction'] in (1,p['faction']) and not c['leader']
        assert copies<=(3 if c['tier']==2 else 1)
for p in active:
    if p['family']=='singleton':assert len(set(p['templateIds']))==25
    if p['id']==32:assert len(p['templateIds'])==40
frozen=ROOT/'BetaGwent/build/stage114/powershell/20261009-083631-771-ai/snapshot/sources/BetaGwent/development/scripts/game/betagwent/duelCatalog.ws'
old=frozen.read_text(encoding='utf-8-sig')
meta=old[old.index('struct SBetaGwentDuelPreset'):old.index('function BetaGwentDuelPresetDeck(')]
for p in presets[:53]:
    match=re.search(r'function BetaGwentDuelPresetCards'+str(p['id'])+r'\(out ids : array<int>\)\s*\{(.*?)\n\}',old,re.S)
    assert match and [int(i) for i in re.findall(r'ids.PushBack\((\d+)\)',match[1])]==p['templateIds']
    record=re.search(r'case '+str(p['id'])+r':(.*?)break;',meta,re.S)
    assert record and int(re.search(r'leaderTemplateId = (\d+)',record[1])[1])==p['leader']
for pair in rules['combos']:assert pair['setup'] in full and pair['payoff'] in full
chase_source=(ROOT/'BetaGwent/development/scripts/game/betagwent/duelAIPass.ws').read_text(encoding='utf-8-sig')
methods=[]
for name in ('BetaGwentAIComboPriority','BetaGwentAIKeyReserve','BetaGwentAIImperaDeployGain','BetaGwentAIChasePassReason'):
    text=chase_source if name=='BetaGwentAIChasePassReason' else source
    match=re.search(r'function '+name+r'\((.*?)\)\s*:\s*(int|bool)\s*\{',text,re.S)
    pos=match.end();start=pos;depth=1
    while depth:depth+=(text[pos]=='{')-(text[pos]=='}');pos+=1
    body=text[start:pos-1]
    body=re.sub(r'\b(Max|Min)\(',r'Math.\1(',body)
    params=', '.join(t.strip()+' '+n.strip() for n,t in (p.split(':') for p in match[1].split(',')))
    methods.append('static '+match[2]+' '+name+'('+params+') {'+body+'}')
cases=[
    ('engine before three held spies','BetaGwentAIComboPriority(3,3,0,0,true,3)',8),
    ('payoff held until engine','BetaGwentAIComboPriority(3,0,0,1,false,3)',-3),
    ('payoff after engine is live','BetaGwentAIComboPriority(3,0,1,1,false,3)',0),
    ('no speculative gain after pass','BetaGwentAIComboPriority(3,3,0,0,true,0)',0),
    ('short round does not set up future chain','BetaGwentAIComboPriority(3,3,0,0,true,1)',0),
    ('no payoff no setup bonus','BetaGwentAIComboPriority(3,0,0,0,true,3)',0),
    ('save finisher in round one','BetaGwentAIKeyReserve(true,1,false)',6),
    ('release finisher to catch pass','BetaGwentAIKeyReserve(true,1,true)',0),
    ('release finisher in deciding round','BetaGwentAIKeyReserve(true,3,false)',0),
    ('ordinary bronze is not reserved','BetaGwentAIKeyReserve(false,1,false)',0),
    ('Impera catches deficit ten with five public spies','6+BetaGwentAIImperaDeployGain(5)',16),
    ('no public spies no actual boost','6+BetaGwentAIImperaDeployGain(0)',6),
]
build=ROOT/'BetaGwent/build/ai-rules88-check';build.mkdir(exist_ok=True)
checks=[f'if ({expression} != {expected}) throw new Exception({json.dumps(name)});' for name,expression,expected in cases]
# Execute the actual chase planner as well: one boosted Impera must beat a pair.
planner=chase_source[chase_source.index('class CBetaGwentAIChasePlanner'):].replace(' extends IScriptable','')
planner=re.sub(r'public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;', '', planner)
def signature(m):
    params=', '.join(t.strip().replace('array<','List<')+' '+n.strip() for n,t in (p.split(':') for p in m[3].split(',')))
    return m[1]+' '+m[4]+' '+m[2]+'('+params+')'
planner=re.sub(r'(private|public) function (\w+)\((.*?)\)\s*:\s*(\w+)',signature,planner,flags=re.S)
def declaration(m):
    kind=m[2].replace('array<','List<');initial='new '+kind+'()' if kind.startswith('List<') else 'default'
    return kind+' '+','.join(n.strip()+'='+initial for n in m[1].split(','))+';'
planner=re.sub(r'var ([\w,\s]+?) : ([\w<>]+);',declaration,planner)
planner=planner.replace('.Size()', '.Count').replace('.PushBack(','.Add(')
structs='\n'.join(re.sub(r'var (\w+) : (\w+);',r'public \2 \1;',m[0]) for m in re.finditer(r'struct SBetaGwentAIChase(?:Action|Plan)\s*\{.*?\}',chase_source,re.S))
checks+=['var actions=new List<SBetaGwentAIChaseAction>{new SBetaGwentAIChaseAction{id=17,gain=6+BetaGwentAIImperaDeployGain(5),cards=1},new SBetaGwentAIChaseAction{id=18,gain=6,cards=1},new SBetaGwentAIChaseAction{id=19,gain=6,cards=1}};',
    'var plan=new CBetaGwentAIChasePlanner().Plan(actions,11);if(!plan.reachable || plan.firstId!=17 || plan.cards!=1 || plan.gain!=16)throw new Exception("Boosted Impera must be a one-card catch");',
    'if(BetaGwentAIChasePassReason(plan.reachable,plan.cards,0,6,6,0,0)!=0)throw new Exception("Do not pass instead of boosted Impera");']
program='using System;using System.Collections.Generic;'+structs+planner+'class Program {'+'\n'.join(methods)+'static void Main(){'+'\n'.join(checks)+'Console.WriteLine("Passed '+str(len(cases))+' archetype-policy cases and boosted Impera chase.");}}'
(build/'Program.cs').write_text(program,encoding='utf-8')
(build/'policy.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net7.0</TargetFramework><CheckEolTargetFramework>false</CheckEolTargetFramework></PropertyGroup></Project>',encoding='utf-8')
offline=build/'empty-feed';offline.mkdir(exist_ok=True)
run=subprocess.run(['dotnet','run','--project',str(build/'policy.csproj'),'--property:RestoreSources='+str(offline)],cwd=build,capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
report=dict(stage=115,passed=run.returncode==0,sourceSha256=hashlib.sha256(raw).hexdigest(),legalPresets=99,activeProfiles=46,
    preservedOriginalDecksAndLeaders=53,sourceTextRetained=True,shupeSingletonVerified=True,foltest40Verified=True,
    cases=[dict(name=n,expected=e) for n,_,e in cases],imperaOneCardChaseVerified=run.returncode==0,
    chaseSourceSha256=hashlib.sha256(chase_source.encode('utf-8')).hexdigest(),stdout=run.stdout,stderr=run.stderr,nativeRuntimeVerified=False)
(ROOT/'docs/evidence/stage115-ai-policy.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(run.stdout);print(run.stderr)
raise SystemExit(run.returncode)
