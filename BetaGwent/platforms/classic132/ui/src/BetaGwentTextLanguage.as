package
{
    import flash.text.TextField;
    import flash.text.TextFormat;
    import flash.utils.Dictionary;
    import flash.display.Loader;
    import flash.events.Event;
    import flash.events.IOErrorEvent;
    import flash.events.SecurityErrorEvent;
    import flash.net.URLRequest;

    public class BetaGwentTextLanguage
    {
        // The English source builder changes only this package default.
        public static const DEFAULT_LANGUAGE:int=1;
        public static var language:int=DEFAULT_LANGUAGE;
        public static var pendingLanguage:int=0;
        public static const CODES:Array=["","ru_ru","en_us","de_de","fr_fr","it_it","pl_pl","es_es","es_mx","pt_br","jp_jp","kr_kr","zh_cn","zh_tw"];
        public static const LABELS:Array=["","Русский","English","Deutsch","Français","Italiano","Polski","Español","Español (Latinoamérica)","Português (Brasil)","日本語","한국어","简体中文","繁體中文"];
        private static var resourceLoader:Loader;
        private static var pendingLoader:Loader;
        private static var bodyFont:String;
        private static var titleFont:String;
        private static var fontCharacters:String="";
        public static var changed:Function;
        private static var fields:Dictionary=new Dictionary(true);
        private static var maps:Array;
        private static var groups:Array;
        private static var protectedNames:Object={};
        private static var caches:Array=[];
        private static var cacheCount:int=0;

        public static function protect(value:String):void
        { if(value){protectedNames[value]=true;protectedNames[value.toUpperCase()]=true;caches=[];cacheCount=0;} }
        private static function initialize():void
        {
            if(maps)return;
            for each(var name:String in LABELS)if(name)protectedNames[name]=true;
            maps=[];groups=[];
            for(var lang:int=1;lang<=13;lang++){maps[lang]={};groups[lang]={};}
        }
        private static function indexLanguage(value:int,data:Object):void
        {
            initialize();
            data=BetaGwentUiText142.extend(value,data);
            for(var old:int=1;old<=13;old++){maps[old]={};groups[old]={};}
            maps[value]=data;caches=[];cacheCount=0;
                for(var key:String in data){
                    if(key.length==0)continue;
                    var head:String=key.charAt(0);
                    if(!groups[value][head])groups[value][head]=[];
                    groups[value][head].push(key);
                }
                for(head in groups[value])groups[value][head].sort(longest);
        }
        private static function longest(a:String,b:String):Number{return b.length-a.length;}
        // TextField.text reads paragraph breaks back as "\r"; dictionaries use "\n".
        public static function normalize(value:String):String
        { return value&&value.indexOf("\r")>=0?value.split("\r\n").join("\n").split("\r").join("\n"):value; }
        private static function word(c:String):Boolean{return c.length>0&&/[A-Za-z0-9_А-Яа-яЁё]/.test(c);}
        public static function translate(value:String,target:int=0):String
        {
            if(!value)return value;
            value=normalize(value);
            if(target==0)target=language;
            if(target==1||target<1||target>13)return value;
            initialize();
            if(protectedNames[value])return value;
            if(!caches[target])caches[target]={};
            if(caches[target].hasOwnProperty(value))return caches[target][value];
            var result:String="";
            if(maps[target].hasOwnProperty(value))result=maps[target][value];
            else{
                var at:int=0;
                while(at<value.length){
                    var chosen:String=null;
                    // Saved deck names are opaque even inside a confirmation or heading.
                    for(var name:String in protectedNames)if(value.substr(at,name.length)==name&&(!chosen||name.length>chosen.length))chosen=name;
                    if(chosen){result+=chosen;at+=chosen.length;continue;}
                    var candidates:Array=groups[target][value.charAt(at)];
                    if(candidates)for each(var key:String in candidates){
                        if(value.substr(at,key.length)!=key)continue;
                        if(word(key.charAt(0))&&at>0&&word(value.charAt(at-1)))continue;
                        if(word(key.charAt(key.length-1))&&word(value.charAt(at+key.length)))continue;
                        chosen=key;break;
                    }
                    if(chosen){result+=maps[target][chosen];at+=chosen.length;}
                    else{result+=value.charAt(at);at++;}
                }
            }
            if(cacheCount++>4096){caches=[];caches[target]={};cacheCount=0;}
            caches[target][value]=result;return result;
        }
        public static function track(field:TextField):void
        {
            if(!field||field.type=="input")return;
            var raw:String=normalize(field.text);
            fields[field]={raw:raw,shown:raw,format:field.getTextFormat(),face:field.getTextFormat().font,embedded:field.embedFonts};
            update(field,fields[field]);
        }
        public static function forget(field:TextField):void{delete fields[field];}
        // Replace a tracked field's source text and show the translation in the same frame.
        public static function assign(field:TextField,value:String):void
        {
            if(!field)return;
            if(field.type=="input"||!fields[field]){field.text=value==null?"":value;if(field.type!="input")track(field);return;}
            var state:Object=fields[field];state.shown=normalize(field.text);state.raw=normalize(value==null?"":value);update(field,state);
        }
        // Cheap per-frame pass: only fields whose text was replaced outside assign().
        public static function sweep():void
        {
            for(var item:Object in fields){
                var field:TextField=item as TextField;var state:Object=fields[item];
                if(field&&state&&field.text!==state.seen)update(field,state);
            }
        }
        // True once the selected language resource (dictionary and fonts) is in use.
        public static function loaded():Boolean{return resourceLoader!=null&&pendingLoader==null;}
        private static function update(field:TextField,state:Object):void
        {
            if(field.type=="input")return;
            if(normalize(field.text)!=state.shown)state.raw=normalize(field.text);
            var shown:String=translate(state.raw);
            var format:TextFormat=field.getTextFormat();var scroll:int=field.scrollV;
            if(normalize(field.text)!=shown)field.text=shown;
            if(bodyFont&&state.face!=BetaGwentFonts.NUMBERS&&hasGlyphs(shown)){
                var original:String=String(state.face);
                format.font=original==BetaGwentFonts.TITLE?titleFont:bodyFont;
                format.bold=original==BetaGwentFonts.TITLE;
                field.embedFonts=true;
            }else if(bodyFont&&state.face!=BetaGwentFonts.NUMBERS){
                format.font="$NormalFont";field.embedFonts=false;
            }
            field.defaultTextFormat=format;field.setTextFormat(format);field.scrollV=scroll;
            state.shown=shown;state.seen=field.text;
        }
        public static function font(field:TextField,face:String):Boolean
        { if(field.type=="input")return false;if(!fields[field])track(field);fields[field].face=face;if(bodyFont)update(field,fields[field]);return bodyFont!=null; }
        private static function hasGlyphs(value:String):Boolean
        { for(var i:int=0;i<value.length;i++){var c:String=value.charAt(i);if(c!="\n"&&c!="\r"&&fontCharacters.indexOf(c)<0)return false;}return true; }
        public static function refresh():void
        { for(var item:Object in fields){var field:TextField=item as TextField;if(field)update(field,fields[field]);} }
        public static function select(value:int):void
        {
            value=value>=1&&value<=13?value:DEFAULT_LANGUAGE;
            if(pendingLanguage==value&&pendingLoader||language==value&&resourceLoader&&!pendingLoader)return;
            initialize();
            if(pendingLoader){try{pendingLoader.close();}catch(cancel:Error){}try{pendingLoader.unloadAndStop(true);}catch(unload:Error){}}
            var loading:Loader=new Loader();pendingLoader=loading;pendingLanguage=value;
            loading.contentLoaderInfo.addEventListener(Event.COMPLETE,languageLoaded);
            loading.contentLoaderInfo.addEventListener(IOErrorEvent.IO_ERROR,languageFailed);
            loading.contentLoaderInfo.addEventListener(SecurityErrorEvent.SECURITY_ERROR,languageFailed);
            try{loading.load(new URLRequest("swf/betagwenttext/"+CODES[value]+".swf"));}catch(error:Error){languageFailed(null);}
            refresh();
        }
        private static function languageLoaded(e:Event):void
        {
            if(!pendingLoader||e.currentTarget!=pendingLoader.contentLoaderInfo)return;
            var data:Object=Object(pendingLoader.content);
            language=pendingLanguage;pendingLanguage=0;
            indexLanguage(language,data.dictionary());bodyFont=data.bodyFont;titleFont=data.titleFont;fontCharacters=data.characters;
            var old:Loader=resourceLoader;resourceLoader=pendingLoader;pendingLoader=null;refresh();
            if(old){try{old.unloadAndStop(true);}catch(error:Error){}}
            if(changed!=null)changed();
        }
        private static function languageFailed(e:Event):void
        {
            if(pendingLoader&&(!e||e.currentTarget==pendingLoader.contentLoaderInfo)){
                trace("UI_ERROR text_language_load_failed="+pendingLanguage+" retained="+language);
                pendingLoader.unloadAndStop(true);pendingLoader=null;pendingLanguage=0;refresh();if(changed!=null)changed();
            }
        }
        public static function label():String{return LABELS[language];}
        public static function search(value:String,query:String):Boolean
        { return value.toLowerCase().indexOf(query.toLowerCase())>=0||translate(value).toLowerCase().indexOf(query.toLowerCase())>=0; }
    }
}
