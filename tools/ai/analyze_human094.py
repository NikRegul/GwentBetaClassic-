"""Extract observed human actions and public score transitions, without inventing hidden cards."""
from pathlib import Path
import argparse, hashlib, json, re

ROOT=Path(__file__).resolve().parents[2]

def analyze(source):
    names={}
    catalog=(ROOT/'BetaGwent/development/scripts/game/betagwent/duelCatalog.ws').read_text('utf-8-sig')
    for block in re.finditer(r'case\s+(\d+):(.+?)(?=\n\s*case\s+\d+:|\n\s*default:|\Z)',catalog,re.S):
        title=re.search(r'value\.title\s*=\s*"((?:\\.|[^"\\])*)"',block[2])
        if title:names[block[1]]=title[1].replace('\\"','"')
    games=[];game=None;view=None;begin=None
    raw=source.read_bytes()
    for number,line in enumerate(raw.decode('utf-8-sig',errors='replace').splitlines(),1):
        if '[BetaGwent] ' not in line:continue
        text=line.split('[BetaGwent] ',1)[1];fields=dict(re.findall(r'(\w+)=([^\s]+)',text))
        if text.startswith('DUEL_STARTED '):
            game=dict(number=len(games)+1,line=number,start=fields,plays=[],intents=[],passes=[],ai=[],rounds={})
            games.append(game);view=None;begin=None
        if not game:continue
        if text.startswith('BOARD_VIEW '):
            view=dict(line=number,**fields);game['lastView']=view
            if int(fields['flags'])&(4|48) and (fields['score']!='0:0' or fields['round'] not in game['rounds']):game['rounds'][fields['round']]=view
        if text.startswith('BOARD_INTENT '):
            intent=dict(line=number,**fields);game['intents'].append(intent)
            if fields['action']=='pass':game['passes'].append(dict(who='human',view=view,**intent))
        if text.startswith('DUEL_PLAY '):game['plays'].append(dict(line=number,title=names.get(fields['template'],fields['template']),**fields))
        if text.startswith('AI_REASON '):
            if fields.get('event')=='BEGIN':begin=dict(line=number,**fields)
            if fields.get('event')=='PASS':game['passes'].append(dict(who='ai',begin=begin,line=number,**fields))
            if fields.get('event') in ['BEGIN','SELECT','PASS']:game['ai'].append(dict(line=number,**fields))
    for game in games:game['winner']=(int(game.get('lastView',{}).get('flags',0))>>4)&3
    return dict(source=str(source),sha256=hashlib.sha256(raw).hexdigest(),games=games,completed=sum(bool(g['winner']) for g in games),humanWins=sum(g['winner']==1 for g in games),limitation='Observed retail actions and displayed scores. Not a bit-for-bit replay or a reconstruction of unlogged hidden cards.')

def main():
    p=argparse.ArgumentParser();p.add_argument('log',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    report=analyze(a.log);(a.out/'human-games.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
    lines=['# Разбор партий пользователя','',f"Начато: {len(report['games'])}; завершено: {report['completed']}; побед пользователя: {report['humanWins']}.",'',
           'Это фактические действия и показанный счёт из лога. Закрытые карты, не попавшие в лог, не восстанавливаются; полное точное воспроизведение партий не заявляется.','']
    for g in report['games']:
        lines += [f"## Партия {g['number']}: {g['start']['ownPreset']} против {g['start']['enemyPreset']}",'',
                  'Результат: '+({0:'не завершена',1:'победа пользователя',2:'победа ИИ',3:'ничья'}[g['winner']])+'.',
                  'Итоги раундов по последним ненулевым кадрам: '+', '.join(k+': '+v['score'] for k,v in g['rounds'].items())+'.','',
                  'Розыгрыши пользователя: '+', '.join(p['title'] for p in g['plays'] if p['player']=='1')+'.','']
        for event in g['passes']:
            if event['who']=='human':lines.append(f"- Пас пользователя, строка {event['line']}: показанный счёт {(event.get('view') or {}).get('score','не записан')}.")
            else:lines.append(f"- Пас ИИ, строка {event['line']}: {event.get('reason','')}; очки ИИ/пользователь {event.get('ownScore','?')}:{event.get('enemyScore','?')}, карты {event.get('ownHand','?')}:{event.get('enemyHand','?')}.")
        lines.append('')
    (a.out/'HUMAN_GAMES_RU.md').write_text('\n'.join(lines),'utf8')
    print(json.dumps({k:report[k] for k in ['completed','humanWins','sha256']}))

if __name__=='__main__':main()
