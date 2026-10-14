"""Validate isolated atlas downsampling and every logical cell's sampling bounds."""
from pathlib import Path
import json,sys,re,hashlib
from PIL import Image
profile=json.loads(Path(sys.argv[1]).read_text('utf8'));root=Path(profile['sourceDir']).parent
checks=0
def check(value,message):
    global checks
    if not value:raise AssertionError(message)
    checks+=1
for item in profile['assets']:check(hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256'],'Asset digest')
for item in profile['reduced']:
    im=Image.open(root/'assets/special144'/item['file'])
    check(list(im.size)==item['after'],'Reduced extent');check([v*2 for v in im.size]==item['before'],'Exact half resolution')
    check(im.mode=='RGBA' and im.getchannel('A').getextrema()[0]<255,'Transparency preserved')
    if item['file'].startswith('kill'):
        count=32 if item['file']=='kill_beta.png' else 16
        for i in range(count):
            x=(i%8)*64;y=(i//8)*64
            check(x+64<=im.width and y+64<=im.height,'Kill cell stays inside reduced sheet')
    else:
        for kind in range(7):
            for i in range(4):
                x=y=0;w=h=128
                if kind==0:x=i*128;h=256
                elif kind==1:x=i*128;y=256;h=64
                elif kind==2:x=i*64;y=320;w=h=64
                elif kind==3:x=256;y=320
                elif kind==4:x=384;y=320
                elif kind==5:x=0;y=384
                else:x=128;y=384
                check((x+w)/2<=im.width and (y+h)/2<=im.height,'Lightning cell stays inside reduced sheet')
for name in ('BetaGwentKillArt144.as','BetaGwentLightning144.as'):
    text=(root/'src'/name).read_text('utf-8-sig');check(text.count('bitmap.scaleX=2;bitmap.scaleY=2;')==1,'Logical dimensions restored once')
print(json.dumps(dict(passed=True,checks=checks,nativeGameTested=False)))
