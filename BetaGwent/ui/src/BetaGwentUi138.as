package {
    // Presentation state only. Rules, random seeds, inventory and AI are never changed here.
    public class BetaGwentUi138 {
        public static var flashes:Boolean=true;
        public static var shake:Boolean=true;
        public static var scenes:int=1; // 0 off, 1 short, 2 full.
        public static var chains:Boolean=true;
        public static var filters:Object={};
        public static function sceneDuration(reduced:Boolean):Number {
            return reduced||scenes==0?0:scenes==1?700:1200;
        }
        public static function publicCard(c:Object):Boolean {
            if(!c||c.hidden||int(c.templateId)<=0)return false;
            if((int(c.zone)&7)!=0&&(int(c.tokens)&8)!=0)return false;
            return !(int(c.side)==2&&(int(c.zone)==16||int(c.zone)==8&&(int(c.tokens)&64)==0));
        }
        public static function view(c:Object):Object {
            if(!publicCard(c))return null;
            // Snapshot only fields already public in this frame. Never retain incoming hidden data.
            return {id:c.id,templateId:c.templateId,title:c.title,power:c.power,normalPower:c.normalPower,
                armor:c.armor,tokens:c.tokens,timer:c.timer,side:c.side,zone:c.zone,created:c.created};
        }
        public static function stateLines(c:Object,base:Object):String {
            if(!publicCard(c))return "";
            var lines:Array=[];
            if(base&&int(base.typeMask)==4&&c.power!=null){
                lines.push("Базовая сила: "+base.power);
                if(c.normalPower!=null)lines.push("Нормальная сила: "+c.normalPower);
                lines.push("Текущая сила: "+c.power);
                if(c.normalPower!=null){var net:int=int(c.power)-int(c.normalPower);
                    if(net!=0)lines.push("Изменение силы: "+(net>0?"+":"")+net);}
            }
            if(c.armor!=null)lines.push("Броня: "+int(c.armor));
            if((int(c.tokens)&512)!=0)lines.push("Обречённость");
            if((int(c.tokens)&64)!=0&&int(c.zone)==8)lines.push("Раскрыта сопернику");
            return lines.join("\n");
        }
        public static function effect(cue:Object,before:Object,after:Object):String {
            if(!cue)return "";
            if(int(cue.kind)==12)return "banish";
            if(int(cue.kind)==11)return "consume";
            if(int(cue.kind)==13)return "deathwish";
            if(int(cue.kind)==16)return "create";
            if((int(cue.kind)==1||int(cue.kind)==15)&&cue.title&&
                (String(cue.title).indexOf("Из сброса")==0||String(cue.title).indexOf("Возвращение из сброса")==0))return "resurrect";
            if(int(cue.kind)==2&&before&&after){
                if(int(after.power)<int(before.power)||int(after.armor)<int(before.armor))return "damage";
                // A positive delta alone cannot distinguish healing from boost; call it recovery
                // only when the normal-power boundary was not exceeded and did not change.
                if(before.normalPower!=null&&after.normalPower!=null&&
                    int(before.normalPower)==int(after.normalPower)&&int(before.power)<int(before.normalPower)&&
                    int(after.power)>int(before.power)&&int(after.power)<=int(after.normalPower))return "recovery";
                if(int(after.power)>int(before.power))return "boost";
            }
            return "";
        }
        public static function deckReasons(total:int,golds:int,silvers:int):Array {
            var reasons:Array=[];
            if(total<25)reasons.push("Не хватает карт: "+(25-total));
            if(total>40)reasons.push("Лишних карт: "+(total-40));
            if(golds>4)reasons.push("Лишних золотых: "+(golds-4));
            if(silvers>6)reasons.push("Лишних серебряных: "+(silvers-6));
            return reasons;
        }
        public static function missingCost(deck:Array,owned:Object,cost:Function):int {
            var total:int=0;
            for each(var c:Object in deck)total+=Math.max(0,int(c.copies)-int(owned[c.templateId]))*int(cost(c));
            return total;
        }
        public static function handOffsets(hand:Array,focusId:int,gap:Number):Object {
            var result:Object={},rank:int=-1;
            for(var i:int=0;i<hand.length;i++)if(int(hand[i].id)==focusId){rank=i;break;}
            var last:int=hand.length-1;
            for(i=0;i<hand.length;i++)result[hand[i].id]=rank<0||i==rank?0:
                i<rank?-gap*i/Math.max(1,rank-1):gap*(last-i)/Math.max(1,last-rank-1);
            return result;
        }
    }
}
