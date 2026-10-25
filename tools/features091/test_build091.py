"""Compiler-success and package-integrity contracts, using isolated temporary files."""
from pathlib import Path
import importlib.util, json, sys, tempfile, unittest, zipfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
build=module('build091',ROOT/'tools/features091/build091.py')
compiler=module('compile_ng',ROOT/'tools/features082/compile_nextgen_final090.py')
classic=module('compile_classic',ROOT/'tools/classic132/native_compile.py')

class BuildChecks(unittest.TestCase):
    def test_private_store_provider_restored_after_failure(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp',prefix='classic-provider091-') as t:
            root=Path(t);probe=root/'probe';logs=root/'logs';logs.mkdir()
            source=probe/'bin/ddi/GOG.dll';source.parent.mkdir(parents=True);source.write_bytes(b'private provider fixture')
            with self.assertRaisesRegex(RuntimeError,'compile failed'):
                with classic.without_store_provider(probe,logs,True):
                    self.assertFalse(source.exists());self.assertTrue((logs/'GOG.dll.disabled').exists())
                    raise RuntimeError('compile failed')
            self.assertEqual(source.read_bytes(),b'private provider fixture')
            self.assertFalse((logs/'GOG.dll.disabled').exists())

    def test_editor_music_requires_verified_platform_cache(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp',prefix='menu-music092-') as t:
            root=Path(t);source=root/'scripts/game/betagwent/duelAudio.ws';source.parent.mkdir(parents=True)
            source.write_text('legacy audio','utf8');self.assertIsNone(build.menu_music_cache(root,'1.32'))
            source.write_text('bg_menu_music_play','utf8')
            with self.assertRaises(AssertionError):build.menu_music_cache(root,'1.32')
            folder=root/'menu-music-caches';folder.mkdir();classic=folder/'classic.cache';nextgen=folder/'nextgen.cache'
            classic.write_bytes(b'isolated classic fixture');nextgen.write_bytes(b'isolated nextgen fixture')
            manifest=folder/'manifest.json';manifest.write_text(json.dumps(dict(platforms={n:dict(cache=str(p),cacheSha256=build.sha(p)) for n,p in [('classic',classic),('nextgen',nextgen)]})),'utf8')
            self.assertEqual(build.menu_music_cache(root,'1.32'),classic)
            self.assertEqual(build.menu_music_cache(root,'5.0+'),nextgen)
            nextgen.write_bytes(b'changed fixture')
            with self.assertRaises(AssertionError):build.menu_music_cache(root,'5.0+')

    def compiler_run(self,success):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp',prefix='compiler091-') as t:
            root=Path(t);inp=root/'candidate';(inp/'scripts').mkdir(parents=True)
            (inp/'scripts/card.ws').write_text('class Card {}','utf8')
            exe=root/'redkit/bin/x64_RedKit/wcc_lite.exe';exe.parent.mkdir(parents=True);exe.write_bytes(b'not executed')
            class Process:
                returncode=None
                def poll(self):return self.returncode
                def kill(self):self.returncode=-9
                def wait(self,timeout):return self.returncode
            def start(*args,**kwargs):
                if success:
                    kwargs['stdout'].write((compiler.SUCCESS+'\n').encode());kwargs['stdout'].flush()
                    (inp/'compile-nextgen-final/compiled/blob.rsblob').write_bytes(b'fresh compiled blob')
                return Process()
            ticks=iter(range(1000))
            with patch.object(sys,'argv',['compiler','--input',str(inp),'--redkit',str(root/'redkit'),'--timeout','3']),patch.object(compiler.subprocess,'Popen',start),patch.object(compiler.time,'monotonic',lambda:next(ticks)),patch.object(compiler.time,'sleep',lambda _:None):
                with self.assertRaises(SystemExit) as result:compiler.main()
            record=json.loads((inp/'compile-nextgen-final/result.json').read_text('utf8'))
            return result.exception.code,record
    def test_verified_success_has_bounded_shutdown(self):
        code,r=self.compiler_run(True)
        self.assertEqual(code,0);self.assertTrue(r['terminatedAfterCompilerSuccess']);self.assertFalse(r['timedOut'])
        self.assertTrue(r['patchSourcesUnchangedDuringCompile'])
    def test_timeout_without_compiler_success_is_failure(self):
        code,r=self.compiler_run(False)
        self.assertEqual(code,1);self.assertTrue(r['timedOut']);self.assertFalse(r['completedByOutput'])
    def test_corrupt_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp',prefix='package091-') as t:
            p=Path(t)/'candidate.zip'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('payload',b'actual');z.writestr('manifest-0.9.1.json',json.dumps(dict(version='0.9.1',files=[dict(path='payload',bytes=6,sha256='wrong')])) )
            with self.assertRaises(AssertionError):build.verify_archive(p)

if __name__=='__main__':unittest.main()
