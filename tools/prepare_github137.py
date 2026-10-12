"""Refresh the existing public source checkout without changing build inputs."""
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'BetaGwent/build/github-0.3.0'
SUFFIXES = {'.py', '.ws', '.as', '.js', '.json', '.xml', '.md', '.cs', '.csproj', '.ps1', '.txt', '.csv'}
EXCLUDE = {'vendor', '__pycache__', 'bin', 'obj', 'node_modules', '.git', 'assets', 'audio', 'build'}
PRIVATE_HELPERS = {'github_auth_probe89.py', 'download_github_cli93.py', 'github_upload_batches89.py'}
LANGUAGES = ('de_de', 'fr_fr', 'it_it', 'pl_pl', 'es_es', 'es_mx', 'pt_br', 'jp_jp', 'kr_kr', 'zh_cn', 'zh_tw')


def main():
    assert (OUT / '.git').is_dir(), 'Existing public checkout required'
    records = []

    def copy(source, target_relative=None):
        relative = source.relative_to(ROOT)
        if target_relative is None and (any(part in EXCLUDE for part in relative.parts) or source.name in PRIVATE_HELPERS):
            return
        if source.suffix not in SUFFIXES and source.name != '.gitattributes':
            return
        raw = source.read_bytes()
        content = raw.decode('utf-8-sig')
        secrets = (
            r'<Property[^>]+Name="LicenseKey"[^>]+Value="[^"\s]+"',
            r'(?m)^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
            r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',
            r'\bsk-(?:proj-)?[A-Za-z0-9_-]{40,}',
        )
        assert not any(re.search(pattern, content) for pattern in secrets), f'Possible secret: {relative}'
        target_relative = Path(target_relative) if target_relative else relative
        assert not target_relative.is_absolute() and '..' not in target_relative.parts
        target = OUT / target_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        assert target.read_bytes() == raw
        records.append({'path': target_relative.as_posix(), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})

    for folder in ('BetaGwent/scripts', 'BetaGwent/development/scripts', 'BetaGwent/ui/src',
                   'tools', 'data/beta924/duel', 'data/beta924/design', 'data/beta924/ai', 'docs'):
        for source in sorted((ROOT / folder).rglob('*')):
            if not source.is_file():
                continue
            if folder == 'docs' and 'evidence' in source.parts:
                # Bounded, relevant reports; generated runtime harnesses/dumps/logs stay local.
                if source.suffix != '.json' or not re.search(r'(133|135|136|137|crash061)', source.name):
                    continue
                if source.name in {'github137-preparation.json', 'stage137-github.json'}:
                    continue
            copy(source)
    for source in sorted((ROOT / 'BetaGwent/release').glob('publish-*/*')):
        if source.is_file():
            copy(source)
    for name in ('.gitattributes', 'README.md', 'BetaGwent/README.md', 'BetaGwent/ui/README.md'):
        copy(ROOT / name)
    # Preserve reviewed translations as source inputs; do not regenerate or overwrite local dictionaries.
    for language in LANGUAGES:
        source = ROOT / 'BetaGwent/build/languages137/ui' / (language + '.json')
        assert source.is_file(), f'Missing reviewed dictionary: {source}'
        copy(source, 'data/beta924/localization137/ui/' + source.name)
    report = {'version': '0.6.1', 'checkout': str(OUT), 'sourceOnly': True,
              'filesCopied': len(records), 'files': records, 'assetsExcluded': True,
              'licenseKeysExcluded': True, 'pushed': False}
    (ROOT / 'docs/evidence/github137-preparation.json').write_text(json.dumps(report, indent=2) + '\n', 'utf8')
    print(json.dumps({key: value for key, value in report.items() if key != 'files'}, indent=2))


if __name__ == '__main__':
    main()
