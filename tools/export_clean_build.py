"""One-time export of approved source assets into the independent CleanBuild kit.

Not used by the portable build. Historical candidates are read only here.
"""
from pathlib import Path
import hashlib, importlib.metadata as md, json, shutil, struct, sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'CleanBuild'
sys.path[:0] = [str(ROOT/'tools/classic132'), str(ROOT/'tools/ui'), str(ROOT/'tools/vendor/audio-python')]
from formats import bundle_entries, sound_index, sha
from dependencies import read_dependency_cache

MAIN = {'betagwent/betagwent_board.redswf':'betagwent_board',
        'betagwent/betagwent_decks.redswf':'betagwent_decks',
        'betagwent/betagwent_npc00.redswf':'betagwent_npc00',
        'gameplay/gui_new/swf/gwint/deck_builder.redswf':'betagwent_decks',
        'gameplay/gui_new/swf/gwint/gwint_game.redswf':'betagwent_npc00',
        'betagwent/betagwent_kegop.redswf':'betagwent_kegop'}

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')

def copy(source, relative):
    target = OUT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__','*.pyc'), dirs_exist_ok=True)
    else: shutil.copy2(source, target)

def helper(relative):
    copy(ROOT/relative, relative)

def main():
    # Code in CleanBuild is authored separately; only generated input directories
    # must be absent. Never overwrite a user-edited source export.
    assert not (OUT/'inputs').exists(), 'Input export already exists'
    copy(ROOT/'BetaGwent/build/release090-final5/scripts', 'source/scripts')
    copy(ROOT/'BetaGwent/ui/src', 'BetaGwent/ui/src')
    copy(ROOT/'BetaGwent/build/release090-banner-runtime2/classic/ui/src', 'source/classic-ui/src')
    copy(ROOT/'BetaGwent/ui/assets', 'BetaGwent/ui/assets')
    copy(ROOT/'BetaGwent/ui/board-config.xml', 'BetaGwent/ui/board-config.xml')
    copy(ROOT/'BetaGwent/native/clipboard', 'BetaGwent/native/clipboard')
    copy(ROOT/'BetaGwent/ui/build/beta-fonts104.json', 'inputs/font-outlines.json')
    for name in ('meshdata','uber'):
        copy(ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/cardassets/fronts'/name, 'inputs/beta-fronts/'+name)
    copy(ROOT/'BetaGwent/build/release090-final5/classic/subimages.json', 'inputs/classic-subimages.json')

    helpers = {
      'classic132':['formats.py','prepare_scripts.py','native_compile.py','classic_text_bridge.as.inc'],
      'recon':['audit_classic132.py'],
      'ui':['update_board_resource.py','read_gui_resource.py','install_native_hd93.py','externalize_gui96.py','build_beta_fonts104.py'],
      'universal':['build_menus.py'],
      'features082':['extract_banners090.py','build_banners090.py','build_clipboard090.py','compile_nextgen_final090.py']}
    for folder,names in helpers.items():
        for name in names: helper('tools/'+folder+'/'+name)
    # Export only the functions used by this kit, without the old packaging chain.
    text=(ROOT/'tools/universal/build_classic_subimages.py').read_text('utf8')
    text=text[:text.index('\ndef main():')]
    text=text.replace('import build_classic_bitmap_fix as base', 'ROOT = Path(__file__).resolve().parents[2]').replace('ROOT = base.ROOT\n','')
    (OUT/'tools/universal/build_classic_subimages.py').write_text(text,'utf8')
    fonts=OUT/'tools/ui/build_beta_fonts104.py'
    fonts.write_text(fonts.read_text('utf8').replace("ROOT / 'BetaGwent/ui/build/beta-fonts104.json'", "ROOT / 'inputs/font-outlines.json'"),'utf8')

    # External executables are configurable, no drive/user-profile literals.
    menu=OUT/'tools/universal/build_menus.py'; t=menu.read_text('utf8')
    t=t.replace("    args=parser.parse_args();out=args.out.resolve()", "    parser.add_argument('--java',type=Path,required=True)\n    parser.add_argument('--redkit',type=Path,required=True)\n    args=parser.parse_args();out=args.out.resolve()")
    t=t.replace("shutil.copytree(args.source_ui/'assets' if args.source_ui else ROOT/'BetaGwent/ui/assets',ui/'assets')", "shutil.copytree(ROOT/'BetaGwent/ui/assets',ui/'assets')")
    t=t.replace("java=Path(r'C:\\Program Files\\Microsoft\\jdk-11.0.12.7-hotspot\\bin\\java.exe')",'java=args.java')
    t=t.replace("api=Path(r'D:\\GOG Galaxy\\Games\\The Witcher 3 REDkit\\r4data\\gameplay\\gui_new\\actionscript')", "api=args.redkit/'r4data/gameplay/gui_new/actionscript'")
    menu.write_text(t,'utf8')
    b=OUT/'tools/features082/build_banners090.py';t=b.read_text('utf8')
    t=t.replace("global WORK, INPUT",'global WORK, INPUT, JAVA, EXPORTER, TEMPLATE')
    t=t.replace('    args = parser.parse_args(); WORK = args.out.resolve()', "    parser.add_argument('--java',type=Path,required=True)\n    parser.add_argument('--gfxexport',type=Path,required=True)\n    parser.add_argument('--template',type=Path,required=True)\n    args = parser.parse_args(); WORK = args.out.resolve()\n    JAVA=args.java;EXPORTER=args.gfxexport;TEMPLATE=args.template")
    t=t.replace("Path(r'C:\\Program Files\\Microsoft\\jdk-11.0.12.7-hotspot\\bin\\java.exe')",'JAVA')
    t=t.replace("Path(r'D:\\GOG Galaxy\\Games\\The Witcher 3 REDkit\\bin\\tools\\GFx4\\gfxexport_mult4fix.exe')",'EXPORTER')
    t=t.replace("ROOT / 'GwentB/myproject1/workspace/betagwent/betagwent_board.redswf'", "ROOT / 'inputs/menus/classic/betagwent_board.redswf'")
    b.write_text(t,'utf8')
    b=OUT/'tools/features082/extract_banners090.py';t=b.read_text('utf8')
    t=t.replace("ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/cardassets/fronts'", "ROOT / 'inputs/beta-fronts'")
    b.write_text(t,'utf8')
    b=OUT/'tools/features082/build_clipboard090.py';t=b.read_text('utf8')
    t=t.replace('    OUT=parser.parse_args().out.resolve()', "    parser.add_argument('--msvc',type=Path,required=True)\n    parser.add_argument('--sdk',type=Path,required=True)\n    parser.add_argument('--sdk-version',required=True)\n    args=parser.parse_args(); OUT=args.out.resolve()")
    t=t.replace("Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.34.31933')",'args.msvc')
    t=t.replace("Path('C:/Program Files (x86)/Windows Kits/10');ver='10.0.22000.0'",'args.sdk;ver=args.sdk_version')
    b.write_text(t,'utf8')
    ng=OUT/'tools/features082/compile_nextgen_final090.py';t=ng.read_text('utf8')
    t=t.replace("REDKIT = Path(r'D:\\GOG Galaxy\\Games\\The Witcher 3 REDkit')", "REDKIT = Path('REDkit-not-configured')")
    ng.write_text(t,'utf8')
    for relative in ('tools/vendor/apache-royale-0.9.12/royale-asjs/lib', 'tools/vendor/apache-royale-0.9.12/royale-asjs/LICENSE',
                     'tools/vendor/apache-royale-0.9.12/royale-asjs/NOTICE','tools/vendor/royale-player-api-0.9.12'):
        helper(relative)
    # Frozen offline wheels, with distribution metadata/licenses; no pip cache.
    vendor=OUT/'tools/vendor/audio-python';vendor.mkdir(parents=True)
    queue=['UnityPy','numpy'];seen=set();versions={}
    from packaging.requirements import Requirement
    while queue:
        name=queue.pop();dist=md.distribution(name);key=dist.metadata['Name'].lower()
        if key in seen:continue
        seen.add(key);versions[dist.metadata['Name']]=dist.version
        base=Path(dist.locate_file('')).resolve()
        for file in dist.files or []:
            src=Path(dist.locate_file(file)).resolve()
            if not src.is_relative_to(base) or not src.is_file() or '__pycache__' in src.parts:continue
            dst=vendor/src.relative_to(base);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        for requirement in dist.requires or []:
            req=Requirement(requirement)
            if not req.marker or req.marker.evaluate({'extra':''}):queue.append(req.name)
    dump(OUT/'inputs/python-lock.json',dict(python='3.13',architecture='win_amd64',distributions=versions))

    from update_board_resource import movie_parts
    from formats import Resource
    def blank_code(data):
        # Art/layout template, deliberately not a usable compiled menu.
        r=Resource(data);root=r.chunks[0];_,pos=r.properties(root)
        rebuilt=root[:pos];cursor=pos
        while cursor<len(root):
            n=struct.unpack_from('<I',root,cursor)[0];cursor+=4
            if not n:rebuilt+=bytes(4);continue
            movie=root[cursor:cursor+n];cursor+=n
            prefix,tags,tail=movie_parts(movie)
            def tag(c,p):return struct.pack('<HI',(c<<6)|63,len(p))+p
            # A valid empty ABC block (all constant pools contain only zero).
            abc=struct.pack('<I',0)+b'asset-template\0'+struct.pack('<HH',16,46)+bytes([1]*7)+bytes(5)
            import zlib
            body=prefix+b''.join(tag(c,abc) if c==82 else raw for c,p,raw in tags)
            compressed=movie[:3] in (b'CFX',b'CWS')
            new=movie[:4]+struct.pack('<I',len(body)+8)+(zlib.compress(body+tail,9) if compressed else body+tail)
            rebuilt+=struct.pack('<I',len(new))+new
        return r.replace_chunks([rebuilt,*r.chunks[1:]])

    report={'origin':'0.9.0 final5 accepted prepared art/audio; editable sources exported separately','platforms':{}}
    for platform,modname in [('classic','modBetaGwentClassic132'),('nextgen','modBetaGwent0924')]:
        source=ROOT/'BetaGwent/build/release090-final5/package-candidate'/platform/'package'
        content=source/'Mods'/modname/'content'
        assets=OUT/'inputs'/platform
        groups=[('mod',content)]
        if platform=='classic':groups.append(('dlc',source/'DLC/dlcBetaGwentClassic132Assets/content'))
        platform_report={'modName':modname,'groups':{}}
        for group,folder in groups:
            bundle=folder/('bundles/blob0.bundle' if group=='dlc' else 'blob0.bundle')
            with bundle.open('rb') as f:head=f.read(32);toc=f.read(struct.unpack_from('<I',head,16)[0])
            width=320 if platform=='classic' else 304
            guids={toc[i:i+256].split(b'\0')[0].decode('ascii').replace('\\','/'):toc[i+256:i+272].hex() for i in range(0,len(toc),width)}
            records={}
            for name,raw in bundle_entries(bundle):
                name=name.replace('\\','/')
                if '/betagwentbanners/' in name:continue # rebuilt from meshes
                if name in MAIN:
                    target='inputs/layouts/'+platform+'/'+MAIN[name]+'.redswf'
                    raw=blank_code(raw)
                else:target='inputs/'+platform+'/'+group+'/resources/'+name
                path=OUT/target;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
                records[name]={'input':target,'guid':guids[name]}
            deps=read_dependency_cache((folder/'dep.cache').read_bytes())
            deps['guids']=[g.hex() for g in deps['guids']]
            dump(assets/group/'dependencies.json',deps)
            dump(assets/group/'resources.json',dict(header=head.hex(),files=records))
            platform_report['groups'][group]=len(records)
        # Loose package data, excluding build artifacts and obsolete evidence.
        for p in source.rglob('*'):
            if not p.is_file():continue
            rel=p.relative_to(source).as_posix()
            if rel.startswith('bin/') or rel.startswith('manifest-'):continue
            if rel.startswith('BetaGwentDocs/') and p.name not in ('Copy-Deck-Code.ps1','save_fact_index.py'):continue
            if '/scripts/' in rel or p.name in ('blob0.bundle','dep.cache','metadata.store','soundspc.cache','precompiled.rsblob'):continue
            if p.name=='texture.cache':
                # Small prepared texture streaming index, not generated code.
                copy(p,'inputs/'+platform+'/loose-assets/'+rel+'.input')
            else:copy(p,'inputs/'+platform+'/loose/'+rel)
        version,index=sound_index(content/'soundspc.cache')
        with (content/'soundspc.cache').open('rb') as f:
            header=f.read(48 if version==1 else 64)
            audio=[]
            for i,(name,(offset,size)) in enumerate(index.items()):
                f.seek(offset);raw=f.read(size);key=f'{i:05d}'+Path(name).suffix
                p=assets/'audio'/key;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
                audio.append(dict(name=name,input=key,sha256=sha(p)))
        dump(assets/'audio/index.json',dict(version=version,header=header.hex(),files=audio))
        report['platforms'][platform]=platform_report
        frozen=json.loads((ROOT/'BetaGwent/build/release090-banner-runtime2'/platform/'ui-inputs.json').read_text('utf8'))
        for menu in frozen['menus']:
            if menu['language']!='ru':continue
            raw=blank_code(Path(menu['resource']).read_bytes())
            dest=OUT/'inputs/menus'/platform/(MAIN[next(n for n,s in MAIN.items() if s=={'BetaGwentBoard':'betagwent_board','GwintGame':'betagwent_npc00','DeckBuilder':'betagwent_decks','BetaGwentKeg':'betagwent_kegop'}[menu['entry']])]+'.redswf')
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
    copy(ROOT/'docs/releases/0.9.0', 'documentation/release090')
    for name in ('0.9.0_CLEANUP_RU.md','0.9.0_CLEANUP_EN.md'):copy(ROOT/'docs/releases'/name,'documentation/'+name)
    # Capture the optional module installation instructions, never its binaries.
    import zipfile
    archive=next((ROOT/'BetaGwent/build/release090-final5/package-candidate/archives-optional').glob('*1.32*.zip'))
    with zipfile.ZipFile(archive) as z:
        for n in z.namelist():
            if n.startswith('Optional-CopyButton/README_'):
                p=OUT/'documentation'/Path(n).name;p.write_bytes(z.read(n))
    dump(OUT/'inputs/provenance.json',report)
    # Only prepared inputs are pinned. Editable code may change freely.
    pinned={p.relative_to(OUT).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))
            for folder in ('inputs','BetaGwent/ui/assets','tools/vendor') for p in sorted((OUT/folder).rglob('*')) if p.is_file()}
    dump(OUT/'asset-manifest.json',pinned)
    print(json.dumps(dict(folder=str(OUT),pinnedFiles=len(pinned),bytes=sum(x['bytes'] for x in pinned.values()))))

if __name__=='__main__':main()
