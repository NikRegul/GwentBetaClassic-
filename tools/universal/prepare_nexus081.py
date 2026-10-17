"""Refresh the 13-language Nexus texts using the accepted Next-Gen status."""
from pathlib import Path
import json
import re
import zipfile

ROOT=Path(__file__).resolve().parents[2]
SOURCE=Path('C:/Users/NikR/Documents/Codex/2026-10-15/new-chat/outputs/release-texts')
OUT=ROOT/'docs/releases/0.8.1/nexus'
ORDER=['en','ru','de','fr','it','pl','es','es-mx','pt-br','ja','ko','zh-cn','zh-tw']
STATUS={
'en':'Version 0.8.1 for Next-Gen 5.0+ has been tested in-game. Classic 1.32 is being fixed and tested separately; its current archive is a test candidate.',
'ru':'Версия 0.8.1 для Next-Gen 5.0+ проверена в игре. Classic 1.32 исправляется и проверяется отдельно; её текущий архив предназначен для тестирования.',
'de':'Version 0.8.1 für Next-Gen 5.0+ wurde im Spiel getestet. Classic 1.32 wird separat korrigiert und geprüft; das aktuelle Archiv ist eine Testversion.',
'fr':'La version 0.8.1 pour Next-Gen 5.0+ a été testée en jeu. Classic 1.32 est corrigée et testée séparément ; son archive actuelle est une version de test.',
'it':'La versione 0.8.1 per Next-Gen 5.0+ è stata provata nel gioco. Classic 1.32 viene corretta e verificata separatamente; l’archivio attuale è una versione di prova.',
'pl':'Wersja 0.8.1 dla Next-Gen 5.0+ została przetestowana w grze. Classic 1.32 jest poprawiana i sprawdzana osobno; obecne archiwum jest wersją testową.',
'es':'La versión 0.8.1 para Next-Gen 5.0+ se ha probado en el juego. Classic 1.32 se está corrigiendo y probando por separado; su archivo actual es una versión de prueba.',
'es-mx':'La versión 0.8.1 para Next-Gen 5.0+ ya se probó dentro del juego. Classic 1.32 se está corrigiendo y probando por separado; su archivo actual es una versión de prueba.',
'pt-br':'A versão 0.8.1 para Next-Gen 5.0+ foi testada no jogo. Classic 1.32 está sendo corrigida e testada separadamente; o arquivo atual é uma versão de teste.',
'ja':'Next-Gen 5.0+向けのバージョン0.8.1はゲーム内で動作確認済みです。Classic 1.32向けは別途修正・検証中で、現在のアーカイブはテスト版です。',
'ko':'Next-Gen 5.0+용 0.8.1은 게임 내에서 테스트되었습니다. Classic 1.32용은 별도로 수정 및 검증 중이며, 현재 배포 파일은 테스트 버전입니다.',
'zh-cn':'适用于 Next-Gen 5.0+ 的 0.8.1 已完成游戏内测试。Classic 1.32 版本正在单独修复和测试，目前的压缩包为测试版本。',
'zh-tw':'適用於 Next-Gen 5.0+ 的 0.8.1 已完成遊戲內測試。Classic 1.32 版本正在另行修正與測試，目前的壓縮檔為測試版本。',
}
NAMES=dict(zip(ORDER,['English','Русский','Deutsch','Français','Italiano','Polski','Español','Español (Latinoamérica)','Português (Brasil)','日本語','한국어','简体中文','繁體中文']))


