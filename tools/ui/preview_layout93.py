"""Offline asset/layout composites, not screenshots or runtime acceptance."""
from pathlib import Path
import json,re,textwrap
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
REPORT=json.loads((ROOT/'docs/evidence/hd-art93.json').read_text('utf8'))
AS=(ROOT/'BetaGwent/ui/src/BetaGwentHDArt.as').read_text('utf8')
SLOTS=json.loads(re.search(r'private static var slots:Object=(\{.*?\});',AS).group(1))
pages={}
def source(ident):
 p,x,y,w,h=SLOTS[str(ident)]
 if p not in pages:pages[p]=Image.open(REPORT['pages'][p]['path']).convert('RGBA')
 return pages[p].crop((x,y,x+w,y+h))
def art(canvas,ident,x,y,w,h):
 image=source(ident).resize((round(w),round(h)),Image.Resampling.LANCZOS)
 canvas.alpha_composite(image,(round(x),round(y)))
def nine(canvas,ident,x,y,w,h):
 image=source(ident);sw,sh=image.size;sx,sy=min(24,sw/3),min(24,sh/3);dx,dy=min(12,w/3),min(12,h/3)
 xx=[0,sx,sw-sx,sw];yy=[0,sy,sh-sy,sh];tx=[0,dx,w-dx,w];ty=[0,dy,h-dy,h]
 for r in range(3):
  for c in range(3):
   part=image.crop(tuple(map(round,(xx[c],yy[r],xx[c+1],yy[r+1]))))
   part=part.resize((round(tx[c+1]-tx[c]),round(ty[r+1]-ty[r])),Image.Resampling.LANCZOS)
   canvas.alpha_composite(part,(round(x+tx[c]),round(y+ty[r])))
def dark(canvas,x,y,w,h,a=130):canvas.alpha_composite(Image.new('RGBA',(w,h),(8,10,9,a)),(x,y))
def text(canvas,value,x,y,size=22,width=None,color='#eee2c7'):
 draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',size)
 lines=[]
 for line in value.split('\n'):
  if not width:lines.append(line);continue
  current=''
  for word in line.split():
   if current and draw.textlength(current+' '+word,font=font)>width:lines.append(current);current=word
   else:current+=((' ' if current else '')+word)
  lines.append(current)
 draw.multiline_text((x,y),'\n'.join(lines),font=font,fill=color,spacing=6)
def button(canvas,value,x,y,w,h=48,chosen=False):
 nine(canvas,-1402 if chosen else -1400,x,y,w,h);text(canvas,value,x+12,y+(h-23)/2,18,width=w-24)
