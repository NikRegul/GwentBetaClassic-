"""Wait for the fixed AI trial, then build and audit once; never install/publish."""
from pathlib import Path
import argparse,datetime,json,os,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[2]
STATE=ROOT/'BetaGwent/drafts/day-iteration-20261023/state.json'
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()


def atomic(path,value):
    temporary=path.with_name(path.name+'.workflow.tmp');temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
    for attempt in range(101):
        try:temporary.replace(path);return
        except PermissionError:
            if attempt==100:raise
            time.sleep(.02)


def notes(proof):
    h=proof['holdout'];rate=100*h['scoreRate'];interval=f"{100*h['lower99']:.2f}–{100*h['upper99']:.2f}%"
    ru=f'''# Gwent Beta Classic0.9.3c

Улучшение обычного ИИ поверх полной0.9.3b для Classic1.32 и Next-Gen5.0+.

- Лидер оценивается вместе с публично допустимым ответом соперника и следующей картой своей руки. Подготовка сброса, воскрешения и усиления больше не ограничивается немедленным телом лидера. Прежний консервативный путь сохраняется при скрытой вражеской засаде и сниженном бюджете.
- В уже развитом первом раунде доборный шпион может конвертироваться в полезную карту с планом уступить раунд без ухудшения баланса руки. Свежая раздача, короткая/меньшая рука и обязательный раунд сохраняют строгую проверку восстановления перевеса. После шпиона бюджет догоняющего хода не ослабляется.
- Обязательные короткие окончания при нормальном бюджете сравнивают полные линии до4своих карт против1–3карт соперника, без оставшихся лидеров. При снижении бюджета для медленного устройства остаются прежние ограничения. Поиск организован шагами, максимум одно моделируемое действие за callback.

Независимое заранее зафиксированное сравнение с0.9.3b:3680партий,92уникальныхсостава,10случайных сеток пар и зеркальные стороны, {h['wins']}побед/{h['losses']}поражений/{h['draws']}ничьих,0ошибок. Доля очков кандидата **{rate:.2f}%**, приблизительный99%интервал по парным блокам {interval}; нижняя99%граница по кластерам составов {100*h['clusterLower99']:.2f}%. Ничьи учтены по0,5. Общие правила/раздачи/RNG, независимые муллиганы, обе стороны — высокая сложность с прежними информационными ограничениями. Это результат данного стенда, не гарантия превосходства на любой колоде или против человека. Доказательство включено в BetaGwentDocs/AI_Validation_0.9.3c.json.

Сохранены исправления блокировки/«Стойкости», видимая сложность в выборе колоды/редакторе, все одобренные колоды и исходная «Классическая» с24профилями/109назначениями. Classic по-прежнему видит скрытую руку/колоду; обычный Hard не получает этих знаний. Старый knockout завершён на неизменной0.9.3 и не используется как испытание новойc.

Технические проверки, оба nativeWS-компилятора, профильные партии, управление контроллером, меню<=65МиБ и независимыеSHA/CRC обязательны для готового архива. Нативная игровая приёмка интерфейса/RNG остаётся открытой. Установка и публикация автоматически не выполняются.
'''
    en=f'''# Gwent Beta Classic0.9.3c

Ordinary AI improvements over the complete0.9.3b release, for Classic1.32 and Next-Gen5.0+.

- Leaders now evaluate an opponent reply and their own subsequent hand play, including enabled discard/resurrection/boost setup. Concealed opposing traps and reduced computation budgets retain the conservative fallback.
- In a developed optional first round, a drawing spy can convert itself into a useful card before conceding without worsening hand balance. Fresh openings, smaller/short hands and mandatory rounds keep strict recovery checks; the subsequent chase budget is unchanged.
- Mandatory short fronts evaluate complete lines with up to4own cards against1–3opposing cards when no leaders remain and the normal budget is available. Slow-device limits remain unchanged. Search stays cooperative with at most one simulated action per callback.

Fixed independent trial against0.9.3b:3680games,92unique compositions,10random matchup grids and mirrored sides; {h['wins']}wins/{h['losses']}losses/{h['draws']}draws,0errors. Candidate score rate **{rate:.2f}%**, approximate99%paired-block interval {interval}; composition-cluster99%lower bound {100*h['clusterLower99']:.2f}%. Draws count0.5. Common mechanics/deals/RNG, independent mulligans, both policies on high difficulty with unchanged information limits. This supports the measured finite trial, not universal superiority or retail gameplay acceptance. Evidence: BetaGwentDocs/AI_Validation_0.9.3c.json.

Includes the lock/resilience and visible deck-difficulty fixes from0.9.3b, approved decks and unchanged original Classic AI with24profiles/109bindings. Classic retains hidden-hand/deck access; ordinary Hard retains its restrictions. The completed frozen0.9.3knockout does not test this update.

Final archives require regressions, both nativeWS compilers, profile games, controller checks, menus<=65MiB and independent SHA/CRC verification. Native in-game UI/RNG acceptance is pending. Nothing is installed or published automatically.
'''
    for language,text in [('RU',ru),('EN',en)]:
        for kind in ['CHANGELOG','DESCRIPTION','POST']:(ROOT/f'docs/releases/0.9.3c_{kind}_{language}.md').write_text(text,'utf8')
    directory=ROOT/'docs/releases/0.9.3c/nexus';directory.mkdir(parents=True,exist_ok=True)
    (directory/'README_RU.md').write_text('Пакет0.9.3c подготовлен локально; публикация не выполнялась. Описания/посты/изменения в docs/releases/0.9.3c_*.md.\n','utf8')


