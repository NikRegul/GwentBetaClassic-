"""Exercise cross-game rollback before using the installer on real games."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import importlib.util,json,tempfile,unittest,zipfile

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('installer092',ROOT/'tools/features092/install092.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class InstallTests(unittest.TestCase):
    def fixture(self,root):
        m.ROOT=root;m.TARGETS={p:root/'games'/p for p in ['1.32','5.0+']}
        build=root/'BetaGwent/build/test';(build/'archives').mkdir(parents=True);archives=[]
        for platform,game in m.TARGETS.items():
            exe=game/'bin/x64/witcher3.exe';exe.parent.mkdir(parents=True);exe.write_bytes(b'fixture')
            for n in [f'Mods/{next(n for n in m.MODS[platform] if n!="modBetaGwentMenuMusic")}/old.txt','Mods/unrelated/keep.txt','BetaGwentDocs/old.txt']:
                f=game/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b'old')
            files={f'Mods/{n}/new.txt':b'new' for n in m.MODS[platform]};files['BetaGwentDocs/new.txt']=b'new docs'
            if platform=='1.32':files['DLC/dlcBetaGwentClassic132Assets/new.txt']=b'asset'
            archive=build/f'archives/GwentBetaClassic-0.9.2-{platform}-AllLanguages.zip'
            import hashlib
            with zipfile.ZipFile(archive,'w') as z:
                for n,raw in files.items():z.writestr(n,raw)
                z.writestr('manifest-0.9.2.json',json.dumps(dict(version='0.9.2',files=[dict(path=n,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()) for n,raw in files.items()])))
            archives.append(dict(path=str(archive),sha256=m.sha(archive)))
        (build/'release.json').write_text(json.dumps(dict(version='0.9.2',archives=archives)),'utf8');return build

    def test_install_and_complete_backups(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp',prefix='install092-test-') as tmp:
            build=self.fixture(Path(tmp));before={p:m.tree(g) for p,g in m.TARGETS.items()};m.prepare(build)
            with patch.object(m.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='')):m.apply(build)
            report=json.loads((build/'install-stage/installed.json').read_text());backup=Path(report['backup'])
            for platform,game in m.TARGETS.items():
                self.assertEqual((game/'Mods/unrelated/keep.txt').read_bytes(),b'old')
                for n,sha in before[platform].items():
                    if n.startswith(('Mods/modBeta','BetaGwentDocs/')):self.assertEqual(m.sha(backup/platform/n),sha)
                self.assertTrue((game/'Mods/modBetaGwentMenuMusic/new.txt').is_file())

    def test_second_game_failure_restores_both(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp',prefix='install092-test-') as tmp:
            build=self.fixture(Path(tmp));before={p:m.tree(g) for p,g in m.TARGETS.items()};m.prepare(build)
            copy=m.shutil.copytree;failed=False
            def injected(source,dest,*args,**kwargs):
                nonlocal failed
                if not failed and 'install-stage/5.0+/Mods/' in Path(source).as_posix():failed=True;raise OSError('injected copy failure')
                return copy(source,dest,*args,**kwargs)
            with patch.object(m.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='')),patch.object(m.shutil,'copytree',side_effect=injected):
                with self.assertRaises(OSError):m.apply(build)
            self.assertTrue(failed)
            for platform,game in m.TARGETS.items():self.assertEqual(m.tree(game),before[platform])

    def test_modified_staging_cannot_change_games(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp',prefix='install092-test-') as tmp:
            build=self.fixture(Path(tmp));m.prepare(build);before={p:m.tree(g) for p,g in m.TARGETS.items()}
            (build/'install-stage/1.32/BetaGwentDocs/new.txt').write_bytes(b'corrupt')
            with patch.object(m.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='')):
                with self.assertRaises(AssertionError):m.apply(build)
            for platform,game in m.TARGETS.items():self.assertEqual(m.tree(game),before[platform])

if __name__=='__main__':unittest.main()
