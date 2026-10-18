"""Inventory obsolete RC archives and memory dumps explicitly authorized for removal."""
from pathlib import Path
import json,subprocess

ROOT=Path(__file__).resolve().parents[2]

def main():
    build=ROOT/'BetaGwent/build/release082-final'
    audit=json.loads((build/'final-audit.json').read_text('utf8'))
    assert len(audit)==2 and all(Path(v['archive']['path']).is_file() for v in audit)
    found=subprocess.run(['rg','--files','--hidden','--no-ignore','-g','*.dmp','-g','*.mdmp','-g','*.hdmp','-g','!**/.git/**'],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
    assert found.returncode in [0,1]
    candidates=[(ROOT/p,'obsolete-memory-dump; user authorized fresh captures if needed') for p in found.stdout.splitlines() if p]
    for revision in ['rc1','rc2','rc3']:
        for platform in ['1.32','5.0+']:
            archive=ROOT/f'BetaGwent/release/GwentBetaClassic-0.8.2-{revision}-{platform}-AllLanguages.zip'
            for p in [archive,archive.with_suffix('.zip.sha256')]:
                if p.exists():candidates.append((p,'superseded by verified full 0.8.2 archive'))
    rows=[]
    for path,reason in candidates:
        absolute=path.resolve()
        assert absolute.is_relative_to(ROOT) and path.is_file() and not path.is_symlink() and '.git' not in path.parts
        rows.append(dict(path=str(absolute),relative=absolute.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,modifiedNs=path.stat().st_mtime_ns,reason=reason))
    assert len({r['path'] for r in rows})==len(rows)
    report=dict(root=str(ROOT),status='planned',files=rows,totalBytes=sum(r['bytes'] for r in rows),sourceAndSaveFilesIncluded=False)
    destination=ROOT/'docs/releases/0.8.2/CLEANUP.json';destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(dict(files=len(rows),memoryDumps=sum('memory-dump' in r['reason'] for r in rows),bytes=report['totalBytes'],GiB=round(report['totalBytes']/1024**3,3),manifest=str(destination)),ensure_ascii=False))

if __name__=='__main__':main()
