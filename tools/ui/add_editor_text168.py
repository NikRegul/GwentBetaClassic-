"""Add the 0.7.1 editor labels to all 13 native dictionaries."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
path=ROOT/'data/beta924/design/ui-polish138.json'
data=json.loads(path.read_text('utf8'))
values={
'ru_ru':['Сохранить изменения колоды?','Состав, лидер или название изменены. Выберите, что сделать перед выходом.','Не сохранять','Позиция: все','Рукопашный','Дальнобойный','Осадный','Подвижные','Событие','По редкости','Слабые сначала','Сильные сначала','Сбросить фильтры','Открыть ещё одну бочку'],
'en_us':['Save deck changes?','Cards, leader or name have changed. Choose what to do before leaving.','Discard','Position: all','Melee','Ranged','Siege','Agile','Event','By rarity','Weakest first','Strongest first','Reset filters','Open another keg'],
'de_de':['Deckänderungen speichern?','Karten, Anführer oder Name wurden geändert. Wähle eine Aktion vor dem Verlassen.','Nicht speichern','Position: alle','Nahkampf','Fernkampf','Belagerung','Agil','Ereignis','Nach Seltenheit','Schwächste zuerst','Stärkste zuerst','Filter zurücksetzen','Weiteres Fass öffnen'],
'fr_fr':['Enregistrer les modifications ?','Les cartes, le chef ou le nom ont changé. Choisissez une action avant de quitter.','Ne pas enregistrer','Position : toutes','Corps à corps','À distance','Siège','Agile','Événement','Par rareté','Faibles en premier','Fortes en premier','Réinitialiser les filtres','Ouvrir un autre baril'],
'it_it':['Salvare le modifiche al mazzo?','Carte, leader o nome sono cambiati. Scegli cosa fare prima di uscire.','Non salvare','Posizione: tutte','Corpo a corpo','A distanza','Assedio','Agile','Evento','Per rarità','Prima le più deboli','Prima le più forti','Azzera filtri','Apri un altro barile'],
'pl_pl':['Zapisać zmiany talii?','Zmieniono karty, dowódcę lub nazwę. Wybierz działanie przed wyjściem.','Nie zapisuj','Pozycja: wszystkie','Wręcz','Dystansowe','Oblężnicze','Zwinne','Wydarzenie','Według rzadkości','Najsłabsze najpierw','Najsilniejsze najpierw','Zresetuj filtry','Otwórz kolejną beczkę'],
'es_es':['¿Guardar cambios del mazo?','Han cambiado las cartas, el líder o el nombre. Elige qué hacer antes de salir.','No guardar','Posición: todas','Cuerpo a cuerpo','A distancia','Asedio','Ágil','Evento','Por rareza','Más débiles primero','Más fuertes primero','Restablecer filtros','Abrir otro barril'],
'es_mx':['¿Guardar cambios del mazo?','Han cambiado las cartas, el líder o el nombre. Elige qué hacer antes de salir.','No guardar','Posición: todas','Cuerpo a cuerpo','A distancia','Asedio','Ágil','Evento','Por rareza','Más débiles primero','Más fuertes primero','Restablecer filtros','Abrir otro barril'],
'pt_br':['Salvar alterações do baralho?','As cartas, o líder ou o nome mudaram. Escolha o que fazer antes de sair.','Não salvar','Posição: todas','Corpo a corpo','À distância','Cerco','Ágil','Evento','Por raridade','Mais fracas primeiro','Mais fortes primeiro','Redefinir filtros','Abrir outro barril'],
'jp_jp':['デッキの変更を保存しますか？','カード、リーダー、または名前が変更されています。終了前の操作を選択してください。','保存しない','配置：すべて','近接','間接','攻城','機動','イベント','レア度順','弱い順','強い順','フィルターをリセット','樽をもう1つ開ける'],
'kr_kr':['덱 변경 사항을 저장할까요?','카드, 리더 또는 이름이 변경되었습니다. 나가기 전에 작업을 선택하세요.','저장 안 함','배치: 전체','근접','원거리','공성','민첩','이벤트','희귀도순','약한 카드부터','강한 카드부터','필터 초기화','술통 하나 더 열기'],
'zh_cn':['保存牌组修改？','卡牌、领袖或名称已更改。请选择离开前的操作。','不保存','位置：全部','近战','远程','攻城','敏捷','事件','按稀有度','弱者优先','强者优先','重置筛选','再开一个桶'],
'zh_tw':['儲存牌組修改？','卡牌、領袖或名稱已變更。請選擇離開前的操作。','不儲存','位置：全部','近戰','遠程','攻城','敏捷','事件','依稀有度','弱者優先','強者優先','重設篩選','再開一個桶'],
}
for i,key in enumerate(values['ru_ru']):
    if key in data['keys']:continue
    data['keys'].append(key)
    for locale,translations in values.items():
        if locale!='ru_ru':data[locale].append(translations[i])
assert all(len(data[k])==len(data['keys']) for k in values if k!='ru_ru')
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
print('Added',len(values['ru_ru']),'labels in',len(values),'languages')
