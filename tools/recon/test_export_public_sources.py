"""Public export must reject unsafe inputs before touching the checkout."""
import contextlib
import gzip
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import export_public_sources as export


class ExportSafetyChecks(unittest.TestCase):
    def setUp(self):
        workspace = export.ROOT/'BetaGwent/build'
        workspace.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=workspace)
        self.assertTrue(Path(self.temp.name).resolve().is_relative_to(workspace.resolve()))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.public = self.root/'BetaGwent/publication'
        (self.public/'.git').mkdir(parents=True)
        self.sources = set()
        for name in ('README.md','LICENSE','ATTRIBUTIONS.md','.gitattributes',
                     'Build-0.9.3.cmd','Build-0.9.4.cmd','Build-0.9.4a.cmd','Build-0.9.5.cmd'):
            self.source(name, b'source\n')
        self.board = b'\xef\xbb\xbf// reviewed board\r\n'
        self.classic = b'\xef\xbb\xbf// reviewed classic board\r\n'
        for folder in ('src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'):
            self.source('BetaGwent/ui/'+folder+'/BetaGwentBoard.as', self.board)
        self.source('tools/features091/BetaGwentBoard_classic093.as', self.classic)
        gate = '\n'.join(hashlib.sha256(raw).hexdigest() for raw in (self.board,self.classic))
        self.source('tools/features091/prepare_ui091.py', gate.encode())

    def source(self, name, raw):
        p = self.root/name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
        self.sources.add(name)
        return p

    def run_export(self, *args):
        def files(directory, *options):
            if directory == self.root:
                return self.sources
            return set()
        with patch.object(export, 'ROOT', self.root), patch.object(export, 'PUBLIC', self.public), \
             patch.object(export, 'files', side_effect=files), \
             patch.object(export.subprocess, 'check_output', return_value='https://github.com/NikRegul/GwentBetaClassic-.git\n'), \
             patch('sys.argv', ['export_public_sources.py', *args]), contextlib.redirect_stdout(io.StringIO()):
            export.main()

    def test_compressed_secret_is_rejected_before_any_write(self):
        # Build the synthetic token at runtime so the test source itself is clean.
        token = 'gh'+'p_'+'x'*40
        self.source('tools/ai/fixtures/private.json.gz', gzip.compress((' {"token":"'+token+'"}').encode()))
        with self.assertRaisesRegex(AssertionError, 'Potential secret'):
            self.run_export('--apply')
        self.assertEqual(list(self.public.iterdir()), [self.public/'.git'])

    def test_unfinished_ui_is_rejected_before_any_write(self):
        self.source('BetaGwent/ui/src/BetaGwentBoard.as', b'// unfinished\n')
        with self.assertRaisesRegex(AssertionError, 'five Board copies'):
            self.run_export('--apply')
        self.assertEqual(list(self.public.iterdir()), [self.public/'.git'])

    def test_reviewed_snapshot_preserves_unfinished_local_work(self):
        local = self.source('BetaGwent/ui/src/BetaGwentBoard.as', b'// unfinished\n')
        snapshot = self.root/'reviewed-ui'
        snapshot.mkdir()
        (snapshot/'BetaGwentBoard.as').write_bytes(self.board)
        (snapshot/'BetaGwentBoard_classic093.as').write_bytes(self.classic)
        self.run_export('--apply', '--ui-snapshot', str(snapshot))
        self.assertEqual(local.read_bytes(), b'// unfinished\n')
        self.assertEqual((self.public/'BetaGwent/ui/src/BetaGwentBoard.as').read_bytes(), self.board)
        self.assertEqual((self.public/'tools/features091/BetaGwentBoard_classic093.as').read_bytes(), self.classic)

    def test_service_files_are_excluded_but_build_entrypoint_is_exported(self):
        private = ('AGENTS.md','docs/prompts/handoff.md','docs/agent-evaluation/result.md',
                   'docs/reviews/2026-11-01-space-audit.md','tools/recon/capture_capability_result.py',
                   'tools/saveprobe094/game_path.txt','tools/saveprobe094/last_result.txt')
        for name in private:
            self.source(name, b'local only\n')
        self.run_export('--apply')
        self.assertTrue((self.public/'Build-0.9.5.cmd').is_file())
        self.assertTrue(all(not (self.public/name).exists() for name in private))


if __name__ == '__main__':
    unittest.main()
