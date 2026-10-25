"""Translate staged typed WS components for parity against the direct JS port."""
import argparse, hashlib, json
from pathlib import Path
import ws2js

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('rules',type=Path);a=p.parse_args()
    sources=sorted(a.directory.glob('*.ws'))
    extra=sorted((a.rules/'sources/BetaGwent/scripts/game/betagwent').glob('*.ws'))
    extra+=sorted((a.rules/'sources/BetaGwent/development/scripts/game/betagwent').glob('*.ws'))
    code,program=ws2js.build(sources,extra)
    # Keep common struct type information for copying/type resolution, but the
    # common engine already declares these types in the parity test context.
    local_names={ws2js.head_name(b)[1] for p in sources for b in ws2js.split_blocks(p.read_text('utf-8-sig'))}
    program.order=[d for d in program.order if d.name in local_names]
    code=ws2js.Emitter(program).program()
    (a.directory/'ws-stage.js').write_text(code,encoding='utf8')
    report=dict(scope='Staged component parity; not integrated game difficulty',
                sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                rules=str(a.rules),compiledSha256=hashlib.sha256(code.encode('utf8')).hexdigest(),
                nativeCompiled=False,typedModuleFloat32Arithmetic=True,classes=len(program.classes),functions=len(program.functions))
    (a.directory/'ws-stage-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report))


if __name__=='__main__':main()
