"""Prepare the complete 13-language 0.6.2 Nexus description without editing older releases."""
import hashlib
import json
import re
from pathlib import Path
from update_nexus137 import UPDATES, validate

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'BetaGwent/release/publish-0.6.2'


def main():
    old=ROOT/'BetaGwent/release/publish-0.6.1/NEXUS_DESCRIPTION_0.6.1.txt'
    notes=json.loads((ROOT/'data/beta924/design/nexus138.json').read_text('utf8'))
    assert list(notes)==list(UPDATES)
    text=old.read_text('utf-8-sig')
    for language,(previous,_,_) in UPDATES.items():
        assert text.count(previous)==1,language
        text=text.replace(previous,notes[language])
    text=text.replace('0.6.1','0.6.2')
    validate(text)
    assert all(text.count(note)==1 for note in notes.values())
    assert 'Large character entrance animations are planned separately.' not in text
    assert text.count('0.6.2')>=27 and '0.6.1' not in text
    target=DEST/'NEXUS_DESCRIPTION_0.6.2.txt'
    target.write_text(text,'utf8')
    for locale in ('RU','EN'):
        source=DEST/f'CHANGELOG_0.4.5_to_0.6.2_{locale}.md'
        content=source.read_text('utf8')
        lines=[];in_list=False
        for line in content.splitlines():
            if line.startswith('- '):
                if not in_list:lines.append('[list]');in_list=True
                lines.append('[*]'+line[2:])
                continue
            if in_list:lines.append('[/list]');in_list=False
            if line.startswith('# '):line='[size=5][b]'+line[2:]+'[/b][/size]'
            elif line.startswith('## '):line='[size=4][b]'+line[3:]+'[/b][/size]'
            lines.append(line)
        if in_list:lines.append('[/list]')
        result='\n'.join(lines)+'\n'
        assert result.count('[list]')==result.count('[/list]')==8
        assert '0.4.5' in result and '0.6.2' in result
        (DEST/f'NEXUS_CHANGELOG_{locale}.txt').write_text(result,'utf8')
    report=dict(version='0.6.2',changelogFrom='0.4.5',languages=list(notes),languageCount=13,
                spoilers=12,bbcodeBalanced=True,nativeSpeakerProofread=False,publishedToNexus=False,
                sourceDescriptionSha256=hashlib.sha256(old.read_bytes()).hexdigest(),
                files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DEST.glob('NEXUS_*.txt')})
    (ROOT/'docs/evidence/nexus138.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    print('Prepared 13-language Nexus description and RU/EN changelog from 0.4.5 to 0.6.2')


if __name__=='__main__':main()
