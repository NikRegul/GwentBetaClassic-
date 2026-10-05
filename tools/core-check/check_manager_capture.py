"""Synthetic acceptance guards only; never write fake game evidence."""
import unittest
from capture_manager_runtime import parse_suite

class ManagerCaptureChecks(unittest.TestCase):
    def good(self):
        return '\n'.join(['MANAGER_SUITE_BEGIN schema=1 key=test',
            'ACTION_CHECK_BEGIN schema=1 fixture=queue39', 'ACTION_CHECK_PASS queue', 'ACTION_CHECK_DONE checks=1 passed=1 failed=0',
            'APPLY_CHECK_BEGIN schema=1 fixture=apply20', 'APPLY_CHECK_PASS apply', 'APPLY_CHECK_DONE checks=1 passed=1 failed=0',
            'MANAGER_CHECK_BEGIN schema=1 fixture=manager1 key=test', 'MANAGER_CHECK_PASS manager', 'MANAGER_CHECK_DONE checks=1 passed=1 failed=0',
            'MANAGER_SUITE_END schema=1'])
    def parse(self, text): return parse_suite(text.encode(), '<synthetic>', 'test', ['queue'], ['apply'], ['manager'])[0]
    def test_complete(self): self.assertTrue(self.parse(self.good())['expectedChecksComplete'])
    def test_no_suite(self): self.assertFalse(self.parse(self.good().split('\n', 1)[1])['expectedChecksComplete'])
    def test_no_end(self): self.assertFalse(self.parse(self.good().replace('MANAGER_SUITE_END schema=1', ''))['expectedChecksComplete'])
    def test_wrong_contract_key(self): self.assertFalse(self.parse(self.good().replace('key=test', 'key=stale'))['expectedChecksComplete'])
    def test_missing_queue(self): self.assertFalse(self.parse(self.good().replace('ACTION_CHECK_BEGIN', 'OLD_BEGIN'))['expectedChecksComplete'])
    def test_missing_apply(self): self.assertFalse(self.parse(self.good().replace('APPLY_CHECK_BEGIN', 'OLD_BEGIN'))['expectedChecksComplete'])
    def test_manager_summary_without_cases(self): self.assertFalse(self.parse(self.good().replace('MANAGER_CHECK_PASS manager', ''))['expectedChecksComplete'])
    def test_wrong_manager_id(self): self.assertFalse(self.parse(self.good().replace('PASS manager', 'PASS wrong'))['expectedChecksComplete'])
    def test_queue_failure(self): self.assertFalse(self.parse(self.good().replace('ACTION_CHECK_DONE', 'ACTION_CHECK_FAIL bad\nACTION_CHECK_DONE'))['expectedChecksComplete'])
    def test_apply_failure(self): self.assertFalse(self.parse(self.good().replace('APPLY_CHECK_DONE', 'APPLY_CHECK_FAIL bad\nAPPLY_CHECK_DONE'))['expectedChecksComplete'])
    def test_manager_failure(self): self.assertFalse(self.parse(self.good().replace('MANAGER_CHECK_DONE', 'MANAGER_CHECK_FAIL bad\nMANAGER_CHECK_DONE'))['expectedChecksComplete'])
    def test_mod_error_after_done(self): self.assertFalse(self.parse(self.good().replace('MANAGER_SUITE_END', '[Error][Script] game\\betagwent\\actionManager.ws error\nMANAGER_SUITE_END'))['expectedChecksComplete'])
    def test_old_failed_does_not_poison_new(self): self.assertTrue(self.parse(self.good().replace('PASS manager', 'FAIL manager') + '\n' + self.good())['expectedChecksComplete'])
    def test_new_unfinished_supersedes_old(self): self.assertFalse(self.parse(self.good() + '\nMANAGER_SUITE_BEGIN schema=1 key=test')['expectedChecksComplete'])
    def test_new_stale_supersedes_old(self): self.assertFalse(self.parse(self.good() + '\n' + self.good().replace('key=test', 'key=stale'))['expectedChecksComplete'])
    def test_order_must_match(self):
        text = self.good().splitlines()
        text = text[:1] + text[4:7] + text[1:4] + text[7:]
        self.assertFalse(self.parse('\n'.join(text))['expectedChecksComplete'])

if __name__ == '__main__': unittest.main()
