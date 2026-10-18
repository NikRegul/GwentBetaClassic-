"""Generate test data and unfilled per-platform results from the scenario document."""
from pathlib import Path
import csv,hashlib,json,subprocess,zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/releases/0.8.2/regression'
BUILD=ROOT/'BetaGwent/build/release082-final'

def main():
    harness=BUILD/'exchange-tests/test.js'
    assert harness.is_file(),'Run the production exchange checks against the frozen final sources first'
    js=r'''const fs=require('fs'),vm=require('vm');const source=fs.readFileSync(process.argv[1],'utf8');
const result=vm.runInNewContext(source+'\nJSON.stringify(compositions.map((x,i)=>({preset:i+1,code:x.code,faction:x.result.faction,leader:x.result.leader,cards:x.result.cards.length})))',{console:{log(){}}},{timeout:120000});process.stdout.write(result);'''
    run=subprocess.run(['node','-e',js,str(harness)],cwd=ROOT,capture_output=True,text=True,encoding='utf8',check=True)
    valid=json.loads(run.stdout)
    assert len(valid)==46 and {v['faction'] for v in valid}=={2,4,8,16,32}
    good=valid[0]['code'];parts=good.split(':');cards=parts[3].split(',')
    bad=[('empty',''),('wrong_version',good.replace('BG1:','BG2:',1)),('leading_space',' '+good),('trailing_space',good+' '),('trailing_comma',good+','),('unknown_leader',':'.join([parts[0],parts[1],'999999',parts[3]])),('unknown_card',':'.join(parts[:3]+[','.join(cards[:-1]+['999999'])])),('too_many_cards',':'.join(parts[:3]+[','.join([cards[0]]*41)])),('extra_separator',good+':1')]
    payload=dict(sourceHarness=str(harness.relative_to(ROOT)),sourceSha256=hashlib.sha256(harness.read_bytes()).hexdigest(),valid=valid,
                 selected=[next(v for v in valid if v['faction']==f) for f in [2,4,8,16,32]],
                 invalid=[dict(id=n,code=c,expected='rejected; draft, saved decks, collection, scraps and slots unchanged') for n,c in bad])
    (OUT/'BG1_FIXTURES.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n','utf8')
    (OUT/'BG1_VALID.txt').write_text('\n\n'.join(f"Preset {v['preset']}; faction={v['faction']}; leader={v['leader']}; cards={v['cards']}\n{v['code']}" for v in payload['selected'])+'\n','utf-8-sig')
    cases=[]
    for line in (OUT/'SCENARIOS_RU.md').read_text('utf8').splitlines():
        if not line.startswith('| ') or not any(line.startswith('| '+p+'-') for p in ['SMK','PAD','EX','LOC','FX','VS','CON','SAVE','AI']):continue
        ident,steps,expected=[p.strip() for p in line.strip('|').split('|')]
        assert ident not in {c['id'] for c in cases}
        cases.append(dict(id=ident,steps=steps,expected=expected,kind='model_and_game_replay' if ident.startswith('AI-') else 'game'))
    assert len(cases)>=70,len(cases)
    (OUT/'SCENARIOS.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n','utf8')
    with (OUT/'RESULTS.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['id','platform','result','game_version','mod_archive','save','seed','text','voice','input','resolution','actual','evidence'])
        for case in cases:
            for platform in ['1.32','5.0+']:writer.writerow([case['id'],platform,'NOT_RUN']+['']*10)
    readme='''# Регрессионный комплект 0.8.2

SCENARIOS_RU.md — условия, действия и ожидания; SCENARIOS.json — те же случаи для инструментария.
RESULTS.csv — отдельные незаполненные результаты для 1.32 и 5.0+.
BG1_VALID.txt — пять готовых кодов разных фракций; BG1_FIXTURES.json — 46 допустимых и отрицательные примеры.

Фикстуры извлечены из настоящего парсера и каталога зафиксированной сборки. Генерация не выполняет игровые сценарии и не меняет сохранения.
Автоматические проверки финальной сборки записаны отдельно в JSON-отчётах BetaGwent/build/release082-final и docs/evidence/features082-*; игровые результаты не отмечены выполненными автоматически.
'''
    (OUT/'README_RU.md').write_text(readme,'utf-8-sig')
    archive=ROOT/'BetaGwent/release/GwentBetaClassic-0.8.2-Regression-Pack.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.iterdir()):
            if p.is_file():z.write(p,p.name)
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print(json.dumps(dict(scenarios=len(cases),resultRows=2*len(cases),validCodes=len(valid),invalidCodes=len(bad),archive=str(archive)),ensure_ascii=False))

if __name__=='__main__':main()
