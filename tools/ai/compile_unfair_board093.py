"""Translate only the actual board coordinator, retaining common type info."""
from pathlib import Path
import argparse,hashlib,json,re
import ws2js,build_js
ROOT=Path(__file__).resolve().parents[2]

def main():
    p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    core=ROOT/'BetaGwent/scripts/game/betagwent';dev=ROOT/'BetaGwent/development/scripts/game/betagwent'
    files=sorted(core.glob('*.ws'))+[dev/(n+'.ws') for n in build_js.NAMES]+[dev/'deckBuilder.ws',dev/'developmentBoardMenu.ws']
    builder=(dev/'deckBuilder.ws').read_text('utf-8-sig');blocks=ws2js.split_blocks(builder)
    library=a.out/'deck-library-types.ws'
    library.write_text('\n'.join(builder[b[0].pos:b[-1].pos+1] for b in blocks if ws2js.head_name(b)[0] in ('class','struct','enum')),encoding='utf8')
    files[-2]=library
    text='\n'.join(f.read_text('utf-8-sig') for f in files)
    defined=set(re.findall(r'\b(?:class|struct|enum)\s+(\w+)',text))
    native=set(re.findall(r'\((\w+)\)',text))-defined-ws2js.PRIM
    native={n for n in native if n.startswith(('W3','C'))}
    stub=a.out/'engine-types.ws';stub.write_text('\n'.join('class '+n+' extends IScriptable {}' for n in sorted(native)),encoding='utf8')
    files.insert(0,stub)
    _,program=ws2js.build(files,sorted(dev.glob('*.ws')))
    program.order=[d for d in program.order if d.name=='CR4BetaGwentBoardMenu']
    code=ws2js.Emitter(program).program();(a.out/'board.js').write_text(code,encoding='utf8')
    flash=[n for n,t in program.classes['CR4BetaGwentBoardMenu'].fields if t=='CScriptedFlashFunction']
    (a.out/'manifest.json').write_text(json.dumps(dict(boardSourceSha256=hashlib.sha256((dev/'developmentBoardMenu.ws').read_bytes()).hexdigest(),flashFields=flash),indent=2)+'\n',encoding='utf8')
    print('Actual board coordinator translated;',len(flash),'Flash bindings')

if __name__=='__main__':main()
