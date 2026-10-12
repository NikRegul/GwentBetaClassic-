"""Read-only logical/allocated disk inventory for the cleanup review (no deletion)."""
import ctypes
import json
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    sizes = defaultdict(lambda: [0, 0, 0])
    errors = []
    largest = []
    seen = set()
    for directory, folders, files in os.walk(ROOT, followlinks=False):
        folders[:] = [f for f in folders if not Path(directory, f).is_symlink()]
        for name in files:
            path = Path(directory, name)
            try:
                stat = path.stat(follow_symlinks=False)
                if path.is_symlink():
                    continue
                relative = path.relative_to(ROOT)
                identity = (stat.st_dev, stat.st_ino)
                unique = stat.st_size if identity not in seen else 0
                seen.add(identity)
                for depth in range(1, min(4, len(relative.parts)) + 1):
                    key = '/'.join(relative.parts[:depth])
                    sizes[key][0] += stat.st_size
                    sizes[key][1] += unique
                    sizes[key][2] += 1
                if stat.st_size >= 200_000_000:
                    largest.append({'path': str(relative), 'bytes': stat.st_size,
                                    'hardlinks': stat.st_nlink})
            except OSError as error:
                errors.append({'path': str(path), 'error': str(error)})
    report = {'root': str(ROOT), 'kind': 'read-only',
              'note': 'Logical bytes; unique bytes count hard links once. Actual reclaimed disk space depends on remaining links and compression.',
              'paths': {k: {'bytes': v[0], 'uniqueBytes': v[1], 'files': v[2]}
                        for k, v in sorted(sizes.items(), key=lambda item: -item[1][0])},
              'largestFiles': sorted(largest, key=lambda item: -item['bytes']), 'errors': errors}
    target = ROOT / 'docs/evidence/project-space137.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print('Inventory saved:', target)
    for key, row in report['paths'].items():
        if key.count('/') <= 1 and row['bytes'] >= 100_000_000:
            print(f"{row['bytes']/1024**3:8.2f} GiB  {key}  ({row['files']} files)")
    print('Read errors:', len(errors))


if __name__ == '__main__':
    main()
