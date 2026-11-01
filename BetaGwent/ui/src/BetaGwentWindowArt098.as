package {
    import flash.display.Sprite;
    import flash.display.Bitmap;
    // Original Beta picker sprites; unused cells of the existing page-18 atlas.
    public class BetaGwentWindowArt098 {
        public static const MAP_LEFT:int=0,MAP_RIGHT:int=1,TITLE:int=2,SLOT:int=3,CROWN:int=4,ROD_TOP:int=5,ROD_MIDDLE:int=6,ROD_BOTTOM:int=7,DIVIDER:int=8;
        public static const WOOD_FIRST:int=9;
        public static const PAPER_FIRST:int=18;
        private static const RECTS:Array=[[4,248,176,160],[820,436,176,160],[520,1080,320,44],[856,184,64,80],[928,184,48,48],[1000,4,20,48],[1000,60,20,12],[1000,80,20,48],[1000,136,12,256],[333,0,16,16],[349,0,480,16],[829,0,16,16],[333,16,16,396],[349,16,480,396],[829,16,16,396],[333,412,16,16],[349,412,480,16],[829,412,16,16],[0,1178,687,48],[0,1226,687,287],[0,1513,687,48]];
        private static const TYPES:Array=[BetaGwentWindowCell098_0,BetaGwentWindowCell098_1,BetaGwentWindowCell098_2,BetaGwentWindowCell098_3,BetaGwentWindowCell098_4,BetaGwentWindowCell098_5,BetaGwentWindowCell098_6,BetaGwentWindowCell098_7,BetaGwentWindowCell098_8,BetaGwentWindowCell098_9,BetaGwentWindowCell098_10,BetaGwentWindowCell098_11,BetaGwentWindowCell098_12,BetaGwentWindowCell098_13,BetaGwentWindowCell098_14,BetaGwentWindowCell098_15,BetaGwentWindowCell098_16,BetaGwentWindowCell098_17,BetaGwentWindowCell098_18,BetaGwentWindowCell098_19,BetaGwentWindowCell098_20];
        public static function cell(id:int,w:Number,h:Number):Sprite {
            var r:Array=RECTS[id];if(!r)return null;
            var type:Class=TYPES[id];var bitmap:Bitmap=new type() as Bitmap;
            if(bitmap&&bitmap.width>0&&bitmap.height>0){
                var bound:Sprite=new Sprite();bound.mouseEnabled=false;bound.mouseChildren=false;
                bitmap.smoothing=true;bitmap.pixelSnapping="never";bitmap.scaleX=w/bitmap.width;bitmap.scaleY=h/bitmap.height;bound.addChild(bitmap);return bound;
            }
            if(id>=PAPER_FIRST)return BetaGwentHDArt.clip(BetaGwentHud104.PARCHMENT,w,h,r[0],r[1]-1178,r[2],r[3]);
            return BetaGwentHDArt.clip(BetaGwentDeckArt104.WOOD_LARGE,w,h,r[0]-333,r[1],r[2],r[3]);
        }
    }
}
