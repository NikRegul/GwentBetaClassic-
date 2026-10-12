"""Prepare leaders for 0.6.0 and retain language inputs for 0.7.0; never modify live menus."""
from pathlib import Path
import argparse,csv,hashlib,io,json,re,sys,zipfile,shutil,subprocess
from PIL import Image,ImageChops,ImageStat,ImageFile

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/data_definitions'
OUT=ROOT/'BetaGwent/build/release060-preparation'

def sha(data):return hashlib.sha256(data).hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')

def prepare_languages():
    sys.path.insert(0,str(ROOT/'tools'))
    from ws_codegen import localized_plain_text
    cards=json.loads((ROOT/'data/beta924/duel/slice.json').read_text('utf8'))['cards']
    english=json.loads((ROOT/'data/beta924/design/english89.json').read_text('utf8'))
    seed=json.loads((ROOT/'data/beta924/design/ui-seed060.json').read_text('utf8'))
    fonts=json.loads((ROOT/'BetaGwent/ui/build/beta-fonts104.json').read_text('utf8'))
    glyphs=set(map(int,fonts['PFDinTextCondPro']['glyphs']))
    voices=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/audio/highend/vo'
    expected={x['voiceKey'] for x in json.loads((ROOT/'docs/evidence/audio-import79.json').read_text('utf8'))['media'] if x['role']=='voice'}
    sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
    import UnityPy
    reports=[]
    with zipfile.ZipFile(SOURCE) as archive:
        russian={r['Key']:r['ru_ru'] for r in csv.DictReader(io.StringIO(archive.read('Localization/ru_ru.csv').decode('utf-8-sig'),newline=''),delimiter=';') if r.get('Key')}
        for entry in sorted(n for n in archive.namelist() if n.startswith('Localization/') and n.endswith('.csv')):
            locale=Path(entry).stem;raw=archive.read(entry)
            rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'),newline=''),delimiter=';'))
            keys=[r['Key'] for r in rows if r.get('Key')]
            if len(keys)!=len(set(keys)):raise ValueError('Duplicate localization key: '+locale)
            text={r['Key']:r.get(locale,'') for r in rows if r.get('Key')}
            save(OUT/'languages'/locale/'original-beta.json',text)
            candidates={}
            for key,value in russian.items():
                if not text.get(key):continue
                for source,target in ((value,text[key]),(localized_plain_text(value),localized_plain_text(text[key]))):
                    candidates.setdefault(source,set()).add(target)
            conflicts={k:sorted(v) for k,v in candidates.items() if len(v)>1}
            lookup={k:next(iter(v)) for k,v in candidates.items() if len(v)==1}
            save(OUT/'languages'/locale/'card-text.lookup.json',lookup)
            save(OUT/'languages'/locale/'ambiguous-text.json',conflicts)
            # Empty fields are intentional: never label English fallback as a completed translation.
            if locale not in ('ru_ru','en_us'):
                pending=OUT/'languages'/locale/'mod-ui.pending.json'
                entries=json.loads(pending.read_text('utf8')) if pending.exists() else [dict(source=k,english=v,translation='',reviewed=False) for k,v in english.items()]
                for item in entries:
                    if not item['translation'] and item['english'] in seed.get(locale,{}):
                        item['translation']=seed[locale][item['english']];item['origin']='draft UI seed; needs language and layout review'
                save(pending,entries)
            missing_names=[c['templateId'] for c in cards if not text.get(str(c['templateId'])+'_name')]
            plain=re.sub(r'<[^>]+>|\{[^}]+\}','', '\n'.join(text.values()))
            missing_glyphs=sorted({ord(c) for c in plain if not c.isspace() and ord(c) not in glyphs})
            bundle=voices/locale.replace('_','-');voice=None
            if bundle.is_file():
                names=set()
                for obj in UnityPy.load(str(bundle)).objects:
                    if obj.type.name=='TextAsset':names.add(obj.read().m_Name)
                missing=sorted(expected-names)
                voice=dict(bundle=str(bundle),sha256=sha(bundle.read_bytes()),required=len(expected),matched=len(expected)-len(missing),missingKeys=missing,decodedAndListened=False)
            reports.append(dict(locale=locale,originalKeys=len(text),csvSha256=sha(raw),missingCardNames=missing_names,lookupEntries=len(lookup),ambiguousLiterals=len(conflicts),
                currentBodyFontMissingCodepoints=missing_glyphs,voice=voice,modUiTranslationPending=locale not in ('ru_ru','en_us'),nativePackageBuilt=False))
    save(OUT/'languages/inventory.json',dict(source=str(SOURCE),sha256=sha(SOURCE.read_bytes()),languages=reports))
    return reports

