from multi_miner.misc.logger import pr

class MiningMonitor(object):
    DEFAULT_CHECK_INTERVAL = 300 # seconds

    @staticmethod
    def switch_miner_and_return_when_started(new_miner, current_miner):
        # Not to be inherited.

        # Start the new mining thread and block until it starts generating currency.
        new_miner.start_and_return_when_miner_is_using_gpu()

        # TODO: Pipe new in new stdout

        # Now, kill the old mining thread.
        if current_miner:
            current_miner.stop_mining_and_return_when_stopped()


    @staticmethod
    def mine(mining_group, check_interval=DEFAULT_CHECK_INTERVAL):
        pr("Starting miner for \033[92m%s\033[0m!\n" % mining_group, prefix="Monitor")
        current_miner = None

        while True:
            pr("Finding most profitable miner for \033[92m%s\033[0m...\n" % mining_group, prefix="Monitor")
            best_miner = mining_group.get_most_profitable_miner()
            pr("Found best miner: \033[92m%s\033[0m!\n" % best_miner, prefix="Monitor")

            if best_miner != current_miner:
                pr("Switching to %s...\n" % best_miner, prefix="Monitor")
                MiningMonitor.switch_miner_and_return_when_started(
                    best_miner, current_miner)
                pr("Switch complete!\n", prefix="Monitor")
                current_miner = best_miner

            pr("Sleeping for %i seconds...\n" % check_interval, prefix="Monitor")
            current_miner.wait(check_interval)
