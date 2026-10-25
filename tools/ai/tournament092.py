"""0.9.2 deck/AI tournament: freeze current rules, compare the changed weak decks with
0.9.2 on identical deals, audit known error classes (old vs new on the same deals), then play
the full 46-deck all-pairs tournament (same protocol as tournament-final 0.9.5: fixed seed,
unique deal blocks, both seats, simDamp 40). Every step resumes; nothing is installed.

  python -X utf8 tools/ai/tournament092.py [--out DIR] [--workers N] [--skip-weak] [--skip-audit] [--skip-tournament]
"""
from pathlib import Path
import argparse, datetime, hashlib, json, re, subprocess, sys

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'BetaGwent/build/release092-final1/rules'
LATEST=ROOT/'BetaGwent/build/tournament092-latest.json'
WEAK=[58,87,89,93,94,95]
# Opponents for the paired weak-deck check: strong and mid-table decks of every faction.
OPPONENTS=[86,68,71,56,61,67,84,90]

def run(args):
    print('RUN',subprocess.list2cmdline([str(x) for x in args]),flush=True)
    subprocess.run([str(x) for x in args],cwd=ROOT,check=True)

def write_once(path,data):
    text=json.dumps(data,ensure_ascii=False,indent=2)
    if path.exists():
        if path.read_text('utf8')!=text:raise SystemExit(f'{path} differs from this run; use a new --out')
    else:path.write_text(text,'utf8')

def deck_metadata(rules):
    manifest=json.loads((rules/'manifest.json').read_text('utf8'))
    s=(rules/'sources/BetaGwent/development/scripts/game/betagwent/duelCatalog.ws').read_text('utf-8-sig')
    titles={};factions={}
    for m in re.finditer(r'case (\d+):\s*\n\s*value\.header\.templateId = \1;(.*?)break;',s,re.S):
        t=re.search(r'value\.title = "([^"]*)"',m.group(2));f=re.search(r'factionMask = (\d+);',m.group(2))
        titles[int(m.group(1))]=t.group(1) if t else '';factions[int(m.group(1))]=int(f.group(1)) if f else 0
    cards={int(m.group(1)):[int(x) for x in re.findall(r'PushBack\((\d+)\)',m.group(2))] for m in re.finditer(r'function BetaGwentDuelPresetCards(\d+)\(out ids : array<int>\)\s*\{(.*?)\}',s,re.S)}
    meta={int(m.group(1)):(int(m.group(2)),m.group(3)) for m in re.finditer(r'case (\d+):\s*\n\s*value\.id = \1; value\.leaderTemplateId = (\d+);\s*\n\s*value\.title = "([^"]*)";',s)}
    decks=[]
    for p in manifest['presets']:
        leader,title=meta[p]
        decks.append(dict(presetId=p,title=title.replace('ИИ · ',''),requestedLeader=titles.get(leader,''),leader=leader,faction=factions.get(leader,0),templateIds=cards[p]))
    return dict(fingerprint=manifest['fingerprint'],decks=decks)

def main():
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--out',type=Path);p.add_argument('--workers',type=int,default=16)
    p.add_argument('--skip-weak',action='store_true');p.add_argument('--skip-audit',action='store_true');p.add_argument('--skip-tournament',action='store_true')
    a=p.parse_args()
    if a.out:out=a.out.resolve()
    elif LATEST.exists():out=Path(json.loads(LATEST.read_text('utf8'))['path'])
    else:out=ROOT/'BetaGwent/build'/('tournament092-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    out.mkdir(parents=True,exist_ok=True);LATEST.write_text(json.dumps(dict(path=str(out)),indent=2),'utf8')
    print('Output:',out,flush=True)
    rules=out/'rules'
    if not (rules/'manifest.json').exists():run([sys.executable,'-X','utf8','tools/ai/snapshot.py',rules])
    if not (out/'parity.json').exists():run(['node','tools/ai/tournament095.js','--parity',rules,out/'parity.json'])
    if not a.skip_weak:
        weak=out/'weak-compare';weak.mkdir(exist_ok=True)
        write_once(weak/'config.json',dict(baseline=str(OLD),versions=dict(old=str(OLD),new=str(rules)),out=str(weak/'results'),
            levels=[2,3,4],decks=WEAK,opponents=OPPONENTS,blocks={'2':8,'3':8,'4':16},seed=922102201,workers=a.workers,diagnostic=False))
        run(['node','tools/ai/weak_arena098.js',weak/'config.json'])
    if not a.skip_audit:
        audit=out/'error-audit';audit.mkdir(exist_ok=True)
        write_once(audit/'config.json',dict(versions=dict(old=str(OLD),new=str(rules)),out=str(audit/'results'),seed=922107701,
            workers=a.workers,simDamp=40,gamesByStrength={'2':150,'3':150,'4':300}))
        run(['node','tools/ai/audit_play092.js',audit/'config.json'])
    if not a.skip_tournament:
        t=out/'tournament';t.mkdir(exist_ok=True)
        write_once(t/'deck-metadata.json',deck_metadata(rules))
        write_once(t/'config.json',dict(snapshot=str(rules),out=str(t),workers=min(a.workers,18),seed=922105501,simDamp=40,blocksByStrength={'2':8,'3':8,'4':32}))
        run(['node','tools/ai/tournament095.js',t/'config.json'])
        run([sys.executable,'-X','utf8','tools/ai/report_tournament095.py',t])
    print('COMPLETE:',out,flush=True)

if __name__=='__main__':main()
