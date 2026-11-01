"""Exercise actual Git restores in an isolated repository, never the project."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

import restore_eol_only as tool


class RestoreEolChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="git-eol-check-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        tool.git(self.root, "init")
        tool.git(self.root, "config", "core.autocrlf", "false")
        tool.git(self.root, "config", "core.filemode", "false")
        self.write(".gitattributes", b"* -text\n")
        self.write("eol.txt", b"one\ntwo\n")
        self.write("bom.txt", b"\xef\xbb\xbfone\r\ntwo\r\n")
        self.write("real.txt", b"one\ntwo\n")
        self.write("space.txt", b"one\n")
        self.write("final.txt", b"one\n")
        self.write("binary.dat", b"\0one\ntwo\n")
        self.write("staged.txt", b"one\ntwo\n")
        self.write("deleted.txt", b"one\n")
        self.write("под папка/[x] файл.txt", b"one\ntwo\n")
        tool.git(self.root, "add", ".")
        tool.git(self.root, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "initial")

    def write(self, name, raw):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def run_tool(self, folder=None, dry_run=False):
        with contextlib.redirect_stdout(io.StringIO()):
            return tool.restore(folder or self.root, dry_run)

    def test_restore_only_eol_preserves_real_changes_and_staging(self):
        self.write("eol.txt", b"one\r\ntwo\r\n")
        self.write("bom.txt", b"\xef\xbb\xbfone\ntwo\n")
        self.write("real.txt", b"ONE\r\ntwo\r\n")
        self.write("space.txt", b"one \r\n")
        self.write("final.txt", b"one")
        self.write("binary.dat", b"\0one\r\ntwo\r\n")
        self.write("staged.txt", b"STAGED\ntwo\n")
        tool.git(self.root, "add", "staged.txt")
        self.write("staged.txt", b"STAGED\r\ntwo\r\n")
        self.write("untracked.txt", b"keep\r\n")
        (self.root / "deleted.txt").unlink()
        index_before = tool.git(self.root, "ls-files", "--stage", "-z")
        self.assertEqual(self.run_tool(), ["bom.txt", "eol.txt"])
        self.assertEqual((self.root / "bom.txt").read_bytes(), b"\xef\xbb\xbfone\r\ntwo\r\n")
        self.assertEqual((self.root / "eol.txt").read_bytes(), b"one\ntwo\n")
        states = tool.status(self.root, ".")
        self.assertNotIn("eol.txt", states)
        self.assertNotIn("bom.txt", states)
        for name in ("real.txt", "space.txt", "final.txt", "binary.dat"):
            self.assertEqual(states[name], b" M")
        self.assertEqual(states["staged.txt"], b"MM")
        self.assertEqual((self.root / "staged.txt").read_bytes(), b"STAGED\r\ntwo\r\n")
        self.assertEqual((self.root / "untracked.txt").read_bytes(), b"keep\r\n")
        self.assertFalse((self.root / "deleted.txt").exists())
        self.assertEqual(tool.git(self.root, "ls-files", "--stage", "-z"), index_before)

    def test_dry_run_then_recursive_folder_with_literal_unicode_filename(self):
        name = "под папка/[x] файл.txt"
        self.write(name, b"one\r\ntwo\r\n")
        self.write("eol.txt", b"one\r\ntwo\r\n")
        before = (self.root / name).read_bytes()
        self.assertEqual(self.run_tool(self.root / "под папка", dry_run=True), [name])
        self.assertEqual((self.root / name).read_bytes(), before)
        self.assertEqual(self.run_tool(self.root / "под папка"), [name])
        self.assertEqual((self.root / name).read_bytes(), b"one\ntwo\n")
        self.assertEqual((self.root / "eol.txt").read_bytes(), b"one\r\ntwo\r\n")

    def test_bom_and_bare_cr_are_significant(self):
        self.write("bom.txt", b"one\ntwo\n")
        self.write("eol.txt", b"one\rtwo\r")
        self.assertEqual(self.run_tool(), [])

    def test_custom_checkout_conversion_is_skipped(self):
        self.write(".gitattributes", b"* -text\neol.txt filter=custom\n")
        self.write("eol.txt", b"one\r\ntwo\r\n")
        self.assertEqual(self.run_tool(), [])
        self.assertEqual((self.root / "eol.txt").read_bytes(), b"one\r\ntwo\r\n")


if __name__ == "__main__":
    unittest.main()
