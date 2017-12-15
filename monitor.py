import sys
sys.path.insert(0, '/home/bryan/src')

from abc import ABC, abstractmethod
from threading import CondVar, Lock, Thread
from time import sleep


class MiningMonitor(object)
    DEFAULT_CHECK_INTERVAL = 300 # seconds

    @staticmethod
    def switch_miner_and_return_when_started(new_miner, current_miner):
        # Not to be inherited.

        # Start the new mining thread and block until it starts generating currency.
        new_miner.start_and_return_when_miner_is_using_gpu()

        # TODO: Pipe new in new stdout

        # Now, kill the old mining thread.
        current_miner.stop_mining_and_return_when_stopped()


    @staticmethod
    def mine(mining_group, check_interval=DEFAULT_CHECK_INTERVAL):
        monitor_condvar = CondVar()
        current_miner = None

        while True:
            best_miner = mining_group.get_most_profitable_miner()

            if best_miner != current_miner:
                MiningMonitor.switch_miner_and_return_when_started(
                    best_miner, current_miner, monitor_condvar)
                current_miner = best_miner

            current_miner.join(check_interval)


class ZPoolMiningGroup(AbstractMiningGroup):
    def __init__(self):
        pass

    def get_most_profitable_miner(self):
        pass


if __name__ == "main":
    MiningMonitor.mine(ZPoolMiningGroup())
