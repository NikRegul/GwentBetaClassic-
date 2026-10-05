"""Stage the accepted-by-compiler UI bytes for external-texture packaging.

No gameplay or ActionScript changes: retain the stage95 bytecode and artwork.
The release preparer externalizes the shipping copies, preserving REDkit files.
"""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((ROOT/'docs/evidence/stage95-completion.json').read_text('utf8'))
assert len(old['menus'])==3 and all(m['language']=='ru' for m in old['menus'])
for name,digest in old['sources'].items():
    assert sha(ROOT/'BetaGwent/ui/src'/name)==digest,'UI source changed: '+name
menus=[]
for m in old['menus']:
    source=Path(m['resource']);assert sha(source)==m['sha256']
    target=ROOT/'BetaGwent/build/stage96/ru/resources'/source.name
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    menus.append(dict(m,resource=str(target),sha256=sha(target)))
result=dict(old,stage=96,menus=menus,derivedFromStage=95,
            shippingExternalTextures=True,actionScriptRecompiled=False,
            nativeRuntimeVerified=False,installedGameModified=False)
(ROOT/'docs/evidence/stage96-completion.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
print('3 unchanged RU menus staged; external textures will be built in shipping workspace only.')
