package {
    import flash.display.Sprite;
    import flash.geom.ColorTransform;
    // Beta UIDBSlotAdd / UIDBSlotRemove / UIDBCounter on a deck row.
    // Shader VFX/Common/AdditiveAlpha (One/One): the atlas holds
    // textureRGB*textureAlpha^2 with alpha 1; RGB is multiplied by the source
    // vertex colour x Brightness x vertex alpha. Each quad is additive itself.
    public class BetaGwentEditorSlot096 extends Sprite {
        public static const ADD:int=0,REMOVE:int=1,COUNTER:int=2;
        private var frames:Array;
        private var unitX:Number,unitY:Number;
        private var pool:Object={};
        private var shown:int=-2;
        public var available:Boolean=true;
        public var ms:Number;
        // Origin: the row's top centre. slotWidth/slotHeight: the drawn deck row.
        public function BetaGwentEditorSlot096(kind:int,slotWidth:Number,slotHeight:Number) {
            mouseEnabled=false;mouseChildren=false;
            frames=kind==ADD?BetaGwentEditorSlotData096.ADD:kind==REMOVE?BetaGwentEditorSlotData096.REMOVE:BetaGwentEditorSlotData096.COUNTER;
            ms=kind==ADD?BetaGwentEditorSlotData096.ADD_MS:kind==REMOVE?BetaGwentEditorSlotData096.REMOVE_MS:BetaGwentEditorSlotData096.COUNTER_MS;
            unitX=slotWidth/292;unitY=slotHeight/37;
            // A menu whose native atlas lacks the cells plays nothing.
            for(var key:String in BetaGwentEditorSlotData096.RECTS)if(!take(int(key),0)){available=false;break;}
            render(0);
        }
        private function take(index:int,n:int):Sprite {
            var list:Array=pool[index];if(!list){list=[];pool[index]=list;}
            while(list.length<=n){
                var cell:Sprite=BetaGwentElementArt164.region(index,BetaGwentEditorSlotData096.RECTS[index],100,100);
                if(!cell)return null;
                cell.mouseEnabled=false;cell.mouseChildren=false;cell.blendMode="add";cell.visible=false;
                list.push(cell);addChild(cell);
            }
            return list[n];
        }
        public function render(progress:Number):void {
            var index:int=progress>=0&&progress<1?Math.min(frames.length-1,int(progress*frames.length)):-1;
            if(index==shown)return;shown=index;
            for(var key:String in pool)for each(var hidden:Sprite in pool[key])hidden.visible=false;
            if(index<0||!available)return;
            var used:Object={};
            for each(var p:Array in frames[index]){
                var id:int=int(p[0]);var n:int=int(used[id]);used[id]=n+1;
                var cell:Sprite=take(id,n);if(!cell)continue;
                cell.visible=true;cell.x=Number(p[1])*unitX;cell.y=Number(p[2])*unitY;
                cell.scaleX=Number(p[3])*unitX/100;cell.scaleY=-Number(p[4])*unitX/100;
                cell.rotation=Number(p[5]);
                var gain:Number=Number(p[9]);
                cell.transform.colorTransform=new ColorTransform(Number(p[6])*gain,Number(p[7])*gain,Number(p[8])*gain,1);
            }
        }
    }
}
