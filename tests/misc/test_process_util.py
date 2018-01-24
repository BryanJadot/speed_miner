import logging
import signal

from speed_miner.misc.process_util import start_proc, term_all_procs, term_proc

from tests.util.test_case import MinerTestCase


class TestProcUtil(MinerTestCase):

    def test_start_proc_basic(self):
        proc = start_proc("sleep 0")
        proc.wait()
        self.assertIsNotNone(proc.poll())
        self.assertIsNone(proc.stdout)
        self.assertIsNone(proc.stderr)

    def test_start_proc_stdout_pipe(self):
        proc = start_proc("echo test test", pipe_stdout=True)
        proc.wait()
        self.assertIsNotNone(proc.poll())
        self.assertEqual(proc.stdout.readline(), b"test test\n")
        self.assertIsNone(proc.stderr)

    def test_start_proc_long(self):
        proc = start_proc("sleep 0.2")
        self.assertIsNone(proc.poll())
        proc.wait()
        self.assertIsNotNone(proc.poll())

    def test_term_proc(self):
        proc = start_proc("sleep 1000")
        self.assertIsNone(proc.poll())
        term_proc(proc)
        self.assertEqual(proc.poll(), -15)

    def test_term_proc_already_termed(self):
        proc = start_proc("sleep 1000")
        self.assertIsNone(proc.poll())
        term_proc(proc)
        self.assertEqual(proc.poll(), -15)
        term_proc(proc)

    def test_term_proc_term_disabled(self):
        logging.getLogger().setLevel(logging.ERROR)

        def trap():
            signal.signal(signal.SIGTERM, signal.SIG_IGN)

        proc = start_proc("sleep 1000", preexec_fn=trap)
        self.assertIsNone(proc.poll())
        term_proc(proc, term_wait_time=0.1)
        self.assertEqual(proc.poll(), -9)
        logging.getLogger().setLevel(logging.WARNING)

    def test_term_all_procs_one_proc(self):
        proc1 = start_proc("sleep 1000")
        term_all_procs()
        self.assertEqual(proc1.poll(), -15)

    def test_term_all_procs_multi_procs(self):
        proc1 = start_proc("sleep 1000")
        proc2 = start_proc("sleep 1000")
        proc3 = start_proc("sleep 1000")
        proc4 = start_proc("sleep 1000")
        proc5 = start_proc("sleep 1000")
        term_all_procs()
        self.assertEqual(proc1.poll(), -15)
        self.assertEqual(proc2.poll(), -15)
        self.assertEqual(proc3.poll(), -15)
        self.assertEqual(proc4.poll(), -15)
        self.assertEqual(proc5.poll(), -15)

    def test_term_all_procs_multi_procs_trapped(self):
        logging.getLogger().setLevel(logging.ERROR)

        def trap():
            signal.signal(signal.SIGTERM, signal.SIG_IGN)

        proc1 = start_proc("sleep 1000", preexec_fn=trap)
        proc2 = start_proc("sleep 1000")
        proc3 = start_proc("sleep 1000", preexec_fn=trap)
        proc4 = start_proc("sleep 1000")
        proc5 = start_proc("sleep 1000")
        term_all_procs(term_wait_time=.05)
        self.assertEqual(proc1.poll(), -9)
        self.assertEqual(proc2.poll(), -15)
        self.assertEqual(proc3.poll(), -9)
        self.assertEqual(proc4.poll(), -15)
        self.assertEqual(proc5.poll(), -15)
        logging.getLogger().setLevel(logging.WARNING)
