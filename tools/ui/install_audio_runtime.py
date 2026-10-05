"""Install only the additional Beta bank into REDkit's loose native audio search path.

Default is a read-only plan. --apply adds a unique bank or verifies an identical
one. --replace-known may upgrade only a previously recorded Beta bank, preserving
a workspace backup. Never installs Init or edits an original native bank.
External installation requires host approval. Reports/backups stay in the workspace.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import struct
import os

ROOT = Path(__file__).resolve().parents[2]
SDK = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit')
FOLDER = SDK / 'r4data/soundbanks/Pc'
TARGET = FOLDER / 'betagwent79.bnk'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--apply', action='store_true')
parser.add_argument('--replace-known', action='store_true')
args = parser.parse_args()
build = json.loads((ROOT / 'docs/evidence/audio-bank-build79.json').read_text('utf-8'))
source = Path(build['target']).resolve()
raw = source.read_bytes()
digest = hashlib.sha256(raw).hexdigest()
if not source.is_relative_to(ROOT) or raw[:4] != b'BKHD' or digest != build['sha256']:
    raise SystemExit('Installed workspace bank differs from verified build')
manifest=json.loads((ROOT/'docs/evidence/audio-import79.json').read_text('utf8'))
expected=manifest['mediaCount'] if manifest.get('fullImport') and manifest.get('wwiseBuildVerified') else 200
if struct.unpack_from('<I', raw, 8)[0] != 150 or not build['expectedEventsVerified'] or build['embeddedMedia'] != expected:
    raise SystemExit('Unexpected bank contents')
if not FOLDER.is_dir() or not (FOLDER / 'Init.bnk').is_file() or not (FOLDER / 'gwint_ep2.bnk').is_file():
    raise SystemExit('Expected native bank folder not found')
if TARGET.resolve().parent != FOLDER.resolve() or TARGET.name.lower() != 'betagwent79.bnk':
    raise SystemExit('Target escaped the additional-bank location')
existing = TARGET.exists()
existing_digest=hashlib.sha256(TARGET.read_bytes()).hexdigest() if existing else None
replacing=existing and existing_digest!=digest
known=set()
for name in ['stage79d-audio-runtime-install.json','audio79-runtime-install.json']:
    path=ROOT/'docs/evidence'/name
    if path.is_file():
        previous=json.loads(path.read_text('utf8'))
        if previous.get('installed') and Path(previous['target']).resolve()==TARGET.resolve():known.add(previous['sha256'])
if replacing and (not args.replace_known or existing_digest not in known):
    raise SystemExit('Different unapproved bank; upgrade needs --replace-known and a recorded Beta bank hash')
native_before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in FOLDER.glob('*.bnk') if p.name.lower() != TARGET.name.lower()}
backup=None
if args.apply and replacing:
    backup=ROOT/'BetaGwent/build/audio-runtime-backups'/('betagwent79-'+existing_digest+'.bnk')
    backup.parent.mkdir(parents=True,exist_ok=True)
    if backup.exists() and hashlib.sha256(backup.read_bytes()).hexdigest()!=existing_digest:
        raise SystemExit('Existing rollback backup differs')
    if not backup.exists():shutil.copyfile(TARGET,backup)
    if hashlib.sha256(backup.read_bytes()).hexdigest()!=existing_digest:raise SystemExit('Backup mismatch')
    temporary=FOLDER/('.betagwent79-update-'+digest[:12]+'.tmp')
    with temporary.open('xb') as handle:handle.write(raw)
    try:
        if hashlib.sha256(TARGET.read_bytes()).hexdigest()!=existing_digest:raise SystemExit('Target changed during upgrade')
        os.replace(temporary,TARGET)
    finally:
        if temporary.exists():temporary.unlink()
if args.apply and not existing:
    # Exclusive creation protects existing files, including concurrent installations.
    with TARGET.open('xb') as handle:
        handle.write(raw)
if args.apply:
    if hashlib.sha256(TARGET.read_bytes()).hexdigest() != digest:
        raise SystemExit('Additional bank hash mismatch after install')
    native_after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in FOLDER.glob('*.bnk') if p.name.lower() != TARGET.name.lower()}
    if native_before != native_after:
        raise SystemExit('Existing native bank changed during installation')
report = dict(stage=82 if build['embeddedMedia']!=200 else '79d', source=str(source), target=str(TARGET), bytes=len(raw), sha256=digest,
    installRequested=args.apply, installed=TARGET.exists() and hashlib.sha256(TARGET.read_bytes()).hexdigest()==digest, preexistingIdentical=existing_digest==digest,
    replacementRequested=args.replace_known, replacingKnownBetaBank=bool(replacing), rollbackBackup=str(backup) if backup else None,
    canonicalRuntimeName=TARGET.name, existingNativeBanks=len(native_before),
    existingNativeBanksUnchanged=True if args.apply else None,
    installedInit=False, installedGameModified=False, originalBetaModified=False,
    runtimeVerified=False, audiblePlaybackVerified=False,
    evidence='Native16:31:03 assert BetaGwent79.bnk not in banks array; script and user always-load CSV requested mixed-case name. Canonical lower-case name applied and additional bank placed in known native loose search path. Enumeration counts alone do not prove workspace ignored, because Init is excluded.',
    rollback='Close REDkit; restore the workspace backup for an upgrade, or remove only the additional betagwent79.bnk for a first installation. Original native banks are untouched.',
    nextAction='Fully restart REDkit and reopen Beta board; check AUDIO_BANK_LOADED and audible Geralt112103 line.')
(ROOT / 'docs/evidence/audio79-runtime-install.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
