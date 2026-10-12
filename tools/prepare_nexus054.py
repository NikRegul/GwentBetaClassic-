"""Prepare complete paste-ready Nexus BBCode from the existing product description."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'BetaGwent/release/publish-0.5.4'

def main():
    for lang in ['RU','EN']:
        text=(ROOT/f'BetaGwent/release/publish-0.5.1/NEXUS_DESCRIPTION_{lang}.txt').read_text('utf8').replace('0.5.1','0.5.4')
        changelog=(DEST/f'CHANGELOG_{lang}.md').read_text('utf8')
        latest=changelog.split('## ')[0]
        bullets=[line[2:] for line in latest.splitlines() if line.startswith('- ')]
        heading='Новое в 0.5.4' if lang=='RU' else 'New in 0.5.4'
        section=f'[size=4][b]{heading}[/b][/size]\n\n[list]\n'+''.join('[*]'+b+'\n' for b in bullets)+'[/list]\n\n'
        pattern=r'\[size=4\]\[b\](?:Новое в|New in) 0\.5\.4\[/b\]\[/size\].*?(?=\[size=4\])'
        text,count=re.subn(pattern,lambda _:section,text,flags=re.S)
        assert count==1
        if lang=='RU':
            text=text.replace('Подбор отдельных составов не означает, что баланс всех колод уже подтверждён.', 'В 0.5.3 также обновлены «Невольничья пехота», «Аретуза» и «Дриады» по итогам парных испытаний. Подбор отдельных составов не означает, что баланс всех колод уже подтверждён.')
            future='В 0.5.4 используются статичные изображения карт. План: 0.6.0+ — анимации и ИИ, включая плавно зацикленные портреты только лидеров; 0.7.0+ — новые языки; 0.8.0+ — UI/UX; 0.9.0 — оставшиеся анимации с целью воспроизвести оригинальную бету. Полноценный релиз 1.0 включает все заявленные языки и отдельную ветку для The Witcher 3 версии 1.32. Это планы, а не возможности текущего пакета; поддержка 1.32 пока недоступна.'
        else:
            text=text.replace('Selecting individual roster candidates does not establish balance across all decks.', '0.5.3 also updated Slave Infantry, Arethusa and Dryads following paired trials. Selecting individual roster candidates does not establish balance across all decks.')
            future='0.5.4 uses static card artwork. Roadmap: 0.6.0+ focuses on animations and AI, including smoothly looping leader portraits only; 0.7.0+ on new languages; 0.8.0+ on UI/UX; 0.9.0 on the remaining animations with the goal of reproducing the original Beta. The full 1.0 release is planned to include all announced languages and a separate branch for The Witcher 3 version 1.32. These are plans, not features of this package; 1.32 support is not available yet.'
        marker='[size=4][b]Как сообщить об ошибке' if lang=='RU' else '[size=4][b]Bug reports'
        text=text.replace(marker,future+'\n\n'+marker)
        (DEST/f'NEXUS_DESCRIPTION_{lang}.txt').write_text(text,'utf8')
        (DEST/f'NEXUS_CHANGELOG_{lang}.txt').write_text(section,'utf8')
    print('Prepared full RU/EN Nexus descriptions and version changelogs.')

if __name__=='__main__':main()
