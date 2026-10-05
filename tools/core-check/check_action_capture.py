"""Acceptance parser checks: completeness, identity/order, failed and stale batches."""
import unittest
from capture_action_runtime import BEGIN, parse_runtime


class ActionCaptureChecks(unittest.TestCase):
    ids = ['one', 'two']

    def parse(self, text):
        return parse_runtime(text.encode(), '<synthetic>', self.ids)[0]

    def successful(self):
        return BEGIN + '\nACTION_CHECK_PASS one\nACTION_CHECK_PASS two\nACTION_CHECK_DONE checks=2 passed=2 failed=0\n'

    def test_complete_batch(self):
        self.assertTrue(self.parse(self.successful())['expectedChecksComplete'])

    def test_no_begin_not_accepted(self):
        self.assertFalse(self.parse('ACTION_CHECK_DONE checks=2 passed=2 failed=0')['expectedChecksComplete'])

    def test_no_done_not_accepted(self):
        self.assertFalse(self.parse(BEGIN + '\nACTION_CHECK_PASS one\nACTION_CHECK_PASS two')['expectedChecksComplete'])

    def test_summary_without_cases_not_accepted(self):
        self.assertFalse(self.parse(BEGIN + '\nACTION_CHECK_DONE checks=2 passed=2 failed=0')['expectedChecksComplete'])

    def test_duplicate_case_not_accepted(self):
        self.assertFalse(self.parse(self.successful().replace('PASS two', 'PASS one'))['expectedChecksComplete'])

    def test_wrong_order_not_accepted(self):
        self.assertFalse(self.parse(self.successful().replace('PASS one', 'PASS temporary').replace('PASS two', 'PASS one').replace('PASS temporary', 'PASS two'))['expectedChecksComplete'])

    def test_failure_blocks_good_summary(self):
        text = self.successful().replace('ACTION_CHECK_DONE', 'ACTION_CHECK_FAIL bad\nACTION_CHECK_DONE')
        self.assertFalse(self.parse(text)['expectedChecksComplete'])

    def test_script_error_blocks(self):
        text = self.successful().replace('ACTION_CHECK_DONE', '[Error][Script] game\\betagwent\\actionQueue.ws error\nACTION_CHECK_DONE')
        self.assertFalse(self.parse(text)['expectedChecksComplete'])

    def test_later_unfinished_attempt_supersedes_success(self):
        self.assertFalse(self.parse(self.successful() + BEGIN + '\nACTION_CHECK_PASS one')['expectedChecksComplete'])

    def test_old_failed_attempt_does_not_poison_new(self):
        report = self.parse(BEGIN + '\nACTION_CHECK_FAIL old\n' + self.successful())
        self.assertTrue(report['expectedChecksComplete'])
        self.assertEqual([], report['checkFailures'])

    def test_apply_batch_does_not_accept_action_summary(self):
        text = 'APPLY_CHECK_BEGIN schema=1 fixture=apply20\n' + self.successful()
        result = parse_runtime(text.encode(), '<synthetic>', self.ids,
            begin='APPLY_CHECK_BEGIN schema=1 fixture=apply20', tag='APPLY')[0]
        self.assertFalse(result['expectedChecksComplete'])

    def test_apply_batch_accepted_with_own_markers(self):
        text = self.successful().replace(BEGIN, 'APPLY_CHECK_BEGIN schema=1 fixture=apply20').replace('ACTION_CHECK_', 'APPLY_CHECK_')
        result = parse_runtime(text.encode(), '<synthetic>', self.ids,
            begin='APPLY_CHECK_BEGIN schema=1 fixture=apply20', tag='APPLY')[0]
        self.assertTrue(result['expectedChecksComplete'])


if __name__ == '__main__':
    unittest.main()
