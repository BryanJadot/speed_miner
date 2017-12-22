from abc import ABC, abstractmethod


class AbstractMiner(ABC):
    @classmethod
    def get_supported_algos(cls):
        raise NotImplementedError()

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
    def benchmark(self, num_samples=20):
        pass

    @abstractmethod
    def wait(self, timeout=None):
        pass

    @abstractmethod
    def get_stdout(self):
        pass

    @abstractmethod
    def get_stderr(self):
        pass

    @abstractmethod
    def __eq__(self):
        pass
