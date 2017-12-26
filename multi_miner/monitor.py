import sys

from subprocess import TimeoutExpired
from time import time

from multi_miner.misc.logging import LOG


class MiningMonitor(object):
    DEFAULT_CHECK_INTERVAL = 60 # seconds

    @staticmethod
    def switch_miner_and_return_when_started(new_miner, current_miner):
        # Start the new mining thread and block until it starts generating currency.
        new_miner.start_and_return_when_miner_is_using_gpu()

        if current_miner:
            # Wait for the current_miner to finish its last share.
            current_miner.return_when_share_is_done()

            # Now, kill the old mining thread.
            current_miner.stop_mining_and_return_when_stopped()

    @staticmethod
    def mine(mining_group, check_interval=DEFAULT_CHECK_INTERVAL):
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

            LOG.debug("Sleeping for %i seconds...", check_interval)
            try:
                current_miner.wait(check_interval)
            except TimeoutExpired as err:
                # Do nothing - this is normal.
                pass
