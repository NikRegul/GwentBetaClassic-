"""Explicit, guarded revisions of the researched AI decks; never touch player presets."""
from collections import Counter
import json


def apply_patch(root, profiles, presets, full, families):
    path = root / 'data/beta924/ai/deck_patch128.json'
    patch = json.loads(path.read_text(encoding='utf-8'))
    assert patch['schema'] == 1
    by_preset = {p['id']: p for p in presets}
    originals = {i: json.dumps(p, sort_keys=True) for i, p in by_preset.items() if i <= 53 or i == 80}
    variety_path = root / 'data/beta924/ai/deck_variety128.json'
    variety = json.loads(variety_path.read_text(encoding='utf-8'))
    assert variety['schema'] == 1
    # 0.9.1b author-directed rosters are applied last, over the variety pass.
    extra_path = root / 'data/beta924/ai/deck_patch091b.json'
    extra = json.loads(extra_path.read_text(encoding='utf-8')) if extra_path.exists() else dict(schema=1, decks=[])
    assert extra['schema'] == 1
    current_path = root / 'data/beta924/ai/deck_patch092.json'
    current = json.loads(current_path.read_text(encoding='utf-8')) if current_path.exists() else dict(schema=1, decks=[], titles={})
    assert current['schema'] == 1
    for change in patch['decks'] + variety['decks'] + extra['decks'] + current['decks']:
        if not change.get('enabled', True):
            continue
        ident = change['presetId']
        assert 54 <= ident <= 99 and ident != 80
        preset = by_preset[ident]
        profile = next(p for p in profiles if p.get('presetId') == ident)
        assert Counter(preset['templateIds']) == Counter(change['expectedTemplateIds']), f'Review changed source roster before applying patch to {ident}'
        assert preset['leader'] == change['expectedLeader'], f'Review changed source leader before applying patch to {ident}'
        cards = list(preset['templateIds'])
        for card in change.get('remove', []):
            cards.remove(card)
        cards += change.get('add', [])
        if 'templateIds' in change:
            cards = list(change['templateIds'])
        leader = change.get('leader', preset['leader'])
        faction = full[leader]['faction']
        counts = Counter(cards)
        tiers = Counter(full[i]['tier'] for i in cards)
        allowed_sizes = (40,) if ident == 83 else ((25,26) if ident == 93 else (25,))
        assert full[leader]['leader'] and len(cards) in allowed_sizes
        assert tiers[8] <= 4 and tiers[4] <= 6
        assert all(not full[i]['leader'] and full[i]['faction'] in (1, faction) and n <= (3 if full[i]['tier'] == 2 else 1) for i, n in counts.items())
        preset.update(templateIds=cards, leader=leader, faction=faction)
        if 'description' in change:
            preset['description'] = change['description']
        profile.update(templateIds=cards, leader=leader, faction=faction)
        if 'family' in change:
            profile.update(family=change['family'], familyId=families[change['family']], passPolicy=change['passPolicy'])
            preset['description'] = 'Исследованный состав Beta 0.9.24; ' + change['family']
        if 'strategy' in change:
            profile['strategy'] = change['strategy']
        profile['notes'].append(change['reason'])
        profile['changes'].append(dict(method='reviewed-deck-patch128', requested=change['reason'], removed=change.get('remove', []), added=change.get('add', [])))
    titles = dict(patch['titles'], **variety['titles']);titles.update(current.get('titles', {}))
    for profile in profiles:
        title = titles.get(str(profile.get('presetId')))
        if title:
            profile['title'] = title
            by_preset[profile['presetId']]['title'] = 'ИИ · ' + title
    positions = 'Связки и позиции — карта → карта; ряд; слева / справа от кого'
    by_preset_profile = {p.get('presetId'): p for p in profiles}
    by_preset_profile[54]['strategy'][positions] = ('Фрингилья копирует силу левого соседа в правого. На чужой половине поставить её между любым слабым отрядом слева и сильным справа. Слабый сосед может уже стоять на поле; Эмиссар и другие слабые шпионы — лишь способы подготовить пару. Учитывать фактическую силу и итоговые подаренные очки. Убийцу ставить справа от жертвы.')
    by_preset_profile[58]['strategy'][positions] = ('Сабрину ставить в чужой ряд со слабым отрядом и более сильными целями, только при доступном способе убить её. Просчитать Завещание и затраты карты активации; без выгодного плана не дарить сопернику шпиона. Проклятую чародейку ставить с другим проклятым отрядом.')
    by_preset_profile[65]['strategy'][positions] = ('Драйг усиливает две полезные будущие цели в своём сбросе до розыгрыша жриц. Жрица Фрейи поднимает бронзового солдата, Зигфрида — подходящий отряд своего клана; учитывать категории и сохранённое усиление. Ветеран как поддержка не является целью жрицы.')
    for ident, cards in patch['retainedCards'].items():
        assert all(card in by_preset[int(ident)]['templateIds'] for card in cards)
    for ident, original in originals.items():
        assert json.dumps(by_preset[ident], sort_keys=True) == original, f'Protected preset {ident} changed'
    return patch
