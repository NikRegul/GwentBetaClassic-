"""Render supplied premium bundles offline, without changing the source player.

Requires Mono.Cecil 0.11.6 NuGet in tools/vendor and a Mono Windows Unity player.
Only the disposable BetaGwent/build/premium-capture copy is patched. All startup
account services are suppressed. This does not launch/install The Witcher 3.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'BetaGwent/build/premium-capture'


def prepare(player, helper_source=None):
    player = player.resolve()
    data = player.with_name(player.stem + '_Data')
    if not (data / 'Managed/Assembly-CSharp.dll').is_file():
        raise ValueError('A Mono Unity player with Assembly-CSharp.dll is required')
    WORK.mkdir(parents=True, exist_ok=True)
    runner = WORK / 'player'
    if not runner.exists():
        # Read-only bundle/runtime files may be linked; the patched assembly is
        # explicitly COPIED and replaced in the clone, never edited in place.
        def link(source, target):
            if Path(source).name == 'Assembly-CSharp.dll':
                return shutil.copy2(source, target)
            try: os.link(source, target)
            except OSError: shutil.copy2(source, target)
        shutil.copytree(player.parent, runner, copy_function=link)
    managed = runner / data.name / 'Managed'
    source_assembly = data / 'Managed/Assembly-CSharp.dll'
    original_hash = hashlib.sha256(source_assembly.read_bytes()).hexdigest()
    vendor = ROOT / 'tools/vendor/mono-cecil-0.11.6'
    if not vendor.exists():
        with zipfile.ZipFile(ROOT / 'tools/vendor/mono.cecil.0.11.6.nupkg') as archive:
            archive.extractall(vendor)
    patch = WORK / 'patch'
    patch.mkdir(exist_ok=True)
    cecil = vendor / 'lib/netstandard2.0/Mono.Cecil.dll'
    (patch / 'Patch.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net7.0</TargetFramework></PropertyGroup><ItemGroup><Reference Include="Mono.Cecil"><HintPath>'+str(cecil)+'</HintPath></Reference></ItemGroup></Project>')
    shutil.copyfile(Path(__file__).parent / 'leaders060/PatchPlayer.cs', patch / 'Program.cs')
    subprocess.run(['dotnet', 'build', str(patch / 'Patch.csproj'), '--nologo', '-v:q', '--ignore-failed-sources'], check=True)
    csc = Path(r'C:\Program Files\dotnet\sdk\7.0.101\Roslyn\bincore\csc.dll')
    helper = managed / 'BetaPremiumCapture.dll'
    references = [p for p in managed.glob('*.dll') if p.name != helper.name]
    response = WORK / 'capture.rsp'
    response.write_text('\n'.join(['-nostdlib', '-target:library', '-out:"'+str(helper)+'"'] +
                                 ['-reference:"'+str(p)+'"' for p in references] +
                                 ['"'+str(helper_source or Path(__file__).parent / 'leaders060/Capture.cs')+'"']))
    subprocess.run(['dotnet', str(csc), '@'+str(response)], check=True)
    patched = WORK / 'Assembly-CSharp.patched.dll'
    subprocess.run(['dotnet', str(patch / 'bin/Debug/net7.0/Patch.dll'), str(source_assembly), str(helper), str(patched)], check=True)
    # replace unlinks the old destination even if it was linked by an older run.
    os.replace(patched, managed / 'Assembly-CSharp.dll')
    assert original_hash == hashlib.sha256(source_assembly.read_bytes()).hexdigest()
    index=data/'StreamingAssets/DynamicCards/cards.index.json'
    (WORK / 'provenance.json').write_text(json.dumps(dict(player=str(player), assemblySha256=original_hash,
                                                       bundleIndexSha256=hashlib.sha256(index.read_bytes()).hexdigest(),
                                                       sourceUntouched=True), indent=2))
    return runner / player.name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--player', type=Path, required=True)
    parser.add_argument('--ids', type=Path, help='One premium art ID per line; defaults to the checked-in premium manifest')
    parser.add_argument('--output', type=Path, default=ROOT / 'BetaGwent/build/leader-loops136-v2')
    parser.add_argument('--helper-source', type=Path, help='Isolated capture implementation; defaults to the immutable 0.6.0 exporter')
    args = parser.parse_args()
    if args.ids is None:
        WORK.mkdir(parents=True,exist_ok=True);args.ids=WORK/'leader-recapture-ids.txt'
        bindings=json.loads((ROOT/'BetaGwent/build/release060-preparation/leaders/BetaGwentLeaderCatalog.json').read_text('utf8'))
        assert len(bindings)==21
        args.ids.write_text('\n'.join(sorted(set(bindings.values()))),'utf8')
    if any(not re.fullmatch(r'[0-9]{6,12}',value.strip()) for value in args.ids.read_text().splitlines() if value.strip()):
        raise ValueError('Art IDs must be numeric')
    executable = prepare(args.player, args.helper_source)
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / 'BetaGwent/build').resolve()):
        raise ValueError('Capture outputs must be inside BetaGwent/build')
    output.mkdir(parents=True, exist_ok=True)
    (output/'complete.txt').unlink(missing_ok=True)
    env = dict(os.environ, BETA_PREMIUM_OUTPUT=str(output), BETA_PREMIUM_IDS=str(args.ids.resolve()),
               GWENT_SERVER_URL='http://127.0.0.1:1')
    subprocess.run([str(executable), '-batchmode', '-screen-width', '512', '-screen-height', '640',
                    '-logFile', str(output / 'unity.log')], env=env, check=True, timeout=3600, creationflags=subprocess.CREATE_NO_WINDOW)
    if not (output / 'complete.txt').is_file():
        raise RuntimeError('Capture completion marker missing; inspect unity.log')


if __name__ == '__main__':
    main()
