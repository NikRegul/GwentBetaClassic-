"""Keep the completed AI comparison valid only across the explicit Bran fix."""
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'))
from comparison_inputs import validate_snapshot

def comparison_compatibility(candidate_rules,experiment):
    old=experiment/'versions-00/candidate';new=Path(candidate_rules)
    a=validate_snapshot(old);b=validate_snapshot(new)
    changed=[n for n in a['files'].keys()|b['files'].keys() if a['files'].get(n)!=b['files'].get(n)]
    if not changed:return dict(comparisonFingerprint=a['fingerprint'],finalFingerprint=b['fingerprint'],samePolicy=True,rosterFix=None)
    catalog='BetaGwent/development/scripts/game/betagwent/duelCatalog.ws'
    assert changed==[catalog],('Comparison policy/source changed',changed)
    before=(old/'sources'/catalog).read_bytes();after=(new/'sources'/catalog).read_bytes()
    text=before.decode('utf-8-sig');match=re.search(r'function BetaGwentDuelPresetCards96\([^)]*\)\s*\{([^}]*)\}',text);assert match
    body=match.group(1);assert body.count('ids.PushBack(201773);')==1 and 'ids.PushBack(152109);' not in body
    expected=text[:match.start(1)]+body.replace('ids.PushBack(201773);','ids.PushBack(152109);')+text[match.end(1):]
    assert after==b'\xef\xbb\xbf'+expected.encode('utf8'),'Only the reviewed single-card roster change is allowed'
    return dict(comparisonFingerprint=a['fingerprint'],finalFingerprint=b['fingerprint'],samePolicy=True,
                rosterFix=dict(preset=96,removed=201773,added=152109,bulkComparisonUsesOldRoster=True))
