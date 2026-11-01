"""Recognize the reviewed partial-node guards and audited whole-request mapping.

The historical mapping and its parity/source proof stay byte-for-byte intact.
Reverse exact edits and require the original published source digest.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def choice_amendment(build,path,digest,raw=None):
    before=b'wholeSet=((source==200159 || source==162103 || source==200163 || source==162316 || source==200227 || source==201616 || source==122204 || source==200209) && request.kind=="choices") || (source==200218 && request.kind=="targets");'
    after=b'wholeSet=((source==200159 || source==162103 || source==200163 || source==162316 || source==200227 || source==201616 || source==122204 || source==200209 || source==122201 || source==152205) && request.kind=="choices") || ((source==200218 || source==162208 || source==200169 || source==152315 || source==112111 || source==152203) && request.kind=="targets");'
    if raw is None:raw=path.read_bytes()
    assert raw.count(after)==1,'Reviewed whole-request context changed'
    assert hashlib.sha256(raw.replace(after,before,1)).hexdigest()==digest,'Other Choices edits require separate review'
    fingerprint=json.loads((Path(build)/'rules/manifest.json').read_text('utf8'))['fingerprint']
    evidence=[]
    for name,count,cases,ids in [
        ('audit_whole_requests096',112,12,{162208,200169}),
        ('audit_batch80_requests096',500,54,{122201,152205,152315,112111,152203})]:
        report=Path(build)/'regressions'/(name+'.json');result=json.loads(report.read_text('utf8'))
        assert result['fingerprint']==fingerprint and not result['failures'] and result['checks']>=count
        assert len(result['cases'])>=cases and {r['id'] for r in result['cases']}==ids
        assert {r['side'] for r in result['cases']}=={1,2}
        evidence.append(dict(path='regressions/'+name+'.json',sha256=sha(report)))
    return dict(path=path.name,historicalSha256=digest,currentSha256=sha(path),
        exactReversePatchMatchesHistoricalSource=True,regressions=evidence,
        reason='Map the seven independently audited multi-card requests as one stored set before effects; preserve selected profiles and historical proof.')

REVIEWED097=ROOT/'tools/ai/reviewed097_original_reactions.json'
def reverse097(name,raw):
    """0.9.5 (29.10.2026): the other seat's reactive request (Standard Bearer) in the
    original-AI search, live wait/answer (CBetaOriginalReaction). Exact reviewed hunks."""
    hunks=json.loads(REVIEWED097.read_text('utf8')).get(name)
    if not hunks or raw.count(hunks[0][0].encode('utf8'))!=1:return raw,False
    for after,before in hunks:
        after=after.encode('utf8');before=before.encode('utf8')
        assert raw.count(after)==1,'Reviewed 097 reaction context changed: '+name
        raw=raw.replace(after,before,1)
    return raw,True
def evidence097(build):
    fingerprint=json.loads((Path(build)/'rules/manifest.json').read_text('utf8'))['fingerprint']
    report=Path(build)/'regressions/check_bearer097.json';result=json.loads(report.read_text('utf8'))
    assert result['fingerprint']==fingerprint and not result['failures'] and result['checks']>=6
    return [dict(path='regressions/check_bearer097.json',sha256=sha(report))]
def amendments(build,proof):
    frozen=Path(build)/'rules/sources/BetaGwent/development/scripts/game/betagwent'
    changes=[]
    for name,digest in proof['wsSources'].items():
        path=frozen/name
        if sha(path)==digest:continue
        if name in ('betaOriginalChoices.ws','betaOriginalController.ws'):
            raw,changed097=reverse097(name,path.read_bytes())
            if changed097:
                changes.append(dict(path=name,step='reactions097',currentSha256=sha(path),regressions=evidence097(build),
                    reason='Other-seat reactive request: simulated by the reacting seat handler (no record/branch/score); live replay waits; AI answers its own reaction during the player turn.'))
            if name=='betaOriginalController.ws':
                assert hashlib.sha256(raw).hexdigest()==digest,'Other Controller edits require separate review';continue
            if hashlib.sha256(raw).hexdigest()==digest:continue
            changes.append(choice_amendment(build,path,digest,raw));continue
        assert name=='betaOriginalPlayMaker.ws','Unreviewed selected-profile source change: '+name
        raw=path.read_bytes();restored=raw
        for before,after in [
          (b'node=root.children[i];if(node.cardId==0 || !node.hasState)continue;',
           b'node=root.children[i];if(node.status!=1 || !node.hasState || node.cardId==0)continue;\r\n            card='),
          (b'node=root.children[i];if(node.cardId==0)continue;value=OriginalDiff(node);if(failed)return;',
           b'node=root.children[i];if(node.status!=1 || !node.hasState || node.cardId==0)continue;value=OriginalDiff(node);if(failed)return;')]:
            assert restored.count(after)==1,'Reviewed guard context changed'
            replacement=before+(b'\r\n            card=' if after.endswith(b'card=') else b'')
            restored=restored.replace(after,replacement,1)
        assert hashlib.sha256(restored).hexdigest()==digest,'Other PlayMaker edits require separate review'
        regression=Path(build)/'regressions/check_classic_partial094.json'
        result=json.loads(regression.read_text('utf8'))
        fingerprint=json.loads((Path(build)/'rules/manifest.json').read_text('utf8'))['fingerprint']
        assert result['fingerprint']==fingerprint and not result['failures'] and result['checks']>=2500
        assert result['peakMutations']<=1 and len(result['records'])==8
        changes.append(dict(path=name,historicalSha256=digest,currentSha256=sha(path),
            exactReversePatchMatchesHistoricalSource=True,regression='regressions/check_classic_partial094.json',
            regressionSha256=sha(regression),reason='Skip unfinished/error root candidates in low-tempo and non-detrimental PlayMaker scans.'))
    return changes
