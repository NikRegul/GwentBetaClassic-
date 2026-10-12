"""Build 0.6.2 dictionaries/fonts in text138, leaving the completed text137 resources intact."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=Path(__file__).with_name('build_languages137.py')

def main():
    # Reuse the proven GDI glyph/DefineFont3/native-resource implementation. Marker
    # assertions make upstream changes explicit instead of silently patching the wrong code.
    source=SOURCE.read_text('utf8')
    changes={
        "WORK = ROOT / 'BetaGwent/build/text137'":"WORK = ROOT / 'BetaGwent/build/text138'",
        "    dictionary.update({k.upper(): v.upper() for k, v in list(dictionary.items()) if k})":
        "    from build_ui_text138 import dictionaries\n    dictionary.update(dictionaries()[locale])\n    dictionary.update({k.upper(): v.upper() for k, v in list(dictionary.items()) if k})",
        "f'generated/text137/{locale}.swf'":"f'generated/text138/{locale}.swf'",
        "report = dict(stage=137,":"report = dict(stage=138,",
        "ROOT/'docs/evidence/languages137.json'":"ROOT/'docs/evidence/languages138.json'",
    }
    for old,new in changes.items():
        if source.count(old)!=1:raise RuntimeError('Language builder changed; review adaptation: '+old)
        source=source.replace(old,new)
    namespace={'__file__':str(SOURCE),'__name__':'ui_languages138'}
    exec(compile(source,str(SOURCE),'exec'),namespace)
    namespace['main']()

if __name__=='__main__':main()
