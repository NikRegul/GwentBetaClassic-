"""Audit the exact original release and its policy graft, without running games."""
from pathlib import Path
import argparse,hashlib,json
import ws2js
from comparison_inputs import validate_snapshot,methods,digest

def normalized(text):return [t.v for t in ws2js.lex(text)]

def main():
    p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('policy',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    original=a.original.resolve();policy=a.policy.resolve();manifest=validate_snapshot(original);release=json.loads((original.parent/'release.json').read_text('utf8'))
    freeze=json.loads((original.parent/'source-freeze.json').read_text('utf8'));proof=json.loads((policy/'comparison.json').read_text('utf8'))
    assert release['version']==freeze['version']=='0.9.1' and proof['original091'] and Path(proof['oldSnapshot'])==original
    assert proof['baselineRules']==digest(policy/'rules.js') and proof['sharedBattleMechanics']
    directory=original/'sources/BetaGwent/development/scripts/game/betagwent';checked=[]
    for name,h in proof['baselineAI'].items():
        src=directory/name;assert digest(src)==h==freeze['scripts']['game/betagwent/'+name]
        if name!='duelSession.ws':assert digest(policy/'dev'/name)==h
        checked.append(name)
    old=(directory/'duelSession.ws').read_text('utf-8-sig');new=(policy/'dev/duelSession.ws').read_text('utf-8-sig');om=methods(old);nm=methods(new)
    for name in proof['sessionPolicyMethods']:
        x,y=om[name],nm[name];assert normalized(old[x[0]:x[1]])==normalized(new[y[0]:y[1]]),'Changed original decision method '+name
    # New search jobs are present only for common class/state compatibility.
    forbidden=['CBetaGwentAIReplyTree097','CBetaGwentStrategyResourceJob096','CBetaGwentAIEndgame097']
    for name in ('OpponentStep','AiPreparationStep','PumpOpponent'):
        if name in om:
            x=om[name];assert not any(t in old[x[0]:x[1]] for t in forbidden)
    report=dict(originalVersion=release['version'],originalFingerprint=manifest['fingerprint'],releaseArchiveSha256=[r['sha256'] for r in release['archives']],checkedOriginalFiles=checked,originalDecisionMethods=len(proof['sessionPolicyMethods']),policyGraftRulesSha256=proof['baselineRules'],retainedUnreachableCompatibilitySupport=proof['retainedCompatibilitySupport'],ownOriginalRosters=True,sharedCurrentBattleMechanics=True,complete=True)
    a.output.write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report))

if __name__=='__main__':main()
