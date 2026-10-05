"""Synthetic parser checks only; never write fake native runtime evidence."""
import unittest
from capture_board_runtime import parse_runtime

OPEN = 'BOARD_OPEN_REQUEST name=BetaGwentBoard\nBOARD_CONFIGURED schema=1 fixture=true\n'
VIEW = 'BOARD_VIEW revision=1 round=1 current=1 score=0:0 flags=0\n'
CHECKS = ('CORE_CHECK_DONE checks=116 passed=116 failed=0\n'
          'BOARD_CHECK_DONE checks=104 passed=104 failed=0\n')
BRIDGE_ERROR = '[Error][Gui] CallGameEvent: Function must be bound to a Flash DisplayObject before calling.\n'


class RuntimeCaptureChecks(unittest.TestCase):
    def parse(self, value):
        return parse_runtime(value.encode(), '<synthetic parser fixture>')[0]

    def test_no_session_has_no_measurements(self):
        report = self.parse('unrelated engine lines')
        self.assertFalse(report['nativeRuntimeObserved'])
        self.assertIsNone(report['revisionIncreasing'])
        self.assertIsNone(report['countersConsistent'])

    def test_latest_failed_open_does_not_reuse_old_success(self):
        report = self.parse(OPEN + VIEW + CHECKS + 'BOARD_CLOSED revision=1\n'
                            'BOARD_OPEN_REQUEST name=BetaGwentBoard\n')
        self.assertFalse(report['nativeRuntimeObserved'])
        self.assertFalse(report['expectedChecksComplete'])

    def test_latest_skipped_open_does_not_reuse_old_success(self):
        report = self.parse(OPEN + VIEW + CHECKS + 'BOARD_OPEN_SKIPPED existing menu\n')
        self.assertFalse(report['nativeRuntimeObserved'])
        self.assertFalse(report['nativeConfigured'])

    def test_reopen_resets_revision_sequence(self):
        report = self.parse(OPEN + VIEW + 'BOARD_VIEW revision=9 round=2 current=2 score=3:8 flags=0\n'
                            'BOARD_CLOSED revision=9\n' + OPEN + VIEW)
        self.assertEqual([1], [view['revision'] for view in report['views']])

    def test_native_logs_never_prove_visual_or_input_result(self):
        report = self.parse(OPEN + VIEW + CHECKS + 'BOARD_CLOSED revision=1\n')
        self.assertTrue(report['nativeRuntimeObserved'])
        self.assertTrue(report['expectedChecksComplete'])
        self.assertFalse(report['visualRenderingVerified'])
        self.assertFalse(report['restoredInputVerified'])

    def test_wrong_or_inconsistent_check_count_rejected(self):
        report = self.parse(OPEN + VIEW + CHECKS.replace('passed=104', 'passed=103'))
        self.assertFalse(report['expectedChecksComplete'])
        report = self.parse(OPEN + VIEW + CHECKS.replace('116', '92'))
        self.assertFalse(report['expectedChecksComplete'])

    def test_failure_and_duplicate_revision_detected(self):
        report = self.parse(OPEN + VIEW + VIEW + CHECKS + 'BOARD_CHECK_FAIL sample\n')
        self.assertFalse(report['revisionIncreasing'])
        self.assertFalse(report['expectedChecksComplete'])
        self.assertEqual(1, len(report['fatalOrCheckFailures']))

    def test_native_receiver_error_without_mod_name_is_captured(self):
        report, trace = parse_runtime(('BOARD_OPEN_REQUEST name=BetaGwentBoard\n' + BRIDGE_ERROR).encode(), '<synthetic>')
        self.assertTrue(report['nativeBridgeFailed'])
        self.assertFalse(report['nativeConfigured'])
        self.assertIn(BRIDGE_ERROR.strip(), trace)

    def test_old_or_post_close_bridge_error_is_not_current_failure(self):
        report = self.parse('BOARD_OPEN_REQUEST name=BetaGwentBoard\n' + BRIDGE_ERROR + OPEN + VIEW + CHECKS
                            + 'BOARD_CLOSED revision=1\n' + BRIDGE_ERROR)
        self.assertFalse(report['nativeBridgeFailed'])
        self.assertTrue(report['expectedChecksComplete'])

    def test_bridge_error_prevents_successful_check_summary_from_hiding_failure(self):
        report = self.parse(OPEN + VIEW + CHECKS + BRIDGE_ERROR)
        self.assertTrue(report['nativeBridgeFailed'])
        self.assertFalse(report['expectedChecksComplete'])

    def test_new_version_requires_request_checks(self):
        expected = {'CORE': 116, 'BOARD': 104, 'REQUEST': 123}
        report, _ = parse_runtime((OPEN + VIEW + CHECKS).encode(), '<synthetic>', expected)
        self.assertFalse(report['expectedChecksComplete'])
        report, _ = parse_runtime((OPEN + VIEW + CHECKS + 'REQUEST_CHECK_DONE checks=123 passed=123 failed=0\n').encode(), '<synthetic>', expected)
        self.assertTrue(report['expectedChecksComplete'])
        self.assertIn('REQUEST', report['checksObserved'])

    def test_request_failure_cannot_hide_behind_later_summary(self):
        report, trace = parse_runtime((OPEN + VIEW + CHECKS + 'REQUEST_CHECK_FAIL bad-selection\n'
                            'REQUEST_CHECK_DONE checks=123 passed=123 failed=0\n').encode(), '<synthetic>')
        self.assertFalse(report['expectedChecksComplete'])
        self.assertTrue(any('REQUEST_CHECK_FAIL' in line for line in trace))

    def test_mod_script_error_blocks_clean_acceptance(self):
        report = self.parse(OPEN + VIEW + CHECKS + '[Error][Script] game\\betagwent\\triggerOrder.ws Value 128 not handled\n')
        self.assertFalse(report['expectedChecksComplete'])
        self.assertEqual(1, len(report['modScriptErrors']))

    def test_new_flow_checks_required(self):
        expected = {'CORE': 116, 'BOARD': 104, 'REQUEST': 123, 'FLOW': 43}
        log = OPEN + VIEW + CHECKS + 'REQUEST_CHECK_DONE checks=123 passed=123 failed=0\n'
        report, _ = parse_runtime(log.encode(), '<synthetic>', expected)
        self.assertFalse(report['expectedChecksComplete'])
        report, _ = parse_runtime((log + 'FLOW_CHECK_DONE checks=43 passed=43 failed=0\n').encode(), '<synthetic>', expected)
        self.assertTrue(report['expectedChecksComplete'])

    def test_fixture_trace_is_not_human_ui_trace(self):
        report = self.parse(OPEN + VIEW + 'REQUEST_FIXTURE_BEGIN id=1\nREQUEST_FIXTURE_END id=1\nREQUEST_FLOW_BEGIN id=2\n')
        self.assertEqual(1, len(report['requestFlowEvents']))
        self.assertIn('id=2', report['requestFlowEvents'][0])


if __name__ == '__main__':
    unittest.main()
