"""Make DE/IT/PT-BR copies of the RU Wwise project with Beta voice WAVs. No bank generation; never touches wwise/ or wwise-en89/."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'BetaGwent/audio/wwise'
OUT=ROOT/'BetaGwent/build/languages137/wwise'
SKIP={'GeneratedSoundBanks','Originals','.cache','.backup','Logs'}
WAVS='Originals/SFX/BetaGwent79'
import sys
def put(a,b):
    if b.is_file() and b.stat().st_size==a.stat().st_size: return
    shutil.copy2(a,b)
def main():
    rp=OUT/'report.json'; report=json.loads(rp.read_text('utf8')) if rp.is_file() else {}
    for loc,folder in [x for x in [('de_de','wwise-de'),('it_it','wwise-it'),('pt_br','wwise-ptbr')] if x[0] in sys.argv[1:]]:
        dst=OUT/folder; dst.mkdir(parents=True,exist_ok=True)
        for p in SRC.rglob('*'):
            rel=p.relative_to(SRC)
            if rel.parts[0] in SKIP or p.is_dir() or p.suffix=='.validationcache': continue
            t=dst/rel; t.parent.mkdir(parents=True,exist_ok=True); put(p,t)
        (dst/WAVS).mkdir(parents=True,exist_ok=True)
        voice=ROOT/'BetaGwent/build/languages137/voice'/loc/'wav'
        fx=vo=0;missing=[]
        for p in sorted((SRC/WAVS).iterdir()):
            if p.name.startswith('vo_'):
                q=voice/p.name
                if not q.is_file(): missing.append(p.name); q=p
                put(q,dst/WAVS/p.name); vo+=1
            else:
                put(p,dst/WAVS/p.name); fx+=1
        changed=sum(1 for p in (dst/WAVS).glob('vo_*') if p.stat().st_size!=(SRC/WAVS/p.name).stat().st_size)
        report[loc]={'folder':str(dst.relative_to(ROOT)),'files':fx+vo,'voice':vo,'other':fx,'voiceDifferentSize':changed,'missingKeptRu':missing}
        assert fx+vo==len(list((SRC/WAVS).iterdir())) and not missing
    rp.write_text(json.dumps(report,indent=1,ensure_ascii=False),'utf8')
    print(json.dumps(report,indent=1))
main()
