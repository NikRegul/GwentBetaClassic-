"""0.9.0 build 6 UI: banner load diagnostics/tolerant COMPLETE, no placement tick.

Source: release090-banner-runtime2 (build 5 UI). Output: release090-banner-runtime3.
* A COMPLETE whose content is not yet measurable is no longer an instant failure:
  the page is polled for up to 90 frames (native texture may arrive later).
* Every failure records a reason (io/security/empty/timeout/throw/limit); the
  inspection card prints it in small text on the fallback flag layer (test aid,
  it never covers the power number).
* The white vertical tick above the row placement preview is removed.
"""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/build/release090-banner-runtime2'
OUT=ROOT/'BetaGwent/build/release090-banner-runtime3'
COPIES=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']

def replace(s,a,b):
    assert s.count(a)==1,a[:120]
    return s.replace(a,b)
def write(p,s):p.write_bytes(b'\xef\xbb\xbf'+s.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))

def board(s):
    s=replace(s,'placementGhost.graphics.moveTo(x+width/2,g.y-3);placementGhost.graphics.lineTo(x+width/2,g.y-15);\n','')
    s=replace(s,'''            BetaGwentBanners090.paint(p,entry?int(entry.faction):1,tier,w,h,null,loaded);
            return face;''','''            var diagnose:Function=function():void{
                // Test aid: the reason a native banner page was not shown.
                var note:TextField=text(flag,"banner: "+BetaGwentBanners090.lastError,w*.04,h-Math.max(18,h*.05),w*.92,Math.max(10,int(h*.022)),0xFFB4A0);
                note.alpha=.85;
            };
            if(!BetaGwentBanners090.paint(p,entry?int(entry.faction):1,tier,w,h,diagnose,loaded))diagnose();
            return face;''')
    return s

def loader(s):
    s=replace(s,'        private static var reaper:Timer;\n','        private static var reaper:Timer;\n        public static var lastError:String="";\n')
    s=replace(s,'var name:String=key(faction,tier);var d:Array=DATA[name];if(!d||!parent||live>=8)return false;',
        'var name:String=key(faction,tier);var d:Array=DATA[name];if(!d||!parent||live>=8){lastError=!d?"data "+name:!parent?"parent":"limit";return false;}')
    s=replace(s,'''            var complete:Function=function(e:Event):void{
                state.done=true;if(state.retired)return;
                if(!loader.content||loader.content.width<=0||loader.content.height<=0){failed(e);return;}
                if(ready!=null)ready();holder.visible=true;
            };''','''            var frames:int=0;
            var show:Function=function():void{if(ready!=null)ready();holder.visible=true;};
            var poll:Function=function(e:Event):void{
                if(state.retired||!loader.content){holder.removeEventListener(Event.ENTER_FRAME,poll);return;}
                if(loader.content.width>0&&loader.content.height>0){holder.removeEventListener(Event.ENTER_FRAME,poll);show();return;}
                if(++frames>=90){holder.removeEventListener(Event.ENTER_FRAME,poll);state.reason="timeout "+name;failed(e);}
            };
            var complete:Function=function(e:Event):void{
                state.done=true;if(state.retired)return;
                if(!loader.content){state.reason="empty "+name;failed(e);return;}
                // A native texture can become measurable after COMPLETE.
                if(loader.content.width>0&&loader.content.height>0){show();return;}
                state.poll=poll;holder.addEventListener(Event.ENTER_FRAME,poll);
            };''')
    s=replace(s,'''                state.done=true;if(state.retired)return;
                trace("UI_ERROR banner_load_failed="+name);''','''                state.done=true;if(state.retired)return;
                lastError=state.reason?state.reason:e&&e.type?e.type+" "+name:"throw "+name;
                trace("UI_ERROR banner_load_failed="+lastError);''')
    s=replace(s,'                state.holder.removeEventListener(Event.REMOVED_FROM_STAGE,state.removed);\n',
        '                state.holder.removeEventListener(Event.REMOVED_FROM_STAGE,state.removed);\n                if(state.poll)state.holder.removeEventListener(Event.ENTER_FRAME,state.poll);\n')
    return s

def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=OUT)
    OUT=parser.parse_args().out.resolve()
    assert OUT.is_relative_to(ROOT/'BetaGwent/build') and not OUT.exists()
    for platform in ['classic','nextgen']:
        target=OUT/platform;target.mkdir(parents=True)
        shutil.copytree(SOURCE/platform/'ui',target/'ui')
        for name,patch in [('BetaGwentBoard.as',board),('BetaGwentBanners090.as',loader)]:
            p=target/'ui/src'/name;write(p,patch(p.read_text('utf-8-sig')))
            for folder in COPIES:
                if folder!='src':shutil.copy2(p,target/'ui'/folder/name)
                if platform=='nextgen':shutil.copy2(p,ROOT/'BetaGwent/ui'/folder/name)
        manifest=json.loads((SOURCE/platform/'ui-inputs.json').read_text('utf8'))
        manifest['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (target/'ui/src').glob('*.as')}
        (target/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
        if platform=='classic':shutil.copy2(SOURCE/'classic/subimages.json',target/'subimages.json')
    shutil.copytree(SOURCE/'scripts',OUT/'scripts')
    print('Prepared build 6 UI: tolerant banner COMPLETE, failure reason, no placement tick.')

if __name__=='__main__':main()
