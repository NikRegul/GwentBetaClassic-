package
{
    import flash.display.Loader;
    import flash.display.Sprite;
    import flash.events.Event;
    import flash.events.IOErrorEvent;
    import flash.events.SecurityErrorEvent;
    import flash.events.TimerEvent;
    import flash.net.URLRequest;
    import flash.utils.Timer;
    // Beta 0.9.24 LargeCardMesh banners (faction x Bronze/Silver/Gold; leaders use Gold),
    // Only the EdgeTex banner mesh, excluding MainTex art tiles and frame UVs.
    // Placement: x, y, w, h, source px width/height.
    public class BetaGwentBanners090
    {
        private static const DATA:Object={"Monsters_Bronze":[-0.18594017646066482,-0.0775132774577494,0.4509408177491095,0.9675542320581388,286,880],"Monsters_Gold":[-0.28152306434116314,-0.13435886900035007,0.5455437228955221,1.0247285186057153,346,932],"Monsters_Silver":[-0.18594017646066482,-0.0775132774577494,0.4509408177491095,0.9675542320581388,286,880],"Neutral_Bronze":[-0.2013904448416066,-0.0600810815379205,0.4083693239629023,0.9499618317469153,259,864],"Neutral_Gold":[-0.2945452884417144,-0.1338367238477895,0.5077025337248476,1.0203291474620217,322,928],"Neutral_Silver":[-0.2013904448416066,-0.0600810815379205,0.4083693239629023,0.9499618317469153,259,864],"Nilfgaard_Bronze":[-0.2489192181199985,-0.08200363981340242,0.4509408756646046,0.9510611540769234,286,865],"Nilfgaard_Gold":[-0.3076552163124723,-0.12568125302950642,0.46040119160314463,0.9939422402583621,292,904],"Nilfgaard_Silver":[-0.24892047512570575,-0.08164823876089389,0.45094097359741625,0.9510612044206421,286,865],"Northern_Bronze":[-0.16442010078193955,-0.05801067392018227,0.28696233402060883,0.9389671963217835,182,854],"Northern_Gold":[-0.25940860037235847,-0.15756481731021313,0.4099459507168334,1.040119682362994,260,946],"Northern_Silver":[-0.16442010078193955,-0.05801067392018227,0.28696233402060883,0.9389671963217835,182,854],"Scoiatael_Bronze":[-0.2552210517194654,-0.06332153035295433,0.43359670280912627,0.5750346723185465,275,523],"Scoiatael_Gold":[-0.2926371350720985,-0.15553523342680625,0.56131086696813,1.0379210474057325,356,944],"Scoiatael_Silver":[-0.2552210517194654,-0.06332153035295433,0.43359670280912627,0.5750346723185465,275,523],"Skellige_Bronze":[-0.2429771764385091,-0.08042601059338603,0.39260210723863537,0.9598577971802736,249,873],"Skellige_Gold":[-0.3675251628162495,-0.15503411802838138,0.5944222656606496,1.0346228908074202,377,941],"Skellige_Silver":[-0.2429771764385091,-0.08042601059338603,0.39260210723863537,0.9598577971802736,249,873]};
        private static const FACTIONS:Object={1:"Neutral",2:"Monsters",4:"Nilfgaard",8:"Northern",16:"Scoiatael",32:"Skellige"};
        private static var live:int=0;
        private static var retired:Array=[];
        private static var reaper:Timer;
        public static var lastError:String="";
        // Centre of the power number on each banner (card fractions).
        private static const SLOTS:Object={"Nilfgaard_Bronze":[-0.0487,0.0741],"Nilfgaard_Silver":[-0.0487,0.0741],"Nilfgaard_Gold":[-0.0396,0.0524],"Northern_Bronze":[-0.0398,0.063],"Northern_Silver":[-0.0398,0.063],"Northern_Gold":[-0.0197,0.072]};
        public static function slot(faction:int,tier:int):Array
        {var s:Array=SLOTS[key(faction,tier)];return s?s:[-0.035, 0.06];}
        public static function key(faction:int,tier:int):String
        {
            var f:String=FACTIONS[faction]||"Neutral";var t:String=tier==1||tier==8?"Gold":tier==4?"Silver":"Bronze";
            if(t=="Silver"&&!DATA[f+"_Silver"])t="Bronze";
            return f+"_"+t;
        }
        // Adds the banner page above the art; on a load failure removes it and calls fallback.
        public static function paint(parent:Sprite,faction:int,tier:int,w:Number,h:Number,fallback:Function,ready:Function=null):Boolean
        {
            var name:String=key(faction,tier);var d:Array=DATA[name];if(!d||!parent||live>=8){lastError=!d?"data "+name:!parent?"parent":"limit";return false;}
            var holder:Sprite=new Sprite();holder.mouseEnabled=false;holder.mouseChildren=false;holder.visible=false;
            holder.x=d[0]*w;holder.y=d[1]*h;holder.scaleX=d[2]*w/d[4];holder.scaleY=d[3]*h/d[5];parent.addChild(holder);
            var loader:Loader=new Loader();holder.addChild(loader);live++;
            var state:Object={loader:loader,done:false,retired:false};
            var frames:int=0;
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
            };
            var retire:Function=function():void{
                if(state.retired)return;state.retired=true;loader.visible=false;
                retired.push(state);
                if(!reaper){reaper=new Timer(40);reaper.addEventListener(TimerEvent.TIMER,reap);reaper.start();}
            };
            var failed:Function=function(e:Event):void{
                state.done=true;if(state.retired)return;
                lastError=state.reason?state.reason:e&&e.type?e.type+" "+name:"throw "+name;
                trace("UI_ERROR banner_load_failed="+lastError);
                retire();
                if(holder.parent)holder.parent.removeChild(holder);
                if(fallback!=null)fallback();
            };
            var removed:Function=function(e:Event):void{if(e.target==holder)retire();};
            state.complete=complete;state.failed=failed;state.removed=removed;state.holder=holder;
            loader.contentLoaderInfo.addEventListener(Event.COMPLETE,complete);
            loader.contentLoaderInfo.addEventListener(IOErrorEvent.IO_ERROR,failed);
            loader.contentLoaderInfo.addEventListener(SecurityErrorEvent.SECURITY_ERROR,failed);
            holder.addEventListener(Event.REMOVED_FROM_STAGE,removed);
            try{loader.load(new URLRequest("swf/betagwentbanners/"+name.toLowerCase()+".swf"));}catch(error:Error){failed(null);}
            return true;
        }
        // Do not cancel in-flight native loads or unload inside loader events.
        private static function reap(e:TimerEvent):void
        {
            var keep:Array=[];
            for each(var state:Object in retired){
                if(!state.done){keep.push(state);continue;}
                var loader:Loader=state.loader;
                loader.contentLoaderInfo.removeEventListener(Event.COMPLETE,state.complete);
                loader.contentLoaderInfo.removeEventListener(IOErrorEvent.IO_ERROR,state.failed);
                loader.contentLoaderInfo.removeEventListener(SecurityErrorEvent.SECURITY_ERROR,state.failed);
                state.holder.removeEventListener(Event.REMOVED_FROM_STAGE,state.removed);
                if(state.poll)state.holder.removeEventListener(Event.ENTER_FRAME,state.poll);
                if(loader.parent)loader.parent.removeChild(loader);
                try{loader.unloadAndStop(false);}catch(error:Error){}
                live--;
            }
            retired=keep;
            if(!retired.length&&reaper){reaper.stop();reaper.removeEventListener(TimerEvent.TIMER,reap);reaper=null;}
        }
    }
}
