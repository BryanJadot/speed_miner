import sys

from subprocess import TimeoutExpired
from time import sleep, time

from speed_miner.misc.logging import LOG


class MiningMonitor(object):
    CHECK_INTERVAL = 60 # seconds
    _exit_status = None

    @staticmethod
    def switch_miner_and_return_when_started(new_miner, current_miner):
        # Start the new mining thread and block until it starts generating currency.
        new_miner.start_and_return_when_miner_is_using_gpu()

        if current_miner:
            # Wait for the current_miner to finish its last share.
            # current_miner.return_when_share_is_done()

            # Now, kill the old mining thread.
            current_miner.stop_mining_and_return_when_stopped()

    @staticmethod
    def mine(mining_group):
        LOG.info("Starting miner for \033[92m%s\033[0m!", mining_group)
        current_miner = None
        last_check_time = None

        while True:
            LOG.debug("Finding most profitable miner for \033[92m%s\033[0m...", mining_group)
            best_miner = mining_group.get_most_profitable_miner()
            LOG.debug("Found best miner: \033[92m%s\033[0m!", best_miner)

            if best_miner != current_miner:
                LOG.info("Switching to \033[92m%s\033[0m...", best_miner)
                MiningMonitor.switch_miner_and_return_when_started(best_miner, current_miner)
                current_miner = best_miner
                LOG.info("Switch complete! Shares incoming...")

            MiningMonitor._wait(current_miner)

    @staticmethod
    def _wait(current_miner):
        start_time = time()
        LOG.debug("Sleeping for %i seconds...", MiningMonitor.CHECK_INTERVAL)

        # We have to busy wait because of some complex exit scenarios.
        while time() < start_time + MiningMonitor.CHECK_INTERVAL and current_miner.is_mining():
            if MiningMonitor._exit_status is not None:
                LOG.debug("Exiting program with status %i...", MiningMonitor._exit_status)
                exit(MiningMonitor._exit_status)

            sleep(0.01)

    @staticmethod
    def mark_monitor_for_exit(status):
        MiningMonitor._exit_status = status
