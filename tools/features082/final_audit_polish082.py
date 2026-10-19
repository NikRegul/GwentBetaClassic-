"""Cross-check release, rule snapshots, native inputs and opt-in cleaner artifacts."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'BetaGwent/build/release082-polish2';CLEAN=ROOT/'BetaGwent/build/cleaner082-safe'
def read(p):return json.loads(p.read_text('utf8'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    audit=read(BUILD/'final-audit.json');assert len(audit)==2
    for row in audit:assert sha(Path(row['archive']['path']))==row['archive']['sha256']
    original=read(ROOT/'BetaGwent/build/release082-final/final-audit.json')
    for row in original:assert sha(Path(row['archive']['path']))==row['archive']['sha256']
    inputs={p.relative_to(BUILD/'scripts').as_posix():sha(p) for p in (BUILD/'scripts').rglob('*.ws')}
    snapshot=read(BUILD/'audit/rules/manifest.json');assert inputs=={k.removeprefix('scripts/'):v for k,v in snapshot['files'].items()}
    compiled=read(BUILD/'compile-nextgen/result.json');assert compiled['exitCode']==0 and compiled['patchSourcesUnchangedDuringCompile'];assert inputs=={r['path']:r['sha256'] for r in compiled['patchSourcesBefore']}
    classic=read(ROOT/'BetaGwent/build/universal081/classic-runtime/runs/release082-polish2-phase-native/result.json');assert classic['compilePassed'] and not classic['errors'];assert classic['preparationManifestSha256']==sha(BUILD/'classic-prepared/preparation.json')
    baseline=read(BUILD/'audit/checks-summary.json');assert len(baseline)==29 and all(r['exitCode']==0 for r in baseline)
    tactics=read(BUILD/'tactics-all/report.json');assert len(tactics['results'])==1426 and all(r['status']=='pass' for r in tactics['results'])
    rows=read(BUILD/'rows-all/report.json');assert len(rows['results'])==414 and all(r.get('pass') for r in rows['results'])
    medium=read(BUILD/'tactics-medium/report.json');assert len(medium['results'])==230 and all(r['status']=='pass' for r in medium['results'])
    weather=read(BUILD/'weather-tests/report.json');assert len(weather['results'])==64 and len(weather['choices'])==20;assert all('error' not in r for r in weather['results']+weather['choices'])
    turns=read(BUILD/'turn-forecast-tests.json');assert turns['checks']==144 and len(turns['results'])==24
    games=read(BUILD/'exploration/selfplay.json');assert games['games']==92 and games['errors']==0 and games['fingerprint']==snapshot['fingerprint']
    human=read(BUILD/'exploration/human-card-exploration.json');assert human['attempted']==1374 and human['completed']==1373 and not human['failures']
    cleaner=[]
    for version,folder in [('1.32','package-classic'),('5.0+','package-nextgen')]:
        package=CLEAN/folder;manifest=read(package/'manifest.json')
        path=ROOT/f'BetaGwent/release/GwentBetaClassic-Cleaner-0.8.2-r2-{version}.zip'
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            for row in manifest['files']:
                assert sha(package/row['path'])==row['sha256']
                with z.open(row['path']) as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==row['sha256']
        cleaner.append(dict(platform=version,path=str(path),bytes=path.stat().st_size,sha256=sha(path),saveRoundTripVerified=False))
    frozen={}
    for folder in ['scripts','classic/ui/src','nextgen/ui/src','redux']:
        for p in (BUILD/folder).rglob('*'):
            if p.is_file():frozen[p.relative_to(BUILD).as_posix()]=sha(p)
    report=dict(createdUtc=datetime.now(timezone.utc).isoformat(),version='0.8.2',revision='polish2',sourceFingerprint=snapshot['fingerprint'],sourceFiles=frozen,
        original082ArchivesUnchanged=True,nativeCompilersPassed=True,release=audit,cleaner=cleaner,
        checks=dict(baselineSuites=29,tactics=1426,mediumTactics=230,rowChoices=414,weatherParity=64,weatherHorizonChoices=20,turnScenarios=24,turnAssertions=144,selfplayGames=92,humanPlayAttempts=1374,validNoTargetRejections=1),
        nativeGameplayVerified=False,nativeVisualAcceptance=False,fullHistoricalSaveErasureVerified=False)
    (BUILD/'completion-audit.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps(dict(checks=report['checks'],archives=[r['archive']['path'] for r in audit],cleaner=[r['path'] for r in cleaner]),indent=2))
if __name__=='__main__':main()
