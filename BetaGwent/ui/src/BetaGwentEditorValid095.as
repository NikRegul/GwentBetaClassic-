package {
    import flash.display.Sprite;
    import flash.geom.ColorTransform;
    // UIDBPrefab/DeckStatsWidget/ValidVFX: source AdditiveAlpha One/One.
    // The atlas holds textureRGB*textureAlpha^2 with output alpha=1.
    public class BetaGwentEditorValid095 extends Sprite {
        private var unit:Number;
        private var cells:Array=[];
        private var shown:int=-2;
        public var available:Boolean=true;
        public function BetaGwentEditorValid095(widgetWidth:Number) {
            mouseEnabled=false;mouseChildren=false;unit=widgetWidth/400;
            for(var i:int=0;i<4;i++){
                var cell:Sprite=BetaGwentElementArt164.region(28,BetaGwentEditorValidData095.RECT,128,128);
                if(!cell){available=false;break;}
                cell.mouseEnabled=false;cell.mouseChildren=false;cell.blendMode="add";
                cell.visible=false;cells.push(cell);addChild(cell);
            }
            render(0);
        }
        public function render(progress:Number):void {
            var index:int=progress>=0&&progress<1?Math.min(47,int(progress*47)):-1;
            if(index==shown)return;shown=index;
            for each(var cell:Sprite in cells)cell.visible=false;
            if(index<0||!available)return;
            var frame:Array=BetaGwentEditorValidData095.FRAMES[index];
            for(var i:int=0;i<frame.length;i++){
                var p:Array=frame[i];cell=cells[i];cell.visible=true;
                cell.x=Number(p[0])*unit;cell.y=(Number(p[1])-15)*unit;
                cell.scaleX=Number(p[2])*unit/128;
                cell.scaleY=-Number(p[3])*unit/128;
                cell.rotation=Number(p[4]);
                // Vertex alpha attenuates RGB; applying display alpha too would
                // multiply it twice. Retain material brightness 2, output alpha1.
                var a:Number=2*Number(p[8]);
                cell.transform.colorTransform=new ColorTransform(Number(p[5])*a,Number(p[6])*a,Number(p[7])*a,1);
            }
        }
    }
}
