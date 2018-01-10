from abc import ABC, abstractmethod


class AbstractMiner(ABC):
    @classmethod
    def get_supported_algos(cls):
        raise NotImplementedError()

    def start_and_return_when_miner_is_using_gpu(self):
        self._start_and_return()
        self._return_when_miner_is_using_gpu()

    @abstractmethod
    def return_when_share_is_done(self):
        pass

    @abstractmethod
    def stop_mining_and_return_when_stopped(self):
        pass

    @abstractmethod
    def benchmark(self, num_samples=20):
        pass

    @abstractmethod
    def is_mining(self):
        pass

    @abstractmethod
    def _return_when_miner_is_using_gpu(self):
        pass

    @abstractmethod
    def _start_and_return(self):
        pass

    @abstractmethod
    def __eq__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass
