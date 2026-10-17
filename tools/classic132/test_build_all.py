"""Exercise release orchestration against tiny real ZIPs, without running compilers."""
from contextlib import nullcontext,redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import build_all as batch
sys.path.insert(0,str(batch.ROOT/'tools'))
import build_voice_packages168 as nextgen


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.test_root=Path(__file__).resolve().parents[2]/'tmp/classic132-tests'
        self.test_root.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=self.test_root);self.addCleanup(self.cleanup)
        self.root=Path(self.temp.name);self.stage=201;self.version='0.8.0'
        self.scope=patch.object(batch,'ROOT',self.root);self.scope.start();self.addCleanup(self.scope.stop)
        (self.root/'BetaGwent/release').mkdir(parents=True)

    def cleanup(self):
        # Validate the absolute workspace target before recursive temporary cleanup.
        assert Path(self.temp.name).resolve().is_relative_to(self.test_root.resolve())
        self.temp.cleanup()

    def source(self):
        ru=self.root/'BetaGwent/release/GwentBetaClassic-0.8.0-RU.zip'
        with zipfile.ZipFile(ru,'w') as z:z.writestr('manifest.json',json.dumps(dict(version=self.version,stage=self.stage,language='ru')))
        for language in batch.VOICES:
            p=self.root/f'BetaGwent/build/release{self.stage}/{language}/package/manifest.json'
            p.parent.mkdir(parents=True);p.write_text(json.dumps({'voice':language}))

    def classic(self,voice,**override):
        path=batch.archive_path(self.version,voice);data=('voice '+voice).encode()
        manifest=dict(version=self.version,sourceVersion=self.version,sourceStage=self.stage,gameVersion='1.32',voiceLanguage=voice,
                      nativeCompilationPassed=True,textLanguages=list(range(13)),guiLimitMiB=63,
                      generators=batch.generator_hashes(),
                      files=[dict(path='payload.txt',bytes=len(data),sha256=hashlib.sha256(data).hexdigest())])
        src=self.root/f'BetaGwent/build/release{self.stage}/{voice}/package/manifest.json'
        if src.exists():manifest['sourceManifestSha256']=batch.sha(src)
        manifest.update(override)
        with zipfile.ZipFile(path,'w') as z:
            z.writestr('payload.txt',data);z.writestr('manifest.json',json.dumps(manifest))
        path.with_suffix('.zip.sha256').write_text(batch.sha(path)+'  '+path.name+'\n')
        return path

    def test_check_only_does_not_build_or_create_outputs(self):
        with patch.object(batch,'run') as run,redirect_stdout(io.StringIO()):plan=batch.main(['--check-only'])
        run.assert_not_called();self.assertIsNone(plan['sourceStage']);self.assertFalse((self.root/'BetaGwent/build').exists())
        self.assertEqual(plan['voices'],list(batch.VOICES));self.assertFalse(plan['installsGame'])

    def test_stage_is_pinned_to_ru_archive(self):
        self.source();self.assertEqual(batch.resolve_stage(self.version,0),self.stage)
        with self.assertRaises(ValueError):batch.resolve_stage(self.version,202)

    def test_all_five_targets_share_only_menus_and_resources(self):
        self.source();commands=[]
        def run(*args):
            commands.append(args)
            if str(args[0]).endswith('build_voice_packages168.py'):
                self.assertIn('--verify',args);return
            voice=args[args.index('--language')+1];out=Path(args[args.index('--out')+1])
            for name in ['menus/menus.json','resources-classic/resources.json']:
                p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{}')
            self.classic(voice)
        with patch.object(batch,'run',side_effect=run),patch.object(batch,'presentation_lock',nullcontext),redirect_stdout(io.StringIO()):
            (self.root/'docs/evidence').mkdir(parents=True)
            result=batch.main([])
        self.assertEqual(len(result),5);self.assertEqual(len(commands),6)
        builds=commands[1:];self.assertNotIn('--menus',builds[0])
        for language,command in zip(batch.VOICES,builds):
            self.assertEqual(command[command.index('--language')+1],language)
            self.assertEqual(command[command.index('--source-stage')+1],self.stage)
            self.assertIn('--release',command);self.assertEqual(command[command.index('--gui-limit-mib')+1],63)
            if language!='ru':self.assertIn('--menus',command);self.assertIn('--resources',command)
        # A second run verifies the existing archives and never invokes a Classic compiler.
        with patch.object(batch,'run') as run,patch.object(batch,'presentation_lock',nullcontext),redirect_stdout(io.StringIO()):batch.main([])
        self.assertEqual(run.call_count,1);self.assertIn('--verify',run.call_args.args)

    def test_verify_does_not_build_missing_classic(self):
        self.source()
        with patch.object(batch,'run') as run,redirect_stdout(io.StringIO()),self.assertRaises(FileNotFoundError):batch.main(['--verify'])
        run.assert_not_called()

    def test_wrong_voice_and_corrupt_payload_are_rejected(self):
        p=self.classic('de',voiceLanguage='ru')
        with self.assertRaises(ValueError):batch.verify_zip(p,self.version,'de',self.stage)
        p=self.classic('de')
        with zipfile.ZipFile(p,'a') as z:z.writestr('unexpected.txt','extra')
        with self.assertRaises(ValueError):batch.verify_zip(p,self.version,'de',self.stage)

    def test_payload_hash_is_checked_independently_of_zip_crc(self):
        p=self.classic('en')
        with zipfile.ZipFile(p) as z:manifest=z.read('manifest.json')
        with zipfile.ZipFile(p,'w') as z:
            z.writestr('payload.txt',b'changed');z.writestr('manifest.json',manifest)
        p.with_suffix('.zip.sha256').write_text(batch.sha(p)+'  '+p.name+'\n')
        with self.assertRaisesRegex(ValueError,'payload mismatch'):batch.verify_zip(p,self.version,'en',self.stage)

    def test_existing_archive_from_different_generators_cannot_join_new_batch(self):
        p=self.classic('ru')
        with self.assertRaisesRegex(ValueError,'generators changed'):
            batch.verify_zip(p,self.version,'ru',self.stage,generators={'new-adapter.py':'new-hash'})

    def test_existing_archive_with_different_source_manifest_is_rejected(self):
        self.source();p=self.classic('ru')
        with self.assertRaisesRegex(ValueError,'source manifest changed'):
            batch.verify_zip(p,self.version,'ru',self.stage,source_manifest='changed')

    def test_frozen_gui_budgets_remain_compatible_but_explicit_mismatch_fails(self):
        self.assertEqual(nextgen.gui_budget(None),63)
        self.assertEqual(nextgen.gui_budget(None,65),65)
        self.assertEqual(nextgen.gui_budget(63,63),63)
        with self.assertRaises(ValueError):nextgen.gui_budget(63,65)
        for value in [0,66]:
            with self.assertRaises(ValueError):nextgen.gui_budget(value)


if __name__=='__main__':unittest.main()
