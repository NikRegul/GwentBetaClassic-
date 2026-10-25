// Exact source graph request node IDs and hints; phase mapping is handwritten.
struct SBetaOriginalSourceHint { var node, sourceHint : int; var kind : string; }
function BetaOriginalSourceRequests(source : int, out hints : array<SBetaOriginalSourceHint>) {
    hints.Clear();
    if(source>=112102 && source<=112212){BetaOriginalSourceHints0(source,hints);return;}
    if(source>=112214 && source<=113303){BetaOriginalSourceHints1(source,hints);return;}
    if(source>=113305 && source<=122103){BetaOriginalSourceHints2(source,hints);return;}
    if(source>=122104 && source<=122301){BetaOriginalSourceHints3(source,hints);return;}
    if(source>=122302 && source<=132106){BetaOriginalSourceHints4(source,hints);return;}
    if(source>=132107 && source<=132312){BetaOriginalSourceHints5(source,hints);return;}
    if(source>=132313 && source<=142107){BetaOriginalSourceHints6(source,hints);return;}
    if(source>=142108 && source<=142311){BetaOriginalSourceHints7(source,hints);return;}
    if(source>=142312 && source<=152205){BetaOriginalSourceHints8(source,hints);return;}
    if(source>=152206 && source<=152317){BetaOriginalSourceHints9(source,hints);return;}
    if(source>=153201 && source<=162206){BetaOriginalSourceHints10(source,hints);return;}
    if(source>=162207 && source<=162310){BetaOriginalSourceHints11(source,hints);return;}
    if(source>=162313 && source<=200030){BetaOriginalSourceHints12(source,hints);return;}
    if(source>=200031 && source<=200062){BetaOriginalSourceHints13(source,hints);return;}
    if(source>=200067 && source<=200124){BetaOriginalSourceHints14(source,hints);return;}
    if(source>=200132 && source<=200163){BetaOriginalSourceHints15(source,hints);return;}
    if(source>=200164 && source<=200220){BetaOriginalSourceHints16(source,hints);return;}
    if(source>=200221 && source<=200299){BetaOriginalSourceHints17(source,hints);return;}
    if(source>=200300 && source<=201579){BetaOriginalSourceHints18(source,hints);return;}
    if(source>=201580 && source<=201599){BetaOriginalSourceHints19(source,hints);return;}
    if(source>=201603 && source<=201627){BetaOriginalSourceHints20(source,hints);return;}
    if(source>=201628 && source<=201647){BetaOriginalSourceHints21(source,hints);return;}
    if(source>=201648 && source<=201690){BetaOriginalSourceHints22(source,hints);return;}
    if(source>=201691 && source<=201708){BetaOriginalSourceHints23(source,hints);return;}
    if(source>=201725 && source<=201772){BetaOriginalSourceHints24(source,hints);return;}
    if(source>=201773 && source<=201780){BetaOriginalSourceHints25(source,hints);return;}
}
function BetaOriginalSourceHints0(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 112102:
        h.node=104;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 112104:
        h.node=19;h.sourceHint=37;h.kind="targets";hints.PushBack(h);
        break;
    case 112105:
        h.node=129;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 112106:
        h.node=107;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 112108:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    case 112109:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    case 112111:
        h.node=81;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 112201:
        h.node=18;h.sourceHint=37;h.kind="targets";hints.PushBack(h);
        break;
    case 112205:
        h.node=44;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 112208:
        h.node=21;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 112211:
        h.node=30;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 112212:
        h.node=17;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints1(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 112214:
        h.node=36;h.sourceHint=39;h.kind="targets";hints.PushBack(h);
        break;
    case 113102:
        h.node=113;h.sourceHint=28;h.kind="choices";hints.PushBack(h);
        break;
    case 113201:
        h.node=7;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 113202:
        h.node=7;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 113203:
        h.node=7;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 113205:
        h.node=330;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 113206:
        h.node=7;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 113207:
        h.node=204;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 113208:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    case 113301:
        h.node=45;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 113302:
        h.node=7;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 113303:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints2(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 113305:
        h.node=7;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 113306:
        h.node=45;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 113307:
        h.node=33;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 113310:
        h.node=167;h.sourceHint=31;h.kind="targets";hints.PushBack(h);
        break;
    case 113311:
        h.node=215;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 113312:
        h.node=1;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 113313:
        h.node=32;h.sourceHint=37;h.kind="targets";hints.PushBack(h);
        break;
    case 113316:
        h.node=7;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 113319:
        h.node=25;h.sourceHint=32;h.kind="targets";hints.PushBack(h);
        break;
    case 113320:
        h.node=32;h.sourceHint=1;h.kind="templates";hints.PushBack(h);
        h.node=182;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 122102:
        h.node=18;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 122103:
        h.node=38;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints3(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 122104:
        h.node=20;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 122106:
        h.node=27;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 122108:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    case 122201:
        h.node=157;h.sourceHint=31;h.kind="choices";hints.PushBack(h);
        break;
    case 122203:
        h.node=111;h.sourceHint=45;h.kind="choices";hints.PushBack(h);
        break;
    case 122204:
        h.node=566;h.sourceHint=49;h.kind="choices";hints.PushBack(h);
        break;
    case 122205:
        h.node=23;h.sourceHint=30;h.kind="choices";hints.PushBack(h);
        break;
    case 122207:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    case 122211:
        h.node=14;h.sourceHint=32;h.kind="targets";hints.PushBack(h);
        break;
    case 122212:
        h.node=21;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 122216:
        h.node=180;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 122301:
        h.node=111;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints4(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 122302:
        h.node=646;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 122303:
        h.node=25;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 122307:
        h.node=362;h.sourceHint=41;h.kind="targets";hints.PushBack(h);
        break;
    case 122314:
        h.node=7;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 122318:
        h.node=33;h.sourceHint=28;h.kind="targets";hints.PushBack(h);
        break;
    case 122403:
        h.node=59;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 123201:
        h.node=33;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 131101:
        h.node=32;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 131102:
        h.node=17;h.sourceHint=26;h.kind="choices";hints.PushBack(h);
        break;
    case 132102:
        h.node=16;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 132104:
        h.node=60;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 132106:
        h.node=7;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints5(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 132107:
        h.node=7;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 132203:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    case 132204:
        h.node=789;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 132205:
        h.node=7;h.sourceHint=32;h.kind="targets";hints.PushBack(h);
        break;
    case 132211:
        h.node=17;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 132214:
        h.node=22;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 132215:
        h.node=51;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        h.node=615;h.sourceHint=1;h.kind="templates";hints.PushBack(h);
        break;
    case 132216:
        h.node=21;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 132303:
        h.node=45;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 132306:
        h.node=10;h.sourceHint=37;h.kind="choices";hints.PushBack(h);
        break;
    case 132309:
        h.node=16;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 132312:
        h.node=33;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints6(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 132313:
        h.node=40;h.sourceHint=40;h.kind="targets";hints.PushBack(h);
        break;
    case 132314:
        h.node=63;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 132406:
        h.node=49;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 132409:
        h.node=16;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 133301:
        h.node=8;h.sourceHint=31;h.kind="targets";hints.PushBack(h);
        h.node=29;h.sourceHint=37;h.kind="choices";hints.PushBack(h);
        break;
    case 133302:
        h.node=115;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 142101:
        h.node=57;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 142102:
        h.node=7;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 142103:
        h.node=36;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 142105:
        h.node=375;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 142106:
        h.node=7;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 142107:
        h.node=53;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints7(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 142108:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    case 142202:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    case 142203:
        h.node=17;h.sourceHint=45;h.kind="choices";hints.PushBack(h);
        break;
    case 142206:
        h.node=16;h.sourceHint=32;h.kind="targets";hints.PushBack(h);
        break;
    case 142209:
        h.node=36;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 142301:
        h.node=25;h.sourceHint=31;h.kind="targets";hints.PushBack(h);
        break;
    case 142302:
        h.node=7;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 142303:
        h.node=40;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 142305:
        h.node=7;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 142308:
        h.node=50;h.sourceHint=26;h.kind="choices";hints.PushBack(h);
        break;
    case 142310:
        h.node=7;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        h.node=65;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 142311:
        h.node=375;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints8(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 142312:
        h.node=78;h.sourceHint=31;h.kind="choices";hints.PushBack(h);
        break;
    case 142314:
        h.node=39;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 142317:
        h.node=17;h.sourceHint=35;h.kind="targets";hints.PushBack(h);
        break;
    case 143201:
        h.node=35;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 152103:
        h.node=47;h.sourceHint=51;h.kind="choices";hints.PushBack(h);
        break;
    case 152105:
        h.node=7;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 152106:
        h.node=11;h.sourceHint=52;h.kind="choices";hints.PushBack(h);
        h.node=48;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 152107:
        h.node=14;h.sourceHint=32;h.kind="targets";hints.PushBack(h);
        break;
    case 152202:
        h.node=179;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 152203:
        h.node=58;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 152204:
        h.node=7;h.sourceHint=32;h.kind="targets";hints.PushBack(h);
        h.node=65;h.sourceHint=53;h.kind="choices";hints.PushBack(h);
        break;
    case 152205:
        h.node=7;h.sourceHint=35;h.kind="choices";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints9(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 152206:
        h.node=158;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    case 152207:
        h.node=7;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 152211:
        h.node=7;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 152213:
        h.node=62;h.sourceHint=51;h.kind="choices";hints.PushBack(h);
        break;
    case 152214:
        h.node=7;h.sourceHint=45;h.kind="choices";hints.PushBack(h);
        break;
    case 152304:
        h.node=145;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 152306:
        h.node=7;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 152308:
        h.node=48;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 152310:
        h.node=7;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 152311:
        h.node=7;h.sourceHint=35;h.kind="targets";hints.PushBack(h);
        break;
    case 152315:
        h.node=24;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 152317:
        h.node=52;h.sourceHint=36;h.kind="targets";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints10(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 153201:
        h.node=23;h.sourceHint=29;h.kind="choices";hints.PushBack(h);
        h.node=88;h.sourceHint=30;h.kind="choices";hints.PushBack(h);
        break;
    case 153301:
        h.node=1;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 162101:
        h.node=545;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 162102:
        h.node=36;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 162103:
        h.node=19;h.sourceHint=43;h.kind="choices";hints.PushBack(h);
        break;
    case 162104:
        h.node=7;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 162105:
        h.node=14;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        h.node=325;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 162106:
        h.node=31;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 162108:
        h.node=31;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 162202:
        h.node=21;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 162204:
        h.node=17;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 162206:
        h.node=69;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints11(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 162207:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    case 162208:
        h.node=14;h.sourceHint=32;h.kind="targets";hints.PushBack(h);
        break;
    case 162209:
        h.node=69;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 162210:
        h.node=32;h.sourceHint=45;h.kind="choices";hints.PushBack(h);
        break;
    case 162213:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    case 162303:
        h.node=29;h.sourceHint=37;h.kind="targets";hints.PushBack(h);
        break;
    case 162304:
        h.node=7;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 162305:
        h.node=22;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 162306:
        h.node=17;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 162308:
        h.node=180;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        h.node=501;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 162309:
        h.node=266;h.sourceHint=31;h.kind="targets";hints.PushBack(h);
        break;
    case 162310:
        h.node=36;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints12(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 162313:
        h.node=180;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 162314:
        h.node=38;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 162315:
        h.node=64;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 162316:
        h.node=214;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 163101:
        h.node=44;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 163201:
        h.node=18;h.sourceHint=55;h.kind="targets";hints.PushBack(h);
        h.node=139;h.sourceHint=56;h.kind="targets";hints.PushBack(h);
        break;
    case 200020:
        h.node=7;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        h.node=50;h.sourceHint=31;h.kind="targets";hints.PushBack(h);
        break;
    case 200021:
        h.node=63;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200023:
        h.node=197;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200026:
        h.node=362;h.sourceHint=41;h.kind="targets";hints.PushBack(h);
        break;
    case 200028:
        h.node=14;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200030:
        h.node=8;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints13(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 200031:
        h.node=7;h.sourceHint=44;h.kind="choices";hints.PushBack(h);
        h.node=61;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 200032:
        h.node=68;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 200036:
        h.node=7;h.sourceHint=54;h.kind="choices";hints.PushBack(h);
        break;
    case 200037:
        h.node=18;h.sourceHint=42;h.kind="targets";hints.PushBack(h);
        h.node=74;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 200048:
        h.node=52;h.sourceHint=49;h.kind="choices";hints.PushBack(h);
        h.node=295;h.sourceHint=45;h.kind="choices";hints.PushBack(h);
        break;
    case 200049:
        h.node=25;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        h.node=188;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200050:
        h.node=93;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 200053:
        h.node=14;h.sourceHint=32;h.kind="targets";hints.PushBack(h);
        break;
    case 200055:
        h.node=8;h.sourceHint=37;h.kind="targets";hints.PushBack(h);
        break;
    case 200056:
        h.node=93;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 200058:
        h.node=65;h.sourceHint=1;h.kind="templates";hints.PushBack(h);
        break;
    case 200062:
        h.node=39;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints14(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 200067:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        h.node=485;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        h.node=520;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 200071:
        h.node=80;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 200073:
        h.node=53;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 200078:
        h.node=7;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200079:
        h.node=17;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 200083:
        h.node=29;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 200087:
        h.node=93;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 200089:
        h.node=8;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 200102:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        h.node=464;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        h.node=556;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 200105:
        h.node=8;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 200118:
        h.node=180;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200124:
        h.node=22;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints15(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 200132:
        h.node=17;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200138:
        h.node=33;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 200139:
        h.node=263;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 200145:
        h.node=7;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 200146:
        h.node=21;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 200147:
        h.node=21;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200149:
        h.node=167;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 200154:
        h.node=34;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 200158:
        h.node=32;h.sourceHint=1;h.kind="templates";hints.PushBack(h);
        break;
    case 200159:
        h.node=24;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 200162:
        h.node=12;h.sourceHint=30;h.kind="choices";hints.PushBack(h);
        h.node=38;h.sourceHint=28;h.kind="targets";hints.PushBack(h);
        break;
    case 200163:
        h.node=8;h.sourceHint=43;h.kind="choices";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints16(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 200164:
        h.node=34;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 200165:
        h.node=50;h.sourceHint=49;h.kind="choices";hints.PushBack(h);
        h.node=95;h.sourceHint=45;h.kind="choices";hints.PushBack(h);
        break;
    case 200166:
        h.node=7;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 200167:
        h.node=89;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 200169:
        h.node=14;h.sourceHint=32;h.kind="targets";hints.PushBack(h);
        break;
    case 200170:
        h.node=362;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200191:
        h.node=8;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200198:
        h.node=8;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200207:
        h.node=7;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 200209:
        h.node=44;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        h.node=192;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 200218:
        h.node=35;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200220:
        h.node=38;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints17(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 200221:
        h.node=7;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 200222:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        h.node=686;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 200223:
        h.node=32;h.sourceHint=1;h.kind="templates";hints.PushBack(h);
        h.node=182;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200225:
        h.node=7;h.sourceHint=25;h.kind="targets";hints.PushBack(h);
        break;
    case 200227:
        h.node=33;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 200228:
        h.node=7;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 200233:
        h.node=211;h.sourceHint=38;h.kind="targets";hints.PushBack(h);
        break;
    case 200235:
        h.node=17;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200236:
        h.node=181;h.sourceHint=33;h.kind="targets";hints.PushBack(h);
        break;
    case 200237:
        h.node=38;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 200294:
        h.node=46;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200299:
        h.node=21;h.sourceHint=31;h.kind="targets";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints18(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 200300:
        h.node=39;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200502:
        h.node=18;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200518:
        h.node=42;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 200520:
        h.node=47;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 200528:
        h.node=362;h.sourceHint=41;h.kind="targets";hints.PushBack(h);
        break;
    case 200534:
        h.node=40;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 200535:
        h.node=36;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 200539:
        h.node=457;h.sourceHint=41;h.kind="choices";hints.PushBack(h);
        break;
    case 200540:
        h.node=33;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 201523:
        h.node=26;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 201578:
        h.node=166;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 201579:
        h.node=43;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints19(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 201580:
        h.node=74;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 201581:
        h.node=93;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 201582:
        h.node=93;h.sourceHint=1;h.kind="templates";hints.PushBack(h);
        break;
    case 201583:
        h.node=93;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 201584:
        h.node=93;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 201585:
        h.node=93;h.sourceHint=1;h.kind="templates";hints.PushBack(h);
        break;
    case 201587:
        h.node=74;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 201589:
        h.node=74;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 201595:
        h.node=74;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 201597:
        h.node=74;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 201598:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        h.node=349;h.sourceHint=36;h.kind="targets";hints.PushBack(h);
        h.node=375;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 201599:
        h.node=15;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints20(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 201603:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        h.node=484;h.sourceHint=33;h.kind="targets";hints.PushBack(h);
        h.node=599;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 201606:
        h.node=27;h.sourceHint=40;h.kind="targets";hints.PushBack(h);
        break;
    case 201609:
        h.node=500;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201611:
        h.node=18;h.sourceHint=55;h.kind="targets";hints.PushBack(h);
        h.node=139;h.sourceHint=56;h.kind="targets";hints.PushBack(h);
        break;
    case 201612:
        h.node=613;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        h.node=688;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201615:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        h.node=464;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        h.node=597;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 201616:
        h.node=138;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 201618:
        h.node=18;h.sourceHint=48;h.kind="targets";hints.PushBack(h);
        break;
    case 201619:
        h.node=563;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 201621:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        h.node=387;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        h.node=565;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 201625:
        h.node=39;h.sourceHint=50;h.kind="targets";hints.PushBack(h);
        break;
    case 201627:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints21(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 201628:
        h.node=59;h.sourceHint=26;h.kind="choices";hints.PushBack(h);
        break;
    case 201630:
        h.node=73;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 201632:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        break;
    case 201633:
        h.node=48;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 201637:
        h.node=7;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 201638:
        h.node=40;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 201639:
        h.node=24;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 201642:
        h.node=45;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 201643:
        h.node=52;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 201644:
        h.node=16;h.sourceHint=36;h.kind="targets";hints.PushBack(h);
        break;
    case 201645:
        h.node=7;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 201647:
        h.node=18;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints22(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 201648:
        h.node=9;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        h.node=87;h.sourceHint=33;h.kind="targets";hints.PushBack(h);
        h.node=130;h.sourceHint=32;h.kind="targets";hints.PushBack(h);
        break;
    case 201650:
        h.node=40;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 201653:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        h.node=182;h.sourceHint=35;h.kind="targets";hints.PushBack(h);
        h.node=387;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        break;
    case 201656:
        h.node=8;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        h.node=29;h.sourceHint=37;h.kind="choices";hints.PushBack(h);
        break;
    case 201657:
        h.node=30;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201661:
        h.node=73;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201662:
        h.node=11;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        h.node=74;h.sourceHint=34;h.kind="targets";hints.PushBack(h);
        h.node=156;h.sourceHint=33;h.kind="targets";hints.PushBack(h);
        break;
    case 201664:
        h.node=63;h.sourceHint=24;h.kind="choices";hints.PushBack(h);
        break;
    case 201676:
        h.node=58;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 201680:
        h.node=122;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201684:
        h.node=18;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201690:
        h.node=34;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints23(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 201691:
        h.node=9;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201692:
        h.node=8;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201693:
        h.node=106;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 201696:
        h.node=37;h.sourceHint=22;h.kind="choices";hints.PushBack(h);
        break;
    case 201697:
        h.node=32;h.sourceHint=26;h.kind="templates";hints.PushBack(h);
        h.node=387;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        h.node=551;h.sourceHint=33;h.kind="targets";hints.PushBack(h);
        break;
    case 201698:
        h.node=24;h.sourceHint=26;h.kind="choices";hints.PushBack(h);
        break;
    case 201699:
        h.node=7;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 201700:
        h.node=65;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        h.node=89;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 201701:
        h.node=40;h.sourceHint=40;h.kind="targets";hints.PushBack(h);
        break;
    case 201704:
        h.node=38;h.sourceHint=26;h.kind="choices";hints.PushBack(h);
        break;
    case 201707:
        h.node=11;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201708:
        h.node=8;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints24(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 201725:
        h.node=32;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        h.node=1172;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        h.node=1230;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201731:
        h.node=32;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        h.node=1017;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        h.node=1199;h.sourceHint=28;h.kind="targets";hints.PushBack(h);
        h.node=1302;h.sourceHint=23;h.kind="targets";hints.PushBack(h);
        break;
    case 201737:
        h.node=32;h.sourceHint=27;h.kind="templates";hints.PushBack(h);
        h.node=1166;h.sourceHint=38;h.kind="targets";hints.PushBack(h);
        h.node=1241;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201743:
        h.node=27;h.sourceHint=40;h.kind="targets";hints.PushBack(h);
        break;
    case 201744:
        h.node=8;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 201748:
        h.node=44;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201749:
        h.node=8;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 201753:
        h.node=8;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 201759:
        h.node=8;h.sourceHint=1;h.kind="templates";hints.PushBack(h);
        h.node=710;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        h.node=1110;h.sourceHint=1;h.kind="locations";hints.PushBack(h);
        break;
    case 201762:
        h.node=149;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201765:
        h.node=8;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201772:
        h.node=12;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    }
}
function BetaOriginalSourceHints25(source : int, out hints : array<SBetaOriginalSourceHint>) {
    var h : SBetaOriginalSourceHint;
    switch(source) {
    case 201773:
        h.node=69;h.sourceHint=1;h.kind="templates";hints.PushBack(h);
        break;
    case 201776:
        h.node=98;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    case 201777:
        h.node=46;h.sourceHint=1;h.kind="targets";hints.PushBack(h);
        break;
    case 201780:
        h.node=35;h.sourceHint=1;h.kind="choices";hints.PushBack(h);
        break;
    }
}
function BetaOriginalHasPlayCardsNode(source : int) : bool {
    switch(source) {
    case 112108: return true;
    case 112109: return true;
    case 112112: return true;
    case 113102: return true;
    case 113201: return true;
    case 113208: return true;
    case 113209: return true;
    case 113303: return true;
    case 113316: return true;
    case 122103: return true;
    case 122105: return true;
    case 122106: return true;
    case 122108: return true;
    case 122205: return true;
    case 122207: return true;
    case 122208: return true;
    case 122307: return true;
    case 122403: return true;
    case 123201: return true;
    case 131101: return true;
    case 131102: return true;
    case 132106: return true;
    case 132203: return true;
    case 132215: return true;
    case 132220: return true;
    case 132402: return true;
    case 132406: return true;
    case 133302: return true;
    case 142102: return true;
    case 142106: return true;
    case 142107: return true;
    case 142108: return true;
    case 142202: return true;
    case 142207: return true;
    case 142304: return true;
    case 142308: return true;
    case 143201: return true;
    case 152201: return true;
    case 152206: return true;
    case 152211: return true;
    case 152306: return true;
    case 152310: return true;
    case 153201: return true;
    case 162104: return true;
    case 162105: return true;
    case 162207: return true;
    case 162211: return true;
    case 162213: return true;
    case 162302: return true;
    case 162304: return true;
    case 162314: return true;
    case 200019: return true;
    case 200021: return true;
    case 200022: return true;
    case 200026: return true;
    case 200032: return true;
    case 200033: return true;
    case 200044: return true;
    case 200050: return true;
    case 200056: return true;
    case 200058: return true;
    case 200079: return true;
    case 200081: return true;
    case 200087: return true;
    case 200102: return true;
    case 200112: return true;
    case 200132: return true;
    case 200138: return true;
    case 200144: return true;
    case 200145: return true;
    case 200149: return true;
    case 200154: return true;
    case 200158: return true;
    case 200160: return true;
    case 200162: return true;
    case 200164: return true;
    case 200166: return true;
    case 200167: return true;
    case 200170: return true;
    case 200201: return true;
    case 200212: return true;
    case 200220: return true;
    case 200221: return true;
    case 200222: return true;
    case 200226: return true;
    case 200237: return true;
    case 200293: return true;
    case 200520: return true;
    case 200528: return true;
    case 200534: return true;
    case 200539: return true;
    case 201579: return true;
    case 201580: return true;
    case 201581: return true;
    case 201582: return true;
    case 201583: return true;
    case 201584: return true;
    case 201585: return true;
    case 201587: return true;
    case 201589: return true;
    case 201595: return true;
    case 201597: return true;
    case 201598: return true;
    case 201601: return true;
    case 201603: return true;
    case 201615: return true;
    case 201617: return true;
    case 201619: return true;
    case 201621: return true;
    case 201627: return true;
    case 201628: return true;
    case 201631: return true;
    case 201632: return true;
    case 201635: return true;
    case 201639: return true;
    case 201642: return true;
    case 201650: return true;
    case 201653: return true;
    case 201664: return true;
    case 201676: return true;
    case 201696: return true;
    case 201697: return true;
    case 201699: return true;
    case 201704: return true;
    case 201725: return true;
    case 201731: return true;
    case 201773: return true;
    case 201776: return true;
    case 201778: return true;
    case 201780: return true;
    }
    return false;
}
