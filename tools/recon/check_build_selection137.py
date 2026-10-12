"""Check selected-package isolation and preservation without running REDkit."""
import importlib.util,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('release137',ROOT/'tools/build_release137.py')
build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
with tempfile.TemporaryDirectory(dir=ROOT/'BetaGwent/build/stage137',prefix='scope-test-') as folder:
    fixture=Path(folder)
    assert fixture.resolve().is_relative_to((ROOT/'BetaGwent/build/stage137').resolve())
    build.ROOT=fixture;build.BASE=fixture/'BetaGwent/build/stage137';build.RUN='test'
    build.BASE.mkdir(parents=True)
    release=fixture/'BetaGwent/release';release.mkdir(parents=True)
    old=release/'GwentBetaClassic-0.6.0-RU.zip';old.write_bytes(b'old stable')
    for language in build.VOICES:
        name=f'GwentBetaClassic-0.6.1-{language.upper()}.zip'
        (release/name).write_bytes(language.encode())
        (release/(name+'.sha256')).write_text(language)
        stage=fixture/f'BetaGwent/build/release137/{language}';stage.mkdir(parents=True)
        (stage/'frozen.json').write_text('{}')
    (build.BASE/'compilations137.json').write_text(json.dumps({x:{'compiled':'native-'+x} for x in build.VOICES}))
    calls=[]
    build.python=lambda name,*arguments:calls.append((name,arguments))
    build.package(('ru',),rebuild=True)
    assert [name for name,args in calls if name.startswith('package-')]==[
        'package-ru-'+phase for phase in ('prepare','cook','strings','audio','dependencies','pack','metadata','archive')]
    assert (release/'quarantine/0.6.1-test/GwentBetaClassic-0.6.1-RU.zip').read_bytes()==b'ru'
    assert (fixture/'BetaGwent/build/history137/test/ru/frozen.json').exists()
    assert not (release/'GwentBetaClassic-0.6.1-RU.zip').exists()
    assert old.read_bytes()==b'old stable'
    for language in ('en','de','it','pt-br'):
        assert (release/f'GwentBetaClassic-0.6.1-{language.upper()}.zip').read_bytes()==language.encode()
        assert (fixture/f'BetaGwent/build/release137/{language}/frozen.json').exists()
    calls.clear();build.RUN='all'
    build.package(build.VOICES,rebuild=True)
    assert len([name for name,args in calls if name.startswith('package-')])==40
    assert {args[args.index('--language')+1] for name,args in calls if name.endswith('-archive')}==set(build.VOICES)
    assert old.read_bytes()==b'old stable'
print('PASS: RU-only selection, all five selections, preserved archives/staging, stable version untouched')
