"""Collect a completed branch-audit package without changing frozen reports."""
import argparse, hashlib, json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text('utf8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('audit', type=Path)
    parser.add_argument('native', type=Path)
    parser.add_argument('--snapshot', default='rules06')
    parser.add_argument('--suffix', default='06')
    parser.add_argument('--allow-current-source-drift',action='store_true',help='Record concurrent checkout changes; frozen and compiled sources must still match exactly')
    args = parser.parse_args()
    audit, native = args.audit.resolve(), args.native.resolve()
    output = audit / ('batch-verification' + args.suffix + '.json')
    assert not output.exists(), 'Fresh collection output required'
    snapshot = audit / args.snapshot
    manifest = read(snapshot / 'manifest.json')
    for name, digest in manifest['snapshotFiles'].items():
        assert sha(snapshot / name) == digest, 'Changed snapshot: ' + name
    sys.path.insert(0, str(ROOT / 'tools/ai'))
    import build_js
    source_records = [];current_differences=[]
    for name in build_js.NAMES:
        relative = 'BetaGwent/development/scripts/game/betagwent/' + name + '.ws'
        if not (snapshot / 'sources' / relative).exists():
            relative = 'BetaGwent/scripts/game/betagwent/' + name + '.ws'
        source = snapshot / 'sources' / relative
        prepared = native / 'scripts/game/betagwent' / (name + '.ws')
        if not source.exists() or not prepared.exists():
            continue
        assert sha(source) == sha(prepared), 'Frozen/prepared mismatch: '+name
        if sha(source)!=sha(ROOT/relative):
            assert args.allow_current_source_drift,'Current source changed: '+name
            current_differences.append(dict(file=relative,snapshotSha256=sha(source),currentSha256=sha(ROOT/relative)))
        source_records.append(dict(file=relative, sha256=sha(source)))
    changed = ['duelCatalog', 'duelNilf', 'duelSession', 'duelMonsters',
               'duelNorth', 'duelSkellige', 'duelNilfDependencies', 'duelClone',
               'duelLiveCard', 'duelScoia', 'duelNeutral', 'duelEvents']
    classic = native / 'classic-prepared-final/Mods/modBetaGwentClassic132/content/scripts/game/betagwent'
    classic_sources = []
    for name in changed:
        source = snapshot / 'sources/BetaGwent/development/scripts/game/betagwent' / (name + '.ws')
        lowered = classic / (name + '.ws')
        assert source.read_text('utf-8-sig') == lowered.read_text('utf16'), name
        classic_sources.append(dict(file=name + '.ws', sha256=sha(lowered),
                                    normalizedSourceMatches=True))
    ng_path = native / 'compile-nextgen-final/result.json'
    cl_path = ROOT / 'BetaGwent/toolchains/classic-runtime/runs' / native.name / 'result.json'
    ng, cl = read(ng_path), read(cl_path)
    assert ng['exitCode'] == 0 and ng['completedByOutput'] and not ng['timedOut']
    assert ng['patchSourcesUnchangedDuringCompile']
    assert cl['compilePassed'] and not cl['errors'] and not cl['timedOut']
    regressions = read(audit / ('regressions' + args.suffix) / 'summary.json')
    assert regressions and all(r['exitCode'] == 0 for r in regressions)
    names = ['audit_movement095', 'audit_move_targets095', 'audit_move_order095',
             'audit_charm_random095', 'audit_corpse_venom095', 'audit_category_tables095']
    # Older frozen batches predate these tests. Collect them when they are part
    # of this batch's registered regression suite; never rewrite old evidence.
    registered = {r['name'] for r in regressions}
    names += [n for n in ['audit_inactive_moves095', 'audit_return_filters095', 'audit_hand_events095', 'audit_choice_moves095', 'audit_summon_events095', 'audit_reveal_tokens096', 'audit_token_events096', 'audit_ambush096', 'audit_power_targets096', 'audit_power_groups096', 'audit_reaction_edges096', 'audit_reaction_pools096', 'audit_whole_requests096', 'audit_batch80a096', 'audit_batch80b096', 'audit_batch80c096', 'audit_batch80d096', 'audit_batch80_requests096'] if n in registered]
    reports = {}
    for name in names:
        p = audit / ('regressions' + args.suffix) / (name + '.json')
        r = read(p)
        assert not r['failures'] and r['fingerprint'] == manifest['fingerprint']
        reports[name] = dict(path=str(p), sha256=sha(p), checks=r['checks'])
    for name in ['all-cards', 'actions', 'parity']:
        p = audit / (name + args.suffix + ('-bound' if name == 'actions' else '') + '.json')
        r = read(p)
        assert r['complete'] and not r.get('error') and not r.get('failures')
        assert r['fingerprint'] == manifest['fingerprint']
        reports[name] = dict(path=str(p), sha256=sha(p), checks=r.get('checks'),
                             cards=r.get('cards'), cases=r.get('cases'),
                             matches=len(r.get('records', [])))
    catalog_path = audit / ('catalog-audit' + args.suffix) / 'catalog-audit.json'
    catalog = read(catalog_path)
    assert catalog['cards'] == 511 and catalog['fingerprint'] == manifest['fingerprint']
    assert not catalog['attributeDifferences'] and not catalog['missingNodeClasses']
    runners = audit / ('evidence-sources' + args.suffix)
    assert not runners.exists(), 'Fresh evidence-source directory required'
    provenance = {}
    for relative in ['tools/ai/' + name + '.cjs' for name in names] + [
        'tools/ai/source_graph095.cjs', 'tools/ai/audit_fixture095.cjs',
        'tools/ai/audit_beta_rules095.cjs', 'tools/ai/validate091.py',
        'tools/ai/check_playtest_rules150.js', 'tools/ai/check_playtest188.js',
        'tools/ai/check_reveal_strategy093.js', 'tools/ai/check_beta_ws_actions092.cjs', 'tools/duel_nilf.py',
        'tools/features091/prepare091.py', 'data/beta924/design/rules_audit095_branches.json',
        'data/beta924/normalized/catalog.json'] + (['data/beta924/design/rules_audit096_token_sources.json', 'data/beta924/design/rules_audit096_token_amendments.json'] if 'audit_reveal_tokens096' in registered else []) + (['tools/ai/source_power096.cjs','data/beta924/design/rules_audit096_power_sources.json'] if 'audit_power_targets096' in registered else []) + (['tools/ai/source_reactions096.cjs','data/beta924/design/rules_audit096_reactions_sources.json','data/beta924/design/rules_audit096_reactions_amendments.json'] if 'audit_reaction_edges096' in registered else []) + (['tools/ai/source_batch80096.cjs','tools/ai/fixture_batch80096.cjs','data/beta924/design/rules_audit096_batch80_sources.json','data/beta924/design/rules_audit096_batch80_amendments.json'] if 'audit_batch80a096' in registered else []):
        target = runners / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
        provenance[relative] = sha(target)
    if (audit/'validate_block.py').exists():
        target=runners/'validate_block.py';shutil.copy2(audit/'validate_block.py',target)
        provenance['validate_block.py']=sha(target)
    record = dict(schema=1, fingerprint=manifest['fingerprint'],
        scope='Branch audit, not full catalog semantic acceptance or a release.',
        regressions=len(regressions), reports=reports, catalog=str(catalog_path),
        independentlyReviewedCards=catalog['independentlyReviewed'],
        battleSources=source_records, classicNormalizedSources=classic_sources,
        currentSourcesMatchSnapshot=not current_differences,currentSourceDifferences=current_differences,
        nativeCompilers=dict(classicResult=str(cl_path), nextgenResult=str(ng_path),
                             classicSha256=sha(cl_path), nextgenSha256=sha(ng_path)),
        evidenceSourcesAtCollection=provenance,
        allCardSemanticComparisonComplete=False, nativeGameplayVerified=False,
        packaged=False, installed=False, published=False)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(dict(output=str(output), fingerprint=record['fingerprint'],
                         regressions=record['regressions'],
                         independentlyReviewedCards=record['independentlyReviewedCards'])))


if __name__ == '__main__':
    main()
