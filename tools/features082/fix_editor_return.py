from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from patch_ui_intro import BUILD,read,write,rep
def main():
    for platform in ['nextgen','classic']:
        p=BUILD/platform/'ui/src/BetaGwentController.as';s=read(p)
        s=rep(s,'        private var navigationColumn:Number=NaN;','        private var navigationColumn:Number=NaN;\n        private var editorReturnKey:String="";')
        s=rep(s,'if(footer){select(footer);invoke("tickSound");return;}','if(footer){editorReturnKey=n.key;select(footer);invoke("tickSound");return;}')
        s=rep(s,'            var mode:String=state().mode;','''            var mode:String=state().mode;
            if(mode=="editor"&&dir==38&&n.tag=="control"&&origin.y>=984){
                var returnCard:Object=null,returnScore:Number=Number.MAX_VALUE;
                for each(var visible:Object in allOptions)if(visible.tag=="card"){
                    if(visible.key==editorReturnKey){returnCard=visible;break;}
                    var returnCost:Number=(1080-visible.rect.y-visible.rect.height)*10+Math.abs(visible.rect.x-origin.x);
                    if(returnCost<returnScore){returnScore=returnCost;returnCard=visible;}
                }
                if(returnCard){select(returnCard);invoke("tickSound");return;}
            }''')
        write(p,s)
    p=BUILD/'scripts/game/betagwent/duelAudio.ws';s=read(p)
    s=rep(s,'{ if(introVoices)StopVoice(); }','{ if(introVoices)StopVoice(); introVoiceSide=0;introVoiceTemplate=0;introVoiceClock=0;introQueuedSides.Clear();introReadySides.Clear(); }');write(p,s)
if __name__=='__main__':main()
