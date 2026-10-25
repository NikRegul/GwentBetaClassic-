"""Run existing battle regressions against an immutable 0.9.1 input snapshot."""
from pathlib import Path
import argparse, concurrent.futures, json, subprocess, time

ROOT = Path(__file__).resolve().parents[2]
NAMES = '''check_consume_self check_no_targets127 check_deck_combos128 check_feedback092 check_round_economy093 check_reply_pass094 check_exhausted_frontier094 check_draw_frontier094 check_chase_budget093a check_plans093c check_four_card093c check_human_patterns094
check_policy133 check_hidden_information133 check_armor_restore165 check_quality095 check_swarm_playtest092 check_log_spy_pass_20261023 check_log_spy_opening_20261023
check_miruna_aglais_scorch180 check_emissary_mulligan181 check_playtest188
check_playtest_rules150 check_lock_resilience093b check_lock_choice144 check_chase139 check_spy138
check_cooperative156 check_ciri_return062 check_decisive127 check_concede127
check_tutor127 check_preventive127 check_ships127 check_draug127 check_losing131 check_deck_order091e
check_emhyr_spent_spy check_spent_spy_hand check_visible_targets check_spy_neighbours check_sweers_copies check_mixed_zone_choices check_round_continuation092 check_banked_boosts092 check_short_round_reply092 check_native_adda_armor092
check_cavalry131 check_ciri131 check_combo127 check_engines126 check_followups126 check_shadow_context092 check_live_engine_threat092 check_pending_charm092 check_resolved_frontier092 check_created_foltest092 check_created_leader_choices092 check_harald_row092
check_strategy140 check_clearrisk127 check_public_response113 check_revealed_reply_instances092 check_responsive_budget092
check_turn_forecast082 check_weather_horizon082 check_tactics091 check_starting_list091 check_proven_endgame091 check_bran091 check_brewess091 check_request_source091 check_miruna_timing091 check_nekker_food091 check_playtest091b check_playtest091c check_creation_pools091 check_shackles_ambush091 check_strategy096 check_strategy_policy096 check_planning097 check_weak098 check_boost_exposure092 check_ciri_nova092 check_ai_classes092 check_user_targets093 check_reveal_strategy093 check_ambush_hyp094b check_ambush_decision094b check_ambush_pairs094b check_special_target_mode197 check_kayran_miruna197 check_cyclops_swordsman197 check_stored_damage198'''.split()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('snapshot', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--workers', type=int, default=2)
    args = p.parse_args()
    from comparison_inputs import validate_snapshot
    validate_snapshot(args.snapshot)
    args.output.mkdir(parents=True, exist_ok=True)
    def run(name):
        start = time.monotonic()
        script=ROOT/'tools/ai'/(name+'.js')
        if not script.is_file():script=script.with_suffix('.cjs')
        command = ['node', str(script), str(args.snapshot.resolve()), str((args.output/(name+'.json')).resolve())]
        try:
            r = subprocess.run(command, cwd=ROOT, capture_output=True, encoding='utf8', errors='replace', timeout=240)
            code, output = r.returncode, r.stdout+r.stderr
        except subprocess.TimeoutExpired as exc:
            code, output = -1, str(exc)
        (args.output/(name+'.log')).write_text(output, encoding='utf8')
        result = dict(name=name, exitCode=code, seconds=round(time.monotonic()-start,2))
        if code: result['failureTail'] = output[-1800:]
        print(json.dumps(result), flush=True)
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(run, NAMES))
    validate_snapshot(args.snapshot)
    (args.output/'summary.json').write_text(json.dumps(results, indent=2), encoding='utf8')
    raise SystemExit(any(r['exitCode'] for r in results))

if __name__ == '__main__': main()
