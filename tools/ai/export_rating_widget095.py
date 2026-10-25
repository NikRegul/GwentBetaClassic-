"""Embed compact verified tournament data in the literal inline fragment."""
import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def main():
    p=argparse.ArgumentParser();p.add_argument('ratings',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    report=json.loads(a.ratings.read_text('utf8'));assert report['complete'] and report['errors']==0
    compact={'names':{},'levels':{}}
    rounded=lambda value:round(value,5)
    for strength,level in report['levels'].items():
        rows=[];matchups={}
        assert len(level['decks'])==46
        for d in level['decks']:
            compact['names'][d['id']]={'title':d['title'],'faction':d['faction'],'leader':d['leader']}
            rows.append([d['id'],d['rank'],d['games'],d['wins'],d['draws'],rounded(d['score']),*map(rounded,d['ci95'])])
            assert len(d['matchups'])==45
            matchups[d['id']]=[[m['opponent'],m['games'],m['wins'],m['draws'],rounded(m['score']),*map(rounded,m['ci95'])] for m in d['matchups']]
        compact['levels'][strength]={'games':level['games'],'gamesPerPair':level['gamesPerPair'],'rows':rows,'matchups':matchups}
    template=(ROOT/'tools/ai/templates/deck-rating095.html').read_text('utf8')
    assert template.count('__RATING_DATA__')==1
    payload=json.dumps(compact,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    html=template.replace('__RATING_DATA__',payload)
    assert len(html.encode('utf8'))<1_000_000 and '<html' not in html and '<!doctype' not in html
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(html,'utf8')
    print(json.dumps({'path':str(a.output.resolve()),'bytes':a.output.stat().st_size,'decks':46,'levels':len(compact['levels'])}))

if __name__=='__main__':main()
