"""Verify saved-profile source delivery into both native compiler inputs.

Classic lowers @addField/@addMethod into playerWitcher.ws. Comparing only the
remaining betagwent file would miss almost all persistence logic.
"""
from pathlib import Path
import argparse, hashlib, json, sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/classic132'))
from prepare_scripts import read_source, extract_annotations
sys.path.insert(0,str(ROOT/'tools/features082'))
from package_classic132keg090 import RNG_OLD,RNG_NEW


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build',type=Path);parser.add_argument('report',type=Path)
    args=parser.parse_args();out=args.build.resolve();records=[]
    classic=out/'classic-prepared-final/Mods/modBetaGwentClassic132/content/scripts'
    injected_path=classic/'game/player/playerWitcher.ws';injected=read_source(injected_path)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    for name in ['deckProfile.ws','profileBackup.ws','collectionProfile.ws','deckBuilder.ws','profileCleanup090.ws']:
        canonical=ROOT/'BetaGwent/development/scripts/game/betagwent'/name;prepared=out/'scripts/game/betagwent'/name
        assert canonical.read_bytes()==prepared.read_bytes(),name
        remaining,blocks=extract_annotations(read_source(prepared),name)
        for block in blocks:
            text=block['text']
            if name=='collectionProfile.ws' and block['member']=='BetaGwentProgressionPick':
                old=RNG_OLD.replace('\r\n','\n');new=RNG_NEW.replace('\r\n','\n')
                assert text.count(old)==1;text=text.replace(old,new)
            assert text in injected,(name,block['member'])
        assert remaining.strip()==read_source(classic/'game/betagwent'/name).strip(),name
        records.append(dict(name=name,canonicalSha256=sha(canonical),preparedSha256=sha(prepared),classicInjectedMembersVerified=len(blocks),classicRemainingSourceVerified=True))
    report=dict(complete=True,records=records,classicPlayerPath=str(injected_path),classicPlayerSha256=sha(injected_path),
        classicProgressionRngAdapterPreserved=True,nativeGameplayVerified=False)
    args.report.write_text(json.dumps(report,indent=2)+'\n','utf8');print('PASS saved-profile native delivery:',sum(r['classicInjectedMembersVerified'] for r in records),'Classic members')


if __name__=='__main__':main()
