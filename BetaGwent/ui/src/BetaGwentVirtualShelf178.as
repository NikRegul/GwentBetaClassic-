package {
    import flash.display.Sprite;
    import flash.display.Shape;
    // One masked viewport with only the intersecting rows instantiated. The
    // atlas cells themselves never use scrollRect or a transformed crop.
    public class BetaGwentVirtualShelf178 extends Sprite {
        public var body:Sprite=new Sprite();
        public var layout:Object;
        public function BetaGwentVirtualShelf178(count:int,columns:int,rowHeight:Number,w:Number,h:Number,offset:Number) {
            layout=window(count,columns,rowHeight,h,offset);
            addChild(body);
            // Scaleform hit-tests a mask that sits above the content and routes the
            // press to this container. Keep the mask below the cards and inert.
            var clip:Sprite=new Sprite();clip.mouseEnabled=false;clip.mouseChildren=false;
            clip.graphics.beginFill(0);clip.graphics.drawRect(0,0,w,h);clip.graphics.endFill();addChildAt(clip,0);body.mask=clip;
            graphics.beginFill(0,0);graphics.drawRect(0,0,w,h);graphics.endFill();
        }
        public static function window(count:int,columns:int,rowHeight:Number,height:Number,offset:Number):Object {
            count=Math.max(0,count);columns=Math.max(1,columns);rowHeight=Math.max(1,rowHeight);height=Math.max(1,height);
            var total:Number=Math.ceil(count/columns)*rowHeight;
            var max:Number=Math.max(0,total-height);offset=Math.max(0,Math.min(max,offset));
            var first:int=int(offset/rowHeight)*columns;
            return {count:count,columns:columns,rowHeight:rowHeight,height:height,total:total,max:max,offset:offset,
                first:first,end:Math.min(count,(int(offset/rowHeight)+int(Math.ceil(height/rowHeight))+1)*columns)};
        }
        public static function ensure(index:int,columns:int,rowHeight:Number,height:Number,offset:Number):Number {
            var top:Number=int(Math.max(0,index)/Math.max(1,columns))*rowHeight;
            if(top<offset)return top;
            if(top+rowHeight>offset+height)return Math.max(0,top+rowHeight-height);
            return offset;
        }
        public static function card(source:Object,pane:String,index:int,x:Number,y:Number,w:Number,h:Number):Object {
            var view:Object={};for(var key:String in source)view[key]=source[key];
            view.viewKey=pane+source.templateId;view.shelfPane=pane;view.shelfIndex=index;view.shelfClip={x:x,y:y,w:w,h:h};return view;
        }
        public static function position(mask:int,typeMask:int,position:int):Boolean {
            if(position==0)return true;
            if(position==5)return typeMask==2;
            if(typeMask!=4)return false;
            if(position==4)return mask!=0&&(mask&(mask-1))!=0;
            return position>0&&position<4&&mask==[0,1,2,4][position];
        }
    }
}
