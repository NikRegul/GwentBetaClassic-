"""Restore unstaged files that differ from Git's index only by CRLF/LF.

Usage (folder defaults to the current directory, including subdirectories):
    python tools/recon/restore_eol_only.py . --dry-run
    python tools/recon/restore_eol_only.py .

Staged changes, untracked/deleted files, symlinks/reparse points, custom checkout
filters and encoding conversions are skipped. Spaces, BOM and the final newline
are significant. Binary files containing NUL are never EOL-normalized.
"""

import argparse
import os
from pathlib import Path
import stat
import subprocess
import sys


def git(root, *args, input=None):
    result = subprocess.run(
        ["git", "--literal-pathspecs", "-C", str(root), *args],
        input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def status(root, scope):
    raw = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=no",
              "--ignore-submodules=all", "--", scope)
    records = iter(raw.split(b"\0"))
    entries = {}
    for record in records:
        if not record:
            continue
        code = record[:2]
        entries[os.fsdecode(record[3:])] = code
        if b"R" in code or b"C" in code:
            next(records)  # Porcelain -z also contains the original path.
    return entries


def index_entries(root, scope):
    entries = {}
    for record in git(root, "ls-files", "--stage", "-z", "--", scope).split(b"\0"):
        if record:
            metadata, name = record.split(b"\t", 1)
            mode, oid, stage = metadata.split()
            if stage == b"0":
                entries[os.fsdecode(name)] = (mode, oid)
    return entries


def converted_paths(root, names):
    if not names:
        return set()
    raw = git(root, "check-attr", "-z", "--stdin", "filter", "working-tree-encoding",
              input=b"".join(os.fsencode(name) + b"\0" for name in names))
    fields = raw.split(b"\0")
    return {os.fsdecode(fields[i]) for i in range(0, len(fields) - 1, 3)
            if fields[i + 2] not in (b"unspecified", b"unset")}


def regular_file(root, name):
    path = root
    for part in Path(name).parts:
        path = path / part
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
        ):
            return False
    return stat.S_ISREG(info.st_mode)


def same_content(left, right):
    if left == right:
        return True
    return (b"\0" not in left and b"\0" not in right
            and left.replace(b"\r\n", b"\n") == right.replace(b"\r\n", b"\n"))


def restore(folder, dry_run=False):
    folder = Path(folder).resolve(strict=True)
    if not folder.is_dir():
        raise ValueError("Expected a folder: " + str(folder))
    root = Path(os.fsdecode(git(folder, "rev-parse", "--show-toplevel")).rstrip("\r\n"))
    scope = folder.relative_to(root).as_posix()
    states = status(root, scope)
    candidates = [name for name, code in states.items() if code == b" M"]
    entries = index_entries(root, scope)
    converted = converted_paths(root, candidates)
    filemode = git(root, "config", "--bool", "--default", "false", "core.filemode").strip() == b"true"
    restored = []
    skipped = 0
    for name in sorted(candidates):
        entry = entries.get(name)
        if (not entry or entry[0] not in (b"100644", b"100755")
                or name in converted or not regular_file(root, name)):
            skipped += 1
            continue
        path = root / name
        if filemode and bool(path.stat().st_mode & stat.S_IXUSR) != (entry[0] == b"100755"):
            skipped += 1
            continue
        current = path.read_bytes()
        original = git(root, "cat-file", "blob", entry[1].decode("ascii"))
        if not same_content(current, original):
            skipped += 1
            continue
        if not dry_run:
            # Recheck before discarding EOL changes in case an editor or git add ran.
            if (status(root, name).get(name) != b" M"
                    or index_entries(root, name).get(name) != entry
                    or not regular_file(root, name) or path.read_bytes() != current):
                raise RuntimeError("File changed during the check; stopped: " + name)
            git(root, "restore", "--worktree", "--", name)
            if status(root, name):
                raise RuntimeError("Git still reports a change after restore: " + name)
        restored.append(name)
        print(("WOULD RESTORE: " if dry_run else "RESTORED: ") + name, flush=True)
    print(f"{'Matched' if dry_run else 'Restored'}: {len(restored)}; "
          f"other unstaged modifications: {skipped}; "
          f"staged/deleted/other entries skipped: {len(states) - len(candidates)}")
    return restored


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", nargs="?", default=".", help="Folder to check recursively (default: .)")
    parser.add_argument("--dry-run", action="store_true", help="List matching files without restoring")
    args = parser.parse_args()
    try:
        restore(args.folder, args.dry_run)
    except (OSError, ValueError, RuntimeError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
