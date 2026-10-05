package mx.core
{
    import flash.display.Bitmap;
    import flash.display.BitmapData;
    // Minimal embed carrier for the standalone AS3 root; no Flex UI framework.
    public class BitmapAsset extends Bitmap
    {
        public function BitmapAsset(data:BitmapData=null, pixelSnapping:String="auto", smoothing:Boolean=false)
        { super(data, pixelSnapping, smoothing); }
    }
}
