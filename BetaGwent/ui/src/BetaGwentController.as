package
{
    import flash.display.DisplayObject;
    import flash.display.Sprite;
    import flash.display.Stage;
    import flash.events.Event;
    import flash.events.KeyboardEvent;
    import flash.events.MouseEvent;
    import flash.geom.Rectangle;
    import flash.geom.Point;
    import flash.text.TextField;
    import flash.text.TextFormat;
    import flash.utils.getTimer;
    import scaleform.gfx.Extensions;
    import scaleform.gfx.GamePad;
    import scaleform.gfx.GamePadAnalogEvent;

    // Key/axis values come from the stock TW3 red.core.constants.KeyCode.
    // Action presses stay latched until release, including across WS snapshots.
    public class BetaGwentController extends Sprite
    {
        private var owner:Sprite;
        private var context:Function;
        private var command:Function;
        private var surface:Stage;
        private var nodes:Array=[];
        private var pressed:Object={};
        private var repeats:Object={};
        private var saved:Object={};
        private var panes:Object={};
        private var focus:Object;
        private var currentMode:String="";
        private var lastRect:Rectangle;
        private var lastKey:String="";
        private var dirty:Boolean=true;
        private var hint:TextField=new TextField();
        private var lastHint:String="";
        private var lastMouseX:Number=NaN;
        private var lastMouseY:Number=NaN;
        private var axis:int=0;
        private var axisNext:int=0;
        private var scrollNext:int=0;
        private var movementAt:int=-1000;
        private var navigationColumn:Number=NaN;
        private var yStarted:int=0;
        private var yCommitted:Boolean=false;
        private var yCanPass:Boolean=false;
        private var gamePad:Object;
        private var traceAt:int=-1000;
        private var inputCode:int=0;
        public var active:Boolean=false;
        public var device:int=0;
        public var swap:Boolean=false;

        public function BetaGwentController(root:Sprite,state:Function,dispatch:Function)
        {
            owner=root;context=state;command=dispatch;
            mouseEnabled=false;mouseChildren=false;
            hint.defaultTextFormat=new TextFormat("$NormalFont",18,0xF5E6A7);
            hint.multiline=false;hint.selectable=false;hint.mouseEnabled=false;
            hint.width=1848;hint.height=29;hint.x=36;addChild(hint);
            addEventListener(Event.ENTER_FRAME,tick);
        }
        public function bind(value:Stage):void
        {
            surface=value;
            surface.addEventListener(KeyboardEvent.KEY_DOWN,down,true,100);
            surface.addEventListener(KeyboardEvent.KEY_UP,up,true,100);
            surface.addEventListener(MouseEvent.MOUSE_MOVE,mouseMove,true,100);
            surface.addEventListener(GamePadAnalogEvent.CHANGE,analog,true,100);
            // Stage-target events have no capture phase. Listen at the target
            // too; handled child events stop before they reach this listener.
            surface.addEventListener(KeyboardEvent.KEY_DOWN,down,false,100);
            surface.addEventListener(KeyboardEvent.KEY_UP,up,false,100);
            surface.addEventListener(MouseEvent.MOUSE_MOVE,mouseMove,false,100);
            surface.addEventListener(GamePadAnalogEvent.CHANGE,analog,false,100);
            surface.addEventListener(Event.DEACTIVATE,deactivate);
            Extensions.enabled=true;gamePad=GamePad;
        }
        public function dispose():void
        {
            removeEventListener(Event.ENTER_FRAME,tick);
            if(surface) {
                surface.removeEventListener(KeyboardEvent.KEY_DOWN,down,true);
                surface.removeEventListener(KeyboardEvent.KEY_UP,up,true);
                surface.removeEventListener(MouseEvent.MOUSE_MOVE,mouseMove,true);
                surface.removeEventListener(GamePadAnalogEvent.CHANGE,analog,true);
                surface.removeEventListener(KeyboardEvent.KEY_DOWN,down,false);
                surface.removeEventListener(KeyboardEvent.KEY_UP,up,false);
                surface.removeEventListener(MouseEvent.MOUSE_MOVE,mouseMove,false);
                surface.removeEventListener(GamePadAnalogEvent.CHANGE,analog,false);
                surface.removeEventListener(Event.DEACTIVATE,deactivate);
            }
            surface=null;nodes=[];focus=null;pressed={};axis=0;
        }
        public function configure(kind:int,enabled:Boolean,swapped:Boolean):void
        {device=kind;swap=swapped;setActive(enabled,false);dirty=true;}
        public function foreignInput(code:int,value:String):void
        {
            if(state().typing||(!isPad(code)&&!(active&&direction(code)>0)))return;
            if(value=="keyUp")release(code);
            else if(value=="keyDown"||value=="keyHold"){setActive(true);press(code);}
        }
        private function invoke(name:String,node:Object=null):void
        {command.call(owner,name,node);}
        private function trace(action:String):void
        {
            var now:int=getTimer();if(now-traceAt<180)return;traceAt=now;
            var s:Object=state();var n:Object=getFocus();
            invoke("trace",{code:inputCode,action:action,mode:s.mode,focus:n?n.label:"none"});
        }
        private function state():Object {return context.call(owner);}
        private function setActive(value:Boolean,notify:Boolean=true):void
        {
            if(active==value)return;active=value;dirty=true;
            if(!value){axis=0;yStarted=0;pressed={};repeats={};invoke("pileHold",{mask:0});graphics.clear();hint.visible=false;if(notify)invoke("mouse");}
            else {if(surface)surface.focus=null;if(notify)invoke("device");}
        }
        private function deactivate(e:Event):void
        {pressed={};repeats={};axis=0;yStarted=0;invoke("pileHold",{mask:0});dirty=true;}
        private function mouseMove(e:MouseEvent):void
        {
            // Let WS distinguish a physical mouse from a gamepad cursor before
            // clearing held buttons. A virtual move must not clear the latch.
            if(active&&!isNaN(lastMouseX)&&(Math.abs(e.stageX-lastMouseX)+Math.abs(e.stageY-lastMouseY)>3))invoke("mouse");
            lastMouseX=e.stageX;lastMouseY=e.stageY;
        }
        private function isPad(code:int):Boolean
        {return (code>=136&&code<=151)||(code>=201&&code<=208)||code==255||code==256;}
        private function direction(code:int):int
        {
            if(code==142||code==206||code==38)return 38;
            if(code==143||code==205||code==40)return 40;
            if(code==144||code==207||code==37)return 37;
            if(code==145||code==208||code==39)return 39;return 0;
        }
        private function down(e:KeyboardEvent):void
        {
            if(state().typing)return;
            if(!isPad(e.keyCode)&&!(active&&direction(e.keyCode)>0)) {setActive(false);return;}
            e.preventDefault();e.stopImmediatePropagation();setActive(true);
            press(e.keyCode);
        }
        private function up(e:KeyboardEvent):void
        {
            if(!isPad(e.keyCode)&&!(active&&direction(e.keyCode)>0))return;
            if(!state().typing){e.preventDefault();e.stopImmediatePropagation();}
            release(e.keyCode);
        }
        private function press(code:int):void
        {
            if(code==255)code=140;else if(code==256)code=141;
            var now:int=getTimer();var dir:int=direction(code);
            if(pressed[code]) {
                if(dir==0||now<int(repeats[code]))return;
                repeats[code]=now+160;
            }else {pressed[code]=true;repeats[code]=now+420;}
            inputCode=code;trace(dir>0?"navigate":"button");
            if(dir>0){navigate(dir);return;}
            if(code>=201&&code<=204){invoke(code==201||code==203?"scrollUp":"scrollDown");return;}
            if(code==(swap?137:136)){activate();return;}
            if(code==(swap?136:137)){invoke("back");dirty=true;return;}
            if(code==138){invoke("inspect",getFocus());dirty=true;return;}
            if(code==139){yStarted=now;yCommitted=false;yCanPass=Boolean(state().pass);dirty=true;return;}
            if(code==140||code==255){invoke("menu");dirty=true;return;}
            if(code==141||code==256){invoke("deck");dirty=true;return;}
            if(code==148||code==149){invoke(code==148?"previous":"next",getFocus());dirty=true;return;}
            if(code==150||code==151){
                if(state().mode=="editor")invoke(code==150?"ownGrave":"enemyGrave");
                else invoke("pileHold",{mask:(pressed[150]?1:0)|(pressed[151]?2:0)});
                dirty=true;return;
            }
            if(code==146){invoke("board");dirty=true;return;}
            if(code==147){invoke("leader");dirty=true;}
        }
        private function release(code:int):void
        {
            if(code==255)code=140;else if(code==256)code=141;
            delete pressed[code];delete repeats[code];
            if((code==150||code==151)&&state().mode!="editor")invoke("pileHold",{mask:(pressed[150]?1:0)|(pressed[151]?2:0)});
            if(code==139&&yStarted>0){if(!yCommitted&&!state().typing)invoke("alternate");yStarted=0;dirty=true;}
        }
        private function analog(e:GamePadAnalogEvent):void
        {
            if(state().typing||!gamePad)return;
            var data:Object=e;var code:int=int(data["code"]);
            var x:Number=Number(data["xvalue"]),y:Number=Number(data["yvalue"]);
            if(isNaN(x)||isNaN(y))return;
            if(code==1000||code==int(gamePad["PAD_LT"])) {
                var next:int=stickDirection(x,y);
                if(next!=axis){axis=next;axisNext=getTimer()+420;if(next>0){setActive(true);navigate(next);}}
            }else if(code==1001||code==int(gamePad["PAD_RT"])) {
                if(Math.max(Math.abs(x),Math.abs(y))>=.55) {
                    setActive(true);if(getTimer()>=scrollNext){scrollNext=getTimer()+150;invoke(y>0?"scrollUp":"scrollDown");}
                }
            }else if(code==1002||code==1003||code==int(gamePad["PAD_L2"])||code==int(gamePad["PAD_R2"])) {
                var trigger:int=code==1002||code==int(gamePad["PAD_L2"])?150:151;
                if(Math.max(Math.abs(x),Math.abs(y))>.65){setActive(true);press(trigger);}
                else if(Math.max(Math.abs(x),Math.abs(y))<.3)release(trigger);
            }
        }
        private function stickDirection(x:Number,y:Number):int
        {
            var magnitude:Number=Math.max(Math.abs(x),Math.abs(y));
            if(magnitude<.3)return 0;
            if(magnitude<.55)return axis;
            // Keep a held direction through diagonal jitter. A deliberate
            // change of axis still works without returning the stick to centre.
            var heldSign:Boolean=axis==37&&x<0||axis==39&&x>0||axis==38&&y>0||axis==40&&y<0;
            if(heldSign&&Math.abs(Math.abs(x)-Math.abs(y))<.18)return axis;
            return Math.abs(x)>Math.abs(y)?(x<0?37:39):(y>0?38:40);
        }
        public function registerControl(sprite:DisplayObject,label:String,callback:Function=null,card:Object=null,detail:Object=null,tag:String="control",placement:Object=null,body:Rectangle=null):void
        {
            prune();var n:Object=null;
            for each(var old:Object in nodes)if(old.sprite==sprite){n=old;break;}
            if(!n){
                var s:Object=state();var scope:String=s.baseMode;
                // Nested dialogs belong to their innermost scope, not the choice screen beneath them.
                for each(var layer:Object in s.layers)if(layer.root&&layer.root.contains(sprite))scope=layer.mode;
                n={sprite:sprite,scope:scope,label:"Выбор карты",tag:"control"};nodes.push(n);
            }
            if(label.length)n.label=label;
            if(tag.length)n.tag=tag;
            if(body!=null)n.body=body.clone();
            if(placement!=null)n.placement=placement;
            if(placement!=null&&placement.rowOnly){n.row=placement;n.placement=null;}
            if(callback!=null)n.action=callback;
            if(card!=null){n.card=card;n.detail=detail;}
            var rect:Rectangle=bodyBounds(n);
            // Card focus follows its instance when hand sorting changes the coordinates.
            n.key=n.scope+":"+(n.card!=null?n.tag+":card"+(n.card.viewKey!=null?n.card.viewKey:n.card.id>0?n.card.id:n.card.templateId):int(rect.x)+":"+int(rect.y)+":"+n.tag);
            dirty=true;
        }
        private function bodyCorners(n:Object):Array
        {
            var b:Rectangle=n.body;
            var result:Array=[];
            for each(var point:Point in [new Point(b.left,b.top),new Point(b.right,b.top),new Point(b.right,b.bottom),new Point(b.left,b.bottom)])
                result.push(owner.globalToLocal(n.sprite.localToGlobal(point)));
            return result;
        }
        private function bodyBounds(n:Object):Rectangle
        {
            if(!n.body)return n.sprite.getBounds(owner);
            var points:Array=bodyCorners(n);var left:Number=points[0].x,top:Number=points[0].y,right:Number=left,bottom:Number=top;
            for each(var p:Point in points){left=Math.min(left,p.x);right=Math.max(right,p.x);top=Math.min(top,p.y);bottom=Math.max(bottom,p.y);}
            return new Rectangle(left,top,right-left,bottom-top);
        }
        private function prune():void
        {for(var i:int=nodes.length-1;i>=0;i--)if(!owner.contains(nodes[i].sprite))nodes.splice(i,1);}
        private function candidates():Array
        {
            prune();var result:Array=[];var s:Object=state();
            for each(var n:Object in nodes) {
                if(n.scope!=s.mode||!s.root.contains(n.sprite)||!n.sprite.visible||n.sprite.alpha<.01)continue;
                if(s.mode=="rows"&&n.tag!="row"&&n.tag!="control")continue;
                if(s.mode=="placement"&&n.tag!="position"&&n.tag!="control")continue;
                if(s.mode=="target"&&n.tag!="target"&&n.tag!="row"&&n.tag!="control")continue;
                if(s.mode=="battle"&&n.tag=="card")continue;
                if(s.mode=="result"&&n.tag!="finish")continue;
                if(s.mode=="inspect"&&n.tag!="card"&&n.tag!="row"&&n.tag!="control")continue;
                if(s.mode=="editor"&&(n.label=="+"||n.label=="−"))continue;
                var r:Rectangle=bodyBounds(n);
                if(r.width<2||r.height<2||r.right<0||r.x>1920||r.bottom<0||r.y>1080)continue;
                if(s.mode=="choice"&&(r.x+r.width/2<40||r.x+r.width/2>1880||r.y+r.height/2<135||r.y+r.height/2>1060))continue;
                n.rect=r;result.push(n);
            }
            return result;
        }
        public function getFocus():Object
        {
            var s:Object=state();var options:Array=candidates();
            if(currentMode!=s.mode){if(focus)saved[currentMode]=focus.key;currentMode=s.mode;focus=null;lastRect=null;lastKey=saved[currentMode]||"";navigationColumn=NaN;}
            if(focus&&options.indexOf(focus)>=0)return focus;
            focus=null;
            for each(var n:Object in options)if(n.key==lastKey){focus=n;break;}
            if(!focus&&lastRect) {
                var nearest:Number=Number.MAX_VALUE;
                for each(n in options){var dx:Number=n.rect.x-lastRect.x,dy:Number=n.rect.y-lastRect.y;var distance:Number=dx*dx+dy*dy;if(distance<nearest){nearest=distance;focus=n;}}
            }
            if(!focus)for each(n in options)if(n.tag==s.preferred){focus=n;break;}
            if(!focus&&options.length)focus=options[0];
            if(focus){lastKey=focus.key;lastRect=focus.rect.clone();invoke("focus",focus);}return focus;
        }
        private function select(n:Object,keepColumn:Boolean=false):void
        {
            if(!n)return;focus=n;lastKey=n.key;lastRect=n.rect.clone();saved[currentMode]=n.key;
            if(!keepColumn)navigationColumn=NaN;
            dirty=true;invoke("focus",n);
        }
        private function navigationLane(n:Object):String
        {
            var lane:Object=n.placement?n.placement:n.row?n.row:n.card;
            return lane&&lane.side>0&&(lane.zone==1||lane.zone==2||lane.zone==4)?lane.side+":"+lane.zone:"";
        }
        private function gridWrap(options:Array,current:Object,dir:int):Object
        {
            var ordered:Array=[];
            for each(var node:Object in options)if(node.tag==current.tag)ordered.push(node);
            ordered.sort(function(a:Object,b:Object):Number{
                var dy:Number=a.rect.y+a.rect.height/2-b.rect.y-b.rect.height/2;
                return Math.abs(dy)>Math.min(a.rect.height,b.rect.height)*.35?dy:a.rect.x-b.rect.x;
            });
            var index:int=ordered.indexOf(current);if(index<0||ordered.length<2)return null;
            return ordered[(index+(dir==39?1:-1)+ordered.length)%ordered.length];
        }
        private function navigate(dir:int):void
        {
            // Some hosts emit both analog and synthesized stick key events.
            // Merge their same-frame movement instead of skipping a card.
            if(getTimer()-movementAt<60)return;movementAt=getTimer();
            var n:Object=getFocus();if(!n)return;
            var options:Array=candidates();var allOptions:Array=options.concat();var origin:Rectangle=n.rect;
            var mode:String=state().mode;
            // The match controls stay behind Start. Stick/D-pad navigation
            // follows cards -> placement -> targets, without jumping to a
            // graveyard/menu button merely because it is spatially closer.
            if(mode=="battle" && n.tag=="hand" && dir==38){invoke("board");dirty=true;return;}
            if(mode=="inspect" && (n.tag=="card"||n.tag=="row") && dir==40 && origin.y>=790){invoke("board");dirty=true;return;}
            if(n.tag!="control" && (mode=="battle"||mode=="inspect"||mode=="placement"||mode=="target"||mode=="rows"||mode=="choice"||mode=="keg"||mode=="editor")){
                var filtered:Array=[];
                for each(var candidate:Object in options){
                    var keep:Boolean=mode=="battle"?candidate.tag=="hand":mode=="inspect"?(candidate.tag=="card"||candidate.tag=="row"):mode=="placement"?candidate.tag=="position":mode=="rows"?candidate.tag=="row":mode=="target"?(candidate.tag=="target"||candidate.tag=="row"):mode=="editor"?candidate.tag=="card"&&(candidate.rect.x<440)==(origin.x<440):candidate.tag=="target";
                    if(keep)filtered.push(candidate);
                }
                options=filtered;
            }
            var cx:Number=origin.x+origin.width/2,cy:Number=origin.y+origin.height/2;
            var best:Object=null;var score:Number=Number.MAX_VALUE;
            var vertical:Boolean=dir==38||dir==40;
            var lane:String=navigationLane(n),nearestLane:String="",nearestY:Number=NaN;
            if(vertical&&n.tag!="control"){
                if(isNaN(navigationColumn))navigationColumn=cx;
                // Choose the adjacent logical row first. Short row buttons and
                // tall cards in the same row are never separate vertical stops.
                for each(var rowNode:Object in options){
                    if(rowNode==n||lane.length&&navigationLane(rowNode)==lane)continue;
                    var delta:Number=rowNode.rect.y+rowNode.rect.height/2-cy;
                    var distance:Number=dir==38?-delta:delta;
                    if(distance<=4||!lane.length&&distance<Math.min(origin.height,rowNode.rect.height)*.35)continue;
                    if(distance<score){score=distance;nearestLane=navigationLane(rowNode);nearestY=rowNode.rect.y+rowNode.rect.height/2;}
                }
                score=Number.MAX_VALUE;
            }
            for each(var other:Object in options) {
                if(other==n)continue;
                var dx:Number=other.rect.x+other.rect.width/2-cx,dy:Number=other.rect.y+other.rect.height/2-cy;
                var forward:Number=dir==37?-dx:dir==39?dx:dir==38?-dy:dy;
                var across:Number=dir==37||dir==39?Math.abs(dy):Math.abs(dx);
                if(forward<=4)continue;
                if(n.tag!="control"){
                    if(vertical){
                        if(isNaN(nearestY))continue;
                        if(nearestLane.length?navigationLane(other)!=nearestLane:Math.abs(other.rect.y+other.rect.height/2-nearestY)>24)continue;
                        across=Math.abs(other.rect.x+other.rect.width/2-navigationColumn);
                    }else if(lane.length?navigationLane(other)!=lane:Math.abs(dy)>Math.min(origin.height,other.rect.height)*.35)continue;
                }
                var cost:Number=vertical&&n.tag!="control"?across:forward+across*2.5+(across>forward?1000:0);
                if(cost<score){score=cost;best=other;}
            }
            // A deck and its collection are two panes of the same editor.
            // Horizontal movement at their boundary must work even when the
            // deck contains only its leader and the row heights differ.
            if(!best&&mode=="editor"&&n.tag=="card"&&!vertical&&((dir==39&&origin.x<440)||(dir==37&&origin.x>=440))){
                score=Number.MAX_VALUE;
                for each(other in allOptions){
                    if(other.tag!="card"||(other.rect.x<440)==(origin.x<440))continue;
                    dx=other.rect.x+other.rect.width/2-cx;dy=other.rect.y+other.rect.height/2-cy;
                    cost=Math.abs(dy)*4+Math.abs(dx);
                    if(cost<score){score=cost;best=other;}
                }
            }
            if(!best&&!vertical&&(n.tag=="card"||n.tag=="target")&&["choice","keg","editor","catalog","pile"].indexOf(mode)>=0)
                best=gridWrap(options,n,dir);
            // Leave the card grid only at its vertical edge. Footer buttons
            // (finish, hide, save, pages) are reachable with the same D-pad;
            // moving within the grid still visits every adjacent card row.
            if(!best&&vertical&&n.tag!="control"&&["choice","keg","editor","catalog","pile"].indexOf(mode)>=0){
                score=Number.MAX_VALUE;
                for each(other in allOptions){
                    if(other.tag!="control")continue;
                    dx=other.rect.x+other.rect.width/2-cx;dy=other.rect.y+other.rect.height/2-cy;
                    forward=dir==38?-dy:dy;if(forward<=4)continue;
                    cost=forward+Math.abs(dx)*.35;
                    if(cost<score){score=cost;best=other;}
                }
            }
            // Deck selection: from the deck's card list the stick goes straight to the
            // buttons (Start match, Edit, Change deck...) in that direction.
            // Right from the deck list: straight to "Start match" when it is on screen.
            if(mode=="selection"&&dir==39&&origin.x<440){
                for each(other in allOptions)if(other.tag=="control"&&other.label=="Начать бой"&&other.rect.x>origin.x){best=other;break;}
            }
            if(!best&&n.tag!="control"&&(mode=="selection"||mode=="result")){
                score=Number.MAX_VALUE;
                for each(other in allOptions){
                    if(other.tag!="control"||other==n)continue;
                    dx=other.rect.x+other.rect.width/2-cx;dy=other.rect.y+other.rect.height/2-cy;
                    forward=dir==37?-dx:dir==39?dx:dir==38?-dy:dy;if(forward<=4)continue;
                    across=dir==37||dir==39?Math.abs(dy):Math.abs(dx);
                    cost=forward+across*.35;
                    if(cost<score){score=cost;best=other;}
                }
            }
            // Wrap along the same column/row at an edge, so D-pad down still
            // reaches the top of a list instead of leaving focus stranded.
            if(!best&&n.tag=="control"){
                score=Number.MAX_VALUE;
                for each(other in options){
                    if(other==n)continue;
                    dx=other.rect.x+other.rect.width/2-cx;dy=other.rect.y+other.rect.height/2-cy;
                    forward=dir==37?-dx:dir==39?dx:dir==38?-dy:dy;
                    across=dir==37||dir==39?Math.abs(dy):Math.abs(dx);
                    if(forward>=-4||across>Math.max(36,dir==37||dir==39?origin.height:origin.width))continue;
                    cost=across*8+forward;
                    if(cost<score){score=cost;best=other;}
                }
            }
            if(best){select(best,vertical&&n.tag!="control");invoke("tickSound");}
        }
        public function restoreFocus(tag:String):void
        {var n:Object=getFocus();if(!n||n.tag!=tag)focusTag(tag);}
        public function focusTag(tag:String,direction:int=0):void
        {
            var options:Array=[];for each(var n:Object in candidates())if(n.tag==tag)options.push(n);
            if(!options.length)return;
            options.sort(function(a:Object,b:Object):Number{return a.rect.y==b.rect.y?a.rect.x-b.rect.x:a.rect.y-b.rect.y;});
            var index:int=options.indexOf(getFocus());
            index=direction==0?0:index<0?(direction>0?0:options.length-1):(index+direction+options.length)%options.length;
            select(options[index]);
        }
        public function focusPane(right:Boolean,split:Number=1254,cardsOnly:Boolean=false):void
        {
            var options:Array=candidates();var pick:Object=null;var current:Object=getFocus();
            if(current)panes[split+":"+(current.rect.x>=split?"right":"left")]=current.key;
            var remembered:String=panes[split+":"+(right?"right":"left")]||"";
            for each(var old:Object in options)if(old.key==remembered&&(old.rect.x>=split)==right&&(!cardsOnly||old.tag=="card")){select(old);return;}
            for each(var n:Object in options)if((n.rect.x>=split)==right&&(!cardsOnly||n.tag=="card")){
                if(!pick)pick=n;
                if(n.tag=="card"){pick=n;break;}
            }
            if(pick)select(pick);
        }
        public function focusNearestCard(tag:String,x:Number,y:Number):void
        {
            var best:Object=null;var distance:Number=Number.MAX_VALUE;
            for each(var n:Object in candidates())if(n.tag==tag){
                var dx:Number=n.rect.x+n.rect.width/2-x,dy:Number=n.rect.y+n.rect.height/2-y;
                var d:Number=dx*dx+dy*dy;if(d<distance){distance=d;best=n;}
            }
            getFocus();if(best)select(best);
        }
        public function focusPlacementRow(direction:int):void
        {
            // Shoulder buttons use the same physical order and column as ↑↓,
            // including the reversed opponent half used for spies.
            navigate(direction<0?38:40);
        }
        private function activate():void
        {
            var s:Object=state();if(!s.accept){trace("confirm_blocked");return;}
            if(s.replay){invoke("fast");return;}
            var n:Object=getFocus();if(!n)return;
            if(n.action!=null){invoke("clickSound");n.action.call(owner);}else invoke("inspect",n);
            dirty=true;
        }
        private function tick(e:Event):void
        {
            if(!active){hint.visible=false;return;}
            var now:int=getTimer();var s:Object=state();
            if(!s.typing&&axis>0&&now>=axisNext){axisNext=now+160;navigate(axis);}
            if(yStarted>0&&yCanPass&&!yCommitted&&!s.typing&&now-yStarted>=650&&s.pass) {yCommitted=true;invoke("pass");dirty=true;}
            // Redraw only on changes; animations still move the selected card.
            var n:Object=getFocus();var r:Rectangle=n?bodyBounds(n):null;
            var line:String=s.typing?"Ввод текста в системной клавиатуре":s.hint+(n?"   ·   "+n.label:"");
            if(yStarted>0&&yCanPass&&s.pass&&!yCommitted)line="Удерживайте "+(device==1||device==6?"△":"Y")+" для паса… "+int(Math.min(100,100*(now-yStarted)/650))+"%";
            if(line!=lastHint){
                lastHint=line;hint.text=line;BetaGwentTextLanguage.track(hint);var fontSize:int=18;
                while(hint.textWidth>hint.width-12&&fontSize>14){fontSize--;hint.setTextFormat(new TextFormat("$NormalFont",fontSize,0xF5E6A7));}
                if(fontSize==18)hint.setTextFormat(new TextFormat("$NormalFont",18,0xF5E6A7));
                dirty=true;
            }
            if(!dirty&&r&&lastRect&&r.equals(lastRect))return;
            dirty=false;graphics.clear();hint.visible=!s.typing;hint.y=s.hintY;
            graphics.beginFill(0x10191F,.95);graphics.drawRoundRect(24,s.hintY-2,1872,31,6,6);graphics.endFill();
            graphics.lineStyle(1,0x92784E,.8);graphics.moveTo(32,s.hintY+29);graphics.lineTo(1888,s.hintY+29);
            if(yStarted>0&&yCanPass&&s.pass&&!yCommitted){
                graphics.beginFill(0xF0D18C,.9);graphics.drawRect(32,s.hintY+26,1856*Math.min(1,(now-yStarted)/650),3);graphics.endFill();dirty=true;
            }
            if(n&&!s.typing){
                lastRect=r.clone();lastKey=n.key;
                graphics.lineStyle(3,0xF5E6A7,1);
                if(n.body){
                    // Short corner marks leave card art and insertion ghosts readable.
                    var corners:Array=bodyCorners(n);
                    for(var i:int=0;i<4;i++){
                        var point:Point=corners[i],previous:Point=corners[(i+3)%4],next:Point=corners[(i+1)%4];
                        var edgeX:Number=next.x-point.x,edgeY:Number=next.y-point.y;
                        var ratio:Number=Math.min(.3,16/Math.max(1,Math.sqrt(edgeX*edgeX+edgeY*edgeY)));
                        graphics.moveTo(point.x+edgeX*ratio,point.y+edgeY*ratio);graphics.lineTo(point.x,point.y);
                        edgeX=previous.x-point.x;edgeY=previous.y-point.y;ratio=Math.min(.3,16/Math.max(1,Math.sqrt(edgeX*edgeX+edgeY*edgeY)));
                        graphics.lineTo(point.x+edgeX*ratio,point.y+edgeY*ratio);
                    }
                }else graphics.drawRoundRect(r.x,r.y,r.width,r.height,4,4);
            }
        }
    }
}
