"""Voice preparation for the DE / IT / PT-BR installers (read-only for the live mod).

For every voice file the current RU sound project uses (BetaGwent/audio/wwise/Originals/
SFX/BetaGwent79/vo_*.wav: 887 card lines + 20 keg troll lines) the original Beta 0.9.24
recording of the locale is taken from AssetBundles/audio/highend/vo/<locale> (cards) and
vo/shop/<locale> (troll), the WEM is kept and decoded to WAV with vgmstream. Output file names
equal the RU project names, so a future wwise-<locale> project is a copy with these files.
Nothing is imported into Wwise and nothing is written outside BetaGwent/build/languages137/voice.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, wave
ROOT = Path(__file__).resolve().parents[2]
try:
    import UnityPy
except ImportError:
    sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python')); import UnityPy
VO = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/audio/highend/vo'
RU = ROOT / 'BetaGwent/audio/wwise/Originals/SFX/BetaGwent79'
EN = ROOT / 'BetaGwent/audio/wwise-en89/Originals/SFX/BetaGwent79'
OUT = ROOT / 'BetaGwent/build/languages137/voice'
CLI = ROOT / 'BetaGwent/build/languages137/tools/vgmstream/vgmstream-cli'
p = argparse.ArgumentParser(); p.add_argument('locales', nargs='*', default=['de-de', 'it-it', 'pt-br']); p.add_argument('--vgmstream', default=str(CLI))
args = p.parse_args()
manifest = json.loads((ROOT / 'docs/evidence/audio-import79.json').read_text('utf8'))
card_keys = {x['key']: x['voiceKey'] for x in manifest['media'] if x['role'] == 'voice'}
needed = sorted(f.stem for f in RU.glob('vo_*.wav'))
def clip_name(key):
    if key in card_keys: return 'cards', card_keys[key]
    if key.startswith('vo_keg_'):
        base, num = key[len('vo_keg_'):].rsplit('_', 1); return 'shop', 'SAY.' + base + '.' + num
    raise SystemExit('unknown voice ' + key)
def clips(path):
    if not path.is_file(): return None
    return {o.read().m_Name: o.read().m_Script.encode('utf8', 'surrogateescape') for o in UnityPy.load(str(path)).objects if o.type.name == 'TextAsset'}
def duration(path):
    with wave.open(str(path)) as w: return round(w.getnframes() * 1000 / w.getframerate()), w.getnchannels(), w.getframerate()
summary = json.loads((OUT / 'summary.json').read_text('utf8')) if (OUT / 'summary.json').is_file() else {}
for locale in args.locales:
    banks = dict(cards=clips(VO / locale), shop=clips(VO / 'shop' / locale))
    folder = OUT / locale.replace('-', '_'); (folder / 'wem').mkdir(parents=True, exist_ok=True); (folder / 'wav').mkdir(parents=True, exist_ok=True)
    items, missing = [], []
    for key in needed:
        kind, name = clip_name(key)
        raw = (banks[kind] or {}).get(name)
        if raw is None: missing.append(dict(key=key, source=kind, clip=name)); continue
        wem = folder / 'wem' / (key + '.wem'); wem.write_bytes(raw); wav = folder / 'wav' / (key + '.wav')
        r = subprocess.run([args.vgmstream, '-o', str(wav), str(wem)], capture_output=True, timeout=60)
        if r.returncode or not wav.is_file(): missing.append(dict(key=key, source=kind, clip=name, decodeError=r.stderr.decode(errors='replace')[-200:])); continue
        ms, ch, rate = duration(wav); ru_ms = duration(RU / (key + '.wav'))[0]; en_ms = duration(EN / (key + '.wav'))[0] if (EN / (key + '.wav')).is_file() else None
        items.append(dict(key=key, source=kind, clip=name, durationMs=ms, channels=ch, sampleRate=rate, ruDurationMs=ru_ms, enDurationMs=en_ms,
                          wavSha256=hashlib.sha256(wav.read_bytes()).hexdigest()))
    long = [i['key'] for i in items if i['durationMs'] > i['ruDurationMs'] * 1.35 + 300]
    report = dict(locale=locale, needed=len(needed), prepared=len(items), missing=missing,
                  bundles={k: (str((VO / locale) if k == 'cards' else (VO / 'shop' / locale)), v is not None) for k, v in banks.items()},
                  totalSeconds=round(sum(i['durationMs'] for i in items) / 1000), longerThanRussianBy35pct=long, items=items,
                  importedIntoWwise=False, listenedByHuman=False)
    (folder / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n', 'utf8')
    summary[locale] = dict(prepared=len(items), missing=len(missing), missingSources=sorted({m['source'] for m in missing}), longer=len(long), seconds=report['totalSeconds'])
(OUT / 'summary.json').write_text(json.dumps(summary, indent=1) + '\n', 'utf8')
print(json.dumps(summary))
