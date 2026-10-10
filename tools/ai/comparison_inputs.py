"""Validate immutable snapshots and isolate decision methods from battle mechanics."""
import hashlib, json
from pathlib import Path
import ws2js

POLICY_HELPERS = set('''ModeValue BestModeChoice ChooseDagonWeather BestNestedRow
BestDeployRow BestCardRow EvaluateCardRow DeckSummonValue ConsumePassiveValue
RallyValue DeckCopiesValue ChooseFirstLight WeatherValue BestWeatherRow BestOwnRow
DamageValue LockToggleValue TargetValue RowEffectValue BestEnemyRow BestTarget
BestEffectValue EpidemicValue BestVranAnchor OpponentStep PumpOpponent'''.split())

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate_snapshot(directory):
    directory=Path(directory)
    manifest=json.loads((directory/'manifest.json').read_text('utf-8-sig'))
    if manifest['schema'] != 2 or len(set(manifest['presets'])) != 46:
        raise ValueError('Expected a schema 2 snapshot with 46 archetypes: '+str(directory))
    for name, expected in manifest['snapshotFiles'].items():
        if digest(directory/name) != expected:
            raise ValueError('Snapshot file changed: '+str(directory/name))
    return manifest

def methods(source):
    """Use WS tokens so braces in quoted strings/comments cannot cut a method."""
    tokens=ws2js.lex(source); result={};i=0
    while i<len(tokens):
        if tokens[i].v!='function': i+=1;continue
        name=tokens[i+1].v;start=i
        while start>0 and tokens[start-1].v in ws2js.MODS: start-=1
        j=i+2
        while tokens[j].v not in ('{',';'): j+=1
        if tokens[j].v=='{':
            depth=1;j+=1
            while depth:
                if tokens[j].v=='{':depth+=1
                elif tokens[j].v=='}':depth-=1
                j+=1
        else:j+=1
        result[name]=(tokens[start].pos,tokens[j-1].pos+1)
        i=j
    return result

def graft_policy(current, old):
    new_methods=methods(current);old_methods=methods(old);replacements=[];copied=[]
    for name,(start,end) in new_methods.items():
        if (name.startswith('Ai') or name in POLICY_HELPERS) and name in old_methods:
            a,b=old_methods[name];replacements.append((start,end,old[a:b]));copied.append(name)
    if 'OpponentStep' not in copied:raise ValueError('Old snapshot lacks OpponentStep')
    # Current fields and all non-policy functions are retained for common state/rules.
    for start,end,text in sorted(replacements,reverse=True):current=current[:start]+text+current[end:]
    missing=[n for n in old_methods if (n.startswith('Ai') or n in POLICY_HELPERS) and n not in new_methods]
    if missing:
        at=current.rfind('}')
        current=current[:at]+'\n'+ '\n'.join(old[a:b] for n in missing for a,b in [old_methods[n]])+'\n'+current[at:]
        copied+=missing
    return current, sorted(copied)
