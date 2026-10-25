"""Index real game decisions for review; never label a loss or a heuristic flag a bug.

Usage: python -X utf8 tools/ai/audit_ai_log198.py <scriptslog.txt> <new-output-dir>
Preserves the input bytes and source line numbers. Logged card fields do not
contain every queued effect, RNG position or private per-card state.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil


def fields(text):
    return dict(re.findall(r'(\w+)=([^\s]+)', text))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log',type=Path);parser.add_argument('out',type=Path)
    args=parser.parse_args();raw=args.log.read_bytes();out=args.out.resolve()
    assert not out.exists(), 'Use a new evidence directory'
    out.mkdir(parents=True);shutil.copyfile(args.log,out/'scriptslog.txt')
    games=[];game=None;decision=None;errors=[]
    for line_no,line in enumerate(raw.decode('utf-8-sig',errors='replace').splitlines(),1):
        if '[BetaGwent] DUEL_STARTED ' in line:
            game=dict(index=len(games)+1,line=line_no,start=fields(line),decisions=[],result=None);games.append(game);decision=None
        if '[BetaGwent]' in line and any(s in line for s in ['DECK_SAVE_REJECT','DUEL_FATAL','PROFILE_RESTORE_REJECTED']):errors.append(dict(line=line_no,text=line))
        if game is None:continue
        if '[BetaGwent] AI_REASON ' in line and 'event=BEGIN ' in line:
            decision=dict(line=line_no,begin=fields(line),position=None,cards=[],events=[]);game['decisions'].append(decision)
        if '[BetaGwent] AI_POSITION ' in line and decision is not None:decision['position']=fields(line)
        if '[BetaGwent] AI_POSITION_CARDS ' in line and decision is not None:
            for token in line.split():
                if not re.fullmatch(r'-?\d+(?::-?\d+){12}',token):continue
                names=['id','template','owner','side','zone','index','power','base','armor','tokens','timer','tier','playable']
                decision['cards'].append(dict(zip(names,map(int,token.split(':')))))
        if '[BetaGwent] AI_REASON ' in line and decision is not None:decision['events'].append(dict(line=line_no,**fields(line)))
        if '[BetaGwent] NATIVE_GWENT_RESULT ' in line:game['result']=dict(line=line_no,**fields(line))
    targets=[];incomplete=[]
    for game in games:
        for decision in game['decisions']:
            position=decision['position']
            if not position or len(decision['cards'])!=int(position['cardCount']):incomplete.append(dict(game=game['index'],line=decision['line']))
            by_id={c['id']:c for c in decision['cards']}
            for event in decision['events']:
                if event.get('event')=='TARGET_SELECT':
                    targets.append(dict(game=game['index'],decision=decision['begin']['decision'],event=event,targetAtDecisionStart=by_id.get(int(event['target'])),
                        reviewPriority='regenerating-swordsman' if by_id.get(int(event['target']),{}).get('template')==200040 else 'ordinary'))
    summary=dict(complete=True,sourceSha256=hashlib.sha256(raw).hexdigest(),games=len(games),completedGames=sum(g['result'] is not None for g in games),
        decisions=sum(len(g['decisions']) for g in games),targetChoices=len(targets),incompleteLoggedPositions=incomplete,storageOrFatalLogEntries=errors,
        seeds=[g['start'].get('seed') for g in games],starters=[g['start'].get('starter') for g in games],
        results=[g['result'] for g in games],indexDoesNotConfirmBugs=True,
        scope='Evidence index only. Targets reflect the decision-start snapshot, not intervening effects. Losses and review priorities do not establish bugs. Full historical runtime replay is not claimed.')
    (out/'decisions.json').write_text(json.dumps(dict(games=games,targets=targets),ensure_ascii=False,indent=2)+'\n','utf8')
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':main()
