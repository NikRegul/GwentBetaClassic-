"""Collect verified 0.9.1 packages, changelogs and a bilingual Nexus post."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,zipfile

ROOT=Path(__file__).resolve().parents[2]

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def inline(s):
    s=re.sub(r'\*\*(.*?)\*\*',r'[b]\1[/b]',s)
    s=re.sub(r'`([^`]+)`',r'\1',s)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:'[url='+m[2]+']'+m[1]+'[/url]' if m[2].startswith('http') else m[1],s)

def bbcode(text):
    lines=[];listed=False;table=False
    for line in text.splitlines():
        if line.startswith('|'):
            cells=[c.strip() for c in line.strip('|').split('|')]
            if not table:
                table=True
                if not listed:lines.append('[list]');listed=True
                continue
            if all(re.fullmatch(r'[-: ]+',c) for c in cells):continue
            lines.append('[*][b]'+inline(cells[0])+'[/b] — '+inline(' | '.join(cells[1:])))
            continue
        table=False
        if line.startswith('- '):
            if not listed:lines.append('[list]');listed=True
            lines.append('[*]'+inline(line[2:]));continue
        if listed:lines.append('[/list]');listed=False
        m=re.match(r'^(#{1,3}) (.*)$',line)
        lines.append('[size='+('5' if len(m[1])==1 else '4')+'][b]'+inline(m[2])+'[/b][/size]' if m else inline(line))
    if listed:lines.append('[/list]')
    result='\n'.join(lines)+'\n'
    for tag in ['b','list','size']:
        assert len(re.findall(r'\['+tag+r'(?:=[^\]]+)?\]',result))==result.count('[/'+tag+']'),tag
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--out',type=Path,default=ROOT/'BetaGwent/release/GwentBetaClassic-0.9.1');a=p.parse_args()
    out=a.out.resolve();assert not out.exists();(out/'nexus').mkdir(parents=True)
    release=json.loads((a.build/'release.json').read_text('utf8'));assert release['version']=='0.9.1'
    for row in release['archives']:
        archive=Path(row['path']);assert sha(archive)==row['sha256']
        with zipfile.ZipFile(archive) as z:
            m=json.loads(z.read('manifest-0.9.1.json'))
            assert m['gamepadHandPreviewFix'] and m['gamepadPileNavigationFix']
            assert z.read('BetaGwentDocs/0.9.1_POST_EN_RU.md')==(ROOT/'docs/releases/0.9.1_POST_EN_RU.md').read_bytes()
            if '1.32' in archive.name:assert m['classicAudioBanks']=='per-language-on-demand'
        shutil.copy2(archive,out/archive.name);shutil.copy2(archive.with_suffix('.zip.sha256'),out/(archive.name+'.sha256'))
    texts={}
    for source,name in [('0.9.1_POST_EN_RU.md','POST_0.9.1_EN_RU'),('0.9.1_CHANGELOG_RU.md','CHANGELOG_0.9.1_RU'),('0.9.1_CHANGELOG_EN.md','CHANGELOG_0.9.1_EN')]:
        text=(ROOT/'docs/releases'/source).read_text('utf8');target=out/'nexus'/(name+'.md');target.write_text(text,'utf8')
        target.with_suffix('.bbcode.txt').write_text(bbcode(text),'utf8')
    for f in (out/'nexus').iterdir():texts[f.name]=sha(f)
    (out/'release.json').write_text(json.dumps(dict(version='0.9.1',build=str(a.build.resolve()),archives=release['archives'],texts=texts,classicAudioPlaybackVerified=True,q601RetestAfterAudioFix=False,published=False),indent=2),'utf8')
    (out/'README_RU.md').write_text('''# Gwent Beta Classic 0.9.1

Два полных пакета: Classic 1.32 и Next-Gen 5.0+. Архив 1.32 содержит рабочую правку звука с языковыми банками. Реплики и эффекты подтверждены пользователем; загрузка пяти банков и освобождение памяти проверены в работающей игре. Повторная проверка доски q601 после окончательной правки звука остаётся.

В nexus лежат полный changelog RU/EN и пост EN/RU в Markdown и BBCode. Для Nexus Posts вставьте POST_0.9.1_EN_RU.bbcode.txt в режиме BBCode. Публикация не выполнялась. SHA-256 находятся рядом с архивами и в release.json.

Выберите архив под свою игру. Next-Gen: заменить modBetaGwent0924. Classic: заменить modBetaGwentClassic132 и скопировать обе папки Mods и DLC. После обновления пересобрать затронутые слияния Script Merger. After-Uninstall при обычном обновлении не устанавливается.
''','utf8')
    print('Release folder:',out)

if __name__=='__main__':main()
