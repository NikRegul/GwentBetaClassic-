"""Read-only inventory of the pinned Beta client's Wwise packages and Russian VO.

Records source hashes and validates bank extents/magic. Does not extract/import
sounds or imply that Beta banks are directly compatible with TW3's Wwise runtime.
"""
from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[2]
STREAM = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets'
OUT = ROOT / 'docs/evidence/beta-audio-inventory78.json'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory_package(path):
    size = path.stat().st_size
    with path.open('rb') as stream:
        header = stream.read(28)
        magic, header_bytes, version, languages_size, banks_size, media_size, external_size = struct.unpack('<4s6I', header)
        if magic != b'AKPK' or version != 1:
            raise ValueError('Unsupported package header: ' + str(path))
        if 8 + header_bytes != 28 + languages_size + banks_size + media_size + external_size:
            raise ValueError('Package header tables do not fit: ' + str(path))
        stream.seek(28)
        languages = stream.read(languages_size)
        language_count = struct.unpack_from('<I', languages)[0]
        language_names = []
        for i in range(language_count):
            offset, ident = struct.unpack_from('<II', languages, 4 + i * 8)
            end = offset
            while end + 2 <= len(languages) and languages[end:end + 2] != b'\0\0':
                end += 2
            language_names.append(dict(id=ident, name=languages[offset:end].decode('utf-16le')))
        tables = {}
        bank_records = []
        for name, length in [('banks', banks_size), ('streamedMedia', media_size), ('externalMedia', external_size)]:
            stream.seek(28 + languages_size + sum(tables[k]['tableBytes'] for k in tables))
            raw = stream.read(length)
            count = struct.unpack_from('<I', raw)[0]
            if length != 4 + count * 20:
                raise ValueError('Unsupported package table schema: ' + name)
            entries = []
            for i in range(count):
                ident, block_size, file_size, start_block, language = struct.unpack_from('<5I', raw, 4 + i * 20)
                offset = start_block * block_size
                if block_size == 0 or offset < 8 + header_bytes or offset + file_size > size:
                    raise ValueError('Invalid embedded source extent')
                entries.append(dict(id=ident, offset=offset, bytes=file_size, languageId=language))
            tables[name] = dict(tableBytes=length, count=count)
            if name == 'banks':
                bank_records = entries
        versions = set()
        for entry in bank_records:
            stream.seek(entry['offset'])
            magic, chunk_size, bank_version = struct.unpack('<4sII', stream.read(12))
            if magic != b'BKHD' or chunk_size + 8 > entry['bytes']:
                raise ValueError('Embedded bank header mismatch')
            entry['wwiseBankVersion'] = bank_version
            versions.add(bank_version)
    return dict(path=str(path), bytes=size, sha256=digest(path), packageVersion=version,
                languages=language_names, tables=tables, wwiseBankVersions=sorted(versions), banks=bank_records)


def main():
    packages = [inventory_package(path) for path in sorted((STREAM / 'Audio/GeneratedSoundBanks/Windows').glob('*.pck'))]
    voices = []
    for relative, role in [('AssetBundles/audio/highend/vo/ru-ru', 'Russian card voice bundle'),
                           ('AssetBundles/audio/highend/vo/announcers/ru-ru', 'Russian announcer bundle')]:
        path = STREAM / relative
        if not path.is_file():
            voices.append(dict(path=str(path), exists=False, role=role))
            continue
        with path.open('rb') as stream:
            signature = stream.read(8)
        if signature != b'UnityFS\0':
            raise ValueError('Unexpected voice bundle signature')
        voices.append(dict(path=str(path), exists=True, role=role, bytes=path.stat().st_size,
                           sha256=digest(path), container='UnityFS'))
    report = dict(stage=78, client='0.9.24.3.432', packages=packages, russianVoiceBundles=voices,
                  embeddedBankCount=sum(p['tables']['banks']['count'] for p in packages),
                  importedIntoMod=False, playbackVerified=False, originalFilesModified=False,
                  next=['Extract voice bank assets from UnityFS into a separate working directory.',
                        'Map bank/event IDs to card template IDs and distinguish UI/Vfx/voice.',
                        'Inspect media codecs and TW3 runtime compatibility before building a small import.',
                        'Connect audio to acknowledged animation cues, with cancellation and volume controls.'])
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Audio inventory: {len(packages)} packages, {report["embeddedBankCount"]} validated bank headers, {sum(v["exists"] for v in voices)} Russian voice bundles. No import/playback claim.')


if __name__ == '__main__':
    main()
