"""Limit only this strategy experiment's running processes and descendants."""
from pathlib import Path
import argparse, json, os
import psutil

ROOT = Path(__file__).resolve().parents[2]
PROJECT = str(ROOT/'BetaGwent/drafts/ai-planning097-20261021').lower().replace('\\','/')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cpus',default='0,2,4,6')
    args=parser.parse_args();cpus=[int(x) for x in args.cpus.split(',')]
    processes={p.pid:p for p in psutil.process_iter()}
    selected=set()
    for pid,p in processes.items():
        if pid==os.getpid():continue
        try:
            if p.name().lower() not in ('python.exe','node.exe','wcc_lite.exe','witcher3.exe','pwsh.exe','powershell.exe'):continue
            command=' '.join(p.cmdline()).lower().replace('\\','/')
            cwd=p.cwd().lower().replace('\\','/')
            if cwd.startswith(PROJECT) or ('ai-planning097-20261021' in command and ('d:/w3mod' in command or cwd.startswith(str(ROOT).lower().replace('\\','/')))):
                selected.add(pid)
        except (psutil.AccessDenied,psutil.NoSuchProcess):pass
    for pid in list(selected):
        try:selected.update(p.pid for p in processes[pid].children(recursive=True))
        except (psutil.AccessDenied,psutil.NoSuchProcess):pass
    rows=[]
    for pid in sorted(selected):
        try:
            p=psutil.Process(pid);prior=p.cpu_affinity();p.cpu_affinity(cpus)
            rows.append(dict(pid=pid,name=p.name(),before=prior,after=p.cpu_affinity()))
        except psutil.NoSuchProcess:pass
    report=dict(logicalProcessors=psutil.cpu_count(),sharedCpuSet=cpus,processes=rows)
    out=ROOT/'BetaGwent/build/ai-planning097-20261021/cpu-limit.json'
    out.write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(dict(logicalProcessors=report['logicalProcessors'],sharedCpuSet=cpus,limitedProcesses=len(rows))))

if __name__=='__main__':main()
