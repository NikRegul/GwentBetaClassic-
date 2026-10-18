"""Keep VS portraits animated and acknowledge the actual queued voice clock."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from patch_ui_intro import ROOT,BUILD,read,write,rep
def preview(s):
    s=rep(s,'        private var playbackStart:int=0;','''        private var playbackStart:int=0;
        private var waitingForSignal:Boolean=false;
        private var idle:BetaGwentLeaderPreview;
        private var loopOrigin:int=0;
        public function waitForVoice():void { waitingForSignal=true; }
        public function startAt(clock:int):void { waitingForSignal=false;playbackStart=clock; }
        public function hasFrame():Boolean { return shown!=null||(idle!=null&&idle.hasFrame()); }
        private function continueIdle():void {
            if(!idle){
                // Free the prefetched page before asking for the idle page; retain the visible frame.
                var obsolete:Array=[];for(var key:String in slots)if(slots[key].loader!=shown)obsolete.push(int(key));
                for each(var page:int in obsolete)releasePage(page);
                idle=new BetaGwentLeaderPreview(cardId,192,234);idle.loopOrigin=getTimer();addChild(idle);
            }
            if(idle.hasFrame()){
                var keys:Array=[];for(key in slots)keys.push(int(key));
                for each(page in keys)releasePage(page);
                removeEventListener(Event.ENTER_FRAME,tick);
            }
        }''')
    s=rep(s,'            if(metadata.once)return Math.min(metadata.frames-1,int(Math.max(0,milliseconds-playbackStart)/duration*metadata.frames));','            if(waitingForSignal)return 0;\n            if(metadata.once)return Math.min(metadata.frames-1,int(Math.max(0,milliseconds-playbackStart)/duration*metadata.frames));')
    s=rep(s,'return int(((milliseconds%duration)+duration)%duration/duration*metadata.frames);','return int((((milliseconds-loopOrigin)%duration)+duration)%duration/duration*metadata.frames);')
    s=rep(s,'if(slots[page]||failedPages[page]||disposed||livePages>=MAX_LIVE_PAGES)return;','if(slots[page]||(failedPages[page]&&getTimer()<Number(failedPages[page]))||disposed||livePages>=MAX_LIVE_PAGES)return;')
    s=s.replace('entry.failed=true;failedPages[page]=true;','entry.failed=true;failedPages[page]=getTimer()+500;')
    s=rep(s,'            if(disposed||!stage||!metadata)return;','            if(disposed||!stage||!metadata)return;\n            if(metadata.once&&!waitingForSignal&&getTimer()>=playbackStart+metadata.duration*1000){continueIdle();return;}')
    s=rep(s,'if(entry&&entry.failed){failedPages[page]=true;drop.push(page);entry=null;}','if(entry&&entry.failed){failedPages[page]=getTimer()+500;drop.push(page);entry=null;}')
    s=rep(s,'if(disposed)return;disposed=true;stopDelay();','if(disposed)return;disposed=true;stopDelay();\n            if(idle){idle.dispose();idle=null;}')
    return s
def board(s):
    s=rep(s,'        private var introAudioPending:Boolean=false;','''        private var introAudioPending:Boolean=false;
        private var introSideMovies:Object={};
        private var introVoiceSeen:Object={};
        public function setIntroVoiceStart(serial:int,side:int,templateId:int,clock:int):void
        {
            if(serial!=introSerial||introStart<=0||introSkipAt>0||side<1||side>2||int(leaderIds[side-1])!=templateId||introVoiceSeen[side])return;
            introVoiceSeen[side]=true;
            var movie:BetaGwentLeaderPreview=introSideMovies[side];
            if(movie&&templateId==201743)movie.startAt(clock);
        }''')
    s=rep(s,'                card.addChildAt(movie,Math.min(1,card.numChildren));introLeaderMovies.push(movie);','''                if(leader==201743&&connected&&voiceEnabled&&betaAudioInstalled)movie.waitForVoice();
                introSideMovies[side]=movie;
                card.addChildAt(movie,Math.min(1,card.numChildren));introLeaderMovies.push(movie);''')
    s=rep(s,'            introVisualMs=INTRO_MS;','            introVisualMs=INTRO_MS;introSideMovies={};introVoiceSeen={};')
    s=rep(s,'for each(var movie:BetaGwentLeaderPreview in introLeaderMovies)movie.dispose();introLeaderMovies=[];','for each(var movie:BetaGwentLeaderPreview in introLeaderMovies)movie.dispose();introLeaderMovies=[];introSideMovies={};introVoiceSeen={};')
    old='if(part.entranceId&&!part.entranceSound&&t>=part.t0){part.entranceSound=true;send("OnBetaGwentAudioLeaderEntrance",[int(part.entranceId),int(part.side),introSerial,getTimer()]);}'
    new='''if(part.entranceId&&!part.entranceSound&&t>=part.t0){
                    var portrait:BetaGwentLeaderPreview=introSideMovies[int(part.side)];
                    if(!portrait||portrait.hasFrame()||t>=part.t0+1500){
                        part.entranceSound=true;
                        if(portrait&&int(part.entranceId)==201743&&(!connected||!voiceEnabled||!betaAudioInstalled))portrait.startAt(getTimer());
                        send("OnBetaGwentAudioLeaderEntrance",[int(part.entranceId),int(part.side),introSerial,getTimer()]);
                    }
                }
                // A missing audio bridge must release a held Queen instead of freezing her first frame.
                if(part.entranceId==201743&&!introVoiceSeen[int(part.side)]&&!introAudioPending&&t>=part.t0+1500){
                    var silent:BetaGwentLeaderPreview=introSideMovies[int(part.side)];
                    if(silent)silent.startAt(getTimer());introVoiceSeen[int(part.side)]=true;
                }'''
    return rep(s,old,new)
def audio(s):
    s=rep(s,'    private var introEffectsPlayed : array<int>;','''    private var introEffectsPlayed : array<int>;
    private var introQueuedSides, introReadySides : array<int>;
    private var introVoiceSide, introVoiceTemplate, introVoiceClock : int;
    public function MarkIntroReady(side : int) { if((side==1 || side==2) && !introReadySides.Contains(side))introReadySides.PushBack(side); }
    public function IntroVoiceSide() : int { return introVoiceSide; }
    public function IntroVoiceTemplate() : int { return introVoiceTemplate; }
    public function IntroVoiceClock() : int { return introVoiceClock; }''')
    s=rep(s,'introEnemyTemplate=opponent;introPlayerTemplate=player;introEffectsPlayed.Clear();','introEnemyTemplate=opponent;introPlayerTemplate=player;introEffectsPlayed.Clear();introQueuedSides.Clear();introReadySides.Clear();introVoiceSide=0;introVoiceTemplate=0;introVoiceClock=0;')
    s=rep(s,'{ queuedVoices.PushBack(opponent); queuedAt.PushBack(now); }','{ queuedVoices.PushBack(opponent); queuedAt.PushBack(now+0.3f); introQueuedSides.PushBack(2); }')
    s=rep(s,'{ queuedVoices.PushBack(player); queuedAt.PushBack(now); }','{ queuedVoices.PushBack(player); queuedAt.PushBack(now+1.1f); introQueuedSides.PushBack(1); }')
    s=rep(s,'            if (now < queuedAt[0]) return;','            if (now < queuedAt[0]) return;\n            if(introVoices && introQueuedSides.Size()>0 && !introReadySides.Contains(introQueuedSides[0]))return;')
    s=rep(s,'            SetVoiceMix(true);theSound.SoundEvent(eventName);','''            SetVoiceMix(true);theSound.SoundEvent(eventName);
            if(introVoices && introQueuedSides.Size()>0){
                introVoiceSide=introQueuedSides[0];introQueuedSides.Erase(0);
                introVoiceTemplate=id;introVoiceClock=(int)(now*1000.0f);
            }''')
    s=rep(s,'        queuedVoices.Clear(); queuedAt.Clear(); voiceUntil = 0.0f;','        queuedVoices.Clear(); queuedAt.Clear(); voiceUntil = 0.0f;introQueuedSides.Clear();introReadySides.Clear();introVoiceSide=0;introVoiceTemplate=0;introVoiceClock=0;')
    return s
def menu(s):
    s=rep(s,'    private var setIntroAudioState : CScriptedFlashFunction;','    private var setIntroAudioState : CScriptedFlashFunction;\n    private var setIntroVoiceStart : CScriptedFlashFunction;')
    s=rep(s,'        setIntroAudioState = GetMenuFlash().GetMemberFlashFunction("setIntroAudioState");','        setIntroAudioState = GetMenuFlash().GetMemberFlashFunction("setIntroAudioState");\n        setIntroVoiceStart = GetMenuFlash().GetMemberFlashFunction("setIntroVoiceStart");')
    s=rep(s,'        if(setIntroAudioState && introAudioSerial>0)setIntroAudioState.InvokeSelfTwoArgs(FlashArgInt(introAudioSerial),FlashArgBool(pending));','''        if(setIntroAudioState && introAudioSerial>0)setIntroAudioState.InvokeSelfTwoArgs(FlashArgInt(introAudioSerial),FlashArgBool(pending));
        if(setIntroVoiceStart && introAudioSerial>0 && audio && audio.IntroVoiceSide()>0)
            setIntroVoiceStart.InvokeSelfFourArgs(FlashArgInt(introAudioSerial),FlashArgInt(audio.IntroVoiceSide()),FlashArgInt(audio.IntroVoiceTemplate()),FlashArgInt(audio.IntroVoiceClock()));''')
    return rep(s,'audio.SetClock(clock);audio.LeaderEntrance(templateId,side);','audio.SetClock(clock);audio.MarkIntroReady(side);audio.LeaderEntrance(templateId,side);')
def main():
    for platform in ['nextgen','classic']:
        ui=BUILD/platform/'ui/src'
        for name,fn in [('BetaGwentBoard.as',board),('BetaGwentLeaderPreview.as',preview)]:
            p=ui/name;write(p,fn(read(p)))
    for name,fn in [('duelAudio.ws',audio),('developmentBoardMenu.ws',menu)]:
        p=BUILD/'scripts/game/betagwent'/name;write(p,fn(read(p)))
    print('Patched entrance-to-idle transition, bounded page retry and voice-start acknowledgements')
if __name__=='__main__':main()