def loop_frames(frames,overlap=8):
    # Crossfade the captured tail into the head, then continue through the middle.
    # There is no repeated frozen first frame at the wrap boundary.
    if len(frames)<=2*overlap:raise ValueError('Capture too short for overlap')
    blended=[]
    for i in range(overlap):
        t=i/(overlap-1);weight=t*t*(3-2*t)
        blended.append(Image.blend(frames[-overlap+i],frames[i],weight))
    return blended+frames[overlap:-overlap]

def delta(a,b):return sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3

def prepare_leaders():
    cards=json.loads((ROOT/'data/beta924/duel/slice.json').read_text('utf8'))['cards']
    leaders={str(c['templateId']):c['title'] for c in cards if c['fields']['Tier']==1}
    assert len(leaders)==21,('unexpected leader list',len(leaders))
    original=json.loads((ROOT/'BetaGwent/build/premium134/parked-assets/premium134.json').read_text('utf8'))
    bindings={k:original['bindings'][k] for k in sorted(leaders,key=int)}
    assert set(bindings)==set(leaders)
    directory=OUT/'leaders';directory.mkdir(parents=True,exist_ok=True)
    expected_files={art+'.dds' for art in bindings.values()}
    if any(p.name not in expected_files for p in directory.glob('*.dds')):raise ValueError('Non-leader atlas in staging')
    ImageFile.MAXBLOCK=max(ImageFile.MAXBLOCK,2048*1872*4)
    reports=[]
    for template,art in bindings.items():
        source=ROOT/'BetaGwent/build/leader-loops136-v2'/art
        metadata=json.loads((source/'complete.json').read_text('utf8'))
        assert (metadata['fps'],metadata['frames'],metadata['width'],metadata['height'])==(12,48,256,312)
        assert metadata['loopOnly'] and metadata['introExcluded']
        start=0
        raw=[(source/f'{i:04}.png').read_bytes() for i in range(48)]
        frames=[Image.open(io.BytesIO(b)).convert('RGB') for b in raw]
        assert all(f.size==(256,312) for f in frames)
        cycle=loop_frames(frames);assert len(cycle)==40
        atlas=Image.new('RGB',(2048,1560))
        for i,frame in enumerate(cycle):atlas.paste(frame,((i%8)*256,(i//8)*312))
        target=directory/(art+'.dds');atlas.save(target,format='DDS',pixel_format='DXT1')
        encoded=target.read_bytes();assert encoded[84:88]==b'DXT1' and len(encoded)==128+2048*1560//2
        steps=[delta(cycle[i],cycle[(i+1)%len(cycle)]) for i in range(len(cycle))]
        # Boundary consists of adjacent original frames (39 -> 40), not 47 -> 0.
        assert abs(steps[-1]-delta(frames[39],frames[40]))<1e-5
        reports.append(dict(templateId=int(template),title=leaders[template],art=art,sourceFrames=str(source),sourceStart=start,loopOnly=True,introExcluded=True,sourceFrameSha256=[sha(b) for b in raw],
            atlas=str(target),bytes=len(encoded),sha256=sha(encoded),originalSeamDelta=delta(frames[-1],frames[0]),
            loopSeamDelta=steps[-1],maximumStepDelta=max(steps),visualReviewPassed=False))
        if len(reports)<=3:
            cycle[0].save(directory/(art+'-loop.gif'),save_all=True,append_images=cycle[1:],duration=83,loop=0)
    report=dict(version='0.6.0-preparation',leaderCount=21,bindings=bindings,frames=40,fps=12,width=2048,height=1560,
        overlap=8,algorithm='smoothstep overlap of tail and head',resources=reports,totalAtlasBytes=sum(r['bytes'] for r in reports),
        source=original['source'],nativeIntegrationComplete=False,nonLeaderAtlases=0,maxActivePreviews=1,
        runtimeRequirement='Only resolve IDs in this allowlist; unload previous preview; never preload all leaders.')
    save(directory/'manifest.json',report)
    save(directory/'BetaGwentLeaderCatalog.json',bindings)
    return report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--part',choices=['languages','leaders','both'],default='both')
    parser.add_argument('--compile-prototype',action='store_true');a=parser.parse_args()
    previous=OUT/'preparation.json'
    report=json.loads(previous.read_text('utf8')) if previous.exists() else {}
    report.update(release='future-release-preparation',leadersRelease='0.6.0',languagesRelease='0.7.0',liveReleaseSourcesModified=False)
    if a.part in ('languages','both'):report['languages']=prepare_languages()
    if a.part in ('leaders','both'):report['leaders']=prepare_leaders()
    if a.compile_prototype:
        work=OUT/'prototype';work.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'tools/ui/leaders060/BetaLeaderMovie.as',work/'BetaLeaderMovie.as')
        first=report['leaders']['resources'][0]
        Image.open(first['atlas']).save(work/'atlas.png')
        command=[r'C:\Program Files\Microsoft\jdk-11.0.12.7-hotspot\bin\java.exe','-Xmx1g','-jar',str(ROOT/'tools/vendor/apache-royale-0.9.12/royale-asjs/lib/mxmlc.jar'),
            '-load-config='+str(ROOT/'BetaGwent/ui/board-config.xml'),'-source-path='+str(work),'-source-path+='+str(ROOT/'BetaGwent/ui/src'),
            '-output='+str(work/'leader-prototype.swf'),str(work/'BetaLeaderMovie.as')]
        with (work/'compile.log').open('wb') as log:
            subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
        output=work/'leader-prototype.swf';assert output.read_bytes()[:3] in (b'FWS',b'CWS')
        report['prototype']=dict(path=str(output),sha256=sha(output.read_bytes()),sourceSha256=sha((work/'BetaLeaderMovie.as').read_bytes()),nativeIntegrationComplete=False)
    save(OUT/'preparation.json',report)
    summary=dict(release=report['release'],leadersRelease='0.6.0',languagesRelease='0.7.0',liveReleaseSourcesModified=False,
        generatorSha256=sha(Path(__file__).read_bytes()),uiSeedSha256=sha((ROOT/'data/beta924/design/ui-seed060.json').read_bytes()),
        inventory=str(OUT/'languages/inventory.json'),leaderManifest=str(OUT/'leaders/manifest.json'),
        languages=[dict(locale=x['locale'],originalKeys=x['originalKeys'],missingCardNames=len(x['missingCardNames']),
            missingBodyFontGlyphs=len(x['currentBodyFontMissingCodepoints']),voiceKeysMatched=x['voice']['matched'] if x['voice'] else 0,
            modUiTranslationPending=x['modUiTranslationPending']) for x in report.get('languages',[])],
        leaders=dict(count=report.get('leaders',{}).get('leaderCount'),atlasBytes=report.get('leaders',{}).get('totalAtlasBytes'),
            nonLeaderAtlases=report.get('leaders',{}).get('nonLeaderAtlases'),nativeIntegrationComplete=False),prototype=report.get('prototype'))
    save(ROOT/'docs/evidence/preparation060.json',summary)
    print(json.dumps(dict(locales=len(report.get('languages',[])),leaders=report.get('leaders',{}).get('leaderCount'),output=str(OUT))))

if __name__=='__main__':main()
