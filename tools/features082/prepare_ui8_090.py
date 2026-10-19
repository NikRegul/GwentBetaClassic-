"""0.9.0 build 8 UI (release090-ui7 -> release090-ui8).

* Deck/editor list rows: unit power centred in the left column (was top-aligned
  from a fixed y), leader power centred in the diamond below the crown.
* Import diagnostics for the Classic 1.32 freeze when Import opens: every step
  (clipboard probe/begin/bits, check, script replies) is logged through the
  existing OnBetaGwentControllerTrace channel as IMPORT_TRACE, before and after
  each native/script call. The last IMPORT_TRACE line in scriptslog.txt shows
  where a freeze happens.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, sys
sys.path.insert(0, str(Path(__file__).parent))
from prepare_ui7_090 import ROOT, COPIES, replace, write

SOURCE = ROOT / 'BetaGwent/build/release090-ui7'
OUT = ROOT / 'BetaGwent/build/release090-ui8'
NL = '\n'


def import_trace(s):
    s = replace(s, '        private function clipboardText():String' + NL,
                '        private function traceImport090(step:String):void' + NL +
                '        { send("OnBetaGwentControllerTrace",[0,"IMPORT_TRACE","ui8",step+" t="+getTimer()]); }' + NL +
                '        private function clipboardText():String' + NL)
    a = s.index('private function clipboardText():String')
    b = s.index('private function copyExchange():Boolean', a)
    body = s[a:b]
    body = replace(body, 'if(!clipboard.setData("betagwent:windows-paste-v1",""))return "";',
                   'traceImport090("clip_probe");if(!clipboard.setData("betagwent:windows-paste-v1",""))return "";')
    body = replace(body, 'if(!clipboard.setData("betagwent:windows-paste-begin-v1",""))return "";',
                   'traceImport090("clip_begin");if(!clipboard.setData("betagwent:windows-paste-begin-v1","")){traceImport090("clip_empty");return "";}traceImport090("clip_bits");')
    body = replace(body, 'if(symbol==0)return /^BG1',
                   'if(symbol==0)traceImport090("clip_done len="+value.length);' + NL + '                    if(symbol==0)return /^BG1')
    s = s[:a] + body + s[b:]
    s = replace(s, 'var pasted:String=clipboardText();if(pasted.length>0',
                'traceImport090("open");var pasted:String=clipboardText();traceImport090("pasted len="+pasted.length);if(pasted.length>0')
    s = replace(s, '                if(nameField.text.length)checkDeckExchange();' + NL + '                return;',
                '                if(nameField.text.length)checkDeckExchange();' + NL + '                traceImport090("open_done");' + NL + '                return;')
    s = replace(s, 'send("OnBetaGwentDeckImportCheck",[revision,code]);',
                'traceImport090("check_send");send("OnBetaGwentDeckImportCheck",[revision,code]);traceImport090("check_sent");')
    s = replace(s, 'send("OnBetaGwentDeckImport",[revision,exchangeQuotedCode,false]);',
                'traceImport090("import_send");send("OnBetaGwentDeckImport",[revision,exchangeQuotedCode,false]);traceImport090("import_sent");')
    s = replace(s, '            if(value!=revision||!nameOpen||!exchangeImport)return;' + NL + '            var a:Array=ids.length?ids.split(","):[]',
                '            traceImport090("missing_recv ids="+ids.length);' + NL + '            if(value!=revision||!nameOpen||!exchangeImport)return;' + NL + '            var a:Array=ids.length?ids.split(","):[]')
    s = replace(s, '            if(accepted){closeNameInput();return;}',
                '            traceImport090("exchange_recv accepted="+accepted);' + NL + '            if(accepted){closeNameInput();traceImport090("closed");return;}')
    return s


def board(s):
    s = replace(s, 'betaLabel(row,String(c.power),4,h*.36,h*.92,h*.36,0xF2EEE4,BetaGwentFonts.NUMBERS,false,"center");',
                'var leaderPower:TextField=betaLabel(row,String(c.power),4,h*.36,h*.92,Math.round(h*.36),0xF2EEE4,BetaGwentFonts.NUMBERS,false,"center");' + NL +
                '                centerBetaNumber(leaderPower,4+h*.46,h*.6,Math.round(h*.36));')
    s = replace(s, '}else if(unit)betaLabel(row,String(c.power),6,(h-h*.62*1.5)/2+2,32,h*.62,0xF2EEE4,BetaGwentFonts.NUMBERS,false,"center");',
                '}else if(unit){' + NL +
                '                // Same column centre for every row and digit count.' + NL +
                '                var rowPower:TextField=betaLabel(row,String(c.power),4,0,36,Math.round(h*.56),0xF2EEE4,BetaGwentFonts.NUMBERS,false,"center");' + NL +
                '                centerBetaNumber(rowPower,23,h/2,Math.round(h*.56));' + NL +
                '            }')
    return import_trace(s)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--source', type=Path, default=SOURCE)
    args = parser.parse_args(); out = args.out.resolve(); assert not out.exists()
    for platform in ['classic', 'nextgen']:
        target = out / platform; target.mkdir(parents=True)
        shutil.copytree(args.source / platform / 'ui', target / 'ui')
        p = target / 'ui/src/BetaGwentBoard.as'; write(p, board(p.read_text('utf-8-sig')))
        for folder in COPIES:
            if folder != 'src' and (target / 'ui' / folder).is_dir(): shutil.copy2(p, target / 'ui' / folder / p.name)
            if platform == 'nextgen' and (ROOT / 'BetaGwent/ui' / folder).is_dir(): shutil.copy2(p, ROOT / 'BetaGwent/ui' / folder / p.name)
        manifest = json.loads((args.source / platform / 'ui-inputs.json').read_text('utf8'))
        manifest['sources'] = {q.name: hashlib.sha256(q.read_bytes()).hexdigest() for q in (target / 'ui/src').glob('*.as')}
        (target / 'ui-inputs.json').write_text(json.dumps(manifest, indent=2), 'utf8')
        if platform == 'classic': shutil.copy2(args.source / 'classic/subimages.json', target / 'subimages.json')
    print('Prepared build 8 UI: centred deck list power numbers, import trace.')


if __name__ == '__main__':
    main()
