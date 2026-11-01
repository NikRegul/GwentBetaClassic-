"""Build the next development baseline as a complete, independently checked 0.9.5."""
from pathlib import Path
import argparse,datetime,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
from ui_release095 import NOTES,inputs as ui_inputs
from ui_release095_text import CHECKLIST as UI_CHECKLIST


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);p.add_argument('--resume',action='store_true');p.add_argument('--finish-prepared',action='store_true',help='only re-run the final collect/package/audit on a folder whose checks all passed');a=p.parse_args()
    if (a.resume or a.finish_prepared) and a.out is None:p.error('--resume/--finish-prepared require an explicit --out')
    if a.resume and a.finish_prepared:p.error('choose one of --resume and --finish-prepared')
    out=(a.out or ROOT/'BetaGwent/build'/datetime.datetime.now().strftime('release095-%Y%m%d-%H%M%S')).resolve()
    if not out.is_relative_to(ROOT/'BetaGwent/build') or out==ROOT/'BetaGwent/build':p.error('--out must be a child of BetaGwent/build')
    subprocess.run([sys.executable,'-X','utf8','tools/recon/check_project_layout.py'],cwd=ROOT,check=True)
    ui_inputs()  # Refuse a stale/missing UI sound cache before expensive compilation.
    command=[sys.executable,'-X','utf8','tools/features094/build094a_public.py','--version','0.9.5','--out',str(out)]
    if a.resume:command.append('--resume')
    if a.finish_prepared:command.append('--finish-prepared')
    subprocess.run(command,cwd=ROOT,check=True)
    sys.path.insert(0,str(ROOT/'tools/features094'))
    import collect_release094a as collect
    collect.VERSION='0.9.5';collect.NOTES=NOTES
    collect.CHECKLIST=collect.CHECKLIST.replace('0.9.4a','0.9.5').replace('## Эффекты редактора колод (новое в 0.9.5)','## Эффекты редактора колод (сохранённое поведение)')+'''
## Новое в 0.9.5
- [ ] Новые меню редактора/коллекции: баннер имени, шесть колонок, фильтры, поиск, правая панель создания.
- [ ] Анимации добавления строки, счётчика копий и удаления строки работают после подтверждения.
- [ ] Подсказки контроллера и удержание паса на монете работают при смене устройства ввода.
- [ ] Нет пояснения под лидером; список начинается сразу под его строкой.
- [ ] Фиолетовая плашка не перекрывает дерево; полотно предпросмотра заполняет внутреннюю рамку, знамя сохраняет исходные пропорции.
- [ ] Нет строки «Соперник: Соперник»; настоящее имя NPC сохраняется.
- [ ] Hard: после шпиона в развитом раунде не тратит последние карты ради запаса очков.
- [ ] Перенос стойкости и возвращение Моркварга учитываются при оценке следующего раунда.
- [ ] Обязательный раунд не сдаётся ради экономии или смены очередности.
- [ ] Кровавый бич без доступной цели создаёт Призрака; при заполненных своих рядах лишнего экземпляра нет.
- [ ] Лже-Цири после паса сохраняет индекс ряда на другой стороне (с ограничением по длине ряда).
- [ ] Эмгыр: возврат отряда предлагается на BeforeTurnEnd после завершения вложенного розыгрыша, включая особую карту.
- [ ] Гнездо чудовищ: созданный отряд уже усилен на 1 до выбора места и выполнения своей способности.
- [ ] Ге’эльс: пропуск необязательного выбора возвращает обе карты наверх колоды в порядке исходного MoveCards.
- [ ] Димун: пропуск выбора не меняет карты; следующий случайный эффект использует корректный поток RNG.
- [ ] Йеннифэр: некромант без подходящих карт завершает способность без пустого окна «Продолжить».
- [ ] Оба Лавка: доступны все предложенные варианты; удар охотника на 15 позволяет выбрать отряд любой стороны.
'''
    collect.CHECKLIST+=UI_CHECKLIST
    dest=collect.main([str(out)])
    ready=json.loads((out/'release-readiness.json').read_text('utf8'))
    (ROOT/'BetaGwent/build/release095-public-latest.json').write_text(json.dumps(dict(path=str(out),version='0.9.5',status='ready',fingerprint=ready['sourceFingerprint'],releaseFolder=str(dest)),indent=2)+'\n','utf8')
    print('READY 0.9.5:',dest,flush=True)


if __name__=='__main__':main()
