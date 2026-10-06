"""Update RU/EN publication text for the compact rendering release."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'BetaGwent/release'
RU='Обновление 0.2.6: исправлены размеры рамок карт и фокус контроллера, обновлена отрисовка атласа для уменьшения мерцания. Компактное разрешение сохранено: карты 288×405, половины поля 1536×531. Запуск RU 0.2.5 в обычной игре подтверждён; новые визуальные изменения и EN ещё требуют проверки. Перед обновлением сделайте бэкап сейвов и целиком замените Mods/modBetaGwent0924.'
EN='Update 0.2.6 fixes card borders and controller focus bounds and changes atlas sampling to reduce flicker. Compact resolution remains: cards 288×405, board halves 1536×531. Russian 0.2.5 startup was confirmed in the installed game; new visual changes and English startup still need testing. Back up saves and replace the whole Mods/modBetaGwent0924 folder.'

def main():
 for lang,note in [('RU',RU),('EN',EN)]:
  for stem in ('NEXUS_FIELDS','NEXUS_DESCRIPTION','STEAM_DESCRIPTION'):
   p=BASE/f'{stem}_{lang}.md';s=p.read_text('utf8')
   s=re.sub(r'(?m)^(?:Update 0\.2\.[46]|Обновление 0\.2\.[46]|0\.2\.[46]).*$',note,s)
   s=s.replace('HD Beta boards and deck-builder skins are included; rendering and input in the installed game are being checked for this update.',
               'Original Beta board and deck-builder artwork is included at a compact resolution suitable for the installed game.')
   s=s.replace('HD Beta presentation','Original Beta presentation').replace('HD-оформление из Beta','Оформление из Beta')
   p.write_text(s,'utf8')
  p=BASE/f'README_{lang}.md';s=p.read_text('utf8')
  s=re.sub(r'^# Gwent Beta Classic .*', '# Gwent Beta Classic 0.2.6',s,count=1,flags=re.M)
  s=s.replace('Эта RU 0.2.5','Эта RU 0.2.6').replace('For 0.2.4 changes','For 0.2.6 changes').replace('Обновление 0.2.5:', 'Обновление 0.2.6:')
  s=s.replace('PRESENTATION98_RU','PRESENTATION99_RU').replace('PRESENTATION97_EN','PRESENTATION99_EN')
  if note not in s:s+='\n'+note+'\n'
  p.write_text(s,'utf8')
  p=BASE/f'CHANGELOG_{lang}.md';s=p.read_text('utf8')
  if not s.startswith('# Gwent Beta Classic 0.2.6'):
   title='# Gwent Beta Classic 0.2.6\n\n'
   bullets=('**Сделайте резервную копию сохранений перед обновлением.**\n\n- Исправлена рамка выбранного отряда: используются размеры карты на поле.\n- Контроллер выделяет тело карты без подписей и эффектов; учитывается поворот руки.\n- У кнопок, рядов и карточных окон фиксированные границы.\n- Выборка атласа с отступом половины текселя и запасным native Bitmap-путём.\n- Разрешение и лимит 55 MiB сохранены. RU и EN на одной игровой базе.\n\n' if lang=='RU' else
            '**Back up saves before updating.**\n\n- Selected units use battlefield card dimensions for their borders.\n- Controller focus excludes text/effect extents and follows hand-card rotation.\n- Fixed button, row and choice-card body bounds.\n- Half-texel atlas sampling and a conservative native Bitmap fallback.\n- Compact resolution and the 55 MiB GUI limit retained. RU/EN share gameplay.\n\n')
   p.write_text(title+bullets+note+'\n\n'+s,'utf8')
 p=ROOT/'docs/AI_MANUAL95_RU.md';s=p.read_text('utf8').replace('--stage 98','--stage 100').replace('0.2.4-ai.1','0.2.6-ai.1');p.write_text(s,'utf8')
 print('Updated Russian/English package and publication text; controls unchanged.')

if __name__=='__main__':main()
