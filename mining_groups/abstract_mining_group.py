from abc import ABC, abstractmethod

class AbstractMiningGroup(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_most_profitable_miner(self):
        pass
