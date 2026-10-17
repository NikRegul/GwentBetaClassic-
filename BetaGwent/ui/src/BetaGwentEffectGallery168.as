package {
    // Presentation fixtures only: no match, collection or reward operations.
    public class BetaGwentEffectGallery168 {
        public static function entries(includeSources:Boolean=false):Array {
            var result:Array=[];
            if(includeSources)for each(var name:String in BetaGwentElementData164.names())result.push({title:name,preset:name,templateId:0,kind:0});
            var cases:Array=[
                [113301,2,"lightning"],[200224,2,"crow"],[201657,2,"parasiteBoost"],[201657,2,"parasiteDamage"],[200301,2,"huntBoost"],
                [113309,3,"burn"],[112102,3,"burn"],[112107,3,"burn"],[113308,3,"poison"],
                [201701,11,"consume"],[132202,11,"consume"],[201648,12,"banish"],
                [113302,4,"frost"],[113206,4,"whiteFrost"],[113101,4,"ragnarok"],[200018,4,"drought"],
                [113303,4,"clear"],[113401,4,"clear"],[201749,4,"froth"],
                [200218,8,"move"],[132407,15,"summon"],[201624,16,"create"],
                [132205,9,"lock"],[113311,2,"armor"],[112101,8,"resilience"],
                [162101,8,"reveal"],[142204,8,"ambush"],[112107,8,"timer"],
                [112101,8,"resilienceHide"],[200118,8,"spy"],[200118,9,"spyHide"],
                [162101,8,"revealHide"],[113311,2,"armorHit"],[113311,2,"armorBreak"],
                [200053,10,"transform"],[112101,1,"play"],
                [132308,1,"playBronze"],[132308,1,"playFrost"],[132308,1,"playFog"],[132308,1,"playRain"],
                [200055,1,"playLeader"]];
            for each(var row:Array in cases){
                card=BetaGwentFullCatalog.find(row[0]);
                result.push({title:row[0]==113401?"Чистое небо":row[2]=="transform"?"Превращение":card?card.title:String(row[0]),templateId:row[0],kind:row[1],mode:row[2],hurting:row[2]!="parasiteBoost"&&row[2]!="huntBoost",count:row[2]=="lightning"||String(row[2]).indexOf("parasite")==0?1:3});
            }
            var cards:Array=BetaGwentFullCatalog.all().concat();
            cards.sort(function(a:Object,b:Object):Number{return a.templateId-b.templateId;});
            var representatives:Array=[],duplicates:Array=[],seen:Object={};
            for each(var card:Object in cards)for each(var hurting:Boolean in [true,false]){
                var p:Object=BetaGwentSpecialVfx.prefabs(card.templateId,hurting);
                if(p){
                    var signature:String=(hurting?"damage:":"boost:")+(p.method==1?p.attack:"")+":"+p.impact+":"+p.element;
                    var sample:Object={title:card.title,templateId:card.templateId,kind:2,hurting:hurting,count:p.method>=2?3:1,
                        mode:(hurting?"Урон":"Усиление")+" · "+(p.attack||p.impact||String(p.element))};
                    if(!seen[signature]){seen[signature]=true;representatives.push(sample);}else duplicates.push(sample);
                }
            }
            result=result.concat(representatives,duplicates);
            // These exercise today's shared battle handlers, including cards
            // without an explicit Beta prefab binding. No raw Side/Row previews.
            result.push({title:"Урон",templateId:113313,kind:2,hurting:true,count:3});
            result.push({title:"Усиление",templateId:113313,kind:2,hurting:false,count:3});
            return result;
        }
        public static function card(id:int,template:int,side:int,zone:int,index:int,power:int=8):Object {
            var definition:Object=BetaGwentFullCatalog.find(template);
            return {id:id,templateId:template,title:definition?definition.title:String(template),side:side,zone:zone,index:index,
                power:power,normalPower:power,armor:0,tokens:0,timer:-1,canPlay:false};
        }
        public static function scene(entry:Object):Object {
            var id:int=int(entry.templateId),mode:String=entry.mode||"",hurting:Boolean=entry.hurting!==false;
            var definition:Object=BetaGwentFullCatalog.find(id),side:int=hurting?2:1;
            var before:Array=[card(1,id>0?id:112101,1,4,0,definition?definition.power:8),
                card(2,112101,side,1,0),card(3,132308,side,2,0),card(4,200299,side,4,side==1?1:0)];
            var after:Array=[];
            for each(var original:Object in before){var copy:Object={};for(var key:String in original)copy[key]=original[key];after.push(copy);}
            var targets:Array=entry.count==3?[2,3,4]:[2];
            var cue:Object={kind:entry.kind,templateId:id,source:1,target:2,side:1,row:0,duration:2500,title:entry.title,
                audioKind:entry.kind==2?(hurting?20:21):entry.kind,attackCount:targets.length,hitTargets:targets};
            var weatherBefore:Array=[],weatherAfter:Array=[];
            if(id==112102&&entry.kind==3)for(var igniIndex:int=1;igniIndex<before.length;igniIndex++){before[igniIndex].zone=1;before[igniIndex].index=igniIndex-1;after[igniIndex].zone=1;after[igniIndex].index=igniIndex-1;}
            if(entry.kind==2)for each(var target:int in targets)after[target-1].power+=mode.indexOf("parasite")==0?(hurting?-9:12):(hurting?-3:3);
            if(mode=="armor"){after[1].power=8;after[1].armor=2;cue.audioKind=23;cue.hitTargets=[2];}
            if(entry.kind==3||mode=="consume"||mode=="banish"){
                cue.targetView=before[1];
                var victims:Array=entry.kind==3?[2,3,4]:[2];
                for(var victimIndex:int=after.length-1;victimIndex>=0;victimIndex--)if(victims.indexOf(int(after[victimIndex].id))>=0)after.splice(victimIndex,1);
                cue.hitTargets=victims;cue.attackCount=victims.length;
                if(mode=="consume")after[0].power+=8;
            }
            if(mode=="move"){before[1].zone=2;before[1].index=1;after[1].zone=1;after[1].index=0;cue.hitTargets=[];}
            if(mode=="lock")after[1].tokens=4;
            if(mode=="resilience")after[1].tokens=1;
            if(mode=="resilienceHide")before[1].tokens=1;
            if(mode=="spy")after[1].tokens=128;
            if(mode=="spyHide"){before[1].tokens=128;after[1].tokens=4;}
            if(mode=="reveal"||mode=="revealHide"){
                before[1].zone=8;after[1].zone=8;before[1].side=1;after[1].side=1;
                if(mode=="reveal")after[1].tokens=64;else before[1].tokens=64;
            }
            if(mode=="armorHit"||mode=="armorBreak"){
                before[1].armor=4;after[1].armor=mode=="armorHit"?2:0;after[1].power=8;
                cue.audioKind=22;cue.hitTargets=[2];
            }
            if(mode=="ambush"){before[1].templateId=142204;after[1].templateId=142204;before[1].tokens=8;}
            if(mode=="timer"){before[1].timer=2;after[1].timer=1;cue.audioKind=32;}
            if(mode=="transform"){before[1].templateId=132308;after[1].templateId=200307;var transformed:Object=BetaGwentFullCatalog.find(200307);if(transformed){after[1].title=transformed.title;after[1].power=transformed.power;after[1].normalPower=transformed.power;}}
            if(mode=="summon"||mode=="create"){before[1].zone=16;cue.targetView=before[1];}
            if(mode.indexOf("play")==0){before[0].zone=8;after[0].zone=1;after[0].index=1;cue.target=1;}
            if(mode=="playFrost"||mode=="playFog"||mode=="playRain"){
                var landingToken:int=mode=="playFrost"?1:mode=="playFog"?2:4;
                weatherBefore.push({side:1,zone:1,token:landingToken,damage:2});weatherAfter.push({side:1,zone:1,token:landingToken,damage:2});
            }
            if(entry.kind==4){
                var token:int=mode=="frost"||mode=="whiteFrost"?1:mode=="ragnarok"?32:mode=="drought"?16:mode=="froth"?128:0;
                var lanes:Array=mode=="whiteFrost"?[1,2]:mode=="frost"||mode=="froth"?[1]:[1,2,4];
                cue.side=mode=="clear"||mode=="froth"?1:2;cue.row=mode=="clear"?0:lanes[0];cue.weatherCastRows=[];
                for each(var lane:int in lanes){
                    cue.weatherCastRows.push({side:cue.side,zone:lane});
                    if(mode=="clear")weatherBefore.push({side:1,zone:lane,token:1,damage:2});
                    else weatherAfter.push({side:cue.side,zone:lane,token:token,damage:2});
                }
            }
            return {before:before,after:after,cue:cue,weatherBefore:weatherBefore,weatherAfter:weatherAfter};
        }
    }
}
