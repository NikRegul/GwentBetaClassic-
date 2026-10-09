"""Convert AI_REASON events from retail/REDkit logs or compressed match replays to Markdown."""
import argparse,gzip,json,re
from pathlib import Path

REASONS={
    'save_long_deciding_round':'Сохранить карты для длинного решающего раунда',
    'already_ahead_after_pass':'Противник спасовал, преимущество уже есть',
    'accept_tie':'Ничья завершает матч в нашу пользу',
    'force_multiple_replies':'Противнику потребуется несколько ответных карт',
    'researched_round_economy':'Сохранить ресурсы по условиям экономики раундов',
    'chase_resource_budget':'Догон недостижим или слишком дорог по картам',
    'last_card_unreachable':'Последняя карта не позволяет догнать',
    'no_legal_hand_or_useful_chase':'Нет допустимого хода или полезного догона',
    'no_duel_target_and_other_card_available':'Нет цели для дуэли; в руке есть другой ход',
    'no_legal_row':'Нет допустимого ряда',
    'best_evaluation_or_reachable_chase':'Лучший итог оценки либо ход плана догона',
    'useful_ability_and_best_evaluation':'Полезная способность лидера и лучшая оценка',
    'reachable_chase':'Лидер позволяет выполнить план догона',
    'no_hand_card':'В руке не осталось карт',
    'ability_value_resource_reserve_and_hand_alternatives':'Ценность способности, резерв лидера и альтернативы из руки',
    'archetype_opening_and_duplicates':'Стартовые связки архетипа и лишние копии',
}

def card_names():
    source=Path(__file__).resolve().parents[2]/'BetaGwent/development/scripts/game/betagwent/duelCatalog.ws'
    if not source.exists():return {}
    names={}
    for block in re.finditer(r'case\s+(\d+):(.+?)(?=\n\s*case\s+\d+:|\n\s*default:|\Z)',source.read_text('utf-8-sig'),re.S):
        title=re.search(r'value\.title\s*=\s*"((?:\\.|[^"\\])*)"',block[2])
        if title:names[block[1]]=title[1].replace('\\"','"')
    return names

def main():
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--language',choices=['ru','en'],default='ru');a=p.parse_args()
    names=card_names() if a.language=='ru' else {}
    if a.input.name.endswith('.json.gz'):
        data=json.loads(gzip.decompress(a.input.read_bytes()))
        lines=[x['version']+' '+x['text'] for x in data['logs']]
    else:lines=a.input.read_text('utf8',errors='replace').splitlines()
    decisions={};epochs={};last={}
    for line in lines:
        if 'AI_REASON ' not in line:continue
        text=line.split('AI_REASON ',1)[1];fields=dict(re.findall(r'(\w+)=([^\s]+)',text))
        decision=int(fields.get('decision','0'))
        version=line.split(' AI_REASON ',1)[0] if line.startswith(('candidate ','baseline ')) else 'game'
        if fields.get('event')=='BEGIN':
            if decision<=last.get(version,0):epochs[version]=epochs.get(version,0)+1
            last[version]=decision
        key=f'{version} / session {epochs.get(version,0)+1} / {decision}'
        decisions.setdefault(key,[]).append((fields.get('event',''),text))
    result=['# AI decisions','',f'Input: {a.input}','']
    for decision,events in decisions.items():
        result.extend([f'## Decision {decision}',''])
        for kind,text in events:
            template=re.search(r'\btemplate=(\d+)',text);reason=re.search(r'\breason=([^\s]+)',text)
            label=names.get(template[1]) if template else None
            explanation=REASONS.get(reason[1]) if reason and a.language=='ru' else None
            result.append(f'- **{kind}'+(f' — {label}' if label else '')+'**: '+text)
            if explanation:result.append(f'  {explanation}.')
        result.append('')
    output=a.output or a.input.with_suffix('.decisions.md');output.write_text('\n'.join(result),'utf8')
    print(f'{len(decisions)} decisions: {output}')
if __name__=='__main__':main()
