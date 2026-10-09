"""Readable rosters and preserved author strategies from the generated AI data."""
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    rules=json.loads((ROOT/'data/beta924/ai/rules.json').read_text('utf-8-sig'))
    full={c['templateId']:c for c in json.loads((ROOT/'data/beta924/planning/full_catalog.json').read_text('utf-8'))['cards']}
    catalog=json.loads((ROOT/'data/beta924/normalized/catalog.json').read_text('utf-8'))
    name=lambda ident:catalog['localization']['ru_ru'][str(ident)+'_name']
    lines=['# 46 колод ИИ — исследованный состав Beta 0.9.24', '',
           'Составы ниже взяты из игровых данных. Текст стратегии сохранён из авторского документа; '
           'он объясняет намерения и не является исполняемым языком команд. Условия реализуются в '
           '`duelArchetypeAI.ws`, `duelAIPass.ws`, таблицах `strategy115.json` и общем поиске ходов.', '',
           'Лимиты: 25–40 карт, до четырёх золотых и шести серебряных; бронза до трёх копий. '
           'Квестовые колоды и стартовые наборы игрока этим импортом не заменяются.', '',
           '| Профиль | Пресет | Колода | Лидер | Карт | Политика |', '|---|---|---|---|---|---|']
    active=[p for p in rules['profiles'] if p['active']]
    for p in active:
        lines.append(f'| {p["id"]} | {p["presetId"]} | {p["title"]} | {name(p["leader"])} | {len(p["templateIds"])} | {p["passPolicy"]} |')
    for p in active:
        lines += ['',f'## {p["id"]}. {p["title"]}', '',
                  f'Пресет: **{p["presetId"]}**. Лидер: **{name(p["leader"])}** (`{p["leader"]}`). '
                  f'Политика: **{p["passPolicy"]}**. Семейство: `{p["family"]}`.', '']
        counts=Counter(p['templateIds'])
        for tier,label in ((8,'Золотые'),(4,'Серебряные'),(2,'Бронзовые')):
            lines += [f'### {label}', '']
            lines += [f'- {name(ident)} ×{count} (`{ident}`)' for ident,count in counts.items() if full[ident]['tier']==tier]
            lines.append('')
        for title,text in p['strategy'].items():
            lines += [f'### {title}', '', text, '']
    target=ROOT/'docs/AI_DECKS115_RU.md'
    target.write_text('\n'.join(lines)+'\n','utf-8')
    print('Exported',len(active),'exact rosters and preserved strategies:',target)
if __name__=='__main__':main()
