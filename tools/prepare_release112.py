from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'data/beta924/design/english89.json';d=json.loads(p.read_text('utf8'))
d.update({
 'ПОИСК КАРТ':'CARD SEARCH',
 ' · Enter — принять · Esc — отменить':' · Enter — apply · Esc — cancel',
 'Клавиатура или кнопки букв · RU / EN переключает язык ввода.\nПосле изменения названия сохраните колоду.':'Type or use the letter buttons · RU / EN switches input language.\nSave the deck after changing its name.',
 'Клавиатура или кнопки букв · RU / EN переключает язык ввода.\nПустая строка убирает поиск; Enter применяет фильтр.':'Type or use the letter buttons · RU / EN switches input language.\nAn empty query clears the search; Enter applies the filter.',
 'Не удалось записать колоду в сохранение.':'Could not write the deck to your save.',
 'Удерживайте P / Y / △ или монету для паса.':'Hold P / Y / triangle or the coin to pass.',
 'йцукенгшщзхъфывапролджэячсмитьбюё':'йцукенгшщзхъфывапролджэячсмитьбюё',
})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
s=(ROOT/'tools/Build-Stage111.ps1').read_text('utf-8-sig').replace('0.3.2','0.3.3').replace('Stage111','Stage112').replace('111','112').replace('BUILD_032_RU','BUILD_033_RU')
# Assets and sound banks are unchanged from 0.3.2; retain the validated inputs.
s=s.replace("Step 'resilience atlas' @('tools/ui/build_tokens112.py')", "Step 'text metrics' @('tools/ui/build_text_metrics112.py')")
s=s.replace("Step 'keg atlas' @('tools/ui/build_keg109.py')", "# Keg textures unchanged from 0.3.2.")
s=s.replace("tools/ui/extract_keg112.py", "tools/ui/extract_keg111.py")
s=s.replace("Step 'keg audio' @('tools/ui/add_keg_audio109.py')", "# Reuse the licensed, validated RU/EN banks from 0.3.2.")
(ROOT/'tools/Build-Stage112.ps1').write_text(s,'utf-8-sig')
log=ROOT/'docs/evidence/stage112-last-game-scriptslog.txt'
shutil.copyfile(Path.home()/'Documents/The Witcher 3/scriptslog.txt',log)
print('0.3.3 build script and preserved game log ready')
