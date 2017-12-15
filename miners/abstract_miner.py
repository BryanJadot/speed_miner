import sys
sys.path.insert(0, '/home/bryan/src')

from abc import ABC, abstractmethod


class AbstractMiner(ABC):
    def __init__(self)
        pass

    def start_and_return_when_miner_is_using_gpu(self):
        self.start_and_return()
        self.return_when_miner_is_using_gpu()

    @abstractmethod
    def return_when_miner_is_using_gpu(self):
        pass

    @abstractmethod
    def start_and_return(self):
        pass

    @abstractmethod
    def stop_mining_and_return_when_stopped(self):
        pass

    @abstractmethod
    def benchmark(self):
        pass
