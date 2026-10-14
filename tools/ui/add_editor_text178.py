"""0.7.3 editor labels in all 13 supported text languages."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=root/'data/beta924/design/ui-polish138.json';data=json.loads(p.read_text('utf8'))
values={
'ru_ru':['Выберите фракцию','Выберите лидера','Вернуться к фракциям','Новые карты','НОВАЯ','Прокрутка'],
'en_us':['Choose a faction','Choose a leader','Back to factions','New cards','NEW','Scroll'],
'de_de':['Fraktion wählen','Anführer wählen','Zurück zu den Fraktionen','Neue Karten','NEU','Scrollen'],
'fr_fr':['Choisissez une faction','Choisissez un chef','Retour aux factions','Nouvelles cartes','NOUVELLE','Défilement'],
'it_it':['Scegli una fazione','Scegli un leader','Torna alle fazioni','Nuove carte','NUOVA','Scorri'],
'pl_pl':['Wybierz frakcję','Wybierz dowódcę','Powrót do frakcji','Nowe karty','NOWA','Przewijanie'],
'es_es':['Elige una facción','Elige un líder','Volver a las facciones','Cartas nuevas','NUEVA','Desplazar'],
'es_mx':['Elige una facción','Elige un líder','Volver a las facciones','Cartas nuevas','NUEVA','Desplazar'],
'pt_br':['Escolha uma facção','Escolha um líder','Voltar às facções','Novas cartas','NOVA','Rolar'],
'jp_jp':['勢力を選択','リーダーを選択','勢力選択に戻る','新しいカード','新規','スクロール'],
'kr_kr':['진영 선택','리더 선택','진영 선택으로 돌아가기','새 카드','신규','스크롤'],
'zh_cn':['选择阵营','选择领袖','返回阵营选择','新卡牌','新','滚动'],
'zh_tw':['選擇陣營','選擇領袖','返回陣營選擇','新卡牌','新','捲動'],
}
extra={'ru_ru': 'LB/RB страницы', 'en_us': 'LB/RB pages', 'de_de': 'LB/RB Seiten', 'fr_fr': 'LB/RB pages', 'it_it': 'LB/RB pagine', 'pl_pl': 'LB/RB strony', 'es_es': 'LB/RB páginas', 'es_mx': 'LB/RB páginas', 'pt_br': 'LB/RB páginas', 'jp_jp': 'LB/RB ページ', 'kr_kr': 'LB/RB 페이지', 'zh_cn': 'LB/RB 翻页', 'zh_tw': 'LB/RB 翻頁'}
for locale,label in extra.items():values[locale].append(label)
for i,key in enumerate(values['ru_ru']):
 if key in data['keys']:continue
 data['keys'].append(key)
 for locale,labels in values.items():
  if locale!='ru_ru':data[locale].append(labels[i])
assert all(len(data[k])==len(data['keys']) for k in values if k!='ru_ru')
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
print('0.7.3 labels prepared for',len(values),'languages')
