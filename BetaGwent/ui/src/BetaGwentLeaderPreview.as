package {
    import flash.display.Loader;
    import flash.display.Sprite;
    import flash.events.Event;
    import flash.events.IOErrorEvent;
    import flash.events.SecurityErrorEvent;
    import flash.events.TimerEvent;
    import flash.net.URLRequest;
    import flash.utils.Timer;
    import flash.utils.getTimer;

    // Two small pages per portrait; the persistent menu clock owns playback.
    // 0.6.1 hotfix: a page movie is never closed or unloaded from inside its own
    // loader event, and an in-flight load is never cancelled. Retired pages are
    // hidden at once and unloaded later by a shared timer, after their load ends.
    public class BetaGwentLeaderPreview extends Sprite {
        public var cardId:int;
        public var used:Boolean=false;
        private var metadata:Object;
        private var slots:Object={};
        private var failedPages:Object={};
        private var shown:Loader;
        private var delay:Timer;
        private var disposed:Boolean=false;
        private var started:Boolean=false;
        private var portraitWidth:Number;
        private var portraitHeight:Number;

        private static var graveyard:Array=[];
        private static var reaper:Timer;
        // Includes retired/in-flight pages, so deferred cleanup cannot grow
        // without bound when disk I/O stalls or the hover target changes rapidly.
        private static var livePages:int=0;
        private static const MAX_LIVE_PAGES:int=12;

        public function BetaGwentLeaderPreview(id:int,w:Number,h:Number) {
            cardId=id;metadata=BetaGwentLeaderCatalog.info(id);resize(w,h);
            mouseEnabled=false;mouseChildren=false;if(!metadata)return;
            addEventListener(Event.ADDED_TO_STAGE,added);
            addEventListener(Event.REMOVED_FROM_STAGE,removed);
            delay=new Timer(180,1);delay.addEventListener(TimerEvent.TIMER_COMPLETE,begin);delay.start();
        }
        public function resize(w:Number,h:Number):void {portraitWidth=w;portraitHeight=h;scaleX=w/192;scaleY=h/234;}
        public function frameAt(milliseconds:Number):int {
            var duration:Number=metadata.duration*1000;
            return int(((milliseconds%duration)+duration)%duration/duration*metadata.frames);
        }
        private function stopDelay():void {if(delay){delay.stop();delay.removeEventListener(TimerEvent.TIMER_COMPLETE,begin);delay=null;}}
        private function begin(e:TimerEvent):void {
            stopDelay();if(disposed)return;started=true;
            if(stage){addEventListener(Event.ENTER_FRAME,tick);tick(null);}
        }
        private function added(e:Event):void {if(started&&!disposed){addEventListener(Event.ENTER_FRAME,tick);tick(null);}}
        private function removed(e:Event):void {removeEventListener(Event.ENTER_FRAME,tick);}
        private function request(page:int):void {
            if(slots[page]||failedPages[page]||disposed||livePages>=MAX_LIVE_PAGES)return;
            var path:String=BetaGwentLeaderCatalog.path(cardId,page);if(!path)return;
            var loader:Loader=new Loader();loader.visible=false;
            livePages++;
            var entry:Object={loader:loader,ready:false,done:false};
            slots[page]=entry;addChild(loader);
            loader.contentLoaderInfo.addEventListener(Event.COMPLETE,loaded);
            loader.contentLoaderInfo.addEventListener(IOErrorEvent.IO_ERROR,failed);
            loader.contentLoaderInfo.addEventListener(SecurityErrorEvent.SECURITY_ERROR,failed);
            try{loader.load(new URLRequest(path));}catch(error:Error){entry.done=true;entry.failed=true;failedPages[page]=true;}
        }
        // Runs only from ENTER_FRAME or the start/add path, never from a loader event.
        private function tick(e:Event):void {
            if(disposed||!stage||!metadata)return;
            var frame:int=frameAt(getTimer()),page:int=int(frame/24),next:int=(page+1)%metadata.pages;
            var entry:Object=slots[page];var key:String;var drop:Array=[];
            if(entry&&entry.failed){failedPages[page]=true;drop.push(page);entry=null;}
            if(entry&&entry.ready&&entry.loader.content){
                if(shown&&shown!=entry.loader)shown.visible=false;
                shown=entry.loader;
                try{Object(shown.content).renderAt(frame);}catch(renderError:Error){}
                shown.visible=true;
                for(key in slots)if(int(key)!=page&&int(key)!=next)drop.push(int(key));
            }else{
                // Retain the last displayed frame if disk I/O misses a page deadline.
                for(key in slots)if(int(key)!=page&&slots[key].loader!=shown)drop.push(int(key));
            }
            for each(var p:int in drop)releasePage(p);
            if(!slots[page])request(page);
            if(slots[page]&&slots[page].ready)request(next);
        }
        private function entryFor(info:Object):Object {
            for(var key:String in slots)if(info==slots[key].loader.contentLoaderInfo)return slots[key];
            return null;
        }
        private function loaded(e:Event):void {var entry:Object=entryFor(e.currentTarget);if(entry){entry.done=true;entry.ready=true;}}
        private function failed(e:Event):void {var entry:Object=entryFor(e.currentTarget);if(entry){entry.done=true;entry.failed=true;}}
        private function releasePage(page:int):void {
            var entry:Object=slots[page];if(!entry)return;delete slots[page];
            var loader:Loader=entry.loader;
            loader.contentLoaderInfo.removeEventListener(Event.COMPLETE,loaded);
            loader.contentLoaderInfo.removeEventListener(IOErrorEvent.IO_ERROR,failed);
            loader.contentLoaderInfo.removeEventListener(SecurityErrorEvent.SECURITY_ERROR,failed);
            loader.visible=false;if(shown==loader)shown=null;
            retire(loader,entry.done);
        }
        public function dispose():void {
            if(disposed)return;disposed=true;stopDelay();
            removeEventListener(Event.ADDED_TO_STAGE,added);removeEventListener(Event.REMOVED_FROM_STAGE,removed);removeEventListener(Event.ENTER_FRAME,tick);
            var keys:Array=[];for(var key:String in slots)keys.push(int(key));
            for each(var p:int in keys)releasePage(p);
            if(parent)parent.removeChild(this);
        }

        // Shared deferred unload. Timer callbacks run outside any loader dispatch.
        private static function retire(loader:Loader,done:Boolean):void {
            var grave:Object={loader:loader,done:done,waits:0};
            if(!done){
                grave.finish=function(e:Event):void {grave.done=true;};
                loader.contentLoaderInfo.addEventListener(Event.COMPLETE,grave.finish);
                loader.contentLoaderInfo.addEventListener(IOErrorEvent.IO_ERROR,grave.finish);
                loader.contentLoaderInfo.addEventListener(SecurityErrorEvent.SECURITY_ERROR,grave.finish);
            }
            graveyard.push(grave);
            if(!reaper){reaper=new Timer(40,0);reaper.addEventListener(TimerEvent.TIMER,reap);reaper.start();}
        }
        private static function reap(e:TimerEvent):void {
            var keep:Array=[];
            for each(var grave:Object in graveyard){
                var loader:Loader=grave.loader;
                if(!grave.done){keep.push(grave);continue;}
                if(grave.finish){
                    loader.contentLoaderInfo.removeEventListener(Event.COMPLETE,grave.finish);
                    loader.contentLoaderInfo.removeEventListener(IOErrorEvent.IO_ERROR,grave.finish);
                    loader.contentLoaderInfo.removeEventListener(SecurityErrorEvent.SECURITY_ERROR,grave.finish);
                }
                if(loader.parent)loader.parent.removeChild(loader);
                if(grave.done){
                    try{if(loader.content)Object(loader.content).release();}catch(releaseError:Error){}
                    try{loader.unloadAndStop(true);}catch(unloadError:Error){}
                    livePages--;
                }
                // Keep unfinished loads counted against the global cap. Never
                // cancel them or pretend their memory has already been freed.
            }
            graveyard=keep;
            if(!graveyard.length&&reaper){reaper.stop();reaper.removeEventListener(TimerEvent.TIMER,reap);reaper=null;}
        }
    }
}
