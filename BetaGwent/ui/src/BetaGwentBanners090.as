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
        private static const DATA:Object={"Monsters_Bronze":[-0.165333934,-0.039499416,0.414865552,0.890149893,286,880],"Monsters_Gold":[-0.205950113,-0.085018553,0.501900225,0.942750237,346,932],"Monsters_Silver":[-0.165333934,-0.039499416,0.414865552,0.890149893,286,880],"Neutral_Bronze":[-0.16582807,-0.026384012,0.375699778,0.873964885,259,864],"Neutral_Gold":[-0.25286284,-0.092099044,0.467086331,0.938702816,322,928],"Neutral_Silver":[-0.16582807,-0.026384012,0.375699778,0.873964885,259,864],"Nilfgaard_Bronze":[-0.178081066,-0.053614655,0.414865606,0.874976262,286,865],"Nilfgaard_Gold":[-0.237554817,-0.098122281,0.423569096,0.914426861,292,904],"Nilfgaard_Silver":[-0.17808111,-0.053614663,0.414865696,0.874976308,286,865],"Northern_Bronze":[-0.115057883,-0.021268712,0.264005347,0.863849821,182,854],"Northern_Gold":[-0.199191321,-0.106237379,0.377150275,0.956910108,260,946],"Northern_Silver":[-0.115057883,-0.021268712,0.264005347,0.863849821,182,854],"Scoiatael_Bronze":[-0.20734538,-0.046499325,0.398908967,0.529031899,275,523],"Scoiatael_Gold":[-0.242159364,-0.096064447,0.516405998,0.954887364,356,944],"Scoiatael_Silver":[-0.20734538,-0.046499325,0.398908967,0.529031899,275,523],"Skellige_Bronze":[-0.19258671,-0.056614759,0.361193939,0.883069173,249,873],"Skellige_Gold":[-0.312985031,-0.107191372,0.546868484,0.95185306,377,941],"Skellige_Silver":[-0.19258671,-0.056614759,0.361193939,0.883069173,249,873]};
        private static const FACTIONS:Object={1:"Neutral",2:"Monsters",4:"Nilfgaard",8:"Northern",16:"Scoiatael",32:"Skellige"};
        private static var live:int=0;
        private static var retired:Array=[];
        private static var reaper:Timer;
        public static var lastError:String="";
        // Reference-aligned strength slots: all six factions and three tiers.
        private static const SLOTS:Object={"Monsters_Bronze":[0.074011577,0.092,0.115],"Monsters_Gold":[0.045,0.092],"Monsters_Silver":[0.074011577,0.092,0.115],"Neutral_Bronze":[0.03,0.095,0.115],"Neutral_Gold":[0.03,0.092],"Neutral_Silver":[0.03,0.095,0.115],"Nilfgaard_Bronze":[0.022098842,0.088,0.115],"Nilfgaard_Gold":[0.025,0.088],"Nilfgaard_Silver":[0.022098841,0.088,0.115],"Northern_Bronze":[0.021296527,0.09,0.115],"Northern_Gold":[0.03,0.09],"Northern_Silver":[0.021296527,0.09,0.115],"Scoiatael_Bronze":[0.068264452,0.085,0.115],"Scoiatael_Gold":[0.032,0.085],"Scoiatael_Silver":[0.068264452,0.085,0.115],"Skellige_Bronze":[0.025,0.085,0.115],"Skellige_Gold":[0.025,0.085],"Skellige_Silver":[0.025,0.085,0.115]};
        public static function slot(faction:int,tier:int):Array
        {var s:Array=SLOTS[key(faction,tier)];return s?s:SLOTS["Neutral_Bronze"];}
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