def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--holdout',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    candidate=a.candidate.resolve();holdout=a.holdout.resolve();out=a.out.resolve();control=out.with_name(out.name+'-workflow')
    assert out.is_relative_to(ROOT/'BetaGwent/build') and not out.exists() and not control.exists();control.mkdir()
    status=dict(status='waiting-fixed-holdout',pid=os.getpid(),candidate=str(candidate),holdout=str(holdout),out=str(out),started=now())
    def save():status['lastActivity']=now();atomic(control/'workflow.json',status)
    def run(label,command):
        status.update(status='running',stage=label);save()
        with (control/(label+'.log')).open('w',encoding='utf8') as log:subprocess.run([str(x) for x in command],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        print('PASS',label,flush=True)
    try:
        save()
        while True:
            try:summary=json.loads((holdout/'summary.json').read_text('utf8'))
            except (OSError,json.JSONDecodeError):time.sleep(10);continue
            status['trialProgress']={k:summary.get(k) for k in ['completedGames','plannedGames','errors','complete']};save()
            if summary['complete']:break
            if time.time()-(holdout/'summary.json').stat().st_mtime>1800:raise RuntimeError('Holdout stale; inspect without blind restart')
            time.sleep(10)
        if not summary.get('acceptancePassed'):
            status.update(status='quality-rejected',reason='Predeclared independent strength criterion failed. No release built.');save();print(json.dumps(status));return
        assert not out.exists(),'Another build already owns the target'
        proof_path=ROOT/'data/beta924/design/ai093c_validation.json'
        run('accept-ai',[sys.executable,'-X','utf8','tools/ai/accept_candidate093c.py',candidate,holdout,proof_path])
        proof=json.loads(proof_path.read_text('utf8'));notes(proof)
        run('build',[sys.executable,'-X','utf8','tools/features093/build093c.py','--out',out])
        run('full-games',['node','tools/ai/check_full_matches094.js',out/'rules',out/'full-ai-games'])
        run('archive-audit',[sys.executable,'-X','utf8','tools/features093/verify093.py',out,'--version','0.9.3c'])
        audit=json.loads((out/'archive-verification.json').read_text('utf8'))
        ready=dict(version='0.9.3c',status='ready',completedAt=now(),verifiedReport='archive-verification.json',sourceFingerprint=proof['candidateFingerprint'],
                   archives=audit['archives'],hardAI=audit['hardAI'],ordinaryAI=audit['ordinaryAI'],maxMenuBytes=audit['maxMenuBytes'],
                   classicCompilerPassed=True,nextgenCompilerPassed=True,fiveIdenticalBomCrlfCopies=True,nativeGameplayVerified=False,installed=False,published=False)
        atomic(out/'release-readiness.json',ready)
        state=json.loads(STATE.read_text('utf8'));state['userRequested093c'].update(ready);state['userRequested093c']['out']=str(out)
        state['mainWorkActive']=False;state['lastMainActivity']=now();state['nextAction']='Verified0.9.3c ready; nothing installed/published; native in-game UI/RNG acceptance remains.';atomic(STATE,state)
        readme=ROOT/'README.md';text=readme.read_text('utf8');first=text.splitlines()[0]
        if '0.9.3b' in first:readme.write_text(text.replace(first,first.replace('0.9.3b','0.9.3c').replace('build093b.py','build093c.py'),1),'utf8')
        current=ROOT/'docs/REPOSITORY_CURRENT_RU.md';text=current.read_text('utf8').replace('# Текущее состояние: 0.9.3b','## Предыдущая версия: 0.9.3b',1)
        current.write_text(f'# Текущее состояние:0.9.3c\n\nПолные проверенные архивы: `{out.relative_to(ROOT).as_posix()}`. [Изменения](releases/0.9.3c_CHANGELOG_RU.md).85регрессионных групп,7508адресных проверок семи новых групп,1426тактик,414рядов,5632дополнительные позиции,10полных технических партий и оба нативных компилятора пройдены. Независимое сравнение3680партий: {proof["holdout"]["scoreRate"]*100:.2f}%очков против0.9.3b; оба99%нижних порога выше50%. SHA/CRC обоих архивов проверены. Обычный Hard сохраняет ограничения информации; исходная Classic не менялась. Нативная игровая приёмка остаётся открытой, установки/публикации нет. Сборка: `python -X utf8 tools/features093/build093c.py`.\n\n'+text,'utf8')
        history=ROOT/'docs/AI_IMPROVEMENT_HISTORY_092_RU.md';text=history.read_text('utf8')
        history.write_text(text+f'\n\n###25октября:0.9.3c после разбора партий\n\nТри изменения политики: продолжение после лидера, развитый R1 с доборным шпионом и сохранением баланса руки, обязательный4-карточный фронт при нормальном бюджете. История отрицательных гипотез и развития в AI_IMPROVEMENT_PLAN_093C_RU.md. Независимый holdout3680/3680: {proof["holdout"]["wins"]}/{proof["holdout"]["losses"]}/{proof["holdout"]["draws"]}, {proof["holdout"]["scoreRate"]*100:.2f}%очков,0errors;99%нижние границы по блокам и составам выше50%. Все85групп/7508адресных проверок,1426тактик/414рядов/5632позиции,10полных технических партий и оба nativeWSкомпилятора прошли. Проверенный UI0.9.3b сохранён поSHA исходников/ресурсов. Итог `{out.relative_to(ROOT).as_posix()}`: archive-verification.json/release-readiness.json подтверждают обаZIP. Ничего не установлено/не опубликовано; nativegameplay/универсальная сила не заявляются.\n','utf8')
        status.update(status='ready',stage='complete',readiness=str(out/'release-readiness.json'));save();print(json.dumps(ready))
    except BaseException as error:
        status.update(status='failed',error=repr(error));save();raise


if __name__=='__main__':main()
