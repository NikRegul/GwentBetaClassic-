"""Relabel the reviewed packages; preserve every executable/resource byte."""
from pathlib import Path
from copy import copy
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / 'BetaGwent/release'
OUT = ROOT / 'BetaGwent/build/release090-label'
SPECS = [
    (f'GwentBetaClassic-0.8.2-polish2-{p}-AllLanguages.zip',
     f'GwentBetaClassic-0.9.0-{p}-AllLanguages.zip')
    for p in ('1.32', '5.0+')
] + [
    (f'GwentBetaClassic-Cleaner-0.8.2-r2-{p}.zip',
     f'GwentBetaClassic-Cleaner-0.9.0-{p}.zip')
    for p in ('1.32', '5.0+')
]


def sha_file(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def sha_entry(z, name):
    with z.open(name) as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def text_label(raw):
    text = raw.decode('utf-8-sig')
    text = text.replace('0.8.2-polish2', '0.9.0').replace('0.8.2-r2', '0.9.0')
    text = text.replace('0.8.2', '0.9.0')
    return (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'') + text.encode('utf-8')


def repackage(source, dest):
    assert not dest.exists(), dest
    temporary = dest.with_suffix('.zip.partial')
    assert not temporary.exists(), temporary
    changed = {}
    renames = {}
    with zipfile.ZipFile(source) as src:
        manifest_name = next(n for n in src.namelist() if n.startswith('manifest') and n.endswith('.json'))
        manifest = json.loads(src.read(manifest_name))
        for info in src.infolist():
            name = info.filename
            if name == manifest_name:
                continue
            if name.endswith('.json'):
                raw = src.read(name)
                obj = json.loads(raw)
                if isinstance(obj, dict) and obj.get('version') in ('0.8.2', '0.8.2-polish2'):
                    # Keep native build reports, paths and compatibility identifiers intact.
                    changed[name] = raw.replace(b'"version": "0.8.2-polish2"', b'"version": "0.9.0"').replace(b'"version": "0.8.2"', b'"version": "0.9.0"')
            elif name.startswith(('BetaGwentDocs/', 'BetaGwentCleanerDocs/')) and name.endswith(('.md', '.txt')):
                raw = src.read(name)
                if b'0.8.2' in raw:
                    changed[name] = text_label(raw)

        manifest['version'] = '0.9.0'
        for row in manifest['files']:
            if row['path'] in changed:
                data = changed[row['path']]
                row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        changed[manifest_name] = json.dumps(manifest, indent=2, ensure_ascii=False).encode('utf-8')
        if manifest_name != 'manifest.json':
            renames[manifest_name] = 'manifest-0.9.0.json'

        infos = src.infolist()
        assert infos == sorted(infos, key=lambda info: info.header_offset)
        # Copy unchanged local ZIP records verbatim, including compressed data.
        # ZipFile writes a new central directory using the updated offsets.
        with zipfile.ZipFile(temporary, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as dst:
            dst.comment = src.comment
            for index, old in enumerate(infos):
                info = copy(old)
                if old.filename in changed:
                    info.filename = renames.get(old.filename, old.filename)
                    dst.writestr(info, changed[old.filename])
                else:
                    end = infos[index + 1].header_offset if index + 1 < len(infos) else src.start_dir
                    info.header_offset = dst.fp.tell()
                    src.fp.seek(old.header_offset)
                    remaining = end - old.header_offset
                    while remaining:
                        block = src.fp.read(min(8 * 1024 * 1024, remaining))
                        assert block
                        dst.fp.write(block)
                        remaining -= len(block)
                    dst.filelist.append(info)
                    dst.NameToInfo[info.filename] = info
                    dst.start_dir = dst.fp.tell()
                    dst._didModify = True

        runtime = 0
        with zipfile.ZipFile(temporary) as dst:
            assert len(dst.namelist()) == len(set(dst.namelist())) == len(infos)
            assert set(dst.namelist()) == {renames.get(i.filename, i.filename) for i in infos}
            assert dst.testzip() is None
            for row in manifest['files']:
                assert dst.getinfo(row['path']).file_size == row['bytes'], row['path']
                assert sha_entry(dst, row['path']) == row['sha256'], row['path']
            for info in infos:
                if info.filename.startswith(('Mods/', 'DLC/')) and not info.filename.endswith('/info.json'):
                    assert sha_entry(src, info.filename) == sha_entry(dst, info.filename), info.filename
                    runtime += 1
            for name, raw in changed.items():
                assert dst.read(renames.get(name, name)) == raw
                if name.endswith('.json'):
                    assert json.loads(raw)['version'] == '0.9.0'

    temporary.rename(dest)
    digest = sha_file(dest)
    dest.with_suffix('.zip.sha256').write_text(digest + '  ' + dest.name + '\n', encoding='ascii')
    result = dict(source=source.name, sourceSha256=sha_file(source), archive=dest.name,
                  bytes=dest.stat().st_size, sha256=digest, runtimeFilesUnchanged=runtime,
                  changedFiles=[renames.get(n, n) for n in changed], crcPassed=True,
                  manifestHashesPassed=True)
    print(json.dumps(result, ensure_ascii=True), flush=True)
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reports = [repackage(RELEASE / source, RELEASE / dest) for source, dest in SPECS]
    (OUT / 'verification.json').write_text(json.dumps(dict(version='0.9.0', labelOnly=True, archives=reports), indent=2), encoding='utf-8')
    instruction = ROOT / 'docs/releases/0.9.0_CLEANER_RU.md'
    assert not instruction.exists()
    instruction.write_bytes(text_label((ROOT / 'docs/releases/0.8.2_CLEANER_RU.md').read_bytes()))
    lines = ['# Gwent Beta Classic 0.9.0', '',
             'Версия изменена на 0.9.0 в актуальных пакетах 0.8.2 polish2 и очистителе r2. Код и ресурсы сохранены побайтно; установочные папки имеют прежние имена.', '']
    for report in reports:
        lines.append(f"- `{report['archive']}` — {report['bytes']:,} байт; рядом SHA-256.")
    lines += ['', 'Classic: копировать обе папки Mods и DLC. Next-Gen: Mods. Выбирать только пакет своей версии игры.',
              '', 'Очиститель устанавливается отдельно по инструкции `docs/releases/0.9.0_CLEANER_RU.md`.',
              '', 'ZIP CRC, хеши всех файлов manifest и неизменность исполняемых файлов/ресурсов проверены. Отчёт: `BetaGwent/build/release090-label/verification.json`.',
              '', 'Смена номера не добавляет игровую приёмку: визуальная проверка всех экранов и сохранение/перезагрузка настоящего .sav после очистки ещё не выполнены.', '']
    (RELEASE / '0.9.0_CURRENT_RU.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