def bbcode(markdown):
    lines=markdown.splitlines();out=[];list_type=None;code=False
    def close_list():
        nonlocal list_type
        if list_type:out.append('[/list]');list_type=None
    for line in lines:
        if line.startswith('```'):
            close_list();code=not code;out.append('[code]' if code else '[/code]');continue
        if code:out.append(line);continue
        item=re.match(r'^(?:- |(\d+)\. )(.*)',line)
        if item:
            kind='numbered' if item[1] else 'bullet'
            if list_type!=kind:
                close_list();list_type=kind;out.append('[list=1]' if kind=='numbered' else '[list]')
            out.append('[*]'+item[2]);continue
        if line.strip():close_list()
        heading=re.match(r'^(#{1,3}) (.*)',line)
        if heading:
            size='5' if len(heading[1])==1 else '4'
            out.append('[size='+size+'][color=#e0b354][b]'+heading[2]+'[/b][/color][/size]')
        elif line.startswith('> '):out.append('[b]'+line[2:]+'[/b]')
        else:out.append(line)
    close_list()
    text='\n'.join(out)
    text=re.sub(r'\[([^\]]+)\]\((https://[^)]+)\)',r'[url=\2]\1[/url]',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'[b]\1[/b]',text)
    text=re.sub(r'`([^`]+)`',r'[b]\1[/b]',text)
    for tag in ['list','code','b','size','color','url']:
        opens=len(re.findall(r'\['+tag+r'(?:=[^\]]+)?\]',text))
        assert opens==text.count('[/'+tag+']'),tag
    return text.strip()+'\n'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    combined={'description':[],'post':[]}
    for code in ORDER:
        folder=OUT/code;folder.mkdir(exist_ok=True)
        for kind in combined:
            body=(SOURCE/code/(kind+'.md')).read_text('utf-8-sig')
            body=body.replace('0.8.1-preview','0.8.1')
            body=re.sub(r'^> .*$', '> '+STATUS[code],body,count=1,flags=re.M)
            if kind=='description':
                # Remove the Classic audio implementation note and internal
                # SymbolClass details. Keep the actual player-facing changes.
                bullet_lines=[line for line in body.splitlines() if line.startswith('- ')]
                # Eight feature rows, followed by nine change rows.
                assert len(bullet_lines)==17,(code,len(bullet_lines))
                for index in [12,16]:body=body.replace(bullet_lines[index]+'\n','',1)
            else:
                paras=body.split('\n\n')
                # Preserve the author's next-steps sentence and drop the old
                # whole-release test warning, now replaced by platform status.
                assert len(paras)>7
                paras[5]=re.split(r'(?<=[.!。])\s*',paras[5],maxsplit=1)[0]
                body='\n\n'.join(paras)
            body=re.sub(r'\n{3,}','\n\n',body).strip()+'\n'
            assert '\ufffd' not in body and '0.8.1-preview' not in body
            (folder/(kind+'.md')).write_text(body,'utf-8-sig')
            bb=bbcode(body)
            (folder/(kind+'.txt')).write_text(bb,'utf-8-sig')
            combined[kind].append((code,body,bb))
    for kind,parts in combined.items():
        (OUT/(kind.upper()+'_ALL_LANGUAGES.md')).write_text('\n\n---\n\n'.join(p[1] for p in parts),'utf-8-sig')
        intro='[center][size=6][b]Gwent Beta Classic[/b][/size]\nStandalone Gwent Beta 0.9.24 inside The Witcher 3\n[b]Version 0.8.1[/b]\n\nEnglish is shown below. Open a spoiler for another language.[/center]\n\n' if kind=='description' else ''
        text=intro+parts[0][2]
        for code,_,bb in parts[1:]:text+='\n[line]\n\n[b]'+NAMES[code]+'[/b]\n[spoiler]\n'+bb+'[/spoiler]\n'
        assert text.count('[spoiler]')==text.count('[/spoiler]')==12
        name='NEXUS_DESCRIPTION_0.8.1.txt' if kind=='description' else 'NEXUS_POST_0.8.1.txt'
        (OUT/name).write_text(text,'utf-8-sig')
        (OUT.parent/name).write_text(text,'utf-8-sig')
    (OUT/'README_RU.md').write_text('''# Тексты для Nexus 0.8.1

NEXUS_DESCRIPTION_0.8.1.txt — полное описание: English открыто, 12 переводов
в spoilers. NEXUS_POST_0.8.1.txt — отдельный пост на тех же 13 языках.
Это готовый BBCode для вставки. В языковых папках — отдельные версии BBCode
и редактируемый Markdown; файлы ALL_LANGUAGES содержат весь Markdown.

5.0+ отмечена проверенной по сообщению пользователя. Classic 1.32 явно
обозначена отдельным тестовым кандидатом. До её игровой приёмки не менять
эту формулировку на обещание поддержки. Инструкции используют ZIP и Mods,
без EXE-установщика. Автоматического резервирования при установке нет.
Сохранены сведения об официальных текстах карт, AI-переводе интерфейса,
fallback озвучки тролля DE/IT и возможных конфликтах других модов.
Тексты подготовлены в файлах; на Nexus ничего не опубликовано.
''','utf-8-sig')
    archive=ROOT/'BetaGwent/release/GwentBetaClassic-0.8.1-Nexus-13-Languages.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(OUT).as_posix())
    print(json.dumps(dict(languages=len(ORDER),archive=str(archive),nextgenUserTested=True,classicGameplayVerified=False),ensure_ascii=False))


if __name__=='__main__':main()
