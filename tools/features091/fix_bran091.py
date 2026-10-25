"""Guarded, reproducible roster correction: Bran 96, Triss -> Holger Blackhand."""
from pathlib import Path
from collections import Counter
import hashlib, json, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text('utf-8-sig'))
def write(p,data):(ROOT/p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    rules=read('data/beta924/ai/rules.json');profile=next(p for p in rules['profiles'] if p['presetId']==96)
    before=profile['templateIds'];assert before.count(201773)==1 and 152109 not in before
    after=[152109 if i==201773 else i for i in before];strategy=dict(profile['strategy'])
    key='Цели контроля и контрдействия — кого бить, блокировать, перемещать'
    strategy[key]=strategy[key].replace('Трисс выбирает доступную бронзовую особую.','Морской Вепрь поддерживает собственную пару: Мечник справа получает рану, полезный отряд слева — укрепление. Не зависит от бронзовых особых соперника.')
    key='Связки и позиции — карта → карта; ряд; слева / справа от кого'
    strategy[key]+=' Морской Вепрь ставится между полезным левым отрядом и Мечником справа; его укрепление слева и ранение справа учитываются отдельно.'
    patch=read('data/beta924/ai/deck_patch128.json');assert not any(p['presetId']==96 for p in patch['decks'])
    patch['decks'].append(dict(presetId=96,expectedLeader=profile['leader'],expectedTemplateIds=before,templateIds=after,
        remove=[201773],add=[152109],strategy=strategy,
        reason='0.9.1: по замечанию пользователя Трисс заменена Морским Вепрем: в собственном составе нет бронзовых особых, а Вепрь поддерживает self-wound/мечников без зависимости от колоды соперника.'))
    write('data/beta924/ai/deck_patch128.json',patch)
    subprocess.run([sys.executable,'-X','utf8','tools/build_ai_rules.py'],cwd=ROOT,check=True)
    path=ROOT/'BetaGwent/development/scripts/game/betagwent/duelCatalog.ws';raw=path.read_bytes();text=raw.decode('utf-8-sig')
    match=re.search(r'function BetaGwentDuelPresetCards96\([^)]*\)\s*\{([^}]*)\}',text);assert match
    old_ids=[int(i) for i in re.findall(r'ids.PushBack\((\d+)\)',match.group(1))];assert old_ids==before
    body=match.group(1).replace('ids.PushBack(201773);','ids.PushBack(152109);');text=text[:match.start(1)]+body+text[match.end(1):]
    # Only this generated preset list changes; card definitions are preserved.
    path.write_bytes(b'\xef\xbb\xbf'+text.encode('utf8'))
    data=read('data/beta924/duel/slice.json');target=next(p for p in data['presets'] if p['id']==96)
    assert target['templateIds']==before;target['templateIds']=after;target['cards']=[dict(templateId=i,copies=n) for i,n in Counter(after).items()]
    data['presetsSourceSha256']=hashlib.sha256((ROOT/'data/beta924/duel/presets.json').read_bytes()).hexdigest();write('data/beta924/duel/slice.json',data)
    result=dict(preset=96,removed=201773,added=152109,oldCards=before,newCards=after,originalCardRulesChanged=False)
    write('docs/evidence/bran091-roster-fix.json',result);print(json.dumps(result))
if __name__=='__main__':main()
