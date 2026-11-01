"""Negative controls for the narrowly reviewed source-provenance amendment."""
from pathlib import Path
import argparse,json,shutil
from profile_provenance094 import amendments,ROOT

def main():
    parser=argparse.ArgumentParser();parser.add_argument('build',type=Path);parser.add_argument('out',type=Path);a=parser.parse_args()
    assert not a.out.exists();a.out.mkdir(parents=True)
    proof=json.loads((ROOT/'data/beta924/design/beta_ai_profiles093-source-proof.json').read_text('utf8'))
    assert len(amendments(a.build,proof))==1
    records=[dict(case='exact-reviewed-amendment',passed=True)]
    for name,mutate in [
      ('unrelated-method-change',lambda p:p.write_bytes(p.read_bytes()+b'\r\n// unreviewed change\r\n')),
      ('changed-guard',lambda p:p.write_bytes(p.read_bytes().replace(b'node.status!=1',b'node.status!=2',1))),
      ('different-port-file',None)]:
        folder=a.out/name;source=Path('rules/sources/BetaGwent/development/scripts/game/betagwent')
        shutil.copytree(a.build/source,folder/source)
        (folder/'regressions').mkdir()
        shutil.copy2(a.build/'regressions/check_classic_partial094.json',folder/'regressions/check_classic_partial094.json')
        shutil.copy2(a.build/'rules/manifest.json',folder/'rules/manifest.json')
        if mutate:mutate(folder/source/'betaOriginalPlayMaker.ws')
        else:
            path=folder/source/'betaOriginalSearch.ws';path.write_bytes(path.read_bytes()+b'\r\n// unreviewed\r\n')
        rejected=False
        try:amendments(folder,proof)
        except AssertionError:rejected=True
        assert rejected,name
        records.append(dict(case=name,passed=True,unreviewedInputRejected=True))
    result=dict(complete=True,checks=len(records),records=records,historicalProofUnchanged=True)
    (a.out/'report.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result))

if __name__=='__main__':main()
