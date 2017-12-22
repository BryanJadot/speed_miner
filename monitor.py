import sys

from subprocess import TimeoutExpired
from threading import Thread
from time import time

from multi_miner.misc.logger import pr


class MiningMonitor(object):
    DEFAULT_CHECK_INTERVAL = 60 # seconds

    @staticmethod
    def output_printer(stream, out_stream, name):
        for line in stream:
            pr(line, prefix=name, stream=out_stream)

    @staticmethod
    def switch_miner_and_return_when_started(new_miner, current_miner):
        # Start the new mining thread and block until it starts generating currency.
        new_miner.start_and_return_when_miner_is_using_gpu()

        # Now, kill the old mining thread.
        if current_miner:
            current_miner.stop_mining_and_return_when_stopped()

        # Finally, start piping the new outputs.
        t = Thread(
            target=MiningMonitor.output_printer,
            args=(new_miner.get_stdout(), sys.stdout, str(new_miner)),
            name="%s (%s)" % (str(new_miner), "stdout"),
        )
        t.daemon = True
        t.start()
        t = Thread(
            target=MiningMonitor.output_printer,
            args=(new_miner.get_stderr(), sys.stderr, str(new_miner)),
            name="%s (%s)" % (str(new_miner), "stderr"),
        )
        t.daemon = True
        t.start()

    @staticmethod
    def mine(mining_group, check_interval=DEFAULT_CHECK_INTERVAL):
        pr("Starting miner for \033[92m%s\033[0m!\n" % mining_group, prefix="Monitor")
        current_miner = None
        last_check_time = None

        while True:
            pr("Finding most profitable miner for \033[92m%s\033[0m...\n" % mining_group, prefix="Monitor")
            best_miner = mining_group.get_most_profitable_miner()
            pr("Found best miner: \033[92m%s\033[0m!\n" % best_miner, prefix="Monitor")

            if best_miner != current_miner:
                pr("Switching to \033[92m%s\033[0m...\n" % best_miner, prefix="Monitor")
                MiningMonitor.switch_miner_and_return_when_started(
                    best_miner, current_miner)
                pr("Switch complete!\n", prefix="Monitor")
                current_miner = best_miner

            pr("Sleeping for %i seconds...\n" % check_interval, prefix="Monitor")
            try:
                current_miner.wait(check_interval)
            except TimeoutExpired as err:
                # Do nothing - this is normal.
                pass
