"""Prepare BBCode copies of the thirteen-language release text; no publishing."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
NOTES=ROOT/'docs/releases/0.9.3-public-20261025'
LANGUAGES=[('EN','English'),('RU','Русский'),('DE','Deutsch'),('FR','Français'),
           ('IT','Italiano'),('PL','Polski'),('ES','Español'),
           ('ES_MX','Español (Latinoamérica)'),('PT_BR','Português (Brasil)'),
           ('JA','日本語'),('KO','한국어'),('ZH_CN','简体中文'),('ZH_TW','繁體中文')]

def combine_descriptions(source,output):
    """One paste for Nexus: English followed by twelve collapsible translations."""
    parts=[];records=[]
    for index,(code,label) in enumerate(LANGUAGES):
        file=source/f'0.9.3_DESCRIPTION_{code}.txt';raw=file.read_bytes();text=file.read_text('utf-8-sig').strip()
        records.append(dict(language=code,source=file.name,sha256=hashlib.sha256(raw).hexdigest()))
        if index==0:parts.append(text)
        else:
            if index==1:parts.append('[size=4][b][color=#D8BC7F]Translations · Переводы[/color][/b][/size]')
            parts.append(f'[size=4][b][color=#D8BC7F]{label}[/color][/b][/size]\n[spoiler]\n{text}\n[/spoiler]')
    text='\n\n'.join(parts)+'\n';stack=[]
    for token in re.finditer(r'\[(/?)(b|size|color|list|spoiler)(?:=[^\]]+)?\]',text):
        closing,tag=token.groups()
        if closing:assert stack and stack.pop()==tag,'Unbalanced combined BBCode: '+tag
        else:stack.append(tag)
    assert not stack and text.count('[spoiler]')==12 and len(records)==13
    output.write_text(text,'utf8')
    return dict(file=output.name,languages=13,collapsedTranslations=12,characters=len(text),
                sha256=hashlib.sha256(output.read_bytes()).hexdigest(),sources=records)

def convert(source):
    result=[];listing=False
    for line in source.splitlines():
        if line.startswith('- '):
            if not listing:result.append('[list]');listing=True
            line='[*]'+line[2:]
        elif line.strip() and listing:
            result.append('[/list]');listing=False
        if line.startswith('## '):line='[size=4][b][color=#D8BC7F]'+line[3:]+'[/color][/b][/size]'
        elif line.startswith('# '):line='[size=5][b][color=#D8BC7F]'+line[2:]+'[/color][/b][/size]'
        line=re.sub(r'\*\*(.+?)\*\*',r'[b]\1[/b]',line)
        line=re.sub(r'`([^`]+)`',r'\1',line)
        result.append(line)
    if listing:result.append('[/list]')
    text='\n'.join(result)+'\n'
    for tag in ['list','size','b','color']:
        assert len(re.findall(r'\['+tag+r'(?:=[^\]]+)?\]',text))==text.count('[/'+tag+']'),tag
    return text

def main():
    target=NOTES/'BBCode';target.mkdir(exist_ok=True);records=[]
    for file in sorted(NOTES.glob('0.9.3_*.md')):
        text=convert(file.read_text('utf8'));out=target/(file.stem+'.txt');out.write_text(text,'utf8')
        records.append(dict(source=file.name,sourceSha256=hashlib.sha256(file.read_bytes()).hexdigest(),bbcode=out.name,sha256=hashlib.sha256(out.read_bytes()).hexdigest()))
    assert len(records)==39
    combined=combine_descriptions(target,target/'0.9.3_DESCRIPTION_ALL_LANGUAGES_NEXUS.txt')
    (target/'manifest.json').write_text(json.dumps(dict(languages=13,documents=39,records=records,combinedDescription=combined,published=False),indent=2)+'\n','utf8')
    (target/'README_RU.md').write_text('# Тексты 0.9.3 в BBCode\n\nОбщий файл для одной страницы Nexus: `0.9.3_DESCRIPTION_ALL_LANGUAGES_NEXUS.txt`. Английский текст открыт, остальные12языков — в раскрывающихся блоках.\n\nТакже39 отдельных файлов: описание, пост и changelog на13языках. Содержимое соответствует Markdown в родительской папке. Для редактора BBCode копируйте текст нужного.txt. Ничего не опубликовано.\n','utf8')
    print('Prepared39 BBCode copies and one combined13-language description; balanced markup, source hashes recorded.')

if __name__=='__main__':main()
