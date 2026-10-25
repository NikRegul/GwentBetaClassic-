"""Prepare BBCode copies of the thirteen-language release text; no publishing."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
NOTES=ROOT/'docs/releases/0.9.3-public-20261025'

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
    (target/'manifest.json').write_text(json.dumps(dict(languages=13,documents=39,records=records,published=False),indent=2)+'\n','utf8')
    (target/'README_RU.md').write_text('# Тексты 0.9.3 в BBCode\n\n39 файлов: описание, пост и changelog на 13 языках. Содержимое соответствует Markdown в родительской папке. Для редактора с поддержкой BBCode копируйте текст нужного .txt. Ничего не опубликовано.\n','utf8')
    print('Prepared39 BBCode copies, balanced markup, source hashes recorded.')

if __name__=='__main__':main()
