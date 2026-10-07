"""Match original line endings: unchanged files get original bytes; changed files use the original's dominant EOL."""
import sys
from pathlib import Path
orig, work = Path(sys.argv[1]), Path(sys.argv[2])
for p in work.rglob('*.ws'):
    o = orig / p.relative_to(work)
    if not o.exists(): continue
    ob = o.read_bytes(); wb = p.read_bytes()
    if ob.replace(b'\r\n', b'\n') == wb.replace(b'\r\n', b'\n'):
        if ob != wb: p.write_bytes(ob)
        continue
    crlf = ob.count(b'\r\n'); lf = ob.count(b'\n') - crlf
    t = wb.replace(b'\r\n', b'\n')
    if crlf > lf: t = t.replace(b'\n', b'\r\n')
    if t != wb: p.write_bytes(t); print('eol', p.relative_to(work), 'crlf' if crlf > lf else 'lf')