def main():
 out=ROOT/'BetaGwent/ui/build';ids=[112103,112108,112112,112101,112201,132103,132201,132213,132303,132104,132102,132402]
 # Battle: common world projection and centred proportional unit cards.
 c=Image.new('RGBA',(1920,1080));art(c,-1311,0,0,1920,1080)
 nine(c,-1400,16,12,1888,54);text(c,'BETA GWENT 0.9.24',36,24,25);text(c,'Дикая Охота / Краснолюды',460,28,22);text(c,'Раунд 1 · Ваш ход',1320,26,24)
 art(c,-1307,312,154,1160,400);art(c,-1300,312,554,1160,400)
 for y,faction,leader,score,name in [(226,3,200166,23,'Соперник'),(588,0,131101,19,'Геральт')]:
  nine(c,-1414,96,y,280,280);dark(c,104,y+8,264,264);art(c,-1420-faction,96,y,280,66)
  text(c,name,114,y+14,25);text(c,'Счёт:',114,y+66,18);text(c,str(score),114,y+90,52)
  text(c,'Раунды: 0 / 2',114,y+156,18);art(c,leader,276,y+70,90,126);nine(c,-1412,274,y+68,94,130)
  button(c,'Сброс: 2 · G',108,y+207,194,28);button(c,'Колода: 15 · D',108,y+242,194,27)
 button(c,'Эредин Бреакк Глас',96,882,280)
 for top,units in [(218,[142201,142202]),(322,[142204]),(426,[142206,142209]),(584,[132402,132303]),(688,[132201]),(792,[132402])]:
  step=(96-8)*256/360+8;w=step-8;x=437+(754-len(units)*step+8)/2
  for i,ident in enumerate(units):art(c,ident,x+i*step,top+4,w,88);text(c,'6',x+i*step+5,top+4,23)
 for i,ident in enumerate(ids[:8]):art(c,ident,484+i*112,926,104,146)
 nine(c,-1414,1504,130,368,538);dark(c,1512,138,352,522)
 art(c,-1250,1516,140,336,50);text(c,'Гончая Дикой Охоты',1528,150,22)
 art(c,132402,1584,202,200,282);nine(c,-1412,1582,200,204,286)
 text(c,'Зверь · Дикая Охота',1528,492,17,width=312)
 text(c,'Гончая Дикой Охоты\nИсходная сила: 4\n\nРазыграйте Трескучий мороз из своей колоды.',1532,520,19,width=312)
 text(c,'Выберите карту в руке, затем ряд.',1532,684,20,width=312)
 button(c,'Пас',1532,790,312);button(c,'Меню партии',1532,850,312)
 button(c,'Повторить',1532,912,150);button(c,'Сдаться',1694,912,150)
 text(c,'P — пас · L — лидер · D — колода\nG / H — сброс · ПКМ / X — карта',1532,978,17,width=312)
 c.convert('RGB').save(out/'battle-hd93-layout.png')
 # Deckbuilder: existing three-column safe-area layout, original sprite pixels.
 c=Image.new('RGBA',(1920,1080));art(c,-1310,0,0,1920,1080);dark(c,0,0,1920,1080,35)
 for x,w in [(44,388),(1440,436)]:nine(c,-1414,x,88,w,930 if x>1000 else 884);dark(c,x+8,96,w-16,914 if x>1000 else 868)
 for y in [88,382,676]:art(c,-1211,426,y,38,294);art(c,-1211,1398,y,38,294)
 text(c,'BETA GWENT · СОЗДАНИЕ КОЛОДЫ',52,26,30);text(c,'Слот 1 / 8',52,83,18)
 nine(c,-1410,56,112,364,40);text(c,'Дикая Охота',68,115,24);button(c,'Изменить имя',56,166,174,36);button(c,'Очистить',242,166,178,36)
 art(c,-1420,44,210,388,122);art(c,131101,56,218,100,141);text(c,'Эредин\nБреакк Глас',172,220,24);text(c,'Лидер · сила 6',172,299,19)
 button(c,'← Лидер',56,372,174,36);button(c,'Лидер →',242,372,178,36);text(c,'25 / 25–40 карт',56,424,27)
 text(c,'Золото 4 / 4 · серебро 6 / 6\n22 отряда · 3 особых',56,469,18)
 for i,ident in enumerate(ids):
  art(c,-1222 if i<4 else -1221 if i<8 else -1220,56,530+i*34,364,32);text(c,'×1  '+str(ident),64,534+i*34,17)
 for i,(ident,name) in enumerate([(-1240,'Чудовища'),(-1242,'Север'),(-1241,'Нильфгаард'),(-1243,'Скоя’таэли'),(-1244,'Скеллиге')]):
  x=464+i*186;button(c,'       '+name,x,88,178,54,i==0);art(c,ident,x+7,93,36,42)
 for i,name in enumerate(['Все','Бронза','Серебро','Золото']):button(c,'      '+name,464+i*139,158,130,42,i==0);art(c,-1214 if i==0 else -1230-i+1,472+i*139,163,28 if i==0 else 13,32)
 for x,w,name in [(1030,104,'Все'),(1144,116,'Отряды'),(1270,118,'Особые')]:button(c,name,x,158,w,42)
 nine(c,-1410,464,218,688,40);text(c,'Поиск карт',476,223,24);button(c,'Фракция + нейтральные',1164,218,224,40)
 text(c,'Поиск по названию, способности и тегам',464,268,17)
 for i,ident in enumerate(ids):
  x=464+i%6*154;y=310+i//6*300;nine(c,-1414,x,y,142,239)
  art(c,ident,x+4,y+4,134,188);nine(c,-1412,x+2,y+2,138,192);dark(c,x+4,y+148,134,44,210)
  text(c,str(ident),x+9,y+153,17);text(c,'1 / 3',x+7,y+208,17)
  button(c,'−',x+67,y+204,31,29);button(c,'+',x+104,y+204,31,29)
 for y in [554,854]:
  for x in [464,772,1080]:art(c,-1210,x,y,308,48)
 art(c,-1250,1448,96,420,58);text(c,'Гончая Дикой Охоты',1464,106,24)
 art(c,132402,1530,176,256,360);nine(c,-1412,1528,174,260,364)
 text(c,'Бронзовая · Отряд',1464,550,20);text(c,'Зверь · Дикая Охота',1464,586,18)
 art(c,-1270,1464,644,388,7)
 text(c,'Разыграйте Трескучий мороз из своей колоды.\n\nСвязки с картами Дикой Охоты.\n\nОписание и словарь доступны при прокрутке.',1464,670,22,width=388)
 button(c,'Сохранить колоду',56,990,364,42,True);button(c,'Отменить',1448,990,420,42)
 text(c,'Коллекция: добавить · состав: убрать · ПКМ / X: просмотр\nLT / RT: − / + · View: панели · LB / RB: страницы · Start: сохранить',464,990,17,width=924)
 c.convert('RGB').save(out/'editor-hd93-layout.png')
 print('Offline composites saved. They do not verify GFx input or runtime rendering.')
if __name__=='__main__':main()
