"""Prove that0.9.3c changes only decision methods, not shared card mechanics."""
from pathlib import Path
import argparse,json
import ws2js
from comparison_inputs import methods,validate_snapshot


def tokens(text):return [t.v for t in ws2js.lex(text)]


def classes(text):
    return {ws2js.head_name(block)[1]:text[block[0].pos:block[-1].pos+1] for block in ws2js.split_blocks(text)}


def declarations(text):
    for start,end in sorted(methods(text).values(),reverse=True):text=text[:start]+text[end:]
    return tokens(text)


def audit(candidate,baseline):
    candidate=Path(candidate);baseline=Path(baseline);fresh=validate_snapshot(candidate);old=validate_snapshot(baseline)
    name='BetaGwent/development/scripts/game/betagwent/duelSession.ws'
    changed_inputs=[n for n,h in fresh['files'].items() if old['files'].get(n)!=h]
    assert changed_inputs==[name],'Unexpected changes outside the session policy container'
    fresh_classes=classes((candidate/'sources'/name).read_text('utf-8-sig'));old_classes=classes((baseline/'sources'/name).read_text('utf-8-sig'))
    assert fresh_classes.keys()==old_classes.keys();changed=[]
    added={'AiLeaderSequencePlanning','AiSpyConcessionWindow'}
    allowed={'AiPreparationStep','AiCounterRisk','AiCriticalShortReply','OpponentStep'}
    for cls,new in fresh_classes.items():
        prior=old_classes[cls];assert declarations(new)==declarations(prior),'Non-method declarations changed: '+cls
        left=methods(prior);right=methods(new);assert not (left.keys()-right.keys()),'Deleted methods'
        for method,(start,end) in right.items():
            if method not in left:
                assert cls=='CBetaGwentDuelSession' and method in added;changed.append(cls+'.'+method);continue
            a,b=left[method]
            if tokens(new[start:end])!=tokens(prior[a:b]):
                assert cls=='CBetaGwentDuelSession' and method in allowed or cls=='CBetaGwentAISpy188' and method=='Step',cls+'.'+method
                changed.append(cls+'.'+method)
    assert len(changed)==7
    return dict(candidateFingerprint=fresh['fingerprint'],baselineFingerprint=old['fingerprint'],changedInputs=changed_inputs,
                changedPolicyMethods=changed,classDeclarationsUnchanged=True,cardMechanicsUnchanged=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    result=audit(a.candidate,a.baseline);a.output.write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result))
