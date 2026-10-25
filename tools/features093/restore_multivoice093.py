"""Restore the permanent five-language catalogue, retaining current RU fixes."""
from pathlib import Path
import argparse,hashlib,json,re,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'))
from comparison_inputs import methods


def main():
    p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args()
    baseline=ROOT/'BetaGwent/build-inputs/script-baseline/scripts/game/betagwent/duelAudioCatalog.ws'
    canonical=ROOT/'BetaGwent/development/scripts/game/betagwent/duelAudioCatalog.ws'
    old=baseline.read_text('utf-8-sig');ru=canonical.read_text('utf-8-sig')
    assert '_Universal_ru' not in ru,'Already restored; do not apply twice'
    left=methods(ru);right=methods(old);assert len(left)==88
    edits=[]
    for name,(start,end) in left.items():
        first,last=right[name+'_Universal_ru']
        body=ru[start:end]
        for called in sorted(left,key=len,reverse=True):
            body=re.sub(r'\b'+called+r'\b',called+'_Universal_ru',body)
        edits.append((first,last,body))
    for first,last,body in sorted(edits,reverse=True):old=old[:first]+body+old[last:]
    assert all('BetaGwentAudioVoiceVariant_Universal_'+lang in old for lang in ['ru','en','de','it','pt_br'])
    a.out.parent.mkdir(parents=True,exist_ok=True);assert not a.out.exists()
    a.out.write_bytes(b'\xef\xbb\xbf'+old.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))
    record=dict(baselineSha256=hashlib.sha256(baseline.read_bytes()).hexdigest(),currentRussianSha256=hashlib.sha256(canonical.read_bytes()).hexdigest(),
                restoredLanguages=['ru','en','de','it','pt-br'],russianFunctionsRetained=len(left),outputSha256=hashlib.sha256(a.out.read_bytes()).hexdigest())
    a.out.with_suffix('.provenance.json').write_text(json.dumps(record,indent=2)+'\n','utf8');print(json.dumps(record))


if __name__=='__main__':main()
