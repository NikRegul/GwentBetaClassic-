"""Compile an explicit 13-language UI supplement and keep BG1 text opaque."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).parent))
from patch_ui_intro import ROOT,BUILD,read,write,rep
CHANGES={
 'Вставьте строку BG1 из буфера обмена. Импорт заменит текущий черновик; сохранённая колода изменится после нажатия «Сохранить колоду».':'Вставьте код BG1. Импорт заменит черновик. Затем сохраните колоду.',
 'Строка колоды скопирована в буфер обмена.':'Код колоды скопирован.',
 'Буфер обмена недоступен. Выделите строку и нажмите Ctrl+C.':'Буфер недоступен. Используйте Ctrl+C.',
 'Строка слишком длинная. Максимум 320 символов.':'Максимум 320 символов.',
 'Буфер обмена пуст или недоступен. Вставьте строку в поле.':'Буфер пуст. Вставьте код вручную.',
 'Сначала проверьте строку кнопкой «Импортировать».':'Сначала проверьте код.',
 'Экспорт доступен для колоды из 25–40 карт с допустимым составом.':'Нужна допустимая колода из 25–40 карт.',
 'Этот квест требует колоду указанной фракции.':'Для квеста нужна другая фракция.',
 'Все восемь слотов заняты. Откройте колоду для замены её черновика.':'Нет свободного слота. Откройте колоду для замены.',
 'Коллекция недоступна: неизвестная схема сохранения.':'Коллекция недоступна.',
 'Сначала завершите выбор оплаченной бочки.':'Сначала завершите выбор бочки.',
 'Колода импортирована в черновик. Нажмите «Сохранить колоду».':'Колода импортирована. Сохраните изменения.',
 'Колода импортирована в черновик.':'Колода импортирована.',
 'Некорректная строка колоды. Ожидается BG1:фракция:лидер:карты.':'Некорректный код BG1.',
 'Колода распознана.':'Код распознан.'}
def main():
    data=json.loads((ROOT/'data/beta924/design/ui-exchange082.json').read_text('utf8'))
    keys=data.pop('keys');data['ru_ru']=keys;data['es_mx']=data['es_es']
    codes=['','ru_ru','en_us','de_de','fr_fr','it_it','pl_pl','es_es','es_mx','pt_br','jp_jp','kr_kr','zh_cn','zh_tw']
    for code in codes[1:]:assert len(data[code])==len(keys) and all(data[code]),code
    source='''package { public class BetaGwentExchangeText082 {
private static const KEYS:Array=KEYS;
private static const VALUES:Array=VALUES;
public static function extend(language:int,data:Object):Object {
    if(language<1||language>13)return data;
    var values:Array=VALUES[language];
    for(var i:int=0;i<KEYS.length;i++){data[KEYS[i]]=values[i];data[String(KEYS[i]).toUpperCase()]=String(values[i]).toUpperCase();}
    return data;
}
} }
'''.replace('=KEYS;','='+json.dumps(keys,ensure_ascii=False,separators=(',',':'))+';').replace('=VALUES;','='+json.dumps([[]]+[data[c] for c in codes[1:]],ensure_ascii=False,separators=(',',':'))+';')
    for platform in ['nextgen','classic']:
        ui=BUILD/platform/'ui/src';write(ui/'BetaGwentExchangeText082.as',source)
        p=ui/'BetaGwentTextLanguage.as';s=rep(read(p),'data=BetaGwentUiText142.extend(value,data);','data=BetaGwentUiText142.extend(value,data);\n            data=BetaGwentExchangeText082.extend(value,data);');write(p,s)
        p=ui/'BetaGwentBoard.as';s=read(p)
        for a,b in CHANGES.items():s=s.replace(a,b)
        write(p,s)
    for name in ['developmentBoardMenu.ws','deckBuilder.ws']:
        p=BUILD/'scripts/game/betagwent'/name;s=read(p)
        for a,b in CHANGES.items():s=s.replace(a,b)
        write(p,s)
    (BUILD/'exchange-languages.json').write_text(json.dumps(dict(languages=13,strings=len(keys),explicitSpanishLatinAmerican=data['es_mx']==data['es_es']),indent=2),'utf8')
    print('Compiled',len(keys),'exchange phrases in all 13 languages')
if __name__=='__main__':main()
